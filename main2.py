# 1. Import required modules
import json
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain.agents import create_agent

# 2. Load environment variables and create model with temperature 0
load_dotenv()
model = ChatOpenAI(
    model=os.getenv("AI_MODEL"),
    base_url=os.getenv("AI_ENDPOINT"),
    api_key=os.getenv("AI_API_KEY"),
    temperature=0
)

# 3. Define your teaching examples list with input/output pairs
#    - Each example should show a product description as input
#    - And the corresponding JSON format as output (use json.dumps for formatting)
examples = [
    {
        "input": "I want to travel from Paris to Barcelona from 2026-06-01 to 2026-06-05. I have a budget of $1000.",
        "output": json.dumps({
            "origin": "Paris",
            "destination": "Barcelona",
            "check_in": "2026-06-01",
            "check_out": "2026-06-05",
            "budget": "$1000"
        })
    },
    {
        "input": "Book a hotel in Tokyo for 3 nights starting from 2026-07-10. I am from New York. My budget is $1500.",
        "output": json.dumps({
            "origin": "New York",
            "destination": "Tokyo",
            "check_in": "2026-07-10",
            "check_out": "2026-07-13",
            "budget": "$1500"
        })
    },
    {
        "input": "Looking for accommodation in Berlin from 2026-08-15 to 2026-08-20. I am from London. My budget is $1200.",
        "output": json.dumps({
            "origin": "London",
            "destination": "Berlin",
            "check_in": "2026-08-15",
            "check_out": "2026-08-20",
            "budget": "$1200"
        })
    }
]

# 4. Create an example template using ChatPromptTemplate.from_messages
#    with ("human", "{input}") and ("ai", "{output}")
example_template = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}")
    ]
)

# 5. Create a FewShotChatMessagePromptTemplate with your examples
few_shot_template = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_template,
)

# 6. Build a final prompt that includes the few-shot template
final_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that helps users plan their travels."),
        few_shot_template,
        ("human", "{input}")
    ]
)

# 7. Test with new product descriptions and parse the JSON output with json.loads()
chain = final_template | model


# Running tests
def run_tests():
    test_descriptions = [
        "I want to travel from Rome to Amsterdam from 2026-09-01 to 2026-09-05. I have a budget of $800.",
        "Book a hotel in Sydney for 5 nights starting from 2026-10-01. I am from Toronto. My budget is $2000.",
        "Looking for accommodation in Madrid from 2026-11-10 to 2026-11-15. I am from Berlin. My budget is $900."
    ]
    for description in test_descriptions:
        result = chain.invoke({"input": description})
        print(f"Input: {description}")
        print("Output:", json.loads(result.content))

def extract_travel_info(text: str):
    result = chain.invoke({"input": text})
    return json.loads(result.content)

# flight tool
# Flight search tool
class FlightSearchInput(BaseModel):
    """Input for flight search."""

    origin: str = Field(description="City where the trip starts")
    destination: str = Field(description="City where the user wants to travel")
    date: str = Field(description="Departure date in YYYY-MM-DD format")


@tool(args_schema=FlightSearchInput)
def search_flights(origin: str, destination: str, date: str) -> str:
    """Search for available flights between two cities on a specific date."""

    # Mock flight database
    flight_data = [
        {
            "origin": "Paris",
            "destination": "Barcelona",
            "date": "2026-06-01",
            "airline": "Vueling",
            "price": 85
        },
        {
            "origin": "Paris",
            "destination": "Barcelona",
            "date": "2026-06-01",
            "airline": "Air France",
            "price": 120
        },
        {
            "origin": "Rome",
            "destination": "Amsterdam",
            "date": "2026-09-01",
            "airline": "KLM",
            "price": 140
        },
        {
            "origin": "Toronto",
            "destination": "Sydney",
            "date": "2026-10-01",
            "airline": "Qantas",
            "price": 950
        }
    ]

    results = []

    for flight in flight_data:
        if (
            flight["origin"].lower() == origin.lower()
            and flight["destination"].lower() == destination.lower()
            and flight["date"] == date
        ):
            results.append(
                f'{flight["airline"]} flight from {origin} to {destination} on {date}: ${flight["price"]}'
            )

    if not results:
        return f"No flights found from {origin} to {destination} on {date}."

    return "Available flights:\n" + "\n".join(results)

def find_flights_for_trip(user_query: str):

    trip = extract_travel_info(user_query)

    flights = search_flights.invoke({
        "origin": trip["origin"],
        "destination": trip["destination"],
        "date": trip["check_in"]
    })

    print("Trip info:", trip)
    print("\nFlights found:")
    print(flights)

# hotel tool
# Hotel search tool
class HotelSearchInput(BaseModel):
    """Input for hotel search."""

    destination: str = Field(description="City where the hotel is located")
    check_in: str = Field(description="Check-in date in YYYY-MM-DD format")
    check_out: str = Field(description="Check-out date in YYYY-MM-DD format")


@tool(args_schema=HotelSearchInput)
def search_hotels(destination: str, check_in: str, check_out: str) -> str:
    """Search for available hotels in a city for given dates."""

    # Mock hotel database
    hotel_data = [
        {
            "destination": "Barcelona",
            "hotel": "Hotel Barcelona Center",
            "price_per_night": 110,
            "rating": 4.3
        },
        {
            "destination": "Barcelona",
            "hotel": "Hostal BCN Ramblas",
            "price_per_night": 70,
            "rating": 4.0
        },
        {
            "destination": "Amsterdam",
            "hotel": "Amsterdam Canal Hotel",
            "price_per_night": 130,
            "rating": 4.5
        },
        {
            "destination": "Sydney",
            "hotel": "Sydney Harbour Hotel",
            "price_per_night": 180,
            "rating": 4.6
        },
        {
            "destination": "Madrid",
            "hotel": "Madrid Central Hotel",
            "price_per_night": 95,
            "rating": 4.2
        }
    ]

    results = []

    for hotel in hotel_data:
        if hotel["destination"].lower() == destination.lower():
            results.append(
                f'{hotel["hotel"]} in {destination}: ${hotel["price_per_night"]}/night (rating {hotel["rating"]})'
            )

    if not results:
        return f"No hotels found in {destination}."

    return (
        f"Hotels available in {destination} from {check_in} to {check_out}:\n"
        + "\n".join(results)
    )

def find_hotels_for_trip(user_query: str):

    trip = extract_travel_info(user_query)

    hotels = search_hotels.invoke({
        "destination": trip["destination"],
        "check_in": trip["check_in"],
        "check_out": trip["check_out"]
    })

    print("Trip info:", trip)
    print("\nHotels found:")
    print(hotels)

# budget tool
# Trip cost estimation tool
class TripCostInput(BaseModel):
    """Input for estimating the total trip cost."""

    flight_price: float = Field(description="Price of the selected flight")
    hotel_price_per_night: float = Field(description="Price of the hotel per night")
    nights: int = Field(description="Number of nights for the hotel stay")
    budget: float = Field(description="User's total travel budget")


@tool(args_schema=TripCostInput)
def estimate_trip_cost(
    flight_price: float,
    hotel_price_per_night: float,
    nights: int,
    budget: float
) -> str:
    """Estimate the total cost of the trip and compare it with the user's budget."""

    hotel_total = hotel_price_per_night * nights
    total_cost = flight_price + hotel_total

    if total_cost <= budget:
        status = "within budget"
    else:
        status = "over budget"

    return (
        f"Estimated trip cost:\n"
        f"Flight: ${flight_price}\n"
        f"Hotel: ${hotel_price_per_night} x {nights} nights = ${hotel_total}\n"
        f"Total cost: ${total_cost}\n"
        f"Budget: ${budget}\n"
        f"Status: The trip is {status}."
    )

from datetime import datetime

def calculate_nights(check_in, check_out):
    start = datetime.strptime(check_in, "%Y-%m-%d")
    end = datetime.strptime(check_out, "%Y-%m-%d")
    return (end - start).days

def estimate_trip(user_query: str):

    trip = extract_travel_info(user_query)

    nights = calculate_nights(trip["check_in"], trip["check_out"])

    cost = estimate_trip_cost.invoke({
        "flight_price": 120,
        "hotel_price_per_night": 100,
        "nights": nights,
        "budget": float(trip["budget"].replace("$",""))
    })

    print(cost)

# grouping tools and creating agent
tools = [
    search_flights,
    search_hotels,
    estimate_trip_cost
]
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="You are a helpful travel planning assistant. Use the tools to find flights, hotels, and estimate the total cost of a trip."
)

def plan_trip(user_query: str):

    # Step 1 — extract structured travel data
    trip = extract_travel_info(user_query)

    nights = calculate_nights(trip["check_in"], trip["check_out"])
    budget = float(trip["budget"].replace("$", ""))

    print("Extracted trip info:", trip)

    # Step 2 — build agent input
    agent_input = f"""
A user wants to plan a trip.

Origin: {trip["origin"]}
Destination: {trip["destination"]}
Departure date: {trip["check_in"]}
Return date: {trip["check_out"]}
Number of nights: {nights}
Budget: {budget}

Use the available tools to:
1. Find flights
2. Find hotels
3. Estimate the total cost

Then recommend a trip.
"""

    # Step 3 — run the agent
    result = agent.invoke({
        "messages": [("user", agent_input)]
    })

    print("\nFinal plan:")
    print(result["messages"][-1].content)

if __name__ == "__main__":

    query = "I want to travel from Paris to Barcelona from 2026-06-01 to 2026-06-05. I have a budget of $1000."

    plan_trip(query)

