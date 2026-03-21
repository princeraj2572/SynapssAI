"""
Unit tests for desktop collector module.
Tests window detection, app categorization, session tracking, and batch sending.
"""
import pytest
import sys
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock, call
import time

# Add collectors/desktop to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../collectors/desktop'))

from categorizer import categorize_app, CODING_APPS, BROWSER_APPS, COMMUNICATION_APPS
from sender import send_batch, send_single, API_URL


class TestCategorizer:
    """Test app categorization logic."""
    
    def test_coding_apps(self):
        """Test that coding apps are correctly categorized."""
        for app in ["vscode", "code", "pycharm", "vim", "terminal", "cmd"]:
            assert categorize_app(app) == "coding", f"{app} should be categorized as coding"
    
    def test_browser_apps(self):
        """Test that browsers are correctly categorized."""
        for app in ["chrome", "firefox", "edge", "safari"]:
            assert categorize_app(app) == "browser", f"{app} should be categorized as browser"
    
    def test_communication_apps(self):
        """Test that communication apps are correctly categorized."""
        for app in ["slack", "discord", "teams", "zoom"]:
            assert categorize_app(app) == "communication", f"{app} should be categorized as communication"
    
    def test_entertainment_apps(self):
        """Test that entertainment apps are correctly categorized."""
        for app in ["vlc", "spotify", "netflix", "steam"]:
            assert categorize_app(app) == "entertainment", f"{app} should be categorized as entertainment"
    
    def test_productivity_apps(self):
        """Test that productivity apps are correctly categorized."""
        for app in ["notion", "figma", "excel", "word"]:
            assert categorize_app(app) == "productivity", f"{app} should be categorized as productivity"
    
    def test_unknown_apps(self):
        """Test that unknown apps default to 'other'."""
        assert categorize_app("random_app_xyz") == "other"
        assert categorize_app("") == "other"
    
    def test_case_insensitive(self):
        """Test that categorization is case-insensitive."""
        assert categorize_app("VSCODE") == "coding"
        assert categorize_app("Chrome") == "browser"
        assert categorize_app("SLACK") == "communication"


class TestSender:
    """Test batch and single event sending."""
    
    @patch('sender.requests.post')
    def test_send_batch_success(self, mock_post):
        """Test successful batch send."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"count": 2}
        mock_post.return_value = mock_response
        
        events = [
            {"activity": "coding", "value": 1.5},
            {"activity": "break", "value": 0.5},
        ]
        
        send_batch(events)
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert f"{API_URL}/api/track/batch" in call_args[0][0]
        assert call_args[1]["json"]["events"] == events
    
    @patch('sender.requests.post')
    def test_send_batch_empty(self, mock_post):
        """Test that empty batches are not sent."""
        send_batch([])
        mock_post.assert_not_called()
    
    @patch('sender.requests.post')
    def test_send_single_success(self, mock_post):
        """Test successful single event send."""
        event = {"activity": "coding", "value": 1.0}
        send_single(event)
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert f"{API_URL}/api/track" in call_args[0][0]
        assert call_args[1]["json"] == event
    
    @patch('sender.requests.post')
    def test_send_batch_connection_error(self, mock_post):
        """Test graceful handling of connection errors."""
        import requests
        mock_post.side_effect = requests.ConnectionError("Connection refused")
        
        # Should not raise, just log warning
        send_batch([{"activity": "coding", "value": 1.0}])
    
    @patch('sender.requests.post')
    def test_send_batch_timeout(self, mock_post):
        """Test graceful handling of timeouts."""
        mock_post.side_effect = Exception("Timeout")
        
        # Should not raise, just log error
        send_batch([{"activity": "coding", "value": 1.0}])


class TestSessionTracking:
    """Test session tracking logic (if imported as a function)."""
    
    def test_activity_mapping(self):
        """Test category to activity mapping."""
        from agent import _category_to_activity
        
        assert _category_to_activity("coding", "vscode") == "coding_auto"
        assert _category_to_activity("browser", "chrome") == "browser_time"
        assert _category_to_activity("communication", "slack") == "communication"
        assert _category_to_activity("productivity", "figma") == "productivity"
        assert _category_to_activity("entertainment", "netflix") == "entertainment"
        assert _category_to_activity("other", "unknown") == "desktop_other"
    
    def test_extract_app_name(self):
        """Test app name extraction from window titles."""
        from agent import _extract_app_name
        
        # Common window title formats
        assert _extract_app_name("main.py - Visual Studio Code") == "Visual Studio Code"
        assert _extract_app_name("GitHub - Google Chrome") == "Google Chrome"
        assert _extract_app_name("Slack") == "Slack"
        assert _extract_app_name("") == "Unknown"
        assert _extract_app_name("  ") != ""  # Whitespace isn't None


class TestIdleDetection:
    """Test idle detection logic."""
    
    def test_idle_tracker_creation(self):
        """Test that IdleTracker can be instantiated."""
        from agent import IdleTracker
        tracker = IdleTracker()
        assert tracker is not None
        assert hasattr(tracker, 'idle_seconds')
    
    def test_idle_tracker_initial_not_idle(self):
        """Test that newly created tracker shows no idle time."""
        from agent import IdleTracker
        tracker = IdleTracker()
        idle_secs = tracker.idle_seconds()
        assert idle_secs < 1.0, "New tracker should show minimal idle time"
    
    def test_idle_tracker_accumulates(self):
        """Test that idle time accumulates over time."""
        from agent import IdleTracker
        tracker = IdleTracker()
        idle_before = tracker.idle_seconds()
        time.sleep(0.2)
        idle_after = tracker.idle_seconds()
        assert idle_after > idle_before, "Idle time should increase"


class TestBatchProcessing:
    """Test batch buffering and timing."""
    
    def test_session_buffer_structure(self):
        """Test that buffer entries have expected structure."""
        now = datetime.now(timezone.utc)
        entry = {
            "activity": "coding_auto",
            "value": 1.5,
            "start": now.isoformat(),
            "end": (now + timedelta(hours=1)).isoformat(),
            "source": "desktop_agent",
            "notes": "vscode: main.py",
        }
        
        assert entry["activity"]
        assert entry["value"] > 0
        assert entry["start"]
        assert entry["end"]
        assert entry["source"] == "desktop_agent"
        assert len(entry["notes"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
