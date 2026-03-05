from .agent import agent
from .extractor import extract_travel_info
from datetime import datetime

def calculate_nights(check_in, check_out):
    start = datetime.strptime(check_in, "%Y-%m-%d")
    end = datetime.strptime(check_out, "%Y-%m-%d")
    return (end - start).days

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