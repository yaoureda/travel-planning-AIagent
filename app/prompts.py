import json
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from .config import model

"""
This file defines the few-shot prompting template for the travel planning agent.
"""

# Defining teaching examples list with input/output pairs
#    - Each example shows a travel query as input
#    - And the corresponding JSON format as output (using json.dumps for formatting)
examples = [
    {
        "input": "I want to travel from Paris to Barcelona from 2026-06-01 to 2026-06-05. I have a budget of $1000.",
        "output": json.dumps({
            "origin": "Paris",
            "destination": "Barcelona",
            "check_in": "2026-06-01",
            "check_out": "2026-06-05",
            "budget": "$1000"
        })
    },
    {
        "input": "Book a hotel in Tokyo for 3 nights starting from 2026-07-10. I am from New York. My budget is $1500.",
        "output": json.dumps({
            "origin": "New York",
            "destination": "Tokyo",
            "check_in": "2026-07-10",
            "check_out": "2026-07-13",
            "budget": "$1500"
        })
    },
    {
        "input": "Looking for accommodation in Berlin from 2026-08-15 to 2026-08-20. I am from London. My budget is $1200.",
        "output": json.dumps({
            "origin": "London",
            "destination": "Berlin",
            "check_in": "2026-08-15",
            "check_out": "2026-08-20",
            "budget": "$1200"
        })
    }
]

# Creating an example template using ChatPromptTemplate.from_messages
#    with ("human", "{input}") and ("ai", "{output}")
example_template = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}")
    ]
)

# 5. Creating a FewShotChatMessagePromptTemplate with the examples
few_shot_template = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_template,
)

# 6. Building a final prompt that includes the few-shot template
final_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that helps users plan their travels."),
        few_shot_template,
        ("human", "{input}")
    ]
)

# Running tests
def run_tests():
    chain = final_template | model

    test_descriptions = [
        "I want to travel from Rome to Amsterdam from 2026-09-01 to 2026-09-05. I have a budget of $800.",
        "Book a hotel in Sydney for 5 nights starting from 2026-10-01. I am from Toronto. My budget is $2000.",
        "Looking for accommodation in Madrid from 2026-11-10 to 2026-11-15. I am from Berlin. My budget is $900."
    ]
    for description in test_descriptions:
        result = chain.invoke({"input": description})
        print(f"Input: {description}")
        print("Output:", json.loads(result.content))