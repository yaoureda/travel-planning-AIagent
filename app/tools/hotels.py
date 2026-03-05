from pydantic import BaseModel, Field
from langchain.tools import tool
from serpapi import GoogleSearch
from ..config import SERPAPI_KEY


class HotelSearchInput(BaseModel):
    destination: str = Field(description="City where the hotel is located")
    check_in: str = Field(description="Check-in date YYYY-MM-DD")
    check_out: str = Field(description="Check-out date YYYY-MM-DD")


@tool(args_schema=HotelSearchInput)
def search_hotels(destination: str, check_in: str, check_out: str) -> str:
    """Search hotels using Google Hotels."""

    try:
        params = {
            "engine": "google_hotels",
            "q": destination,
            "check_in_date": check_in,
            "check_out_date": check_out,
            "adults": 1,
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

        return f"Top hotels in {destination}:\n\n" + "\n".join(output)

    except Exception as e:
        return f"Hotel search error: {str(e)}"