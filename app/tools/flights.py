from pydantic import BaseModel, Field
from langchain.tools import tool


# Input obligatoire pour aller-retour
class FlightSearchInput(BaseModel):
    origin: str = Field(description="City where the trip starts")
    destination: str = Field(description="City where the user wants to travel")
    departure_date: str = Field(description="Departure date in YYYY-MM-DD format")
    return_date: str = Field(description="Return date in YYYY-MM-DD format")


@tool(args_schema=FlightSearchInput, description="Search for available flights for departure and return")
def search_flights(origin: str, destination: str, departure_date: str, return_date: str) -> str:
    """Search for available flights (departure and return) between two cities."""

    # Mock flight database
    flight_data = [
        {"origin": "Paris", "destination": "Barcelona", "date": "2026-06-01", "airline": "Vueling", "price": 85},
        {"origin": "Paris", "destination": "Barcelona", "date": "2026-06-01", "airline": "Air France", "price": 120},
        {"origin": "Barcelona", "destination": "Paris", "date": "2026-06-05", "airline": "Vueling", "price": 90},
        {"origin": "Barcelona", "destination": "Paris", "date": "2026-06-05", "airline": "Air France", "price": 110},
        {"origin": "Rome", "destination": "Amsterdam", "date": "2026-09-01", "airline": "KLM", "price": 140},
        {"origin": "Amsterdam", "destination": "Rome", "date": "2026-09-05", "airline": "KLM", "price": 150},
    ]

    results = []

    # Chercher le vol aller
    for f in flight_data:
        if f["origin"].lower() == origin.lower() and f["destination"].lower() == destination.lower() and f["date"] == departure_date:
            results.append(f'Departure: {f["airline"]} from {origin} to {destination} on {departure_date}: ${f["price"]}')

    # Chercher le vol retour
    for f in flight_data:
        if f["origin"].lower() == destination.lower() and f["destination"].lower() == origin.lower() and f["date"] == return_date:
            results.append(f'Return: {f["airline"]} from {destination} to {origin} on {return_date}: ${f["price"]}')

    if not results:
        return f"No flights found for the trip from {origin} to {destination} and back on the specified dates."

    return "Available flights:\n" + "\n".join(results)