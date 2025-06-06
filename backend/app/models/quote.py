from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Numeric, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class TreeSpecies(str, enum.Enum):
    PINE = "Tall (Pine)"
    SPRUCE = "Gran (Spruce)"
    OAK = "Ek (Oak)"
    BEECH = "Bok (Beech)"
    MAPLE = "Lönn (Maple)"
    ASH = "Ask (Ash)"
    ALDER = "Al (Alder)"
    BIRCH = "Björk (Birch)"
    LINDEN = "Lind (Linden)"
    BIRD_CHERRY = "Hägg (Bird Cherry)"
    ROWAN = "Rönn (Rowan)"
    CHERRY = "Körsbär (Cherry)"
    WALNUT = "Valnöt (Walnut)"
    POPLAR = "Poppel (Poplar)"
    PLANE = "Platan (Plane)"
    WILLOW = "Pil (Willow)"


class OperationType(str, enum.Enum):
    DEAD_WOOD = "Död veds beskärning"
    FELLING = "Trädfällning"
    SECTION_FELLING = "Sektionsfällning"
    ADVANCED_SECTION_FELLING = "Avancerad sektionsfällning"
    CROWN_REDUCTION = "Kronreducering"
    MAINTENANCE_PRUNING = "Underhållsbeskäring"
    SPACE_PRUNING = "Utrymmesbeskärning"
    CROWN_LIFTING = "Kronlyft"
    POLLARDING = "Hamling"
    OTHER = "Annat"
    REMOVAL = "Bortförsling"
    THINNING = "Urglesing"
    STUMP_GRINDING = "Stubbfräsning"
    CROWN_STABILIZATION = "Kronstabilisering"
    EMERGENCY = "Jour"


class QuoteStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    APPROVED = "approved"
    DECLINED = "declined"


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    lead = relationship("Lead", back_populates="quotes")

    status = Column(Enum(QuoteStatus), default=QuoteStatus.DRAFT, nullable=False, index=True)
    total_amount = Column(Numeric(precision=10, scale=2), nullable=False, default=0.00)
    commission_amount = Column(Numeric(precision=10, scale=2), nullable=False, default=0.00)

    sent_at = Column(DateTime(timezone=True), nullable=True)
    customer_response_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

    items = relationship("QuoteItem", back_populates="quote", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Quote {self.id}: Lead {self.lead_id} - {self.status}>"


class QuoteItem(Base):
    __tablename__ = "quote_items"

    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False, index=True)
    quote = relationship("Quote", back_populates="items")

    quantity = Column(Integer, nullable=False)
    tree_species = Column(Enum(TreeSpecies), nullable=False)
    operation_type = Column(Enum(OperationType), nullable=False)
    custom_operation = Column(String(255), nullable=True)

    cost = Column(Numeric(precision=10, scale=2), nullable=False, default=0.00)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<QuoteItem {self.id}: {self.quantity} x {self.tree_species} - {self.operation_type}>"