# 1. Import required modules
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
import os

# 2. Load environment variables
load_dotenv()

# 3. Create the ChatOpenAI model
model = ChatOpenAI(
    model=os.getenv("AI_MODEL"),
    base_url=os.getenv("AI_ENDPOINT"),
    api_key=os.getenv("AI_API_KEY")
)

print("🤖 Chatbot: Hello! I'm your helpful assistant. Ask me anything!")
# 4. Initialize conversation history list with a SystemMessage for personality
messages = [
    SystemMessage(content="You are a helpful assistant."),
]

human_message = str(input("You:"))
messages.append(HumanMessage(content=human_message))

while messages[-1].content != "quit":

    response = model.invoke(messages)
    print(f"\n🤖 AI: {response.content}")
    messages.append(AIMessage(content=str(response.content)))

    human_message = str(input("You:"))
    messages.append(HumanMessage(content=human_message))

print(f"👋 Goodbye! We had {len(messages)-1} messages in our conversation.")
