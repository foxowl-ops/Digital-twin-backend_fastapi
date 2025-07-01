"""
Common Pydantic schemas and base classes
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Generic, TypeVar, List
from datetime import datetime
from enum import Enum

DataT = TypeVar('DataT')

class TimestampMixin(BaseModel):
    """Common timestamp fields"""
    created_at: datetime
    updated_at: datetime

class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")
    
class PaginatedResponse(BaseModel, Generic[DataT]):
    """Paginated response wrapper"""
    items: List[DataT]
    total: int
    page: int
    size: int
    pages: int

class FileUploadResponse(BaseModel):
    """File upload response"""
    filename: str
    size: int
    records_imported: int
    status: str
    message: str

class AnalyticsResponse(BaseModel):
    """Analytics response"""
    total_count: int
    period: str
    data: dict

# Common enums
class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class SeverityEnum(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
