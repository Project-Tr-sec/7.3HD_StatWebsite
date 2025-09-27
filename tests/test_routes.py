"""Tests for routes module."""
import math
from app import create_app


def test_healthz():
    """Test health check endpoint."""
    app = create_app()
    with app.test_client() as client:
        response = client.get('/healthz')
        assert response.status_code == 200
        assert response.json == {"status": "healthy"}


def test_api_log():
    """Test logarithm API endpoint."""
    app = create_app()
    with app.test_client() as client:
        response = client.post('/api/log', json={'value': math.e})
        assert response.status_code == 200
        assert abs(response.json['result'] - 1.0) < 1e-12