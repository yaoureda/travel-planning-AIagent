from langchain.tools import tool
from langchain.agents import create_agent

from ..config import model
from ..tools.flights import search_flights

# Create a subagent
flights_agent = create_agent(model=model, 
                        tools=[search_flights], 
                        system_prompt="You are a helpful assistant that searches for flights using the search_flights tool. " \
                        "Always use the search_flights tool to find flight information when asked about flights.")

# Wrap it as a tool
@tool("flights", description="Search for available flights")
def call_flights_agent(query: str):
    print("Calling flights agent with query:", query)  # Debug statement
    result = flights_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content
