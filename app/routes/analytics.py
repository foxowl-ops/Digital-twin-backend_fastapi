"""
Analytics and dashboard metrics API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.services.analytics import AnalyticsService
from app.schemas.common import AnalyticsResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/dashboard/overview")
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """Get overall dashboard statistics"""
    try:
        analytics_service = AnalyticsService(db)
        overview = await analytics_service.get_dashboard_overview()
        return overview
        
    except Exception as e:
        logger.error(f"Error fetching dashboard overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard overview"
        )

@router.get("/payments/trends")
async def get_payment_trends(
    period: str = Query("monthly", description="Period: daily, weekly, monthly, yearly"),
    days: int = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """Get payment trends over time"""
    try:
        analytics_service = AnalyticsService(db)
        trends = await analytics_service.get_payment_trends(period=period, days=days)
        return trends
        
    except Exception as e:
        logger.error(f"Error fetching payment trends: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment trends"
        )

@router.get("/claims/analysis")
async def get_claims_analysis(
    period: str = Query("monthly", description="Period: daily, weekly, monthly, yearly"),
    db: Session = Depends(get_db)
):
    """Get claims analysis and statistics"""
    try:
        analytics_service = AnalyticsService(db)
        analysis = await analytics_service.get_claims_analysis(period=period)
        return analysis
        
    except Exception as e:
        logger.error(f"Error fetching claims analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch claims analysis"
        )

@router.get("/policies/metrics")
async def get_policy_metrics(
    group_by: str = Query("type", description="Group by: type, status, agent"),
    db: Session = Depends(get_db)
):
    """Get policy metrics grouped by specified field"""
    try:
        analytics_service = AnalyticsService(db)
        metrics = await analytics_service.get_policy_metrics(group_by=group_by)
        return metrics
        
    except Exception as e:
        logger.error(f"Error fetching policy metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch policy metrics"
        )

@router.get("/agents/performance")
async def get_agent_performance(
    limit: int = Query(10, description="Number of top agents to return"),
    metric: str = Query("premium", description="Metric: premium, policies, commission"),
    db: Session = Depends(get_db)
):
    """Get top performing agents"""
    try:
        analytics_service = AnalyticsService(db)
        performance = await analytics_service.get_agent_performance(limit=limit, metric=metric)
        return performance
        
    except Exception as e:
        logger.error(f"Error fetching agent performance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch agent performance"
        )

@router.get("/customers/segmentation")
async def get_customer_segmentation(
    segment_by: str = Query("type", description="Segment by: type, status, vip, claims"),
    db: Session = Depends(get_db)
):
    """Get customer segmentation analysis"""
    try:
        analytics_service = AnalyticsService(db)
        segmentation = await analytics_service.get_customer_segmentation(segment_by=segment_by)
        return segmentation
        
    except Exception as e:
        logger.error(f"Error fetching customer segmentation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch customer segmentation"
        )

@router.get("/revenue/analysis")
async def get_revenue_analysis(
    period: str = Query("monthly", description="Period: daily, weekly, monthly, yearly"),
    months: int = Query(12, description="Number of months to analyze"),
    db: Session = Depends(get_db)
):
    """Get revenue analysis over time"""
    try:
        analytics_service = AnalyticsService(db)
        analysis = await analytics_service.get_revenue_analysis(period=period, months=months)
        return analysis
        
    except Exception as e:
        logger.error(f"Error fetching revenue analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch revenue analysis"
        )

@router.get("/system/health")
async def get_system_health(db: Session = Depends(get_db)):
    """Get system health metrics"""
    try:
        analytics_service = AnalyticsService(db)
        health = await analytics_service.get_system_health()
        return health
        
    except Exception as e:
        logger.error(f"Error fetching system health: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch system health"
        )

@router.get("/reports/summary")
async def get_summary_report(
    start_date: Optional[datetime] = Query(None, description="Start date for report"),
    end_date: Optional[datetime] = Query(None, description="End date for report"),
    db: Session = Depends(get_db)
):
    """Get comprehensive summary report"""
    try:
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        analytics_service = AnalyticsService(db)
        report = await analytics_service.get_summary_report(start_date=start_date, end_date=end_date)
        return report
        
    except Exception as e:
        logger.error(f"Error generating summary report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate summary report"
        )
