from langchain.tools import tool
from langchain.agents import create_agent

from ..config import model
from ..tools.hotels import search_hotels

# Create a subagent
hotels_agent = create_agent(model=model, 
                        tools=[search_hotels], 
                        system_prompt="You are a helpful assistant that searches for hotels using the search_hotels tool. " \
                        "Always use the search_hotels tool to find hotel information when asked about hotels.")

# Wrap it as a tool
@tool("hotels", description="Search for available hotels")
def call_hotels_agent(query: str):
    print("Calling hotels agent with query:", query)  # Debug statement
    result = hotels_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content