# 1. Import required modules
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# 2. Define your search tool using @tool decorator:
#    Sample search data to get you started:
#    {
#      "population of tokyo": "Tokyo has a population of approximately 14 million...",
#      "capital of france": "The capital of France is Paris.",
#      "capital of japan": "The capital of Japan is Tokyo.",
#      "population of new york": "New York City has a population of approximately 8.3 million.",
#      # Add more...
#    }
#
#    Implementation tips:
#    - Create a dict with search results
#    - Convert the query to lowercase
#    - Loop through entries and check if query includes key or key includes query
#    - Return matching result or "No results found"
#
#    Use Pydantic BaseModel for args_schema with:
#    - query: str = Field(description="The search query...")
class SearchInput(BaseModel):
    """Input for search."""

    query: str = Field(description="The search query")

@tool(args_schema=SearchInput)
def search(query: str) -> str:
    """Search for information."""
    # Sample search data
    search_data = {
        "population of tokyo": "Tokyo has a population of approximately 14 million...",
        "capital of france": "The capital of France is Paris.",
        "capital of japan": "The capital of Japan is Tokyo.",
        "population of new york": "New York City has a population of approximately 8.3 million.",
        "capital of morocco": "The capital of Morocco is Rabat.",
        "population of rabat": "Rabat has a population of approximately 1.2 million.",
    }

    query_lower = query.lower()
    for key, value in search_data.items():
        if query_lower in key or key in query_lower:
            return f'Search results for "{query}": {value}'

    return f'Search results for "{query}": No results found.'

# 3. Define your calculator tool using @tool decorator:
#    - Use Python's eval() with restricted builtins for safe expression evaluation
#    - Example: eval(expression, {"__builtins__": {}}, {"abs": abs, ...})
#    - Return result as a string
#    - Handle errors with try/except
#
#    Schema should have:
#    - expression: str = Field(description="The mathematical expression...")
class CalculatorInput(BaseModel):
    """Input for calculator."""

    expression: str = Field(description="The mathematical expression to evaluate")

@tool(args_schema=CalculatorInput)
def calculator(expression: str) -> str:
    """Perform mathematical calculations."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"The result is: {result}"
    except Exception as e:
        return f"Error: {e}"
    
# 4. Create the ChatOpenAI model with your environment variables
load_dotenv()
model = ChatOpenAI(
    model=os.getenv("AI_MODEL"),
    base_url=os.getenv("AI_ENDPOINT"),
    api_key=os.getenv("AI_API_KEY"),
)

# 5. Create agent using create_agent():
#    agent = create_agent(model, tools=[search_tool, calculator_tool])
agent = create_agent(model, tools=[search, calculator])

# 6. Test with multi-step queries in a loop:
#    queries = ["What is the population of Tokyo multiplied by 2?", ...]
#    for query in queries:
#        response = agent.invoke({"messages": [HumanMessage(content=query)]})
#        last_message = response["messages"][-1]
#        print(last_message.content)
queries = [
    "What is the population of Tokyo multiplied by 2?",
    "What is the capital of France?",
    "What is 7 + 3 * 3?",
    "What is the population of New York divided by 2?",
    "What is the capital of Morocco?",
]


for query in queries:
    print(f"Query: {query}")
    response = agent.invoke({"messages": [HumanMessage(content=query)]})
    last_message = response["messages"][-1]
    print(last_message.content)
    print("-" * 50)

# 7. Optional: Display which tools were used:
#    tool_calls = []
#    for msg in response["messages"]:
#        if isinstance(msg, AIMessage) and msg.tool_calls:
#            tool_calls.extend([tc["name"] for tc in msg.tool_calls])
#    print(f"Tools used: {', '.join(set(tool_calls))}")
    tool_calls = []
    for msg in response["messages"]:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            tool_calls.extend([tc["name"] for tc in msg.tool_calls])
    print(f"Tools used: {', '.join(set(tool_calls))}")
    print("=" * 50)
