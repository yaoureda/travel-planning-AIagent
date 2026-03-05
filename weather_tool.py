# 1. Import required modules
import os
from typing import Literal, Optional
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# 2. Create input schema with Pydantic BaseModel
#    - city: str with Field(description="...")
#    - units: Optional[Literal["celsius", "fahrenheit"]] with default
class WeatherInput(BaseModel):
    """Input for weather tool."""
    city: str = Field(description="The name of the city to get the weather for.")
    units: Optional[Literal["celsius", "fahrenheit"]] = Field(
        default="celsius",
        description="The unit of temperature to return. Can be 'celsius' or 'fahrenheit'. Default is 'celsius'."
    )

# 3. Create a weather tool using the @tool decorator:
#    - Use args_schema parameter to specify the Pydantic model
#    - Implement function to return simulated weather data
#    - Add detailed docstring as the tool description
@tool(args_schema=WeatherInput)
def get_weather(city: str, units: Optional[Literal["celsius", "fahrenheit"]] = "celsius") -> str:
    """Get current weather for a city."""
    temps_celsius = {"Seattle": 62, "Paris": 18, "Tokyo": 24, "London": 14, "Sydney": 26}
    temp_c = temps_celsius.get(city, 20) 

    if units == "fahrenheit":
        temp_f = temp_c * 9/5 + 32
        return f"Current temperature in {city}: {temp_f:.1f}°F, partly cloudy"
    else:
        return f"Current temperature in {city}: {temp_c}°C, partly cloudy"

# 4. Bind the tool to the model using model.bind_tools()
load_dotenv()
model = ChatOpenAI(
    model=os.getenv("AI_MODEL"),
    base_url=os.getenv("AI_ENDPOINT"),
    api_key=os.getenv("AI_API_KEY"),
)
model_with_tools = model.bind_tools([get_weather])

# 5. Implement the 3-step execution pattern:
#    Step 1: Invoke model with user query, check for tool_calls
#    Step 2: Execute the tool with tool.invoke(tool_call["args"])
#    Step 3: Create messages list with HumanMessage, AIMessage, and ToolMessage
#            Then invoke model again for final natural language response
query = "What's the weather in Paris in Celsius?"
response1 = model_with_tools.invoke([HumanMessage(content=query)])  
if not response1.tool_calls or len(response1.tool_calls) == 0:
    print("No tool calls generated")
else:
    tool_call = response1.tool_calls[0]
    tool_result = get_weather.invoke(tool_call["args"])
    messages = [
        HumanMessage(content=query),
        AIMessage(
            content=str(response1.content),
            tool_calls=response1.tool_calls,
        ),
        ToolMessage(
            content=str(tool_result),
            tool_call_id=tool_call["id"],
        ),
    ]
    final_response = model.invoke(messages)
    print("Final response:", final_response.content)