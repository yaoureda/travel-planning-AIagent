import pytest
import json
from app.tools.extractor import extract_travel

# Test cases
tests = [
    {
        "message": "Trip from Paris to Rome 2026-04-01 to 2026-04-05 for 2 adults",
        "expected": {"origin": "Paris", "destination": "Rome", "rooms": 2, "rooms_specified": False}
    },
    {
        "message": "Travel from Berlin to Madrid from 10 june 2026 to 15 june 2026 for 1 adult and 1 child",
        "expected": {"departure_date": "2026-06-10", "return_date": "2026-06-15", "children": 1, "rooms": 1, "rooms_specified": False}
    },
    {
        "message": "Trip from Paris to Rome 2026-04-01 to 2026-04-05 for 3 adults and 5 room",
        "expected": {"adults": 3, "rooms": 5, "rooms_specified": True}
    }
]

@pytest.mark.parametrize("test_case", tests)
def test_extract_travel(test_case):
    """Test the extract_travel tool with multiple messages."""
    result_json = extract_travel.invoke({"message": test_case["message"]})
    
    try:
        result = json.loads(result_json)
    except Exception as e:
        pytest.fail(f"Failed to parse JSON: {e}")

    for key, value in test_case["expected"].items():
        assert result.get(key) == value, f"For message '{test_case['message']}', expected {key}={value} but got {result.get(key)}"