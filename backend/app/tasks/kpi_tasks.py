from sqlalchemy.orm import Session
from app.services.kpi_service import KPIService

class KPITasks:
    def __init__(self, db: Session):
        self.db = db

    def run_daily_kpi_aggregation(self):
        kpi_service = KPIService(self.db)
        kpi_service.calculate_metrics(time_range="1d")
        print("Daily KPI aggregation completed")