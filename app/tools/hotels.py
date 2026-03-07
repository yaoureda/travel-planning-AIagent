from pydantic import BaseModel, Field, model_validator
from langchain.tools import tool
from serpapi import GoogleSearch
from ..config import SERPAPI_KEY

"""
This file defines the hotel search tool that uses SerpAPI to find hotels based on user input.
"""

class HotelSearchInput(BaseModel):
    destination: str = Field(description="City where the hotel is located")
    check_in: str = Field(description="Check-in date YYYY-MM-DD")
    check_out: str = Field(description="Check-out date YYYY-MM-DD")
    adults: int = Field(default=1, description="Number of adults (optional)")
    rooms: int = Field(default=None, description="Number of hotel rooms")

    @model_validator(mode="after")
    def default_rooms_to_adults(cls, model):
        """If rooms not specified, default to number of adults."""
        if model.rooms is None:
            model.rooms = model.adults
        return model


@tool(args_schema=HotelSearchInput)
def search_hotels(
    destination: str,
    check_in: str,
    check_out: str,
    adults: int = 1,
    rooms: int = None
) -> str:
    """Search hotels using Google Hotels."""

    try:
        if rooms is None:
            rooms = adults
            
        params = {
            "engine": "google_hotels",
            "q": destination,
            "check_in_date": check_in,
            "check_out_date": check_out,
            "adults": adults,
            "rooms": rooms,
            "currency": "EUR",
            "hl": "en",
            "api_key": SERPAPI_KEY
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        hotels = results.get("properties", [])

        if not hotels:
            return f"No hotels found in {destination}"

        output = []

        for hotel in hotels[:5]:
            name = hotel.get("name", "Unknown hotel")
            price = hotel.get("rate_per_night", {}).get("lowest", "N/A")
            rating = hotel.get("overall_rating", "N/A")
            location = hotel.get("address", "")

            output.append(
                f"{name}\n⭐ Rating: {rating}\n💰 Price: {price}\n📍 {location}\n"
            )
        print("Using Hotel Search Tool")
        return f"Top hotels in {destination}:\n\n" + "\n".join(output)

    except Exception as e:
        return f"Hotel search error: {str(e)}"