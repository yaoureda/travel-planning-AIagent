from unittest.mock import patch, MagicMock

from app.tools.places import search_touristic_places


def test_search_touristic_places_found():
    mock_data = {
        "local_results": [
            {
                "title": "Sagrada Familia",
                "rating": 4.8,
                "reviews": 120000,
                "address": "Carrer de Mallorca, Barcelona",
                "type": "Basilica",
            },
            {
                "title": "Park Guell",
                "rating": 4.6,
                "reviews": 90000,
                "address": "Gracia, Barcelona",
                "type": "Park",
            },
        ]
    }

    with patch("app.tools.places.GoogleSearch") as mock_search:
        instance = MagicMock()
        instance.get_dict.return_value = mock_data
        mock_search.return_value = instance

        result = search_touristic_places.run({"destination": "Barcelona", "max_results": 2})
        assert "Top touristic places in Barcelona" in result
        assert "Sagrada Familia" in result
        assert "Park Guell" in result


def test_search_touristic_places_no_results():
    with patch("app.tools.places.GoogleSearch") as mock_search:
        instance = MagicMock()
        instance.get_dict.return_value = {"local_results": []}
        mock_search.return_value = instance

        result = search_touristic_places.run({"destination": "UnknownCity", "max_results": 3})
        assert "No touristic places found for UnknownCity" in result
