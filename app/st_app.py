import sys
from pathlib import Path

# Add repo root to sys.path so `app` package is resolvable under Streamlit.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from app.agents.planner_agent import agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# A way to have a conversation with the agent on a Streamlit app.

st.set_page_config(page_title="Travel Planner", page_icon="✈️")
st.title("✈️ AI Travel Planner")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(
            content="You are a helpful travel planning assistant. Use tools to find flights, hotels, and estimate trip cost."
        )
    ]

# Display previous conversation
for msg in st.session_state.messages[1:]:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)

def send_request(user_input: str):
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)

    st.session_state.messages.append(HumanMessage(content=user_input))

    # Call agent
    with st.spinner("Planning your trip..."):
        response = agent.invoke({"messages": st.session_state.messages})

    # Display AI response
    ai_text = (
        response["messages"][-1].content
    )
    with st.chat_message("assistant"):
        st.write(ai_text)

    st.session_state.messages.append(AIMessage(content=ai_text))

# Chat input
user_input = st.chat_input("Ask me to plan your trip")

@st.dialog("Request Template")
def fill_template():
    st.write("Fill in the template:")
    origine = st.text_input("Origin...")
    destination = st.text_input("Destination...")
    departure_date = st.date_input("Departure date...")
    return_date = st.date_input("Return date...")
    duraation = st.text_input("Duration...")
    budget = st.text_input("Budget...")
    number_of_travelers = st.text_input("Number of travelers...")
    if st.button("Submit"):
        st.session_state.pending_template_request = (
            f"Plan a trip from {origine if origine else 'N/A'} to {destination if destination else 'N/A'} departing on {departure_date if departure_date else 'N/A'} and returning on {return_date if return_date else 'N/A'}. "
            f"The trip duration is {duraation if duraation else 'N/A'} and the budget is {budget if budget else 'N/A'}. "
            f"There are {number_of_travelers if number_of_travelers else 'N/A'} travelers."
        )
        st.rerun()

with st.sidebar:
    if st.button("Use Template"):
        fill_template()

if user_input:
    send_request(user_input)

if "pending_template_request" in st.session_state:
    req = st.session_state.pending_template_request
    del st.session_state.pending_template_request
    send_request(req)
