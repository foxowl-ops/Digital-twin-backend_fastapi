"""
Receipt model for payment confirmations
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from app.models.base import BaseModel

class Receipt(BaseModel):
    """Receipt generation model"""
    __tablename__ = "receipts"
    
    # Receipt identification
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)
    payment_id = Column(String(50), nullable=False, index=True)
    
    # Receipt details
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    receipt_date = Column(DateTime, nullable=False)
    
    # Related entities
    policy_number = Column(String(50), nullable=True, index=True)
    customer_id = Column(String(50), nullable=True, index=True)
    customer_name = Column(String(200), nullable=False)
    customer_email = Column(String(100), nullable=True)
    
    # Receipt content
    description = Column(Text, nullable=True)
    payment_method = Column(String(50), nullable=False)
    
    # Status and processing
    receipt_status = Column(String(20), default="generated")  # generated, sent, viewed
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime, nullable=True)
    
    # File information
    receipt_file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<Receipt(receipt_number='{self.receipt_number}', amount={self.amount})>"
