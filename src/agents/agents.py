import os

from crewai import Agent
from crewai.tools.base_tool import Tool
from dotenv import load_dotenv
from pydantic import BaseModel

from CephViz.agent import tools as ceph_tools
from llm.llm_client import groq_llm_client, hf_llm_client
from Observability.backend.agent import tools as observability_tools
from tools.tools import GetClusterHealthTool, GetDiskOccupationTool

load_dotenv()


class ObservabilityModel(BaseModel):
    diskoccupation: str
    nodename: str


## Create a ceph observability agent
observability_agent = Agent(
    role="Monitor from Ceph metrics",
    goal="Get the relevant suggestions based on ceph cluster metrics",
    verbose=True,
    backstory=(
        "Expert in understanding metrics inside Ceph Cluster and providing suggestion"
    ),
    # tools=[Tool.from_langchain(lang_tool) for lang_tool in observability_tools],
    tools=[GetDiskOccupationTool],
    allow_delegation=False,
    llm=hf_llm_client("huggingface/mistralai/Mistral-7B-Instruct-v0.3"),
    # llm=hf_llm_client("huggingface/mistralai/Mistral-7B-Instruct-v0.2"),
    # llm=hf_llm_client(),
    # llm=groq_llm_client("groq/llama3-70b-8192"),
    # llm=groq_llm_client("groq/deepseek-r1-distill-llama-70b"),
)


# creating a management agent
ceph_management_agent = Agent(
    role="Ceph Manager",
    goal="Efficiently manage and respond to all Ceph cluster-related queries",
    verbose=True,
    backstory=(
        "You are an AI operator responsible for executing tasks on Ceph clusters"
        "and returning detailed, structured summaries of results"
    ),
    # tools=[Tool.from_langchain(lang_tool) for lang_tool in ceph_tools],
    tools=[GetClusterHealthTool],
    # llm=llm,
    allow_delegation=False,
    # llm=groq_llm_client("groq/llama3-70b-8192"),
    llm=hf_llm_client(),
)

if __name__ == "__main__":
    print(
        observability_agent.kickoff(
            messages="Disk occupation in the cluster?"
        )
    )

    # print(ceph_management_agent.kickoff("What is the cluster status?"))
