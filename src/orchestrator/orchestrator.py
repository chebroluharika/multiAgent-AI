from crewai import Agent

from llm.llm_client import groq_llm_client, hf_llm_client
from orchestrator.prompts import ORCHESTRATOR_PROMPT

ceph_orchestrator = Agent(
    role="Ceph Orchestrator",
    goal="Decompose user queries and delegate tasks to the appropriate Ceph agents.",
    verbose=True,
    backstory="I analyze Ceph-related queries and delegate tasks to the specialized agents.",
    tools=[],
    # llm=groq_llm_client("groq/llama3-70b-8192"),
    llm=groq_llm_client("groq/llama-3.1-8b-instant"),
    allow_delegation=True,
)
