from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.quote import Quote, QuoteStatus, QuoteItem
from app.models.lead import Lead, LeadStatus
from app.utils.kpi import log_event
from app.schemas.quote import Quote as QuoteSchema, QuoteCreate, QuoteUpdate, OperationType
from app.config import settings

router = APIRouter()


@router.get("/", response_model=List[QuoteSchema])
def get_all_quotes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[QuoteStatus] = None
):
    """
    Get all quotes. Only accessible by admin users.
    """
    query = db.query(Quote)
    if status:
        query = query.filter(Quote.status == status)
    
    quotes = query.offset(skip).limit(limit).all()
    
    # Fix for operation_type validation error
    for quote in quotes:
        for item in quote.items:
            # Ensure operation_type is a valid enum value
            if not any(item.operation_type == op_type.value for op_type in OperationType):
                # Default to "OTHER" if not a valid value
                item.operation_type = OperationType.OTHER.value
    
    return quotes


@router.post("/", response_model=QuoteSchema)
def create_quote(
    quote_in: QuoteCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new quote. Only accessible by partner users.
    """
    # Check if lead exists
    db_lead = db.query(Lead).filter(Lead.id == quote_in.lead_id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Create new quote
    db_quote = Quote(
        lead_id=quote_in.lead_id,
        total_amount=quote_in.total_amount,
        commission_amount=quote_in.commission_amount
    )
    
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    
    # Create quote items
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
        lead_id=db_lead.id,
        quote_id=db_quote.id,
        data=f"Quote created with total amount: {db_quote.total_amount} SEK"
    )
    
    return db_quote


@router.get("/{quote_id}", response_model=QuoteSchema)
def get_quote(
    quote_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific quote by ID.
    """
    db_quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if db_quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Fix for operation_type validation error
    for item in db_quote.items:
        # Ensure operation_type is a valid enum value
        if not any(item.operation_type == op_type.value for op_type in OperationType):
            # Default to "OTHER" if not a valid value
            item.operation_type = OperationType.OTHER.value
    
    return db_quote


@router.put("/{quote_id}", response_model=QuoteSchema)
def update_quote(
    quote_id: int,
    quote_in: QuoteUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a quote. Only accessible by partner users who created the quote.
    """
    db_quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if db_quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Track status changes for KPI
    old_status = db_quote.status
    
    # Update quote fields
    update_data = quote_in.dict(exclude_unset=True)
    
    # Handle status transitions
    if "status" in update_data and update_data["status"] != old_status:
        if update_data["status"] == QuoteStatus.SENT:
            update_data["sent_at"] = datetime.utcnow()
        elif update_data["status"] in [QuoteStatus.APPROVED, QuoteStatus.DECLINED]:
            update_data["customer_response_at"] = datetime.utcnow()
            
            # Also update the lead status
            db_lead = db.query(Lead).filter(Lead.id == db_quote.lead_id).first()
            if db_lead:
                if update_data["status"] == QuoteStatus.APPROVED:
                    db_lead.status = LeadStatus.APPROVED
                else:
                    db_lead.status = LeadStatus.DECLINED
                db_lead.customer_response_at = datetime.utcnow()
                db.add(db_lead)
    
    for key, value in update_data.items():
        setattr(db_quote, key, value)
    
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    
    # Log KPI event for status change
    if "status" in update_data and update_data["status"] != old_status:
        log_event(
            db=db,
            event_type=f"quote_status_changed",
            lead_id=db_quote.lead_id,
            quote_id=db_quote.id,
            data=f"Status changed from {old_status} to {db_quote.status}"
        )
    
    # Fix for operation_type validation error
    for item in db_quote.items:
        # Ensure operation_type is a valid enum value
        if not any(item.operation_type == op_type.value for op_type in OperationType):
            # Default to "OTHER" if not a valid value
            item.operation_type = OperationType.OTHER.value
    
    return db_quote


@router.post("/{quote_id}/send", response_model=QuoteSchema)
def send_quote_to_customer(
    quote_id: int,
    db: Session = Depends(get_db)
):
    """
    Send a quote to the customer. Only accessible by partner users who created the quote.
    """
    db_quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if db_quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Check if quote is in draft status
    if db_quote.status != QuoteStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Quote has already been sent")
    
    # Get lead information
    db_lead = db.query(Lead).filter(Lead.id == db_quote.lead_id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Update quote status
    db_quote.status = QuoteStatus.SENT
    db_quote.sent_at = datetime.utcnow()
    
    # Update lead status
    db_lead.status = LeadStatus.QUOTED
    db_lead.quoted_at = datetime.utcnow()
    
    db.add(db_quote)
    db.add(db_lead)
    db.commit()
    db.refresh(db_quote)
    
    # Log KPI event
    log_event(
        db=db,
        event_type="quote_sent",
        lead_id=db_lead.id,
        quote_id=db_quote.id,
        data=f"Quote sent to customer: {db_lead.customer_email}"
    )
    
    # Fix for operation_type validation error
    for item in db_quote.items:
        # Ensure operation_type is a valid enum value
        if not any(item.operation_type == op_type.value for op_type in OperationType):
            # Default to "OTHER" if not a valid value
            item.operation_type = OperationType.OTHER.value
    
    return db_quote
