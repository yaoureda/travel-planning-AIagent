# 1. Import required modules
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

# 2. Load environment variables
load_dotenv()

def main():
    system_messages= ["You are a pirate. Answer all questions in pirate speak with 'Arrr!' and nautical terms.",
                      "You are a professional business analyst. Give precise, data-driven answers.",
                      "You are a friendly teacher explaining concepts to 8-year-old children."]
    print("🎭 Using different system Messages\n")

    model = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
    )

    for system_message in system_messages:
        # Using structured messages for better control
        messages = [
            SystemMessage(
                content=system_message
            ),
            HumanMessage(content="What is artificial intelligence?"),
        ]

        response = model.invoke(messages)

        print("🤖 AI Response with:\n")
        print(system_message)
        print(response.content)


if __name__ == "__main__":
    main()