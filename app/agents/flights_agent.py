from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain.agents import create_agent

from ..config import model
from ..tools.flights import search_flights

# Create a subagent
flights_agent = create_agent(
    model=model,
    tools=[search_flights],
    system_prompt=(
        "You are a flight specialist subagent. "
        "You receive the full travel request and are responsible for finding flights. "
        "If the itinerary is multi-city, split it into the required legs and run search_flights for each leg as needed. "
        "Do not ask the planner for per-leg prompts. "
        "Always use search_flights to fetch flight data before responding."
    ),
)


class FlightsAgentInput(BaseModel):
    trip_request: str = Field(
        description="Full travel request, including itinerary details and traveler constraints."
    )

# Wrap it as a tool
@tool(
    "flights",
    args_schema=FlightsAgentInput,
    description=(
        "Delegate flight planning to the flights subagent using one full trip request. "
        "The subagent handles multi-leg decomposition internally."
    ),
)
def call_flights_agent(trip_request: str):
    print("Calling flights agent with full trip request")
    result = flights_agent.invoke({"messages": [{"role": "user", "content": trip_request}]})
    return result["messages"][-1].content
