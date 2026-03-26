# Travel Planning AI Agent

A travel planning multi-agent system that helps you search for flights and hotels based on your travel dates, destinations, and budget. Built with Python, LangChain, and integrates with flight & hotel APIs.

---

## Features

- **Flight search:** Finds round-trip flight options with prices and airlines from amadeus API.
- **Hotel search:** Retrieves hotels for your travel dates, including price and rating from SERPAPI.
- **Budget-aware:** Considers your travel budget when suggesting options.
- **Places-to-visit planning:** Finds top touristic attractions and suggests a visit plan.
- **Travel duration lookup:** Estimates travel time between places in destination cities using SerpApi.
- **Interactive Chatbot:** Ask for trips in natural language, get structured results.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yaoureda/travel-planning-AIagent.git
cd travel-planning-AIagent
```

2. Create a .env file, paste in it the code from .env_example, and fill in this file your personal API keys.
For amadeus API: https://developers.amadeus.com/signin/external
For SERPAPI API: https://serpapi.com/

3. Create and activate a virtual environment:
**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> This creates a folder named `venv` in your project directory.

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the streamlit app:
```bash
python -m streamlit run app/st_app.py
```

Or run the main.py file:
```bash
python -m app.main
```

Example query to ask the chatbot:
"I want to travel from Paris to Barcelona from 2026-06-01 to 2026-06-05. I have a budget of $1000."

---

## Running tests

Run :
```bash
pytest
```

---

## Agent Evaluation With LangChain Evals

This repository includes an end-to-end evaluation harness in `langchain_evals/` to measure the agent's quality, efficiency, and safety across curated scenarios using an LLM-as-a-judge approach.

### What it evaluates

The evaluation measures three key metrics for each scenario:
- **Correctness (`evaluate_itinerary_correctness_llm`)**: Evaluates whether the generated itinerary accurately follows the scenario's constraints (e.g., correct dates, locations, within budget).
- **Faithfulness (`evaluate_faithfulness_llm`)**: Checks for hallucinations by ensuring the agent's final recommendations are consistently supported by the actual outputs returned from the API tools during the execution.
- **Trajectory Match (`evaluate_trajectory_match`)**: Examines the internal trace of the agent to identify whether it used the expected tools (e.g., flight tools, hotel tools, places tools) efficiently without wasting steps or missing crucial tool calls.

### Scenarios

- Default suite: `langchain_evals/scenarios_v1.json`
- Tests varying complexities: simple single-city plans, multi-city round trips, missing trip parameters (prompting clarification), and tight budgets.

### Run evaluation

```bash
python -m langchain_evals.run_langchain_evals
```

### Output artifacts

At the end of the evaluation run, summary metrics are printed to the console (showing Average Correctness, Faithfulness, and Trajectory Match). 
A comprehensive JSON report containing raw per-scenario inputs, expected properties, agent responses, extracted tool traces, and evaluator rationales is saved to:
- `langchain_evals/eval_report_<timestamp>.json`

### Notes

- The benchmark runs the complex graph agent and invokes live LLM and API calls. Ensure your `.env` variables are correctly configured.
- If the agent throws a `GRAPH_RECURSION_LIMIT` error, the execution was likely too complex to resolve within minimal steps. The script overrides the standard limit, giving the agent a recursion depth up to 100 steps.

---

## Project structure

```
Travel-Planning-AIagent/
├── README.md
├── app
│   ├── __init__.py
│   ├── agents
│   │   ├── __init__.py
│   │   ├── flights_agent.py
│   │   ├── hotels_agent.py
│   │   ├── places_agent.py
│   │   └── planner_agent.py
│   ├── config.py
│   ├── main.py
│   ├── st_app.py
│   └── tools
│       ├── __init__.py
│       ├── budget.py
│       ├── extractor.py
│       ├── flights.py
│       ├── hotels.py
│       ├── places.py
│       └── travel_duration.py
├── langchain_evals
│   ├── __init__.py
│   ├── evaluators.py
│   ├── run_langchain_evals.py
│   ├── scenario_schema.py
│   └── scenarios_v1.json
├── requirements.txt
└── tests
    ├── __init__.py
    ├── test_budget.py
    ├── test_extractor.py
    ├── test_flights.py
    ├── test_hotels.py
    ├── test_places.py
    └── test_travel_duration.py
```