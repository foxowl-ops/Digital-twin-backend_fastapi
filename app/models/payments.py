"""
Payment model for transaction records
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.models.base import BaseModel

class Payment(BaseModel):
    """Payment transaction model"""
    __tablename__ = "payments"
    
    # Payment identification
    payment_id = Column(String(50), unique=True, nullable=False, index=True)
    transaction_reference = Column(String(100), nullable=False, index=True)
    
    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    payment_method = Column(String(50), nullable=False)  # credit_card, bank_transfer, etc.
    payment_status = Column(String(20), nullable=False)  # pending, completed, failed, refunded
    
    # Related entities
    policy_number = Column(String(50), nullable=True, index=True)
    customer_id = Column(String(50), nullable=True, index=True)
    agent_id = Column(String(50), nullable=True, index=True)
    
    # Payment metadata
    payment_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    
    # Processing details
    gateway_transaction_id = Column(String(100), nullable=True)
    gateway_response = Column(Text, nullable=True)
    processing_fee = Column(Float, default=0.0)
    
    # Flags
    is_recurring = Column(Boolean, default=False)
    is_late_payment = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Payment(payment_id='{self.payment_id}', amount={self.amount}, status='{self.payment_status}')>"
