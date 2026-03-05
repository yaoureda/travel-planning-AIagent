from pydantic import BaseModel, Field
from langchain.tools import tool

# Hotel search tool
class HotelSearchInput(BaseModel):
    """Input for hotel search."""
    destination: str = Field(description="City where the hotel is located")
    check_in: str = Field(description="Check-in date in YYYY-MM-DD format")
    check_out: str = Field(description="Check-out date in YYYY-MM-DD format")

@tool(args_schema=HotelSearchInput, description="Search for available hotels in a city for given dates")
def search_hotels(destination: str, check_in: str, check_out: str) -> str:
    """Search for hotels in a given city for the specified date range."""

    # Mock hotel database
    hotel_data = [
        {"destination": "Barcelona", "hotel": "Hotel Barcelona Center", "price_per_night": 110, "rating": 4.3},
        {"destination": "Barcelona", "hotel": "Hostal BCN Ramblas", "price_per_night": 70, "rating": 4.0},
        {"destination": "Amsterdam", "hotel": "Amsterdam Canal Hotel", "price_per_night": 130, "rating": 4.5},
        {"destination": "Sydney", "hotel": "Sydney Harbour Hotel", "price_per_night": 180, "rating": 4.6},
        {"destination": "Madrid", "hotel": "Madrid Central Hotel", "price_per_night": 95, "rating": 4.2}
    ]

    results = [
        f'{hotel["hotel"]} in {destination}: ${hotel["price_per_night"]}/night (rating {hotel["rating"]})'
        for hotel in hotel_data if hotel["destination"].lower() == destination.lower()
    ]

    if not results:
        return f"No hotels found in {destination}."

    return f"Hotels available in {destination} from {check_in} to {check_out}:\n" + "\n".join(results)