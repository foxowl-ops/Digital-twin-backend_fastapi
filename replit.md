# replit.md

## Overview

This is an Insurance Dashboard API built with FastAPI that provides a comprehensive data management system for insurance operations. The application handles payments, receipts, policies, claims, customers, agents, and audit logs with XLSX file processing capabilities and analytics features.

## System Architecture

The application follows a layered architecture pattern:

- **API Layer**: FastAPI-based REST endpoints organized by domain
- **Business Logic Layer**: Services for file processing and analytics
- **Data Access Layer**: SQLAlchemy ORM with model definitions
- **Database Layer**: Configurable database support (SQLite default, extensible to PostgreSQL)

## Key Components

### Backend Framework
- **FastAPI**: Modern Python web framework for building APIs
- **SQLAlchemy**: ORM for database operations with declarative models
- **Alembic**: Database migration management
- **Pydantic**: Data validation and serialization using schemas

### Database Models
Core entities include:
- **Customers**: Policy holders and client information
- **Agents**: Insurance agents and brokers
- **Policies**: Insurance policy records
- **Payments**: Transaction records
- **Receipts**: Payment confirmations
- **Claims**: Insurance claim processing
- **AuditLogs**: System activity tracking

### API Structure
RESTful endpoints organized by domain:
- `/payments` - Payment transaction management
- `/receipts` - Receipt generation and tracking
- `/policies` - Policy lifecycle management
- `/claims` - Claims processing workflow
- `/customers` - Customer relationship management
- `/agents` - Agent management system
- `/audit-logs` - System audit trail
- `/file-upload` - XLSX file processing
- `/analytics` - Dashboard metrics and insights

### File Processing
- XLSX/XLS file upload support
- Background processing for large datasets
- Data validation and cleansing
- Bulk import capabilities for all entity types

## Data Flow

1. **File Upload**: XLSX files uploaded via `/file-upload/{data_type}` endpoint
2. **Processing**: Background tasks handle file parsing and data validation
3. **Storage**: Validated data inserted into appropriate database tables
4. **API Access**: RESTful endpoints provide CRUD operations
5. **Analytics**: Dashboard metrics generated from aggregated data
6. **Audit Trail**: All operations logged for compliance and monitoring

## External Dependencies

### Core Dependencies
- **FastAPI**: Web framework and API routing
- **SQLAlchemy**: Database ORM and query builder
- **Pandas**: Data processing for XLSX files
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server for FastAPI applications

### File Processing
- **openpyxl/xlrd**: Excel file reading capabilities
- **python-multipart**: File upload handling

### Development Tools
- **Alembic**: Database migrations
- **Python-dotenv**: Environment variable management

## Deployment Strategy

### Configuration
- Environment-based configuration using Pydantic Settings
- Database URL configurable via environment variables
- CORS and security settings for production deployment
- File upload limits and directory configuration

### Database Setup
- Automatic table creation via SQLAlchemy
- Migration support through Alembic
- SQLite for development, PostgreSQL-ready for production
- Connection pooling and optimization settings

### Security Features
- CORS middleware for cross-origin requests
- Trusted host middleware for production security
- File upload validation and size limits
- Comprehensive error handling and logging

### Monitoring
- Structured logging with configurable levels
- Audit trail for all system operations
- Error tracking and exception handling
- Performance metrics through analytics service

## Changelog

- July 01, 2025. Initial setup
- July 01, 2025. Successfully deployed FastAPI backend with PostgreSQL database, all 7 insurance data types implemented with working API endpoints, analytics dashboard functional, database tables created and operational

## User Preferences

Preferred communication style: Simple, everyday language.