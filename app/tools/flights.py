from pydantic import BaseModel, Field
from langchain.tools import tool
from amadeus import ResponseError
from ..config import amadeus

"""
This file defines the flight search tool that uses the Amadeus API to find available round-trip flights based on user input.
"""

# Define input schema
class FlightSearchInput(BaseModel):
    origin: str = Field(description="IATA code of departure city (ex: PAR)")
    destination: str = Field(description="IATA code of destination city (ex: BCN)")
    departure_date: str = Field(description="Departure date in YYYY-MM-DD format")
    return_date: str = Field(description="Return date in YYYY-MM-DD format")
    adults: int = Field(default=1, description="Number of adult travelers (optional)")
    children: int = Field(default=0, description="Number of children (optional)")
    infants: int = Field(default=0, description="Number of infants (optional)")


@tool(args_schema=FlightSearchInput, description="Search for available round-trip flights using Amadeus API")
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str,
    adults: int = 1,
    children: int = 0,
    infants: int = 0
) -> str:
    """Search for round-trip flights between two cities using Amadeus."""

    try:
        # Call Amadeus API to search for flight offers
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            returnDate=return_date,
            adults=adults,
            children=children,
            infants=infants,
            max=5
        )

        flights = response.data

        if not flights:
            return f"No flights found from {origin} to {destination} between {departure_date} and {return_date}"

        # Format the flight information into a readable string
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
        print("Using Flight Search Tool")
        return "Available flights:\n" + "\n".join(results)

    except ResponseError as error:
        return f"Error retrieving flights: {error}"