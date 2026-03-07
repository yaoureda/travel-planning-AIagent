from pydantic import BaseModel, Field
from langchain.tools import tool

"""
This file defines the trip cost estimation tool that calculates the total cost of a trip based on flight and hotel prices, and compares it to the user's budget.
"""

# Trip cost estimation tool including round-trip flight
class TripCostInput(BaseModel):
    """Input for estimating the total trip cost (round-trip flights included)."""

    departure_flight_price: float = Field(description="Price of the departure flight")
    return_flight_price: float = Field(description="Price of the return flight")
    hotel_price_per_night: float = Field(description="Price of the hotel per night")
    nights: int = Field(description="Number of nights for the hotel stay")
    budget: float = Field(description="User's total travel budget")


@tool(args_schema=TripCostInput, description="Estimate the total trip cost including return flight")
def estimate_trip_cost(
    departure_flight_price: float,
    return_flight_price: float,
    hotel_price_per_night: float,
    nights: int,
    budget: float
) -> str:
    """Estimate the total cost of the trip including departure and return flights and hotel stay."""

    flight_total = departure_flight_price + return_flight_price
    hotel_total = hotel_price_per_night * nights
    total_cost = flight_total + hotel_total

    if total_cost <= budget:
        status = "within budget"
    else:
        status = "over budget"

    return (
        f"Estimated trip cost:\n"
        f"Departure flight: ${departure_flight_price}\n"
        f"Return flight: ${return_flight_price}\n"
        f"Hotel: ${hotel_price_per_night} x {nights} nights = ${hotel_total}\n"
        f"Total cost: ${total_cost}\n"
        f"Budget: ${budget}\n"
        f"Status: The trip is {status}."
    )
