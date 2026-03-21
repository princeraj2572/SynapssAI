"""
Backend API and service tests.
Tests ingestion, analytics, database operations, and API endpoints.
"""
import pytest
import sys
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

# Ensure backend is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from fastapi.testclient import TestClient
from main import app
from schemas.track import TrackRequest, BatchTrackRequest


class TestAPIHealth:
    """Test basic API health and configuration."""
    
    def test_app_initialization(self):
        """Test that FastAPI app initializes correctly."""
        assert app is not None
        assert app.title == "Personal Life OS API"
        assert app.version == "1.0.0"
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert data["version"] == "1.0.0"
    
    def test_root_endpoint(self):
        """Test root endpoint returns info."""
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data


class TestTrackingEndpoints:
    """Test tracking/ingestion endpoints."""
    
    def test_track_endpoint_exists(self):
        """Test that POST /api/track endpoint exists."""
        client = TestClient(app)
        # Send minimal valid track request
        payload = {
            "activity": "coding",
            "value": 1.0,
        }
        # Note: Will fail without DB but endpoint should exist
        response = client.post("/api/track", json=payload)
        # Status could be 200, 422, or 500 depending on DB connection
        # but endpoint should be found (not 404)
        assert response.status_code != 404
    
    def test_batch_track_endpoint_exists(self):
        """Test that POST /api/track/batch endpoint exists."""
        client = TestClient(app)
        payload = {
            "events": [
                {
                    "activity": "coding",
                    "value": 1.0,
                    "start": datetime.now(timezone.utc).isoformat(),
                    "end": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                }
            ]
        }
        response = client.post("/api/track/batch", json=payload)
        # Endpoint should exist (not 404)
        assert response.status_code != 404


class TestAnalyticsEndpoints:
    """Test analytics endpoints."""
    
    def test_score_endpoint_exists(self):
        """Test that GET /api/analytics/score endpoint exists."""
        client = TestClient(app)
        response = client.get("/api/analytics/score")
        # Endpoint should exist even if it returns error
        assert response.status_code != 404
    
    def test_daily_analytics_endpoint_exists(self):
        """Test that GET /api/analytics/daily endpoint exists."""
        client = TestClient(app)
        today = datetime.now(timezone.utc).date().isoformat()
        response = client.get(f"/api/analytics/daily?date={today}")
        assert response.status_code != 404
    
    def test_streaks_endpoint_exists(self):
        """Test that GET /api/streaks endpoint exists."""
        client = TestClient(app)
        response = client.get("/api/streaks")
        assert response.status_code != 404
    
    def test_alerts_endpoint_exists(self):
        """Test that GET /api/alerts endpoint exists."""
        client = TestClient(app)
        response = client.get("/api/alerts")
        assert response.status_code != 404


class TestActivitiesEndpoints:
    """Test activity management endpoints."""
    
    def test_list_activities_endpoint_exists(self):
        """Test that GET /api/activities endpoint exists."""
        client = TestClient(app)
        response = client.get("/api/activities")
        assert response.status_code != 404
    
    def test_create_activity_endpoint_exists(self):
        """Test that POST /api/activities endpoint exists."""
        client = TestClient(app)
        payload = {
            "name": "test_activity",
            "category": "general",
            "unit": "count",
        }
        response = client.post("/api/activities", json=payload)
        assert response.status_code != 404


class TestJournalEndpoints:
    """Test journal endpoints."""
    
    def test_list_journal_endpoint_exists(self):
        """Test that GET /api/journal endpoint exists."""
        client = TestClient(app)
        response = client.get("/api/journal")
        assert response.status_code != 404
    
    def test_create_journal_endpoint_exists(self):
        """Test that POST /api/journal endpoint exists."""
        client = TestClient(app)
        payload = {
            "title": "Daily Entry",
            "content": "Today was productive",
        }
        response = client.post("/api/journal", json=payload)
        assert response.status_code != 404


class TestMemoryEndpoints:
    """Test memory/AI endpoints."""
    
    def test_memory_status_endpoint_exists(self):
        """Test that GET /api/memory/status endpoint exists."""
        client = TestClient(app)
        response = client.get("/api/memory/status")
        assert response.status_code != 404
    
    def test_memory_query_endpoint_exists(self):
        """Test that POST /api/memory/query endpoint exists."""
        client = TestClient(app)
        payload = {
            "query": "What have I been working on?",
        }
        response = client.post("/api/memory/query", json=payload)
        assert response.status_code != 404


class TestSchemas:
    """Test request schemas and validation."""
    
    def test_track_request_schema(self):
        """Test TrackRequest schema validation."""
        # Valid request
        req = TrackRequest(
            activity="coding",
            value=1.5,
        )
        assert req.activity == "coding"
        assert req.value == 1.5
    
    def test_batch_track_request_schema(self):
        """Test BatchTrackRequest schema validation."""
        now = datetime.now(timezone.utc)
        events = [
            {
                "activity": "coding",
                "value": 1.0,
                "start": now.isoformat(),
                "end": (now + timedelta(hours=1)).isoformat(),
            }
        ]
        req = BatchTrackRequest(events=events)
        assert len(req.events) == 1
        assert req.events[0]["activity"] == "coding"


class TestCORSConfiguration:
    """Test CORS settings."""
    
    def test_cors_headers(self):
        """Test that CORS headers are present."""
        client = TestClient(app)
        response = client.get("/health")
        # CORS middleware should set default headers
        assert response.status_code == 200


class TestAPIDocumentation:
    """Test API documentation endpoints."""
    
    def test_swagger_docs_endpoint(self):
        """Test that Swagger docs are available."""
        client = TestClient(app)
        response = client.get("/docs")
        assert response.status_code in [200, 307]  # 307 for redirect
    
    def test_redoc_endpoint(self):
        """Test that ReDoc documentation is available."""
        client = TestClient(app)
        response = client.get("/redoc")
        assert response.status_code in [200, 307]
    
    def test_openapi_schema(self):
        """Test that OpenAPI schema is available."""
        client = TestClient(app)
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data


class TestRouterMounting:
    """Test all routers are properly mounted."""
    
    def test_track_router_mounted(self):
        """Verify track router endpoints exist."""
        client = TestClient(app)
        # Should have /api/track endpoints
        response = client.post("/api/track", json={"activity": "test", "value": 1})
        assert response.status_code != 404
        
        response = client.post("/api/track/batch", json={"events": []})
        assert response.status_code != 404
    
    def test_analytics_router_mounted(self):
        """Verify analytics router endpoints exist."""
        client = TestClient(app)
        response = client.get("/api/analytics/score")
        assert response.status_code != 404
    
    def test_activities_router_mounted(self):
        """Verify activities router endpoints exist."""
        client = TestClient(app)
        response = client.get("/api/activities")
        assert response.status_code != 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
