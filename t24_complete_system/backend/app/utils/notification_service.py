from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import uuid
import json
import logging

from app.database import get_db
from app.models.notification import Notification, NotificationType, NotificationChannel, NotificationTemplate, NotificationPreference
from app.models.lead import Lead
from app.models.quote import Quote, QuoteItem
from app.models.user import User
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailNotificationService:
    """
    Comprehensive email notification service that handles all email communications
    in the T24 Arborist Lead System.
    """
    
    def __init__(self, db: Session, background_tasks: BackgroundTasks = None):
        self.db = db
        self.background_tasks = background_tasks
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None, 
                   tracking_id: str = None, notification_id: int = None) -> bool:
        """
        Send an email with HTML and optional plain text content.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (fallback for email clients that don't support HTML)
            tracking_id: Optional tracking ID for analytics
            notification_id: Optional notification record ID to update after sending
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = settings.EMAIL_FROM
            message["To"] = to_email
            
            # Add tracking pixel if tracking_id is provided
            if tracking_id:
                tracking_pixel = f'<img src="{settings.BASE_URL}/api/v1/notifications/track/{tracking_id}" width="1" height="1" />'
                html_content = html_content + tracking_pixel
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Add plain text content if provided
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # For development, we'll just log the email content
            logger.info(f"Email would be sent to: {to_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Content: {html_content[:100]}...")
            
            # In production, uncomment this code to actually send emails
            if settings.ENABLE_EMAIL_SENDING:
                with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(settings.EMAIL_FROM, to_email, message.as_string())
            
            # Update notification record if provided
            if notification_id:
                notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
                if notification:
                    notification.sent = True
                    notification.sent_at = datetime.utcnow()
                    self.db.add(notification)
                    self.db.commit()
            
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def get_template(self, notification_type: NotificationType) -> NotificationTemplate:
        """Get the notification template for a specific notification type"""
        template = self.db.query(NotificationTemplate).filter(
            NotificationTemplate.type == notification_type
        ).first()
        
        if not template:
            # Use default template if specific one not found
            logger.warning(f"Template for {notification_type} not found, using default")
            return self._get_default_template(notification_type)
        
        return template
    
    def _get_default_template(self, notification_type: NotificationType) -> NotificationTemplate:
        """Create a default template for the notification type"""
        # This would be replaced with actual default templates in production
        subject = f"T24 Arborist: {notification_type.replace('_', ' ').title()}"
        html = f"<html><body><h1>{notification_type.replace('_', ' ').title()}</h1><p>This is a notification from T24 Arborist Lead System.</p></body></html>"
        text = f"{notification_type.replace('_', ' ').title()}\n\nThis is a notification from T24 Arborist Lead System."
        
        return NotificationTemplate(
            type=notification_type,
            subject=subject,
            html_template=html,
            text_template=text,
            push_template=f"{notification_type.replace('_', ' ').title()}"
        )
    
    def render_template(self, template: NotificationTemplate, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Render a notification template with the provided context
        
        Args:
            template: The notification template to render
            context: Dictionary of variables to use in the template
            
        Returns:
            Dict containing rendered subject, html_content, and text_content
        """
        # In a production system, this would use a proper template engine like Jinja2
        # For simplicity, we'll use basic string replacement
        
        subject = template.subject
        html_content = template.html_template
        text_content = template.text_template
        
        # Replace placeholders in templates
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            subject = subject.replace(placeholder, str(value))
            html_content = html_content.replace(placeholder, str(value))
            text_content = text_content.replace(placeholder, str(value))
        
        return {
            "subject": subject,
            "html_content": html_content,
            "text_content": text_content
        }
    
    def create_notification(self, 
                           notification_type: NotificationType,
                           user_id: int = None,
                           customer_email: str = None,
                           customer_phone: str = None,
                           lead_id: int = None,
                           quote_id: int = None,
                           title: str = None,
                           content: str = None,
                           channel: NotificationChannel = NotificationChannel.EMAIL) -> Notification:
        """
        Create a notification record
        
        Args:
            notification_type: Type of notification
            user_id: ID of the user to notify (for internal users)
            customer_email: Customer email (for external notifications)
            customer_phone: Customer phone (for SMS notifications)
            lead_id: Related lead ID
            quote_id: Related quote ID
            title: Notification title
            content: Notification content
            channel: Notification channel
            
        Returns:
            Created Notification object
        """
        # Generate tracking ID for analytics
        tracking_id = str(uuid.uuid4())
        
        # Create notification record
        notification = Notification(
            user_id=user_id,
            customer_email=customer_email,
            customer_phone=customer_phone,
            type=notification_type,
            channel=channel,
            title=title or notification_type.replace('_', ' ').title(),
            content=content or f"Notification: {notification_type}",
            lead_id=lead_id,
            quote_id=quote_id,
            tracking_id=tracking_id
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def send_lead_created_notification(self, lead_id: int) -> bool:
        """Send notification when a new lead is created"""
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            logger.error(f"Lead {lead_id} not found")
            return False
        
        # Notify admin users
        admin_users = self.db.query(User).filter(User.role == "admin").all()
        
        for admin in admin_users:
            # Check notification preferences
            pref = self.db.query(NotificationPreference).filter(
                NotificationPreference.user_id == admin.id,
                NotificationPreference.notification_type == NotificationType.LEAD_CREATED
            ).first()
            
            # Default to email if no preference found
            if not pref or pref.email_enabled:
                # Get template
                template = self.get_template(NotificationType.LEAD_CREATED)
                
                # Prepare context
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
                    "created_at": lead.created_at.strftime("%Y-%m-%d %H:%M")
                }
                
                # Render template
                rendered = self.render_template(template, context)
                
                # Create notification record
                notification = self.create_notification(
                    notification_type=NotificationType.LEAD_CREATED,
                    user_id=admin.id,
                    lead_id=lead.id,
                    title=rendered["subject"],
                    content=rendered["html_content"]
                )
                
                # Send email
                if self.background_tasks:
                    # Send in background if background_tasks is available
                    self.background_tasks.add_task(
                        self.send_email,
                        admin.email,
                        rendered["subject"],
                        rendered["html_content"],
                        rendered["text_content"],
                        notification.tracking_id,
                        notification.id
                    )
                else:
                    # Send immediately otherwise
                    self.send_email(
                        admin.email,
                        rendered["subject"],
                        rendered["html_content"],
                        rendered["text_content"],
                        notification.tracking_id,
                        notification.id
                    )
        
        return True
    
    def send_lead_assigned_notification(self, lead_id: int) -> bool:
        """Send notification when a lead is assigned to a partner"""
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead or not lead.assigned_partner_id:
            logger.error(f"Lead {lead_id} not found or not assigned")
            return False
        
        partner = self.db.query(User).filter(User.id == lead.assigned_partner_id).first()
        if not partner:
            logger.error(f"Partner {lead.assigned_partner_id} not found")
            return False
        
        # Check notification preferences
        pref = self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == partner.id,
            NotificationPreference.notification_type == NotificationType.LEAD_ASSIGNED
        ).first()
        
        # Default to email if no preference found
        if not pref or pref.email_enabled:
            # Get template
            template = self.get_template(NotificationType.LEAD_ASSIGNED)
            
            # Prepare context
            context = {
                "partner_name": partner.full_name,
                "lead_id": lead.id,
                "customer_name": lead.customer_name,
                "customer_email": lead.customer_email,
                "customer_phone": lead.customer_phone,
                "address": lead.address,
                "city": lead.city,
                "region": lead.region,
                "summary": lead.summary,
                "assigned_at": lead.assigned_at.strftime("%Y-%m-%d %H:%M") if lead.assigned_at else "N/A"
            }
            
            # Render template
            rendered = self.render_template(template, context)
            
            # Create notification record
            notification = self.create_notification(
                notification_type=NotificationType.LEAD_ASSIGNED,
                user_id=partner.id,
                lead_id=lead.id,
                title=rendered["subject"],
                content=rendered["html_content"]
            )
            
            # Send email
            if self.background_tasks:
                # Send in background if background_tasks is available
                self.background_tasks.add_task(
                    self.send_email,
                    partner.email,
                    rendered["subject"],
                    rendered["html_content"],
                    rendered["text_content"],
                    notification.tracking_id,
                    notification.id
                )
            else:
                # Send immediately otherwise
                self.send_email(
                    partner.email,
                    rendered["subject"],
                    rendered["html_content"],
                    rendered["text_content"],
                    notification.tracking_id,
                    notification.id
                )
        
        return True
    
    def send_quote_to_customer(self, quote_id: int) -> bool:
        """Send a quote to the customer"""
        quote = self.db.query(Quote).filter(Quote.id == quote_id).first()
        if not quote:
            logger.error(f"Quote {quote_id} not found")
            return False
        
        lead = self.db.query(Lead).filter(Lead.id == quote.lead_id).first()
        if not lead:
            logger.error(f"Lead {quote.lead_id} not found")
            return False
        
        items = self.db.query(QuoteItem).filter(QuoteItem.quote_id == quote.id).all()
        
        # Get template
        template = self.get_template(NotificationType.QUOTE_SENT)
        
        # Format items for template
        items_html = ""
        items_text = ""
        
        for item in items:
            items_html += f"""
            <tr>
                <td>{item.quantity}</td>
                <td>{item.tree_species}</td>
                <td>{item.operation_type}</td>
                <td>{item.cost} SEK</td>
            </tr>
            """
            
            items_text += f"{item.quantity} x {item.tree_species} - {item.operation_type}: {item.cost} SEK\n"
        
        # Prepare context
        context = {
            "customer_name": lead.customer_name,
            "quote_id": quote.id,
            "lead_id": lead.id,
            "items_html": items_html,
            "items_text": items_text,
            "total_cost": quote.total_cost,
            "created_at": quote.created_at.strftime("%Y-%m-%d %H:%M"),
            "valid_until": quote.valid_until.strftime("%Y-%m-%d") if quote.valid_until else "N/A",
            "portal_link": f"{settings.BASE_URL}/customer-portal/quote/{quote.id}?token={quote.access_token}"
        }
        
        # Render template
        rendered = self.render_template(template, context)
        
        # Create notification record
        notification = self.create_notification(
            notification_type=NotificationType.QUOTE_SENT,
            customer_email=lead.customer_email,
            lead_id=lead.id,
            quote_id=quote.id,
            title=rendered["subject"],
            content=rendered["html_content"]
        )
        
        # Send email
        if self.background_tasks:
            # Send in background if background_tasks is available
            self.background_tasks.add_task(
                self.send_email,
                lead.customer_email,
                rendered["subject"],
                rendered["html_content"],
                rendered["text_content"],
                notification.tracking_id,
                notification.id
            )
        else:
            # Send immediately otherwise
            self.send_email(
                lead.customer_email,
                rendered["subject"],
                rendered["html_content"],
                rendered["text_content"],
                notification.tracking_id,
                notification.id
            )
        
        return True
    
    def send_quote_approved_notification(self, quote_id: int) -> bool:
        """Send notification when a quote is approved by the customer"""
        quote = self.db.query(Quote).filter(Quote.id == quote_id).first()
        if not quote:
            logger.error(f"Quote {quote_id} not found")
            return False
        
        lead = self.db.query(Lead).filter(Lead.id == quote.lead_id).first()
        if not lead:
            logger.error(f"Lead {quote.lead_id} not found")
            return False
        
        # Notify the partner who created the quote
        partner = self.db.query(User).filter(User.id == quote.created_by).first()
        if not partner:
            logger.error(f"Partner {quote.created_by} not found")
            return False
        
        # Check notification preferences
        pref = self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == partner.id,
            NotificationPreference.notification_type == NotificationType.QUOTE_APPROVED
        ).first()
        
        # Default to email if no preference found
        if not pref or pref.email_enabled:
            # Get template
            template = self.get_template(NotificationType.QUOTE_APPROVED)
            
            # Prepare context
            context = {
                "partner_name": partner.full_name,
                "quote_id": quote.id,
                "lead_id": lead.id,
                "customer_name": lead.customer_name,
                "customer_email": lead.customer_email,
                "customer_phone": lead.customer_phone,
                "total_cost": quote.total_cost,
                "approved_at": quote.updated_at.strftime("%Y-%m-%d %H:%M")
            }
            
            # Render template
            rendered = self.render_template(template, context)
            
            # Create notification record
            notification = self.create_notification(
                notification_type=NotificationType.QUOTE_APPROVED,
                user_id=partner.id,
                lead_id=lead.id,
                quote_id=quote.id,
                title=rendered["subject"],
                content=rendered["html_content"]
            )
            
            # Send email
            if self.background_tasks:
                # Send in background if background_tasks is available
                self.background_tasks.add_task(
                    self.send_email,
                    partner.email,
                    rendered["subject"],
                    rendered["html_content"],
                    rendered["text_content"],
                    notification.tracking_id,
                    notification.id
                )
            else:
                # Send immediately otherwise
                self.send_email(
                    partner.email,
                    rendered["subject"],
                    rendered["html_content"],
                    rendered["text_content"],
                    notification.tracking_id,
                    notification.id
                )
        
        return True
    
    def send_quote_declined_notification(self, quote_id: int) -> bool:
        """Send notification when a quote is declined by the customer"""
        quote = self.db.query(Quote).filter(Quote.id == quote_id).first()
        if not quote:
            logger.error(f"Quote {quote_id} not found")
            return False
        
        lead = self.db.query(Lead).filter(Lead.id == quote.lead_id).first()
        if not lead:
            logger.error(f"Lead {quote.lead_id} not found")
            return False
        
        # Notify the partner who created the quote
        partner = self.db.query(User).filter(User.id == quote.created_by).first()
        if not partner:
            logger.error(f"Partner {quote.created_by} not found")
            return False
        
        # Check notification preferences
        pref = self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == partner.id,
            NotificationPreference.notification_type == NotificationType.QUOTE_DECLINED
        ).first()
        
        # Default to email if no preference found
        if not pref or pref.email_enabled:
            # Get template
            template = self.get_template(NotificationType.QUOTE_DECLINED)
            
            # Prepare context
            context = {
                "partner_name": partner.full_name,
                "quote_id": quote.id,
                "lead_id": lead.id,
                "customer_name": lead.customer_name,
                "customer_email": lead.customer_email,
                "customer_phone": lead.customer_phone,
                "total_cost": quote.total_cost,
                "declined_at": quote.updated_at.strftime("%Y-%m-%d %H:%M"),
                "feedback": quote.feedback or "No feedback provided"
            }
            
            # Render template
            rendered = self.render_template(template, context)
            
            # Create notification record
            notification = self.create_notification(
                notification_type=NotificationType.QUOTE_DECLINED,
                user_id=partner.id,
                lead_id=lead.id,
                quote_id=quote.id,
                title=rendered["subject"],
                content=rendered["html_content"]
            )
            
            # Send email
            if self.background_tasks:
                # Send in background if background_tasks is available
                self.background_tasks.add_task(
                    self.send_email,
                    partner.email,
                    rendered["subject"],
                    rendered["html_content"],
                    rendered["text_content"],
                    notification.tracking_id,
                    notification.id
                )
            else:
                # Send immediately otherwise
                self.send_email(
                    partner.email,
                    rendered["subject"],
                    rendered["html_content"],
                    rendered["text_content"],
                    notification.tracking_id,
                    notification.id
                )
        
        return True

# Create FastAPI router
router = APIRouter()

# Dependency to get notification service
def get_notification_service(db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    return EmailNotificationService(db, background_tasks)

@router.get("/notifications", response_model=List[Dict])
def get_notifications(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get notifications for a user"""
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(
        Notification.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return [
        {
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "content": n.content,
            "read": n.read,
            "created_at": n.created_at.isoformat(),
            "lead_id": n.lead_id,
            "quote_id": n.quote_id
        }
        for n in notifications
    ]

@router.put("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.read = True
    notification.read_at = datetime.utcnow()
    db.add(notification)
    db.commit()
    
    return {"status": "success"}

@router.put("/notifications/read-all")
def mark_all_notifications_read(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for a user"""
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.read == False
    ).all()
    
    for notification in notifications:
        notification.read = True
        notification.read_at = datetime.utcnow()
        db.add(notification)
    
    db.commit()
    
    return {"status": "success", "count": len(notifications)}

@router.get("/notifications/settings", response_model=Dict)
def get_notification_settings(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get notification settings for a user"""
    preferences = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id
    ).all()
    
    # If no preferences found, create default ones
    if not preferences:
        preferences = []
        for notification_type in NotificationType.__members__.values():
            pref = NotificationPreference(
                user_id=user_id,
                notification_type=notification_type,
                email_enabled=True,
                sms_enabled=False,
                push_enabled=True,
                in_app_enabled=True
            )
            db.add(pref)
            preferences.append(pref)
        db.commit()
    
    return {
        "user_id": user_id,
        "preferences": [
            {
                "type": p.notification_type,
                "email_enabled": p.email_enabled,
                "sms_enabled": p.sms_enabled,
                "push_enabled": p.push_enabled,
                "in_app_enabled": p.in_app_enabled
            }
            for p in preferences
        ]
    }

@router.put("/notifications/settings")
def update_notification_settings(
    user_id: int,
    settings: Dict,
    db: Session = Depends(get_db)
):
    """Update notification settings for a user"""
    if "preferences" not in settings:
        raise HTTPException(status_code=400, detail="Preferences not provided")
    
    for pref_update in settings["preferences"]:
        if "type" not in pref_update:
            continue
        
        pref = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id,
            NotificationPreference.notification_type == pref_update["type"]
        ).first()
        
        if not pref:
            pref = NotificationPreference(
                user_id=user_id,
                notification_type=pref_update["type"]
            )
        
        if "email_enabled" in pref_update:
            pref.email_enabled = pref_update["email_enabled"]
        if "sms_enabled" in pref_update:
            pref.sms_enabled = pref_update["sms_enabled"]
        if "push_enabled" in pref_update:
            pref.push_enabled = pref_update["push_enabled"]
        if "in_app_enabled" in pref_update:
            pref.in_app_enabled = pref_update["in_app_enabled"]
        
        db.add(pref)
    
    db.commit()
    
    return {"status": "success"}

@router.get("/notifications/track/{tracking_id}")
def track_notification(
    tracking_id: str,
    db: Session = Depends(get_db)
):
    """Track when a notification is opened (via tracking pixel)"""
    notification = db.query(Notification).filter(Notification.tracking_id == tracking_id).first()
    if notification:
        notification.opened = True
        notification.opened_at = datetime.utcnow()
        db.add(notification)
        db.commit()
    
    # Return a 1x1 transparent pixel
    return "GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"

# Webhook endpoints for external notification services
@router.post("/notifications/webhook/email")
def email_webhook(
    payload: Dict,
    db: Session = Depends(get_db)
):
    """Webhook for email delivery status updates"""
    if "tracking_id" not in payload:
        raise HTTPException(status_code=400, detail="Tracking ID not provided")
    
    notification = db.query(Notification).filter(Notification.tracking_id == payload["tracking_id"]).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Update notification status based on webhook payload
    if "status" in payload:
        if payload["status"] == "delivered":
            notification.delivered = True
            notification.delivered_at = datetime.utcnow()
        elif payload["status"] == "opened":
            notification.opened = True
            notification.opened_at = datetime.utcnow()
        elif payload["status"] == "clicked":
            notification.clicked = True
            notification.clicked_at = datetime.utcnow()
        elif payload["status"] == "bounced":
            notification.bounced = True
            notification.bounced_at = datetime.utcnow()
            notification.bounce_reason = payload.get("reason", "Unknown")
    
    db.add(notification)
    db.commit()
    
    return {"status": "success"}
