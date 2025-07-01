"""
Receipt-related API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import logging

from app.database import get_db
from app.models.receipts import Receipt
from app.schemas.receipts import ReceiptCreate, ReceiptUpdate, ReceiptResponse, ReceiptSummary
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=PaginatedResponse[ReceiptResponse])
async def get_receipts(
    pagination: PaginationParams = Depends(),
    status: Optional[str] = Query(None, description="Filter by receipt status"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    payment_id: Optional[str] = Query(None, description="Filter by payment ID"),
    db: Session = Depends(get_db)
):
    """Get paginated receipts with optional filters"""
    try:
        query = db.query(Receipt)
        
        # Apply filters
        if status:
            query = query.filter(Receipt.receipt_status == status)
        if customer_id:
            query = query.filter(Receipt.customer_id == customer_id)
        if payment_id:
            query = query.filter(Receipt.payment_id == payment_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        receipts = query.offset(
            (pagination.page - 1) * pagination.size
        ).limit(pagination.size).all()
        
        return PaginatedResponse(
            items=receipts,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        logger.error(f"Error fetching receipts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch receipts"
        )

@router.get("/{receipt_number}", response_model=ReceiptResponse)
async def get_receipt(receipt_number: str, db: Session = Depends(get_db)):
    """Get a specific receipt by number"""
    try:
        receipt = db.query(Receipt).filter(Receipt.receipt_number == receipt_number).first()
        if not receipt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Receipt with number {receipt_number} not found"
            )
        return receipt
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching receipt {receipt_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch receipt"
        )

@router.post("/", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
async def create_receipt(receipt_data: ReceiptCreate, db: Session = Depends(get_db)):
    """Create a new receipt"""
    try:
        # Check if receipt number already exists
        existing = db.query(Receipt).filter(Receipt.receipt_number == receipt_data.receipt_number).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Receipt with number {receipt_data.receipt_number} already exists"
            )
        
        receipt = Receipt(**receipt_data.model_dump())
        db.add(receipt)
        db.commit()
        db.refresh(receipt)
        
        logger.info(f"Created receipt: {receipt.receipt_number}")
        return receipt
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating receipt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create receipt"
        )

@router.put("/{receipt_number}", response_model=ReceiptResponse)
async def update_receipt(
    receipt_number: str, 
    receipt_data: ReceiptUpdate, 
    db: Session = Depends(get_db)
):
    """Update a receipt"""
    try:
        receipt = db.query(Receipt).filter(Receipt.receipt_number == receipt_number).first()
        if not receipt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Receipt with number {receipt_number} not found"
            )
        
        # Update fields
        update_data = receipt_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(receipt, field, value)
        
        db.commit()
        db.refresh(receipt)
        
        logger.info(f"Updated receipt: {receipt.receipt_number}")
        return receipt
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating receipt {receipt_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update receipt"
        )

@router.delete("/{receipt_number}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_receipt(receipt_number: str, db: Session = Depends(get_db)):
    """Delete a receipt"""
    try:
        receipt = db.query(Receipt).filter(Receipt.receipt_number == receipt_number).first()
        if not receipt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Receipt with number {receipt_number} not found"
            )
        
        db.delete(receipt)
        db.commit()
        
        logger.info(f"Deleted receipt: {receipt_number}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting receipt {receipt_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete receipt"
        )

@router.get("/summary/stats", response_model=ReceiptSummary)
async def get_receipt_summary(db: Session = Depends(get_db)):
    """Get receipt statistics summary"""
    try:
        total_receipts = db.query(func.count(Receipt.id)).scalar()
        total_amount = db.query(func.sum(Receipt.amount)).scalar() or 0
        
        generated_receipts = db.query(func.count(Receipt.id)).filter(
            Receipt.receipt_status == "generated"
        ).scalar()
        
        sent_receipts = db.query(func.count(Receipt.id)).filter(
            Receipt.email_sent == True
        ).scalar()
        
        viewed_receipts = db.query(func.count(Receipt.id)).filter(
            Receipt.receipt_status == "viewed"
        ).scalar()
        
        return ReceiptSummary(
            total_receipts=total_receipts,
            total_amount=round(total_amount, 2),
            generated_receipts=generated_receipts,
            sent_receipts=sent_receipts,
            viewed_receipts=viewed_receipts
        )
        
    except Exception as e:
        logger.error(f"Error fetching receipt summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch receipt summary"
        )
