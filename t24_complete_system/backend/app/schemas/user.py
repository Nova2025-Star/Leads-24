from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    PARTNER = "partner"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    region: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    region: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str
