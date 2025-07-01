"""
Customer model for policy holders and clients
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from app.models.base import BaseModel

class Customer(BaseModel):
    """Customer/Policy holder model"""
    __tablename__ = "customers"
    
    # Customer identification
    customer_id = Column(String(50), unique=True, nullable=False, index=True)
    customer_number = Column(String(50), unique=True, nullable=True, index=True)
    
    # Personal information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), nullable=False)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(10), nullable=True)
    
    # Contact information
    email = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    
    # Address information
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(50), nullable=True)
    
    # Customer status
    status = Column(String(20), default="active", nullable=False, index=True)  # active, inactive, suspended
    customer_type = Column(String(20), default="individual")  # individual, corporate
    
    # Agent relationship
    primary_agent_id = Column(String(50), nullable=True, index=True)
    
    # Customer metadata
    registration_date = Column(DateTime, nullable=False)
    last_contact_date = Column(DateTime, nullable=True)
    preferred_contact_method = Column(String(20), default="email")  # email, phone, mail
    
    # Financial information
    credit_score = Column(Integer, nullable=True)
    payment_method = Column(String(50), nullable=True)
    
    # Notes and preferences
    notes = Column(Text, nullable=True)
    marketing_consent = Column(Boolean, default=False)
    
    # Flags
    is_vip = Column(Boolean, default=False)
    has_claims = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Customer(customer_id='{self.customer_id}', name='{self.full_name}', status='{self.status}')>"
