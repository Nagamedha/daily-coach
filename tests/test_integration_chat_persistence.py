"""
Integration tests for chat persistence flow (Task 10.2)
Tests: User sends message → coach responds → reload page → verify history
Requirements: 4.1, 4.2, 4.3
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


def test_chat_persistence_flow(client, test_date):
    """
    Test complete chat persistence flow:
    1. User sends a message
    2. Coach responds
    3. Message and response are saved
    4. User reloads page (simulated by fetching conversation)
    5. History is displayed correctly
    
    Requirements: 4.1, 4.2, 4.3
    """
    # Step 1 & 2: User sends message and gets response
    user_message = "How am I doing this week?"
    
    chat_response = client.post('/api/chat',
                               json={'message': user_message, 'date': test_date},
                               content_type='application/json')
    
    assert chat_response.status_code == 200, f"Expected 200, got {chat_response.status_code}"
    
    chat_data = chat_response.get_json()
    assert 'response' in chat_data, "Response should contain 'response' field"
    assert chat_data['response'], "Coach response should not be empty"
    
    coach_response = chat_data['response']
    print(f"Coach response: {coach_response[:100]}...")
    
    # Step 3 & 4: Verify messages were saved - simulate reload
    conversation_response = client.get(f'/api/conversation?date={test_date}')
    assert conversation_response.status_code == 200
    
    conversation_data = conversation_response.get_json()
    assert 'messages' in conversation_data, "Response should contain 'messages' field"
    
    messages = conversation_data['messages']
    assert len(messages) >= 2, "Should have at least user message and coach response"
    
    # Step 5: Verify history displays correctly
    # Find the user message and coach response
    user_msg_found = False
    coach_msg_found = False
    
    for msg in messages:
        if msg['sender'] == 'user' and msg['text'] == user_message:
            user_msg_found = True
        if msg['sender'] == 'coach' and msg['text'] == coach_response:
            coach_msg_found = True
    
    assert user_msg_found, "User message should be in conversation history"
    assert coach_msg_found, "Coach response should be in conversation history"
    
    print("✓ Chat persistence flow test passed")


def test_multiple_messages_persist(client, test_date):
    """
    Test that multiple messages in a conversation all persist.
    Requirements: 4.1, 4.2, 4.3
    """
    messages_to_send = [
        "What's my gym streak?",
        "How many study days do I have?",
        "Am I making progress?"
    ]
    
    # Send multiple messages
    for msg in messages_to_send:
        response = client.post('/api/chat',
                              json={'message': msg, 'date': test_date},
                              content_type='application/json')
        assert response.status_code == 200
    
    # Verify all messages persisted
    conversation_response = client.get(f'/api/conversation?date={test_date}')
    assert conversation_response.status_code == 200
    
    conversation_data = conversation_response.get_json()
    messages = conversation_data['messages']
    
    # Should have at least 6 messages (3 user + 3 coach)
    assert len(messages) >= 6, f"Expected at least 6 messages, got {len(messages)}"
    
    # Verify all user messages are present
    user_messages = [m['text'] for m in messages if m['sender'] == 'user']
    for sent_msg in messages_to_send:
        assert sent_msg in user_messages, f"Message '{sent_msg}' should be in history"
    
    print("✓ Multiple messages persist correctly")


def test_conversation_reload_maintains_order(client, test_date):
    """
    Test that conversation maintains chronological order after reload.
    Requirements: 4.2
    """
    # Send messages with identifiable content
    message_sequence = [
        "First message",
        "Second message",
        "Third message"
    ]
    
    for msg in message_sequence:
        response = client.post('/api/chat',
                              json={'message': msg, 'date': test_date},
                              content_type='application/json')
        assert response.status_code == 200
    
    # Fetch conversation
    conversation_response = client.get(f'/api/conversation?date={test_date}')
    conversation_data = conversation_response.get_json()
    messages = conversation_data['messages']
    
    # Extract user messages in order
    user_messages = [m['text'] for m in messages if m['sender'] == 'user']
    
    # Verify order is maintained
    for i, expected_msg in enumerate(message_sequence):
        assert expected_msg in user_messages, f"Message '{expected_msg}' should be present"
        # Find index of this message
        actual_index = user_messages.index(expected_msg)
        # All previous messages should appear before this one
        for j in range(i):
            prev_msg = message_sequence[j]
            prev_index = user_messages.index(prev_msg)
            assert prev_index < actual_index, \
                f"Message '{prev_msg}' should appear before '{expected_msg}'"
    
    print("✓ Conversation order maintained after reload")


def test_empty_conversation_returns_empty_array(client):
    """
    Test that fetching conversation for a date with no messages returns empty array.
    Requirements: 4.2
    """
    # Use a date far in the past that definitely has no messages
    empty_date = '2020-01-01'
    
    response = client.get(f'/api/conversation?date={empty_date}')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'messages' in data
    assert isinstance(data['messages'], list)
    assert len(data['messages']) == 0, "Should return empty array for date with no messages"
    
    print("✓ Empty conversation returns empty array")


def test_conversation_persists_across_multiple_reloads(client, test_date):
    """
    Test that conversation persists across multiple page reloads.
    Requirements: 4.3
    """
    # Send a message
    test_message = "Test persistence message"
    
    chat_response = client.post('/api/chat',
                               json={'message': test_message, 'date': test_date},
                               content_type='application/json')
    assert chat_response.status_code == 200
    
    original_response = chat_response.get_json()['response']
    
    # Simulate multiple reloads by fetching conversation multiple times
    for i in range(5):
        conversation_response = client.get(f'/api/conversation?date={test_date}')
        assert conversation_response.status_code == 200
        
        conversation_data = conversation_response.get_json()
        messages = conversation_data['messages']
        
        # Verify our message is still there
        user_messages = [m['text'] for m in messages if m['sender'] == 'user']
        assert test_message in user_messages, \
            f"Message should persist on reload #{i+1}"
        
        # Verify coach response is still there
        coach_messages = [m['text'] for m in messages if m['sender'] == 'coach']
        assert original_response in coach_messages, \
            f"Coach response should persist on reload #{i+1}"
    
    print("✓ Conversation persists across multiple reloads")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
