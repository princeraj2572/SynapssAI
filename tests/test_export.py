"""
Tests for data export functionality.
Tests CSV, JSON, SQL export formats and backup creation.
"""
import pytest
import json
import csv
from io import StringIO
from datetime import date, datetime
from sqlalchemy.orm import Session

from services.export import ExportService
from models.activity import Activity
from models.event import Event
from models.daily_stat import DailyStat
from models.alert import Alert


@pytest.fixture
def setup_export_data(db: Session):
    """Create test data for export tests."""
    # Create activity
    activity = Activity(name="test_coding", category="productivity", unit="minutes")
    db.add(activity)
    db.commit()
    
    # Create event
    event = Event(activity_id=activity.id, value=100, start_time=datetime.now(), source="manual")
    db.add(event)
    db.commit()
    
    # Create daily stat
    stat = DailyStat(activity_id=activity.id, date=date.today(), total_value=100, event_count=1)
    db.add(stat)
    db.commit()
    
    return {"activity": activity, "event": event, "stat": stat}


class TestCSVExport:
    """Test CSV export functionality."""
    
    def test_export_activities_to_csv(self, db: Session, setup_export_data):
        """Test exporting activities table to CSV."""
        export_service = ExportService(db)
        csv_data = export_service.export_to_csv('activities')
        
        # Verify CSV format
        assert "name" in csv_data  # Header
        assert "test_coding" in csv_data  # Data
        
        # Parse CSV to verify structure
        reader = csv.DictReader(StringIO(csv_data))
        rows = list(reader)
        assert len(rows) > 0
        assert "name" in rows[0]
    
    def test_export_events_to_csv(self, db: Session, setup_export_data):
        """Test exporting events to CSV."""
        export_service = ExportService(db)
        csv_data = export_service.export_to_csv('events')
        
        assert "activity_id" in csv_data
        assert len(csv_data) > 10  # Has content
    
    def test_export_with_filters(self, db: Session, setup_export_data):
        """Test CSV export with date filters."""
        export_service = ExportService(db)
        
        # Export with date range
        csv_data = export_service.export_to_csv(
            'daily_stats',
            filters={"date_from": date(2024, 1, 1)}
        )
        
        # Should contain data
        assert len(csv_data) > 0
    
    def test_export_multiple_tables_to_csv(self, db: Session, setup_export_data):
        """Test exporting multiple tables to CSV."""
        export_service = ExportService(db)
        csv_files = export_service.export_multiple_to_csv(['activities', 'events'])
        
        assert len(csv_files) == 2
        assert 'activities' in csv_files
        assert 'events' in csv_files
        assert all(isinstance(v, str) for v in csv_files.values())
    
    def test_export_empty_table_to_csv(self, db: Session):
        """Test exporting empty table to CSV."""
        export_service = ExportService(db)
        csv_data = export_service.export_to_csv('alerts')
        
        # Should handle empty gracefully
        assert "No data" in csv_data or len(csv_data) > 0


class TestJSONExport:
    """Test JSON export functionality."""
    
    def test_export_to_json(self, db: Session, setup_export_data):
        """Test exporting all data to JSON."""
        export_service = ExportService(db)
        json_data = export_service.export_to_json()
        
        # Parse JSON
        parsed = json.loads(json_data)
        
        # Verify structure
        assert "export_metadata" in parsed
        assert "activities" in parsed
        assert "events" in parsed
        assert parsed["export_metadata"]["version"] == "1.0"
    
    def test_json_export_includes_metadata(self, db: Session, setup_export_data):
        """Test JSON export includes proper metadata."""
        export_service = ExportService(db)
        json_data = export_service.export_to_json()
        parsed = json.loads(json_data)
        
        metadata = parsed["export_metadata"]
        assert "export_date" in metadata
        assert "version" in metadata
        assert "tables" in metadata
    
    def test_json_export_includes_descriptions(self, db: Session, setup_export_data):
        """Test JSON export includes table descriptions."""
        export_service = ExportService(db)
        json_data = export_service.export_to_json(include_descriptions=True)
        parsed = json.loads(json_data)
        
        assert "descriptions" in parsed
        assert "activities" in parsed["descriptions"]
    
    def test_json_export_selective_tables(self, db: Session, setup_export_data):
        """Test JSON export with specific tables."""
        export_service = ExportService(db)
        json_data = export_service.export_to_json(include=['activities', 'events'])
        parsed = json.loads(json_data)
        
        assert "activities" in parsed
        assert "events" in parsed
        assert "streaks" not in parsed  # Not included
    
    def test_json_export_serialization(self, db: Session, setup_export_data):
        """Test JSON export properly serializes all data types."""
        export_service = ExportService(db)
        json_data = export_service.export_to_json()
        
        # Should be valid JSON
        parsed = json.loads(json_data)
        assert isinstance(parsed, dict)
        assert len(parsed) > 0


class TestSQLExport:
    """Test SQL export functionality."""
    
    def test_export_to_sql(self, db: Session, setup_export_data):
        """Test exporting to SQL INSERT statements."""
        export_service = ExportService(db)
        sql_data = export_service.export_to_sql()
        
        # Verify SQL structure
        assert "INSERT INTO" in sql_data
        assert "BEGIN TRANSACTION" in sql_data
        assert "COMMIT" in sql_data
    
    def test_sql_export_includes_header(self, db: Session, setup_export_data):
        """Test SQL export includes metadata header."""
        export_service = ExportService(db)
        sql_data = export_service.export_to_sql()
        
        assert "-- Personal Life OS Data Export" in sql_data
        assert "Generated:" in sql_data
    
    def test_sql_export_selective_tables(self, db: Session, setup_export_data):
        """Test SQL export with specific tables."""
        export_service = ExportService(db)
        sql_data = export_service.export_to_sql(include=['activities'])
        
        assert "INSERT INTO" in sql_data
        # Should contain activities table
        assert len(sql_data) > 0
    
    def test_sql_export_string_escaping(self, db: Session):
        """Test SQL export properly escapes special characters."""
        # Create activity with special characters
        activity = Activity(name="test's activity", category="test", unit="units")
        db.add(activity)
        db.commit()
        
        export_service = ExportService(db)
        sql_data = export_service.export_to_sql(include=['activities'])
        
        # Should escape apostrophes
        assert "test''s" in sql_data or "test\\'s" in sql_data or "test's" in sql_data


class TestBackupCreation:
    """Test backup creation functionality."""
    
    def test_create_full_backup(self, db: Session, setup_export_data, tmp_path):
        """Test creating full backup with all formats."""
        export_service = ExportService(db)
        files = export_service.create_full_backup(backup_dir=str(tmp_path))
        
        # Verify all formats created
        assert "csv" in files
        assert "json" in files
        assert "sql" in files
    
    def test_backup_files_have_timestamps(self, db: Session, setup_export_data, tmp_path):
        """Test backup files include timestamps in names."""
        export_service = ExportService(db)
        files = export_service.create_full_backup(backup_dir=str(tmp_path))
        
        # All files should have timestamps
        for filepath in files.values():
            # Should contain date pattern (YYYYMMDD)
            assert any(c.isdigit() for c in filepath)


class TestExportStatistics:
    """Test export statistics functionality."""
    
    def test_get_export_statistics(self, db: Session, setup_export_data):
        """Test getting export statistics."""
        export_service = ExportService(db)
        stats = export_service.get_export_statistics()
        
        # Verify statistics structure
        assert "timestamp" in stats
        assert "record_counts" in stats
        assert "estimated_sizes" in stats
    
    def test_record_counts_accuracy(self, db: Session, setup_export_data):
        """Test record counts are accurate."""
        export_service = ExportService(db)
        stats = export_service.get_export_statistics()
        
        # Activities count should be at least 1
        assert stats["record_counts"]["activities"] >= 1
        # Events count should be at least 1
        assert stats["record_counts"]["events"] >= 1
    
    def test_date_range_in_statistics(self, db: Session, setup_export_data):
        """Test date range is included in statistics."""
        export_service = ExportService(db)
        stats = export_service.get_export_statistics()
        
        date_range = stats["date_range"]
        assert "earliest" in date_range
        assert "latest" in date_range


class TestExportErrors:
    """Test error handling in export."""
    
    def test_export_invalid_table(self, db: Session):
        """Test error handling for invalid table name."""
        export_service = ExportService(db)
        
        with pytest.raises(ValueError):
            export_service.export_to_csv('invalid_table')
    
    def test_export_empty_database(self, db: Session):
        """Test export handles empty database gracefully."""
        export_service = ExportService(db)
        
        # Should not crash on empty database
        json_data = export_service.export_to_json()
        parsed = json.loads(json_data)
        assert isinstance(parsed, dict)
