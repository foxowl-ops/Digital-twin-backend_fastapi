"""
Policy model for insurance policies
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from app.models.base import BaseModel

class Policy(BaseModel):
    """Insurance policy model"""
    __tablename__ = "policies"
    
    # Policy identification
    policy_number = Column(String(50), unique=True, nullable=False, index=True)
    policy_type = Column(String(50), nullable=False, index=True)  # auto, home, life, health, etc.
    
    # Policy details
    premium_amount = Column(Float, nullable=False)
    coverage_amount = Column(Float, nullable=False)
    deductible = Column(Float, default=0.0)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Policy periods
    effective_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    renewal_date = Column(DateTime, nullable=True)
    
    # Policy holder information
    customer_id = Column(String(50), nullable=False, index=True)
    customer_name = Column(String(200), nullable=False)
    
    # Agent information
    agent_id = Column(String(50), nullable=True, index=True)
    agent_name = Column(String(200), nullable=True)
    
    # Policy status
    status = Column(String(20), nullable=False, index=True)  # active, inactive, cancelled, expired
    
    # Payment information
    payment_frequency = Column(String(20), nullable=False)  # monthly, quarterly, annually
    next_payment_due = Column(DateTime, nullable=True)
    
    # Additional details
    description = Column(Text, nullable=True)
    terms_conditions = Column(Text, nullable=True)
    
    # Flags
    auto_renewal = Column(Boolean, default=False)
    is_group_policy = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Policy(policy_number='{self.policy_number}', type='{self.policy_type}', status='{self.status}')>"
