from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.lead import Lead, LeadStatus
from app.utils.kpi import log_event
from app.schemas.lead import Lead as LeadSchema, LeadCreate, LeadUpdate
from app.config import settings
from app.services.lead_status_transition import LeadStatusTransitionService
from app.utils.auth import get_current_user, require_roles

router = APIRouter()

@router.get("/", response_model=List[LeadSchema])
def get_all_leads(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin", "chief engineer")),
    skip: int = 0,
    limit: int = 100,
    status: Optional[LeadStatus] = None
):
    query = db.query(Lead)
    if status is not None:
        query = query.filter(Lead.status == status)
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=LeadSchema)
def create_lead(
    lead_in: LeadCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin", "chief engineer"))
):
    expires_at = datetime.utcnow() + timedelta(hours=settings.LEAD_EXPIRY_HOURS)
    db_lead = Lead(**lead_in.dict(), expires_at=expires_at)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)

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
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return db_lead

@router.put("/{lead_id}", response_model=LeadSchema)
def update_lead(
    lead_id: int,
    lead_in: LeadUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin", "chief engineer"))
):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    old_status = db_lead.status
    update_data = lead_in.dict(exclude_unset=True)

    if "status" in update_data and update_data["status"] != old_status:
        transition_service = LeadStatusTransitionService(db)
        try:
            transition_service.update_lead_status(lead_id, update_data["status"], current_user.role, current_user.id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        # Auto-update timestamps for specific statuses
        status_timestamps = {
            LeadStatus.ASSIGNED: "assigned_at",
            LeadStatus.ACCEPTED: "accepted_at",
            LeadStatus.QUOTED: "quoted_at",
            LeadStatus.APPROVED: "customer_response_at",
            LeadStatus.DECLINED: "customer_response_at",
        }
        timestamp_field = status_timestamps.get(update_data["status"])
        if timestamp_field:
            update_data[timestamp_field] = datetime.utcnow()

    for key, value in update_data.items():
        setattr(db_lead, key, value)

    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)

    if "status" in update_data and update_data["status"] != old_status:
        log_event(
            db=db,
            event_type="lead_status_changed",
            lead_id=db_lead.id,
            data=f"Status changed from {old_status} to {db_lead.status}"
        )

    return db_lead

@router.post("/{lead_id}/assign/{partner_id}", response_model=LeadSchema)
def assign_lead(
    lead_id: int,
    partner_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin", "chief engineer"))
):
    from app.models.user import User, UserRole
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    db_partner = db.query(User).filter(User.id == partner_id, User.role == UserRole.PARTNER).first()
    if not db_partner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")

    db_lead.assigned_partner_id = partner_id
    db_lead.status = LeadStatus.ASSIGNED
    db_lead.assigned_at = datetime.utcnow()

    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)

    log_event(
        db=db,
        event_type="lead_assigned",
        lead_id=db_lead.id,
        user_id=partner_id,
        data=f"Lead assigned to partner {db_partner.full_name}"
    )

    return db_lead

@router.put("/{lead_id}/recall", response_model=dict)
def recall_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("partner", "admin"))
):
    transition_service = LeadStatusTransitionService(db)
    try:
        transition_service.update_lead_status(lead_id, "CONTACTED", user_role=current_user.role, user_id=current_user.id)
    except ValueError:
        try:
            transition_service.update_lead_status(lead_id, "NEW", user_role=current_user.role, user_id=current_user.id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {"detail": f"Lead {lead_id} recalled successfully"}
