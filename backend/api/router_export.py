"""
API endpoints for data export functionality.
Provides CSV, JSON, and SQL exports via HTTP.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import io

from db.session import SessionLocal
from services.export import ExportService

router = APIRouter(prefix="/api/export", tags=["export"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/stats")
def get_export_statistics(db: Session = Depends(get_db)):
    """
    Get statistics about data to be exported.
    
    Returns:
        - record_counts: Number of records per table
        - estimated_sizes: Estimated file sizes in KB
        - date_range: Range of tracked data
    """
    export_service = ExportService(db)
    return export_service.get_export_statistics()


@router.get("/csv/{table_name}")
def export_table_csv(table_name: str, db: Session = Depends(get_db)):
    """
    Export a single table to CSV format.
    
    Parameters:
        - table_name: Table to export (activities, events, daily_stats, streaks, memories, journal, alerts)
    
    Returns:
        CSV file for download
    """
    try:
        export_service = ExportService(db)
        csv_data = export_service.export_to_csv(table_name)
        
        return {
            "format": "csv",
            "table": table_name,
            "data": csv_data,
            "records": len(csv_data.split('\n')) - 1,  # Exclude header
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/csv/multiple")
def export_multiple_csv(tables: List[str], db: Session = Depends(get_db)):
    """
    Export multiple tables to CSV format.
    
    Parameters:
        - tables: List of table names to export
    
    Returns:
        Dictionary with table names mapped to CSV data
    """
    try:
        export_service = ExportService(db)
        csv_files = export_service.export_multiple_to_csv(tables)
        
        return {
            "format": "csv",
            "tables": list(csv_files.keys()),
            "data": csv_files,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/json")
def export_json(db: Session = Depends(get_db)):
    """
    Export all data to JSON format.
    
    Returns:
        Complete data as JSON with metadata
    """
    try:
        export_service = ExportService(db)
        json_data = export_service.export_to_json()
        
        return {
            "format": "json",
            "status": "success",
            "data": json_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/sql")
def export_sql(tables: Optional[List[str]] = None, db: Session = Depends(get_db)):
    """
    Export data as SQL INSERT statements (suitable for backups/transfers).
    
    Parameters:
        - tables: Optional list of specific tables to include
    
    Returns:
        SQL script as text
    """
    try:
        export_service = ExportService(db)
        sql_data = export_service.export_to_sql(include=tables)
        
        return {
            "format": "sql",
            "status": "success",
            "data": sql_data,
            "line_count": len(sql_data.split('\n')),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/backup/create")
def create_backup(db: Session = Depends(get_db)):
    """
    Create a full backup with all export formats.
    
    Returns:
        - csv: Path to CSV backup
        - json: Path to compressed JSON backup
        - sql: Path to SQL backup
    """
    try:
        export_service = ExportService(db)
        files = export_service.create_full_backup()
        
        return {
            "status": "success",
            "message": "Full backup created",
            "files": files,
            "timestamp": export_service.export_timestamp.isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup creation failed: {str(e)}")


@router.get("/formats")
def get_supported_formats():
    """Get list of supported export formats and table names."""
    return {
        "formats": ["csv", "json", "sql"],
        "tables": [
            "activities",
            "events", 
            "daily_stats",
            "streaks",
            "memories",
            "journal",
            "alerts",
        ],
        "endpoints": {
            "csv_single": "GET /api/export/csv/{table_name}",
            "csv_multiple": "POST /api/export/csv/multiple",
            "json_full": "GET /api/export/json",
            "sql_script": "GET /api/export/sql",
            "create_backup": "GET /api/export/backup/create",
            "statistics": "GET /api/export/stats",
        },
    }
