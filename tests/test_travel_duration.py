from unittest.mock import patch, MagicMock

from app.tools.travel_duration import search_travel_duration


def test_search_travel_duration_found():
    mock_data = {
        "directions": [
            {
                "duration": "18 mins",
                "distance": "6.4 km",
            }
        ]
    }

    with patch("app.tools.travel_duration.GoogleSearch") as mock_search:
        instance = MagicMock()
        instance.get_dict.return_value = mock_data
        mock_search.return_value = instance

        result = search_travel_duration.run(
            {"origin": "Hotel Arts Barcelona", "destination": "Sagrada Familia", "mode": "transit"}
        )
        assert "Estimated travel from Hotel Arts Barcelona to Sagrada Familia by transit" in result
        assert "Duration: 18 mins" in result
        assert "Distance: 6.4 km" in result


def test_search_travel_duration_no_route():
    with patch("app.tools.travel_duration.GoogleSearch") as mock_search:
        instance = MagicMock()
        instance.get_dict.return_value = {"directions": []}
        mock_search.return_value = instance

        result = search_travel_duration.run(
            {"origin": "Point A", "destination": "Point B", "mode": "walking"}
        )
        assert "No route found from Point A to Point B by walking" in result
