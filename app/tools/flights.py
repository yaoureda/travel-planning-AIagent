from pydantic import BaseModel, Field
from langchain.tools import tool
from amadeus import ResponseError
from ..config import amadeus


# Input obligatoire pour aller-retour
class FlightSearchInput(BaseModel):
    origin: str = Field(description="IATA code of departure city (ex: PAR)")
    destination: str = Field(description="IATA code of destination city (ex: BCN)")
    departure_date: str = Field(description="Departure date in YYYY-MM-DD format")
    return_date: str = Field(description="Return date in YYYY-MM-DD format")


@tool(args_schema=FlightSearchInput, description="Search for available round-trip flights using Amadeus API")
def search_flights(origin: str, destination: str, departure_date: str, return_date: str) -> str:
    """Search for round-trip flights between two cities using Amadeus."""

    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            returnDate=return_date,
            adults=1,
            max=5
        )

        flights = response.data

        if not flights:
            return f"No flights found from {origin} to {destination} between {departure_date} and {return_date}"

        results = []

        for flight in flights:

            price = flight["price"]["total"]

            dep_segment = flight["itineraries"][0]["segments"][0]
            ret_segment = flight["itineraries"][1]["segments"][0]

            dep_airline = dep_segment["carrierCode"]
            dep_departure = dep_segment["departure"]["at"]
            dep_arrival = dep_segment["arrival"]["at"]

            ret_airline = ret_segment["carrierCode"]
            ret_departure = ret_segment["departure"]["at"]
            ret_arrival = ret_segment["arrival"]["at"]

            results.append(
                f"""
Departure:
Airline: {dep_airline}
From {origin} → {destination}
Departure: {dep_departure}
Arrival: {dep_arrival}

Return:
Airline: {ret_airline}
From {destination} → {origin}
Departure: {ret_departure}
Arrival: {ret_arrival}

Total price: ${price}
"""
            )

        return "Available flights:\n" + "\n".join(results)

    except ResponseError as error:
        return f"Error retrieving flights: {error}"