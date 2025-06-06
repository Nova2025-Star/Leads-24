from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime, timedelta

from app.database import get_db
from app.models.kpi import KPIEvent, KPIMetric
from app.schemas.kpi import KPIEvent as KPIEventSchema, KPIMetric as KPIMetricSchema, KPIDashboard
from app.utils.kpi import calculate_metrics, get_kpi_dashboard_data

router = APIRouter()


@router.get("/events", response_model=List[KPIEventSchema])
def get_kpi_events(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[str] = None
):
    """
    Get KPI events. Only accessible by admin users.
    """
    query = db.query(KPIEvent)
    if event_type:
        query = query.filter(KPIEvent.event_type == event_type)
    
    return query.order_by(KPIEvent.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/metrics", response_model=List[KPIMetricSchema])
def get_kpi_metrics(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    metric_name: Optional[str] = None
):
    """
    Get KPI metrics. Only accessible by admin users.
    """
    query = db.query(KPIMetric)
    if metric_name:
        query = query.filter(KPIMetric.metric_name == metric_name)
    
    return query.order_by(KPIMetric.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/dashboard", response_model=KPIDashboard)
def get_kpi_dashboard(
    db: Session = Depends(get_db)
):
    """
    Get KPI dashboard data. Only accessible by admin users.
    """
    dashboard_data = get_kpi_dashboard_data(db)
    
    # Extract the metrics we need for the dashboard
    return {
        "lead_assignment_time": dashboard_data["metrics"].get("avg_lead_assignment_time", 0),
        "partner_response_time": dashboard_data["metrics"].get("avg_partner_response_time", 0),
        "quote_submission_time": dashboard_data["metrics"].get("avg_quote_submission_time", 0),
        "customer_decision_time": dashboard_data["metrics"].get("avg_customer_decision_time", 0),
        "missed_leads_count": dashboard_data["metrics"].get("missed_leads_count", 0),
        "quotes_accepted_percent": dashboard_data["metrics"].get("quotes_accepted_percent", 0),
        "average_job_value": dashboard_data["metrics"].get("average_job_value", 0),
        "total_revenue": dashboard_data["revenue"]["total_revenue"]
    }


@router.get("", response_model=dict)
@router.get("/", response_model=dict)
def get_kpi_data(
    time_range: str = Query("week", description="Time range for KPI data (day, week, month, year, all)"),
    db: Session = Depends(get_db)
):
    """
    Get KPI data with time range filter. Only accessible by admin users.
    This endpoint handles the /api/v1/admin/kpi?time_range=week request.
    """
    # Calculate date range based on time_range parameter
    end_date = datetime.utcnow()
    if time_range == "day":
        start_date = end_date - timedelta(days=1)
    elif time_range == "week":
        start_date = end_date - timedelta(weeks=1)
    elif time_range == "month":
        start_date = end_date - timedelta(days=30)
    elif time_range == "year":
        start_date = end_date - timedelta(days=365)
    else:  # "all"
        start_date = datetime(2000, 1, 1)  # A date far in the past
    
    # Query KPI events within the time range
    events = db.query(KPIEvent).filter(
        KPIEvent.created_at >= start_date,
        KPIEvent.created_at <= end_date
    ).order_by(KPIEvent.created_at.desc()).all()
    
    # Get metrics for the time range
    metrics = db.query(KPIMetric).filter(
        KPIMetric.created_at >= start_date,
        KPIMetric.created_at <= end_date
    ).order_by(KPIMetric.created_at.desc()).all()
    
    # Format the response
    return {
        "time_range": time_range,
        "events_count": len(events),
        "metrics_count": len(metrics),
        "events": [
            {
                "id": event.id,
                "event_type": event.event_type,
                "lead_id": event.lead_id,
                "user_id": event.user_id,
                "quote_id": event.quote_id,
                "data": event.data,
                "created_at": event.created_at
            } for event in events[:10]  # Limit to 10 events for performance
        ],
        "metrics": {
            metric.metric_name: metric.metric_value
            for metric in metrics if metric.metric_name in [
                "avg_lead_assignment_time",
                "avg_partner_response_time",
                "avg_quote_submission_time",
                "avg_customer_decision_time",
                "missed_leads_count",
                "quotes_accepted_percent",
                "average_job_value"
            ]
        }
    }


# Add a specific endpoint for time_range parameter to fix the 404 issue
@router.get("/time/{time_range}", response_model=dict)
def get_kpi_data_by_time(
    time_range: str,
    db: Session = Depends(get_db)
):
    """
    Get KPI data with time range filter using path parameter.
    This endpoint handles the /api/v1/admin/kpi/time/week request.
    """
    # Calculate date range based on time_range parameter
    end_date = datetime.utcnow()
    if time_range == "day":
        start_date = end_date - timedelta(days=1)
    elif time_range == "week":
        start_date = end_date - timedelta(weeks=1)
    elif time_range == "month":
        start_date = end_date - timedelta(days=30)
    elif time_range == "year":
        start_date = end_date - timedelta(days=365)
    else:  # "all"
        start_date = datetime(2000, 1, 1)  # A date far in the past
    
    # Query KPI events within the time range
    events = db.query(KPIEvent).filter(
        KPIEvent.created_at >= start_date,
        KPIEvent.created_at <= end_date
    ).order_by(KPIEvent.created_at.desc()).all()
    
    # Get metrics for the time range
    metrics = db.query(KPIMetric).filter(
        KPIMetric.created_at >= start_date,
        KPIMetric.created_at <= end_date
    ).order_by(KPIMetric.created_at.desc()).all()
    
    # Format the response
    return {
        "time_range": time_range,
        "events_count": len(events),
        "metrics_count": len(metrics),
        "events": [
            {
                "id": event.id,
                "event_type": event.event_type,
                "lead_id": event.lead_id,
                "user_id": event.user_id,
                "quote_id": event.quote_id,
                "data": event.data,
                "created_at": event.created_at
            } for event in events[:10]  # Limit to 10 events for performance
        ],
        "metrics": {
            metric.metric_name: metric.metric_value
            for metric in metrics if metric.metric_name in [
                "avg_lead_assignment_time",
                "avg_partner_response_time",
                "avg_quote_submission_time",
                "avg_customer_decision_time",
                "missed_leads_count",
                "quotes_accepted_percent",
                "average_job_value"
            ]
        }
    }


@router.post("/calculate-metrics")
def trigger_metric_calculation(
    db: Session = Depends(get_db)
):
    """
    Trigger calculation of KPI metrics. Only accessible by admin users.
    """
    result = calculate_metrics(db)
    return {"message": result}


@router.post("/log-event", response_model=KPIEventSchema)
def log_kpi_event(
    event_type: str,
    lead_id: Optional[int] = None,
    user_id: Optional[int] = None,
    quote_id: Optional[int] = None,
    data: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Log a KPI event. Used internally by the system.
    """
    kpi_event = KPIEvent(
        event_type=event_type,
        lead_id=lead_id,
        user_id=user_id,
        quote_id=quote_id,
        data=data
    )
    
    db.add(kpi_event)
    db.commit()
    db.refresh(kpi_event)
    
    return kpi_event
