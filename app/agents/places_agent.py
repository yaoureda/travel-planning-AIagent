from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain.agents import create_agent

from ..config import model
from ..tools.places import search_touristic_places
from ..tools.travel_duration import search_travel_duration


places_agent = create_agent(
    model=model,
    tools=[search_touristic_places, search_travel_duration],
    system_prompt=(
        "You are a sightseeing specialist subagent. "
        "You receive the full travel request plus selected flight and hotel context from the planner. "
        "First identify the destination city and search for relevant touristic places to visit. "
        "Then estimate travel duration for practical movement between the hotel area and suggested places. "
        "Return a concise place-visit plan with day grouping, ordering, and brief rationale. "
        "Always use both tools before finalizing recommendations when route context is available."
    ),
)


class PlacesAgentInput(BaseModel):
    trip_request: str = Field(
        description="Full travel request and selected transport/lodging context."
    )


@tool(
    "places",
    args_schema=PlacesAgentInput,
    description=(
        "Delegate sightseeing planning to the places subagent using the full trip request "
        "plus selected flights and hotels context."
    ),
)
def call_places_agent(trip_request: str):
    print("Calling places agent with full trip request")
    result = places_agent.invoke({"messages": [{"role": "user", "content": trip_request}]})
    return result["messages"][-1].content
