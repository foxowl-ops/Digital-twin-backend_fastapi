"""
Receipt-related Pydantic schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.schemas.common import BaseSchema, TimestampMixin

class ReceiptBase(BaseSchema):
    """Base receipt schema"""
    receipt_number: str = Field(..., description="Unique receipt number")
    payment_id: str = Field(..., description="Related payment ID")
    amount: float = Field(..., gt=0, description="Receipt amount")
    currency: str = Field(default="USD", description="Currency code")
    receipt_date: datetime = Field(..., description="Receipt date")
    policy_number: Optional[str] = Field(None, description="Related policy number")
    customer_id: Optional[str] = Field(None, description="Customer identifier")
    customer_name: str = Field(..., description="Customer name")
    customer_email: Optional[str] = Field(None, description="Customer email")
    description: Optional[str] = Field(None, description="Receipt description")
    payment_method: str = Field(..., description="Payment method")
    receipt_status: str = Field(default="generated", description="Receipt status")
    email_sent: bool = Field(default=False, description="Email sent flag")
    email_sent_at: Optional[datetime] = Field(None, description="Email sent timestamp")

class ReceiptCreate(ReceiptBase):
    """Schema for creating receipts"""
    pass

class ReceiptUpdate(BaseSchema):
    """Schema for updating receipts"""
    receipt_number: Optional[str] = None
    payment_id: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = None
    receipt_date: Optional[datetime] = None
    policy_number: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    description: Optional[str] = None
    payment_method: Optional[str] = None
    receipt_status: Optional[str] = None
    email_sent: Optional[bool] = None
    email_sent_at: Optional[datetime] = None

class ReceiptResponse(ReceiptBase, TimestampMixin):
    """Schema for receipt responses"""
    id: int
    uuid: str
    receipt_file_path: Optional[str] = None
    file_size: Optional[int] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        return round(float(v), 2)

class ReceiptSummary(BaseSchema):
    """Receipt summary schema"""
    total_receipts: int
    total_amount: float
    generated_receipts: int
    sent_receipts: int
    viewed_receipts: int
