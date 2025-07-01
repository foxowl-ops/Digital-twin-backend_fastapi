"""
Policy-related Pydantic schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.schemas.common import BaseSchema, TimestampMixin

class PolicyBase(BaseSchema):
    """Base policy schema"""
    policy_number: str = Field(..., description="Unique policy number")
    policy_type: str = Field(..., description="Policy type")
    premium_amount: float = Field(..., gt=0, description="Premium amount")
    coverage_amount: float = Field(..., gt=0, description="Coverage amount")
    deductible: float = Field(default=0.0, ge=0, description="Deductible amount")
    currency: str = Field(default="USD", description="Currency code")
    effective_date: datetime = Field(..., description="Policy effective date")
    expiration_date: datetime = Field(..., description="Policy expiration date")
    renewal_date: Optional[datetime] = Field(None, description="Policy renewal date")
    customer_id: str = Field(..., description="Customer identifier")
    customer_name: str = Field(..., description="Customer name")
    agent_id: Optional[str] = Field(None, description="Agent identifier")
    agent_name: Optional[str] = Field(None, description="Agent name")
    status: str = Field(..., description="Policy status")
    payment_frequency: str = Field(..., description="Payment frequency")
    next_payment_due: Optional[datetime] = Field(None, description="Next payment due date")
    description: Optional[str] = Field(None, description="Policy description")
    terms_conditions: Optional[str] = Field(None, description="Terms and conditions")
    auto_renewal: bool = Field(default=False, description="Auto renewal flag")
    is_group_policy: bool = Field(default=False, description="Group policy flag")

class PolicyCreate(PolicyBase):
    """Schema for creating policies"""
    pass

class PolicyUpdate(BaseSchema):
    """Schema for updating policies"""
    policy_type: Optional[str] = None
    premium_amount: Optional[float] = Field(None, gt=0)
    coverage_amount: Optional[float] = Field(None, gt=0)
    deductible: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = None
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    renewal_date: Optional[datetime] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    status: Optional[str] = None
    payment_frequency: Optional[str] = None
    next_payment_due: Optional[datetime] = None
    description: Optional[str] = None
    terms_conditions: Optional[str] = None
    auto_renewal: Optional[bool] = None
    is_group_policy: Optional[bool] = None

class PolicyResponse(PolicyBase, TimestampMixin):
    """Schema for policy responses"""
    id: int
    uuid: str
    
    @validator('premium_amount', 'coverage_amount', 'deductible')
    def validate_amounts(cls, v):
        return round(float(v), 2)

class PolicySummary(BaseSchema):
    """Policy summary schema"""
    total_policies: int
    active_policies: int
    expired_policies: int
    total_premium: float
    total_coverage: float
