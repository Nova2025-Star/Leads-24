from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import json
import logging
import uuid
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User, UserRole
from app.models.lead import Lead, LeadStatus
from app.models.quote import Quote, QuoteItem, QuoteStatus
from app.models.notification import Notification, NotificationType
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define API router
router = APIRouter()

# Define Pydantic models for mobile API
class MobileAuthRequest(BaseModel):
    email: str
    password: str
    device_id: str
    device_type: str
    push_token: Optional[str] = None

class MobileAuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: int
    role: str
    expires_in: int

class MobileRefreshRequest(BaseModel):
    refresh_token: str
    device_id: str

class MobileDeviceInfo(BaseModel):
    device_id: str
    device_type: str
    push_token: Optional[str] = None
    app_version: Optional[str] = None
    os_version: Optional[str] = None

class MobileLeadSummary(BaseModel):
    id: int
    customer_name: str
    city: str
    status: str
    created_at: datetime
    expires_at: Optional[datetime] = None

class MobileQuoteSummary(BaseModel):
    id: int
    lead_id: int
    customer_name: str
    total_amount: float
    status: str
    created_at: datetime
    sent_at: Optional[datetime] = None

class MobileNotification(BaseModel):
    id: int
    type: str
    title: str
    content: str
    created_at: datetime
    read: bool
    lead_id: Optional[int] = None
    quote_id: Optional[int] = None

class MobileApiService:
    """
    Service for handling mobile API functionality for the T24 Arborist Lead System.
    This enables partners to manage leads and quotes from mobile devices.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_user(self, email: str, password: str, device_info: MobileDeviceInfo) -> Dict[str, Any]:
        """
        Authenticate a user and generate access and refresh tokens
        
        Args:
            email: User email
            password: User password
            device_info: Information about the mobile device
            
        Returns:
            Dict containing authentication tokens and user info
        """
        # Find user by email
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password (in a real system, this would use bcrypt or similar)
        # For this example, we'll assume the password verification logic is implemented elsewhere
        # and just check if the user exists
        
        # Generate tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=30)  # Refresh token valid for 30 days
        
        access_token = self._create_access_token(
            data={"sub": user.email, "id": user.id, "role": user.role},
            expires_delta=access_token_expires
        )
        
        refresh_token = self._create_refresh_token(
            data={"sub": user.email, "id": user.id, "device_id": device_info.device_id},
            expires_delta=refresh_token_expires
        )
        
        # Store device info and push token
        self._update_device_info(user.id, device_info)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user.id,
            "role": user.role,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    def refresh_token(self, refresh_token: str, device_id: str) -> Dict[str, Any]:
        """
        Refresh an access token using a refresh token
        
        Args:
            refresh_token: The refresh token
            device_id: The device ID that was used to generate the original token
            
        Returns:
            Dict containing new access token and expiration
        """
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            email = payload.get("sub")
            user_id = payload.get("id")
            token_device_id = payload.get("device_id")
            
            if email is None or user_id is None:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            
            # Verify device ID matches
            if token_device_id != device_id:
                raise HTTPException(status_code=401, detail="Invalid device")
            
            # Get user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                raise HTTPException(status_code=401, detail="User not found or inactive")
            
            # Generate new access token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self._create_access_token(
                data={"sub": user.email, "id": user.id, "role": user.role},
                expires_delta=access_token_expires
            )
            
            return {
                "access_token": access_token,
                "user_id": user.id,
                "role": user.role,
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    def _create_access_token(self, data: dict, expires_delta: timedelta) -> str:
        """Create a new access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def _create_refresh_token(self, data: dict, expires_delta: timedelta) -> str:
        """Create a new refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def _update_device_info(self, user_id: int, device_info: MobileDeviceInfo) -> None:
        """Update or store device information for push notifications"""
        # In a real implementation, this would store the device info in a database table
        # For this example, we'll just log it
        logger.info(f"Updating device info for user {user_id}: {device_info.dict()}")
        
        # This would typically update a MobileDevice table in the database
        # Example:
        # device = db.query(MobileDevice).filter(
        #     MobileDevice.user_id == user_id,
        #     MobileDevice.device_id == device_info.device_id
        # ).first()
        # 
        # if not device:
        #     device = MobileDevice(user_id=user_id)
        # 
        # device.device_id = device_info.device_id
        # device.device_type = device_info.device_type
        # device.push_token = device_info.push_token
        # device.app_version = device_info.app_version
        # device.os_version = device_info.os_version
        # device.last_active = datetime.utcnow()
        # 
        # db.add(device)
        # db.commit()
    
    def get_partner_leads(self, user_id: int, status: Optional[str] = None, 
                         limit: int = 50, offset: int = 0) -> List[MobileLeadSummary]:
        """
        Get leads assigned to a partner
        
        Args:
            user_id: Partner user ID
            status: Optional filter by lead status
            limit: Maximum number of leads to return
            offset: Offset for pagination
            
        Returns:
            List of lead summaries
        """
        # Verify user is a partner
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.role != UserRole.PARTNER:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Build query
        query = self.db.query(Lead).filter(Lead.assigned_partner_id == user_id)
        
        # Apply status filter if provided
        if status:
            try:
                lead_status = LeadStatus(status)
                query = query.filter(Lead.status == lead_status)
            except ValueError:
                # Invalid status, ignore filter
                pass
        
        # Get leads with pagination
        leads = query.order_by(Lead.created_at.desc()).offset(offset).limit(limit).all()
        
        # Convert to response model
        result = []
        for lead in leads:
            result.append(MobileLeadSummary(
                id=lead.id,
                customer_name=lead.customer_name,
                city=lead.city,
                status=lead.status,
                created_at=lead.created_at,
                expires_at=lead.expires_at
            ))
        
        return result
    
    def get_lead_details(self, lead_id: int, user_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a lead
        
        Args:
            lead_id: Lead ID
            user_id: User ID requesting the details
            
        Returns:
            Dict containing lead details
        """
        # Get lead
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Verify user has access to this lead
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        if user.role == UserRole.PARTNER and lead.assigned_partner_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this lead")
        
        # Get quotes for this lead
        quotes = self.db.query(Quote).filter(Quote.lead_id == lead_id).all()
        
        # Format quotes
        formatted_quotes = []
        for quote in quotes:
            formatted_quotes.append({
                "id": quote.id,
                "status": quote.status,
                "total_amount": quote.total_amount,
                "created_at": quote.created_at,
                "sent_at": quote.sent_at
            })
        
        # Return lead details
        return {
            "id": lead.id,
            "customer_name": lead.customer_name,
            "customer_email": lead.customer_email,
            "customer_phone": lead.customer_phone,
            "address": lead.address,
            "city": lead.city,
            "postal_code": lead.postal_code,
            "region": lead.region,
            "summary": lead.summary,
            "details": lead.details,
            "status": lead.status,
            "assigned_at": lead.assigned_at,
            "accepted_at": lead.accepted_at,
            "quoted_at": lead.quoted_at,
            "customer_response_at": lead.customer_response_at,
            "created_at": lead.created_at,
            "expires_at": lead.expires_at,
            "quotes": formatted_quotes
        }
    
    def update_lead_status(self, lead_id: int, user_id: int, status: str) -> Dict[str, Any]:
        """
        Update the status of a lead
        
        Args:
            lead_id: Lead ID
            user_id: User ID making the update
            status: New status
            
        Returns:
            Dict containing updated lead info
        """
        # Get lead
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Verify user has access to this lead
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        if user.role == UserRole.PARTNER and lead.assigned_partner_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this lead")
        
        # Validate status transition
        try:
            new_status = LeadStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        # Check if status transition is allowed
        if not self._is_valid_status_transition(lead.status, new_status, user.role):
            raise HTTPException(status_code=400, detail="Invalid status transition")
        
        # Update lead status
        lead.status = new_status
        
        # Update timestamps based on status
        if new_status == LeadStatus.ACCEPTED:
            lead.accepted_at = datetime.utcnow()
        elif new_status == LeadStatus.QUOTED:
            lead.quoted_at = datetime.utcnow()
        
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        
        return {
            "id": lead.id,
            "status": lead.status,
            "updated_at": lead.updated_at
        }
    
    def _is_valid_status_transition(self, current_status: LeadStatus, new_status: LeadStatus, 
                                   user_role: UserRole) -> bool:
        """Check if a status transition is valid"""
        # Define allowed transitions based on role and current status
        if user_role == UserRole.ADMIN:
            # Admins can make any transition
            return True
        
        if user_role == UserRole.PARTNER:
            # Partners can only make certain transitions
            if current_status == LeadStatus.ASSIGNED:
                return new_status in [LeadStatus.ACCEPTED, LeadStatus.REJECTED]
            elif current_status == LeadStatus.ACCEPTED:
                return new_status in [LeadStatus.QUOTED]
            elif current_status == LeadStatus.QUOTED:
                return new_status in [LeadStatus.COMPLETED]
        
        return False
    
    def get_partner_quotes(self, user_id: int, status: Optional[str] = None,
                          limit: int = 50, offset: int = 0) -> List[MobileQuoteSummary]:
        """
        Get quotes created by a partner
        
        Args:
            user_id: Partner user ID
            status: Optional filter by quote status
            limit: Maximum number of quotes to return
            offset: Offset for pagination
            
        Returns:
            List of quote summaries
        """
        # Verify user is a partner
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.role != UserRole.PARTNER:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get leads assigned to this partner
        lead_ids = [lead.id for lead in self.db.query(Lead).filter(
            Lead.assigned_partner_id == user_id
        ).all()]
        
        if not lead_ids:
            return []
        
        # Build query
        query = self.db.query(Quote, Lead).join(
            Lead, Quote.lead_id == Lead.id
        ).filter(Quote.lead_id.in_(lead_ids))
        
        # Apply status filter if provided
        if status:
            try:
                quote_status = QuoteStatus(status)
                query = query.filter(Quote.status == quote_status)
            except ValueError:
                # Invalid status, ignore filter
                pass
        
        # Get quotes with pagination
        results = query.order_by(Quote.created_at.desc()).offset(offset).limit(limit).all()
        
        # Convert to response model
        result = []
        for quote, lead in results:
            result.append(MobileQuoteSummary(
                id=quote.id,
                lead_id=quote.lead_id,
                customer_name=lead.customer_name,
                total_amount=quote.total_amount,
                status=quote.status,
                created_at=quote.created_at,
                sent_at=quote.sent_at
            ))
        
        return result
    
    def get_quote_details(self, quote_id: int, user_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a quote
        
        Args:
            quote_id: Quote ID
            user_id: User ID requesting the details
            
        Returns:
            Dict containing quote details
        """
        # Get quote
        quote = self.db.query(Quote).filter(Quote.id == quote_id).first()
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")
        
        # Get lead
        lead = self.db.query(Lead).filter(Lead.id == quote.lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Verify user has access to this quote
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        if user.role == UserRole.PARTNER and lead.assigned_partner_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this quote")
        
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
        
        # Return quote details
        return {
            "id": quote.id,
            "lead_id": quote.lead_id,
            "status": quote.status,
            "total_amount": quote.total_amount,
            "commission_amount": quote.commission_amount,
            "sent_at": quote.sent_at,
            "customer_response_at": quote.customer_response_at,
            "created_at": quote.created_at,
            "updated_at": quote.updated_at,
            "items": formatted_items,
            "customer": {
                "name": lead.customer_name,
                "email": lead.customer_email,
                "phone": lead.customer_phone,
                "address": lead.address,
                "city": lead.city,
                "postal_code": lead.postal_code
            }
        }
    
    def get_user_notifications(self, user_id: int, limit: int = 50, 
                              offset: int = 0) -> List[MobileNotification]:
        """
        Get notifications for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of notifications to return
            offset: Offset for pagination
            
        Returns:
            List of notifications
        """
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get notifications
        notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(
            Notification.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        # Convert to response model
        result = []
        for notification in notifications:
            result.append(MobileNotification(
                id=notification.id,
                type=notification.type,
                title=notification.title,
                content=notification.content,
                created_at=notification.created_at,
                read=notification.read,
                lead_id=notification.lead_id,
                quote_id=notification.quote_id
            ))
        
        return result
    
    def mark_notification_read(self, notification_id: int, user_id: int) -> Dict[str, Any]:
        """
        Mark a notification as read
        
        Args:
            notification_id: Notification ID
            user_id: User ID
            
        Returns:
            Dict containing status
        """
        # Get notification
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        # Verify user owns this notification
        if notification.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Mark as read
        notification.read = True
        notification.read_at = datetime.utcnow()
        self.db.add(notification)
        self.db.commit()
        
        return {"status": "success"}


# API endpoints for mobile app
@router.post("/mobile/auth", response_model=MobileAuthResponse)
def mobile_authenticate(
    auth_request: MobileAuthRequest,
    db: Session = Depends(get_db)
):
    """Authenticate a mobile user and get tokens"""
    service = MobileApiService(db)
    device_info = MobileDeviceInfo(
        device_id=auth_request.device_id,
        device_type=auth_request.device_type,
        push_token=auth_request.push_token
    )
    
    result = service.authenticate_user(auth_request.email, auth_request.password, device_info)
    return MobileAuthResponse(**result)

@router.post("/mobile/refresh", response_model=Dict[str, Any])
def mobile_refresh_token(
    refresh_request: MobileRefreshRequest,
    db: Session = Depends(get_db)
):
    """Refresh an access token"""
    service = MobileApiService(db)
    result = service.refresh_token(refresh_request.refresh_token, refresh_request.device_id)
    return result

@router.get("/mobile/leads", response_model=List[MobileLeadSummary])
def get_mobile_leads(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Get leads for a partner"""
    # Extract user ID from token
    # In a real implementation, this would use a proper authentication middleware
    user_id = 1  # Placeholder, would be extracted from token
    
    service = MobileApiService(db)
    return service.get_partner_leads(user_id, status, limit, offset)

@router.get("/mobile/leads/{lead_id}", response_model=Dict[str, Any])
def get_mobile_lead_details(
    lead_id: int,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Get detailed information about a lead"""
    # Extract user ID from token
    user_id = 1  # Placeholder, would be extracted from token
    
    service = MobileApiService(db)
    return service.get_lead_details(lead_id, user_id)

@router.post("/mobile/leads/{lead_id}/status", response_model=Dict[str, Any])
def update_mobile_lead_status(
    lead_id: int,
    status: str,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Update the status of a lead"""
    # Extract user ID from token
    user_id = 1  # Placeholder, would be extracted from token
    
    service = MobileApiService(db)
    return service.update_lead_status(lead_id, user_id, status)

@router.get("/mobile/quotes", response_model=List[MobileQuoteSummary])
def get_mobile_quotes(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Get quotes for a partner"""
    # Extract user ID from token
    user_id = 1  # Placeholder, would be extracted from token
    
    service = MobileApiService(db)
    return service.get_partner_quotes(user_id, status, limit, offset)

@router.get("/mobile/quotes/{quote_id}", response_model=Dict[str, Any])
def get_mobile_quote_details(
    quote_id: int,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Get detailed information about a quote"""
    # Extract user ID from token
    user_id = 1  # Placeholder, would be extracted from token
    
    service = MobileApiService(db)
    return service.get_quote_details(quote_id, user_id)

@router.get("/mobile/notifications", response_model=List[MobileNotification])
def get_mobile_notifications(
    limit: int = 50,
    offset: int = 0,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Get notifications for a user"""
    # Extract user ID from token
    user_id = 1  # Placeholder, would be extracted from token
    
    service = MobileApiService(db)
    return service.get_user_notifications(user_id, limit, offset)

@router.post("/mobile/notifications/{notification_id}/read", response_model=Dict[str, Any])
def mark_mobile_notification_read(
    notification_id: int,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    # Extract user ID from token
    user_id = 1  # Placeholder, would be extracted from token
    
    service = MobileApiService(db)
    return service.mark_notification_read(notification_id, user_id)
