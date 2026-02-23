"""
Unit tests for getCoaching() response handling.
Tests Requirement 1.4 from coach-improvements spec.

This test verifies that the frontend properly handles both success and error
responses from the /api/coach endpoint without displaying "undefined".
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.index import app
import json


def test_coach_endpoint_success_response():
    """
    Test that /api/coach returns proper success response with 'message' field.
    Requirement 1.1, 1.4
    """
    with app.test_client() as client:
        # Prepare valid coaching request
        request_data = {
            'date': '2024-03-15',
            'mode': 'morning_gym',
            'checked': {'wakeup': True, 'gym': True},
            'done': 2,
            'total': 5,
            'score': 40,
            'note': 'Good morning workout'
        }
        
        response = client.post(
            '/api/coach',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Verify response structure
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = json.loads(response.data)
        
        # Critical: response must have 'message' field, not 'error'
        assert 'message' in data, "Success response must contain 'message' field"
        assert isinstance(data['message'], str), "Message must be a string"
        assert len(data['message']) > 0, "Message must not be empty"
        
        # Should NOT have error field on success
        assert 'error' not in data, "Success response should not contain 'error' field"
        
        print("✅ Success response contains 'message' field")


def test_coach_endpoint_error_response():
    """
    Test that /api/coach returns proper error response with 'error' field.
    Requirement 1.4
    """
    with app.test_client() as client:
        # Send invalid request (missing required fields)
        request_data = {
            'date': '2024-03-15',
            # Missing: mode, checked, done, total, score
        }
        
        response = client.post(
            '/api/coach',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Verify error response structure
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
        data = json.loads(response.data)
        
        # Critical: error response must have 'error' field, not 'message'
        assert 'error' in data, "Error response must contain 'error' field"
        assert isinstance(data['error'], str), "Error must be a string"
        assert len(data['error']) > 0, "Error message must not be empty"
        
        # Should NOT have message field on error
        assert 'message' not in data, "Error response should not contain 'message' field"
        
        print("✅ Error response contains 'error' field (not 'message')")


def test_response_field_consistency():
    """
    Test that responses consistently use either 'message' OR 'error', never both.
    This prevents the "undefined" bug in the frontend.
    Requirement 1.4
    """
    with app.test_client() as client:
        # Test 1: Valid request should have 'message' only
        valid_request = {
            'date': '2024-03-15',
            'mode': 'morning_gym',
            'checked': {'wakeup': True},
            'done': 1,
            'total': 5,
            'score': 20,
            'note': ''
        }
        
        response = client.post(
            '/api/coach',
            data=json.dumps(valid_request),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        has_message = 'message' in data
        has_error = 'error' in data
        
        # Must have exactly one of message or error
        assert has_message != has_error, "Response must have either 'message' OR 'error', not both or neither"
        
        if response.status_code == 200:
            assert has_message, "Success response (200) must have 'message'"
            assert not has_error, "Success response (200) must not have 'error'"
        else:
            assert has_error, "Error response must have 'error'"
            assert not has_message, "Error response must not have 'message'"
        
        print("✅ Response fields are consistent (message XOR error)")


if __name__ == '__main__':
    print("Running getCoaching() response handling tests...\n")
    
    try:
        test_coach_endpoint_success_response()
    except AssertionError as e:
        print(f"❌ Test 1 failed: {e}")
    
    try:
        test_coach_endpoint_error_response()
    except AssertionError as e:
        print(f"❌ Test 2 failed: {e}")
    
    try:
        test_response_field_consistency()
    except AssertionError as e:
        print(f"❌ Test 3 failed: {e}")
    
    print("\n✅ All response handling tests completed!")
