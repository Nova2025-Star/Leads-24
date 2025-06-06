from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class LeadStatus(str, Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    QUOTED = "quoted"
    APPROVED = "approved"
    DECLINED = "declined"
    COMPLETED = "completed"
    EXPIRED = "expired"


class LeadBase(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    address: str
    city: str
    postal_code: str
    region: str
    summary: str
    details: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    region: Optional[str] = None
    summary: Optional[str] = None
    details: Optional[str] = None
    status: Optional[LeadStatus] = None
    assigned_partner_id: Optional[int] = None


class LeadInDBBase(LeadBase):
    id: int
    status: LeadStatus
    assigned_partner_id: Optional[int] = None
    assigned_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    quoted_at: Optional[datetime] = None
    customer_response_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    lead_fee: float
    commission_percent: float
    billed: bool
    viewed_details: bool
    view_count: int

    class Config:
        orm_mode = True


class Lead(LeadInDBBase):
    pass


class LeadPreview(BaseModel):
    id: int
    region: str
    summary: str
    created_at: datetime
    status: LeadStatus

    class Config:
        orm_mode = True
