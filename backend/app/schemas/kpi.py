from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class KPIEventBase(BaseModel):
    event_type: str
    lead_id: Optional[int] = None
    user_id: Optional[int] = None
    quote_id: Optional[int] = None
    data: Optional[str] = None


class KPIEventCreate(KPIEventBase):
    pass


class KPIEventInDBBase(KPIEventBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class KPIEvent(KPIEventInDBBase):
    pass


class KPIMetricBase(BaseModel):
    metric_name: str
    metric_value: float
    time_period: Optional[str] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    user_id: Optional[int] = None
    region: Optional[str] = None


class KPIMetricCreate(KPIMetricBase):
    pass


class KPIMetricUpdate(BaseModel):
    metric_value: Optional[float] = None
    period_end: Optional[datetime] = None


class KPIMetricInDBBase(KPIMetricBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class KPIMetric(KPIMetricInDBBase):
    pass


class KPIDashboard(BaseModel):
    lead_assignment_time: float  # Average time in hours
    partner_response_time: float  # Average time in hours
    quote_submission_time: float  # Average time in hours
    customer_decision_time: float  # Average time in hours
    missed_leads_count: int
    quotes_accepted_percent: float
    average_job_value: float
    total_revenue: float
