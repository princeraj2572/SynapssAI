"""
Database indexes for optimized query performance.
Create these indexes to speed up common queries.

Run with:
    alembic upgrade head
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    """Add performance indexes to database tables."""
    
    # Composite index: critical for analytics queries
    # Most analytics queries filter by date range and activity
    op.create_index(
        'idx_daily_stat_date_activity',
        'daily_stats',
        ['date', 'activity_id'],
        unique=False,
        mysql_length={'activity_id': None}
    )
    
    # Composite index for Memory queries
    # Useful for filtering by type and retrieving recent memories
    op.create_index(
        'idx_memory_type_created',
        'memories',
        ['type', 'created_at'],
        unique=False
    )
    
    # Composite index for Alert queries
    # Common pattern: find unread alerts of specific type
    op.create_index(
        'idx_alert_type_dismissed',
        'alerts',
        ['type', 'dismissed'],
        unique=False
    )
    
    # Composite index for Event queries
    # Queries often filter by activity and time range
    op.create_index(
        'idx_event_activity_start_time',
        'events',
        ['activity_id', 'start_time'],
        unique=False
    )
    
    # Single index for Journal date queries
    op.create_index(
        'idx_journal_date',
        'journal_entries',
        ['date'],
        unique=False
    )
    
    # Index for alert type filtering
    op.create_index(
        'idx_alert_type',
        'alerts',
        ['type'],
        unique=False
    )


def downgrade():
    """Remove performance indexes."""
    op.drop_index('idx_daily_stat_date_activity', table_name='daily_stats')
    op.drop_index('idx_memory_type_created', table_name='memories')
    op.drop_index('idx_alert_type_dismissed', table_name='alerts')
    op.drop_index('idx_event_activity_start_time', table_name='events')
    op.drop_index('idx_journal_date', table_name='journal_entries')
    op.drop_index('idx_alert_type', table_name='alerts')
