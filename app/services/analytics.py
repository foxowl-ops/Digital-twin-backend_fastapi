"""
Analytics service for dashboard metrics and insights
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from app.models.payments import Payment
from app.models.receipts import Receipt
from app.models.policies import Policy
from app.models.claims import Claim
from app.models.customers import Customer
from app.models.agents import Agent
from app.models.audit_logs import AuditLog

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for generating analytics and dashboard metrics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_dashboard_overview(self) -> Dict[str, Any]:
        """Get overall dashboard statistics"""
        try:
            # Count totals for each entity
            total_payments = self.db.query(func.count(Payment.id)).scalar() or 0
            total_receipts = self.db.query(func.count(Receipt.id)).scalar() or 0
            total_policies = self.db.query(func.count(Policy.id)).scalar() or 0
            total_claims = self.db.query(func.count(Claim.id)).scalar() or 0
            total_customers = self.db.query(func.count(Customer.id)).scalar() or 0
            total_agents = self.db.query(func.count(Agent.id)).scalar() or 0
            
            # Active counts
            active_policies = self.db.query(func.count(Policy.id)).filter(
                Policy.status == "active"
            ).scalar() or 0
            
            active_customers = self.db.query(func.count(Customer.id)).filter(
                Customer.status == "active"
            ).scalar() or 0
            
            active_agents = self.db.query(func.count(Agent.id)).filter(
                Agent.status == "active"
            ).scalar() or 0
            
            # Financial metrics
            total_premium = self.db.query(func.sum(Policy.premium_amount)).scalar() or 0
            total_coverage = self.db.query(func.sum(Policy.coverage_amount)).scalar() or 0
            total_payments_amount = self.db.query(func.sum(Payment.amount)).scalar() or 0
            total_claims_amount = self.db.query(func.sum(Claim.claim_amount)).scalar() or 0
            
            # Recent activity (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_payments = self.db.query(func.count(Payment.id)).filter(
                Payment.created_at >= thirty_days_ago
            ).scalar() or 0
            
            recent_claims = self.db.query(func.count(Claim.id)).filter(
                Claim.created_at >= thirty_days_ago
            ).scalar() or 0
            
            return {
                "totals": {
                    "payments": total_payments,
                    "receipts": total_receipts,
                    "policies": total_policies,
                    "claims": total_claims,
                    "customers": total_customers,
                    "agents": total_agents
                },
                "active": {
                    "policies": active_policies,
                    "customers": active_customers,
                    "agents": active_agents
                },
                "financial": {
                    "total_premium": round(total_premium, 2),
                    "total_coverage": round(total_coverage, 2),
                    "total_payments": round(total_payments_amount, 2),
                    "total_claims": round(total_claims_amount, 2)
                },
                "recent_activity": {
                    "payments_30d": recent_payments,
                    "claims_30d": recent_claims
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating dashboard overview: {str(e)}")
            raise
    
    async def get_payment_trends(self, period: str = "monthly", days: int = 30) -> Dict[str, Any]:
        """Get payment trends over time"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Group by period
            if period == "daily":
                date_format = "%Y-%m-%d"
                date_trunc = func.date(Payment.payment_date)
            elif period == "weekly":
                date_format = "%Y-W%U"
                date_trunc = func.strftime("%Y-W%U", Payment.payment_date)
            elif period == "monthly":
                date_format = "%Y-%m"
                date_trunc = func.strftime("%Y-%m", Payment.payment_date)
            else:
                date_format = "%Y"
                date_trunc = func.strftime("%Y", Payment.payment_date)
            
            # Query payment trends
            trends = self.db.query(
                date_trunc.label("period"),
                func.count(Payment.id).label("count"),
                func.sum(Payment.amount).label("total_amount"),
                func.avg(Payment.amount).label("avg_amount")
            ).filter(
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            ).group_by("period").order_by("period").all()
            
            # Format results
            trend_data = []
            for trend in trends:
                trend_data.append({
                    "period": trend.period,
                    "count": trend.count,
                    "total_amount": round(float(trend.total_amount or 0), 2),
                    "avg_amount": round(float(trend.avg_amount or 0), 2)
                })
            
            return {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "trends": trend_data
            }
            
        except Exception as e:
            logger.error(f"Error generating payment trends: {str(e)}")
            raise
    
    async def get_claims_analysis(self, period: str = "monthly") -> Dict[str, Any]:
        """Get claims analysis and statistics"""
        try:
            # Claims by status
            status_counts = self.db.query(
                Claim.status,
                func.count(Claim.id).label("count"),
                func.sum(Claim.claim_amount).label("total_amount")
            ).group_by(Claim.status).all()
            
            status_data = []
            for status in status_counts:
                status_data.append({
                    "status": status.status,
                    "count": status.count,
                    "total_amount": round(float(status.total_amount or 0), 2)
                })
            
            # Claims by type
            type_counts = self.db.query(
                Claim.claim_type,
                func.count(Claim.id).label("count"),
                func.avg(Claim.claim_amount).label("avg_amount")
            ).group_by(Claim.claim_type).all()
            
            type_data = []
            for claim_type in type_counts:
                type_data.append({
                    "type": claim_type.claim_type,
                    "count": claim_type.count,
                    "avg_amount": round(float(claim_type.avg_amount or 0), 2)
                })
            
            # Processing time analysis (for processed claims)
            processing_times = self.db.query(
                func.avg(
                    func.julianday(Claim.processed_date) - func.julianday(Claim.claim_date)
                ).label("avg_processing_days")
            ).filter(
                Claim.processed_date.isnot(None)
            ).scalar()
            
            return {
                "by_status": status_data,
                "by_type": type_data,
                "avg_processing_days": round(float(processing_times or 0), 1),
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating claims analysis: {str(e)}")
            raise
    
    async def get_policy_metrics(self, group_by: str = "type") -> Dict[str, Any]:
        """Get policy metrics grouped by specified field"""
        try:
            if group_by == "type":
                field = Policy.policy_type
            elif group_by == "status":
                field = Policy.status
            elif group_by == "agent":
                field = Policy.agent_name
            else:
                field = Policy.policy_type
            
            metrics = self.db.query(
                field.label("group"),
                func.count(Policy.id).label("count"),
                func.sum(Policy.premium_amount).label("total_premium"),
                func.sum(Policy.coverage_amount).label("total_coverage"),
                func.avg(Policy.premium_amount).label("avg_premium")
            ).group_by(field).all()
            
            metrics_data = []
            for metric in metrics:
                metrics_data.append({
                    "group": metric.group or "Unknown",
                    "count": metric.count,
                    "total_premium": round(float(metric.total_premium or 0), 2),
                    "total_coverage": round(float(metric.total_coverage or 0), 2),
                    "avg_premium": round(float(metric.avg_premium or 0), 2)
                })
            
            return {
                "grouped_by": group_by,
                "metrics": metrics_data,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating policy metrics: {str(e)}")
            raise
    
    async def get_agent_performance(self, limit: int = 10, metric: str = "premium") -> Dict[str, Any]:
        """Get top performing agents"""
        try:
            if metric == "premium":
                order_field = Agent.total_premium_written.desc()
                metric_field = Agent.total_premium_written
            elif metric == "policies":
                order_field = Agent.total_policies.desc()
                metric_field = Agent.total_policies
            elif metric == "commission":
                order_field = Agent.total_commission_earned.desc()
                metric_field = Agent.total_commission_earned
            else:
                order_field = Agent.total_premium_written.desc()
                metric_field = Agent.total_premium_written
            
            top_agents = self.db.query(
                Agent.agent_id,
                Agent.full_name,
                Agent.department,
                Agent.territory,
                metric_field.label("metric_value"),
                Agent.total_policies,
                Agent.active_policies,
                Agent.customer_satisfaction_score
            ).filter(
                Agent.status == "active"
            ).order_by(order_field).limit(limit).all()
            
            performance_data = []
            for agent in top_agents:
                performance_data.append({
                    "agent_id": agent.agent_id,
                    "name": agent.full_name,
                    "department": agent.department,
                    "territory": agent.territory,
                    "metric_value": float(agent.metric_value or 0),
                    "total_policies": agent.total_policies,
                    "active_policies": agent.active_policies,
                    "satisfaction_score": float(agent.customer_satisfaction_score or 0)
                })
            
            return {
                "metric": metric,
                "limit": limit,
                "top_performers": performance_data,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating agent performance: {str(e)}")
            raise
    
    async def get_customer_segmentation(self, segment_by: str = "type") -> Dict[str, Any]:
        """Get customer segmentation analysis"""
        try:
            if segment_by == "type":
                field = Customer.customer_type
            elif segment_by == "status":
                field = Customer.status
            elif segment_by == "vip":
                field = Customer.is_vip
            elif segment_by == "claims":
                field = Customer.has_claims
            else:
                field = Customer.customer_type
            
            segments = self.db.query(
                field.label("segment"),
                func.count(Customer.id).label("count")
            ).group_by(field).all()
            
            segment_data = []
            total_customers = self.db.query(func.count(Customer.id)).scalar() or 1
            
            for segment in segments:
                count = segment.count
                percentage = (count / total_customers) * 100
                segment_data.append({
                    "segment": str(segment.segment),
                    "count": count,
                    "percentage": round(percentage, 1)
                })
            
            return {
                "segmented_by": segment_by,
                "total_customers": total_customers,
                "segments": segment_data,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating customer segmentation: {str(e)}")
            raise
    
    async def get_revenue_analysis(self, period: str = "monthly", months: int = 12) -> Dict[str, Any]:
        """Get revenue analysis over time"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            # Premium revenue from policies
            premium_revenue = self.db.query(
                func.strftime("%Y-%m", Policy.created_at).label("month"),
                func.sum(Policy.premium_amount).label("premium_revenue")
            ).filter(
                Policy.created_at >= start_date,
                Policy.created_at <= end_date
            ).group_by("month").all()
            
            # Payment revenue
            payment_revenue = self.db.query(
                func.strftime("%Y-%m", Payment.payment_date).label("month"),
                func.sum(Payment.amount).label("payment_revenue")
            ).filter(
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date,
                Payment.payment_status == "completed"
            ).group_by("month").all()
            
            # Combine revenue data
            revenue_data = {}
            
            for premium in premium_revenue:
                month = premium.month
                if month not in revenue_data:
                    revenue_data[month] = {"month": month, "premium": 0, "payments": 0}
                revenue_data[month]["premium"] = round(float(premium.premium_revenue or 0), 2)
            
            for payment in payment_revenue:
                month = payment.month
                if month not in revenue_data:
                    revenue_data[month] = {"month": month, "premium": 0, "payments": 0}
                revenue_data[month]["payments"] = round(float(payment.payment_revenue or 0), 2)
            
            # Calculate total revenue
            for month_data in revenue_data.values():
                month_data["total"] = month_data["premium"] + month_data["payments"]
            
            # Sort by month
            sorted_revenue = sorted(revenue_data.values(), key=lambda x: x["month"])
            
            return {
                "period": period,
                "months_analyzed": months,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "revenue_by_month": sorted_revenue,
                "total_revenue": sum(item["total"] for item in sorted_revenue)
            }
            
        except Exception as e:
            logger.error(f"Error generating revenue analysis: {str(e)}")
            raise
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        try:
            # Database health
            db_status = "healthy"
            try:
                self.db.execute(text("SELECT 1"))
            except:
                db_status = "unhealthy"
            
            # Data freshness (last 24 hours)
            yesterday = datetime.now() - timedelta(days=1)
            recent_activity = {
                "payments": self.db.query(func.count(Payment.id)).filter(Payment.created_at >= yesterday).scalar() or 0,
                "policies": self.db.query(func.count(Policy.id)).filter(Policy.created_at >= yesterday).scalar() or 0,
                "claims": self.db.query(func.count(Claim.id)).filter(Claim.created_at >= yesterday).scalar() or 0,
                "customers": self.db.query(func.count(Customer.id)).filter(Customer.created_at >= yesterday).scalar() or 0
            }
            
            # Error rates from audit logs
            error_count = self.db.query(func.count(AuditLog.id)).filter(
                AuditLog.severity == "error",
                AuditLog.created_at >= yesterday
            ).scalar() or 0
            
            total_logs = self.db.query(func.count(AuditLog.id)).filter(
                AuditLog.created_at >= yesterday
            ).scalar() or 1
            
            error_rate = (error_count / total_logs) * 100
            
            return {
                "database_status": db_status,
                "recent_activity_24h": recent_activity,
                "error_rate_24h": round(error_rate, 2),
                "error_count_24h": error_count,
                "health_check_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking system health: {str(e)}")
            raise
    
    async def get_summary_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get comprehensive summary report"""
        try:
            # Payments summary
            payments_summary = self.db.query(
                func.count(Payment.id).label("count"),
                func.sum(Payment.amount).label("total_amount"),
                func.avg(Payment.amount).label("avg_amount")
            ).filter(
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            ).first()
            
            # Claims summary
            claims_summary = self.db.query(
                func.count(Claim.id).label("count"),
                func.sum(Claim.claim_amount).label("total_amount"),
                func.sum(Claim.approved_amount).label("approved_amount")
            ).filter(
                Claim.claim_date >= start_date,
                Claim.claim_date <= end_date
            ).first()
            
            # Policies summary
            policies_summary = self.db.query(
                func.count(Policy.id).label("count"),
                func.sum(Policy.premium_amount).label("total_premium"),
                func.sum(Policy.coverage_amount).label("total_coverage")
            ).filter(
                Policy.created_at >= start_date,
                Policy.created_at <= end_date
            ).first()
            
            # New customers
            new_customers = self.db.query(func.count(Customer.id)).filter(
                Customer.registration_date >= start_date,
                Customer.registration_date <= end_date
            ).scalar() or 0
            
            return {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": (end_date - start_date).days
                },
                "payments": {
                    "count": payments_summary.count or 0,
                    "total_amount": round(float(payments_summary.total_amount or 0), 2),
                    "avg_amount": round(float(payments_summary.avg_amount or 0), 2)
                },
                "claims": {
                    "count": claims_summary.count or 0,
                    "total_claimed": round(float(claims_summary.total_amount or 0), 2),
                    "total_approved": round(float(claims_summary.approved_amount or 0), 2)
                },
                "policies": {
                    "count": policies_summary.count or 0,
                    "total_premium": round(float(policies_summary.total_premium or 0), 2),
                    "total_coverage": round(float(policies_summary.total_coverage or 0), 2)
                },
                "customers": {
                    "new_customers": new_customers
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating summary report: {str(e)}")
            raise
