from datetime import datetime

from langchain.agents import create_agent

from app.agents.flights_agent import call_flights_agent
from app.agents.hotels_agent import call_hotels_agent
from app.agents.places_agent import call_places_agent

from ..config import model
from ..tools.extractor import extract_travel
from ..tools.budget import estimate_trip_cost

# grouping tools and creating agent
tools = [
    extract_travel,
    call_flights_agent,
    call_hotels_agent,
    call_places_agent,
    estimate_trip_cost
]
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=(
        "You are a helpful travel planning assistant. "
        "Use the tools to find flights, hotels, and estimate the total cost of the trip. "
        "When delegating to subagents, call each subagent tool with the full itinerary — "
        "subagents handle multi-leg and multi-city decomposition internally. "
        "After you have selected the recommended flights and hotels, call the places subagent to build a places-to-visit plan that fits the stay. "
        "Before using tools, reason through the user's request and make a clear plan for which tools to call with what information. "
        "API calls are costly, so be efficient and avoid calling tools multiple times with overlapping information. "
        "Make reasonable assumptions: if no departure city is given, ask only once; "
        "for multi-city trips always search one-way flights between each leg, not round-trips. "
        "Always use the extractor tool first to normalize trip details before using other tools. "
        "Don't give the user multiple options for flights or hotels; just give the best one based on price and convenience."
        "If the distance does not require a flight, recommend others modes of transport. "
        "Your role is to give the user ready-to-book recommendations, not to provide a menu of choices. To acheive this, you should consider the subagents as real experts in their domain and trust them to make the best choice for the user. "
        "But don't be afraid to ask them for more information if you think it will help them make a better recommendation. "
        "In your final response, include: chosen flights, chosen hotels, places-to-visit plan, and budget verdict. "
        "Always compare the final estimated cost to the user's budget and give a clear recommendation."
        f"If no year is specified for travel dates, assume the next occurrence of those dates. Here is the current date for reference: {datetime.now().strftime('%Y-%m-%d')}"
    )
)
