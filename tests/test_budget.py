import pytest
from app.tools.budget import estimate_trip_cost

# Test cases
tests = [
    (
        "Test 1",
        {
            "departure_flight_price": 300,
            "return_flight_price": 200,
            "hotel_price_per_night": 150,
            "nights": 4,
            "adults": 2,
            "children": 1,
            "infants": 0,
            "budget": 3000
        },
        """Estimated trip cost:
Departure flight: $300.0 x 3 travelers = $900.0
Return flight: $200.0 x 3 travelers = $600.0
Hotel: $150.0 x 4 nights x 2 room(s) = $1200.0
Total cost: $2700.0
Budget: $3000.0
Status: The trip is within budget."""
    ),
    (
        "Test 2",
        {
            "departure_flight_price": 500,
            "return_flight_price": 400,
            "hotel_price_per_night": 200,
            "nights": 5,
            "adults": 3,
            "children": 2,
            "infants": 1,
            "budget": 8000,
            "rooms": 4
        },
        """Estimated trip cost:
Departure flight: $500.0 x 6 travelers = $3000.0
Return flight: $400.0 x 6 travelers = $2400.0
Hotel: $200.0 x 5 nights x 4 room(s) = $4000.0
Total cost: $9400.0
Budget: $8000.0
Status: The trip is over budget."""
    )
]

@pytest.mark.parametrize("test_name,input_data,expected_output", tests)
def test_estimate_trip_cost(test_name, input_data, expected_output):
    """Test estimate_trip_cost tool with multiple inputs."""
    result = estimate_trip_cost.invoke(input_data)

    assert result.strip() == expected_output.strip(), (
        f"{test_name} failed:\nExpected:\n{expected_output}\nGot:\n{result}"
    )
