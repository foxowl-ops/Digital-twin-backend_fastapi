"""
File upload and processing routes
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import os
import logging
from datetime import datetime

from app.database import get_db
from app.config import settings
from app.services.file_processor import FileProcessor
from app.schemas.common import FileUploadResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize file processor
file_processor = FileProcessor()

@router.post("/{data_type}", response_model=FileUploadResponse)
async def upload_file(
    data_type: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process XLSX file for specific data type"""
    
    # Validate data type
    allowed_types = ["payments", "receipts", "policies", "claims", "customers", "agents", "audit_logs"]
    if data_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Validate file type
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only XLSX and XLS files are allowed"
        )
    
    # Validate file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )
    
    try:
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(settings.UPLOAD_DIRECTORY, data_type)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        logger.info(f"File saved: {file_path}")
        
        # Process file in background
        background_tasks.add_task(
            file_processor.process_file,
            file_path=file_path,
            data_type=data_type,
            db=db
        )
        
        return FileUploadResponse(
            filename=filename,
            size=file_size,
            records_imported=0,  # Will be updated after processing
            status="processing",
            message=f"File uploaded successfully and is being processed for {data_type} data"
        )
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file"
        )

@router.get("/status/{data_type}")
async def get_upload_status(data_type: str):
    """Get upload status for a data type"""
    try:
        upload_dir = os.path.join(settings.UPLOAD_DIRECTORY, data_type)
        
        if not os.path.exists(upload_dir):
            return {
                "data_type": data_type,
                "status": "no_uploads",
                "files": []
            }
        
        files = []
        for filename in os.listdir(upload_dir):
            if filename.endswith(('.xlsx', '.xls')):
                file_path = os.path.join(upload_dir, filename)
                file_stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": file_stat.st_size,
                    "uploaded_at": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "status": "completed"  # Assume completed for now
                })
        
        return {
            "data_type": data_type,
            "status": "completed" if files else "no_uploads",
            "files": files
        }
        
    except Exception as e:
        logger.error(f"Error getting upload status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get upload status"
        )

@router.delete("/{data_type}/{filename}")
async def delete_uploaded_file(data_type: str, filename: str):
    """Delete an uploaded file"""
    try:
        file_path = os.path.join(settings.UPLOAD_DIRECTORY, data_type, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        os.remove(file_path)
        logger.info(f"Deleted file: {file_path}")
        
        return {"message": f"File {filename} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )

@router.get("/")
async def list_all_uploads():
    """List all uploaded files across all data types"""
    try:
        all_uploads = {}
        allowed_types = ["payments", "receipts", "policies", "claims", "customers", "agents", "audit_logs"]
        
        for data_type in allowed_types:
            upload_dir = os.path.join(settings.UPLOAD_DIRECTORY, data_type)
            files = []
            
            if os.path.exists(upload_dir):
                for filename in os.listdir(upload_dir):
                    if filename.endswith(('.xlsx', '.xls')):
                        file_path = os.path.join(upload_dir, filename)
                        file_stat = os.stat(file_path)
                        files.append({
                            "filename": filename,
                            "size": file_stat.st_size,
                            "uploaded_at": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                        })
            
            all_uploads[data_type] = {
                "count": len(files),
                "files": files
            }
        
        return all_uploads
        
    except Exception as e:
        logger.error(f"Error listing uploads: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  
            detail="Failed to list uploads"
        )
