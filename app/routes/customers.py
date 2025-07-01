"""
Customer-related API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import logging

from app.database import get_db
from app.models.customers import Customer
from app.schemas.customers import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerSummary
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=PaginatedResponse[CustomerResponse])
async def get_customers(
    pagination: PaginationParams = Depends(),
    status: Optional[str] = Query(None, description="Filter by customer status"),  
    customer_type: Optional[str] = Query(None, description="Filter by customer type"),
    agent_id: Optional[str] = Query(None, description="Filter by primary agent ID"),
    db: Session = Depends(get_db)
):
    """Get paginated customers with optional filters"""
    try:
        query = db.query(Customer)
        
        # Apply filters
        if status:
            query = query.filter(Customer.status == status)
        if customer_type:
            query = query.filter(Customer.customer_type == customer_type)
        if agent_id:
            query = query.filter(Customer.primary_agent_id == agent_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        customers = query.offset(
            (pagination.page - 1) * pagination.size
        ).limit(pagination.size).all()
        
        return PaginatedResponse(
            items=customers,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        logger.error(f"Error fetching customers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch customers"
        )

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """Get a specific customer by ID"""
    try:
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        return customer
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer {customer_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch customer"
        )

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(customer_data: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer"""
    try:
        # Check if customer ID already exists
        existing = db.query(Customer).filter(Customer.customer_id == customer_data.customer_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with ID {customer_data.customer_id} already exists"
            )
        
        customer = Customer(**customer_data.model_dump())
        db.add(customer)
        db.commit()
        db.refresh(customer)
        
        logger.info(f"Created customer: {customer.customer_id}")
        return customer
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating customer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create customer"
        )

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str, 
    customer_data: CustomerUpdate, 
    db: Session = Depends(get_db)
):
    """Update a customer"""
    try:
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        
        # Update fields
        update_data = customer_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        db.commit()
        db.refresh(customer)
        
        logger.info(f"Updated customer: {customer.customer_id}")
        return customer
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating customer {customer_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update customer"
        )

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: str, db: Session = Depends(get_db)):
    """Delete a customer"""
    try:
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        
        db.delete(customer)
        db.commit()
        
        logger.info(f"Deleted customer: {customer_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting customer {customer_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete customer"
        )

@router.get("/summary/stats", response_model=CustomerSummary)
async def get_customer_summary(db: Session = Depends(get_db)):
    """Get customer statistics summary"""
    try:
        total_customers = db.query(func.count(Customer.id)).scalar()
        
        active_customers = db.query(func.count(Customer.id)).filter(
            Customer.status == "active"
        ).scalar()
        
        inactive_customers = db.query(func.count(Customer.id)).filter(
            Customer.status == "inactive"
        ).scalar()
        
        vip_customers = db.query(func.count(Customer.id)).filter(
            Customer.is_vip == True
        ).scalar()
        
        customers_with_claims = db.query(func.count(Customer.id)).filter(
            Customer.has_claims == True
        ).scalar()
        
        return CustomerSummary(
            total_customers=total_customers,
            active_customers=active_customers,
            inactive_customers=inactive_customers,
            vip_customers=vip_customers,
            customers_with_claims=customers_with_claims
        )
        
    except Exception as e:
        logger.error(f"Error fetching customer summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch customer summary"
        )
