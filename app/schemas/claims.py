"""
Claim-related Pydantic schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.schemas.common import BaseSchema, TimestampMixin

class ClaimBase(BaseSchema):
    """Base claim schema"""
    claim_number: str = Field(..., description="Unique claim number")
    policy_number: str = Field(..., description="Related policy number")
    claim_type: str = Field(..., description="Claim type")
    claim_amount: float = Field(..., gt=0, description="Claim amount")
    approved_amount: Optional[float] = Field(None, ge=0, description="Approved amount")
    currency: str = Field(default="USD", description="Currency code")
    incident_date: datetime = Field(..., description="Incident date")
    claim_date: datetime = Field(..., description="Claim submission date")
    processed_date: Optional[datetime] = Field(None, description="Processing date")
    settlement_date: Optional[datetime] = Field(None, description="Settlement date")
    customer_id: str = Field(..., description="Customer identifier")
    customer_name: str = Field(..., description="Customer name")
    agent_id: Optional[str] = Field(None, description="Agent identifier")
    status: str = Field(..., description="Claim status")
    priority: str = Field(default="medium", description="Claim priority")
    description: str = Field(..., description="Claim description")
    incident_location: Optional[str] = Field(None, description="Incident location")
    adjuster_id: Optional[str] = Field(None, description="Adjuster identifier")
    adjuster_name: Optional[str] = Field(None, description="Adjuster name")
    adjuster_notes: Optional[str] = Field(None, description="Adjuster notes")
    settlement_method: Optional[str] = Field(None, description="Settlement method")
    settlement_reference: Optional[str] = Field(None, description="Settlement reference")
    is_fraudulent: bool = Field(default=False, description="Fraudulent flag")
    requires_investigation: bool = Field(default=False, description="Investigation required flag")
    has_attachments: bool = Field(default=False, description="Attachments flag")

class ClaimCreate(ClaimBase):
    """Schema for creating claims"""
    pass

class ClaimUpdate(BaseSchema):
    """Schema for updating claims"""
    policy_number: Optional[str] = None
    claim_type: Optional[str] = None
    claim_amount: Optional[float] = Field(None, gt=0)
    approved_amount: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = None
    incident_date: Optional[datetime] = None
    claim_date: Optional[datetime] = None
    processed_date: Optional[datetime] = None
    settlement_date: Optional[datetime] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    agent_id: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    description: Optional[str] = None
    incident_location: Optional[str] = None
    adjuster_id: Optional[str] = None
    adjuster_name: Optional[str] = None
    adjuster_notes: Optional[str] = None
    settlement_method: Optional[str] = None
    settlement_reference: Optional[str] = None
    is_fraudulent: Optional[bool] = None
    requires_investigation: Optional[bool] = None
    has_attachments: Optional[bool] = None

class ClaimResponse(ClaimBase, TimestampMixin):
    """Schema for claim responses"""
    id: int
    uuid: str
    
    @validator('claim_amount', 'approved_amount')
    def validate_amounts(cls, v):
        if v is not None:
            return round(float(v), 2)
        return v

class ClaimSummary(BaseSchema):
    """Claim summary schema"""
    total_claims: int
    submitted_claims: int
    approved_claims: int
    denied_claims: int
    settled_claims: int
    total_claim_amount: float
    total_approved_amount: float
