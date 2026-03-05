from pydantic import BaseModel, Field
from langchain.tools import tool

from ..extractor import extract_travel_info

# flight tool
# Flight search tool
class FlightSearchInput(BaseModel):
    """Input for flight search."""

    origin: str = Field(description="City where the trip starts")
    destination: str = Field(description="City where the user wants to travel")
    date: str = Field(description="Departure date in YYYY-MM-DD format")


@tool(args_schema=FlightSearchInput)
def search_flights(origin: str, destination: str, date: str) -> str:
    """Search for available flights between two cities on a specific date."""

    # Mock flight database
    flight_data = [
        {
            "origin": "Paris",
            "destination": "Barcelona",
            "date": "2026-06-01",
            "airline": "Vueling",
            "price": 85
        },
        {
            "origin": "Paris",
            "destination": "Barcelona",
            "date": "2026-06-01",
            "airline": "Air France",
            "price": 120
        },
        {
            "origin": "Rome",
            "destination": "Amsterdam",
            "date": "2026-09-01",
            "airline": "KLM",
            "price": 140
        },
        {
            "origin": "Toronto",
            "destination": "Sydney",
            "date": "2026-10-01",
            "airline": "Qantas",
            "price": 950
        }
    ]

    results = []

    for flight in flight_data:
        if (
            flight["origin"].lower() == origin.lower()
            and flight["destination"].lower() == destination.lower()
            and flight["date"] == date
        ):
            results.append(
                f'{flight["airline"]} flight from {origin} to {destination} on {date}: ${flight["price"]}'
            )

    if not results:
        return f"No flights found from {origin} to {destination} on {date}."

    return "Available flights:\n" + "\n".join(results)

# Example of how to use the tool
def find_flights_for_trip(user_query: str):

    trip = extract_travel_info(user_query)

    flights = search_flights.invoke({
        "origin": trip["origin"],
        "destination": trip["destination"],
        "date": trip["check_in"]
    })

    print("Trip info:", trip)
    print("\nFlights found:")
    print(flights)