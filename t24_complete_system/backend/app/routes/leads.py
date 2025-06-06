from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.lead import Lead, LeadStatus
from app.models.kpi import KPIEvent
from app.utils.kpi import log_event
from app.schemas.lead import Lead as LeadSchema, LeadCreate, LeadUpdate, LeadPreview
from app.config import settings

router = APIRouter()


@router.get("/", response_model=List[LeadSchema])
def get_all_leads(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[LeadStatus] = None
):
    """
    Get all leads. Only accessible by admin users.
    """
    query = db.query(Lead)
    if status:
        query = query.filter(Lead.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=LeadSchema)
def create_lead(
    lead_in: LeadCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new lead. Only accessible by admin users.
    """
    # Create new lead
    expires_at = datetime.utcnow() + timedelta(hours=settings.LEAD_EXPIRY_HOURS)
    db_lead = Lead(**lead_in.dict(), expires_at=expires_at)
    
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    # Log KPI event
    log_event(
        db=db,
        event_type="lead_created",
        lead_id=db_lead.id,
        data=f"Lead created for region: {db_lead.region}"
    )
    
    return db_lead


@router.get("/{lead_id}", response_model=LeadSchema)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific lead by ID.
    """
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return db_lead


@router.put("/{lead_id}", response_model=LeadSchema)
def update_lead(
    lead_id: int,
    lead_in: LeadUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a lead. Only accessible by admin users.
    """
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Track status changes for KPI
    old_status = db_lead.status
    
    # Update lead fields
    update_data = lead_in.dict(exclude_unset=True)
    
    # Handle status transitions
    if "status" in update_data and update_data["status"] != old_status:
        if update_data["status"] == LeadStatus.ASSIGNED:
            update_data["assigned_at"] = datetime.utcnow()
        elif update_data["status"] == LeadStatus.ACCEPTED:
            update_data["accepted_at"] = datetime.utcnow()
        elif update_data["status"] == LeadStatus.QUOTED:
            update_data["quoted_at"] = datetime.utcnow()
        elif update_data["status"] in [LeadStatus.APPROVED, LeadStatus.DECLINED]:
            update_data["customer_response_at"] = datetime.utcnow()
    
    for key, value in update_data.items():
        setattr(db_lead, key, value)
    
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    # Log KPI event for status change
    if "status" in update_data and update_data["status"] != old_status:
        log_event(
            db=db,
            event_type=f"lead_status_changed",
            lead_id=db_lead.id,
            data=f"Status changed from {old_status} to {db_lead.status}"
        )
    
    return db_lead


@router.post("/{lead_id}/assign/{partner_id}", response_model=LeadSchema)
def assign_lead(
    lead_id: int,
    partner_id: int,
    db: Session = Depends(get_db)
):
    """
    Assign a lead to a partner. Only accessible by admin users.
    """
    # Check if lead exists
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Check if partner exists and is a partner
    from app.models.user import User, UserRole
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
