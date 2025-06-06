from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class KPIEvent(Base):
    __tablename__ = "kpi_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=True)
    
    # Additional data as JSON string
    data = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<KPIEvent {self.id}: {self.event_type} - Lead {self.lead_id}>"


class KPIMetric(Base):
    __tablename__ = "kpi_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    
    # For time-based metrics
    time_period = Column(String, nullable=True)  # daily, weekly, monthly
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    
    # For user or region specific metrics
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    region = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<KPIMetric {self.id}: {self.metric_name} = {self.metric_value}>"
