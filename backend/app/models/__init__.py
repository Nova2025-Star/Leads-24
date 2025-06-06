# Import models to make them available for SQLAlchemy
from app.models.user import User, UserRole
from app.models.lead import Lead, LeadStatus
from app.models.quote import Quote, QuoteStatus, QuoteItem
from app.models.kpi import KPIEvent
