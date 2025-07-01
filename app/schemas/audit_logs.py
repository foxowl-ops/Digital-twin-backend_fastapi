"""
Audit log-related Pydantic schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from app.schemas.common import BaseSchema, TimestampMixin, SeverityEnum

class AuditLogBase(BaseSchema):
    """Base audit log schema"""
    log_id: str = Field(..., description="Unique log identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    user_email: Optional[str] = Field(None, description="User email")
    user_role: Optional[str] = Field(None, description="User role")
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Resource type")
    resource_id: Optional[str] = Field(None, description="Resource identifier")
    event_timestamp: datetime = Field(..., description="Event timestamp")
    event_type: str = Field(..., description="Event type")
    severity: str = Field(default="info", description="Event severity")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    request_method: Optional[str] = Field(None, description="HTTP method")
    request_url: Optional[str] = Field(None, description="Request URL")
    old_values: Optional[Dict[str, Any]] = Field(None, description="Previous values")
    new_values: Optional[Dict[str, Any]] = Field(None, description="New values")
    changes: Optional[Dict[str, Any]] = Field(None, description="Summary of changes")
    description: Optional[str] = Field(None, description="Event description")
    error_message: Optional[str] = Field(None, description="Error message")
    stack_trace: Optional[str] = Field(None, description="Stack trace")
    status: str = Field(default="success", description="Event status")
    is_sensitive: bool = Field(default=False, description="Sensitive data flag")
    requires_review: bool = Field(default=False, description="Requires review flag")
    correlation_id: Optional[str] = Field(None, description="Correlation ID")
    parent_log_id: Optional[str] = Field(None, description="Parent log ID")

class AuditLogCreate(AuditLogBase):
    """Schema for creating audit logs"""
    pass

class AuditLogUpdate(BaseSchema):
    """Schema for updating audit logs"""
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    event_timestamp: Optional[datetime] = None
    event_type: Optional[str] = None
    severity: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_method: Optional[str] = None
    request_url: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    status: Optional[str] = None
    is_sensitive: Optional[bool] = None
    requires_review: Optional[bool] = None
    correlation_id: Optional[str] = None
    parent_log_id: Optional[str] = None

class AuditLogResponse(AuditLogBase, TimestampMixin):
    """Schema for audit log responses"""
    id: int
    uuid: str

class AuditLogSummary(BaseSchema):
    """Audit log summary schema"""
    total_logs: int
    success_logs: int
    error_logs: int
    warning_logs: int
    sensitive_logs: int
    logs_requiring_review: int
