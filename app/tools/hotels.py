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
    rooms: int | None = Field(default=None, description="Number of hotel rooms")

    @model_validator(mode="after")
    def default_rooms_to_adults(self):
        if self.rooms is None:
            self.rooms = self.adults
        return self


@tool(args_schema=HotelSearchInput)
def search_hotels(
    destination: str,
    check_in: str,
    check_out: str,
    adults: int = 1,
    rooms: int | None = None
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
        print(f"Hotel search parameters: {params}")
        print(f"Searching hotels in {destination} for check-in on {check_in} and check-out on {check_out} for {adults} adults and {rooms} rooms.")
        search = GoogleSearch(params)
        results = search.get_dict()

        hotels = results.get("properties", [])

        if not hotels:
            print("No hotels found")
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
    
if __name__ == "__main__":
    # Example usage for dubugging
    params = {
        "engine": "google_hotels",
        "q": "Barcelona",
        "check_in_date": "2026-07-01",
        "check_out_date": "2026-07-05",
        "adults": 2,
        "rooms": 1,
        "currency": "EUR",
        "hl": "en",
        "api_key": SERPAPI_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    hotels = results.get("properties", [])
    for hotel in hotels[:5]:
        name = hotel.get("name", "Unknown hotel")
        price = hotel.get("rate_per_night", {}).get("lowest", "N/A")
        rating = hotel.get("overall_rating", "N/A")
        location = hotel.get("address", "")
        print(f"{name}\n⭐ Rating: {rating}\n💰 Price: {price}\n📍 {location}\n")
