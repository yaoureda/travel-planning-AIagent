# Travel Planning AI Agent

A travel planning chatbot that helps you search for flights and hotels based on your travel dates, destinations, and budget. Built with Python, LangChain, and integrates with flight & hotel APIs.

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

---

## Project structure

```
Travel-Planning-AIagent/
├── app
│   ├── __init__.py
│   ├── agent.py
│   ├── config.py
│   ├── main.py
│   ├── prompts.py
│   ├── st_app.py
│   └── tools
│       ├── __init__.py
│       ├── budget.py
│       ├── extractor.py
│       ├── flights.py
│       └── hotels.py
├── README.md
├── requirements.txt
└── .env_example
```