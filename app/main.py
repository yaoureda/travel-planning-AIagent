from .agent import agent
from datetime import datetime


def plan_trip(user_query: str):
    """
    Plan a trip given a user's natural language query.
    The agent now decides when to call the extractor, flights, hotels, and budget tools.
    """
    # Step 1 — build agent input
    agent_input = f"Plan this trip: {user_query}"

    # Step 2 — run the agent
    result = agent.invoke({
        "messages": [("user", agent_input)]
    })

    print("\nFinal plan:")
    print(result["messages"][-1].content)


if __name__ == "__main__":

    query = "I want to travel from Paris to Barcelona from 2026-06-01 to 2026-06-05. I have a budget of $1000."

    plan_trip(query)