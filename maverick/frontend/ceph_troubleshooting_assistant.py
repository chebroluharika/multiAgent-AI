from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.extensions.langchain import WatsonxLLM


from dotenv import load_dotenv
import os, sys

sys.path.append("..")

import json
import streamlit as st # type: ignore
from langchain_community.llms import Ollama # type: ignore
from langchain.chains import ConversationChain # type: ignore
from langchain.memory import ConversationBufferMemory # type: ignore
from streamlit_lottie import st_lottie # type: ignore
from backend.parse_documentation import DocumentParse
from backend.check_kcs import CheckKcs
from backend.ceph_upstream import Upstream
from backend.connect_bugzilla import Bugzilla
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from langchain_community.llms import Ollama



# Load environment variables
load_dotenv("../backend/config/auth.env")
BUGZILLA_URL = os.getenv("BUGZILLA_URL")
BUGZILLA_API_KEY = os.getenv("BUGZILLA_API_KEY")
DOCUMENTATION = os.getenv("DOCUMENTATION")

# if "chat_history" not in st.session_state:
st.session_state.chat_history = []

document_parse = DocumentParse(DOCUMENTATION)
kcs = CheckKcs()
bugzilla = Bugzilla(BUGZILLA_URL, BUGZILLA_API_KEY)
upstream = Upstream()


# Tool Functions
def search_document(query):
    result = document_parse.answer_query(query)
    return result


def check_kcs(query):
    result = kcs.get_results_from_kcs(query)
    return result


def search_bugzilla(query):
    result = bugzilla.search_or_get_bug(query)
    return result


def search_support_pages(label):
    result = upstream.fetch_ceph_issues(label)
    return result


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
    Tool(
        name="Check upstream issues",
        func=search_support_pages,
        description="Search issues in upstream for a given label",
        return_direct=True,  # Ensures the response is directly sent to the user
    ),
    ]

# Memory and LLM
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

generate_params = {GenParams.MAX_NEW_TOKENS: 25}
model = Model(
    model_id = "meta-llama/llama-3-3-70b-instruct",  # Specify the model ID
    credentials={"apikey": "<api_key>", "url":"<url>"},  # Get API key and URL from environment variables
    params=generate_params,  # Set generation parameters
    project_id="project_id",  # Get project ID from environment variables
)

# Wrap the model with WatsonxLLM to use with LangChain
llm = WatsonxLLM(model=model)


# Initialize AI Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,
)


# Load Lottie animations
def load_lottie(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


loading_animation = load_lottie("Octopus.json")  # Replace with your Lottie animation file

# Create a layout with columns for the animation and title
col1, col2 = st.columns([1, 2])  # Adjust column widths as needed


with col1:
    if loading_animation:
        # Welcome animation
        st_lottie(loading_animation, speed=1, height=200, key="chat_animation")

with col2:
    # Streamlit app title
    st.title("🛠️ Ceph Troubleshooting Assistant")


# Initialize LangChain components with Ollama
@st.cache_resource
def load_chain():
    # Create an Ollama instance with the Llama3 model
    llm = Ollama(model="llama3")

    # Create a conversation chain with memory
    memory = ConversationBufferMemory()
    chain = ConversationChain(llm=llm, memory=memory)
    return chain


# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Sidebar for chat history and reset button
with st.sidebar:
    st.header("Chat History")
    # Display chat history in the sidebar
    for i, message in enumerate(st.session_state.messages):
        st.write(f"**{message['role'].title()}:** {message['content']}")

    # Add a reset button
    if st.button("Reset Chat"):
        st.session_state.messages = []
        # chain.memory.clear()
        agent.memory.clear()
        st.rerun()  # Rerun the app to reflect the reset

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What assistant with ceph are you looking today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate a response using LangChain and Ollama
    with st.chat_message("assistant"):
        response = agent.run(prompt)
        st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
