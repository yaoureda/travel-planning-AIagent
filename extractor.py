import json
from config import model
from prompts import final_template

chain = final_template | model

# Running tests
def run_tests():
    test_descriptions = [
        "I want to travel from Rome to Amsterdam from 2026-09-01 to 2026-09-05. I have a budget of $800.",
        "Book a hotel in Sydney for 5 nights starting from 2026-10-01. I am from Toronto. My budget is $2000.",
        "Looking for accommodation in Madrid from 2026-11-10 to 2026-11-15. I am from Berlin. My budget is $900."
    ]
    for description in test_descriptions:
        result = chain.invoke({"input": description})
        print(f"Input: {description}")
        print("Output:", json.loads(result.content))

#extract_travel_info function to parse user query and return structured travel info as a dictionary
def extract_travel_info(text: str):
    result = chain.invoke({"input": text})
    return json.loads(result.content)