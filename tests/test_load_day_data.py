"""
Integration tests for loadDayData() frontend function.
Tests Requirements 1.1, 1.3 from coach-improvements spec.

This test verifies that the frontend can correctly load and display
daily log data including checked blocks, coaching messages, mode, and notes.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.index import app
import json


def test_load_day_data_integration():
    """
    Integration test: Verify that saved data can be retrieved via GET /api/log
    and contains all necessary fields for the frontend loadDayData() function.
    """
    with app.test_client() as client:
        # Save a complete daily log
        test_log = {
            'date': '2024-02-15',
            'mode': 'evening_gym',
            'checked': {
                'wakeup': True,
                'gym': True,
                'study1': False,
                'study2': True
            },
            'done': 3,
            'total': 4,
            'score': 75,
            'note': 'Good day overall, missed one study session',
            'coach_msg': 'Great job today! You hit 75% completion.'
        }
        
        # Save the log
        save_response = client.post('/api/save',
                                   data=json.dumps(test_log),
                                   content_type='application/json')
        assert save_response.status_code == 200
        
        # Retrieve the log (simulating what loadDayData() does)
        response = client.get('/api/log?date=2024-02-15')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # Verify all fields needed by loadDayData() are present
        assert 'mode' in data, "Mode field is required for loadDayData()"
        assert data['mode'] == 'evening_gym'
        
        assert 'checked' in data, "Checked blocks are required for loadDayData()"
        assert isinstance(data['checked'], dict)
        assert data['checked']['wakeup'] == True
        assert data['checked']['gym'] == True
        assert data['checked']['study1'] == False
        assert data['checked']['study2'] == True
        
        assert 'note' in data, "Note field is required for loadDayData()"
        assert data['note'] == 'Good day overall, missed one study session'
        
        assert 'coach_msg' in data, "Coach message is required for loadDayData()"
        assert data['coach_msg'] == 'Great job today! You hit 75% completion.'
        
        print("✅ All fields required by loadDayData() are present and correct")


def test_load_day_data_empty_date():
    """
    Test that loadDayData() receives an empty object for dates with no data.
    This allows the frontend to reset the UI appropriately.
    """
    with app.test_client() as client:
        # Request a date that has no data
        response = client.get('/api/log?date=1999-12-31')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data == {}, "Empty dates should return empty object"
        
        print("✅ Empty dates return empty object for UI reset")


def test_load_day_data_with_empty_coach_msg():
    """
    Test that logs without coaching messages still load correctly.
    This happens when user saves progress but hasn't clicked "How did I do today?"
    """
    with app.test_client() as client:
        # Save a log without a coaching message
        test_log = {
            'date': '2024-03-01',
            'mode': 'morning_gym',
            'checked': {'wakeup': True},
            'done': 1,
            'total': 5,
            'score': 20,
            'note': 'Just started the day'
        }
        
        save_response = client.post('/api/save',
                                   data=json.dumps(test_log),
                                   content_type='application/json')
        assert save_response.status_code == 200
        
        # Retrieve the log
        response = client.get('/api/log?date=2024-03-01')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # Verify the data loads correctly even without coach_msg
        assert data['mode'] == 'morning_gym'
        assert data['checked']['wakeup'] == True
        assert data['note'] == 'Just started the day'
        
        # coach_msg might be empty string or not present
        # loadDayData() should handle both cases
        if 'coach_msg' in data:
            assert data['coach_msg'] == '' or data['coach_msg'] is None
        
        print("✅ Logs without coaching messages load correctly")


if __name__ == '__main__':
    print("Running loadDayData() integration tests...\n")
    
    try:
        test_load_day_data_integration()
    except AssertionError as e:
        print(f"❌ Test 1 failed: {e}")
    
    try:
        test_load_day_data_empty_date()
    except AssertionError as e:
        print(f"❌ Test 2 failed: {e}")
    
    try:
        test_load_day_data_with_empty_coach_msg()
    except AssertionError as e:
        print(f"❌ Test 3 failed: {e}")
    
    print("\n✅ All loadDayData() integration tests completed!")
