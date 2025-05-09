from textwrap import dedent
from typing import cast

from crewai import Agent, Task
from pydantic import BaseModel

from llm.llm_client import gemini_llm_client
from utils.agents import AgentsEnum

CEPH_ORCHESTRATOR = Agent(
    role="Ceph Orchestrator Manager",
    goal="""Decompose user queries and delegate tasks to the appropriate Ceph agents. 
    Available agents:
    - Bug Intelligence Agent
    - Ceph Viz Agent
    - Observability Agent
    User query: {topic}""",
    verbose=True,
    backstory="You are an expert in analyzing Ceph-related queries from users and delegate tasks to the specialized agents.",
    # llm=groq_llm_client("groq/llama3-70b-8192"),
    # llm=groq_llm_client("groq/llama-3.1-8b-instant"),
    # llm=groq_llm_client(),
    # llm=openai_llm_client(),
    llm=gemini_llm_client(),
    allow_delegation=True,
    max_iter=1,
)


class OrchestratorPlan(BaseModel):
    chosen_agents: list[AgentsEnum] = []


def ceph_orchestrator(topic: str):
    agent = Agent(
        role="Ceph Orchestrator Manager",
        goal=dedent(
            """Decompose user queries and delegate tasks to the appropriate Ceph agents in order of how task should be executed. 
                Available agents:
                - Bug Intelligence Agent: Get the bug details for a given bug id
                - Ceph Viz Agent: Get the cluster status
                - Observability Agent: Get the disk occupation, osd status, mds status, mgr status, mon status, pg status, pool status, and pool usage
                - Performance Agent: Get the relevant suggestions on cluster performance tunings
                - Maverick Agent: Get the relevant documentation, support pages, and RedHat Customer Portal (KCS) related to Ceph clusters
                """
        ),
        backstory="You are an expert in analyzing Ceph-related queries from users and delegate tasks to the specialized agents releated to Ceph.",
        llm=gemini_llm_client(),
        allow_delegation=False,
        max_iter=3,
        max_execution_time=40,
        verbose=True,
    )
    task = Task(
        description=dedent(
            f"""Evaluate the user's Ceph-related query and identify 
                which Ceph agents are best suited to address the 
                task. Provide only a list of agent names that should be executed in order.
                Exclude agents who are not relevant to the Ceph context. 
                If no agent is needed, return an empty list.\n\n
                Ceph User Query: {topic}"""
        ),
        expected_output="List of names of relevant Ceph agents from the team or an empty list if no agent is needed.",
        agent=agent,
        output_pydantic=OrchestratorPlan,
    )
    plan = task.execute_sync()

    if plan.pydantic:
        plan.pydantic = cast(OrchestratorPlan, plan.pydantic)
        return plan.pydantic.chosen_agents

    else:
        raise ValueError("Invalid list of agents: {plan.raw}")


if __name__ == "__main__":
    # print(ceph_orchestrator("What is the status of the Ceph cluster?"))
    # print(ceph_orchestrator("What are the bugs in the Ceph cluster?"))
    print(ceph_orchestrator("How to configure the sync modules in multisite?"))
