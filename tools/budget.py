from pydantic import BaseModel, Field
from langchain.tools import tool

from extractor import extract_travel_info
from main import calculate_nights

# budget tool
# Trip cost estimation tool
class TripCostInput(BaseModel):
    """Input for estimating the total trip cost."""

    flight_price: float = Field(description="Price of the selected flight")
    hotel_price_per_night: float = Field(description="Price of the hotel per night")
    nights: int = Field(description="Number of nights for the hotel stay")
    budget: float = Field(description="User's total travel budget")


@tool(args_schema=TripCostInput)
def estimate_trip_cost(
    flight_price: float,
    hotel_price_per_night: float,
    nights: int,
    budget: float
) -> str:
    """Estimate the total cost of the trip and compare it with the user's budget."""

    hotel_total = hotel_price_per_night * nights
    total_cost = flight_price + hotel_total

    if total_cost <= budget:
        status = "within budget"
    else:
        status = "over budget"

    return (
        f"Estimated trip cost:\n"
        f"Flight: ${flight_price}\n"
        f"Hotel: ${hotel_price_per_night} x {nights} nights = ${hotel_total}\n"
        f"Total cost: ${total_cost}\n"
        f"Budget: ${budget}\n"
        f"Status: The trip is {status}."
    )

# Example of how to use the tool
def estimate_trip(user_query: str):

    trip = extract_travel_info(user_query)

    nights = calculate_nights(trip["check_in"], trip["check_out"])

    cost = estimate_trip_cost.invoke({
        "flight_price": 120,
        "hotel_price_per_night": 100,
        "nights": nights,
        "budget": float(trip["budget"].replace("$",""))
    })

    print(cost)