from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from app.database import get_db
from app.models.quote import Quote, QuoteStatus, QuoteItem
from app.models.lead import Lead
from app.config import settings

router = APIRouter()

def send_email(to_email: str, subject: str, html_content: str):
    """
    Utility function to send emails.
    In a production environment, this would connect to a real SMTP server.
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.EMAIL_FROM
        message["To"] = to_email
        
        # Add HTML content
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # For development, we'll just log the email content
        print(f"Email would be sent to: {to_email}")
        print(f"Subject: {subject}")
        print(f"Content: {html_content}")
        
        # In production, uncomment this code to actually send emails
        """
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, to_email, message.as_string())
        """
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def format_quote_email(quote: Quote, lead: Lead, items: List[QuoteItem]):
    """
    Format a quote email to send to the customer.
    """
    # Calculate total
    total = sum(item.cost for item in items)
    
    # Format items as HTML table rows
    items_html = ""
    for item in items:
        items_html += f"""
        <tr>
            <td>{item.quantity}</td>
            <td>{item.tree_species}</td>
            <td>{item.operation_type}</td>
            <td>{item.cost} SEK</td>
        </tr>
        """
    
    # Create HTML email
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .total {{ font-weight: bold; }}
        </style>
    </head>
    <body>
        <h2>Arborist Quote for {lead.customer_name}</h2>
        <p>Dear {lead.customer_name},</p>
        <p>Thank you for your inquiry. Please find your quote details below:</p>
        
        <h3>Quote Details</h3>
        <table>
            <tr>
                <th>Quantity</th>
                <th>Tree Species</th>
                <th>Operation</th>
                <th>Cost (SEK)</th>
            </tr>
            {items_html}
            <tr class="total">
                <td colspan="3">Total</td>
                <td>{total} SEK</td>
            </tr>
        </table>
        
        <h3>Property Information</h3>
        <p>Address: {lead.address}, {lead.city}, {lead.postal_code}</p>
        
        <p>To approve this quote, please reply to this email with "APPROVE". 
        If you have any questions or would like to discuss modifications, 
        please contact us.</p>
        
        <p>This quote is valid for 30 days from the date of this email.</p>
        
        <p>Best regards,<br>
        T24 Arborist Services</p>
    </body>
    </html>
    """
    
    return html

@router.post("/quotes/{quote_id}/email", response_model=dict)
def email_quote_to_customer(
    quote_id: int,
    db: Session = Depends(get_db)
):
    """
    Send a quote email to the customer.
    """
    # Get the quote
    db_quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if db_quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Get the lead
    db_lead = db.query(Lead).filter(Lead.id == db_quote.lead_id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get quote items
    db_items = db.query(QuoteItem).filter(QuoteItem.quote_id == quote_id).all()
    
    # Format email
    html_content = format_quote_email(db_quote, db_lead, db_items)
    
    # Send email
    subject = f"Your Arborist Quote - T24 Lead System"
    result = send_email(db_lead.customer_email, subject, html_content)
    
    if result:
        # Update quote status
        db_quote.status = QuoteStatus.SENT
        db_quote.sent_at = datetime.utcnow()
        db.add(db_quote)
        db.commit()
        
        return {"status": "success", "message": f"Quote email sent to {db_lead.customer_email}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send email")
