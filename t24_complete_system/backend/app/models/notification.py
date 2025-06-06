from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class NotificationType(str, enum.Enum):
    LEAD_CREATED = "lead_created"
    LEAD_ASSIGNED = "lead_assigned"
    LEAD_ACCEPTED = "lead_accepted"
    LEAD_REJECTED = "lead_rejected"
    QUOTE_CREATED = "quote_created"
    QUOTE_SENT = "quote_sent"
    QUOTE_APPROVED = "quote_approved"
    QUOTE_DECLINED = "quote_declined"
    JOB_COMPLETED = "job_completed"
    PAYMENT_RECEIVED = "payment_received"
    LEAD_EXPIRING = "lead_expiring"
    QUOTE_EXPIRING = "quote_expiring"
    SYSTEM_ALERT = "system_alert"


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    
    # Who is receiving the notification
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", foreign_keys=[user_id])
    
    # For customer notifications (not linked to a user account)
    customer_email = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    
    # Notification details
    type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    
    # Related entities
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=True)
    
    # Status tracking
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered = Column(Boolean, default=False)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # For tracking email opens, link clicks, etc.
    tracking_id = Column(String, nullable=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Notification {self.id}: {self.type} via {self.channel}>"


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(NotificationType), nullable=False, unique=True)
    subject = Column(String, nullable=False)
    html_template = Column(Text, nullable=False)
    text_template = Column(Text, nullable=False)
    push_template = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<NotificationTemplate {self.id}: {self.type}>"


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")
    
    notification_type = Column(Enum(NotificationType), nullable=False)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    in_app_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        # Ensure each user has only one preference per notification type
        {"sqlite_autoincrement": True},
    )
    
    def __repr__(self):
        return f"<NotificationPreference {self.id}: User {self.user_id} - {self.notification_type}>"
