from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class TreeSpecies(str, Enum):
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


class OperationType(str, Enum):
    DEAD_WOOD = "Död veds beskärning"
    FELLING = "Trädfällning"
    SECTION_FELLING = "Sektionsfällning"
    ADVANCED_SECTION_FELLING = "Avancerad sektionsfällning"
    CROWN_REDUCTION = "Kronreducering"
    MAINTENANCE_PRUNING = "Underhållsbeskärning"
    SPACE_PRUNING = "Utrymmesbeskärning"
    CROWN_LIFTING = "Kronlyft"
    POLLARDING = "Hamling"
    OTHER = "Annat"
    REMOVAL = "Bortförsling"
    THINNING = "Urglesing"
    STUMP_GRINDING = "Stubbfräsning"
    CROWN_STABILIZATION = "Kronstabilisering"
    EMERGENCY = "Jour"


class QuoteStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    APPROVED = "approved"
    DECLINED = "declined"


class QuoteItemBase(BaseModel):
    quantity: int
    tree_species: TreeSpecies
    operation_type: OperationType
    custom_operation: Optional[str] = None
    cost: float


class QuoteItemCreate(QuoteItemBase):
    pass


class QuoteItemUpdate(BaseModel):
    quantity: Optional[int] = None
    tree_species: Optional[TreeSpecies] = None
    operation_type: Optional[OperationType] = None
    custom_operation: Optional[str] = None
    cost: Optional[float] = None


class QuoteItemInDBBase(QuoteItemBase):
    id: int
    quote_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class QuoteItem(QuoteItemInDBBase):
    pass


class QuoteBase(BaseModel):
    lead_id: int
    total_amount: float
    commission_amount: float


class QuoteCreate(QuoteBase):
    items: List[QuoteItemCreate]


class QuoteUpdate(BaseModel):
    total_amount: Optional[float] = None
    commission_amount: Optional[float] = None
    status: Optional[QuoteStatus] = None


class QuoteInDBBase(QuoteBase):
    id: int
    status: QuoteStatus
    sent_at: Optional[datetime] = None
    customer_response_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Quote(QuoteInDBBase):
    items: List[QuoteItem]
