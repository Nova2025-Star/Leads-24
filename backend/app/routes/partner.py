from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User, UserRole
from app.models.lead import Lead, LeadStatus
from app.models.quote import Quote, QuoteStatus
from app.models.kpi import KPIEvent
from app.utils.kpi import log_event
from app.schemas.lead import Lead as LeadSchema, LeadPreview
from app.schemas.quote import Quote as QuoteSchema, QuoteCreate

router = APIRouter()


@router.get("/leads", response_model=List[LeadPreview])
def get_partner_leads(
    partner_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[LeadStatus] = None
):
    """
    Get all leads assigned to a specific partner.
    Only shows preview information until accepted.
    """
    query = db.query(Lead).filter(Lead.assigned_partner_id == partner_id)
    if status:
        query = query.filter(Lead.status == status)
    
    return query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/leads/{lead_id}", response_model=LeadSchema)
def get_partner_lead_details(
    lead_id: int,
    partner_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information for a specific lead.
    Full details are only available if the lead has been accepted.
    """
    db_lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.assigned_partner_id == partner_id
    ).first()
    
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # If lead is not accepted yet, increment view count
    if not db_lead.viewed_details and db_lead.status in [LeadStatus.ASSIGNED, LeadStatus.ACCEPTED]:
        db_lead.viewed_details = True
        db_lead.view_count += 1
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
        
        # Log KPI event
        log_event(
            db=db,
            event_type="lead_details_viewed",
            lead_id=db_lead.id,
            user_id=partner_id,
            data=f"Lead details viewed by partner"
        )
    
    return db_lead


@router.post("/leads/{lead_id}/accept", response_model=LeadSchema)
def accept_lead(
    lead_id: int,
    partner_id: int,
    db: Session = Depends(get_db)
):
    """
    Accept a lead that has been assigned to a partner.
    """
    db_lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.assigned_partner_id == partner_id,
        Lead.status == LeadStatus.ASSIGNED
    ).first()
    
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found or not available for acceptance")
    
    # Update lead status
    db_lead.status = LeadStatus.ACCEPTED
    db_lead.accepted_at = datetime.utcnow()
    
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    # Log KPI event
    log_event(
        db=db,
        event_type="lead_accepted",
        lead_id=db_lead.id,
        user_id=partner_id,
        data=f"Lead accepted by partner"
    )
    
    return db_lead


@router.post("/leads/{lead_id}/reject", response_model=LeadSchema)
def reject_lead(
    lead_id: int,
    partner_id: int,
    db: Session = Depends(get_db)
):
    """
    Reject a lead that has been assigned to a partner.
    """
    db_lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.assigned_partner_id == partner_id,
        Lead.status == LeadStatus.ASSIGNED
    ).first()
    
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found or not available for rejection")
    
    # Update lead status
    db_lead.status = LeadStatus.REJECTED
    
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    # Log KPI event
    log_event(
        db=db,
        event_type="lead_rejected",
        lead_id=db_lead.id,
        user_id=partner_id,
        data=f"Lead rejected by partner"
    )
    
    return db_lead


@router.get("/quotes", response_model=List[QuoteSchema])
def get_partner_quotes(
    partner_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[QuoteStatus] = None
):
    """
    Get all quotes created by a specific partner.
    """
    # First get all leads assigned to this partner
    partner_leads = db.query(Lead).filter(Lead.assigned_partner_id == partner_id).all()
    partner_lead_ids = [lead.id for lead in partner_leads]
    
    # Then get quotes for those leads
    query = db.query(Quote).filter(Quote.lead_id.in_(partner_lead_ids))
    if status:
        query = query.filter(Quote.status == status)
    
    return query.order_by(Quote.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/leads/{lead_id}/quote", response_model=QuoteSchema)
def create_partner_quote(
    lead_id: int,
    partner_id: int,
    quote_in: QuoteCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new quote for a lead.
    """
    # Check if lead exists and is assigned to this partner
    db_lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.assigned_partner_id == partner_id,
        Lead.status == LeadStatus.ACCEPTED
    ).first()
    
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found or not available for quoting")
    
    # Create new quote
    db_quote = Quote(
        lead_id=lead_id,
        total_amount=quote_in.total_amount,
        commission_amount=quote_in.commission_amount
    )
    
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    
    # Create quote items
    from app.models.quote import QuoteItem
    for item in quote_in.items:
        db_item = QuoteItem(
            quote_id=db_quote.id,
            **item.dict()
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_quote)
    
    # Update lead status
    db_lead.status = LeadStatus.QUOTED
    db_lead.quoted_at = datetime.utcnow()
    db.add(db_lead)
    db.commit()
    
    # Log KPI event
    log_event(
        db=db,
        event_type="quote_created",
        lead_id=lead_id,
        quote_id=db_quote.id,
        user_id=partner_id,
        data=f"Quote created with total amount: {db_quote.total_amount} SEK"
    )
    
    return db_quote


@router.post("/quotes/{quote_id}/send", response_model=QuoteSchema)
def send_partner_quote(
    quote_id: int,
    partner_id: int,
    db: Session = Depends(get_db)
):
    """
    Send a quote to the customer.
    """
    # Get the quote
    db_quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if db_quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Check if lead is assigned to this partner
    db_lead = db.query(Lead).filter(
        Lead.id == db_quote.lead_id,
        Lead.assigned_partner_id == partner_id
    ).first()
    
    if db_lead is None:
        raise HTTPException(status_code=403, detail="Not authorized to send this quote")
    
    # Update quote status
    db_quote.status = QuoteStatus.SENT
    db_quote.sent_at = datetime.utcnow()
    
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    
    # Log KPI event
    log_event(
        db=db,
        event_type="quote_sent",
        lead_id=db_lead.id,
        quote_id=db_quote.id,
        user_id=partner_id,
        data=f"Quote sent to customer: {db_lead.customer_email}"
    )
    
    # In a real system, we would send an email to the customer here
    # For now, we'll just log it
    
    return db_quote
