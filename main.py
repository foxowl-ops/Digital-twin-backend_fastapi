"""
FastAPI Insurance Dashboard Backend
Main application entry point
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db
from app.routes import (
    payments, receipts, policies, claims, 
    customers, agents, audit_logs, file_upload, analytics
)
from app.utils.logging import setup_logging
from app.utils.exceptions import setup_exception_handlers

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting Insurance Dashboard API...")
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    # Initialize database
    await init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Insurance Dashboard API...")

# Create FastAPI app
app = FastAPI(
    title="Insurance Dashboard API",
    description="RESTful API for insurance data management with XLSX file processing",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Setup exception handlers
setup_exception_handlers(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(receipts.router, prefix="/api/receipts", tags=["Receipts"])
app.include_router(policies.router, prefix="/api/policies", tags=["Policies"])
app.include_router(claims.router, prefix="/api/claims", tags=["Claims"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(audit_logs.router, prefix="/api/audit-logs", tags=["Audit Logs"])
app.include_router(file_upload.router, prefix="/api/upload", tags=["File Upload"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Insurance Dashboard API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "insurance-dashboard-api"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )
