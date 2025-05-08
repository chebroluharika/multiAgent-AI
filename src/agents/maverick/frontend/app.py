import streamlit as st
from dotenv import load_dotenv
import os, sys

sys.path.append("..")

from backend.parse_documentation import DocumentParse
from backend.check_kcs import CheckKcs
from backend.connect_bugzilla import Bugzilla
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from langchain_community.llms import Ollama

# Load environment variables
load_dotenv("../backend/config/auth.env")
BUGZILLA_URL = os.getenv("BUGZILLA_URL")
BUGZILLA_API_KEY = os.getenv("BUGZILLA_API_KEY")

# if "chat_history" not in st.session_state:
st.session_state.chat_history = []

document_parse = DocumentParse()
kcs = CheckKcs()
bugzilla = Bugzilla(BUGZILLA_URL, BUGZILLA_API_KEY)

# Tool Functions
def search_document(query):
    print("DOCUMENT!!!")
    result = document_parse.answer_query(query)
    return result

def check_kcs(query):
    print("KCS!!!!")
    result = kcs.get_results_from_kcs(query)
    return result


def search_bugzilla(query):
    result = bugzilla.search_or_get_bug(query)
    return result

# Define Tools
tools = [
    Tool(
        name="Check the documentation",
        func=search_document,
        description="Searches the document for a given query and returns the best possible result",
        return_direct=True,  # Ensures the response is directly sent to the user
    ),
    Tool(
        name="Check support pages",
        func=check_kcs,
        description="Searches the support pages and returns the best possible results ",
        return_direct=True,  # Ensures the response is directly sent to the user
    ),
    Tool(
        name="Check bugzilla records",
        func=search_bugzilla,
        description="Search bugzilla for a bug or fetch details of a specific bug by ID, summary or keywords",
        return_direct=True,  # Ensures the response is directly sent to the user
    ),
    ]

# Memory and LLM
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
llm = Ollama(model="llama3")

# Initialize AI Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,
)

def process_query (query: str):
    response = agent.run(query)
    st.session_state.chat_history.append((query, response))
    return response


# Streamlit UI
st.set_page_config(page_title="Ceph Troubleshooting Assistant", page_icon="🤖")
st.title("....")


# Chat Interface
# st.subheader("🔑 Login")
# st.session_state.authenticated_user = {"username": "Admin", "role": "Administrator"}
# st.success(f"Welcome!")
# st.rerun()
st.subheader(" AI Assistant for Ceph Product Troubleshoot")
for query, response in st.session_state.chat_history:
    st.write(f"🧑‍💻 You: {query}")
    st.write(f"🤖 Bot: {response}")

prompt = st.chat_input("Type your command (e.g., check documentation, check support pages)...")
if prompt:
    with st.spinner("Processing..."):
        response = process_query(prompt)
        st.write(f"🤖 {response}")
