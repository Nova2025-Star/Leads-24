from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import json
import logging
import uuid
from pydantic import BaseModel
import secrets
import hashlib

from app.database import get_db
from app.models.user import User, UserRole
from app.models.lead import Lead, LeadStatus
from app.models.quote import Quote, QuoteItem, QuoteStatus
from app.utils.notification_service import EmailNotificationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define API router
router = APIRouter()

# Define Pydantic models for customer portal
class CustomerPortalSettings(BaseModel):
    enable_customer_portal: bool = True
    require_email_verification: bool = True
    allow_quote_modifications: bool = False
    feedback_required: bool = False
    auto_expire_days: int = 30

class CustomerRegistration(BaseModel):
    email: str
    name: str
    phone: str
    password: str

class CustomerLogin(BaseModel):
    email: str
    password: str

class CustomerQuoteResponse(BaseModel):
    decision: str  # "approve" or "decline"
    feedback: Optional[str] = None
    modification_request: Optional[str] = None

class CustomerPortalService:
    """
    Service for customer portal functionality for the T24 Arborist Lead System.
    This enables customers to view and approve/decline quotes online.
    """
    
    def __init__(self, db: Session, background_tasks: Optional[BackgroundTasks] = None):
        self.db = db
        self.background_tasks = background_tasks
    
    def generate_customer_access_token(self, lead_id: int, quote_id: int) -> str:
        """
        Generate a secure access token for customer to access their quote
        
        Args:
            lead_id: Lead ID
            quote_id: Quote ID
            
        Returns:
            Secure access token
        """
        # Get lead and quote
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        quote = self.db.query(Quote).filter(Quote.id == quote_id, Quote.lead_id == lead_id).first()
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")
        
        # Generate token with expiration (30 days)
        expires = datetime.utcnow() + timedelta(days=30)
        
        # Create token payload
        payload = {
            "sub": lead.customer_email,
            "lead_id": lead.id,
            "quote_id": quote.id,
            "customer_name": lead.customer_name,
            "exp": expires
        }
        
        # Sign token
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        # Store token hash in database for verification
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # In a real implementation, this would store the token hash in a database table
        # For this example, we'll just log it
        logger.info(f"Generated customer access token for lead {lead_id}, quote {quote_id}: {token_hash}")
        
        return token
    
    def verify_customer_access_token(self, token: str) -> Dict[str, Any]:
        """
        Verify a customer access token
        
        Args:
            token: Access token
            
        Returns:
            Dict with token payload if valid
        """
        try:
            # Decode token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # Check if token is expired
            if "exp" in payload and datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Token expired")
            
            # In a real implementation, this would verify the token hash in the database
            # For this example, we'll just return the payload
            
            return payload
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def get_customer_quote(self, token_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get quote details for customer
        
        Args:
            token_payload: Verified token payload
            
        Returns:
            Dict with quote details
        """
        lead_id = token_payload.get("lead_id")
        quote_id = token_payload.get("quote_id")
        
        # Get lead and quote
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        quote = self.db.query(Quote).filter(Quote.id == quote_id, Quote.lead_id == lead_id).first()
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")
        
        # Get quote items
        items = self.db.query(QuoteItem).filter(QuoteItem.quote_id == quote_id).all()
        
        # Format items
        formatted_items = []
        for item in items:
            formatted_items.append({
                "id": item.id,
                "quantity": item.quantity,
                "tree_species": item.tree_species,
                "operation_type": item.operation_type,
                "custom_operation": item.custom_operation,
                "cost": item.cost
            })
        
        # Get partner info
        partner = None
        if lead.assigned_partner_id:
            partner = self.db.query(User).filter(User.id == lead.assigned_partner_id).first()
        
        # Return quote details
        return {
            "quote_id": quote.id,
            "lead_id": lead.id,
            "status": quote.status,
            "total_amount": quote.total_amount,
            "created_at": quote.created_at,
            "sent_at": quote.sent_at,
            "expires_at": quote.sent_at + timedelta(days=30) if quote.sent_at else None,
            "items": formatted_items,
            "customer": {
                "name": lead.customer_name,
                "email": lead.customer_email,
                "phone": lead.customer_phone,
                "address": lead.address,
                "city": lead.city,
                "postal_code": lead.postal_code
            },
            "partner": {
                "name": partner.full_name if partner else None,
                "email": partner.email if partner else None
            } if partner else None
        }
    
    def process_customer_response(self, token_payload: Dict[str, Any], 
                                 response: CustomerQuoteResponse) -> Dict[str, Any]:
        """
        Process customer response to quote (approve/decline)
        
        Args:
            token_payload: Verified token payload
            response: Customer response
            
        Returns:
            Dict with updated quote status
        """
        lead_id = token_payload.get("lead_id")
        quote_id = token_payload.get("quote_id")
        
        # Get lead and quote
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        quote = self.db.query(Quote).filter(Quote.id == quote_id, Quote.lead_id == lead_id).first()
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")
        
        # Check if quote can be responded to
        if quote.status != QuoteStatus.SENT:
            raise HTTPException(status_code=400, detail="Quote cannot be responded to")
        
        # Check if quote is expired
        if quote.sent_at and quote.sent_at + timedelta(days=30) < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Quote has expired")
        
        # Process response
        if response.decision.lower() == "approve":
            # Update quote status
            quote.status = QuoteStatus.APPROVED
            lead.status = LeadStatus.APPROVED
        elif response.decision.lower() == "decline":
            # Update quote status
            quote.status = QuoteStatus.DECLINED
            lead.status = LeadStatus.DECLINED
        else:
            raise HTTPException(status_code=400, detail="Invalid decision")
        
        # Update response timestamp
        quote.customer_response_at = datetime.utcnow()
        lead.customer_response_at = datetime.utcnow()
        
        # Save feedback if provided
        if response.feedback:
            # In a real implementation, this would store the feedback in a database table
            logger.info(f"Customer feedback for quote {quote_id}: {response.feedback}")
        
        # Save modification request if provided
        if response.modification_request:
            # In a real implementation, this would store the modification request in a database table
            logger.info(f"Customer modification request for quote {quote_id}: {response.modification_request}")
        
        # Save changes
        self.db.add(quote)
        self.db.add(lead)
        self.db.commit()
        
        # Send notification to partner
        if self.background_tasks:
            notification_service = EmailNotificationService(self.db, self.background_tasks)
            notification_service.send_quote_status_notification(quote_id, response.decision.lower())
        
        return {
            "quote_id": quote.id,
            "lead_id": lead.id,
            "status": quote.status,
            "response_at": quote.customer_response_at
        }
    
    def register_customer(self, registration: CustomerRegistration) -> Dict[str, Any]:
        """
        Register a new customer in the portal
        
        Args:
            registration: Customer registration data
            
        Returns:
            Dict with registration status
        """
        # Check if email already exists
        existing_customer = self.db.query(Customer).filter(Customer.email == registration.email).first()
        if existing_customer:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create verification token
        verification_token = secrets.token_urlsafe(32)
        
        # Create customer record
        customer = Customer(
            email=registration.email,
            name=registration.name,
            phone=registration.phone,
            hashed_password=hash_password(registration.password),
            verification_token=verification_token,
            is_verified=False,
            created_at=datetime.utcnow()
        )
        
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        
        # Send verification email
        if self.background_tasks:
            notification_service = EmailNotificationService(self.db, self.background_tasks)
            # This would send a verification email in a real implementation
            logger.info(f"Would send verification email to {registration.email} with token {verification_token}")
        
        return {
            "customer_id": customer.id,
            "email": customer.email,
            "requires_verification": True
        }
    
    def verify_customer_email(self, token: str) -> Dict[str, Any]:
        """
        Verify a customer's email address
        
        Args:
            token: Verification token
            
        Returns:
            Dict with verification status
        """
        # Find customer with this verification token
        customer = self.db.query(Customer).filter(Customer.verification_token == token).first()
        if not customer:
            raise HTTPException(status_code=400, detail="Invalid verification token")
        
        # Mark as verified
        customer.is_verified = True
        customer.verification_token = None
        customer.verified_at = datetime.utcnow()
        
        self.db.add(customer)
        self.db.commit()
        
        return {
            "customer_id": customer.id,
            "email": customer.email,
            "is_verified": True
        }
    
    def authenticate_customer(self, login: CustomerLogin) -> Dict[str, Any]:
        """
        Authenticate a customer
        
        Args:
            login: Customer login data
            
        Returns:
            Dict with authentication token
        """
        # Find customer by email
        customer = self.db.query(Customer).filter(Customer.email == login.email).first()
        if not customer:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not verify_password(login.password, customer.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if email is verified
        if not customer.is_verified:
            raise HTTPException(status_code=401, detail="Email not verified")
        
        # Generate token
        access_token_expires = timedelta(minutes=60)
        access_token = create_access_token(
            data={"sub": customer.email, "id": customer.id, "type": "customer"},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "customer_id": customer.id,
            "email": customer.email
        }
    
    def get_customer_quotes(self, customer_id: int) -> List[Dict[str, Any]]:
        """
        Get all quotes for a customer
        
        Args:
            customer_id: Customer ID
            
        Returns:
            List of quotes
        """
        # Get customer
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Find leads with this customer's email
        leads = self.db.query(Lead).filter(Lead.customer_email == customer.email).all()
        if not leads:
            return []
        
        lead_ids = [lead.id for lead in leads]
        
        # Get quotes for these leads
        quotes = self.db.query(Quote).filter(Quote.lead_id.in_(lead_ids)).all()
        
        # Format quotes
        result = []
        for quote in quotes:
            lead = next((l for l in leads if l.id == quote.lead_id), None)
            if lead:
                result.append({
                    "quote_id": quote.id,
                    "lead_id": lead.id,
                    "status": quote.status,
                    "total_amount": quote.total_amount,
                    "created_at": quote.created_at,
                    "sent_at": quote.sent_at,
                    "customer_response_at": quote.customer_response_at,
                    "address": lead.address,
                    "city": lead.city
                })
        
        return result


# Helper functions for password hashing and token creation
def hash_password(password: str) -> str:
    """Hash a password for storing"""
    # In a real implementation, this would use bcrypt or similar
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against a provided password"""
    # In a real implementation, this would use bcrypt or similar
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """Create a new access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# Define Customer model (would be in models/customer.py in a real implementation)
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)


# API endpoints for customer portal
@router.post("/customer/register", response_model=Dict[str, Any])
def register_customer(
    registration: CustomerRegistration,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new customer"""
    service = CustomerPortalService(db, background_tasks)
    return service.register_customer(registration)

@router.get("/customer/verify/{token}", response_model=Dict[str, Any])
def verify_customer_email(
    token: str,
    db: Session = Depends(get_db)
):
    """Verify a customer's email address"""
    service = CustomerPortalService(db)
    return service.verify_customer_email(token)

@router.post("/customer/login", response_model=Dict[str, Any])
def login_customer(
    login: CustomerLogin,
    db: Session = Depends(get_db)
):
    """Authenticate a customer"""
    service = CustomerPortalService(db)
    return service.authenticate_customer(login)

@router.get("/customer/quotes", response_model=List[Dict[str, Any]])
def get_customer_quotes(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all quotes for a customer"""
    # Extract customer ID from token
    # In a real implementation, this would use a proper authentication middleware
    customer_id = 1  # Placeholder, would be extracted from token
    
    service = CustomerPortalService(db)
    return service.get_customer_quotes(customer_id)

@router.post("/quotes/{quote_id}/access-token", response_model=Dict[str, Any])
def generate_quote_access_token(
    quote_id: int,
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Generate an access token for a customer to view a quote"""
    service = CustomerPortalService(db)
    token = service.generate_customer_access_token(lead_id, quote_id)
    
    return {
        "access_token": token,
        "quote_id": quote_id,
        "lead_id": lead_id,
        "expires_in": 30 * 24 * 60 * 60  # 30 days in seconds
    }

@router.get("/quotes/view", response_model=Dict[str, Any])
def view_quote_with_token(
    token: str,
    db: Session = Depends(get_db)
):
    """View a quote using an access token"""
    service = CustomerPortalService(db)
    payload = service.verify_customer_access_token(token)
    return service.get_customer_quote(payload)

@router.post("/quotes/respond", response_model=Dict[str, Any])
def respond_to_quote(
    token: str,
    response: CustomerQuoteResponse,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Respond to a quote (approve/decline)"""
    service = CustomerPortalService(db, background_tasks)
    payload = service.verify_customer_access_token(token)
    return service.process_customer_response(payload, response)

@router.get("/customer-portal/settings", response_model=CustomerPortalSettings)
def get_customer_portal_settings(
    db: Session = Depends(get_db)
):
    """Get customer portal settings"""
    # In a real implementation, this would retrieve settings from the database
    return CustomerPortalSettings()
