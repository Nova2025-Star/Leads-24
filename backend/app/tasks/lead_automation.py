from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.lead import Lead, LeadStatus
from app.services.kpi_service import KPIService

class LeadAutomation:
    def __init__(self, db: Session):
        self.db = db

    def expire_old_leads(self, hours_threshold: int = 48):
        expiry_time = datetime.utcnow() - timedelta(hours=hours_threshold)
        leads_to_expire = self.db.query(Lead).filter(Lead.status == LeadStatus.NEW, Lead.created_at < expiry_time).all()
        for lead in leads_to_expire:
            lead.status = LeadStatus.EXPIRED
            lead.expires_at = datetime.utcnow()
            self.db.add(lead)
            KPIService(self.db).log_event("LeadExpired", lead_id=lead.id)
        self.db.commit()