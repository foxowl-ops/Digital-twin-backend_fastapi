"""
Agent-related Pydantic schemas
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
from datetime import datetime
from app.schemas.common import BaseSchema, TimestampMixin

class AgentBase(BaseSchema):
    """Base agent schema"""
    agent_id: str = Field(..., description="Unique agent identifier")
    employee_id: Optional[str] = Field(None, description="Employee ID")
    license_number: Optional[str] = Field(None, description="License number")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    full_name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    mobile: Optional[str] = Field(None, description="Mobile number")
    hire_date: datetime = Field(..., description="Hire date")
    department: Optional[str] = Field(None, description="Department")
    position: Optional[str] = Field(None, description="Position")
    manager_id: Optional[str] = Field(None, description="Manager ID")
    status: str = Field(default="active", description="Agent status")
    agent_type: str = Field(..., description="Agent type")
    total_policies: int = Field(default=0, description="Total policies")
    active_policies: int = Field(default=0, description="Active policies")
    total_premium_written: float = Field(default=0.0, description="Total premium written")
    commission_rate: float = Field(default=0.0, description="Commission rate")
    total_commission_earned: float = Field(default=0.0, description="Total commission earned")
    last_commission_date: Optional[datetime] = Field(None, description="Last commission date")
    territory: Optional[str] = Field(None, description="Territory")
    specialization: Optional[str] = Field(None, description="Specialization")
    license_state: Optional[str] = Field(None, description="License state")
    license_expiry: Optional[datetime] = Field(None, description="License expiry date")
    certifications: Optional[str] = Field(None, description="Certifications")
    customer_satisfaction_score: Optional[float] = Field(None, description="Customer satisfaction score")
    performance_rating: Optional[str] = Field(None, description="Performance rating")
    notes: Optional[str] = Field(None, description="Agent notes")
    is_top_performer: bool = Field(default=False, description="Top performer flag")
    can_approve_claims: bool = Field(default=False, description="Can approve claims flag")

class AgentCreate(AgentBase):
    """Schema for creating agents"""
    pass

class AgentUpdate(BaseSchema):
    """Schema for updating agents"""
    employee_id: Optional[str] = None
    license_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    hire_date: Optional[datetime] = None
    department: Optional[str] = None
    position: Optional[str] = None
    manager_id: Optional[str] = None
    status: Optional[str] = None
    agent_type: Optional[str] = None
    total_policies: Optional[int] = None
    active_policies: Optional[int] = None
    total_premium_written: Optional[float] = None
    commission_rate: Optional[float] = None
    total_commission_earned: Optional[float] = None
    last_commission_date: Optional[datetime] = None
    territory: Optional[str] = None
    specialization: Optional[str] = None
    license_state: Optional[str] = None
    license_expiry: Optional[datetime] = None
    certifications: Optional[str] = None
    customer_satisfaction_score: Optional[float] = None
    performance_rating: Optional[str] = None
    notes: Optional[str] = None
    is_top_performer: Optional[bool] = None
    can_approve_claims: Optional[bool] = None

class AgentResponse(AgentBase, TimestampMixin):
    """Schema for agent responses"""
    id: int
    uuid: str
    
    @validator('total_premium_written', 'commission_rate', 'total_commission_earned', 'customer_satisfaction_score')
    def validate_amounts(cls, v):
        if v is not None:
            return round(float(v), 2)
        return v

class AgentSummary(BaseSchema):
    """Agent summary schema"""
    total_agents: int
    active_agents: int
    inactive_agents: int
    top_performers: int
    total_premium_written: float
    total_commission_paid: float
