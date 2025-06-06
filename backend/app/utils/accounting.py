from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging
import requests
from pydantic import BaseModel

from app.database import get_db
from app.models.lead import Lead, LeadStatus
from app.models.quote import Quote, QuoteStatus, QuoteItem
from app.models.user import User, UserRole
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define API router
router = APIRouter()

# Define Pydantic models for accounting integration
class AccountingSettings(BaseModel):
    accounting_system: str = "quickbooks"  # quickbooks, xero, fortnox, visma
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    tenant_id: Optional[str] = None
    auto_sync: bool = True
    sync_frequency: str = "daily"  # daily, weekly, monthly, on_change
    sync_invoices: bool = True
    sync_payments: bool = True
    sync_customers: bool = True
    sync_expenses: bool = False

class InvoiceData(BaseModel):
    quote_id: int
    lead_id: int
    customer_name: str
    customer_email: str
    customer_address: str
    total_amount: float
    items: List[Dict[str, Any]]
    due_date: Optional[datetime] = None

class PaymentData(BaseModel):
    invoice_id: str
    amount: float
    payment_date: datetime
    payment_method: str

class AccountingIntegrationService:
    """
    Service for integrating with accounting systems for the T24 Arborist Lead System.
    This enables automatic creation of invoices, tracking of payments, and financial reporting.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = self._get_accounting_settings()
    
    def _get_accounting_settings(self) -> AccountingSettings:
        """Get accounting integration settings"""
        # In a real implementation, this would retrieve settings from the database
        # For this example, we'll return default settings
        return AccountingSettings(
            accounting_system="quickbooks",
            api_key=settings.ACCOUNTING_API_KEY if hasattr(settings, 'ACCOUNTING_API_KEY') else None,
            api_secret=settings.ACCOUNTING_API_SECRET if hasattr(settings, 'ACCOUNTING_API_SECRET') else None,
            tenant_id=settings.ACCOUNTING_TENANT_ID if hasattr(settings, 'ACCOUNTING_TENANT_ID') else None,
            auto_sync=True,
            sync_frequency="daily",
            sync_invoices=True,
            sync_payments=True,
            sync_customers=True,
            sync_expenses=False
        )
    
    def create_invoice(self, quote_id: int) -> Dict[str, Any]:
        """
        Create an invoice in the accounting system for an approved quote
        
        Args:
            quote_id: Quote ID
            
        Returns:
            Dict with invoice details
        """
        # Get quote
        quote = self.db.query(Quote).filter(Quote.id == quote_id).first()
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")
        
        # Check if quote is approved
        if quote.status != QuoteStatus.APPROVED:
            raise HTTPException(status_code=400, detail="Cannot create invoice for non-approved quote")
        
        # Get lead
        lead = self.db.query(Lead).filter(Lead.id == quote.lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Get quote items
        items = self.db.query(QuoteItem).filter(QuoteItem.quote_id == quote_id).all()
        
        # Format items for invoice
        formatted_items = []
        for item in items:
            formatted_items.append({
                "description": f"{item.quantity} x {item.tree_species} - {item.operation_type}",
                "quantity": item.quantity,
                "unit_price": item.cost / item.quantity,
                "amount": item.cost,
                "tax_rate": 0.25  # 25% VAT in Sweden
            })
        
        # Set due date (30 days from now)
        due_date = datetime.utcnow() + timedelta(days=30)
        
        # Create invoice data
        invoice_data = InvoiceData(
            quote_id=quote.id,
            lead_id=lead.id,
            customer_name=lead.customer_name,
            customer_email=lead.customer_email,
            customer_address=f"{lead.address}, {lead.city}, {lead.postal_code}",
            total_amount=quote.total_amount,
            items=formatted_items,
            due_date=due_date
        )
        
        # Create invoice in accounting system
        invoice_id = self._create_invoice_in_accounting_system(invoice_data)
        
        # Store invoice reference in database
        # In a real implementation, this would update a field in the Quote model
        # For this example, we'll just log it
        logger.info(f"Created invoice {invoice_id} for quote {quote_id}")
        
        # Return invoice details
        return {
            "invoice_id": invoice_id,
            "quote_id": quote.id,
            "lead_id": lead.id,
            "customer_name": lead.customer_name,
            "total_amount": quote.total_amount,
            "due_date": due_date,
            "created_at": datetime.utcnow()
        }
    
    def _create_invoice_in_accounting_system(self, invoice_data: InvoiceData) -> str:
        """
        Create an invoice in the external accounting system
        
        Args:
            invoice_data: Invoice data
            
        Returns:
            Invoice ID from accounting system
        """
        # In a real implementation, this would make API calls to the accounting system
        # For this example, we'll simulate the API call
        
        accounting_system = self.settings.accounting_system.lower()
        
        if accounting_system == "quickbooks":
            # Simulate QuickBooks API call
            logger.info(f"Would create invoice in QuickBooks for {invoice_data.customer_name}")
            # Generate a fake invoice ID
            invoice_id = f"QB-INV-{invoice_data.quote_id}-{int(datetime.utcnow().timestamp())}"
            
        elif accounting_system == "xero":
            # Simulate Xero API call
            logger.info(f"Would create invoice in Xero for {invoice_data.customer_name}")
            # Generate a fake invoice ID
            invoice_id = f"XR-INV-{invoice_data.quote_id}-{int(datetime.utcnow().timestamp())}"
            
        elif accounting_system == "fortnox":
            # Simulate Fortnox API call
            logger.info(f"Would create invoice in Fortnox for {invoice_data.customer_name}")
            # Generate a fake invoice ID
            invoice_id = f"FN-INV-{invoice_data.quote_id}-{int(datetime.utcnow().timestamp())}"
            
        elif accounting_system == "visma":
            # Simulate Visma API call
            logger.info(f"Would create invoice in Visma for {invoice_data.customer_name}")
            # Generate a fake invoice ID
            invoice_id = f"VS-INV-{invoice_data.quote_id}-{int(datetime.utcnow().timestamp())}"
            
        else:
            # Unknown accounting system
            logger.error(f"Unknown accounting system: {accounting_system}")
            raise HTTPException(status_code=400, detail=f"Unsupported accounting system: {accounting_system}")
        
        return invoice_id
    
    def record_payment(self, invoice_id: str, payment_data: PaymentData) -> Dict[str, Any]:
        """
        Record a payment for an invoice
        
        Args:
            invoice_id: Invoice ID
            payment_data: Payment data
            
        Returns:
            Dict with payment details
        """
        # In a real implementation, this would verify the invoice exists in the database
        # For this example, we'll just log it
        logger.info(f"Recording payment for invoice {invoice_id}")
        
        # Record payment in accounting system
        payment_id = self._record_payment_in_accounting_system(invoice_id, payment_data)
        
        # Return payment details
        return {
            "payment_id": payment_id,
            "invoice_id": invoice_id,
            "amount": payment_data.amount,
            "payment_date": payment_data.payment_date,
            "payment_method": payment_data.payment_method,
            "recorded_at": datetime.utcnow()
        }
    
    def _record_payment_in_accounting_system(self, invoice_id: str, payment_data: PaymentData) -> str:
        """
        Record a payment in the external accounting system
        
        Args:
            invoice_id: Invoice ID
            payment_data: Payment data
            
        Returns:
            Payment ID from accounting system
        """
        # In a real implementation, this would make API calls to the accounting system
        # For this example, we'll simulate the API call
        
        accounting_system = self.settings.accounting_system.lower()
        
        if accounting_system == "quickbooks":
            # Simulate QuickBooks API call
            logger.info(f"Would record payment in QuickBooks for invoice {invoice_id}")
            # Generate a fake payment ID
            payment_id = f"QB-PMT-{invoice_id}-{int(datetime.utcnow().timestamp())}"
            
        elif accounting_system == "xero":
            # Simulate Xero API call
            logger.info(f"Would record payment in Xero for invoice {invoice_id}")
            # Generate a fake payment ID
            payment_id = f"XR-PMT-{invoice_id}-{int(datetime.utcnow().timestamp())}"
            
        elif accounting_system == "fortnox":
            # Simulate Fortnox API call
            logger.info(f"Would record payment in Fortnox for invoice {invoice_id}")
            # Generate a fake payment ID
            payment_id = f"FN-PMT-{invoice_id}-{int(datetime.utcnow().timestamp())}"
            
        elif accounting_system == "visma":
            # Simulate Visma API call
            logger.info(f"Would record payment in Visma for invoice {invoice_id}")
            # Generate a fake payment ID
            payment_id = f"VS-PMT-{invoice_id}-{int(datetime.utcnow().timestamp())}"
            
        else:
            # Unknown accounting system
            logger.error(f"Unknown accounting system: {accounting_system}")
            raise HTTPException(status_code=400, detail=f"Unsupported accounting system: {accounting_system}")
        
        return payment_id
    
    def sync_customers(self) -> Dict[str, Any]:
        """
        Sync customers between the lead system and accounting system
        
        Returns:
            Dict with sync results
        """
        # Get all leads with unique customer emails
        leads = self.db.query(Lead).all()
        
        # Extract unique customers
        customers = {}
        for lead in leads:
            if lead.customer_email not in customers:
                customers[lead.customer_email] = {
                    "name": lead.customer_name,
                    "email": lead.customer_email,
                    "phone": lead.customer_phone,
                    "address": lead.address,
                    "city": lead.city,
                    "postal_code": lead.postal_code,
                    "region": lead.region
                }
        
        # Sync customers with accounting system
        synced_count = self._sync_customers_with_accounting_system(list(customers.values()))
        
        return {
            "total_customers": len(customers),
            "synced_customers": synced_count,
            "synced_at": datetime.utcnow()
        }
    
    def _sync_customers_with_accounting_system(self, customers: List[Dict[str, Any]]) -> int:
        """
        Sync customers with the external accounting system
        
        Args:
            customers: List of customer data
            
        Returns:
            Number of customers synced
        """
        # In a real implementation, this would make API calls to the accounting system
        # For this example, we'll simulate the API call
        
        accounting_system = self.settings.accounting_system.lower()
        
        if accounting_system == "quickbooks":
            # Simulate QuickBooks API call
            logger.info(f"Would sync {len(customers)} customers with QuickBooks")
            
        elif accounting_system == "xero":
            # Simulate Xero API call
            logger.info(f"Would sync {len(customers)} customers with Xero")
            
        elif accounting_system == "fortnox":
            # Simulate Fortnox API call
            logger.info(f"Would sync {len(customers)} customers with Fortnox")
            
        elif accounting_system == "visma":
            # Simulate Visma API call
            logger.info(f"Would sync {len(customers)} customers with Visma")
            
        else:
            # Unknown accounting system
            logger.error(f"Unknown accounting system: {accounting_system}")
            raise HTTPException(status_code=400, detail=f"Unsupported accounting system: {accounting_system}")
        
        # Return number of customers synced
        return len(customers)
    
    def sync_invoices(self) -> Dict[str, Any]:
        """
        Sync invoices between the lead system and accounting system
        
        Returns:
            Dict with sync results
        """
        # Get all approved quotes that need invoicing
        quotes = self.db.query(Quote).filter(
            Quote.status == QuoteStatus.APPROVED,
            # In a real implementation, this would check if the quote has already been invoiced
            # For this example, we'll just get all approved quotes
        ).all()
        
        # Create invoices for each quote
        created_invoices = []
        for quote in quotes:
            try:
                invoice = self.create_invoice(quote.id)
                created_invoices.append(invoice)
            except Exception as e:
                logger.error(f"Error creating invoice for quote {quote.id}: {e}")
        
        return {
            "total_quotes": len(quotes),
            "created_invoices": len(created_invoices),
            "synced_at": datetime.utcnow()
        }
    
    def get_accounting_settings(self) -> AccountingSettings:
        """Get accounting integration settings"""
        return self.settings
    
    def update_accounting_settings(self, settings: AccountingSettings) -> AccountingSettings:
        """
        Update accounting integration settings
        
        Args:
            settings: New settings
            
        Returns:
            Updated settings
        """
        # In a real implementation, this would update settings in the database
        # For this example, we'll just log it
        logger.info(f"Would update accounting settings: {settings.dict()}")
        
        # Update settings
        self.settings = settings
        
        return self.settings
    
    def get_financial_accounts(self) -> List[Dict[str, Any]]:
        """
        Get list of financial accounts from the accounting system
        
        Returns:
            List of accounts
        """
        # In a real implementation, this would make API calls to the accounting system
        # For this example, we'll return sample accounts
        
        accounting_system = self.settings.accounting_system.lower()
        
        if accounting_system == "quickbooks":
            # Sample QuickBooks accounts
            accounts = [
                {"id": "1", "name": "Sales", "type": "Income", "balance": 0},
                {"id": "2", "name": "Accounts Receivable", "type": "Asset", "balance": 0},
                {"id": "3", "name": "Bank Account", "type": "Asset", "balance": 0},
                {"id": "4", "name": "Expenses", "type": "Expense", "balance": 0},
                {"id": "5", "name": "VAT", "type": "Liability", "balance": 0}
            ]
            
        elif accounting_system == "xero":
            # Sample Xero accounts
            accounts = [
                {"id": "1", "name": "Sales", "type": "Revenue", "balance": 0},
                {"id": "2", "name": "Accounts Receivable", "type": "Asset", "balance": 0},
                {"id": "3", "name": "Bank Account", "type": "Asset", "balance": 0},
                {"id": "4", "name": "Expenses", "type": "Expense", "balance": 0},
                {"id": "5", "name": "VAT", "type": "Liability", "balance": 0}
            ]
            
        elif accounting_system == "fortnox":
            # Sample Fortnox accounts
            accounts = [
                {"id": "3000", "name": "Försäljning", "type": "Intäkt", "balance": 0},
                {"id": "1500", "name": "Kundfordringar", "type": "Tillgång", "balance": 0},
                {"id": "1920", "name": "Bankkonto", "type": "Tillgång", "balance": 0},
                {"id": "5000", "name": "Kostnader", "type": "Kostnad", "balance": 0},
                {"id": "2610", "name": "Utgående moms", "type": "Skuld", "balance": 0}
            ]
            
        elif accounting_system == "visma":
            # Sample Visma accounts
            accounts = [
                {"id": "3000", "name": "Försäljning", "type": "Intäkt", "balance": 0},
                {"id": "1500", "name": "Kundfordringar", "type": "Tillgång", "balance": 0},
                {"id": "1920", "name": "Bankkonto", "type": "Tillgång", "balance": 0},
                {"id": "5000", "name": "Kostnader", "type": "Kostnad", "balance": 0},
                {"id": "2610", "name": "Utgående moms", "type": "Skuld", "balance": 0}
            ]
            
        else:
            # Unknown accounting system
            logger.error(f"Unknown accounting system: {accounting_system}")
            raise HTTPException(status_code=400, detail=f"Unsupported accounting system: {accounting_system}")
        
        return accounts
    
    def get_invoice_status(self, invoice_id: str) -> Dict[str, Any]:
        """
        Get status of an invoice from the accounting system
        
        Args:
            invoice_id: Invoice ID
            
        Returns:
            Dict with invoice status
        """
        # In a real implementation, this would make API calls to the accounting system
        # For this example, we'll return sample status
        
        # Generate random status for demo purposes
        import random
        statuses = ["draft", "sent", "viewed", "paid", "overdue"]
        status = random.choice(statuses)
        
        return {
            "invoice_id": invoice_id,
            "status": status,
            "amount": 1000.0,
            "amount_paid": 1000.0 if status == "paid" else 0.0,
            "due_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }


# API endpoints for accounting integration
@router.get("/accounting/settings", response_model=AccountingSettings)
def get_accounting_settings(
    db: Session = Depends(get_db)
):
    """Get accounting integration settings"""
    service = AccountingIntegrationService(db)
    return service.get_accounting_settings()

@router.post("/accounting/settings", response_model=AccountingSettings)
def update_accounting_settings(
    settings: AccountingSettings,
    db: Session = Depends(get_db)
):
    """Update accounting integration settings"""
    service = AccountingIntegrationService(db)
    return service.update_accounting_settings(settings)

@router.post("/accounting/invoices", response_model=Dict[str, Any])
def create_invoice(
    quote_id: int,
    db: Session = Depends(get_db)
):
    """Create an invoice for an approved quote"""
    service = AccountingIntegrationService(db)
    return service.create_invoice(quote_id)

@router.post("/accounting/payments", response_model=Dict[str, Any])
def record_payment(
    invoice_id: str,
    payment_data: PaymentData,
    db: Session = Depends(get_db)
):
    """Record a payment for an invoice"""
    service = AccountingIntegrationService(db)
    return service.record_payment(invoice_id, payment_data)

@router.post("/accounting/sync/customers", response_model=Dict[str, Any])
def sync_customers(
    db: Session = Depends(get_db)
):
    """Sync customers with accounting system"""
    service = AccountingIntegrationService(db)
    return service.sync_customers()

@router.post("/accounting/sync/invoices", response_model=Dict[str, Any])
def sync_invoices(
    db: Session = Depends(get_db)
):
    """Sync invoices with accounting system"""
    service = AccountingIntegrationService(db)
    return service.sync_invoices()

@router.get("/accounting/accounts", response_model=List[Dict[str, Any]])
def get_financial_accounts(
    db: Session = Depends(get_db)
):
    """Get list of financial accounts from accounting system"""
    service = AccountingIntegrationService(db)
    return service.get_financial_accounts()

@router.get("/accounting/invoices/{invoice_id}", response_model=Dict[str, Any])
def get_invoice_status(
    invoice_id: str,
    db: Session = Depends(get_db)
):
    """Get status of an invoice from accounting system"""
    service = AccountingIntegrationService(db)
    return service.get_invoice_status(invoice_id)
