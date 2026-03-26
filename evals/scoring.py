from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from .scenario_schema import Scenario


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "your",
    "trip",
    "plan",
    "flight",
    "hotel",
    "places",
    "visit",
    "budget",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _contains_any(text: str, terms: list[str]) -> bool:
    lowered = _normalize(text)
    return any(_normalize(term) in lowered for term in terms)


def _extract_iso_dates(text: str) -> list[str]:
    return re.findall(r"\b\d{4}-\d{2}-\d{2}\b", text)


def _extract_budget_amount(text: str) -> float | None:
    amounts = re.findall(r"\$\s*(\d+(?:,\d{3})*(?:\.\d+)?)", text)
    if not amounts:
        amounts = re.findall(r"\bbudget\s*(?:is|of|around|only)?\s*(\d+(?:,\d{3})*(?:\.\d+)?)\b", _normalize(text))
    if not amounts:
        return None
    return float(amounts[0].replace(",", ""))


def _extract_primary_destination(text: str) -> str | None:
    match = re.search(r"\bfrom\s+([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+?)(?:\s+from\s+\d{4}-\d{2}-\d{2}|\s+on\s+\d{4}-\d{2}-\d{2}|\s*,|\s*\.)", text)
    if match:
        return match.group(2).strip().lower()

    # Fallback for prompts like "visit Vienna ..."
    match = re.search(r"\bvisit\s+([a-zA-Z\s]+?)(?:\s+from\s+\d{4}-\d{2}-\d{2}|\s+with\s+a\s+budget|\s*,|\s*\.)", text)
    if match:
        return match.group(1).strip().lower()

    return None


def _parse_required_fields(scenario: Scenario) -> dict[str, Any]:
    prompt = scenario.prompt
    lower_prompt = _normalize(prompt)
    dates = _extract_iso_dates(prompt)
    destination = _extract_primary_destination(prompt)
    has_budget = "budget" in lower_prompt or _extract_budget_amount(prompt) is not None

    traveler_markers: dict[str, int] = {}
    for label in ("adult", "adults", "child", "children", "infant", "infants"):
        m = re.search(rf"\b(\d+)\s+{label}\b", lower_prompt)
        if m:
            traveler_markers[label] = int(m.group(1))

    return {
        "dates": dates,
        "primary_destination": destination,
        "has_budget": has_budget,
        "traveler_markers": traveler_markers,
    }


def _token_overlap_supported(claim: str, evidence_text: str) -> bool:
    claim_tokens = [tok for tok in re.findall(r"[a-zA-Z0-9]+", _normalize(claim)) if tok not in STOPWORDS and len(tok) > 2]
    if not claim_tokens:
        return False
    evidence = _normalize(evidence_text)
    matches = sum(1 for token in set(claim_tokens) if token in evidence)
    return matches >= min(2, len(set(claim_tokens)))


def extract_claims(final_response: str) -> list[str]:
    claims: list[str] = []
    for sentence in re.split(r"[\n\.\!]+", final_response):
        sent = sentence.strip()
        if not sent:
            continue
        sent_norm = _normalize(sent)
        if any(key in sent_norm for key in ("flight", "transport", "airline", "hotel", "accommodation")):
            claims.extend(re.findall(r"\$\s*\d+(?:,\d{3})*(?:\.\d+)?", sent))

    for pattern in (
        r"(?im)^.*(?:flight|transport|airline).*$",
        r"(?im)^.*(?:hotel|accommodation).*$",
        r"(?im)^.*(?:places? to visit|attractions?|itinerary).*$",
    ):
        for line in re.findall(pattern, final_response):
            cleaned = line.strip()
            if len(cleaned) > 10:
                claims.append(cleaned)

    return list(dict.fromkeys(claims))


@dataclass
class DimensionScore:
    score: float
    rationale: str
    failures: list[str] = field(default_factory=list)


@dataclass
class ScenarioScore:
    scenario_id: str
    itinerary_correctness: DimensionScore
    tool_call_reliability: DimensionScore
    hallucination_rate: float
    faithfulness_score: float
    overall_score: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def score_scenario(
    scenario: Scenario,
    final_response: str,
    tool_calls: list[dict[str, Any]] | None = None,
) -> ScenarioScore:
    tool_calls = tool_calls or []

    itinerary = score_itinerary_correctness(scenario, final_response)
    reliability = score_tool_call_reliability(tool_calls, final_response)
    hallucination = score_hallucination_rate(final_response, tool_calls)

    faithfulness = round(1.0 - hallucination["rate"], 4)
    overall = round(
        0.45 * itinerary.score + 0.35 * reliability.score + 0.20 * faithfulness,
        4,
    )

    return ScenarioScore(
        scenario_id=scenario.id,
        itinerary_correctness=itinerary,
        tool_call_reliability=reliability,
        hallucination_rate=hallucination["rate"],
        faithfulness_score=faithfulness,
        overall_score=overall,
    )


def score_itinerary_correctness(scenario: Scenario, final_response: str) -> DimensionScore:
    required = _parse_required_fields(scenario)
    failures: list[str] = []
    checks = 0
    passed = 0
    critical_failure = False

    response_lower = _normalize(final_response)

    destination = required["primary_destination"]
    if destination:
        checks += 1
        if destination in response_lower:
            passed += 1
        else:
            failures.append("destination_missing_or_wrong")
            critical_failure = True

    dates = required["dates"]
    if dates:
        checks += 1
        response_dates = _extract_iso_dates(final_response)
        if response_dates:
            passed += 1
        else:
            failures.append("travel_dates_missing")
            critical_failure = True

    if required["has_budget"]:
        checks += 1
        if "budget" in response_lower:
            passed += 1
        else:
            failures.append("budget_missing")

    if required["traveler_markers"]:
        checks += 1
        traveler_hits = 0
        for label, count in required["traveler_markers"].items():
            if str(count) in response_lower and label.rstrip("s") in response_lower:
                traveler_hits += 1
        if traveler_hits > 0:
            passed += 1
        else:
            failures.append("traveler_details_missing")

    checks = max(1, checks)
    score = passed / checks
    if critical_failure:
        score = min(score, 0.5)
        failures.append("critical_consistency_failure")

    score = round(score, 4)
    rationale = "Response satisfies required itinerary fields." if not failures else "Response misses one or more required itinerary fields."
    return DimensionScore(score=score, rationale=rationale, failures=failures)


def score_tool_call_reliability(
    tool_calls: list[dict[str, Any]],
    final_response: str,
) -> DimensionScore:
    failures: list[str] = []
    if not tool_calls:
        return DimensionScore(
            score=0.0,
            rationale="No tool calls were captured.",
            failures=["no_tool_calls_captured"],
        )

    per_tool: dict[str, dict[str, int]] = {}
    usable = 0
    failed = 0

    for call in tool_calls:
        name = str(call.get("tool_name") or "unknown")
        is_usable = bool(call.get("usable_result", False))
        if name not in per_tool:
            per_tool[name] = {"total": 0, "usable": 0}
        per_tool[name]["total"] += 1
        if is_usable:
            usable += 1
            per_tool[name]["usable"] += 1
        else:
            failed += 1

    base = usable / len(tool_calls)
    response_lower = _normalize(final_response)
    mentions_limitation = _contains_any(
        response_lower,
        ["could not", "unavailable", "not found", "limited", "no results", "couldn't"],
    )
    has_partial_plan = _contains_any(response_lower, ["hotel", "flight", "transport", "place", "attraction"])

    bonus = 0.0
    if failed > 0 and mentions_limitation and has_partial_plan:
        bonus = 0.1

    score = round(min(1.0, base + bonus), 4)

    breakdown = {
        tool: round(values["usable"] / values["total"], 4)
        for tool, values in per_tool.items()
        if values["total"] > 0
    }

    if failed > 0 and bonus == 0.0:
        failures.append("failure_without_explicit_recovery")
    if usable == 0:
        failures.append("zero_usable_tool_results")

    rationale = f"Usable tool calls: {usable}/{len(tool_calls)}."
    if breakdown:
        rationale += f" Per-tool: {breakdown}."
    return DimensionScore(score=score, rationale=rationale, failures=failures)


def score_hallucination_rate(
    final_response: str,
    tool_calls: list[dict[str, Any]],
) -> dict[str, Any]:
    claims = extract_claims(final_response)
    evidence_text = "\n".join(str(call.get("output", "")) for call in tool_calls)
    evidence_norm = _normalize(evidence_text)

    if not claims:
        return {
            "rate": 0.0,
            "unsupported_claims": [],
            "supported_claims": [],
        }

    supported: list[str] = []
    unsupported: list[str] = []

    for claim in claims:
        claim_norm = _normalize(claim)
        if claim.startswith("$"):
            is_supported = claim_norm in evidence_norm
        else:
            is_supported = claim_norm in evidence_norm or _token_overlap_supported(claim, evidence_text)

        if is_supported:
            supported.append(claim)
        else:
            unsupported.append(claim)

    rate = round(len(unsupported) / len(claims), 4)
    return {
        "rate": rate,
        "unsupported_claims": unsupported,
        "supported_claims": supported,
    }
