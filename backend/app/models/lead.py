from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class LeadStatus(str, enum.Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    QUOTED = "quoted"
    APPROVED = "approved"
    DECLINED = "declined"
    COMPLETED = "completed"
    EXPIRED = "expired"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    region = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, nullable=False)
    
    assigned_partner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_partner = relationship("User", foreign_keys=[assigned_partner_id])
    
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    quoted_at = Column(DateTime(timezone=True), nullable=True)
    customer_response_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Billing information
    lead_fee = Column(Float, default=500.0)  # 500 SEK per lead
    commission_percent = Column(Float, default=10.0)  # 10% of quote value
    billed = Column(Boolean, default=False)
    
    # Relationships
    quotes = relationship("Quote", back_populates="lead")
    
    # Audit and KPI tracking
    viewed_details = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Lead {self.id}: {self.customer_name} - {self.status}>"
