"""
Test suite for Flask API endpoints
"""
import pytest
import json
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    """Test the index route returns HTML"""
    response = client.get('/')
    assert response.status_code == 200


def test_search_endpoint(client):
    """Test the search endpoint"""
    # Test with GET request (query parameter)
    response = client.get('/search?q=laptop&page=1&per_page=5')
    assert response.status_code in [200, 405]  # May not support GET
    
    # Test with POST request
    payload = {
        'q': 'gaming laptop',
        'page': 1,
        'per_page': 5
    }
    response = client.post(
        '/search',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'query' in data or 'results' in data


def test_chat_endpoint(client):
    """Test the chat endpoint"""
    payload = {'message': 'What are the best laptops?'}
    response = client.post(
        '/chat',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'reply' in data or 'query' in data


def test_admin_rebuild_unauthorized(client):
    """Test admin rebuild endpoint without authentication"""
    response = client.post('/admin/rebuild')
    assert response.status_code == 401


def test_admin_rotate_unauthorized(client):
    """Test admin rotate endpoint without authentication"""
    response = client.post('/admin/rotate')
    assert response.status_code == 401


def test_admin_reset_password_unauthorized(client):
    """Test admin reset password endpoint without authentication"""
    payload = {
        'new_username': 'test',
        'new_password': 'test123'
    }
    response = client.post(
        '/admin/reset_password',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 401


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
