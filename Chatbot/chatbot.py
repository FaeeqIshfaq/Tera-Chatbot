from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Tera Chatbot", layout="centered")
st.title("🦙😏🤪 Tera Chatbot")

# ----------------- Style -----------------
st.markdown("""
    <style>
    .stTextInput>div>div>input {
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- Auto Topic Function -----------------
def generate_topic(chat_history):
    for role, msg in chat_history:
        if role == "user":
            return msg[:30] + "..." if len(msg) > 30 else msg
    return "Untitled Chat"

# ----------------- State Init -----------------
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_session" not in st.session_state:
    st.session_state.current_session = ""

if st.session_state.current_session not in st.session_state.chat_sessions:
    st.session_state.chat_sessions[st.session_state.current_session] = {
        "title": "Untitled Chat",
        "history": [("system", "You are a helpful AI assistant. Please respond to the user's queries clearly and concisely.")]
    }

# Access session info
current_session = st.session_state.current_session
chat_data = st.session_state.chat_sessions[current_session]
chat_history = chat_data["history"]

# ----------------- Sidebar -----------------
st.sidebar.title("💬 Chat History")

for session_name, session_data in st.session_state.chat_sessions.items():
    title = session_data["title"]
    button_label = f"{session_name} - {title}"
    if st.sidebar.button(button_label, key=session_name):
        st.session_state.current_session = session_name
        st.rerun()

if st.sidebar.button("➕ New Chat"):
    new_name = f"Chat {len(st.session_state.chat_sessions) + 1}"
    st.session_state.chat_sessions[new_name] = {
        "title": "Untitled Chat",
        "history": [("system", "You are a helpful AI assistant. Please respond to the user's queries clearly and concisely.")]
    }
    st.session_state.current_session = new_name
    st.rerun()

if st.sidebar.button("🗑️ Clear This Chat"):
    chat_data["history"] = [("system", "You are a helpful AI assistant. Please respond to the user's queries clearly and concisely.")]
    chat_data["title"] = "Untitled Chat"
    st.rerun()

# ----------------- Show Topic -----------------
st.markdown(f"### 🧠 Topic: `{chat_data['title']}`")

# ----------------- Model Setup -----------------
temperature = st.slider("🔧 Set Model Temperature", 0.0, 1.0, 0.7)
llm = Ollama(model="deepseek-r1:1.5b", temperature=temperature)
output_parser = StrOutputParser()

# ----------------- Show Chat -----------------
for role, message in chat_history:
    if role == "user":
        st.markdown(f"**🧍 You:** {message}")
    elif role == "assistant":
        st.markdown(f"**🤖 Bot:** {message}")

# ----------------- Input -----------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("💬 Type your message", key="user_input")
    submitted = st.form_submit_button("Send")

# ----------------- Response Logic -----------------
if submitted and user_input:
    chat_history.append(("user", user_input))

    # Auto-generate topic on first user message
    if chat_data["title"] == "Untitled Chat":
        chat_data["title"] = generate_topic(chat_history)

    prompt = ChatPromptTemplate.from_messages(chat_history)
    chain = prompt | llm | output_parser

    with st.spinner("🤔 Sochny De Bhai..."):
        try:
            response = chain.invoke({})
            chat_history.append(("assistant", response))
        except Exception as e:
            chat_history.append(("assistant", f"Error: {e}"))

    st.rerun()
