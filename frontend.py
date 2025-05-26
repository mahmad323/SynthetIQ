import os
from dotenv import load_dotenv
import streamlit as st
import requests

load_dotenv()

# --- Page Config ---
st.set_page_config(
    page_title="Multi Purpose AI Agent",
    page_icon="🤖",
    layout="centered"
)

# --- Styles ---
st.markdown("""
    <style>
    .message.user {
        background-color: #e0f7fa;
        padding: 0.8em;
        border-radius: 10px;
        margin-bottom: 1em;
    }
    .message.agent {
        background-color: #f0f4c3;
        padding: 0.8em;
        border-radius: 10px;
        margin-bottom: 1em;
    }
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1em;
        border: 1px solid #ddd;
        border-radius: 10px;
        margin-bottom: 1em;
        background-color: #fafafa;
    }
    </style>
""", unsafe_allow_html=True)

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Header ---
st.title("🤖 SynthetIQ")
st.caption("Multi-turn chat with intelligent AI Agents!")

# --- Sidebar: Agent Definition ---
with st.sidebar:
    st.header("🧠 Configure Your Agent")
    system_prompt = st.text_area(
        "System Prompt",
        placeholder="Define your agent’s personality, behavior, etc.",
        height=100
    )
    
    provider = st.radio("Model Provider", ["Groq", "OpenAI"])
    
    if provider == "Groq":
        selected_model = st.selectbox("Groq Models", ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"])
    elif provider == "OpenAI":
        selected_model = st.selectbox("OpenAI Models", ["gpt-4o-mini"])
        
    allow_web_search = st.checkbox("🌐 Allow Web Search")
    
    if st.button("🧹 Reset Chat"):
        st.session_state.chat_history = []

# --- Chat Interface ---
st.subheader("💬 Chat with Your Agent")

# --- Display Chat History ---
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for i, msg in enumerate(st.session_state.chat_history):
    role = msg["role"]
    content = msg["content"]
    css_class = "user" if role == "user" else "agent"
    st.markdown(f"<div class='message {css_class}'><strong>{role.capitalize()}:</strong><br>{content}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- Input box ---
user_input = st.text_area("Your Message:", height=100, placeholder="Ask anything...")

if st.button("🚀 Send"):
    if user_input.strip():
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Prepare payload
        payload = {
            "model_name": selected_model,
            "model_provider": provider,
            "system_prompt": system_prompt,
            "messages": [msg["content"] for msg in st.session_state.chat_history if msg["role"] == "user"],
            "allow_search": allow_web_search
        }

        # Call backend
        try:
            response = requests.post("http://127.0.0.1:9999/chat", json=payload)
            if response.status_code == 200:
                data = response.json()
                if "error" in data:
                    st.error(f"❌ {data['error']}")
                else:
                    # Add agent response to history
                    st.session_state.chat_history.append({"role": "agent", "content": str(data)})
                    st.experimental_rerun()  # Refresh UI to show new message
            else:
                st.error(f"Server error: {response.status_code}")
        except Exception as e:
            st.error(f"Connection error: {e}")
    else:
        st.warning("Please enter a message before sending.")

# Optional Footer
st.markdown("---")
st.caption("Built with ❤️ using LangGraph + Streamlit.")
