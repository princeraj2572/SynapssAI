"""
Data export service for CSV, JSON, and SQL formats.
Supports full data dumps, filtered exports, and versioning.

Usage:
    export_service = ExportService(db)
    
    # Export activities to CSV
    csv_data = export_service.export_to_csv('activities')
    
    # Export all data to JSON
    json_data = export_service.export_to_json(include=['activities', 'events', 'stats'])
    
    # Create backup
    backup_file = export_service.create_backup('full_backup.sql')
"""
import csv
import json
import logging
from io import StringIO, BytesIO
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import gzip

from sqlalchemy.orm import Session
from sqlalchemy import text

from models.activity import Activity
from models.event import Event
from models.daily_stat import DailyStat
from models.streak import Streak
from models.memory import Memory
from models.journal import JournalEntry
from models.alert import Alert

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting data in various formats."""
    
    def __init__(self, db: Session):
        self.db = db
        self.export_timestamp = datetime.now()
    
    # ========== CSV EXPORT ==========
    
    def export_to_csv(self, table_name: str, filters: Optional[Dict] = None) -> str:
        """
        Export table to CSV format.
        
        Args:
            table_name: Table to export (activities, events, daily_stats, etc.)
            filters: Optional filters (e.g., {"date_from": "2024-01-01"})
        
        Returns:
            CSV string with headers
        """
        logger.info(f"Exporting {table_name} to CSV")
        
        # Map table names to models
        model_map = {
            'activities': Activity,
            'events': Event,
            'daily_stats': DailyStat,
            'streaks': Streak,
            'memories': Memory,
            'journal': JournalEntry,
            'alerts': Alert,
        }
        
        if table_name not in model_map:
            raise ValueError(f"Unknown table: {table_name}")
        
        model = model_map[table_name]
        query = self.db.query(model)
        
        # Apply filters if provided
        if filters:
            if 'date_from' in filters and hasattr(model, 'date'):
                query = query.filter(model.date >= filters['date_from'])
            if 'date_to' in filters and hasattr(model, 'date'):
                query = query.filter(model.date <= filters['date_to'])
            if 'activity_id' in filters and hasattr(model, 'activity_id'):
                query = query.filter(model.activity_id == filters['activity_id'])
        
        rows = query.all()
        
        if not rows:
            logger.warning(f"No data found for {table_name}")
            return "No data\n"
        
        # Get column names
        columns = [col.name for col in model.__table__.columns]
        
        # Build CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        
        for row in rows:
            row_dict = {col: str(getattr(row, col, '')) for col in columns}
            writer.writerow(row_dict)
        
        csv_string = output.getvalue()
        logger.info(f"Exported {len(rows)} {table_name} records to CSV")
        return csv_string
    
    def export_multiple_to_csv(self, tables: List[str]) -> Dict[str, str]:
        """
        Export multiple tables to separate CSV strings.
        
        Args:
            tables: List of table names
        
        Returns:
            Dictionary mapping table names to CSV strings
        """
        results = {}
        for table in tables:
            try:
                results[table] = self.export_to_csv(table)
            except Exception as e:
                logger.error(f"Error exporting {table}: {e}")
                results[table] = f"Error: {str(e)}\n"
        
        return results
    
    # ========== JSON EXPORT ==========
    
    def export_to_json(self, include: Optional[List[str]] = None,
                      include_descriptions: bool = True) -> str:
        """
        Export data to JSON format.
        
        Args:
            include: Tables to include (None = all)
            include_descriptions: Include metadata descriptions
        
        Returns:
            JSON string with structured data
        """
        if include is None:
            include = ['activities', 'events', 'daily_stats', 'streaks', 'memories', 'journal', 'alerts']
        
        logger.info(f"Exporting to JSON: {include}")
        
        data = {
            "export_metadata": {
                "export_date": self.export_timestamp.isoformat(),
                "version": "1.0",
                "tables": include,
            }
        }
        
        # Export each table
        for table in include:
            try:
                data[table] = self._table_to_dict(table)
            except Exception as e:
                logger.error(f"Error exporting {table}: {e}")
                data[table] = {"error": str(e)}
        
        # Add descriptions if requested
        if include_descriptions:
            data["descriptions"] = self._get_descriptions()
        
        return json.dumps(data, indent=2, default=str)
    
    def _table_to_dict(self, table_name: str) -> List[Dict]:
        """Convert table to list of dictionaries."""
        model_map = {
            'activities': Activity,
            'events': Event,
            'daily_stats': DailyStat,
            'streaks': Streak,
            'memories': Memory,
            'journal': JournalEntry,
            'alerts': Alert,
        }
        
        model = model_map.get(table_name)
        if not model:
            raise ValueError(f"Unknown table: {table_name}")
        
        rows = self.db.query(model).all()
        columns = [col.name for col in model.__table__.columns]
        
        return [
            {col: str(getattr(row, col, None)) for col in columns}
            for row in rows
        ]
    
    @staticmethod
    def _get_descriptions() -> Dict[str, str]:
        """Get human-readable descriptions of tables."""
        return {
            "activities": "User-defined or auto-detected activities (coding, sleep, exercise, etc.)",
            "events": "Individual activity tracking events with timestamp and value",
            "daily_stats": "Aggregated daily statistics per activity",
            "streaks": "Consecutive-day activity streaks",
            "memories": "AI-generated memories and daily summaries for LLM context",
            "journal": "User journal entries with mood/energy scores",
            "alerts": "System alerts (burnout, streak risk, etc.)",
        }
    
    # ========== SQL EXPORT ==========
    
    def export_to_sql(self, include: Optional[List[str]] = None) -> str:
        """
        Export data as SQL INSERT statements suitable for backups/transfers.
        
        Args:
            include: Tables to include (None = all)
        
        Returns:
            SQL script with CREATE and INSERT statements
        """
        if include is None:
            include = ['activities', 'events', 'daily_stats', 'streaks', 'memories', 'journal', 'alerts']
        
        logger.info(f"Exporting to SQL: {include}")
        
        sql_lines = [
            "-- Personal Life OS Data Export",
            f"-- Generated: {self.export_timestamp.isoformat()}",
            f"-- Tables: {', '.join(include)}",
            "",
            "BEGIN TRANSACTION;",
            "",
        ]
        
        model_map = {
            'activities': Activity,
            'events': Event,
            'daily_stats': DailyStat,
            'streaks': Streak,
            'memories': Memory,
            'journal': JournalEntry,
            'alerts': Alert,
        }
        
        for table_name in include:
            if table_name not in model_map:
                continue
            
            model = model_map[table_name]
            rows = self.db.query(model).all()
            columns = [col.name for col in model.__table__.columns]
            
            # Generate INSERT statements
            for row in rows:
                values = []
                for col in columns:
                    val = getattr(row, col, None)
                    if val is None:
                        values.append('NULL')
                    elif isinstance(val, str):
                        values.append(f"'{val.replace(chr(39), chr(39)*2)}'")  # Escape quotes
                    elif isinstance(val, bool):
                        values.append(f"{1 if val else 0}")
                    else:
                        values.append(str(val))
                
                col_str = ", ".join(f'"{col}"' for col in columns)
                val_str = ", ".join(values)
                sql_lines.append(f'INSERT INTO "{table_name}" ({col_str}) VALUES ({val_str});')
        
        sql_lines.extend([
            "",
            "COMMIT;",
            f"-- End of export ({len(sql_lines)} lines)",
        ])
        
        sql_script = "\n".join(sql_lines)
        logger.info(f"Generated SQL export with {len(sql_lines)} lines")
        return sql_script
    
    # ========== FILE OPERATIONS ==========
    
    def save_csv_to_file(self, table_name: str, filepath: str) -> str:
        """Save CSV export to file."""
        csv_data = self.export_to_csv(table_name)
        Path(filepath).write_text(csv_data)
        logger.info(f"Saved CSV export to {filepath}")
        return filepath
    
    def save_json_to_file(self, filepath: str, compressed: bool = False) -> str:
        """Save JSON export to file, optionally compressed."""
        json_data = self.export_to_json()
        
        if compressed:
            filepath_gz = filepath + '.gz'
            with gzip.open(filepath_gz, 'wt') as f:
                f.write(json_data)
            logger.info(f"Saved compressed JSON export to {filepath_gz}")
            return filepath_gz
        else:
            Path(filepath).write_text(json_data)
            logger.info(f"Saved JSON export to {filepath}")
            return filepath
    
    def save_sql_to_file(self, filepath: str) -> str:
        """Save SQL export to file."""
        sql_data = self.export_to_sql()
        Path(filepath).write_text(sql_data)
        logger.info(f"Saved SQL export to {filepath}")
        return filepath
    
    def create_full_backup(self, backup_dir: str = "backups") -> Dict[str, str]:
        """
        Create full backup with all formats.
        
        Args:
            backup_dir: Directory to save backups
        
        Returns:
            Dictionary with paths to generated files
        """
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = self.export_timestamp.strftime("%Y%m%d_%H%M%S")
        
        files = {
            "csv": self.save_csv_to_file('activities', str(backup_path / f"activities_{timestamp}.csv")),
            "json": self.save_json_to_file(str(backup_path / f"full_export_{timestamp}.json"), compressed=True),
            "sql": self.save_sql_to_file(str(backup_path / f"backup_{timestamp}.sql")),
        }
        
        logger.info(f"Created full backup in {backup_dir}: {files}")
        return files
    
    # ========== STATISTICS ==========
    
    def get_export_statistics(self) -> Dict[str, Any]:
        """Get statistics about data to be exported."""
        stats = {
            "timestamp": self.export_timestamp.isoformat(),
            "record_counts": {
                "activities": self.db.query(Activity).count(),
                "events": self.db.query(Event).count(),
                "daily_stats": self.db.query(DailyStat).count(),
                "streaks": self.db.query(Streak).count(),
                "memories": self.db.query(Memory).count(),
                "journal": self.db.query(JournalEntry).count(),
                "alerts": self.db.query(Alert).count(),
            },
            "date_range": self._get_date_range(),
        }
        
        # Calculate estimated file sizes
        total_rows = sum(stats["record_counts"].values())
        stats["estimated_sizes"] = {
            "json_kb": round(total_rows * 0.5),  # Rough estimate: 0.5KB per row
            "csv_kb": round(total_rows * 0.3),
            "sql_kb": round(total_rows * 0.4),
        }
        
        return stats
    
    def _get_date_range(self) -> Dict[str, str]:
        """Get date range of tracked data."""
        earliest_event = self.db.query(Event).order_by(Event.start_time).first()
        latest_event = self.db.query(Event).order_by(Event.start_time.desc()).first()
        
        return {
            "earliest": str(earliest_event.start_time) if earliest_event else None,
            "latest": str(latest_event.start_time) if latest_event else None,
        }
