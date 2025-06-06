from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import jwt
from datetime import datetime

from app.database import get_db
from app.models.user import User, UserRole
from app.models.lead import Lead, LeadStatus
from app.models.kpi import KPIEvent
from app.config import settings
from app.routes.auth import oauth2_scheme

router = APIRouter()

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

# Dependency to check if user is admin
async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Function to log API access for KPI tracking (moved to main.py as middleware)
async def log_api_access(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()
    
    # Log API access time for KPI tracking
    # This would be implemented in a real system
    
    return response

# Include the routes from other modules with proper dependencies
from app.routes import admin, partner, leads, quotes, kpi, auth

# Admin routes with admin permission check
router.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)]
)

# Partner routes with authentication
router.include_router(
    partner.router,
    prefix="/partner",
    tags=["partner"],
    dependencies=[Depends(get_current_user)]
)

# Lead routes with authentication
router.include_router(
    leads.router,
    prefix="/leads",
    tags=["leads"],
    dependencies=[Depends(get_current_user)]
)

# Quote routes with authentication
router.include_router(
    quotes.router,
    prefix="/quotes",
    tags=["quotes"],
    dependencies=[Depends(get_current_user)]
)

# KPI routes with admin permission check
router.include_router(
    kpi.router,
    prefix="/kpi",
    tags=["kpi"],
    dependencies=[Depends(get_current_admin)]
)

# Auth routes (no authentication required)
router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
)
