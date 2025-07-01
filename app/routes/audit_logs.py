"""
Audit log-related API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.models.audit_logs import AuditLog
from app.schemas.audit_logs import AuditLogCreate, AuditLogUpdate, AuditLogResponse, AuditLogSummary
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=PaginatedResponse[AuditLogResponse])
async def get_audit_logs(
    pagination: PaginationParams = Depends(),
    action: Optional[str] = Query(None, description="Filter by action"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db)
):
    """Get paginated audit logs with optional filters"""
    try:
        query = db.query(AuditLog)
        
        # Apply filters
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if severity:
            query = query.filter(AuditLog.severity == severity)
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        if start_date:
            query = query.filter(AuditLog.event_timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.event_timestamp <= end_date)
        
        # Order by timestamp descending (most recent first)
        query = query.order_by(AuditLog.event_timestamp.desc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        logs = query.offset(
            (pagination.page - 1) * pagination.size
        ).limit(pagination.size).all()
        
        return PaginatedResponse(
            items=logs,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        logger.error(f"Error fetching audit logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch audit logs"
        )

@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(log_id: str, db: Session = Depends(get_db)):
    """Get a specific audit log by ID"""
    try:
        log = db.query(AuditLog).filter(AuditLog.log_id == log_id).first()
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audit log with ID {log_id} not found"
            )
        return log
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching audit log {log_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch audit log"
        )

@router.post("/", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
async def create_audit_log(log_data: AuditLogCreate, db: Session = Depends(get_db)):
    """Create a new audit log"""
    try:
        # Check if log ID already exists
        existing = db.query(AuditLog).filter(AuditLog.log_id == log_data.log_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Audit log with ID {log_data.log_id} already exists"
            )
        
        audit_log = AuditLog(**log_data.model_dump())
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        logger.info(f"Created audit log: {audit_log.log_id}")
        return audit_log
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating audit log: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create audit log"
        )

@router.put("/{log_id}", response_model=AuditLogResponse)
async def update_audit_log(
    log_id: str, 
    log_data: AuditLogUpdate, 
    db: Session = Depends(get_db)
):
    """Update an audit log"""
    try:
        audit_log = db.query(AuditLog).filter(AuditLog.log_id == log_id).first()
        if not audit_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audit log with ID {log_id} not found"
            )
        
        # Update fields
        update_data = log_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(audit_log, field, value)
        
        db.commit()
        db.refresh(audit_log)
        
        logger.info(f"Updated audit log: {audit_log.log_id}")
        return audit_log
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating audit log {log_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update audit log"
        )

@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit_log(log_id: str, db: Session = Depends(get_db)):
    """Delete an audit log"""
    try:
        audit_log = db.query(AuditLog).filter(AuditLog.log_id == log_id).first()
        if not audit_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audit log with ID {log_id} not found"
            )
        
        db.delete(audit_log)
        db.commit()
        
        logger.info(f"Deleted audit log: {log_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting audit log {log_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete audit log"
        )

@router.get("/summary/stats", response_model=AuditLogSummary)
async def get_audit_log_summary(db: Session = Depends(get_db)):
    """Get audit log statistics summary"""
    try:
        total_logs = db.query(func.count(AuditLog.id)).scalar()
        
        success_logs = db.query(func.count(AuditLog.id)).filter(
            AuditLog.status == "success"
        ).scalar()
        
        error_logs = db.query(func.count(AuditLog.id)).filter(
            AuditLog.severity == "error"
        ).scalar()
        
        warning_logs = db.query(func.count(AuditLog.id)).filter(
            AuditLog.severity == "warning"
        ).scalar()
        
        sensitive_logs = db.query(func.count(AuditLog.id)).filter(
            AuditLog.is_sensitive == True
        ).scalar()
        
        logs_requiring_review = db.query(func.count(AuditLog.id)).filter(
            AuditLog.requires_review == True
        ).scalar()
        
        return AuditLogSummary(
            total_logs=total_logs,
            success_logs=success_logs,
            error_logs=error_logs,
            warning_logs=warning_logs,
            sensitive_logs=sensitive_logs,
            logs_requiring_review=logs_requiring_review
        )
        
    except Exception as e:
        logger.error(f"Error fetching audit log summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch audit log summary"
        )
