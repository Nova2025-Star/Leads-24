from sqlalchemy.orm import Session
from app.models.lead import Lead

class LeadStatusTransitionService:
    def __init__(self, db: Session):
        self.db = db

    def update_lead_status(self, lead_id: int, new_status: str, user_role: str, user_id=None):
        lead = self.db.query(Lead).filter(Lead.id == lead_id).one_or_none()
        if not lead:
            raise ValueError(f"Lead with id {lead_id} not found")

        new_status_upper = new_status.upper()
        current_status = lead.status.upper()

        allowed_transitions = {
            "NEW": ["CONTACTED", "CLOSED"],
            "CONTACTED": ["QUOTED", "CLOSED"],
            "QUOTED": ["ACCEPTED", "REJECTED"],
            "ACCEPTED": ["COMPLETED"],
            "REJECTED": ["CLOSED"],
            "COMPLETED": [],
            "CLOSED": []
        }

        # Admins can move lead to any status
        if user_role.lower().startswith("admin"):
            lead.status = new_status_upper
        else:
            # Partners can recall leads only to NEW or CONTACTED if lead not closed/completed
            recall_allowed_states = {"NEW", "CONTACTED"}
            if new_status_upper in recall_allowed_states:
                if current_status not in {"COMPLETED", "CLOSED"}:
                    lead.status = new_status_upper
                else:
                    raise ValueError(f"Cannot recall lead from {current_status} to {new_status_upper}")
            else:
                # Otherwise enforce normal transitions
                if new_status_upper not in allowed_transitions.get(current_status, []):
                    raise ValueError(f"Invalid transition from {current_status} to {new_status_upper}")
                lead.status = new_status_upper

        self.db.commit()
        return lead
