"""
Claim-related API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import logging

from app.database import get_db
from app.models.claims import Claim
from app.schemas.claims import ClaimCreate, ClaimUpdate, ClaimResponse, ClaimSummary
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=PaginatedResponse[ClaimResponse])
async def get_claims(
    pagination: PaginationParams = Depends(),
    status: Optional[str] = Query(None, description="Filter by claim status"),
    claim_type: Optional[str] = Query(None, description="Filter by claim type"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    policy_number: Optional[str] = Query(None, description="Filter by policy number"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db)
):
    """Get paginated claims with optional filters"""
    try:
        query = db.query(Claim)
        
        # Apply filters
        if status:
            query = query.filter(Claim.status == status)
        if claim_type:
            query = query.filter(Claim.claim_type == claim_type)
        if customer_id:
            query = query.filter(Claim.customer_id == customer_id)
        if policy_number:
            query = query.filter(Claim.policy_number == policy_number)
        if priority:
            query = query.filter(Claim.priority == priority)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        claims = query.offset(
            (pagination.page - 1) * pagination.size
        ).limit(pagination.size).all()
        
        return PaginatedResponse(
            items=claims,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        logger.error(f"Error fetching claims: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch claims"
        )

@router.get("/{claim_number}", response_model=ClaimResponse)
async def get_claim(claim_number: str, db: Session = Depends(get_db)):
    """Get a specific claim by number"""
    try:
        claim = db.query(Claim).filter(Claim.claim_number == claim_number).first()
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Claim with number {claim_number} not found"
            )
        return claim
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching claim {claim_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch claim"
        )

@router.post("/", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
async def create_claim(claim_data: ClaimCreate, db: Session = Depends(get_db)):
    """Create a new claim"""
    try:
        # Check if claim number already exists
        existing = db.query(Claim).filter(Claim.claim_number == claim_data.claim_number).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Claim with number {claim_data.claim_number} already exists"
            )
        
        claim = Claim(**claim_data.model_dump())
        db.add(claim)
        db.commit()
        db.refresh(claim)
        
        logger.info(f"Created claim: {claim.claim_number}")
        return claim
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating claim: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create claim"
        )

@router.put("/{claim_number}", response_model=ClaimResponse)
async def update_claim(
    claim_number: str, 
    claim_data: ClaimUpdate, 
    db: Session = Depends(get_db)
):
    """Update a claim"""
    try:
        claim = db.query(Claim).filter(Claim.claim_number == claim_number).first()
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Claim with number {claim_number} not found"
            )
        
        # Update fields
        update_data = claim_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(claim, field, value)
        
        db.commit()
        db.refresh(claim)
        
        logger.info(f"Updated claim: {claim.claim_number}")
        return claim
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating claim {claim_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update claim"
        )

@router.delete("/{claim_number}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_claim(claim_number: str, db: Session = Depends(get_db)):
    """Delete a claim"""
    try:
        claim = db.query(Claim).filter(Claim.claim_number == claim_number).first()
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Claim with number {claim_number} not found"
            )
        
        db.delete(claim)
        db.commit()
        
        logger.info(f"Deleted claim: {claim_number}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting claim {claim_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete claim"
        )

@router.get("/summary/stats", response_model=ClaimSummary)
async def get_claim_summary(db: Session = Depends(get_db)):
    """Get claim statistics summary"""
    try:
        total_claims = db.query(func.count(Claim.id)).scalar()
        
        submitted_claims = db.query(func.count(Claim.id)).filter(
            Claim.status == "submitted"
        ).scalar()
        
        approved_claims = db.query(func.count(Claim.id)).filter(
            Claim.status == "approved"
        ).scalar()
        
        denied_claims = db.query(func.count(Claim.id)).filter(
            Claim.status == "denied"
        ).scalar()
        
        settled_claims = db.query(func.count(Claim.id)).filter(
            Claim.status == "settled"
        ).scalar()
        
        total_claim_amount = db.query(func.sum(Claim.claim_amount)).scalar() or 0
        total_approved_amount = db.query(func.sum(Claim.approved_amount)).scalar() or 0
        
        return ClaimSummary(
            total_claims=total_claims,
            submitted_claims=submitted_claims,
            approved_claims=approved_claims,
            denied_claims=denied_claims,
            settled_claims=settled_claims,
            total_claim_amount=round(total_claim_amount, 2),
            total_approved_amount=round(total_approved_amount, 2)
        )
        
    except Exception as e:
        logger.error(f"Error fetching claim summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch claim summary"
        )
