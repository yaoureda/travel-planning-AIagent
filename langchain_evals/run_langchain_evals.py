import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from langchain_core.messages import SystemMessage, HumanMessage

# Import the actual agent and system prompt
from app.agents.planner_agent import agent
from langchain_evals.scenario_schema import load_scenarios

# Import our new LLM-as-a-judge evaluators
from langchain_evals.evaluators import (
    evaluate_itinerary_correctness_llm,
    evaluate_faithfulness_llm,
    evaluate_trajectory_match
)

def _extract_content(msg: Any) -> str:
    """Safely convert different message content payload shapes to text."""

    content = getattr(msg, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)

def _is_usable_tool_output(text: str) -> bool:
    """Heuristic for whether a tool output is usable for downstream planning."""

    lowered = text.strip().lower()
    if not lowered:
        return False
    failure_markers = (
        "error",
        "failed",
        "no flights found",
        "no hotels found",
        "no places found",
        "no route",
        "not found",
    )
    return not any(marker in lowered for marker in failure_markers)

def _extract_tool_traces(messages: list[Any]) -> list[dict[str, Any]]:
    """Reconstruct tool-call traces from agent message history."""

    pending: dict[str, dict[str, Any]] = {}
    traces: list[dict[str, Any]] = []

    for msg in messages:
        tool_calls = getattr(msg, "tool_calls", None)
        if tool_calls:
            for call in tool_calls:
                call_id = str(call.get("id", ""))
                record = {
                    "tool_call_id": call_id,
                    "tool_name": str(call.get("name", "unknown")),
                    "input": call.get("args", {}),
                    "output": "",
                    "usable_result": False,
                }
                pending[call_id] = record

        cls_name = msg.__class__.__name__.lower()
        if cls_name == "toolmessage":
            tool_call_id = str(getattr(msg, "tool_call_id", ""))
            output = _extract_content(msg)
            tool_name = getattr(msg, "name", "unknown")

            if tool_call_id and tool_call_id in pending:
                record = pending.pop(tool_call_id)
                record["output"] = output
                record["usable_result"] = _is_usable_tool_output(output)
                traces.append(record)
            else:
                traces.append(
                    {
                        "tool_call_id": tool_call_id,
                        "tool_name": str(tool_name),
                        "input": {},
                        "output": output,
                        "usable_result": _is_usable_tool_output(output),
                    }
                )

    for record in pending.values():
        record["output"] = ""
        record["usable_result"] = False
        traces.append(record)

    return traces


DEFAULT_SYSTEM_MESSAGE = f"""

    You are a travel planning assistant. Your goal is to produce a single, ready-to-book travel plan — not a menu of options.

    ## Reasoning & tool use
    - Before calling any tool, reason through the request: identify origin, destination(s), dates, traveler count, and budget.
    - Always call the extractor tool first to normalize trip details.
    - Call subagent tools with the full itinerary — they handle multi-leg decomposition internally.
    - For multi-city trips, search one-way flights between each leg, never round-trips.
    - Call flights and hotels subagents before the places subagent — places must fit the confirmed stay dates.
    - Avoid redundant tool calls. Each tool should be called once with complete information.
    - If the distance between cities does not require a flight, recommend train or other ground transport instead.

    ## Handling missing information
    - If origin city is missing: ask once, then proceed.
    - If return date is missing: ask once, then proceed.
    - If budget is missing: proceed without one and omit the budget verdict section.

    ## Output format
    Return your final response using exactly this structure — no extra sections, no deviations:

    ---
    ### ✈️ Flight(s)
    - **Route**: [Origin] → [Destination]
    - **Option**: [Airline, flight number, departure time, arrival time]
    - **Price**: $[amount] per adult / $[total] total

    ### 🏨 Hotel
    - **Name**: [Hotel name]
    - **Location**: [Neighborhood or address]
    - **Price**: $[amount]/night × [N] nights = $[subtotal]

    ### 📍 Places to visit
    [Day-by-day or thematic list from the places subagent, suggest time to visit each place, taking into account the travel duration estimates that you get from the places agent. 
    For example: "Day 1: Visit the Louvre in the morning at 9:00 AM (2h), then walk 20 minutes to Notre-Dame in the afternoon (1.5h). Day 2: Explore Montmartre and Sacré-Cœur (3h)."]

    ### 💰 Budget verdict
    - Flights: $[amount]
    - Hotel: $[amount]
    - Estimated activities: $[amount]
    - **Total estimated cost: $[amount]**
    - **Budget: $[user budget]**
    - **Verdict**: [Within budget ✅ / Over budget ⚠️ by $X — followed by a one-sentence recommendation]
    ---

    Today's date: {datetime.now().strftime('%Y-%m-%d')}. If no year is given for travel dates, assume the next occurrence.
    """


def run_langchain_evals():
    # Load scenarios - let's run just the first 3 for speed unless you want the full dataset
    scenarios_path = Path("langchain_evals/scenarios_v1.json")
    all_scenarios = load_scenarios(scenarios_path)
    
    # Optional: Slice to say, top 5 scenarios so it doesn't consume too many tokens / time testing.
    scenarios_to_run = all_scenarios[:5] 
    
    results = []
    
    print(f"Starting LangChain complex agent evaluation on {len(scenarios_to_run)} scenarios...")
    
    for idx, scenario in enumerate(scenarios_to_run):
        print(f"\n[{idx + 1}/{len(scenarios_to_run)}] Running Scenario: {scenario.id}")
        start_time = time.perf_counter()
        
        # 1. Execute the Agent
        try:
            state = {
                "messages": [
                    SystemMessage(content=DEFAULT_SYSTEM_MESSAGE),
                    HumanMessage(content=scenario.prompt)
                ]
            }
            
            response = agent.invoke(state, config={"recursion_limit": 100})
            messages = response["messages"]
            
            final_answer = _extract_content(messages[-1])
            raw_traces = _extract_tool_traces(messages)
            
            # Format traces for the judging LLM
            context_str = "\n---\n".join([f"Tool [{t['tool_name']}] Output: {t['output'] if t['output'] else '[tool call failed — no output]'}" for t in raw_traces])
            actual_tools = [t['tool_name'] for t in raw_traces]
            # Per-scenario expected tools (optional) with a sensible default.
            expected_tools = getattr(
                scenario,
                "expected_tools",
                ["extract_travel", "call_flights_agent", "call_hotels_agent", "call_places_agent", "estimate_trip_cost"],
            )
            
            duration = round(time.perf_counter() - start_time, 2)
            print(f"  └ Agent finished in {duration}s. Running Local Evaluators...")
            
            # 2. Run Evaluators
            correctness = evaluate_itinerary_correctness_llm(scenario, final_answer)
            faithfulness = evaluate_faithfulness_llm(final_answer, context_str)
            traj_mode = "unordered" if getattr(scenario, "expect_clarification", False) else "subset"
            efficiency = evaluate_trajectory_match(actual_tools, expected_tools, mode=traj_mode)
            
            scenario_result = {
                "scenario_id": scenario.id,
                "duration_seconds": duration,
                "scores": {
                    "correctness": correctness.get("score"),
                    "faithfulness": faithfulness.get("score"),
                    "trajectory_match": efficiency.get("score")
                },
                "reasoning": {
                    "correctness_rationale": correctness.get("reasoning"),
                    "faithfulness_rationale": faithfulness.get("reasoning"),
                    "trajectory_match_rationale": efficiency.get("reasoning")
                }
            }
            results.append(scenario_result)
            
            print(f"  └ Scores -> Correctness: {scenario_result['scores']['correctness']} | Faithfulness: {scenario_result['scores']['faithfulness']} | Trajectory: {scenario_result['scores']['trajectory_match']}")

        except Exception as e:
            print(f"  └ Error during scenario {scenario.id}: {e}")
            results.append({
                "scenario_id": scenario.id, 
                "error": str(e),
                "scores": {
                    "correctness": 0,
                    "faithfulness": 0,
                    "trajectory_match": 0
                }
            })

    # 3. Save Report & Compute Summaries
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    
    # Compute Medians/Averages
    avg_correctness = 0.0
    avg_faithfulness = 0.0
    avg_trajectory = 0.0
    error_count = 0
    total_count = len(scenarios_to_run)
    for r in results:
        if "error" in r:
            error_count += 1
        if "scores" in r:
            avg_correctness += r["scores"].get("correctness", 0)
            avg_faithfulness += r["scores"].get("faithfulness", 0)
            avg_trajectory += r["scores"].get("trajectory_match", 0)
            
    if total_count > 0:
        avg_correctness /= total_count
        avg_faithfulness /= total_count
        avg_trajectory /= total_count
        
    print("\n=== EVALUATION SUMMARY ===")
    print(f"Total Scenarios Run: {total_count}")
    print(f"Errors: {error_count}/{total_count} (errored scenarios scored as 0)")
    print(f"Average Itinerary Correctness: {avg_correctness:.2f}/1.0")
    print(f"Average Faithfulness: {avg_faithfulness:.2f}/1.0")
    print(f"Average Trajectory Match: {avg_trajectory:.2f}/1.0")
    print("==========================\n")
    
    report_dict = {
        "timestamp": timestamp,
        "total_scenarios": len(scenarios_to_run),
        "summary": {
            "avg_correctness": avg_correctness,
            "avg_faithfulness": avg_faithfulness,
            "avg_trajectory": avg_trajectory
        },
        "results": results
    }
    
    out_dir = Path("langchain_evals")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"eval_report_{timestamp}.json"
    out_file.write_text(json.dumps(report_dict, indent=2))
    print(f"Evaluation complete! Report saved to {out_file}")

if __name__ == "__main__":
    run_langchain_evals()
