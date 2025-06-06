from sqlalchemy.orm import Session
from app.models.user import User

class PartnerRankingService:
    def __init__(self, db: Session):
        self.db = db

    def get_top_partners(self, region: str, limit: int = 3):
        partners = self.db.query(User).filter(User.region == region, User.role == "Partner").all()
        ranked_partners = sorted(partners, key=lambda p: (p.kpi_accept_rate, -p.kpi_response_time), reverse=True)
        return ranked_partners[:limit]