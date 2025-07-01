"""
Agent model for insurance agents and brokers
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from app.models.base import BaseModel

class Agent(BaseModel):
    """Insurance agent model"""
    __tablename__ = "agents"
    
    # Agent identification
    agent_id = Column(String(50), unique=True, nullable=False, index=True)
    employee_id = Column(String(50), unique=True, nullable=True, index=True)
    license_number = Column(String(50), unique=True, nullable=True, index=True)
    
    # Personal information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), nullable=False)
    
    # Contact information
    email = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    
    # Employment information
    hire_date = Column(DateTime, nullable=False)
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    manager_id = Column(String(50), nullable=True, index=True)
    
    # Agent status
    status = Column(String(20), default="active", nullable=False, index=True)  # active, inactive, terminated
    agent_type = Column(String(20), nullable=False)  # employee, broker, independent
    
    # Performance metrics
    total_policies = Column(Integer, default=0)
    active_policies = Column(Integer, default=0)
    total_premium_written = Column(Float, default=0.0)
    
    # Commission information
    commission_rate = Column(Float, default=0.0)  # as percentage
    total_commission_earned = Column(Float, default=0.0)
    last_commission_date = Column(DateTime, nullable=True)
    
    # Territory and specialization
    territory = Column(String(100), nullable=True)
    specialization = Column(String(100), nullable=True)  # auto, home, life, commercial, etc.
    
    # License information
    license_state = Column(String(2), nullable=True)
    license_expiry = Column(DateTime, nullable=True)
    certifications = Column(Text, nullable=True)  # JSON string of certifications
    
    # Performance ratings
    customer_satisfaction_score = Column(Float, nullable=True)
    performance_rating = Column(String(10), nullable=True)  # excellent, good, average, poor
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Flags
    is_top_performer = Column(Boolean, default=False)
    can_approve_claims = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Agent(agent_id='{self.agent_id}', name='{self.full_name}', status='{self.status}')>"
