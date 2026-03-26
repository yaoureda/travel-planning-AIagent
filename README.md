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

## Benchmark Evaluation

This repository now includes an end-to-end evaluation harness in `evals/` to measure planner quality across curated scenarios.

### What it evaluates

- Itinerary correctness (field-level constraint and consistency checks)
- Tool call reliability (usable result rate from captured tool traces)
- Hallucination rate (unsupported claims vs tool outputs from the same run)

### Scenario set

- Default suite: `evals/scenarios_v1.json`
- Count: 20 scenarios (single-city, multi-city, family, tight budget, ambiguous/missing fields)

### Run benchmark

```bash
python -m evals.runner
```

### Run a quick subset

```bash
python -m evals.runner --limit 5
```

### Output artifacts

Each run writes two files to `evals/results/`:

- `benchmark_<timestamp>.json` (raw per-scenario outputs + scores)
- `benchmark_<timestamp>.md` (human-readable report)

The JSON artifact includes captured tool calls and extracted response claims for metric traceability.

### Notes

- The benchmark invokes live LLM/API calls through the planner agent.
- Ensure environment variables in `.env` are configured before running.

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