"""
API Routes Package
"""

from app.routes import (
    payments,
    receipts,
    policies,
    claims,
    customers,
    agents,
    audit_logs,
    file_upload,
    analytics
)

__all__ = [
    "payments",
    "receipts", 
    "policies",
    "claims",
    "customers",
    "agents",
    "audit_logs",
    "file_upload",
    "analytics"
]
