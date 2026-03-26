import time

from pydantic import BaseModel, Field
from langchain.tools import tool
from serpapi import GoogleSearch

from ..config import SERPAPI_KEY


class PlacesSearchInput(BaseModel):
    destination: str = Field(description="City or area to explore")
    max_results: int = Field(default=5, description="Maximum number of places to return")


@tool(args_schema=PlacesSearchInput, description="Search top touristic places to visit using SerpApi Google Local results.")
def search_touristic_places(destination: str, max_results: int = 5) -> str:
    """Search popular touristic places in a destination."""

    try:
        start = time.time()
        limit = max(1, min(max_results, 10))
        params = {
            "engine": "google_local",
            "q": f"best touristic places to visit in {destination}",
            "google_domain": "google.com",
            "hl": "en",
            "api_key": SERPAPI_KEY,
        }
        #print(f"Places search parameters: {params}")

        search = GoogleSearch(params)
        results = search.get_dict()
        sights = results.get("top_sights", [])

        if not sights:
            return f"No touristic places found for {destination}."

        output = []
        for sight in sights[:limit]:
            name = sight.get("title", "Unknown place")
            rating = sight.get("rating", "N/A")
            reviews = sight.get("reviews", "N/A")
            description = sight.get("description", "")
            output.append(
                f"{name}\n"
                f"Rating: {rating} ({reviews} reviews)\n"
                f"Description: {description}\n"
            )

        duration = time.time() - start
        print(f"[Tool Timing] search_touristic_places took {duration:.2f}s")

        return f"Top touristic places in {destination}:\n\n" + "\n".join(output)
    except Exception as e:
        print(f"Error during touristic places search: {str(e)}")
        return f"Touristic places search error: {str(e)}"
