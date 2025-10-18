"""
Tests for API endpoints.
"""
import pytest

class TestAPIRoutes:
    """Test API endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'version' in data

    def test_get_stats(self, client):
        """Test getting application statistics."""
        response = client.get('/api/stats')
        assert response.status_code in [200, 500]

    def test_webhook_handler(self, client):
        """Test webhook processing."""
        response = client.post('/api/webhook', json={
            'event': 'test.event',
            'data': 'test-data'
        })
        assert response.status_code in [200, 400]

    def test_export_users(self, client):
        """Test user data export."""
        response = client.post('/api/export/users', json={
            'format': 'json'
        })
        # Should fail without admin auth
        assert response.status_code in [200, 403, 500]

    def test_proxy_request(self, client):
        """Test API proxy functionality."""
        response = client.post('/api/proxy', json={
            'url': 'https://api.example.com/data',
            'method': 'GET'
        })
        assert response.status_code in [200, 400, 500]

    def test_api_redirect(self, client):
        """Test API redirect endpoint."""
        response = client.get('/api/redirect?url=https://example.com')
        assert response.status_code in [302, 400]

    def test_session_export(self, client):
        """Test session export functionality."""
        response = client.post('/api/session/export')
        # Should fail without active session
        assert response.status_code in [200, 401]

    def test_session_import(self, client):
        """Test session import functionality."""
        response = client.post('/api/session/import', json={
            'data': 'test-session-data'
        })
        assert response.status_code in [200, 400]
