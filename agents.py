from crewai import Agent, LLM
from langchain_community.llms import Ollama

from dotenv import load_dotenv
from tools import GetClusterHealthTool, GetDiskOccupationTool
from pydantic import BaseModel

load_dotenv()

import os

class ObservabilityModel(BaseModel):
    diskoccupation: str
    nodename: str
    
# if we want to use local models with Ollama
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# os.environ["OPENAI_MODEL_NAME"] = "ollama/llama3.2"
# os.environ["OPENAI_API_BASE"] = "http://localhost:11434"
# llm=LLM(model="ollama/llama3.2", base_url="http://localhost:11434")


# if we want to use groq
# os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
# GROQ_API_KEY = "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"
# os.environ["OPENAI_API_KEY"] = GROQ_API_KEY
# os.environ["OPENAI_MODEL_NAME"] = "llama3-70b"



## Create a ceph observability agent
observability_agent=Agent(
    role='Monitor from Ceph metrics',
    goal='Get the relevant suggestions based on ceph cluster metrics',
    verbose=True,
    memory=True,
    backstory=(
       "Expert in understanding metrics inside Ceph Cluster and providing suggestion" 
    ),
    tools=[GetDiskOccupationTool],
    # llm=llm,
    allow_delegation=False
)

# creating a management agent
ceph_management_agent=Agent(
    role='Ceph Manager',
    goal='Efficiently manage and respond to all Ceph cluster-related queries',
    verbose=True,
    memory=True,
    backstory=(
        "You are an AI operator responsible for executing tasks on Ceph clusters" 
        "and returning detailed, structured summaries of results"
    ),
    tools=[GetClusterHealthTool],
    # llm=llm,
    allow_delegation=False
)