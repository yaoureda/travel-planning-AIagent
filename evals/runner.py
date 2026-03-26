from __future__ import annotations

import argparse
import json
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.planner_agent import agent

from .scenario_schema import Scenario, load_scenarios
from .scoring import ScenarioScore, extract_claims, score_scenario

DEFAULT_SYSTEM_MESSAGE = (
    "You are a helpful travel planning assistant. Use tools to find flights, hotels, "
    "places to visit, and estimate trip cost."
)


@dataclass
class ScenarioRunResult:
    scenario_id: str
    prompt: str
    tags: list[str]
    duration_seconds: float
    final_response: str
    tool_calls: list[dict[str, Any]]
    extracted_claims: list[str]
    score: dict[str, Any]
    error: str | None = None


def _extract_content(msg: Any) -> str:
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

    # Keep calls with missing tool responses visible for reliability accounting.
    for record in pending.values():
        record["output"] = ""
        record["usable_result"] = False
        traces.append(record)

    return traces


def run_single_scenario(scenario: Scenario) -> ScenarioRunResult:
    start = time.perf_counter()
    try:
        response = agent.invoke(
            {
                "messages": [
                    SystemMessage(content=DEFAULT_SYSTEM_MESSAGE),
                    HumanMessage(content=scenario.prompt),
                ]
            }
        )

        messages = response["messages"]
        tool_calls = _extract_tool_traces(messages)
        last_message = messages[-1]
        final_response = _extract_content(last_message)
        claims = extract_claims(final_response)
        scenario_score: ScenarioScore = score_scenario(scenario, final_response, tool_calls)

        return ScenarioRunResult(
            scenario_id=scenario.id,
            prompt=scenario.prompt,
            tags=scenario.tags,
            duration_seconds=round(time.perf_counter() - start, 3),
            final_response=final_response,
            tool_calls=tool_calls,
            extracted_claims=claims,
            score=scenario_score.to_dict(),
        )
    except Exception as exc:
        scenario_score = score_scenario(scenario, "", [])
        return ScenarioRunResult(
            scenario_id=scenario.id,
            prompt=scenario.prompt,
            tags=scenario.tags,
            duration_seconds=round(time.perf_counter() - start, 3),
            final_response="",
            tool_calls=[],
            extracted_claims=[],
            score=scenario_score.to_dict(),
            error=str(exc),
        )


def summarize(results: list[ScenarioRunResult]) -> dict[str, Any]:
    overall = [r.score["overall_score"] for r in results]
    itinerary = [r.score["itinerary_correctness"]["score"] for r in results]
    reliability = [r.score["tool_call_reliability"]["score"] for r in results]
    faithfulness = [r.score["faithfulness_score"] for r in results]
    hallucination = [r.score["hallucination_rate"] for r in results]

    errors = [r for r in results if r.error]

    return {
        "scenario_count": len(results),
        "error_count": len(errors),
        "avg_overall_score": round(statistics.fmean(overall), 4) if overall else 0.0,
        "avg_itinerary_correctness": round(statistics.fmean(itinerary), 4) if itinerary else 0.0,
        "avg_tool_call_reliability": round(statistics.fmean(reliability), 4) if reliability else 0.0,
        "avg_faithfulness_score": round(statistics.fmean(faithfulness), 4) if faithfulness else 0.0,
        "avg_hallucination_rate": round(statistics.fmean(hallucination), 4) if hallucination else 0.0,
        "avg_duration_seconds": round(statistics.fmean([r.duration_seconds for r in results]), 3) if results else 0.0,
        "failed_scenarios": [r.scenario_id for r in errors],
    }


def save_outputs(output_dir: Path, results: list[ScenarioRunResult], summary: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    raw_path = output_dir / f"benchmark_{timestamp}.json"
    markdown_path = output_dir / f"benchmark_{timestamp}.md"

    payload = {
        "generated_at_utc": timestamp,
        "summary": summary,
        "results": [asdict(result) for result in results],
    }
    raw_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Travel Agent Benchmark Report",
        "",
        f"Generated at (UTC): {timestamp}",
        "",
        "## Summary",
        "",
        f"- Scenario count: {summary['scenario_count']}",
        f"- Error count: {summary['error_count']}",
        f"- Avg overall score: {summary['avg_overall_score']}",
        f"- Avg itinerary correctness: {summary['avg_itinerary_correctness']}",
        f"- Avg tool call reliability: {summary['avg_tool_call_reliability']}",
        f"- Avg faithfulness score: {summary['avg_faithfulness_score']}",
        f"- Avg hallucination rate: {summary['avg_hallucination_rate']}",
        f"- Avg duration (s): {summary['avg_duration_seconds']}",
        "",
        "## Per Scenario",
        "",
        "| Scenario | Overall | Itinerary | Reliability | Faithfulness | Hallucination | Tool Calls | Duration(s) | Error |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]

    for result in results:
        s = result.score
        lines.append(
            "| "
            f"{result.scenario_id} | "
            f"{s['overall_score']} | "
            f"{s['itinerary_correctness']['score']} | "
            f"{s['tool_call_reliability']['score']} | "
            f"{s['faithfulness_score']} | "
            f"{s['hallucination_rate']} | "
            f"{len(result.tool_calls)} | "
            f"{result.duration_seconds} | "
            f"{result.error or ''} |"
        )

    markdown_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run travel planner benchmark scenarios.")
    parser.add_argument(
        "--scenario-file",
        default="evals/scenarios_v1.json",
        help="Path to scenario JSON file.",
    )
    parser.add_argument(
        "--output-dir",
        default="evals/results",
        help="Directory where benchmark artifacts are written.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="If > 0, run only the first N scenarios.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scenarios = load_scenarios(args.scenario_file)
    if args.limit > 0:
        scenarios = scenarios[: args.limit]

    results: list[ScenarioRunResult] = []
    for scenario in scenarios:
        result = run_single_scenario(scenario)
        print(
            f"[{result.scenario_id}] score={result.score['overall_score']} "
            f"duration={result.duration_seconds}s error={bool(result.error)}"
        )
        results.append(result)

    summary = summarize(results)
    output_dir = Path(args.output_dir)
    save_outputs(output_dir, results, summary)

    print("\nBenchmark completed.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
