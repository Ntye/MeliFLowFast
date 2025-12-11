"""
Tests for health check endpoints.
"""
import json


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code in [200, 503]  # May be unhealthy if no DB
    
    data = json.loads(response.data)
    assert 'status' in data
    assert 'timestamp' in data
    assert 'checks' in data
    assert 'database' in data['checks']


def test_status_endpoint(client):
    """Test status endpoint."""
    response = client.get('/status')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'api_title' in data
    assert 'api_version' in data
    assert 'timestamp' in data
    assert 'features' in data


def test_docs_endpoint(client):
    """Test documentation endpoint."""
    response = client.get('/docs')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'api_title' in data
    assert 'endpoints' in data
    assert 'features' in data
    
    # Check root path also works
    response = client.get('/')
    assert response.status_code == 200
