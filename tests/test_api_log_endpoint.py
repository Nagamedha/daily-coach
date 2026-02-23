"""
Unit tests for GET /api/log endpoint.
Tests Requirements 1.1, 1.3 from coach-improvements spec.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.index import app
import json


def test_get_log_missing_date_parameter():
    """Test that missing date parameter returns 400 error."""
    with app.test_client() as client:
        response = client.get('/api/log')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Missing date parameter' in data['error']


def test_get_log_nonexistent_date_returns_empty():
    """Test that non-existent date returns empty object."""
    with app.test_client() as client:
        # Use a date that's unlikely to exist
        response = client.get('/api/log?date=1900-01-01')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == {}


def test_get_log_existing_date_returns_data():
    """Test that existing date returns log data."""
    with app.test_client() as client:
        # First, save a log entry
        test_log = {
            'date': '2024-01-15',
            'mode': 'morning_gym',
            'checked': {'1': True, '2': False},
            'done': 1,
            'total': 2,
            'score': 50,
            'note': 'Test note',
            'coach_msg': 'Test coaching message'
        }
        
        save_response = client.post('/api/save', 
                                   data=json.dumps(test_log),
                                   content_type='application/json')
        
        if save_response.status_code != 200:
            print(f"Save failed with status {save_response.status_code}")
            print(f"Response: {save_response.data}")
            return
        
        # Now retrieve it
        response = client.get('/api/log?date=2024-01-15')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify the data
        assert data['date'] == '2024-01-15'
        assert data['mode'] == 'morning_gym'
        assert data['done'] == 1
        assert data['total'] == 2
        assert data['score'] == 50
        assert data['note'] == 'Test note'
        assert data['coach_msg'] == 'Test coaching message'
        assert 'checked' in data


if __name__ == '__main__':
    print("Running GET /api/log endpoint tests...")
    
    try:
        test_get_log_missing_date_parameter()
        print("✅ Test 1: Missing date parameter returns 400")
    except AssertionError as e:
        print(f"❌ Test 1 failed: {e}")
    
    try:
        test_get_log_nonexistent_date_returns_empty()
        print("✅ Test 2: Non-existent date returns empty object")
    except AssertionError as e:
        print(f"❌ Test 2 failed: {e}")
    
    try:
        test_get_log_existing_date_returns_data()
        print("✅ Test 3: Existing date returns log data")
    except AssertionError as e:
        print(f"❌ Test 3 failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nAll tests completed!")
