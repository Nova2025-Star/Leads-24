import uuid
import json
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional, Any

from sqlalchemy.orm import Session

from app.config import settings
from app.models.notification import (
    Notification,
    NotificationType,
    NotificationTemplate,
    NotificationPreference,
)
from app.models.lead import Lead
from app.models.quote import Quote, QuoteItem
from app.models.user import User

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class EmailNotificationService:
    def __init__(self, db: Session, background_tasks=None):
        self.db = db
        self.background_tasks = background_tasks

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        tracking_id: Optional[str] = None,
        notification_id: Optional[int] = None,
    ) -> bool:
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = settings.EMAIL_FROM
            message["To"] = to_email

            if tracking_id:
                tracking_pixel = f'<img src="{settings.BASE_URL}/api/v1/notifications/track/{tracking_id}" width="1" height="1" style="display:none;" />'
                html_content += tracking_pixel

            message.attach(MIMEText(html_content, "html"))

            if text_content:
                message.attach(MIMEText(text_content, "plain"))

            logger.info(f"Email to: {to_email}, Subject: {subject}")
            logger.debug(f"Email content preview: {html_content[:200]}")

            if settings.ENABLE_EMAIL_SENDING:
                with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(settings.EMAIL_FROM, to_email, message.as_string())

            if notification_id:
                notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
                if notification:
                    notification.sent = True
                    notification.sent_at = datetime.utcnow()
                    self.db.add(notification)
                    self.db.commit()

            return True
        except Exception as e:
            logger.error(f"Failed sending email to {to_email}: {e}", exc_info=True)
            return False

    def get_template(self, notification_type: NotificationType) -> NotificationTemplate:
        template = (
            self.db.query(NotificationTemplate)
            .filter(NotificationTemplate.type == notification_type)
            .first()
        )
        if not template:
            logger.warning(f"No template for {notification_type}, returning default.")
            return self._get_default_template(notification_type)
        return template

    def _get_default_template(self, notification_type: NotificationType) -> NotificationTemplate:
        subject = f"T24 Arborist: {notification_type.name.replace('_', ' ').title()}"
        html = f"<html><body><h1>{subject}</h1><p>This is an automated notification from T24 Arborist Lead System.</p></body></html>"
        text = f"{subject}\n\nThis is an automated notification from T24 Arborist Lead System."
        return NotificationTemplate(
            type=notification_type,
            subject=subject,
            html_template=html,
            text_template=text,
            push_template=subject,
        )

    def render_template(self, template: NotificationTemplate, context: Dict[str, Any]) -> Dict[str, str]:
        subject = template.subject
        html_content = template.html_template
        text_content = template.text_template

        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            subject = subject.replace(placeholder, str(value))
            html_content = html_content.replace(placeholder, str(value))
            text_content = text_content.replace(placeholder, str(value))

        return {"subject": subject, "html_content": html_content, "text_content": text_content}

    def create_notification(
        self,
        notification_type: NotificationType,
        user_id: Optional[int] = None,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        lead_id: Optional[int] = None,
        quote_id: Optional[int] = None,
        title: Optional[str] = None,
        content: Optional[str] = None,
        channel: Optional[str] = NotificationPreference.channel_default(),
    ) -> Notification:
        tracking_id = str(uuid.uuid4())
        notification = Notification(
            user_id=user_id,
            customer_email=customer_email,
            customer_phone=customer_phone,
            type=notification_type,
            channel=channel,
            title=title or notification_type.name.replace("_", " ").title(),
            content=content or f"Notification: {notification_type.name}",
            lead_id=lead_id,
            quote_id=quote_id,
            tracking_id=tracking_id,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    # Example of one notification type method: Send Lead Created Notification
    def send_lead_created_notification(self, lead_id: int) -> bool:
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            logger.error(f"Lead {lead_id} not found")
            return False

        admin_users = self.db.query(User).filter(User.role == "admin").all()

        for admin in admin_users:
            pref = self.db.query(NotificationPreference).filter(
                NotificationPreference.user_id == admin.id,
                NotificationPreference.notification_type == NotificationType.LEAD_CREATED,
            ).first()

            if not pref or pref.email_enabled:
                template = self.get_template(NotificationType.LEAD_CREATED)
                context = {
                    "admin_name": admin.full_name,
                    "lead_id": lead.id,
                    "customer_name": lead.customer_name,
                    "customer_email": lead.customer_email,
                    "customer_phone": lead.customer_phone,
                    "address": lead.address,
                    "city": lead.city,
                    "region": lead.region,
                    "summary": lead.summary,
                    "created_at": lead.created_at.strftime("%Y-%m-%d %H:%M"),
                }

                rendered = self.render_template(template, context)
                notification = self.create_notification(
                    notification_type=NotificationType.LEAD_CREATED,
                    user_id=admin.id,
                    lead_id=lead.id,
                    title=rendered["subject"],
                    content=rendered["html_content"],
                )

                if self.background_tasks:
                    self.background_tasks.add_task(
                        self.send_email,
                        admin.email,
                        rendered["subject"],
                        rendered["html_content"],
                        rendered["text_content"],
                        notification.tracking_id,
                        notification.id,
                    )
                else:
                    self.send_email(
                        admin.email,
                        rendered["subject"],
                        rendered["html_content"],
                        rendered["text_content"],
                        notification.tracking_id,
                        notification.id,
                    )
        return True
