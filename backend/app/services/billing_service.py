from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.lead import Lead
from app.models.kpi import KPIEvent

class BillingService:
    def __init__(self, db: Session):
        self.db = db

    def charge_lead_acceptance(self, lead: Lead):
        if not lead.billed:
            lead.billed = True
            lead.billed_at = datetime.utcnow()
            lead.partner_debt += Decimal('500.00')
            self.db.add(lead)
            self.db.commit()
            self.db.refresh(lead)
            self._log_event(lead.id, "LeadAcceptedBilling")

    def deduct_commission(self, lead: Lead, commission_rate: Decimal):
        commission_amount = lead.total_amount * commission_rate
        lead.partner_commission = commission_amount
        lead.partner_debt += commission_amount
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        self._log_event(lead.id, "CommissionDeducted")

    def _log_event(self, lead_id: int, event_type: str):
        event = KPIEvent(event_type=event_type, lead_id=lead_id, created_at=datetime.utcnow())
        self.db.add(event)
        self.db.commit()