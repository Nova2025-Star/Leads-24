from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.quote import Quote, QuoteItem, OperationType
from app.models.lead import LeadStatus
from app.schemas.quote import QuoteCreate, QuoteUpdate
from app.services.quote_logic import QuoteCalculator, QuoteItem as QuoteItemLogic
from app.services.kpi_service import KPIService
from app.services.offert_creator import OffertCreator
from app.services.lead_status_transition import LeadStatusTransitionService
from app.utils.notification_service import NotificationService

router = APIRouter()

@router.post("/quotes", response_model=dict)
def create_quote(quote_data: QuoteCreate, db: Session = Depends(get_db)):
    # Calculate quote totals using QuoteLogic
    items = [QuoteItemLogic(**item.dict()) for item in quote_data.items]
    calculator = QuoteCalculator(commission_rate=quote_data.commission_rate, discount_rate=quote_data.discount_rate)
    result = calculator.calculate_quote(items, apply_discount=quote_data.apply_discount)

    # Create Quote and QuoteItems
    new_quote = Quote(
        lead_id=quote_data.lead_id,
        subtotal=result["subtotal"],
        discount=result["discount"],
        commission=result["commission"],
        total_amount=result["final_total"],
        status="DRAFT",
        versions=[result]
    )
    db.add(new_quote)
    db.commit()
    db.refresh(new_quote)

    for item in quote_data.items:
        db_item = QuoteItem(
            quote_id=new_quote.id,
            tree_species=item.tree_species,
            operation_type=OperationType(item.operation_type),
            quantity=item.quantity,
            cost=item.cost
        )
        db.add(db_item)
    db.commit()

    KPIService(db).log_event("QuoteCreated", lead_id=quote_data.lead_id, quote_id=new_quote.id)
    return new_quote.to_dict()

@router.get("/quotes/{quote_id}", response_model=dict)
def get_quote(quote_id: int, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return quote.to_dict()

@router.put("/quotes/{quote_id}", response_model=dict)
def update_quote(quote_id: int, quote_data: QuoteUpdate, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Recalculate quote totals
    items = [QuoteItemLogic(**item.dict()) for item in quote_data.items]
    calculator = QuoteCalculator(commission_rate=quote_data.commission_rate, discount_rate=quote_data.discount_rate)
    result = calculator.calculate_quote(items, apply_discount=quote_data.apply_discount)

    # Versioning
    if not quote.versions:
        quote.versions = []
    quote.versions.append(result)

    # Update Quote fields
    quote.subtotal = result["subtotal"]
    quote.discount = result["discount"]
    quote.commission = result["commission"]
    quote.total_amount = result["final_total"]
    quote.status = "UPDATED"

    db.add(quote)
    db.commit()
    db.refresh(quote)

    # Update QuoteItems
    db.query(QuoteItem).filter(QuoteItem.quote_id == quote_id).delete()
    for item in quote_data.items:
        db_item = QuoteItem(
            quote_id=quote.id,
            tree_species=item.tree_species,
            operation_type=OperationType(item.operation_type),
            quantity=item.quantity,
            cost=item.cost
        )
        db.add(db_item)
    db.commit()

    KPIService(db).log_event("QuoteUpdated", lead_id=quote.lead_id, quote_id=quote.id)
    return quote.to_dict()

@router.post("/quotes/{quote_id}/send", response_model=dict)
def send_quote(quote_id: int, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    offert_text = OffertCreator(db).generate_offert_text(quote_id)
    NotificationService(db).send_quote_to_customer(quote.lead_id, offert_text)

    LeadStatusTransitionService(db).update_lead_status(quote.lead_id, LeadStatus.QUOTED, None)
    KPIService(db).log_event("QuoteSent", lead_id=quote.lead_id, quote_id=quote.id)

    quote.status = "SENT"
    db.add(quote)
    db.commit()

    return {"detail": "Quote sent successfully"}