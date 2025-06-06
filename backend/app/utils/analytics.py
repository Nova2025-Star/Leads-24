from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, extract, cast, Date
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import logging
from pydantic import BaseModel

from app.database import get_db
from app.models.lead import Lead, LeadStatus
from app.models.quote import Quote, QuoteStatus, QuoteItem
from app.models.user import User, UserRole

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define API router
router = APIRouter()

# Define Pydantic models for analytics API
class DateRangeParams(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    time_unit: Optional[str] = "day"  # day, week, month, quarter, year

class PerformanceMetrics(BaseModel):
    total_leads: int
    assigned_leads: int
    accepted_leads: int
    quoted_leads: int
    approved_quotes: int
    declined_quotes: int
    expired_leads: int
    conversion_rate: float
    avg_response_time: float
    avg_quote_time: float
    avg_quote_value: float
    total_revenue: float
    lead_fees: float
    commissions: float

class AnalyticsService:
    """
    Service for advanced reporting and analytics for the T24 Arborist Lead System.
    Provides comprehensive data analysis and visualization capabilities.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_performance_metrics(self, start_date: Optional[datetime] = None, 
                               end_date: Optional[datetime] = None,
                               partner_id: Optional[int] = None) -> PerformanceMetrics:
        """
        Get key performance metrics for the specified date range and optional partner
        
        Args:
            start_date: Start date for metrics calculation
            end_date: End date for metrics calculation
            partner_id: Optional partner ID to filter metrics
            
        Returns:
            PerformanceMetrics object with calculated KPIs
        """
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Base query filters
        date_filter = and_(Lead.created_at >= start_date, Lead.created_at <= end_date)
        
        # Add partner filter if specified
        if partner_id:
            partner_filter = Lead.assigned_partner_id == partner_id
        else:
            partner_filter = True  # No filter
        
        # Get lead counts by status
        lead_query = self.db.query(
            func.count(Lead.id).label("total"),
            func.sum(case((Lead.status == LeadStatus.ASSIGNED, 1), else_=0)).label("assigned"),
            func.sum(case((Lead.status == LeadStatus.ACCEPTED, 1), else_=0)).label("accepted"),
            func.sum(case((Lead.status == LeadStatus.QUOTED, 1), else_=0)).label("quoted"),
            func.sum(case((Lead.status == LeadStatus.APPROVED, 1), else_=0)).label("approved"),
            func.sum(case((Lead.status == LeadStatus.DECLINED, 1), else_=0)).label("declined"),
            func.sum(case((Lead.status == LeadStatus.EXPIRED, 1), else_=0)).label("expired"),
        ).filter(date_filter, partner_filter).first()
        
        # Get quote metrics
        quote_query = self.db.query(
            func.count(Quote.id).label("total_quotes"),
            func.sum(case((Quote.status == QuoteStatus.APPROVED, 1), else_=0)).label("approved_quotes"),
            func.sum(case((Quote.status == QuoteStatus.DECLINED, 1), else_=0)).label("declined_quotes"),
            func.avg(Quote.total_amount).label("avg_quote_value"),
            func.sum(Quote.total_amount).label("total_quote_value"),
            func.sum(Quote.commission_amount).label("total_commission")
        )
        
        # Join with leads to apply filters
        quote_query = quote_query.join(Lead, Quote.lead_id == Lead.id)
        
        # Apply date and partner filters
        quote_query = quote_query.filter(date_filter, partner_filter)
        
        # Execute query
        quote_results = quote_query.first()
        
        # Calculate lead fees (500 SEK per assigned lead)
        lead_fees = (lead_query.assigned or 0) * 500
        
        # Calculate conversion rates
        if lead_query.assigned and lead_query.assigned > 0:
            conversion_rate = (quote_results.approved_quotes or 0) / lead_query.assigned * 100
        else:
            conversion_rate = 0
        
        # Calculate average response times
        response_time_query = self.db.query(
            func.avg(
                func.extract('epoch', Lead.accepted_at - Lead.assigned_at) / 3600
            ).label("avg_response_time")
        ).filter(
            Lead.assigned_at.isnot(None),
            Lead.accepted_at.isnot(None),
            date_filter,
            partner_filter
        ).first()
        
        # Calculate average quote creation time
        quote_time_query = self.db.query(
            func.avg(
                func.extract('epoch', Lead.quoted_at - Lead.accepted_at) / 3600
            ).label("avg_quote_time")
        ).filter(
            Lead.accepted_at.isnot(None),
            Lead.quoted_at.isnot(None),
            date_filter,
            partner_filter
        ).first()
        
        # Return metrics
        return PerformanceMetrics(
            total_leads=lead_query.total or 0,
            assigned_leads=lead_query.assigned or 0,
            accepted_leads=lead_query.accepted or 0,
            quoted_leads=lead_query.quoted or 0,
            approved_quotes=quote_results.approved_quotes or 0,
            declined_quotes=quote_results.declined_quotes or 0,
            expired_leads=lead_query.expired or 0,
            conversion_rate=round(conversion_rate, 2),
            avg_response_time=round(response_time_query.avg_response_time or 0, 2),
            avg_quote_time=round(quote_time_query.avg_quote_time or 0, 2),
            avg_quote_value=round(quote_results.avg_quote_value or 0, 2),
            total_revenue=round((quote_results.total_quote_value or 0) + lead_fees, 2),
            lead_fees=lead_fees,
            commissions=round(quote_results.total_commission or 0, 2)
        )
    
    def get_time_series_data(self, metric: str, start_date: datetime, end_date: datetime,
                            time_unit: str = "day", partner_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get time series data for a specific metric
        
        Args:
            metric: Metric to analyze (leads, quotes, revenue, etc.)
            start_date: Start date for time series
            end_date: End date for time series
            time_unit: Time unit for grouping (day, week, month, quarter, year)
            partner_id: Optional partner ID to filter data
            
        Returns:
            List of data points with date and value
        """
        # Validate time unit
        valid_time_units = ["day", "week", "month", "quarter", "year"]
        if time_unit not in valid_time_units:
            time_unit = "day"
        
        # Define date trunc function based on time unit
        if time_unit == "day":
            date_trunc = func.date_trunc('day', Lead.created_at)
        elif time_unit == "week":
            date_trunc = func.date_trunc('week', Lead.created_at)
        elif time_unit == "month":
            date_trunc = func.date_trunc('month', Lead.created_at)
        elif time_unit == "quarter":
            date_trunc = func.date_trunc('quarter', Lead.created_at)
        else:  # year
            date_trunc = func.date_trunc('year', Lead.created_at)
        
        # Base query filters
        date_filter = and_(Lead.created_at >= start_date, Lead.created_at <= end_date)
        
        # Add partner filter if specified
        if partner_id:
            partner_filter = Lead.assigned_partner_id == partner_id
        else:
            partner_filter = True  # No filter
        
        # Define query based on metric
        if metric == "leads":
            # Count leads by date
            query = self.db.query(
                date_trunc.label("date"),
                func.count(Lead.id).label("value")
            ).filter(date_filter, partner_filter).group_by("date").order_by("date")
            
        elif metric == "leads_by_status":
            # Count leads by status and date
            results = []
            
            for status in LeadStatus:
                status_query = self.db.query(
                    date_trunc.label("date"),
                    func.count(Lead.id).label("value")
                ).filter(
                    Lead.status == status,
                    date_filter,
                    partner_filter
                ).group_by("date").order_by("date").all()
                
                status_data = [{"date": row.date, "value": row.value} for row in status_query]
                results.append({"status": status, "data": status_data})
            
            return results
            
        elif metric == "quotes":
            # Count quotes by date
            query = self.db.query(
                date_trunc.label("date"),
                func.count(Quote.id).label("value")
            ).join(Lead, Quote.lead_id == Lead.id).filter(
                date_filter, partner_filter
            ).group_by("date").order_by("date")
            
        elif metric == "quote_value":
            # Sum quote values by date
            query = self.db.query(
                date_trunc.label("date"),
                func.sum(Quote.total_amount).label("value")
            ).join(Lead, Quote.lead_id == Lead.id).filter(
                date_filter, partner_filter
            ).group_by("date").order_by("date")
            
        elif metric == "revenue":
            # Calculate total revenue by date (lead fees + commissions)
            lead_fees_query = self.db.query(
                date_trunc.label("date"),
                (func.count(Lead.id) * 500).label("lead_fees")
            ).filter(
                Lead.status != LeadStatus.NEW,  # Only count assigned leads
                date_filter,
                partner_filter
            ).group_by("date")
            
            commission_query = self.db.query(
                date_trunc.label("date"),
                func.sum(Quote.commission_amount).label("commission")
            ).join(Lead, Quote.lead_id == Lead.id).filter(
                Quote.status == QuoteStatus.APPROVED,
                date_filter,
                partner_filter
            ).group_by("date")
            
            # Convert to pandas for easier merging
            lead_fees_df = pd.read_sql(lead_fees_query.statement, self.db.bind)
            commission_df = pd.read_sql(commission_query.statement, self.db.bind)
            
            # Merge dataframes
            if not lead_fees_df.empty and not commission_df.empty:
                merged_df = pd.merge(lead_fees_df, commission_df, on="date", how="outer").fillna(0)
                merged_df["value"] = merged_df["lead_fees"] + merged_df["commission"]
                merged_df = merged_df.sort_values("date")
                
                # Convert to list of dicts
                return merged_df[["date", "value"]].to_dict(orient="records")
            elif not lead_fees_df.empty:
                lead_fees_df["value"] = lead_fees_df["lead_fees"]
                lead_fees_df = lead_fees_df.sort_values("date")
                return lead_fees_df[["date", "value"]].to_dict(orient="records")
            elif not commission_df.empty:
                commission_df["value"] = commission_df["commission"]
                commission_df = commission_df.sort_values("date")
                return commission_df[["date", "value"]].to_dict(orient="records")
            else:
                return []
            
        elif metric == "conversion_rate":
            # Calculate conversion rate by date
            assigned_query = self.db.query(
                date_trunc.label("date"),
                func.count(Lead.id).label("assigned")
            ).filter(
                Lead.status != LeadStatus.NEW,
                date_filter,
                partner_filter
            ).group_by("date")
            
            converted_query = self.db.query(
                date_trunc.label("date"),
                func.count(Lead.id).label("converted")
            ).filter(
                Lead.status == LeadStatus.APPROVED,
                date_filter,
                partner_filter
            ).group_by("date")
            
            # Convert to pandas for easier calculation
            assigned_df = pd.read_sql(assigned_query.statement, self.db.bind)
            converted_df = pd.read_sql(converted_query.statement, self.db.bind)
            
            # Calculate conversion rate
            if not assigned_df.empty and not converted_df.empty:
                merged_df = pd.merge(assigned_df, converted_df, on="date", how="outer").fillna(0)
                merged_df["value"] = (merged_df["converted"] / merged_df["assigned"] * 100).replace([np.inf, -np.inf], 0)
                merged_df = merged_df.sort_values("date")
                
                # Convert to list of dicts
                return merged_df[["date", "value"]].to_dict(orient="records")
            else:
                return []
        
        else:
            # Invalid metric
            return []
        
        # Execute query and format results
        results = query.all()
        return [{"date": row.date, "value": row.value} for row in results]
    
    def get_regional_performance(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get performance metrics by region
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            List of regions with performance metrics
        """
        # Base query filters
        date_filter = and_(Lead.created_at >= start_date, Lead.created_at <= end_date)
        
        # Query leads by region
        region_query = self.db.query(
            Lead.region,
            func.count(Lead.id).label("total_leads"),
            func.sum(case((Lead.status == LeadStatus.ASSIGNED, 1), else_=0)).label("assigned_leads"),
            func.sum(case((Lead.status == LeadStatus.ACCEPTED, 1), else_=0)).label("accepted_leads"),
            func.sum(case((Lead.status == LeadStatus.QUOTED, 1), else_=0)).label("quoted_leads"),
            func.sum(case((Lead.status == LeadStatus.APPROVED, 1), else_=0)).label("approved_leads"),
            func.sum(case((Lead.status == LeadStatus.DECLINED, 1), else_=0)).label("declined_leads"),
            func.sum(case((Lead.status == LeadStatus.EXPIRED, 1), else_=0)).label("expired_leads"),
        ).filter(date_filter).group_by(Lead.region).order_by(desc("total_leads"))
        
        # Execute query
        regions = region_query.all()
        
        # Format results
        results = []
        for region in regions:
            # Calculate conversion rate
            if region.assigned_leads and region.assigned_leads > 0:
                conversion_rate = region.approved_leads / region.assigned_leads * 100
            else:
                conversion_rate = 0
            
            # Get quote data for this region
            quote_query = self.db.query(
                func.avg(Quote.total_amount).label("avg_quote_value"),
                func.sum(Quote.total_amount).label("total_quote_value"),
                func.sum(Quote.commission_amount).label("total_commission")
            ).join(Lead, Quote.lead_id == Lead.id).filter(
                Lead.region == region.region,
                date_filter
            ).first()
            
            # Calculate lead fees
            lead_fees = (region.assigned_leads or 0) * 500
            
            # Add to results
            results.append({
                "region": region.region,
                "total_leads": region.total_leads or 0,
                "assigned_leads": region.assigned_leads or 0,
                "accepted_leads": region.accepted_leads or 0,
                "quoted_leads": region.quoted_leads or 0,
                "approved_leads": region.approved_leads or 0,
                "declined_leads": region.declined_leads or 0,
                "expired_leads": region.expired_leads or 0,
                "conversion_rate": round(conversion_rate, 2),
                "avg_quote_value": round(quote_query.avg_quote_value or 0, 2),
                "total_revenue": round((quote_query.total_quote_value or 0) + lead_fees, 2),
                "lead_fees": lead_fees,
                "commissions": round(quote_query.total_commission or 0, 2)
            })
        
        return results
    
    def get_partner_performance(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get performance metrics by partner
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            List of partners with performance metrics
        """
        # Base query filters
        date_filter = and_(Lead.created_at >= start_date, Lead.created_at <= end_date)
        
        # Query leads by partner
        partner_query = self.db.query(
            Lead.assigned_partner_id,
            User.full_name.label("partner_name"),
            User.email.label("partner_email"),
            func.count(Lead.id).label("total_leads"),
            func.sum(case((Lead.status == LeadStatus.ACCEPTED, 1), else_=0)).label("accepted_leads"),
            func.sum(case((Lead.status == LeadStatus.REJECTED, 1), else_=0)).label("rejected_leads"),
            func.sum(case((Lead.status == LeadStatus.QUOTED, 1), else_=0)).label("quoted_leads"),
            func.sum(case((Lead.status == LeadStatus.APPROVED, 1), else_=0)).label("approved_leads"),
            func.sum(case((Lead.status == LeadStatus.DECLINED, 1), else_=0)).label("declined_leads"),
            func.sum(case((Lead.status == LeadStatus.EXPIRED, 1), else_=0)).label("expired_leads"),
        ).join(User, Lead.assigned_partner_id == User.id).filter(
            Lead.assigned_partner_id.isnot(None),
            date_filter
        ).group_by(Lead.assigned_partner_id, User.full_name, User.email).order_by(desc("total_leads"))
        
        # Execute query
        partners = partner_query.all()
        
        # Format results
        results = []
        for partner in partners:
            # Calculate acceptance rate
            if partner.total_leads and partner.total_leads > 0:
                acceptance_rate = partner.accepted_leads / partner.total_leads * 100
            else:
                acceptance_rate = 0
            
            # Calculate conversion rate
            if partner.accepted_leads and partner.accepted_leads > 0:
                conversion_rate = partner.approved_leads / partner.accepted_leads * 100
            else:
                conversion_rate = 0
            
            # Get quote data for this partner
            quote_query = self.db.query(
                func.count(Quote.id).label("total_quotes"),
                func.avg(Quote.total_amount).label("avg_quote_value"),
                func.sum(Quote.total_amount).label("total_quote_value"),
                func.sum(Quote.commission_amount).label("total_commission")
            ).join(Lead, Quote.lead_id == Lead.id).filter(
                Lead.assigned_partner_id == partner.assigned_partner_id,
                date_filter
            ).first()
            
            # Calculate response times
            response_time_query = self.db.query(
                func.avg(
                    func.extract('epoch', Lead.accepted_at - Lead.assigned_at) / 3600
                ).label("avg_response_time")
            ).filter(
                Lead.assigned_partner_id == partner.assigned_partner_id,
                Lead.assigned_at.isnot(None),
                Lead.accepted_at.isnot(None),
                date_filter
            ).first()
            
            # Calculate quote creation times
            quote_time_query = self.db.query(
                func.avg(
                    func.extract('epoch', Lead.quoted_at - Lead.accepted_at) / 3600
                ).label("avg_quote_time")
            ).filter(
                Lead.assigned_partner_id == partner.assigned_partner_id,
                Lead.accepted_at.isnot(None),
                Lead.quoted_at.isnot(None),
                date_filter
            ).first()
            
            # Calculate lead fees
            lead_fees = partner.total_leads * 500
            
            # Add to results
            results.append({
                "partner_id": partner.assigned_partner_id,
                "partner_name": partner.partner_name,
                "partner_email": partner.partner_email,
                "total_leads": partner.total_leads,
                "accepted_leads": partner.accepted_leads or 0,
                "rejected_leads": partner.rejected_leads or 0,
                "quoted_leads": partner.quoted_leads or 0,
                "approved_leads": partner.approved_leads or 0,
                "declined_leads": partner.declined_leads or 0,
                "expired_leads": partner.expired_leads or 0,
                "acceptance_rate": round(acceptance_rate, 2),
                "conversion_rate": round(conversion_rate, 2),
                "avg_response_time": round(response_time_query.avg_response_time or 0, 2),
                "avg_quote_time": round(quote_time_query.avg_quote_time or 0, 2),
                "total_quotes": quote_query.total_quotes or 0,
                "avg_quote_value": round(quote_query.avg_quote_value or 0, 2),
                "total_revenue": round((quote_query.total_quote_value or 0) + lead_fees, 2),
                "lead_fees": lead_fees,
                "commissions": round(quote_query.total_commission or 0, 2)
            })
        
        return results
    
    def get_tree_operation_analysis(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Analyze tree operations in quotes
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dict with tree species and operation type analysis
        """
        # Base query filters for quotes
        date_filter = and_(Quote.created_at >= start_date, Quote.created_at <= end_date)
        
        # Analyze tree species
        species_query = self.db.query(
            QuoteItem.tree_species,
            func.count(QuoteItem.id).label("count"),
            func.sum(QuoteItem.cost).label("total_cost"),
            func.avg(QuoteItem.cost).label("avg_cost")
        ).join(Quote, QuoteItem.quote_id == Quote.id).filter(
            date_filter
        ).group_by(QuoteItem.tree_species).order_by(desc("count"))
        
        # Analyze operation types
        operation_query = self.db.query(
            QuoteItem.operation_type,
            func.count(QuoteItem.id).label("count"),
            func.sum(QuoteItem.cost).label("total_cost"),
            func.avg(QuoteItem.cost).label("avg_cost")
        ).join(Quote, QuoteItem.quote_id == Quote.id).filter(
            date_filter
        ).group_by(QuoteItem.operation_type).order_by(desc("count"))
        
        # Execute queries
        species_results = species_query.all()
        operation_results = operation_query.all()
        
        # Format results
        species_data = []
        for species in species_results:
            species_data.append({
                "species": species.tree_species,
                "count": species.count,
                "total_cost": round(species.total_cost, 2),
                "avg_cost": round(species.avg_cost, 2)
            })
        
        operation_data = []
        for operation in operation_results:
            operation_data.append({
                "operation": operation.operation_type,
                "count": operation.count,
                "total_cost": round(operation.total_cost, 2),
                "avg_cost": round(operation.avg_cost, 2)
            })
        
        # Analyze species-operation combinations
        combo_query = self.db.query(
            QuoteItem.tree_species,
            QuoteItem.operation_type,
            func.count(QuoteItem.id).label("count"),
            func.sum(QuoteItem.cost).label("total_cost"),
            func.avg(QuoteItem.cost).label("avg_cost")
        ).join(Quote, QuoteItem.quote_id == Quote.id).filter(
            date_filter
        ).group_by(QuoteItem.tree_species, QuoteItem.operation_type).order_by(desc("count"))
        
        combo_results = combo_query.all()
        
        combo_data = []
        for combo in combo_results:
            combo_data.append({
                "species": combo.tree_species,
                "operation": combo.operation_type,
                "count": combo.count,
                "total_cost": round(combo.total_cost, 2),
                "avg_cost": round(combo.avg_cost, 2)
            })
        
        return {
            "species_analysis": species_data,
            "operation_analysis": operation_data,
            "combination_analysis": combo_data
        }
    
    def generate_financial_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate a financial report for the specified date range
        
        Args:
            start_date: Start date for report
            end_date: End date for report
            
        Returns:
            Dict with financial data
        """
        # Base query filters
        date_filter = and_(Lead.created_at >= start_date, Lead.created_at <= end_date)
        
        # Calculate lead fees
        lead_fees_query = self.db.query(
            func.count(Lead.id).label("assigned_leads")
        ).filter(
            Lead.status != LeadStatus.NEW,  # Only count assigned leads
            date_filter
        ).first()
        
        lead_fees = (lead_fees_query.assigned_leads or 0) * 500
        
        # Calculate commission revenue
        commission_query = self.db.query(
            func.sum(Quote.commission_amount).label("total_commission")
        ).join(Lead, Quote.lead_id == Lead.id).filter(
            Quote.status == QuoteStatus.APPROVED,
            date_filter
        ).first()
        
        commission_revenue = commission_query.total_commission or 0
        
        # Calculate total revenue
        total_revenue = lead_fees + commission_revenue
        
        # Calculate revenue by month
        monthly_revenue_query = self.db.query(
            func.date_trunc('month', Lead.created_at).label("month"),
            func.count(Lead.id).label("assigned_leads")
        ).filter(
            Lead.status != LeadStatus.NEW,
            date_filter
        ).group_by("month").order_by("month")
        
        monthly_commission_query = self.db.query(
            func.date_trunc('month', Quote.created_at).label("month"),
            func.sum(Quote.commission_amount).label("commission")
        ).join(Lead, Quote.lead_id == Lead.id).filter(
            Quote.status == QuoteStatus.APPROVED,
            date_filter
        ).group_by("month").order_by("month")
        
        # Convert to pandas for easier merging
        monthly_leads_df = pd.read_sql(monthly_revenue_query.statement, self.db.bind)
        monthly_commission_df = pd.read_sql(monthly_commission_query.statement, self.db.bind)
        
        # Calculate monthly revenue
        monthly_revenue = []
        
        if not monthly_leads_df.empty:
            monthly_leads_df["lead_fees"] = monthly_leads_df["assigned_leads"] * 500
            
            if not monthly_commission_df.empty:
                merged_df = pd.merge(monthly_leads_df, monthly_commission_df, on="month", how="outer").fillna(0)
                merged_df["total"] = merged_df["lead_fees"] + merged_df["commission"]
                
                for _, row in merged_df.iterrows():
                    monthly_revenue.append({
                        "month": row["month"],
                        "lead_fees": row["lead_fees"],
                        "commission": row["commission"],
                        "total": row["total"]
                    })
            else:
                for _, row in monthly_leads_df.iterrows():
                    monthly_revenue.append({
                        "month": row["month"],
                        "lead_fees": row["lead_fees"],
                        "commission": 0,
                        "total": row["lead_fees"]
                    })
        
        # Return financial report
        return {
            "start_date": start_date,
            "end_date": end_date,
            "lead_fees": lead_fees,
            "commission_revenue": commission_revenue,
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue
        }
    
    def export_data(self, entity_type: str, start_date: datetime, end_date: datetime) -> str:
        """
        Export data as JSON for the specified entity type and date range
        
        Args:
            entity_type: Type of entity to export (leads, quotes, etc.)
            start_date: Start date for export
            end_date: End date for export
            
        Returns:
            JSON string with exported data
        """
        # Base query filters
        date_filter = and_(Lead.created_at >= start_date, Lead.created_at <= end_date)
        
        if entity_type == "leads":
            # Export leads
            leads_query = self.db.query(Lead).filter(date_filter).order_by(Lead.created_at)
            leads = leads_query.all()
            
            # Convert to dict
            leads_data = []
            for lead in leads:
                leads_data.append({
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
                    "assigned_partner_id": lead.assigned_partner_id,
                    "assigned_at": lead.assigned_at.isoformat() if lead.assigned_at else None,
                    "accepted_at": lead.accepted_at.isoformat() if lead.accepted_at else None,
                    "quoted_at": lead.quoted_at.isoformat() if lead.quoted_at else None,
                    "customer_response_at": lead.customer_response_at.isoformat() if lead.customer_response_at else None,
                    "created_at": lead.created_at.isoformat(),
                    "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
                    "expires_at": lead.expires_at.isoformat() if lead.expires_at else None,
                    "lead_fee": lead.lead_fee,
                    "commission_percent": lead.commission_percent,
                    "billed": lead.billed
                })
            
            return json.dumps(leads_data, indent=2)
            
        elif entity_type == "quotes":
            # Export quotes with items
            quotes_query = self.db.query(Quote).join(Lead, Quote.lead_id == Lead.id).filter(date_filter).order_by(Quote.created_at)
            quotes = quotes_query.all()
            
            # Get all quote items
            quote_ids = [quote.id for quote in quotes]
            items_query = self.db.query(QuoteItem).filter(QuoteItem.quote_id.in_(quote_ids))
            items = items_query.all()
            
            # Group items by quote
            items_by_quote = {}
            for item in items:
                if item.quote_id not in items_by_quote:
                    items_by_quote[item.quote_id] = []
                
                items_by_quote[item.quote_id].append({
                    "id": item.id,
                    "quantity": item.quantity,
                    "tree_species": item.tree_species,
                    "operation_type": item.operation_type,
                    "custom_operation": item.custom_operation,
                    "cost": item.cost
                })
            
            # Convert quotes to dict
            quotes_data = []
            for quote in quotes:
                quotes_data.append({
                    "id": quote.id,
                    "lead_id": quote.lead_id,
                    "status": quote.status,
                    "total_amount": quote.total_amount,
                    "commission_amount": quote.commission_amount,
                    "sent_at": quote.sent_at.isoformat() if quote.sent_at else None,
                    "customer_response_at": quote.customer_response_at.isoformat() if quote.customer_response_at else None,
                    "created_at": quote.created_at.isoformat(),
                    "updated_at": quote.updated_at.isoformat() if quote.updated_at else None,
                    "items": items_by_quote.get(quote.id, [])
                })
            
            return json.dumps(quotes_data, indent=2)
            
        elif entity_type == "partners":
            # Export partner performance
            partners = self.get_partner_performance(start_date, end_date)
            return json.dumps(partners, indent=2)
            
        elif entity_type == "regions":
            # Export regional performance
            regions = self.get_regional_performance(start_date, end_date)
            return json.dumps(regions, indent=2)
            
        elif entity_type == "financial":
            # Export financial report
            financial = self.generate_financial_report(start_date, end_date)
            return json.dumps(financial, indent=2)
            
        else:
            # Invalid entity type
            return json.dumps({"error": "Invalid entity type"})


# API endpoints for analytics
@router.get("/analytics/performance", response_model=PerformanceMetrics)
def get_performance_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    partner_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get key performance metrics"""
    service = AnalyticsService(db)
    return service.get_performance_metrics(start_date, end_date, partner_id)

@router.get("/analytics/timeseries/{metric}", response_model=List[Dict[str, Any]])
def get_time_series(
    metric: str,
    start_date: datetime,
    end_date: datetime,
    time_unit: str = "day",
    partner_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get time series data for a specific metric"""
    service = AnalyticsService(db)
    return service.get_time_series_data(metric, start_date, end_date, time_unit, partner_id)

@router.get("/analytics/regions", response_model=List[Dict[str, Any]])
def get_regional_performance(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """Get performance metrics by region"""
    service = AnalyticsService(db)
    return service.get_regional_performance(start_date, end_date)

@router.get("/analytics/partners", response_model=List[Dict[str, Any]])
def get_partner_performance(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """Get performance metrics by partner"""
    service = AnalyticsService(db)
    return service.get_partner_performance(start_date, end_date)

@router.get("/analytics/tree-operations", response_model=Dict[str, Any])
def get_tree_operation_analysis(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """Analyze tree operations in quotes"""
    service = AnalyticsService(db)
    return service.get_tree_operation_analysis(start_date, end_date)

@router.get("/analytics/financial", response_model=Dict[str, Any])
def get_financial_report(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """Generate a financial report"""
    service = AnalyticsService(db)
    return service.generate_financial_report(start_date, end_date)

@router.get("/analytics/export/{entity_type}")
def export_data(
    entity_type: str,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """Export data as JSON"""
    service = AnalyticsService(db)
    data = service.export_data(entity_type, start_date, end_date)
    
    # Return as JSON response
    return Response(
        content=data,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={entity_type}_{start_date.date()}_{end_date.date()}.json"}
    )
