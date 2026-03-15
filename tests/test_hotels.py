import pytest
from unittest.mock import patch, MagicMock
from app.tools.hotels import search_hotels

# Mock data simulating SerpAPI response
mock_hotels_data = {
    "properties": [
        {
            "name": "Hotel Sunshine",
            "rate_per_night": {"lowest": "120 EUR"},
            "overall_rating": "8.5",
            "address": "123 Main St, Paris"
        },
        {
            "name": "Hotel Moonlight",
            "rate_per_night": {"lowest": "150 EUR"},
            "overall_rating": "9.0",
            "address": "456 Rue de Paris"
        }
    ]
}

def test_search_hotels_found():
    """Test the search_hotels tool when hotels are found."""
    
    # Replace the GoogleSearch call with our mock response
    with patch("app.tools.hotels.GoogleSearch") as mock_search:
        # Mock the GoogleSearch instance and its get_dict() method
        instance = MagicMock()
        instance.get_dict.return_value = mock_hotels_data
        mock_search.return_value = instance

        # Input dictionary matching HotelSearchInput schema
        input_data = {
            "destination": "Paris",
            "check_in": "2026-05-01",
            "check_out": "2026-05-05",
            "adults": 2,
            "rooms": 1
        }

        result = search_hotels.run(input_data)
        assert "Hotel Sunshine" in result
        assert "Hotel Moonlight" in result
        assert "Top hotels in Paris" in result

def test_search_hotels_no_results():
    """Test the search_hotels tool when no hotels are found."""

    with patch("app.tools.hotels.GoogleSearch") as mock_search:
        instance = MagicMock()
        instance.get_dict.return_value = {"properties": []}
        mock_search.return_value = instance

        input_data = {
            "destination": "NowhereCity",
            "check_in": "2026-05-01",
            "check_out": "2026-05-05",
            "adults": 1,
            "rooms": 1
        }

        result = search_hotels.run(input_data)
        assert "No hotels found in NowhereCity" in result