"""
Policy-related API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import logging

from app.database import get_db
from app.models.policies import Policy
from app.schemas.policies import PolicyCreate, PolicyUpdate, PolicyResponse, PolicySummary
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=PaginatedResponse[PolicyResponse])
async def get_policies(
    pagination: PaginationParams = Depends(),
    status: Optional[str] = Query(None, description="Filter by policy status"),
    policy_type: Optional[str] = Query(None, description="Filter by policy type"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    db: Session = Depends(get_db)
):
    """Get paginated policies with optional filters"""
    try:
        query = db.query(Policy)
        
        # Apply filters
        if status:
            query = query.filter(Policy.status == status)
        if policy_type:
            query = query.filter(Policy.policy_type == policy_type)
        if customer_id:
            query = query.filter(Policy.customer_id == customer_id)
        if agent_id:
            query = query.filter(Policy.agent_id == agent_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        policies = query.offset(
            (pagination.page - 1) * pagination.size
        ).limit(pagination.size).all()
        
        return PaginatedResponse(
            items=policies,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        logger.error(f"Error fetching policies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch policies"
        )

@router.get("/{policy_number}", response_model=PolicyResponse)
async def get_policy(policy_number: str, db: Session = Depends(get_db)):
    """Get a specific policy by number"""
    try:
        policy = db.query(Policy).filter(Policy.policy_number == policy_number).first()
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy with number {policy_number} not found"
            )
        return policy
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching policy {policy_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch policy"
        )

@router.post("/", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(policy_data: PolicyCreate, db: Session = Depends(get_db)):
    """Create a new policy"""
    try:
        # Check if policy number already exists
        existing = db.query(Policy).filter(Policy.policy_number == policy_data.policy_number).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Policy with number {policy_data.policy_number} already exists"
            )
        
        policy = Policy(**policy_data.model_dump())
        db.add(policy)
        db.commit()
        db.refresh(policy)
        
        logger.info(f"Created policy: {policy.policy_number}")
        return policy
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create policy"
        )

@router.put("/{policy_number}", response_model=PolicyResponse)
async def update_policy(
    policy_number: str, 
    policy_data: PolicyUpdate, 
    db: Session = Depends(get_db)
):
    """Update a policy"""
    try:
        policy = db.query(Policy).filter(Policy.policy_number == policy_number).first()
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy with number {policy_number} not found"
            )
        
        # Update fields
        update_data = policy_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(policy, field, value)
        
        db.commit()
        db.refresh(policy)
        
        logger.info(f"Updated policy: {policy.policy_number}")
        return policy
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating policy {policy_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update policy"
        )

@router.delete("/{policy_number}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(policy_number: str, db: Session = Depends(get_db)):
    """Delete a policy"""
    try:
        policy = db.query(Policy).filter(Policy.policy_number == policy_number).first()
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy with number {policy_number} not found"
            )
        
        db.delete(policy)
        db.commit()
        
        logger.info(f"Deleted policy: {policy_number}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting policy {policy_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete policy"
        )

@router.get("/summary/stats", response_model=PolicySummary)
async def get_policy_summary(db: Session = Depends(get_db)):
    """Get policy statistics summary"""
    try:
        total_policies = db.query(func.count(Policy.id)).scalar()
        
        active_policies = db.query(func.count(Policy.id)).filter(
            Policy.status == "active"
        ).scalar()
        
        expired_policies = db.query(func.count(Policy.id)).filter(
            Policy.status == "expired"
        ).scalar()
        
        total_premium = db.query(func.sum(Policy.premium_amount)).scalar() or 0
        total_coverage = db.query(func.sum(Policy.coverage_amount)).scalar() or 0
        
        return PolicySummary(
            total_policies=total_policies,
            active_policies=active_policies,
            expired_policies=expired_policies,
            total_premium=round(total_premium, 2),
            total_coverage=round(total_coverage, 2)
        )
        
    except Exception as e:
        logger.error(f"Error fetching policy summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch policy summary"
        )
