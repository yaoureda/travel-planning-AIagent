from pydantic import BaseModel, Field
from langchain.tools import tool
from ..config import model
from ..prompts import final_template

# Define input schema
class ExtractTravelInput(BaseModel):
    query: str = Field(description="User's natural language travel request")

# Create the tool
@tool(
    args_schema=ExtractTravelInput,
    description="Extracts structured travel information from a user's request as JSON"
)
def extract_travel(query: str) -> str:
    """Use the few-shot chain to parse a natural language query into structured travel info"""
    chain = final_template | model
    result = chain.invoke({"input": query})
    # Return JSON string (not Python dict, because tools should return strings)
    return result.content