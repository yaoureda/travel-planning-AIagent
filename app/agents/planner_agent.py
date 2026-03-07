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
    system_prompt="You are a helpful travel planning assistant. " \
    "Use tools to find flights, hotels, and estimate total cost. " \
    "When delegating to subagents, call each subagent tool once using the full itinerary request, " \
    "not one call per leg. Subagents are responsible for splitting multi-city itineraries internally. " \
    "Always use the extractor tool first to normalize trip details before using other tools. " \
    "Provide detailed but concise recommendations and compare final cost to user budget when available."
)