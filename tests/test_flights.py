from unittest.mock import patch, MagicMock
from app.tools.flights import search_flights

# Mock data simulating Amadeus API response for flight search
mock_flight_data = {
    "data": [
        {
            "price": {"total": "250.00"},
            "itineraries": [
                {
                    "segments": [
                        {"carrierCode": "AF",
                         "departure": {"at": "2026-04-01T10:00"},
                         "arrival": {"at": "2026-04-01T12:00"}}
                    ]
                },
                {
                    "segments": [
                        {"carrierCode": "AF",
                         "departure": {"at": "2026-04-07T15:00"},
                         "arrival": {"at": "2026-04-07T17:00"}}
                    ]
                }
            ]
        }
    ]
}

def test_search_flights_round_trip():
    """Test the search_flights tool for a round-trip flight search."""

    # Replace the Amadeus API call with our mock response
    with patch("app.tools.flights.amadeus.shopping.flight_offers_search.get") as mock_get:
        mock_response = MagicMock()
        mock_response.data = mock_flight_data["data"]
        mock_get.return_value = mock_response

        input_data = {
            "origin": "PAR",
            "destination": "BCN",
            "departure_date": "2026-04-01",
            "return_date": "2026-04-07",
            "adults": 1,
            "children": 0,
            "infants": 0,
        }

        result = search_flights.run(input_data)
        assert "Airline: AF" in result
        assert "Return — Airline: AF" in result

def test_search_flights_no_results():
    """Test the search_flights tool when no flights are found."""
    
    with patch("app.tools.flights.amadeus.shopping.flight_offers_search.get") as mock_get:
        mock_response = MagicMock()
        mock_response.data = []
        mock_get.return_value = mock_response

        input_data = {
            "origin": "PAR",
            "destination": "MAD",
            "departure_date": "2026-04-01",
            "adults": 1,
            "children": 0,
            "infants": 0,
            "return_date": None
        }

        result = search_flights.run(input_data)
        assert "No flights found from PAR to MAD departing 2026-04-01" in result