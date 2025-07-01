"""
Logging configuration and setup utilities
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.config import settings

def setup_logging(log_level: Optional[str] = None, log_file: Optional[str] = None):
    """Setup application logging configuration"""
    
    # Use provided values or fall back to settings
    level = log_level or settings.LOG_LEVEL
    file_path = log_file or settings.LOG_FILE
    
    # Create logs directory if it doesn't exist
    log_dir = Path(file_path).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)8s | %(name)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=file_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        # If file logging fails, log to console only
        console_handler.setFormatter(detailed_formatter)
        root_logger.warning(f"Failed to setup file logging: {e}")
    
    # Configure specific loggers
    
    # Reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    
    # Application loggers
    app_logger = logging.getLogger("app")
    app_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # FastAPI logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)
    
    # Log startup message
    root_logger.info(f"Logging configured - Level: {level.upper()}, File: {file_path}")

class RequestLogger:
    """Middleware for logging HTTP requests"""
    
    def __init__(self):
        self.logger = logging.getLogger("app.requests")
    
    def log_request(self, request, response_time: float = None, status_code: int = None):
        """Log HTTP request details"""
        try:
            log_data = {
                "method": request.method,
                "url": str(request.url),
                "client_ip": getattr(request.client, 'host', 'unknown'),
                "user_agent": request.headers.get("user-agent", "unknown"),
                "response_time": response_time,
                "status_code": status_code
            }
            
            if response_time:
                message = f"{request.method} {request.url.path} - {status_code} - {response_time:.3f}s"
            else:
                message = f"{request.method} {request.url.path}"
            
            if status_code and status_code >= 400:
                self.logger.warning(message, extra=log_data)
            else:
                self.logger.info(message, extra=log_data)
                
        except Exception as e:
            self.logger.error(f"Failed to log request: {e}")

class AuditLogger:
    """Logger for audit events"""
    
    def __init__(self):
        self.logger = logging.getLogger("app.audit")
    
    def log_event(self, action: str, resource_type: str, resource_id: str = None, 
                  user_id: str = None, details: dict = None):
        """Log audit event"""
        try:
            log_data = {
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "details": details or {}
            }
            
            message = f"AUDIT: {action} {resource_type}"
            if resource_id:
                message += f" [{resource_id}]"
            if user_id:
                message += f" by user {user_id}"
            
            self.logger.info(message, extra=log_data)
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
    
    def log_data_import(self, data_type: str, records_count: int, file_name: str = None):
        """Log data import event"""
        self.log_event(
            action="DATA_IMPORT",
            resource_type=data_type,
            details={
                "records_imported": records_count,
                "file_name": file_name
            }
        )
    
    def log_file_upload(self, file_name: str, file_size: int, data_type: str):
        """Log file upload event"""
        self.log_event(
            action="FILE_UPLOAD",
            resource_type="file",
            details={
                "file_name": file_name,
                "file_size": file_size,
                "data_type": data_type
            }
        )

class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger("app.performance")
    
    def log_query_performance(self, query_type: str, execution_time: float, 
                            record_count: int = None):
        """Log database query performance"""
        try:
            log_data = {
                "query_type": query_type,
                "execution_time": execution_time,
                "record_count": record_count,
                "timestamp": datetime.now().isoformat()
            }
            
            message = f"QUERY: {query_type} - {execution_time:.3f}s"
            if record_count is not None:
                message += f" ({record_count} records)"
            
            # Log slow queries as warnings
            if execution_time > 1.0:
                self.logger.warning(f"SLOW {message}", extra=log_data)
            else:
                self.logger.info(message, extra=log_data)
                
        except Exception as e:
            self.logger.error(f"Failed to log query performance: {e}")
    
    def log_file_processing_performance(self, file_name: str, processing_time: float, 
                                      records_processed: int):
        """Log file processing performance"""
        try:
            log_data = {
                "file_name": file_name,
                "processing_time": processing_time,
                "records_processed": records_processed,
                "records_per_second": records_processed / processing_time if processing_time > 0 else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            message = f"FILE_PROCESSING: {file_name} - {processing_time:.3f}s ({records_processed} records)"
            
            self.logger.info(message, extra=log_data)
            
        except Exception as e:
            self.logger.error(f"Failed to log file processing performance: {e}")

# Global logger instances
request_logger = RequestLogger()
audit_logger = AuditLogger()
performance_logger = PerformanceLogger()
