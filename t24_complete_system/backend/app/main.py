from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import logging
import os

from app.database import engine, Base, get_db
from app.routes import auth, leads, quotes, admin, partner, kpi
from app.utils.notification_service import router as notification_router
from app.utils.mobile_api import router as mobile_api_router
from app.utils.analytics import router as analytics_router
from app.utils.customer_portal import router as customer_portal_router
from app.utils.accounting import router as accounting_router
from app.sample_data import create_sample_data

# OAuth2 token path fix for Swagger & authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="T24 Arborist Lead System API",
    description="API for managing arborist leads, quotes, and partners",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(leads.router, prefix="/api/v1", tags=["Leads"])
app.include_router(quotes.router, prefix="/api/v1", tags=["Quotes"])
app.include_router(admin.router, prefix="/api/v1", tags=["Admin"])
app.include_router(partner.router, prefix="/api/v1", tags=["Partner"])
app.include_router(kpi.router, prefix="/api/v1", tags=["KPI"])

# Include additional feature routers
app.include_router(notification_router, prefix="/api/v1", tags=["Notifications"])
app.include_router(mobile_api_router, prefix="/api/v1", tags=["Mobile API"])
app.include_router(analytics_router, prefix="/api/v1", tags=["Analytics"])
app.include_router(customer_portal_router, prefix="/api/v1", tags=["Customer Portal"])
app.include_router(accounting_router, prefix="/api/v1", tags=["Accounting"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to T24 Arborist Lead System API"}

@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
def startup_event():
    # Load sample data if enabled
    if os.environ.get("CREATE_SAMPLE_DATA", "false").lower() == "true":
        db = next(get_db())
        create_sample_data(db)
        logger.info("Sample data created")
