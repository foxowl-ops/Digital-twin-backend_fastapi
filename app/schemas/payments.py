"""
Payment-related Pydantic schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.schemas.common import BaseSchema, TimestampMixin

class PaymentBase(BaseSchema):
    """Base payment schema"""
    payment_id: str = Field(..., description="Unique payment identifier")
    transaction_reference: str = Field(..., description="Transaction reference number")
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field(default="USD", description="Currency code")
    payment_method: str = Field(..., description="Payment method")
    payment_status: str = Field(..., description="Payment status")
    policy_number: Optional[str] = Field(None, description="Related policy number")
    customer_id: Optional[str] = Field(None, description="Customer identifier")
    agent_id: Optional[str] = Field(None, description="Agent identifier")
    payment_date: datetime = Field(..., description="Payment date")
    due_date: Optional[datetime] = Field(None, description="Due date")
    description: Optional[str] = Field(None, description="Payment description")
    gateway_transaction_id: Optional[str] = Field(None, description="Gateway transaction ID")
    processing_fee: float = Field(default=0.0, ge=0, description="Processing fee")
    is_recurring: bool = Field(default=False, description="Is recurring payment")
    is_late_payment: bool = Field(default=False, description="Is late payment")

class PaymentCreate(PaymentBase):
    """Schema for creating payments"""
    pass

class PaymentUpdate(BaseSchema):
    """Schema for updating payments"""
    transaction_reference: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = None
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None
    policy_number: Optional[str] = None
    customer_id: Optional[str] = None
    agent_id: Optional[str] = None
    payment_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    description: Optional[str] = None
    gateway_transaction_id: Optional[str] = None
    processing_fee: Optional[float] = Field(None, ge=0)
    is_recurring: Optional[bool] = None
    is_late_payment: Optional[bool] = None

class PaymentResponse(PaymentBase, TimestampMixin):
    """Schema for payment responses"""
    id: int
    uuid: str
    
    @validator('amount', 'processing_fee')
    def validate_amounts(cls, v):
        return round(float(v), 2)

class PaymentSummary(BaseSchema):
    """Payment summary schema"""
    total_payments: int
    total_amount: float
    average_amount: float
    successful_payments: int
    failed_payments: int
    pending_payments: int
