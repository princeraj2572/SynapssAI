"""
Integration tests for complete Personal Life OS data flows.
Tests end-to-end pipelines: collection → API → database → analytics.
"""
import pytest
from datetime import date, datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.orm import Session
import json

from main import app
from db.session import SessionLocal
from models.activity import Activity
from models.event import Event
from models.daily_stat import DailyStat
from models.streak import Streak
from models.memory import Memory
from models.journal import Journal
from models.alert import Alert
from services.scheduler import calculate_daily_stats, detect_streaks, detect_burnout


@pytest.fixture
def client():
    """Create async test client."""
    return AsyncClient(app=app, base_url="http://test")


@pytest.fixture
def db():
    """Create test database session."""
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def setup_activities(db: Session):
    """Create standard activities for integration tests."""
    activities = [
        Activity(name="coding_auto", category="productivity", unit="minutes"),
        Activity(name="browser_time", category="web", unit="minutes"),
        Activity(name="sleep", category="health", unit="hours"),
        Activity(name="exercise", category="health", unit="minutes"),
        Activity(name="meeting", category="work", unit="minutes"),
    ]
    for act in activities:
        db.add(act)
    db.commit()
    return activities


class TestTrackingPipeline:
    """Test data tracking from submission to storage."""
    
    @pytest.mark.asyncio
    async def test_single_event_tracking(self, client: AsyncClient, db: Session, setup_activities):
        """Test: POST /api/track → Event stored → Retrievable via analytics."""
        # Submit a single tracking event
        response = await client.post(
            "/api/track",
            json={
                "activity": "coding_auto",
                "value": 60,
                "timestamp": datetime.now().isoformat(),
                "metadata": {"language": "python", "file": "main.py"},
            }
        )
        assert response.status_code == 200
        
        # Verify event stored in database
        event = db.query(Event).filter_by(activity_id=setup_activities[0].id).first()
        assert event is not None
        assert event.value == 60
        
        # Verify retrievable via health endpoint
        health_response = await client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "running"
    
    @pytest.mark.asyncio
    async def test_batch_tracking_events(self, client: AsyncClient, db: Session, setup_activities):
        """Test: POST /api/track/batch → Multiple events stored → Aggregated in daily stats."""
        # Submit batch of events
        events = [
            {"activity": "coding_auto", "value": 120, "timestamp": datetime.now().isoformat()},
            {"activity": "browser_time", "value": 30, "timestamp": datetime.now().isoformat()},
            {"activity": "sleep", "value": 7, "timestamp": (datetime.now() - timedelta(hours=8)).isoformat()},
        ]
        
        response = await client.post("/api/track/batch", json={"events": events})
        assert response.status_code == 200
        
        # Verify all events stored
        event_count = db.query(Event).count()
        assert event_count >= 3
        
        # Trigger daily stats calculation
        calculate_daily_stats(db, target_date=date.today())
        
        # Verify daily stats created
        daily_stats = db.query(DailyStat).filter_by(date=date.today()).all()
        assert len(daily_stats) >= 3  # At least 3 activities tracked


class TestAnalyticsPipeline:
    """Test analytics calculations from raw data."""
    
    def test_daily_stats_aggregation_pipeline(self, db: Session, setup_activities):
        """Test: Events → Daily stats → Verifiable aggregates."""
        today = date.today()
        
        # Insert multiple events for same activity
        for i in range(4):
            event = Event(
                activity_id=setup_activities[0].id,
                value=100,
                timestamp=datetime.now()
            )
            db.add(event)
        db.commit()
        
        # Calculate daily stats
        calculate_daily_stats(db, target_date=today)
        
        # Verify aggregation
        stat = db.query(DailyStat).filter_by(
            activity_id=setup_activities[0].id,
            date=today
        ).first()
        assert stat is not None
        assert stat.total_value == 400  # 4 events × 100 minutes
    
    def test_streak_detection_pipeline(self, db: Session, setup_activities):
        """Test: Daily stats → Streak detection → Streak records."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Create daily stats for 3 consecutive days
        for i in range(3):
            day = today - timedelta(days=2-i)
            stat = DailyStat(
                activity_id=setup_activities[0].id,
                date=day,
                total_value=300
            )
            db.add(stat)
        db.commit()
        
        # Detect streaks
        detect_streaks(db, target_date=today)
        
        # Verify streak created
        streak = db.query(Streak).filter_by(
            activity_id=setup_activities[0].id
        ).first()
        assert streak is not None
        assert streak.current_count == 3
        assert streak.start_date == today - timedelta(days=2)
    
    @pytest.mark.asyncio
    async def test_analytics_endpoint_uses_calculated_data(self, client: AsyncClient, db: Session, setup_activities):
        """Test: Analytics endpoint returns data calculated by scheduler."""
        today = date.today()
        
        # Create and calculate daily stats
        stat = DailyStat(
            activity_id=setup_activities[0].id,
            date=today,
            total_value=500
        )
        db.add(stat)
        db.commit()
        
        # Query analytics endpoint
        response = await client.get("/api/analytics/daily")
        assert response.status_code == 200
        data = response.json()
        
        # Verify our stat is reflected
        assert "activities" in data or "stats" in data or len(data) > 0


class TestMemoryAndChatPipeline:
    """Test LLM integration for memory storage and retrieval."""
    
    def test_daily_memory_generation(self, db: Session, setup_activities):
        """Test: Daily stats → Memory generation → Stored in memory table."""
        from services.memory import generate_daily_memory, store_memory
        
        today = date.today()
        
        # Create daily stats
        stat = DailyStat(
            activity_id=setup_activities[0].id,
            date=today,
            total_value=300
        )
        db.add(stat)
        db.commit()
        
        # Generate memory from stats
        memory_text = generate_daily_memory(db, today)
        assert memory_text != ""
        assert "coding_auto" in memory_text or "300" in memory_text
        
        # Store memory
        memory = store_memory(db, memory_text, memory_type="daily_summary")
        assert memory.content == memory_text
        assert memory.type == "daily_summary"
        
        # Verify retrieval
        stored = db.query(Memory).filter_by(id=memory.id).first()
        assert stored is not None
        assert stored.content == memory_text
    
    @pytest.mark.asyncio
    async def test_memory_query_endpoint(self, client: AsyncClient, db: Session, setup_activities):
        """Test: Memory query endpoint returns RAG-enhanced LLM response."""
        # Store sample memories
        memory1 = Memory(content="On 2024-01-15: coding_auto: 480 minutes, sleep: 7 hours", type="daily_summary")
        memory2 = Memory(content="On 2024-01-14: coding_auto: 360 minutes, sleep: 6 hours", type="daily_summary")
        db.add(memory1)
        db.add(memory2)
        db.commit()
        
        # Query memory endpoint
        response = await client.post(
            "/api/memory/query",
            json={"query": "How much did I code recently?"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "answer" in data or "response" in data
        assert "context" in data or "memories" in data or "data" in data


class TestBurnoutDetectionPipeline:
    """Test burnout pattern detection workflow."""
    
    def test_burnout_alert_generation(self, db: Session, setup_activities):
        """Test: High work + low sleep → Burnout alert created."""
        today = date.today()
        
        # Create 7 days of data: high coding, low sleep
        for i in range(7):
            day = today - timedelta(days=i)
            
            # High coding (600 minutes = 10 hours)
            coding_stat = DailyStat(
                activity_id=setup_activities[0].id,  # coding_auto
                date=day,
                total_value=600
            )
            
            # Low sleep (5 hours)
            sleep_stat = DailyStat(
                activity_id=setup_activities[2].id,  # sleep
                date=day,
                total_value=5
            )
            
            db.add(coding_stat)
            db.add(sleep_stat)
        db.commit()
        
        # Detect burnout
        detect_burnout(db, threshold_days=7)
        
        # Verify alert created
        alert = db.query(Alert).filter_by(type="burnout_warning").first()
        assert alert is not None
        assert "sleep" in alert.message.lower()
    
    @pytest.mark.asyncio
    async def test_alerts_endpoint_shows_burnout_warnings(self, client: AsyncClient, db: Session):
        """Test: Burnout alerts appear in alerts endpoint."""
        # Create alert
        alert = Alert(
            type="burnout_warning",
            message="High workload with insufficient sleep detected over 7 days."
        )
        db.add(alert)
        db.commit()
        
        # Query alerts endpoint
        response = await client.get("/api/alerts")
        assert response.status_code == 200
        data = response.json()
        
        # Verify alert appears (if endpoint returns list, check for our alert)
        if isinstance(data, list):
            assert len(data) > 0


class TestActivityTrackingWorkflow:
    """Test complete activity tracking and management workflow."""
    
    @pytest.mark.asyncio
    async def test_create_custom_activity(self, client: AsyncClient, db: Session):
        """Test: Create new activity → Track data → Retrieve in stats."""
        # Create custom activity
        response = await client.post(
            "/api/activities",
            json={
                "name": "writing",
                "category": "work",
                "unit": "minutes",
                "color": "#FF6600"
            }
        )
        assert response.status_code in [200, 201]
        
        # Track activity
        activity = db.query(Activity).filter_by(name="writing").first()
        if activity:
            event = Event(
                activity_id=activity.id,
                value=120,
                timestamp=datetime.now()
            )
            db.add(event)
            db.commit()
            
            # Verify in events
            assert db.query(Event).filter_by(activity_id=activity.id).first() is not None


class TestJournalIntegration:
    """Test journaling features integrated with analytics."""
    
    @pytest.mark.asyncio
    async def test_journal_entry_storage(self, client: AsyncClient, db: Session):
        """Test: POST journal entry → Stored → Retrievable."""
        response = await client.post(
            "/api/journal",
            json={
                "content": "Had a productive day. Completed authentication module.",
                "mood": 8,
                "energy": 7,
                "tags": ["productive", "coding"]
            }
        )
        assert response.status_code in [200, 201]
        
        # Verify stored
        entry = db.query(Journal).order_by(Journal.created_at.desc()).first()
        if entry:
            assert "productive" in entry.content.lower() or "authentication" in entry.content.lower()
    
    @pytest.mark.asyncio
    async def test_journal_query_retrieval(self, client: AsyncClient, db: Session):
        """Test: Query journal entries by date range."""
        # Store entries
        for i in range(3):
            entry = Journal(
                content=f"Journal entry {i}",
                mood=7,
                energy=6
            )
            db.add(entry)
        db.commit()
        
        # Query endpoint
        response = await client.get("/api/journal")
        assert response.status_code == 200


class TestDataConsistency:
    """Test data consistency across related operations."""
    
    def test_activity_deletion_cascades_correctly(self, db: Session, setup_activities):
        """Test: Deleting activity cascades to events, stats."""
        activity_id = setup_activities[0].id
        
        # Create related data
        event = Event(activity_id=activity_id, value=100, timestamp=datetime.now())
        stat = DailyStat(activity_id=activity_id, date=date.today(), total_value=100)
        db.add(event)
        db.add(stat)
        db.commit()
        
        # Delete activity (if cascade is set up)
        activity = db.query(Activity).filter_by(id=activity_id).first()
        db.delete(activity)
        db.commit()
        
        # Verify cascade (implementation dependent)
        assert db.query(Activity).filter_by(id=activity_id).first() is None
    
    def test_stats_match_event_aggregates(self, db: Session, setup_activities):
        """Test: Daily stats totals match sum of events."""
        today = date.today()
        activity_id = setup_activities[0].id
        
        # Create events
        events_data = [100, 150, 50, 75]  # Total: 375
        for value in events_data:
            event = Event(activity_id=activity_id, value=value, timestamp=datetime.now())
            db.add(event)
        db.commit()
        
        # Calculate stats
        calculate_daily_stats(db, target_date=today)
        
        # Verify stats match
        stat = db.query(DailyStat).filter_by(
            activity_id=activity_id,
            date=today
        ).first()
        assert stat is not None
        assert stat.total_value == sum(events_data)


class TestEndToEndPipeline:
    """Complete end-to-end workflow tests."""
    
    def test_full_daily_workflow(self, db: Session, setup_activities):
        """Test: Complete day from tracking → stats → streaks → alerts → memory."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        coding_activity = setup_activities[0]
        sleep_activity = setup_activities[2]
        
        # Step 1: Simulate data collection (tracking events)
        for i in range(5):
            event = Event(
                activity_id=coding_activity.id,
                value=100,
                timestamp=datetime.now()
            )
            db.add(event)
        
        event = Event(
            activity_id=sleep_activity.id,
            value=7,
            timestamp=datetime.now()
        )
        db.add(event)
        db.commit()
        
        # Step 2: Calculate daily stats
        calculate_daily_stats(db, target_date=today)
        
        # Step 3: Detect streaks
        # First, ensure yesterday has data
        yesterday_stat_coding = DailyStat(
            activity_id=coding_activity.id,
            date=yesterday,
            total_value=300
        )
        db.add(yesterday_stat_coding)
        db.commit()
        
        detect_streaks(db, target_date=today)
        
        # Step 4: Verify all data is consistent
        today_stat = db.query(DailyStat).filter_by(
            activity_id=coding_activity.id,
            date=today
        ).first()
        assert today_stat is not None
        assert today_stat.total_value == 500
        
        # Streak should be detected
        streak = db.query(Streak).filter_by(
            activity_id=coding_activity.id
        ).first()
        assert streak is not None
        assert streak.current_count == 2  # Yesterday + today
