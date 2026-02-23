"""
Integration tests for date restrictions (Task 10.3)
Tests: Future dates cannot be selected, past dates work, backend rejects future dates
Requirements: 3.1, 3.2, 3.3, 3.4
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
def today():
    """Get today's date."""
    return datetime.now().strftime('%Y-%m-%d')


@pytest.fixture
def yesterday():
    """Get yesterday's date."""
    return (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')


@pytest.fixture
def tomorrow():
    """Get tomorrow's date."""
    return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')


@pytest.fixture
def next_week():
    """Get date one week in the future."""
    return (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')


def test_backend_rejects_future_date_coaching(client, tomorrow):
    """
    Test that backend rejects coaching requests for future dates.
    Requirements: 3.2
    """
    future_coaching_data = {
        'date': tomorrow,
        'mode': 'morning_gym',
        'checked': {'mg_1': True},
        'done': 1,
        'total': 4,
        'score': 25,
        'note': 'Future date test'
    }
    
    response = client.post('/api/coach',
                          json=future_coaching_data,
                          content_type='application/json')
    
    # Should return 400 error
    assert response.status_code == 400, \
        f"Expected 400 for future date, got {response.status_code}"
    
    data = response.get_json()
    assert 'error' in data, "Response should contain error message"
    assert 'future' in data['error'].lower(), \
        "Error message should mention future dates"
    
    print("✓ Backend rejects future date for coaching")


def test_backend_rejects_future_date_chat(client, next_week):
    """
    Test that backend rejects chat requests for future dates.
    Requirements: 3.2
    """
    future_chat_data = {
        'message': 'How will I do next week?',
        'date': next_week
    }
    
    response = client.post('/api/chat',
                          json=future_chat_data,
                          content_type='application/json')
    
    # Should return 400 error
    assert response.status_code == 400, \
        f"Expected 400 for future date, got {response.status_code}"
    
    data = response.get_json()
    assert 'error' in data, "Response should contain error message"
    assert 'future' in data['error'].lower(), \
        "Error message should mention future dates"
    
    print("✓ Backend rejects future date for chat")


def test_backend_accepts_today_date(client, today):
    """
    Test that backend accepts today's date.
    Requirements: 3.1, 3.3
    """
    today_coaching_data = {
        'date': today,
        'mode': 'morning_gym',
        'checked': {'mg_1': True, 'mg_2': True},
        'done': 2,
        'total': 4,
        'score': 50,
        'note': 'Today test'
    }
    
    response = client.post('/api/coach',
                          json=today_coaching_data,
                          content_type='application/json')
    
    # Should succeed
    assert response.status_code == 200, \
        f"Expected 200 for today's date, got {response.status_code}"
    
    data = response.get_json()
    assert 'message' in data, "Response should contain coaching message"
    assert data['message'], "Coaching message should not be empty"
    
    print("✓ Backend accepts today's date")


def test_backend_accepts_past_dates(client, yesterday):
    """
    Test that backend accepts past dates.
    Requirements: 3.3
    """
    past_coaching_data = {
        'date': yesterday,
        'mode': 'evening_gym',
        'checked': {'eg_1': True, 'eg_2': True, 'eg_3': True},
        'done': 3,
        'total': 4,
        'score': 75,
        'note': 'Past date test'
    }
    
    response = client.post('/api/coach',
                          json=past_coaching_data,
                          content_type='application/json')
    
    # Should succeed
    assert response.status_code == 200, \
        f"Expected 200 for past date, got {response.status_code}"
    
    data = response.get_json()
    assert 'message' in data, "Response should contain coaching message"
    
    print("✓ Backend accepts past dates")


def test_backend_accepts_past_date_chat(client, yesterday):
    """
    Test that backend accepts chat for past dates.
    Requirements: 3.3
    """
    past_chat_data = {
        'message': 'How did I do yesterday?',
        'date': yesterday
    }
    
    response = client.post('/api/chat',
                          json=past_chat_data,
                          content_type='application/json')
    
    # Should succeed
    assert response.status_code == 200, \
        f"Expected 200 for past date chat, got {response.status_code}"
    
    data = response.get_json()
    assert 'response' in data, "Response should contain coach response"
    
    print("✓ Backend accepts past date for chat")


def test_multiple_future_dates_rejected(client):
    """
    Test that various future dates are all rejected.
    Requirements: 3.2
    """
    future_dates = [
        (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
        (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
        (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
    ]
    
    for future_date in future_dates:
        coaching_data = {
            'date': future_date,
            'mode': 'no_gym',
            'checked': {},
            'done': 0,
            'total': 2,
            'score': 0,
            'note': f'Test for {future_date}'
        }
        
        response = client.post('/api/coach',
                              json=coaching_data,
                              content_type='application/json')
        
        assert response.status_code == 400, \
            f"Date {future_date} should be rejected with 400"
        
        data = response.get_json()
        assert 'error' in data, f"Date {future_date} should return error"
    
    print("✓ Multiple future dates all rejected")


def test_multiple_past_dates_accepted(client):
    """
    Test that various past dates are all accepted.
    Requirements: 3.3
    """
    past_dates = [
        (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
        (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
        (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
    ]
    
    for past_date in past_dates:
        coaching_data = {
            'date': past_date,
            'mode': 'morning_gym',
            'checked': {'mg_1': True},
            'done': 1,
            'total': 4,
            'score': 25,
            'note': f'Test for {past_date}'
        }
        
        response = client.post('/api/coach',
                              json=coaching_data,
                              content_type='application/json')
        
        assert response.status_code == 200, \
            f"Date {past_date} should be accepted with 200, got {response.status_code}"
        
        data = response.get_json()
        assert 'message' in data, f"Date {past_date} should return coaching message"
    
    print("✓ Multiple past dates all accepted")


def test_date_validation_error_message_clarity(client, tomorrow):
    """
    Test that date validation error messages are clear and helpful.
    Requirements: 3.2
    """
    future_data = {
        'date': tomorrow,
        'mode': 'morning_gym',
        'checked': {},
        'done': 0,
        'total': 4,
        'score': 0,
        'note': ''
    }
    
    response = client.post('/api/coach',
                          json=future_data,
                          content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    
    error_message = data['error']
    
    # Error message should be clear and mention future dates
    assert 'future' in error_message.lower(), \
        "Error should mention 'future'"
    assert 'cannot' in error_message.lower() or 'not' in error_message.lower(), \
        "Error should indicate action is not allowed"
    
    print(f"✓ Clear error message: '{error_message}'")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
