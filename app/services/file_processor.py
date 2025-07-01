"""
File processing service for XLSX uploads
"""

import pandas as pd
import logging
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
import uuid

from app.models.payments import Payment
from app.models.receipts import Receipt
from app.models.policies import Policy
from app.models.claims import Claim
from app.models.customers import Customer
from app.models.agents import Agent
from app.models.audit_logs import AuditLog

logger = logging.getLogger(__name__)

class FileProcessor:
    """Service for processing uploaded XLSX files"""
    
    def __init__(self):
        self.model_mapping = {
            "payments": Payment,
            "receipts": Receipt,
            "policies": Policy,
            "claims": Claim,
            "customers": Customer,
            "agents": Agent,
            "audit_logs": AuditLog
        }
    
    async def process_file(self, file_path: str, data_type: str, db: Session) -> Dict[str, Any]:
        """Process uploaded XLSX file and import data"""
        try:
            logger.info(f"Processing file: {file_path} for data type: {data_type}")
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Clean and validate data
            df = self._clean_dataframe(df)
            
            # Get model class
            model_class = self.model_mapping.get(data_type)
            if not model_class:
                raise ValueError(f"Unsupported data type: {data_type}")
            
            # Process records
            processed_records = []
            errors = []
            
            for index, row in df.iterrows():
                try:
                    record_data = self._prepare_record_data(row, data_type)
                    record = model_class(**record_data)
                    db.add(record)
                    processed_records.append(record)
                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")
                    logger.warning(f"Error processing row {index + 1}: {str(e)}")
            
            # Commit successful records
            if processed_records:
                db.commit()
                logger.info(f"Successfully imported {len(processed_records)} records")
            
            # Log audit entry
            await self._log_import_audit(data_type, len(processed_records), len(errors), db)
            
            return {
                "records_imported": len(processed_records),
                "errors": errors,
                "status": "completed" if not errors else "completed_with_errors"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare DataFrame for processing"""
        # Remove empty rows
        df = df.dropna(how='all')
        
        # Convert column names to lowercase and replace spaces with underscores
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Handle missing values
        df = df.fillna('')
        
        return df
    
    def _prepare_record_data(self, row: pd.Series, data_type: str) -> Dict[str, Any]:
        """Prepare record data based on data type"""
        current_time = datetime.now()
        
        if data_type == "payments":
            return self._prepare_payment_data(row, current_time)
        elif data_type == "receipts":
            return self._prepare_receipt_data(row, current_time)
        elif data_type == "policies":
            return self._prepare_policy_data(row, current_time)
        elif data_type == "claims":
            return self._prepare_claim_data(row, current_time)
        elif data_type == "customers":
            return self._prepare_customer_data(row, current_time)
        elif data_type == "agents":
            return self._prepare_agent_data(row, current_time)
        elif data_type == "audit_logs":
            return self._prepare_audit_log_data(row, current_time)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
    
    def _prepare_payment_data(self, row: pd.Series, current_time: datetime) -> Dict[str, Any]:
        """Prepare payment record data"""
        return {
            "payment_id": str(row.get("payment_id", f"PAY-{uuid.uuid4().hex[:8].upper()}")),
            "transaction_reference": str(row.get("transaction_reference", f"TXN-{uuid.uuid4().hex[:12].upper()}")),
            "amount": float(row.get("amount", 0)),
            "currency": str(row.get("currency", "USD")),
            "payment_method": str(row.get("payment_method", "unknown")),
            "payment_status": str(row.get("payment_status", "pending")),
            "policy_number": str(row.get("policy_number", "")) if row.get("policy_number") else None,
            "customer_id": str(row.get("customer_id", "")) if row.get("customer_id") else None,
            "agent_id": str(row.get("agent_id", "")) if row.get("agent_id") else None,
            "payment_date": pd.to_datetime(row.get("payment_date", current_time)),
            "due_date": pd.to_datetime(row.get("due_date")) if row.get("due_date") else None,
            "description": str(row.get("description", "")) if row.get("description") else None,
            "processing_fee": float(row.get("processing_fee", 0)),
            "is_recurring": bool(row.get("is_recurring", False)),
            "is_late_payment": bool(row.get("is_late_payment", False))
        }
    
    def _prepare_receipt_data(self, row: pd.Series, current_time: datetime) -> Dict[str, Any]:
        """Prepare receipt record data"""
        return {
            "receipt_number": str(row.get("receipt_number", f"RCP-{uuid.uuid4().hex[:8].upper()}")),
            "payment_id": str(row.get("payment_id", f"PAY-{uuid.uuid4().hex[:8].upper()}")),
            "amount": float(row.get("amount", 0)),
            "currency": str(row.get("currency", "USD")),
            "receipt_date": pd.to_datetime(row.get("receipt_date", current_time)),
            "policy_number": str(row.get("policy_number", "")) if row.get("policy_number") else None,
            "customer_id": str(row.get("customer_id", "")) if row.get("customer_id") else None,
            "customer_name": str(row.get("customer_name", "Unknown Customer")),
            "customer_email": str(row.get("customer_email", "")) if row.get("customer_email") else None,
            "description": str(row.get("description", "")) if row.get("description") else None,
            "payment_method": str(row.get("payment_method", "unknown")),
            "receipt_status": str(row.get("receipt_status", "generated")),
            "email_sent": bool(row.get("email_sent", False))
        }
    
    def _prepare_policy_data(self, row: pd.Series, current_time: datetime) -> Dict[str, Any]:
        """Prepare policy record data"""
        return {
            "policy_number": str(row.get("policy_number", f"POL-{uuid.uuid4().hex[:8].upper()}")),
            "policy_type": str(row.get("policy_type", "unknown")),
            "premium_amount": float(row.get("premium_amount", 0)),
            "coverage_amount": float(row.get("coverage_amount", 0)),
            "deductible": float(row.get("deductible", 0)),
            "currency": str(row.get("currency", "USD")),
            "effective_date": pd.to_datetime(row.get("effective_date", current_time)),
            "expiration_date": pd.to_datetime(row.get("expiration_date", current_time)),
            "renewal_date": pd.to_datetime(row.get("renewal_date")) if row.get("renewal_date") else None,
            "customer_id": str(row.get("customer_id", f"CUST-{uuid.uuid4().hex[:8].upper()}")),
            "customer_name": str(row.get("customer_name", "Unknown Customer")),
            "agent_id": str(row.get("agent_id", "")) if row.get("agent_id") else None,
            "agent_name": str(row.get("agent_name", "")) if row.get("agent_name") else None,
            "status": str(row.get("status", "active")),
            "payment_frequency": str(row.get("payment_frequency", "monthly")),
            "next_payment_due": pd.to_datetime(row.get("next_payment_due")) if row.get("next_payment_due") else None,
            "description": str(row.get("description", "")) if row.get("description") else None,
            "auto_renewal": bool(row.get("auto_renewal", False)),
            "is_group_policy": bool(row.get("is_group_policy", False))
        }
    
    def _prepare_claim_data(self, row: pd.Series, current_time: datetime) -> Dict[str, Any]:
        """Prepare claim record data"""
        return {
            "claim_number": str(row.get("claim_number", f"CLM-{uuid.uuid4().hex[:8].upper()}")),
            "policy_number": str(row.get("policy_number", f"POL-{uuid.uuid4().hex[:8].upper()}")),
            "claim_type": str(row.get("claim_type", "unknown")),
            "claim_amount": float(row.get("claim_amount", 0)),
            "approved_amount": float(row.get("approved_amount")) if row.get("approved_amount") else None,
            "currency": str(row.get("currency", "USD")),
            "incident_date": pd.to_datetime(row.get("incident_date", current_time)),
            "claim_date": pd.to_datetime(row.get("claim_date", current_time)),
            "processed_date": pd.to_datetime(row.get("processed_date")) if row.get("processed_date") else None,
            "settlement_date": pd.to_datetime(row.get("settlement_date")) if row.get("settlement_date") else None,
            "customer_id": str(row.get("customer_id", f"CUST-{uuid.uuid4().hex[:8].upper()}")),
            "customer_name": str(row.get("customer_name", "Unknown Customer")),
            "agent_id": str(row.get("agent_id", "")) if row.get("agent_id") else None,
            "status": str(row.get("status", "submitted")),
            "priority": str(row.get("priority", "medium")),
            "description": str(row.get("description", "Claim description")),
            "incident_location": str(row.get("incident_location", "")) if row.get("incident_location") else None,
            "adjuster_id": str(row.get("adjuster_id", "")) if row.get("adjuster_id") else None,
            "adjuster_name": str(row.get("adjuster_name", "")) if row.get("adjuster_name") else None,
            "is_fraudulent": bool(row.get("is_fraudulent", False)),
            "requires_investigation": bool(row.get("requires_investigation", False)),
            "has_attachments": bool(row.get("has_attachments", False))
        }
    
    def _prepare_customer_data(self, row: pd.Series, current_time: datetime) -> Dict[str, Any]:
        """Prepare customer record data"""
        first_name = str(row.get("first_name", "Unknown"))
        last_name = str(row.get("last_name", "Customer"))
        full_name = str(row.get("full_name", f"{first_name} {last_name}"))
        
        return {
            "customer_id": str(row.get("customer_id", f"CUST-{uuid.uuid4().hex[:8].upper()}")),
            "customer_number": str(row.get("customer_number", "")) if row.get("customer_number") else None,
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "date_of_birth": pd.to_datetime(row.get("date_of_birth")) if row.get("date_of_birth") else None,
            "gender": str(row.get("gender", "")) if row.get("gender") else None,
            "email": str(row.get("email", f"customer{uuid.uuid4().hex[:8]}@example.com")),
            "phone": str(row.get("phone", "")) if row.get("phone") else None,
            "mobile": str(row.get("mobile", "")) if row.get("mobile") else None,
            "address_line1": str(row.get("address_line1", "")) if row.get("address_line1") else None,
            "address_line2": str(row.get("address_line2", "")) if row.get("address_line2") else None,
            "city": str(row.get("city", "")) if row.get("city") else None,
            "state": str(row.get("state", "")) if row.get("state") else None,
            "postal_code": str(row.get("postal_code", "")) if row.get("postal_code") else None,
            "country": str(row.get("country", "")) if row.get("country") else None,
            "status": str(row.get("status", "active")),
            "customer_type": str(row.get("customer_type", "individual")),
            "primary_agent_id": str(row.get("primary_agent_id", "")) if row.get("primary_agent_id") else None,
            "registration_date": pd.to_datetime(row.get("registration_date", current_time)),
            "last_contact_date": pd.to_datetime(row.get("last_contact_date")) if row.get("last_contact_date") else None,
            "preferred_contact_method": str(row.get("preferred_contact_method", "email")),
            "credit_score": int(row.get("credit_score")) if row.get("credit_score") else None,
            "payment_method": str(row.get("payment_method", "")) if row.get("payment_method") else None,
            "notes": str(row.get("notes", "")) if row.get("notes") else None,
            "marketing_consent": bool(row.get("marketing_consent", False)),
            "is_vip": bool(row.get("is_vip", False)),
            "has_claims": bool(row.get("has_claims", False))
        }
    
    def _prepare_agent_data(self, row: pd.Series, current_time: datetime) -> Dict[str, Any]:
        """Prepare agent record data"""
        first_name = str(row.get("first_name", "Unknown"))
        last_name = str(row.get("last_name", "Agent"))
        full_name = str(row.get("full_name", f"{first_name} {last_name}"))
        
        return {
            "agent_id": str(row.get("agent_id", f"AGT-{uuid.uuid4().hex[:8].upper()}")),
            "employee_id": str(row.get("employee_id", "")) if row.get("employee_id") else None,
            "license_number": str(row.get("license_number", "")) if row.get("license_number") else None,
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "email": str(row.get("email", f"agent{uuid.uuid4().hex[:8]}@example.com")),
            "phone": str(row.get("phone", "")) if row.get("phone") else None,
            "mobile": str(row.get("mobile", "")) if row.get("mobile") else None,
            "hire_date": pd.to_datetime(row.get("hire_date", current_time)),
            "department": str(row.get("department", "")) if row.get("department") else None,
            "position": str(row.get("position", "")) if row.get("position") else None,
            "manager_id": str(row.get("manager_id", "")) if row.get("manager_id") else None,
            "status": str(row.get("status", "active")),
            "agent_type": str(row.get("agent_type", "employee")),
            "total_policies": int(row.get("total_policies", 0)),
            "active_policies": int(row.get("active_policies", 0)),
            "total_premium_written": float(row.get("total_premium_written", 0)),
            "commission_rate": float(row.get("commission_rate", 0)),
            "total_commission_earned": float(row.get("total_commission_earned", 0)),
            "last_commission_date": pd.to_datetime(row.get("last_commission_date")) if row.get("last_commission_date") else None,
            "territory": str(row.get("territory", "")) if row.get("territory") else None,
            "specialization": str(row.get("specialization", "")) if row.get("specialization") else None,
            "license_state": str(row.get("license_state", "")) if row.get("license_state") else None,
            "license_expiry": pd.to_datetime(row.get("license_expiry")) if row.get("license_expiry") else None,
            "customer_satisfaction_score": float(row.get("customer_satisfaction_score")) if row.get("customer_satisfaction_score") else None,
            "performance_rating": str(row.get("performance_rating", "")) if row.get("performance_rating") else None,
            "notes": str(row.get("notes", "")) if row.get("notes") else None,
            "is_top_performer": bool(row.get("is_top_performer", False)),
            "can_approve_claims": bool(row.get("can_approve_claims", False))
        }
    
    def _prepare_audit_log_data(self, row: pd.Series, current_time: datetime) -> Dict[str, Any]:
        """Prepare audit log record data"""
        return {
            "log_id": str(row.get("log_id", f"LOG-{uuid.uuid4().hex[:8].upper()}")),
            "session_id": str(row.get("session_id", "")) if row.get("session_id") else None,
            "user_id": str(row.get("user_id", "")) if row.get("user_id") else None,
            "user_email": str(row.get("user_email", "")) if row.get("user_email") else None,
            "user_role": str(row.get("user_role", "")) if row.get("user_role") else None,
            "action": str(row.get("action", "UNKNOWN")),
            "resource_type": str(row.get("resource_type", "unknown")),
            "resource_id": str(row.get("resource_id", "")) if row.get("resource_id") else None,
            "event_timestamp": pd.to_datetime(row.get("event_timestamp", current_time)),
            "event_type": str(row.get("event_type", "user_action")),
            "severity": str(row.get("severity", "info")),
            "ip_address": str(row.get("ip_address", "")) if row.get("ip_address") else None,
            "user_agent": str(row.get("user_agent", "")) if row.get("user_agent") else None,
            "request_method": str(row.get("request_method", "")) if row.get("request_method") else None,
            "request_url": str(row.get("request_url", "")) if row.get("request_url") else None,
            "description": str(row.get("description", "")) if row.get("description") else None,
            "error_message": str(row.get("error_message", "")) if row.get("error_message") else None,
            "status": str(row.get("status", "success")),
            "is_sensitive": bool(row.get("is_sensitive", False)),
            "requires_review": bool(row.get("requires_review", False)),
            "correlation_id": str(row.get("correlation_id", "")) if row.get("correlation_id") else None,
            "parent_log_id": str(row.get("parent_log_id", "")) if row.get("parent_log_id") else None
        }
    
    async def _log_import_audit(self, data_type: str, records_imported: int, error_count: int, db: Session):
        """Log file import audit entry"""
        try:
            audit_log = AuditLog(
                log_id=f"IMPORT-{uuid.uuid4().hex[:8].upper()}",
                action="FILE_IMPORT",
                resource_type=data_type,
                event_timestamp=datetime.now(),
                event_type="system_event",
                severity="info" if error_count == 0 else "warning",
                description=f"File import completed for {data_type}: {records_imported} records imported, {error_count} errors",
                status="success" if error_count == 0 else "warning"
            )
            db.add(audit_log)
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to log import audit: {str(e)}")
