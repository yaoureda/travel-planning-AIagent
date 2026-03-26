import os

from langchain_openai import ChatOpenAI
from typing import Any, Dict
import re

_EVAL_LLM = None

def get_eval_llm():
    global _EVAL_LLM
    if _EVAL_LLM is None:
        _EVAL_LLM = ChatOpenAI(
    model=os.getenv("AI_MODEL"),
    base_url=os.getenv("AI_ENDPOINT"),
    api_key=os.getenv("AI_API_KEY"),
    temperature=0
)
    return _EVAL_LLM

def _run_custom_eval(llm: ChatOpenAI, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    try:
        result = llm.invoke(messages).content
        # Parse a score line robustly: accept SCORE: 1, SCORE=1, SCORE: 0.8, etc.
        score_val = 0.0
        parsed = False
        for line in result.split('\n'):
            m = re.search(r"score\s*[:=]\s*([0-9]*\.?[0-9]+)", line, re.IGNORECASE)
            if m:
                score_val = round(float(m.group(1)))
                parsed = True
                break
        
        if not parsed:
            print(f"WARNING: Could not parse SCORE from judge output. Defaulting to 0. Raw output:\n{result}")
            
        return {"score": score_val, "reasoning": result}
    except Exception as e:
        return {"score": 0, "reasoning": f"Eval failed: {str(e)}"}

def evaluate_itinerary_correctness_llm(scenario: Any, agent_response: str) -> Dict[str, Any]:
    """Metric 1: Itinerary Correctness."""
    llm = get_eval_llm()
    
    # Customize the system prompt if the scenario expects a clarification
    if getattr(scenario, "expect_clarification", False):
        system_prompt = """
        You are evaluating a travel planning agent's response.
        The user's prompt was missing critical information (like origin, destination, return date, or budget).
        Score 1 if the agent correctly noticed the missing information and asked the user to clarify instead of assuming or making up details.
        Score 0 if the agent proceeded to build a full itinerary without asking for the required missing information.

        You MUST structure your response exactly like this:
        SCORE: [1 or 0]
        REASONING: [Your detailed explanation of why]"""
    else:
        budget_hint = getattr(scenario, "budget_expectation", "")
        budget_labels = {
            "over": "the trip will likely exceed the user's budget — the agent should explicitly flag this",
            "within": "the trip should fit within the user's budget — the agent should confirm this",
            "mention": "the agent should mention the budget but no specific verdict is required",
        }
        budget_str = f"\n    Budget context: {budget_labels.get(budget_hint, budget_hint)}" if budget_hint else ""
        system_prompt = f"""
        You are evaluating a travel planning agent's final response.
        Score 1 if the response correctly includes: the right destination, correct travel dates, a hotel recommendation, a flight or transport option, and a budget verdict.{budget_str}
        Score 0 if any of these are missing, wrong, or only mentioned in a disclaimer.

        You MUST structure your response exactly like this:
        SCORE: [1 or 0]
        REASONING: [Your detailed explanation of why]"""
        
    user_prompt = f"Inputs (User Request): {scenario.prompt}\n\nOutputs (Agent Response): {agent_response}"
    return _run_custom_eval(llm, system_prompt, user_prompt)

def evaluate_faithfulness_llm(agent_response: str, tool_context: str) -> Dict[str, Any]:
    """Metric 2: Faithfulness (Hallucination Detection)."""
    llm = get_eval_llm()
    system_prompt = """
    You are checking whether a travel itinerary is grounded in real data.
    Score 3 if every flight, hotel, and attraction mentioned in the response can be perfectly traced to the tool outputs.
    Score 2 if there are very minor discrepancies (e.g., slight mismatch in price or time) but the core items are grounded.
    Score 1 if there is a major hallucinated item (e.g., one completely fabricated hotel, flight, or attraction).
    Score 0 if the response is mostly or entirely fabricated.

    You MUST structure your response exactly like this:
    SCORE: [0, 1, 2, or 3]
    REASONING: [Your detailed explanation of why, noting specifically the unsupported items if any]"""
    user_prompt = f"Tool Outputs (Context):\n{tool_context}\n\nAgent's Final Response:\n{agent_response}"
    eval_result = _run_custom_eval(llm, system_prompt, user_prompt)
    
    # Normalize the 0-3 score to 0.0-1.0
    raw_score = eval_result.get("score", 0)
    eval_result["score"] = round(min(raw_score, 3.0) / 3.0, 2)
    eval_result["reasoning"] = f"Raw Score: {raw_score}/3\n" + eval_result.get("reasoning", "")
    
    return eval_result

def evaluate_trajectory_match(actual_tool_calls: list[str], expected_tools: list[str], mode: str = "subset") -> Dict[str, Any]:
    """
    Metric 3: Trajectory Match (Local, Deterministic)
    mode="subset": Scores 1 if all expected tools were called.
    mode="unordered": Scores 1 if exactly the expected tools were called, regardless of order.
    """
    actual_set = set(actual_tool_calls)
    expected_set = set(expected_tools)
    
    if mode == "subset":
        is_match = expected_set.issubset(actual_set)
    else:
        is_match = expected_set == actual_set

    score = 1 if is_match else 0
    missing = list(expected_set - actual_set)
    extra = list(actual_set - expected_set)
    
    reasoning = f"Mode: {mode}\nExpected: {expected_tools}\nActual: {actual_tool_calls}\n"
    if score == 1:
        reasoning += "Result: MATCH."
    else:
        reasoning += f"Result: FAILED. Missing required tools: {missing}. Extra tools used: {extra}."

    return {"score": score, "reasoning": reasoning}

