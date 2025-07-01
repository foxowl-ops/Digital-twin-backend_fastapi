"""
Customer-related Pydantic schemas
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
from datetime import datetime
from app.schemas.common import BaseSchema, TimestampMixin

class CustomerBase(BaseSchema):
    """Base customer schema"""
    customer_id: str = Field(..., description="Unique customer identifier")
    customer_number: Optional[str] = Field(None, description="Customer number")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    full_name: str = Field(..., description="Full name")
    date_of_birth: Optional[datetime] = Field(None, description="Date of birth")
    gender: Optional[str] = Field(None, description="Gender")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    mobile: Optional[str] = Field(None, description="Mobile number")
    address_line1: Optional[str] = Field(None, description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Country")
    status: str = Field(default="active", description="Customer status")
    customer_type: str = Field(default="individual", description="Customer type")
    primary_agent_id: Optional[str] = Field(None, description="Primary agent ID")
    registration_date: datetime = Field(..., description="Registration date")
    last_contact_date: Optional[datetime] = Field(None, description="Last contact date")
    preferred_contact_method: str = Field(default="email", description="Preferred contact method")
    credit_score: Optional[int] = Field(None, description="Credit score")
    payment_method: Optional[str] = Field(None, description="Preferred payment method")
    notes: Optional[str] = Field(None, description="Customer notes")
    marketing_consent: bool = Field(default=False, description="Marketing consent")
    is_vip: bool = Field(default=False, description="VIP status")
    has_claims: bool = Field(default=False, description="Has claims flag")

class CustomerCreate(CustomerBase):
    """Schema for creating customers"""
    pass

class CustomerUpdate(BaseSchema):
    """Schema for updating customers"""
    customer_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    status: Optional[str] = None
    customer_type: Optional[str] = None
    primary_agent_id: Optional[str] = None
    last_contact_date: Optional[datetime] = None
    preferred_contact_method: Optional[str] = None
    credit_score: Optional[int] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    marketing_consent: Optional[bool] = None
    is_vip: Optional[bool] = None
    has_claims: Optional[bool] = None

class CustomerResponse(CustomerBase, TimestampMixin):
    """Schema for customer responses"""
    id: int
    uuid: str

class CustomerSummary(BaseSchema):
    """Customer summary schema"""
    total_customers: int
    active_customers: int
    inactive_customers: int
    vip_customers: int
    customers_with_claims: int
