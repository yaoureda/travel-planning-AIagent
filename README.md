# Travel Planning AI Agent

A travel planning multi-agent system that helps you search for flights and hotels based on your travel dates, destinations, and budget. Built with Python, LangChain, and integrates with flight & hotel APIs.

---

## Features

- **Flight search:** Finds round-trip flight options with prices and airlines from amadeus API.
- **Hotel search:** Retrieves hotels for your travel dates, including price and rating from SERPAPI.
- **Budget-aware:** Considers your travel budget when suggesting options.
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
│   │   └── planner_agent.py
│   ├── config.py
│   ├── main.py
│   ├── st_app.py
│   └── tools
│       ├── __init__.py
│       ├── budget.py
│       ├── extractor.py
│       ├── flights.py
│       └── hotels.py
├── requirements.txt
└── tests
    ├── __init__.py
    ├── test_budget.py
    ├── test_extractor.py
    ├── test_flights.py
    └── test_hotels.py
```