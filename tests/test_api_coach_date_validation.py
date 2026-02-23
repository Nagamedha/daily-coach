"""
Unit tests for date validation in POST /api/coach endpoint.
Tests Requirement 3.2 from coach-improvements spec.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.index import app
import json
from datetime import datetime, timedelta


def test_coach_future_date_returns_400():
    """Test that future date returns 400 error."""
    with app.test_client() as client:
        # Create a date in the future
        future_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        test_data = {
            'date': future_date,
            'mode': 'morning_gym',
            'checked': {'1': True, '2': False},
            'done': 1,
            'total': 2,
            'score': 50,
            'note': 'Test note'
        }
        
        response = client.post('/api/coach',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Cannot create logs for future dates' in data['error']


def test_coach_today_date_is_accepted():
    """Test that today's date is accepted."""
    with app.test_client() as client:
        # Use today's date
        today = datetime.now().strftime('%Y-%m-%d')
        
        test_data = {
            'date': today,
            'mode': 'morning_gym',
            'checked': {'1': True, '2': False},
            'done': 1,
            'total': 2,
            'score': 50,
            'note': 'Test note'
        }
        
        response = client.post('/api/coach',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        # Should not return 400 for date validation
        # (may return other errors like AI service issues, but not date validation error)
        if response.status_code == 400:
            data = json.loads(response.data)
            assert 'Cannot create logs for future dates' not in data.get('error', '')


def test_coach_past_date_is_accepted():
    """Test that past date is accepted."""
    with app.test_client() as client:
        # Use a date 7 days ago
        past_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        test_data = {
            'date': past_date,
            'mode': 'morning_gym',
            'checked': {'1': True, '2': False},
            'done': 1,
            'total': 2,
            'score': 50,
            'note': 'Test note'
        }
        
        response = client.post('/api/coach',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        # Should not return 400 for date validation
        # (may return other errors like AI service issues, but not date validation error)
        if response.status_code == 400:
            data = json.loads(response.data)
            assert 'Cannot create logs for future dates' not in data.get('error', '')


if __name__ == '__main__':
    print("Running POST /api/coach date validation tests...")
    
    try:
        test_coach_future_date_returns_400()
        print("✅ Test 1: Future date returns 400")
    except AssertionError as e:
        print(f"❌ Test 1 failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        test_coach_today_date_is_accepted()
        print("✅ Test 2: Today's date is accepted")
    except AssertionError as e:
        print(f"❌ Test 2 failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        test_coach_past_date_is_accepted()
        print("✅ Test 3: Past date is accepted")
    except AssertionError as e:
        print(f"❌ Test 3 failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nAll tests completed!")
