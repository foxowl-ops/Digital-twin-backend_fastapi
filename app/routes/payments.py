"""
Payment-related API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
import logging

from app.database import get_db
from app.models.payments import Payment
from app.schemas.payments import PaymentCreate, PaymentUpdate, PaymentResponse, PaymentSummary
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=PaginatedResponse[PaymentResponse])
async def get_payments(
    pagination: PaginationParams = Depends(),
    status: Optional[str] = Query(None, description="Filter by payment status"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    policy_number: Optional[str] = Query(None, description="Filter by policy number"),
    db: Session = Depends(get_db)
):
    """Get paginated payments with optional filters"""
    try:
        query = db.query(Payment)
        
        # Apply filters
        if status:
            query = query.filter(Payment.payment_status == status)
        if customer_id:
            query = query.filter(Payment.customer_id == customer_id)
        if policy_number:
            query = query.filter(Payment.policy_number == policy_number)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        payments = query.offset(
            (pagination.page - 1) * pagination.size
        ).limit(pagination.size).all()
        
        return PaginatedResponse(
            items=payments,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        logger.error(f"Error fetching payments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payments"
        )

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str, db: Session = Depends(get_db)):
    """Get a specific payment by ID"""
    try:
        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment with ID {payment_id} not found"
            )
        return payment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching payment {payment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment"
        )

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(payment_data: PaymentCreate, db: Session = Depends(get_db)):
    """Create a new payment"""
    try:
        # Check if payment ID already exists
        existing = db.query(Payment).filter(Payment.payment_id == payment_data.payment_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment with ID {payment_data.payment_id} already exists"
            )
        
        payment = Payment(**payment_data.model_dump())
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        logger.info(f"Created payment: {payment.payment_id}")
        return payment
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment"
        )

@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: str, 
    payment_data: PaymentUpdate, 
    db: Session = Depends(get_db)
):
    """Update a payment"""
    try:
        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment with ID {payment_id} not found"
            )
        
        # Update fields
        update_data = payment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(payment, field, value)
        
        db.commit()
        db.refresh(payment)
        
        logger.info(f"Updated payment: {payment.payment_id}")
        return payment
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating payment {payment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update payment"
        )

@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(payment_id: str, db: Session = Depends(get_db)):
    """Delete a payment"""
    try:
        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment with ID {payment_id} not found"
            )
        
        db.delete(payment)
        db.commit()
        
        logger.info(f"Deleted payment: {payment_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting payment {payment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete payment"
        )

@router.get("/summary/stats", response_model=PaymentSummary)
async def get_payment_summary(db: Session = Depends(get_db)):
    """Get payment statistics summary"""
    try:
        total_payments = db.query(func.count(Payment.id)).scalar()
        total_amount = db.query(func.sum(Payment.amount)).scalar() or 0
        average_amount = db.query(func.avg(Payment.amount)).scalar() or 0
        
        successful_payments = db.query(func.count(Payment.id)).filter(
            Payment.payment_status == "completed"
        ).scalar()
        
        failed_payments = db.query(func.count(Payment.id)).filter(
            Payment.payment_status == "failed"
        ).scalar()
        
        pending_payments = db.query(func.count(Payment.id)).filter(
            Payment.payment_status == "pending"
        ).scalar()
        
        return PaymentSummary(
            total_payments=total_payments,
            total_amount=round(total_amount, 2),
            average_amount=round(average_amount, 2),
            successful_payments=successful_payments,
            failed_payments=failed_payments,
            pending_payments=pending_payments
        )
        
    except Exception as e:
        logger.error(f"Error fetching payment summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment summary"
        )
