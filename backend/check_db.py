#!/usr/bin/env python
"""Quick backend health check"""
import sys
sys.path.insert(0, '.')

try:
    from db.session import engine, SessionLocal
    from sqlalchemy import text
    
    # Try to establish connection
    with engine.connect() as conn:
        result = conn.execute(text('SELECT version();'))
        db_version = result.fetchone()[0]
        print('✓ Database connection successful')
        print(f'  Version: {db_version.split()[1]}')
        
        # Check tables
        tables = ['activities', 'events', 'streaks', 'alerts', 'daily_stats', 'journal_entries', 'memories']
        for table in tables:
            result = conn.execute(text(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table}';"))
            exists = result.fetchone()[0] > 0
            status = '✓' if exists else '✗'
            print(f'  {status} {table}')

except Exception as e:
    print(f'✗ Database check failed: {e}')
    sys.exit(1)
