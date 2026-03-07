import streamlit as st
from app.agent import agent
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

# Chat input
user_input = st.chat_input("Ask me to plan your trip")

if user_input:

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