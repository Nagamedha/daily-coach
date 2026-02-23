"""
Integration tests for end-to-end flow (Task 10.1)
Tests: User selects date → checks blocks → gets coaching → message persists
Requirements: 1.1, 1.2, 1.3
"""
import pytest
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.index import app
from services.config_service import ConfigService
from services.database_service import DatabaseService


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def db_service():
    """Create database service for cleanup."""
    config = ConfigService()
    return DatabaseService(config)


@pytest.fixture
def test_date():
    """Use yesterday's date for testing."""
    return (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')


def test_end_to_end_coaching_flow(client, db_service, test_date):
    """
    Test complete end-to-end flow:
    1. User selects a date
    2. User checks some blocks
    3. User requests coaching
    4. Coaching message is generated and saved
    5. User reloads the date
    6. Coaching message persists
    
    Requirements: 1.1, 1.2, 1.3
    """
    # Step 1 & 2: User checks blocks and requests coaching
    coaching_data = {
        'date': test_date,
        'mode': 'morning_gym',
        'checked': {
            'mg_1': True,
            'mg_2': True,
            'mg_3': False,
            'mg_4': True
        },
        'done': 3,
        'total': 4,
        'score': 75,
        'note': 'Felt good today'
    }
    
    # Step 3: Request coaching feedback
    response = client.post('/api/coach', 
                          json=coaching_data,
                          content_type='application/json')
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.get_json()
    assert 'message' in data, "Response should contain 'message' field"
    assert data['message'], "Coaching message should not be empty"
    
    coaching_message = data['message']
    print(f"Generated coaching message: {coaching_message[:100]}...")
    
    # Step 4: Verify message was saved to database
    log_response = client.get(f'/api/log?date={test_date}')
    assert log_response.status_code == 200
    
    log_data = log_response.get_json()
    assert log_data, "Log data should exist"
    assert 'coach_msg' in log_data, "Log should contain coach_msg field"
    assert log_data['coach_msg'] == coaching_message, "Saved message should match generated message"
    
    # Step 5 & 6: Simulate reload - fetch the date again
    reload_response = client.get(f'/api/log?date={test_date}')
    assert reload_response.status_code == 200
    
    reload_data = reload_response.get_json()
    assert reload_data['coach_msg'] == coaching_message, "Message should persist after reload"
    assert reload_data['score'] == 75, "Score should persist"
    assert reload_data['mode'] == 'morning_gym', "Mode should persist"
    
    print("✓ End-to-end coaching flow test passed")


def test_coaching_message_displays_correctly(client, test_date):
    """
    Test that coaching message displays correctly in the response.
    Requirements: 1.1
    """
    coaching_data = {
        'date': test_date,
        'mode': 'no_gym',
        'checked': {'ng_1': True, 'ng_2': True},
        'done': 2,
        'total': 2,
        'score': 100,
        'note': 'Perfect day!'
    }
    
    response = client.post('/api/coach',
                          json=coaching_data,
                          content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Verify message is not undefined or empty
    assert 'message' in data
    assert data['message'] is not None
    assert data['message'] != 'undefined'
    assert len(data['message']) > 0
    
    print("✓ Coaching message displays correctly")


def test_coaching_message_persists_on_reload(client, test_date):
    """
    Test that coaching message persists when page is reloaded.
    Requirements: 1.3
    """
    # First, create a coaching message
    coaching_data = {
        'date': test_date,
        'mode': 'evening_gym',
        'checked': {'eg_1': True, 'eg_2': False},
        'done': 1,
        'total': 2,
        'score': 50,
        'note': 'Struggled today'
    }
    
    coach_response = client.post('/api/coach',
                                json=coaching_data,
                                content_type='application/json')
    
    assert coach_response.status_code == 200
    original_message = coach_response.get_json()['message']
    
    # Simulate multiple reloads
    for i in range(3):
        reload_response = client.get(f'/api/log?date={test_date}')
        assert reload_response.status_code == 200
        
        reload_data = reload_response.get_json()
        assert reload_data['coach_msg'] == original_message, \
            f"Message should persist on reload #{i+1}"
    
    print("✓ Coaching message persists on multiple reloads")


def test_error_handling_no_undefined(client, test_date):
    """
    Test that errors don't result in 'undefined' being displayed.
    Requirements: 1.4
    """
    # Test with missing required field
    invalid_data = {
        'date': test_date,
        'mode': 'morning_gym',
        # Missing 'checked', 'done', 'total', 'score'
    }
    
    response = client.post('/api/coach',
                          json=invalid_data,
                          content_type='application/json')
    
    # Should return error, not undefined
    data = response.get_json()
    
    # Verify we get a proper error message, not undefined
    if 'error' in data:
        assert data['error'] != 'undefined'
        assert isinstance(data['error'], str)
        assert len(data['error']) > 0
    elif 'message' in data:
        assert data['message'] != 'undefined'
    
    print("✓ Error handling doesn't show 'undefined'")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
