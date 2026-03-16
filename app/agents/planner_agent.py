from datetime import datetime

from langchain.agents import create_agent

from app.agents.flights_agent import call_flights_agent
from app.agents.hotels_agent import call_hotels_agent

from ..config import model
from ..tools.extractor import extract_travel
from ..tools.budget import estimate_trip_cost

# grouping tools and creating agent
tools = [
    extract_travel,
    call_flights_agent,
    call_hotels_agent,
    estimate_trip_cost
]
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=(
        "You are a helpful travel planning assistant. "
        "Use the tools to find flights, hotels, and estimate the total cost of the trip. "
        "When delegating to subagents, call each subagent tool ONCE with the full itinerary — "
        "subagents handle multi-leg and multi-city decomposition internally. "
        "Before using tools, reason through the user's request and make a clear plan for which tools to call with what information. "
        "API calls are costly, so be efficient and avoid calling tools multiple times with overlapping information. "
        "Make reasonable assumptions: if no departure city is given, ask only once; "
        "for multi-city trips always search one-way flights between each leg, not round-trips. "
        "Always use the extractor tool first to normalize trip details before using other tools. " \
        "Always compare the final estimated cost to the user's budget and give a clear recommendation."
        f"If no year is specified for travel dates, assume the next occurrence of those dates. Here is the current date for reference: {datetime.now().strftime('%Y-%m-%d')}"
    )
)
