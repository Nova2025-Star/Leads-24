from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    PARTNER = "partner"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    region = Column(String, nullable=True)  # For partners, their operating region
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
