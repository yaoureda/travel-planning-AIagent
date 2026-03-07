from langchain.agents import create_agent

from .config import model
from .tools.extractor import extract_travel
from .tools.flights import search_flights
from .tools.hotels import search_hotels
from .tools.budget import estimate_trip_cost

# grouping tools and creating agent
tools = [
    extract_travel,
    search_flights,
    search_hotels,
    estimate_trip_cost
]
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="You are a helpful travel planning assistant." \
    " Use the tools to find flights, hotels, and estimate the total cost of a trip. " \
    "Give a lot of details about the flights and hotels." \
    "Estimate the total cost of the trip and compare it to the user's budget. " \
    " Always consider using extract_travel tool first when possible."
)