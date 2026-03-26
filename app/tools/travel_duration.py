import time

from pydantic import BaseModel, Field
from langchain.tools import tool
from serpapi import GoogleSearch

from ..config import SERPAPI_KEY


class TravelDurationInput(BaseModel):
    origin: str = Field(description="Starting location")
    destination: str = Field(description="Destination location")
    mode: str = Field(default="transit", description="Travel mode: driving, transit, walking, or bicycling")


@tool(args_schema=TravelDurationInput, description="Get estimated travel duration between two places using SerpApi Google Maps Directions.")
def search_travel_duration(origin: str, destination: str, mode: str = "transit") -> str:
    """Search travel duration between origin and destination."""

    try:
        start = time.time()
        normalized_mode = mode.lower().strip()
        if normalized_mode not in {"driving", "transit", "walking", "bicycling"}:
            normalized_mode = "transit"

        params = {
            "engine": "google_maps_directions",
            "start_addr": origin,
            "end_addr": destination,
            "travel_mode": normalized_mode,
            "hl": "en",
            "api_key": SERPAPI_KEY,
        }
        #print(f"Travel duration parameters: {params}")

        search = GoogleSearch(params)
        results = search.get_dict()

        directions = results.get("directions", [])
        if not directions:
            return f"No route found from {origin} to {destination} by {normalized_mode}."

        best_route = directions[0]
        route_duration = best_route.get("duration", "N/A")
        distance = best_route.get("distance", "N/A")

        time_taken = time.time() - start
        print(f"[Tool Timing] search_travel_duration took {time_taken:.2f}s")

        return (
            f"Estimated travel from {origin} to {destination} by {normalized_mode}:\n"
            f"Duration: {route_duration}\n"
            f"Distance: {distance}"
        )
    except Exception as e:
        print(f"Error during travel duration search: {str(e)}")
        return f"Travel duration search error: {str(e)}"
