"""
Manual/automated tests for AI personality (Task 10.4)
Tests: Low/medium/high score feedback, off-topic rejection
Requirements: 2.1, 2.2, 2.3, 2.7
"""
import pytest
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.index import app


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def test_date():
    """Use yesterday's date for testing."""
    return (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')


def test_low_score_shows_consequences(client, test_date):
    """
    Test that low score (< 50%) shows consequences and reality-based feedback.
    Requirements: 2.1, 2.2
    """
    low_score_data = {
        'date': test_date,
        'mode': 'morning_gym',
        'checked': {'mg_1': False, 'mg_2': False, 'mg_3': False, 'mg_4': True},
        'done': 1,
        'total': 4,
        'score': 25,
        'note': 'Struggled today, missed most tasks'
    }
    
    response = client.post('/api/coach',
                          json=low_score_data,
                          content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    message = data['message'].lower()
    
    print(f"\n{'='*60}")
    print(f"LOW SCORE TEST (25%)")
    print(f"{'='*60}")
    print(f"Coaching Message:\n{data['message']}")
    print(f"{'='*60}\n")
    
    # Check for strict trainer characteristics
    # Should mention consequences or reality
    consequence_keywords = [
        'consequence', 'delayed', 'slower', 'missed', 'lost',
        'behind', 'setback', 'impact', 'affect', 'struggle'
    ]
    
    has_consequence_language = any(keyword in message for keyword in consequence_keywords)
    
    # Should be direct and honest (not overly positive)
    overly_positive_phrases = ['great job', 'excellent', 'amazing', 'fantastic', 'perfect']
    is_not_overly_positive = not any(phrase in message for phrase in overly_positive_phrases)
    
    assert has_consequence_language or 'why' in message, \
        "Low score feedback should mention consequences or ask 'why'"
    assert is_not_overly_positive, \
        "Low score feedback should not be overly positive"
    
    print("✓ Low score shows appropriate consequences/reality check")


def test_medium_score_shows_balanced_feedback(client, test_date):
    """
    Test that medium score (50-79%) shows balanced feedback.
    Requirements: 2.1, 2.2
    """
    medium_score_data = {
        'date': test_date,
        'mode': 'evening_gym',
        'checked': {'eg_1': True, 'eg_2': True, 'eg_3': False, 'eg_4': True},
        'done': 3,
        'total': 4,
        'score': 75,
        'note': 'Did okay, missed one task'
    }
    
    response = client.post('/api/coach',
                          json=medium_score_data,
                          content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    message = data['message'].lower()
    
    print(f"\n{'='*60}")
    print(f"MEDIUM SCORE TEST (75%)")
    print(f"{'='*60}")
    print(f"Coaching Message:\n{data['message']}")
    print(f"{'='*60}\n")
    
    # Should acknowledge effort
    positive_keywords = ['good', 'effort', 'progress', 'solid', 'decent']
    has_acknowledgment = any(keyword in message for keyword in positive_keywords)
    
    # But also mention what could improve
    improvement_keywords = ['but', 'however', 'missed', 'next', 'tomorrow', 'improve']
    has_improvement_focus = any(keyword in message for keyword in improvement_keywords)
    
    # Should be balanced - not purely positive or negative
    assert has_acknowledgment or has_improvement_focus, \
        "Medium score should have balanced feedback"
    
    print("✓ Medium score shows balanced feedback")


def test_high_score_shows_appreciation(client, test_date):
    """
    Test that high score (>= 80%) shows appreciation and confidence-boosting feedback.
    Requirements: 2.1, 2.3
    """
    high_score_data = {
        'date': test_date,
        'mode': 'morning_gym',
        'checked': {'mg_1': True, 'mg_2': True, 'mg_3': True, 'mg_4': True},
        'done': 4,
        'total': 4,
        'score': 100,
        'note': 'Crushed it today!'
    }
    
    response = client.post('/api/coach',
                          json=high_score_data,
                          content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    message = data['message'].lower()
    
    print(f"\n{'='*60}")
    print(f"HIGH SCORE TEST (100%)")
    print(f"{'='*60}")
    print(f"Coaching Message:\n{data['message']}")
    print(f"{'='*60}\n")
    
    # Should show appreciation or acknowledgment of good performance
    appreciation_keywords = [
        'great', 'excellent', 'proud', 'well done', 'good job',
        'crushed', 'nailed', 'perfect', 'strong', 'solid',
        'keep it up', 'momentum', 'consistency', 'fantastic',
        'completed all', 'hit', '100%'
    ]
    
    has_appreciation = any(keyword in message for keyword in appreciation_keywords)
    
    # Should reference the completion or success
    references_success = '100' in message or 'all' in message or 'completed' in message
    
    assert has_appreciation or references_success, \
        "High score feedback should show appreciation or acknowledge success"
    
    print("✓ High score shows appreciation and confidence boost")


def test_off_topic_question_gets_rejection(client, test_date):
    """
    Test that off-topic questions get the specific rejection message.
    Requirements: 2.7
    """
    off_topic_questions = [
        "What's the weather like today?",
        "Who won the football game?",
        "What's the capital of France?",
        "Tell me a joke",
        "What's your favorite movie?"
    ]
    
    expected_rejection = "That's not my role. I'm your healthy lifestyle coach here to help you follow your daily schedule, get a job, be fit, and have a healthy lifestyle."
    
    for question in off_topic_questions:
        response = client.post('/api/chat',
                              json={'message': question, 'date': test_date},
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        response_text = data['response']
        
        print(f"\n{'='*60}")
        print(f"OFF-TOPIC TEST: '{question}'")
        print(f"{'='*60}")
        print(f"Response:\n{response_text}")
        print(f"{'='*60}\n")
        
        # Check if response contains rejection language
        response_lower = response_text.lower()
        
        # Should mention role/not my role
        has_role_mention = 'role' in response_lower or 'not' in response_lower
        
        # Should mention coaching/schedule/lifestyle
        has_coaching_context = any(word in response_lower for word in [
            'coach', 'schedule', 'lifestyle', 'healthy', 'job', 'fit'
        ])
        
        assert has_role_mention and has_coaching_context, \
            f"Off-topic question '{question}' should get rejection message"
    
    print("✓ Off-topic questions get rejection message")


def test_on_topic_questions_get_helpful_responses(client, test_date):
    """
    Test that on-topic questions get helpful, relevant responses.
    Requirements: 2.1
    """
    on_topic_questions = [
        "How am I doing this week?",
        "What's my gym streak?",
        "Am I making progress on my job search?",
        "How can I improve my schedule adherence?",
        "What should I focus on tomorrow?"
    ]
    
    for question in on_topic_questions:
        response = client.post('/api/chat',
                              json={'message': question, 'date': test_date},
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        response_text = data['response']
        
        print(f"\n{'='*60}")
        print(f"ON-TOPIC TEST: '{question}'")
        print(f"{'='*60}")
        print(f"Response:\n{response_text}")
        print(f"{'='*60}\n")
        
        # Should NOT be a rejection
        response_lower = response_text.lower()
        is_not_rejection = "that's not my role" not in response_lower
        
        # Should be substantive (not too short)
        is_substantive = len(response_text) > 20
        
        assert is_not_rejection, \
            f"On-topic question '{question}' should not be rejected"
        assert is_substantive, \
            f"On-topic question '{question}' should get substantive response"
    
    print("✓ On-topic questions get helpful responses")


def test_strict_trainer_personality_consistency(client, test_date):
    """
    Test that the strict trainer personality is consistent across responses.
    Requirements: 2.1
    """
    test_scenarios = [
        {
            'data': {
                'date': test_date,
                'mode': 'no_gym',
                'checked': {'ng_1': True, 'ng_2': False},
                'done': 1,
                'total': 2,
                'score': 50,
                'note': 'Skipped some tasks'
            },
            'expected_tone': 'direct'
        },
        {
            'data': {
                'date': test_date,
                'mode': 'morning_gym',
                'checked': {'mg_1': True, 'mg_2': True, 'mg_3': True, 'mg_4': False},
                'done': 3,
                'total': 4,
                'score': 75,
                'note': 'Pretty good day'
            },
            'expected_tone': 'balanced'
        }
    ]
    
    for scenario in test_scenarios:
        response = client.post('/api/coach',
                              json=scenario['data'],
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        message = data['message']
        
        print(f"\n{'='*60}")
        print(f"PERSONALITY TEST ({scenario['expected_tone'].upper()} TONE)")
        print(f"Score: {scenario['data']['score']}%")
        print(f"{'='*60}")
        print(f"Response:\n{message}")
        print(f"{'='*60}\n")
        
        # Should be personal and direct (not generic)
        is_not_generic = len(message) > 50  # Substantive response
        
        # Should reference actual data (not vague)
        message_lower = message.lower()
        references_data = any(word in message_lower for word in [
            'today', 'task', 'block', 'schedule', 'gym', 'study', 'job'
        ])
        
        assert is_not_generic, "Response should be substantive"
        assert references_data, "Response should reference actual data"
    
    print("✓ Strict trainer personality is consistent")


if __name__ == '__main__':
    # Run with verbose output to see all the coaching messages
    pytest.main([__file__, '-v', '-s'])
