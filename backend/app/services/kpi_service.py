# app/services/kpi_service.py
from app.models.kpi import KPIEvent, KPIMetric
from app.database import SessionLocal
import json
from datetime import datetime, timedelta

class KPIService:
    def __init__(self):
        self.db = SessionLocal()

    def log_event(self, event_type: str, lead_id=None, user_id=None, quote_id=None, data: dict = None):
        event = KPIEvent(
            event_type=event_type,
            lead_id=lead_id,
            user_id=user_id,
            quote_id=quote_id,
            data=json.dumps(data) if data else None,
        )
        self.db.add(event)
        self.db.commit()

    def record_metric(self, metric_name: str, metric_value: float, user_id=None, region=None, 
                      time_period: str = None, period_start: datetime = None, period_end: datetime = None):
        metric = KPIMetric(
            metric_name=metric_name,
            metric_value=metric_value,
            user_id=user_id,
            region=region,
            time_period=time_period,
            period_start=period_start,
            period_end=period_end
        )
        self.db.add(metric)
        self.db.commit()

    def get_recent_metrics(self, metric_name: str, days: int = 7):
        cutoff = datetime.utcnow() - timedelta(days=days)
        metrics = self.db.query(KPIMetric).filter(
            KPIMetric.metric_name == metric_name,
            KPIMetric.created_at >= cutoff
        ).all()
        return metrics

    def get_summary(self):
        # Example: summarize count of KPIEvents by event_type in last 30 days
        cutoff = datetime.utcnow() - timedelta(days=30)
        events = self.db.query(KPIEvent.event_type, func.count(KPIEvent.id)).filter(
            KPIEvent.created_at >= cutoff
        ).group_by(KPIEvent.event_type).all()
        return {event_type: count for event_type, count in events}
