"""
Tests for background job scheduler (APScheduler integration).
"""
import pytest
import asyncio
from datetime import date, timedelta
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch, MagicMock

from models.activity import Activity
from models.daily_stat import DailyStat
from models.event import Event
from models.streak import Streak
from models.alert import Alert
from services.scheduler import (
    calculate_daily_stats,
    detect_streaks,
    detect_correlations,
    detect_burnout,
    daily_analytics_job,
    start_scheduler,
    stop_scheduler,
)


@pytest.fixture
def sample_activities(db: Session):
    """Create sample activities for testing."""
    activities = [
        Activity(name="coding_auto", category="productivity", unit="minutes"),
        Activity(name="sleep", category="health", unit="hours"),
        Activity(name="exercise", category="health", unit="minutes"),
        Activity(name="coding", category="productivity", unit="minutes"),
    ]
    for activity in activities:
        db.add(activity)
    db.commit()
    return activities


@pytest.fixture
def sample_events(db: Session, sample_activities):
    """Create sample activity events for testing."""
    today = date.today()
    events = []
    
    # Today: 8 hours coding, 7 hours sleep
    events.append(Event(activity_id=sample_activities[0].id, value=480, timestamp=date(today.year, today.month, today.day)))
    events.append(Event(activity_id=sample_activities[1].id, value=7, timestamp=date(today.year, today.month, today.day)))
    
    # Yesterday: 6 hours coding, 5 hours sleep
    yesterday = today - timedelta(days=1)
    events.append(Event(activity_id=sample_activities[0].id, value=360, timestamp=yesterday))
    events.append(Event(activity_id=sample_activities[1].id, value=5, timestamp=yesterday))
    
    for event in events:
        db.add(event)
    db.commit()
    return events


class TestDailyStatsCalculation:
    """Test daily stats calculation."""
    
    def test_calculate_daily_stats_aggregates_events(self, db: Session, sample_activities, sample_events):
        """Test that daily stats are calculated correctly from events."""
        today = date.today()
        calculate_daily_stats(db, target_date=today)
        
        # Verify daily stat was created
        stat = db.query(DailyStat).filter_by(
            activity_id=sample_activities[0].id,
            date=today
        ).first()
        assert stat is not None
        assert stat.total_value == 480  # 8 hours in minutes
    
    def test_calculate_daily_stats_updates_existing(self, db: Session, sample_activities, sample_events):
        """Test that existing daily stats are updated."""
        today = date.today()
        
        # Create initial stat
        stat = DailyStat(activity_id=sample_activities[0].id, date=today, total_value=100)
        db.add(stat)
        db.commit()
        
        # Calculate (should update)
        calculate_daily_stats(db, target_date=today)
        
        # Verify it was updated, not duplicated
        stats = db.query(DailyStat).filter_by(
            activity_id=sample_activities[0].id,
            date=today
        ).all()
        assert len(stats) == 1
        assert stats[0].total_value == 480  # Updated value


class TestStreakDetection:
    """Test streak detection logic."""
    
    def test_detect_streaks_starts_new_streak(self, db: Session, sample_activities):
        """Test that streaks are started for activities done today."""
        today = date.today()
        
        # Create today's stat
        stat = DailyStat(activity_id=sample_activities[0].id, date=today, total_value=480)
        db.add(stat)
        db.commit()
        
        # Detect streaks
        detect_streaks(db, target_date=today)
        
        # Verify streak was created
        streak = db.query(Streak).filter_by(activity_id=sample_activities[0].id).first()
        assert streak is not None
        assert streak.current_count == 1
        assert streak.start_date == today
    
    def test_detect_streaks_continues_streak(self, db: Session, sample_activities):
        """Test that streaks continue for consecutive days."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Create stats for yesterday and today
        yesterday_stat = DailyStat(activity_id=sample_activities[0].id, date=yesterday, total_value=240)
        today_stat = DailyStat(activity_id=sample_activities[0].id, date=today, total_value=480)
        db.add(yesterday_stat)
        db.add(today_stat)
        db.commit()
        
        # Start streak on yesterday
        streak = Streak(
            activity_id=sample_activities[0].id,
            start_date=yesterday,
            current_count=1,
            longest_count=1,
        )
        db.add(streak)
        db.commit()
        
        # Detect streaks
        detect_streaks(db, target_date=today)
        
        # Verify streak was continued
        streak = db.query(Streak).filter_by(activity_id=sample_activities[0].id).first()
        assert streak.current_count == 2
        assert streak.end_date is None


class TestBurnoutDetection:
    """Test burnout pattern detection."""
    
    def test_detect_burnout_triggers_alert(self, db: Session, sample_activities):
        """Test that burnout alert is created for high work + low sleep."""
        today = date.today()
        
        # Create stats for last 7 days: high coding + low sleep
        for i in range(7):
            day = today - timedelta(days=i)
            # High coding (10 hours = 600 minutes)
            coding_stat = DailyStat(activity_id=sample_activities[0].id, date=day, total_value=600)
            # Low sleep (5 hours)
            sleep_stat = DailyStat(activity_id=sample_activities[1].id, date=day, total_value=5)
            db.add(coding_stat)
            db.add(sleep_stat)
        db.commit()
        
        # Detect burnout
        detect_burnout(db, threshold_days=7)
        
        # Verify alert was created
        alert = db.query(Alert).filter_by(type="burnout_warning").first()
        assert alert is not None
        assert "sleep" in alert.message.lower()
    
    def test_detect_burnout_no_alert_with_rest(self, db: Session, sample_activities):
        """Test that no burnout alert is created with adequate rest."""
        today = date.today()
        
        # Create stats for last 7 days: high coding + good sleep
        for i in range(7):
            day = today - timedelta(days=i)
            coding_stat = DailyStat(activity_id=sample_activities[0].id, date=day, total_value=600)
            sleep_stat = DailyStat(activity_id=sample_activities[1].id, date=day, total_value=8)  # 8 hours sleep
            db.add(coding_stat)
            db.add(sleep_stat)
        db.commit()
        
        # Count existing alerts
        initial_alerts = db.query(Alert).filter_by(type="burnout_warning").count()
        
        # Detect burnout
        detect_burnout(db, threshold_days=7)
        
        # Verify no new alert was created
        final_alerts = db.query(Alert).filter_by(type="burnout_warning").count()
        assert final_alerts == initial_alerts


class TestCorrelationDetection:
    """Test correlation pattern detection."""
    
    def test_detect_correlations_analyzes_patterns(self, db: Session, sample_activities):
        """Test that correlation analysis runs without error."""
        today = date.today()
        
        # Create stats with potential patterns
        for i in range(30):
            day = today - timedelta(days=i)
            stat = DailyStat(activity_id=sample_activities[0].id, date=day, total_value=300 + (i * 10))
            db.add(stat)
        db.commit()
        
        # Run correlation detection (just verify it doesn't crash)
        detect_correlations(db, days=30)


class TestDailyAnalyticsJob:
    """Test the complete daily analytics job."""
    
    def test_daily_analytics_job_runs_all_tasks(self, db: Session, sample_activities, sample_events):
        """Test that the job runs all analytics tasks."""
        # Just verify the job doesn't crash
        daily_analytics_job()


class TestSchedulerLifecycle:
    """Test scheduler start/stop lifecycle."""
    
    def test_start_and_stop_scheduler(self):
        """Test that scheduler can be started and stopped."""
        # Start scheduler
        start_scheduler()
        
        # Stop scheduler
        stop_scheduler()
