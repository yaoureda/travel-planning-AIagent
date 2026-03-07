import json
from pydantic import BaseModel, Field, model_validator
from langchain.tools import tool
from ..config import model
import warnings

# Ignore Pydantic serialization warnings
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=r"Pydantic serializer warnings:.*"
)

"""
Travel extractor tool: takes a user query and returns structured trip details.
"""

# Define the Pydantic schema for the extracted trip
class TripExtraction(BaseModel):
    origin: str = Field(description="Departure city")
    destination: str = Field(description="Destination city")
    departure_date: str = Field(description="Departure date in YYYY-MM-DD format")
    return_date: str = Field(description="Return date in YYYY-MM-DD format")
    adults: int = Field(default=1, description="Number of adult travelers")
    children: int = Field(default=0, description="Number of children")
    infants: int = Field(default=0, description="Number of infants")
    rooms: int | None = Field(default=None, description="Number of hotel rooms")

    @model_validator(mode="after")
    def default_rooms_to_adults(cls, model):
        """If rooms not specified, default to number of adults."""
        if model.rooms is None:
            model.rooms = model.adults
        return model
    
# Wrap the LLM with structured output capabilities for TripExtraction
structured_llm = model.with_structured_output(TripExtraction)

# Define the tool
@tool(
    description=(
        "Extracts trip details from a user message. "
        "Returns JSON with origin, destination, departure_date, return_date, "
        "adults, children, infants, and rooms."
    )
)
def extract_travel(message: str) -> str:
    """
    Accepts a raw user message, uses a structured LLM to parse it into
    TripExtraction fields, and returns JSON.
    """
    try:
        trip = structured_llm.invoke(message) 
        print("Using Travel Extraction Tool")
        return json.dumps(trip.dict())
    except Exception as e:
        return json.dumps({"error": f"Extraction failed: {str(e)}"})