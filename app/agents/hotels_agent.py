from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain.agents import create_agent

from ..config import model
from ..tools.hotels import search_hotels

# Create a subagent
hotels_agent = create_agent(
    model=model,
    tools=[search_hotels],
    system_prompt=(
        "You are a hotel specialist subagent. "
        "You receive the full travel request and are responsible for finding hotels. "
        "If the itinerary includes multiple stays, split it into the required city/date stays and run search_hotels for each stay. "
        "Do not ask the planner for per-stay prompts. "
        "Always use search_hotels to fetch hotel data before responding."
        "Optimize hotels API calls by only calling once per city with the full date range of the stay, rather than one call per night."
    ),
)


class HotelsAgentInput(BaseModel):
    trip_request: str = Field(
        description="Full travel request, including itinerary details and traveler constraints."
    )

# Wrap it as a tool
@tool(
    "hotels",
    args_schema=HotelsAgentInput,
    description=(
        "Delegate hotel planning to the hotels subagent using one full trip request. "
        "The subagent handles multi-stay decomposition internally."
    ),
)
def call_hotels_agent(trip_request: str):
    print("Calling hotels agent with full trip request")
    result = hotels_agent.invoke({"messages": [{"role": "user", "content": trip_request}]})
    return result["messages"][-1].content