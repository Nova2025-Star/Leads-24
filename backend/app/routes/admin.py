from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import bcrypt

from app.database import get_db
from app.models.user import User, UserRole
from app.models.lead import Lead, LeadStatus
from app.models.quote import Quote, QuoteStatus
from app.models.kpi import KPIEvent
from app.utils.kpi import log_event
from app.schemas.lead import Lead as LeadSchema, LeadCreate
from app.schemas.quote import Quote as QuoteSchema
from app.schemas.user import User as UserSchema, UserCreate

router = APIRouter()


@router.get("/leads", response_model=List[LeadSchema])
def get_admin_leads(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[LeadStatus] = None
):
    """
    Get all leads for admin dashboard.
    """
    query = db.query(Lead)
    if status:
        query = query.filter(Lead.status == status)
    
    return query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/leads", response_model=LeadSchema)
def create_lead(
    lead_in: LeadCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new lead. Only accessible by admin users.
    """
    # Create new lead
    db_lead = Lead(
        customer_name=lead_in.customer_name,
        customer_email=lead_in.customer_email,
        customer_phone=lead_in.customer_phone,
        region=lead_in.region,
        address=lead_in.address,
        description=lead_in.description,
        status=LeadStatus.NEW
    )
    
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    # Log KPI event
    log_event(
        db=db,
        event_type="lead_created",
        lead_id=db_lead.id,
        data=f"Lead created for {db_lead.customer_name} in {db_lead.region}"
    )
    
    return db_lead


@router.delete("/leads/{lead_id}", response_model=dict)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a lead. Only accessible by admin users.
    """
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(db_lead)
    db.commit()
    
    return {"message": "Lead deleted successfully"}


@router.get("/partners", response_model=List[UserSchema])
def get_partners(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    region: Optional[str] = None
):
    """
    Get all franchise partners.
    """
    query = db.query(User).filter(User.role == UserRole.PARTNER)
    if region:
        query = query.filter(User.region == region)
    
    return query.offset(skip).limit(limit).all()


@router.post("/partners", response_model=UserSchema)
def create_partner(
    partner_in: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new franchise partner. Only accessible by admin users.
    """
    # Check if email already exists
    db_user = db.query(User).filter(User.email == partner_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_password = bcrypt.hashpw(partner_in.password.encode('utf-8'), bcrypt.gensalt())
    
    # Create new partner
    db_partner = User(
        email=partner_in.email,
        hashed_password=hashed_password.decode('utf-8'),
        full_name=partner_in.full_name,
        region=partner_in.region,
        role=UserRole.PARTNER
    )
    
    db.add(db_partner)
    db.commit()
    db.refresh(db_partner)
    
    # Log KPI event
    log_event(
        db=db,
        event_type="partner_created",
        user_id=db_partner.id,
        data=f"Partner {db_partner.full_name} created for region {db_partner.region}"
    )
    
    return db_partner


@router.delete("/partners/{partner_id}", response_model=dict)
def delete_partner(
    partner_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a franchise partner. Only accessible by admin users.
    """
    db_partner = db.query(User).filter(User.id == partner_id, User.role == UserRole.PARTNER).first()
    if db_partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    db.delete(db_partner)
    db.commit()
    
    return {"message": "Partner deleted successfully"}


@router.get("/leads/by-region", response_model=List[LeadSchema])
def get_leads_by_region(
    region: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get leads filtered by region.
    """
    query = db.query(Lead).filter(Lead.region == region)
    return query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/leads/unassigned", response_model=List[LeadSchema])
def get_unassigned_leads(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all unassigned leads.
    """
    query = db.query(Lead).filter(Lead.status == LeadStatus.NEW)
    return query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/leads/{lead_id}/assign/{partner_id}", response_model=LeadSchema)
def admin_assign_lead(
    lead_id: int,
    partner_id: int,
    db: Session = Depends(get_db)
):
    """
    Assign a lead to a franchise partner.
    """
    # Check if lead exists
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Check if partner exists and is a partner
    db_partner = db.query(User).filter(User.id == partner_id, User.role == UserRole.PARTNER).first()
    if db_partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Assign lead to partner
    db_lead.assigned_partner_id = partner_id
    db_lead.status = LeadStatus.ASSIGNED
    db_lead.assigned_at = datetime.utcnow()
    
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    # Log KPI event
    log_event(
        db=db,
        event_type="lead_assigned",
        lead_id=db_lead.id,
        user_id=partner_id,
        data=f"Lead assigned to partner {db_partner.full_name}"
    )
    
    return db_lead


@router.get("/quotes", response_model=List[QuoteSchema])
def get_all_quotes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[QuoteStatus] = None
):
    """
    Get all quotes for admin monitoring.
    """
    query = db.query(Quote)
    if status:
        query = query.filter(Quote.status == status)
    
    return query.order_by(Quote.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/accepted-leads", response_model=List[LeadSchema])
def get_accepted_leads(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all accepted leads for billing purposes.
    """
    query = db.query(Lead).filter(Lead.status == LeadStatus.ACCEPTED)
    return query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/leads/{lead_id}/bill", response_model=dict)
def bill_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark a lead as billed to the franchise partner.
    """
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Check if lead is in a billable state
    if db_lead.status not in [LeadStatus.ACCEPTED, LeadStatus.QUOTED, LeadStatus.APPROVED, LeadStatus.COMPLETED]:
        raise HTTPException(status_code=400, detail="Lead is not in a billable state")
    
    # Mark lead as billed
    db_lead.billed = True
    db_lead.billed_at = datetime.utcnow()
    
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    # Log KPI event
    log_event(
        db=db,
        event_type="lead_billed",
        lead_id=db_lead.id,
        data=f"Lead billed to partner"
    )
    
    return {"message": "Lead marked as billed successfully"}


@router.get("/dashboard/summary")
def get_admin_dashboard_summary(
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for admin dashboard.
    """
    total_leads = db.query(Lead).count()
    new_leads = db.query(Lead).filter(Lead.status == LeadStatus.NEW).count()
    assigned_leads = db.query(Lead).filter(Lead.status == LeadStatus.ASSIGNED).count()
    accepted_leads = db.query(Lead).filter(Lead.status == LeadStatus.ACCEPTED).count()
    quoted_leads = db.query(Lead).filter(Lead.status == LeadStatus.QUOTED).count()
    approved_leads = db.query(Lead).filter(Lead.status == LeadStatus.APPROVED).count()
    declined_leads = db.query(Lead).filter(Lead.status == LeadStatus.DECLINED).count()
    completed_leads = db.query(Lead).filter(Lead.status == LeadStatus.COMPLETED).count()
    expired_leads = db.query(Lead).filter(Lead.status == LeadStatus.EXPIRED).count()
    
    # Calculate revenue
    lead_revenue = total_leads * 500  # 500 SEK per lead
    
    # Get approved quotes for commission calculation
    approved_quotes = db.query(Quote).filter(Quote.status == QuoteStatus.APPROVED).all()
    commission_revenue = sum(quote.commission_amount for quote in approved_quotes)
    
    total_revenue = lead_revenue + commission_revenue
    
    return {
        "total_leads": total_leads,
        "new_leads": new_leads,
        "assigned_leads": assigned_leads,
        "accepted_leads": accepted_leads,
        "quoted_leads": quoted_leads,
        "approved_leads": approved_leads,
        "declined_leads": declined_leads,
        "completed_leads": completed_leads,
        "expired_leads": expired_leads,
        "lead_revenue": lead_revenue,
        "commission_revenue": commission_revenue,
        "total_revenue": total_revenue
    }
