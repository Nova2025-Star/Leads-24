from sqlalchemy.orm import Session
from app.models.partner import Partner  # Assuming you have this model
from app.models.lead import LeadStatus

class PartnerBillingService:
    def __init__(self, db: Session, debt_increment: float = 500.0):
        self.db = db
        self.debt_increment = debt_increment

    def increment_debt_on_lead_acceptance(self, partner_id: int):
        partner = self.db.query(Partner).filter(Partner.id == partner_id).first()
        if not partner:
            raise ValueError(f"Partner {partner_id} not found")
        
        partner.debt = (partner.debt or 0) + self.debt_increment
        self.db.add(partner)
        self.db.commit()

    def generate_monthly_invoices(self):
        # Placeholder: implement invoice generation for partners with debt > 0
        partners = self.db.query(Partner).filter(Partner.debt > 0).all()
        invoices = []
        for partner in partners:
            invoice = {
                "partner_id": partner.id,
                "amount_due": partner.debt,
                # Add additional invoice details as needed
            }
            # Reset debt after invoicing
            partner.debt = 0
            self.db.add(partner)
            invoices.append(invoice)
        self.db.commit()
        return invoices
