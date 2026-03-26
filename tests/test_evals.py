from evals.scenario_schema import load_scenarios
from evals.scoring import score_scenario


def test_load_scenarios_v1_has_expected_size():
    scenarios = load_scenarios("evals/scenarios_v1.json")
    assert len(scenarios) == 20
    assert scenarios[0].id == "S01_single_city_baseline"


def test_score_scenario_core_dimensions_present():
    scenarios = load_scenarios("evals/scenarios_v1.json")
    scenario = scenarios[0]

    response = (
        "Flight from Paris to Barcelona on 2026-06-01 and return on 2026-06-05. "
        "Chosen hotel near city center for 1 adult. "
        "Places to visit: Sagrada Familia and Gothic Quarter. "
        "Estimated total cost: $980. Budget: $1200. Status: within budget. Recommendation: book this plan."
    )
    tool_calls = [
        {
            "tool_name": "extract_travel",
            "usable_result": True,
            "output": '{"origin":"Paris","destination":"Barcelona","departure_date":"2026-06-01","return_date":"2026-06-05","adults":1}',
        },
        {
            "tool_name": "call_flights_agent",
            "usable_result": True,
            "output": "Airline: Vueling, Price: $420, Departure: Paris, Arrival: Barcelona",
        },
        {
            "tool_name": "call_hotels_agent",
            "usable_result": True,
            "output": "Hotel: Casa Bonita, Price: $120/night, Location: Barcelona",
        },
        {
            "tool_name": "call_places_agent",
            "usable_result": True,
            "output": "Places to visit: Sagrada Familia, Gothic Quarter",
        },
    ]

    scored = score_scenario(scenario, response, tool_calls)

    assert scored.overall_score > 0.8
    assert scored.itinerary_correctness.score >= 0.75
    assert scored.tool_call_reliability.score >= 0.9
    assert scored.hallucination_rate < 0.4
    assert scored.faithfulness_score > 0.6


def test_score_scenario_penalizes_missing_destination_and_dates():
    scenarios = load_scenarios("evals/scenarios_v1.json")
    scenario = scenarios[0]

    response = "I selected flights and a hotel. Budget is okay."
    tool_calls = [{"tool_name": "extract_travel", "usable_result": True, "output": "{}"}]

    scored = score_scenario(scenario, response, tool_calls)

    assert scored.itinerary_correctness.score <= 0.5
    assert "critical_consistency_failure" in scored.itinerary_correctness.failures


def test_score_scenario_detects_unsupported_claims_as_hallucinations():
    scenarios = load_scenarios("evals/scenarios_v1.json")
    scenario = scenarios[0]

    response = (
        "Flight from Paris to Barcelona costs $9999. "
        "Hotel Luxury Sky Palace costs $2000/night. "
        "Places to visit include Atlantis Dome."
    )
    tool_calls = [
        {
            "tool_name": "call_flights_agent",
            "usable_result": True,
            "output": "Airline: Vueling, Price: $320",
        },
        {
            "tool_name": "call_hotels_agent",
            "usable_result": True,
            "output": "Hotel: Budget Inn, Price: $90/night",
        },
    ]

    scored = score_scenario(scenario, response, tool_calls)
    assert scored.hallucination_rate > 0.5
    assert scored.faithfulness_score < 0.5
