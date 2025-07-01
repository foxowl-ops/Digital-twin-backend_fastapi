"""
Exception handling and error management utilities
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers for the FastAPI app"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions"""
        logger.warning(f"HTTP {exc.status_code} error: {exc.detail} - Path: {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Error",
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors"""
        logger.warning(f"Validation error: {exc.errors()} - Path: {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "message": "Request validation failed",
                "details": exc.errors(),
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Handle database integrity errors"""
        logger.error(f"Database integrity error: {str(exc)} - Path: {request.url.path}")
        
        # Extract meaningful error message
        error_msg = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        
        if "UNIQUE constraint failed" in error_msg:
            message = "A record with this identifier already exists"
        elif "FOREIGN KEY constraint failed" in error_msg:
            message = "Referenced record does not exist"
        elif "NOT NULL constraint failed" in error_msg:
            message = "Required field is missing"
        else:
            message = "Database constraint violation"
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Database Integrity Error",
                "message": message,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        """Handle SQLAlchemy database errors"""
        logger.error(f"Database error: {str(exc)} - Path: {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Database Error",
                "message": "A database error occurred while processing your request",
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle value errors"""
        logger.warning(f"Value error: {str(exc)} - Path: {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Invalid Value",
                "message": str(exc),
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(FileNotFoundError)
    async def file_not_found_handler(request: Request, exc: FileNotFoundError):
        """Handle file not found errors"""
        logger.warning(f"File not found: {str(exc)} - Path: {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "File Not Found",
                "message": "The requested file could not be found",
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError):
        """Handle permission errors"""
        logger.error(f"Permission error: {str(exc)} - Path: {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "Permission Denied",
                "message": "You don't have permission to perform this action",
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other unhandled exceptions"""
        logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)} - Path: {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred while processing your request",
                "path": str(request.url.path)
            }
        )

class InsuranceAPIException(Exception):
    """Base exception for Insurance API"""
    def __init__(self, message: str, status_code: int = 500, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class DataProcessingError(InsuranceAPIException):
    """Exception raised during data processing"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status_code=422, details=details)

class FileProcessingError(InsuranceAPIException):
    """Exception raised during file processing"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status_code=422, details=details)

class DatabaseConnectionError(InsuranceAPIException):
    """Exception raised when database connection fails"""
    def __init__(self, message: str = "Database connection failed"):
        super().__init__(message, status_code=503)

class RecordNotFoundError(InsuranceAPIException):
    """Exception raised when a requested record is not found"""
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, status_code=404)

class DuplicateRecordError(InsuranceAPIException):
    """Exception raised when attempting to create a duplicate record"""
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with identifier '{identifier}' already exists"
        super().__init__(message, status_code=409)
