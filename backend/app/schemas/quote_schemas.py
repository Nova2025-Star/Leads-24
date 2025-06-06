from typing import List, Optional
from pydantic import BaseModel, condecimal
from enum import Enum

class OperationType(str, Enum):
    PRUNING = 'PRUNING'
    FELLING = 'FELLING'
    REMOVAL = 'REMOVAL'
    OTHER = 'OTHER'

class QuoteItemCreate(BaseModel):
    tree_species: str
    operation_type: OperationType
    quantity: int
    cost: condecimal(max_digits=10, decimal_places=2)

class QuoteCreate(BaseModel):
    lead_id: int
    items: List[QuoteItemCreate]
    commission_rate: Optional[condecimal(max_digits=5, decimal_places=2)] = 0.15
    discount_rate: Optional[condecimal(max_digits=5, decimal_places=2)] = 0.00
    apply_discount: Optional[bool] = False

class QuoteUpdate(BaseModel):
    items: List[QuoteItemCreate]
    commission_rate: Optional[condecimal(max_digits=5, decimal_places=2)] = 0.15
    discount_rate: Optional[condecimal(max_digits=5, decimal_places=2)] = 0.00
    apply_discount: Optional[bool] = False