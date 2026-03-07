from pydantic import BaseModel, Field, model_validator
from langchain.tools import tool

"""
This file defines the budget estimation tool that calculates the total cost of a trip.
"""
# Trip cost estimation input
class TripCostInput(BaseModel):
    """Input for estimating the total trip cost including flights and hotel."""
    departure_flight_price: float = Field(description="Price of the departure flight per traveler")
    return_flight_price: float = Field(description="Price of the return flight per traveler")
    hotel_price_per_night: float = Field(description="Price of the hotel per night per room")
    nights: int = Field(description="Number of nights for the hotel stay")
    adults: int = Field(default=1, description="Number of adult travelers (optional)")
    children: int = Field(default=0, description="Number of children (optional)")
    infants: int = Field(default=0, description="Number of infants (optional)")
    rooms: int | None = Field(default=None, description="Number of hotel rooms")
    budget: float = Field(description="User's total travel budget")

    @model_validator(mode="after")
    def default_rooms_to_adults(cls, model):
        """If rooms not specified, default to number of adults."""
        if model.rooms is None:
            model.rooms = model.adults
        return model


# Trip cost estimation tool
@tool(args_schema=TripCostInput, description="Estimate total trip cost including flights and hotel for all travelers")
def estimate_trip_cost(
    departure_flight_price: float,
    return_flight_price: float,
    hotel_price_per_night: float,
    nights: int,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    rooms: int | None = None,
    budget: float = 0.0
) -> str:
    """Estimate the total cost including all travelers and rooms."""
    if rooms is None:
        rooms = adults

    num_travelers = adults + children + infants
    flight_total = (departure_flight_price + return_flight_price) * num_travelers
    hotel_total = hotel_price_per_night * nights * rooms
    total_cost = flight_total + hotel_total

    status = "within budget" if total_cost <= budget else "over budget"

    print("Using Budget Estimation Tool")

    return (
        f"Estimated trip cost:\n"
        f"Departure flight: ${departure_flight_price} x {num_travelers} travelers = ${departure_flight_price * num_travelers}\n"
        f"Return flight: ${return_flight_price} x {num_travelers} travelers = ${return_flight_price * num_travelers}\n"
        f"Hotel: ${hotel_price_per_night} x {nights} nights x {rooms} room(s) = ${hotel_total}\n"
        f"Total cost: ${total_cost}\n"
        f"Budget: ${budget}\n"
        f"Status: The trip is {status}."
    )