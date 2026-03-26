import time
from app.agents.planner_agent import agent

query = "I want to travel from Paris to Barcelona from 2026-06-01 to 2026-06-05. I have a budget of $1000."

queries = [
    "I want to travel from Paris to Barcelona from 2026-06-01 to 2026-06-05. I have a budget of $1000.",
    "Plan a trip from New York to Tokyo for 2 people from 2026-07-10 to 2026-07-20. My budget is $3000.",
    "I want to visit Rome from 2026-08-15 to 2026-08-20. I'm traveling alone and my budget is $1500.",
    "Plan a trip from London to Sydney for 4 people from 2026-09-01 to 2026-09-10. My budget is $5000.",
    "I want to travel from Berlin to Amsterdam from 2026-10-05 to 2026-10-10. I have a budget of $800."
]

for i, query in enumerate(queries):
    print(f"\n=== Running Query {i+1} ===")

    start = time.time()
    response = agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    duration = time.time() - start

    #print("=== Agent Response ===")
    #print(f"\n🤖 AI: {response['messages'][-1].content}")

    print(f"\n=== Total Agent Time {i+1} ===")
    print(f"The agent took {duration:.2f} seconds to respond.")
    print(f"=====================\n")