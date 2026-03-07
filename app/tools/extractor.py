import json
from pydantic import BaseModel, Field, model_validator
from langchain.tools import tool

"""
This file defines the extractor tool that uses LangChain's structured tool capabilities to extract trip details from
user input. It returns a JSON string with the extracted information.
"""

# Define the structure using Pydantic model
class TripExtraction(BaseModel):
    origin: str = Field(description="Departure city")
    destination: str = Field(description="Destination city")
    departure_date: str = Field(description="Departure date in YYYY-MM-DD format")
    return_date: str = Field(description="Return date in YYYY-MM-DD format")
    adults: int = Field(default=1, description="Number of adult travelers (optional)")
    children: int = Field(default=0, description="Number of children (optional)")
    infants: int = Field(default=0, description="Number of infants (optional)")
    rooms: int = Field(default=None, description="Number of hotel rooms")


    @model_validator(mode="after")
    def default_rooms_to_adults(cls, model):
        """If rooms not specified, default to number of adults."""
        if model.rooms is None:
            model.rooms = model.adults
        return model


# Define the extractor tool
@tool(
    args_schema=TripExtraction,
    description=(
        "Extract trip details from a user message. "
        "Returns JSON string with origin, destination, departure_date, return_date, "
        "adults, children, infants, and rooms."
    )
)
def extract_travel(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    rooms: int = None
) -> str:
    """
    LangChain structured tool for extracting trip info.
    Returns JSON string.
    """
    try:
        if rooms is None:
            rooms = adults

        print("Using Travel Extraction Tool")
        trip_data = {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "adults": adults,
            "children": children,
            "infants": infants,
            "rooms": rooms
        }
        return json.dumps(trip_data)
    except Exception as e:
        return json.dumps({"error": f"Extraction failed: {str(e)}"})