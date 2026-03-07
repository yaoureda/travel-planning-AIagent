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
    return_date: str = Field(default=None, description="Return date in YYYY-MM-DD format. Omit for one-way flights.")
    adults: int = Field(default=1, description="Number of adult travelers (optional)")
    children: int = Field(default=0, description="Number of children (optional)")
    infants: int = Field(default=0, description="Number of infants (optional)")


@tool(args_schema=FlightSearchInput, description="Search for one-way or round-trip flights using Amadeus API. Omit return_date for one-way flights.")
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0
) -> str:
    """Search for one-way or round-trip flights between two cities using Amadeus."""

    try:
        # Call Amadeus API to search for flight offers
        trip_type = "round-trip" if return_date else "one-way"
        print(f"Searching {trip_type} flights from {origin} to {destination} departing {departure_date}")

        params = dict(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            adults=adults,
            children=children,
            infants=infants,
            max=5,
        )
        if return_date:
            params["returnDate"] = return_date

        response = amadeus.shopping.flight_offers_search.get(**params)

        flights = response.data

        if not flights:
            print("No flights found")
            date_info = f"departing {departure_date}" + (f" returning {return_date}" if return_date else "")
            return f"No flights found from {origin} to {destination} {date_info}"

        # Format the flight information into a readable string
        results = []

        for flight in flights:

            price = flight["price"]["total"]

            dep_segment = flight["itineraries"][0]["segments"][0]
            dep_airline = dep_segment["carrierCode"]
            dep_departure = dep_segment["departure"]["at"]
            dep_arrival = dep_segment["arrival"]["at"]

            entry = (
                f"Airline: {dep_airline}\n"
                f"From {origin} → {destination}\n"
                f"Departure: {dep_departure} | Arrival: {dep_arrival}\n"
            )

            if return_date and len(flight["itineraries"]) > 1:
                ret_segment = flight["itineraries"][1]["segments"][0]
                ret_airline = ret_segment["carrierCode"]
                ret_departure = ret_segment["departure"]["at"]
                ret_arrival = ret_segment["arrival"]["at"]
                entry += (
                    f"Return — Airline: {ret_airline}\n"
                    f"From {destination} → {origin}\n"
                    f"Departure: {ret_departure} | Arrival: {ret_arrival}\n"
                )

            entry += f"Total price: ${price}"
            results.append(entry)
        print("Using Flight Search Tool")
        return "Available flights:\n" + "\n".join(results)

    except ResponseError as error:
        print(f"Error retrieving flights: {error}")
        return f"Error retrieving flights: {error}"