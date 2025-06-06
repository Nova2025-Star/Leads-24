from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from app.models.kpi import KPIEvent, KPIMetric
from app.models.lead import Lead, LeadStatus
from app.models.quote import Quote, QuoteStatus
from app.models.user import User, UserRole


def log_event(db: Session, event_type: str, lead_id=None, user_id=None, quote_id=None, data=None):
    """Helper function to log KPI events"""
    kpi_event = KPIEvent(
        event_type=event_type,
        lead_id=lead_id,
        user_id=user_id,
        quote_id=quote_id,
        data=data
    )
    db.add(kpi_event)
    db.commit()
    return kpi_event


def calculate_metrics(db: Session):
    """Calculate and store KPI metrics"""
    # Calculate lead assignment time (from creation to assignment)
    assigned_leads = db.query(Lead).filter(Lead.assigned_at.isnot(None)).all()
    if assigned_leads:
        total_assignment_time = sum((lead.assigned_at - lead.created_at).total_seconds() / 3600 for lead in assigned_leads)
        avg_assignment_time = total_assignment_time / len(assigned_leads)
        
        # Store metric
        assignment_metric = KPIMetric(
            metric_name="avg_lead_assignment_time",
            metric_value=avg_assignment_time,
            time_period="daily",
            period_start=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
            period_end=datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
        )
        db.add(assignment_metric)
    
    # Calculate partner response time (from assignment to acceptance/rejection)
    responded_leads = db.query(Lead).filter(Lead.accepted_at.isnot(None)).all()
    if responded_leads:
        total_response_time = sum((lead.accepted_at - lead.assigned_at).total_seconds() / 3600 for lead in responded_leads)
        avg_response_time = total_response_time / len(responded_leads)
        
        # Store metric
        response_metric = KPIMetric(
            metric_name="avg_partner_response_time",
            metric_value=avg_response_time,
            time_period="daily",
            period_start=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
            period_end=datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
        )
        db.add(response_metric)
    
    # Calculate quote submission time (from acceptance to quote)
    quoted_leads = db.query(Lead).filter(Lead.quoted_at.isnot(None)).all()
    if quoted_leads:
        total_quote_time = sum((lead.quoted_at - lead.accepted_at).total_seconds() / 3600 for lead in quoted_leads)
        avg_quote_time = total_quote_time / len(quoted_leads)
        
        # Store metric
        quote_metric = KPIMetric(
            metric_name="avg_quote_submission_time",
            metric_value=avg_quote_time,
            time_period="daily",
            period_start=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
            period_end=datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
        )
        db.add(quote_metric)
    
    # Calculate customer decision time (from quote to response)
    decided_leads = db.query(Lead).filter(Lead.customer_response_at.isnot(None)).all()
    if decided_leads:
        total_decision_time = sum((lead.customer_response_at - lead.quoted_at).total_seconds() / 3600 for lead in decided_leads)
        avg_decision_time = total_decision_time / len(decided_leads)
        
        # Store metric
        decision_metric = KPIMetric(
            metric_name="avg_customer_decision_time",
            metric_value=avg_decision_time,
            time_period="daily",
            period_start=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
            period_end=datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
        )
        db.add(decision_metric)
    
    # Count missed leads (expired)
    missed_leads_count = db.query(Lead).filter(Lead.status == LeadStatus.EXPIRED).count()
    missed_metric = KPIMetric(
        metric_name="missed_leads_count",
        metric_value=missed_leads_count,
        time_period="daily",
        period_start=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
        period_end=datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
    )
    db.add(missed_metric)
    
    # Calculate quote acceptance rate
    approved_quotes = db.query(Lead).filter(Lead.status == LeadStatus.APPROVED).count()
    total_quotes = db.query(Lead).filter(Lead.quoted_at.isnot(None)).count()
    quotes_accepted_percent = (approved_quotes / total_quotes * 100) if total_quotes else 0
    
    acceptance_metric = KPIMetric(
        metric_name="quotes_accepted_percent",
        metric_value=quotes_accepted_percent,
        time_period="daily",
        period_start=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
        period_end=datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
    )
    db.add(acceptance_metric)
    
    # Calculate average job value
    approved_quotes = db.query(Quote).filter(Quote.status == QuoteStatus.APPROVED).all()
    if approved_quotes:
        total_value = sum(quote.total_amount for quote in approved_quotes)
        avg_job_value = total_value / len(approved_quotes)
        
        value_metric = KPIMetric(
            metric_name="average_job_value",
            metric_value=avg_job_value,
            time_period="daily",
            period_start=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
            period_end=datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
        )
        db.add(value_metric)
    
    # Calculate total revenue (lead fees + commissions)
    total_lead_fees = db.query(Lead).count() * 500  # 500 SEK per lead
    total_commissions = sum(quote.commission_amount for quote in approved_quotes) if approved_quotes else 0
    total_revenue = total_lead_fees + total_commissions
    
    revenue_metric = KPIMetric(
        metric_name="total_revenue",
        metric_value=total_revenue,
        time_period="daily",
        period_start=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
        period_end=datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
    )
    db.add(revenue_metric)
    
    # Calculate metrics per partner
    partners = db.query(User).filter(User.role == UserRole.PARTNER).all()
    for partner in partners:
        # Count leads assigned to this partner
        assigned_count = db.query(Lead).filter(Lead.assigned_partner_id == partner.id).count()
        
        # Count leads accepted by this partner
        accepted_count = db.query(Lead).filter(
            Lead.assigned_partner_id == partner.id,
            Lead.status == LeadStatus.ACCEPTED
        ).count()
        
        # Calculate acceptance rate
        acceptance_rate = (accepted_count / assigned_count * 100) if assigned_count else 0
        
        partner_metric = KPIMetric(
            metric_name="partner_acceptance_rate",
            metric_value=acceptance_rate,
            time_period="daily",
            period_start=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
            period_end=datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999),
            user_id=partner.id
        )
        db.add(partner_metric)
    
    db.commit()
    return "Metrics calculated and stored"


def get_kpi_dashboard_data(db: Session):
    """Get KPI dashboard data for admin view"""
    # Get the latest metrics
    metrics = {}
    latest_metrics = db.query(KPIMetric).order_by(KPIMetric.created_at.desc()).all()
    
    for metric in latest_metrics:
        if metric.metric_name not in metrics:
            metrics[metric.metric_name] = metric.metric_value
    
    # Get counts by status
    status_counts = {}
    for status in LeadStatus:
        count = db.query(Lead).filter(Lead.status == status).count()
        status_counts[status.value] = count
    
    # Get revenue data
    total_leads = db.query(Lead).count()
    lead_revenue = total_leads * 500  # 500 SEK per lead
    
    approved_quotes = db.query(Quote).filter(Quote.status == QuoteStatus.APPROVED).all()
    commission_revenue = sum(quote.commission_amount for quote in approved_quotes) if approved_quotes else 0
    
    total_revenue = lead_revenue + commission_revenue
    
    # Combine all data
    dashboard_data = {
        "metrics": metrics,
        "status_counts": status_counts,
        "revenue": {
            "lead_revenue": lead_revenue,
            "commission_revenue": commission_revenue,
            "total_revenue": total_revenue
        }
    }
    
    return dashboard_data
