"""
Audit log model for system activity tracking
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from app.models.base import BaseModel

class AuditLog(BaseModel):
    """System audit log model"""
    __tablename__ = "audit_logs"
    
    # Log identification
    log_id = Column(String(50), unique=True, nullable=False, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    
    # User and action information
    user_id = Column(String(50), nullable=True, index=True)
    user_email = Column(String(100), nullable=True)
    user_role = Column(String(50), nullable=True)
    
    # Action details
    action = Column(String(100), nullable=False, index=True)  # CREATE, READ, UPDATE, DELETE, LOGIN, etc.
    resource_type = Column(String(50), nullable=False, index=True)  # payment, policy, claim, etc.
    resource_id = Column(String(50), nullable=True, index=True)
    
    # Event details
    event_timestamp = Column(DateTime, nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # user_action, system_event, security_event
    severity = Column(String(10), default="info")  # debug, info, warning, error, critical
    
    # Request information
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE
    request_url = Column(String(500), nullable=True)
    
    # Change tracking
    old_values = Column(JSON, nullable=True)  # Previous state
    new_values = Column(JSON, nullable=True)  # New state
    changes = Column(JSON, nullable=True)  # Summary of changes
    
    # Additional context
    description = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Status and flags
    status = Column(String(20), default="success")  # success, failure, warning
    is_sensitive = Column(Boolean, default=False)
    requires_review = Column(Boolean, default=False)
    
    # Correlation
    correlation_id = Column(String(100), nullable=True, index=True)
    parent_log_id = Column(String(50), nullable=True, index=True)
    
    def __repr__(self):
        return f"<AuditLog(log_id='{self.log_id}', action='{self.action}', resource='{self.resource_type}')>"
