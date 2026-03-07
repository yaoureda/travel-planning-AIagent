import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from amadeus import Client

# Load environment variables from .env file
load_dotenv()

# Configuration for AI model
model = ChatOpenAI(
    model=os.getenv("AI_MODEL"),
    base_url=os.getenv("AI_ENDPOINT"),
    api_key=os.getenv("AI_API_KEY"),
    temperature=0
)

# Amadeus API for flight search
amadeus = Client(
    client_id=os.getenv("AMADEUS_CLIENT_ID"),
    client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
)

# SerpAPI for hotel search
SERPAPI_KEY = os.getenv("SERPAPI_KEY")