"""
Claim model for insurance claims processing
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from app.models.base import BaseModel

class Claim(BaseModel):
    """Insurance claim model"""
    __tablename__ = "claims"
    
    # Claim identification
    claim_number = Column(String(50), unique=True, nullable=False, index=True)
    policy_number = Column(String(50), nullable=False, index=True)
    
    # Claim details
    claim_type = Column(String(50), nullable=False, index=True)  # accident, theft, damage, medical, etc.
    claim_amount = Column(Float, nullable=False)
    approved_amount = Column(Float, nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Dates
    incident_date = Column(DateTime, nullable=False)
    claim_date = Column(DateTime, nullable=False)
    processed_date = Column(DateTime, nullable=True)
    settlement_date = Column(DateTime, nullable=True)
    
    # Related entities
    customer_id = Column(String(50), nullable=False, index=True)
    customer_name = Column(String(200), nullable=False)
    agent_id = Column(String(50), nullable=True, index=True)
    
    # Claim status and processing
    status = Column(String(20), nullable=False, index=True)  # submitted, under_review, approved, denied, settled
    priority = Column(String(10), default="medium")  # low, medium, high, urgent
    
    # Claim details
    description = Column(Text, nullable=False)
    incident_location = Column(String(500), nullable=True)
    
    # Adjuster information
    adjuster_id = Column(String(50), nullable=True)
    adjuster_name = Column(String(200), nullable=True)
    adjuster_notes = Column(Text, nullable=True)
    
    # Settlement information
    settlement_method = Column(String(50), nullable=True)  # check, bank_transfer, etc.
    settlement_reference = Column(String(100), nullable=True)
    
    # Flags
    is_fraudulent = Column(Boolean, default=False)
    requires_investigation = Column(Boolean, default=False)
    has_attachments = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Claim(claim_number='{self.claim_number}', amount={self.claim_amount}, status='{self.status}')>"
