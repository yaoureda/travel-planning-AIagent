from .agents.planner_agent import agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

"""
A way to have a conversation with the agent in the terminal. 
Tap "quit" to end it.
"""

def plan_trip():
    """
    Plan a trip given a user's natural language query.
    The agent decides when to call the extractor, flights, hotels, and budget tools.
    """
    print("🤖 AI: Hello! I'm a travel planning assistant. You can ask me to plan trips for you.")
    # Initialize conversation history list with a SystemMessage for personality
    messages = [
        SystemMessage(content="You are a helpful travel planning assistant. Use the tools to find flights, hotels, and estimate the total cost of a trip."),
    ]

    human_message = str(input("You:"))
    messages.append(HumanMessage(content=human_message))

    # Keep the conversation going until the user types "quit"
    while messages[-1].content.lower() != "quit":

        response = agent.invoke({"messages": messages})

        print(f"\n🤖 AI: {response['messages'][-1].content}")
        messages.append(AIMessage(content=str(response['messages'][-1].content)))

        human_message = str(input("You:"))
        messages.append(HumanMessage(content=human_message))

    print(f"👋 Goodbye! We had {len(messages)-1} messages in our conversation.")


if __name__ == "__main__":
    #Example query = "I want to travel from Paris to Barcelona from 2026-06-01 to 2026-06-05. I have a budget of $1000."
    plan_trip()