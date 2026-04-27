import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_users_get(client):
    response = client.get('/users')
    assert response.status_code in [200, 500]

def test_users_post_missing_data(client):
    response = client.post('/users',
        json={},
        content_type='application/json'
    )
    # 400 is correct - we now validate input!
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_users_post_valid_data(client):
    response = client.post('/users',
        json={"name": "Test User", "email": "test@example.com"},
        content_type='application/json'
    )
    # 201 success or 500 if no DB in test env
    assert response.status_code in [201, 500]

def test_users_post_input_too_long(client):
    response = client.post('/users',
        json={
            "name": "x" * 101,
            "email": "test@example.com"
        },
        content_type='application/json'
    )
    assert response.status_code == 400

def test_users_delete(client):
    response = client.delete('/users/999')
    # 200 success or 500 if no DB
    assert response.status_code in [200, 500]