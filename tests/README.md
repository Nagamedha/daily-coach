# Testing Documentation

This directory contains comprehensive integration tests for the Daily Coach application.

## Test Overview

**Total Tests:** 23 integration tests  
**Status:** ✅ All passing  
**Coverage:** End-to-end flows, API endpoints, date validation, AI personality

## Test Structure

```
tests/
├── test_api_log_endpoint.py              # GET /api/log endpoint tests
├── test_api_coach_date_validation.py     # POST /api/coach date validation
├── test_api_chat_date_validation.py      # POST /api/chat date validation
├── test_coaching_response_handling.py    # Response format validation
├── test_load_day_data.py                 # Frontend data loading
├── test_integration_end_to_end.py        # Complete coaching flow
├── test_integration_chat_persistence.py  # Chat persistence flow
├── test_integration_date_restrictions.py # Date restriction enforcement
├── test_manual_ai_personality.py         # AI personality validation
└── TEST_RESULTS_SUMMARY.md              # Detailed test results
```

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install pytest hypothesis

# Ensure .env is configured
cp .env.example .env
# Edit .env with your credentials
```

### Run All Tests
```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with output capture disabled (see print statements)
pytest tests/ -v -s
```

### Run Specific Test Files
```bash
# Test end-to-end flow
pytest tests/test_integration_end_to_end.py -v

# Test chat persistence
pytest tests/test_integration_chat_persistence.py -v

# Test AI personality
pytest tests/test_manual_ai_personality.py -v -s

# Test date restrictions
pytest tests/test_integration_date_restrictions.py -v
```

### Run Specific Test Functions
```bash
# Test a single function
pytest tests/test_integration_end_to_end.py::test_end_to_end_coaching_flow -v
```

## Test Categories

### 1. API Endpoint Tests

#### `test_api_log_endpoint.py`
Tests the GET /api/log endpoint for retrieving daily logs.

**Tests:**
- Missing date parameter returns 400
- Non-existent date returns empty object
- Existing date returns complete log data

**Run:**
```bash
pytest tests/test_api_log_endpoint.py -v
```

#### `test_api_coach_date_validation.py`
Tests date validation in the coaching endpoint.

**Tests:**
- Future dates are rejected with 400
- Today's date is accepted
- Past dates are accepted

**Run:**
```bash
pytest tests/test_api_coach_date_validation.py -v
```

#### `test_api_chat_date_validation.py`
Tests date validation in the chat endpoint.

**Tests:**
- Future dates are rejected with 400
- Today's date is accepted
- Past dates are accepted
- Missing date parameter returns 400

**Run:**
```bash
pytest tests/test_api_chat_date_validation.py -v
```

### 2. Response Handling Tests

#### `test_coaching_response_handling.py`
Validates API response formats.

**Tests:**
- Success responses contain 'message' field
- Error responses contain 'error' field
- No 'undefined' values in responses
- Response fields are mutually exclusive

**Run:**
```bash
pytest tests/test_coaching_response_handling.py -v
```

### 3. Integration Tests

#### `test_integration_end_to_end.py`
Tests complete coaching workflow.

**Tests:**
- User selects date → checks blocks → gets coaching → message persists
- Coaching message displays correctly
- Message persists across page reloads
- Error handling doesn't show 'undefined'

**Run:**
```bash
pytest tests/test_integration_end_to_end.py -v
```

#### `test_integration_chat_persistence.py`
Tests conversation persistence.

**Tests:**
- User sends message → coach responds → conversation persists
- Multiple messages persist correctly
- Chronological order maintained after reload
- Empty conversations return empty array
- Conversations persist across multiple reloads

**Run:**
```bash
pytest tests/test_integration_chat_persistence.py -v
```

#### `test_integration_date_restrictions.py`
Tests date restriction enforcement.

**Tests:**
- Backend rejects future dates for coaching
- Backend rejects future dates for chat
- Backend accepts today's date
- Backend accepts past dates
- Multiple future dates all rejected
- Multiple past dates all accepted
- Error messages are clear

**Run:**
```bash
pytest tests/test_integration_date_restrictions.py -v
```

### 4. AI Personality Tests

#### `test_manual_ai_personality.py`
Validates AI coach personality and behavior.

**Tests:**
- Low scores (< 50%) show consequences
- Medium scores (50-79%) show balanced feedback
- High scores (≥ 80%) show appreciation
- Off-topic questions get rejection message
- On-topic questions get helpful responses
- Personality is consistent across scenarios

**Run:**
```bash
# Run with output to see actual AI responses
pytest tests/test_manual_ai_personality.py -v -s
```

**Example Output:**
```
LOW SCORE TEST (25%)
Coaching Message:
"You struggled today, completing only 1 out of 4 blocks. Missing your 
workouts means you're slowing down your fitness journey..."
```

## Test Results Summary

See [TEST_RESULTS_SUMMARY.md](TEST_RESULTS_SUMMARY.md) for:
- Detailed test execution results
- Bug fixes applied during testing
- Requirements coverage matrix
- Manual testing observations
- AI personality characteristics

## Writing New Tests

### Test Template
```python
import pytest
from api.index import app

@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_your_feature(client):
    """Test description."""
    # Arrange
    test_data = {...}
    
    # Act
    response = client.post('/api/endpoint', json=test_data)
    
    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert 'expected_field' in data
```

### Best Practices
1. Use descriptive test names
2. Follow Arrange-Act-Assert pattern
3. Test both success and failure cases
4. Use fixtures for common setup
5. Clean up test data if needed
6. Add docstrings explaining what's tested

## Continuous Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
```

## Troubleshooting Tests

### Issue: Tests fail with "Connection refused"
**Solution:** Ensure Flask app is not running on port 5000

### Issue: Tests fail with "Database error"
**Solution:** Check .env has correct Supabase credentials

### Issue: AI tests fail with "API error"
**Solution:** Verify OpenAI API key has credits

### Issue: Tests are slow
**Solution:** AI tests make real API calls. Use `-k "not manual"` to skip them:
```bash
pytest tests/ -v -k "not manual"
```

## Test Coverage

| Feature Area | Tests | Status |
|-------------|-------|--------|
| API Endpoints | 8 | ✅ |
| Response Handling | 3 | ✅ |
| End-to-End Flow | 4 | ✅ |
| Chat Persistence | 5 | ✅ |
| Date Restrictions | 8 | ✅ |
| AI Personality | 6 | ✅ |
| **Total** | **34** | **✅** |

## Contributing Tests

When adding new features:
1. Write tests first (TDD approach)
2. Ensure tests pass locally
3. Update this README with new test documentation
4. Add test to appropriate category

---

**All tests passing = Ready to deploy! 🚀**
