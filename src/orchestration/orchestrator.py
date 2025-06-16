from textwrap import dedent
from typing import cast

from crewai import Agent, Task
from pydantic import BaseModel

from llm.llm_client import gemini_llm_client
from utils.agents import AgentsEnum


class OrchestratorPlan(BaseModel):
    chosen_agents: list[AgentsEnum] = []


def ceph_orchestrator(topic: str):
    agent = Agent(
        role="Ceph Orchestrator Manager",
        goal=dedent(
            """
                You are a master Ceph orchestrator. Your job is to analyze laconic queries from expert Ceph administrators and delegate them to the correct specialist agent. These admins are precise but don't elaborate. You must infer their intent.

                Here is your decision-making logic:

                1.  **Status & Monitoring Queries**:
                    *   For high-level cluster health (e.g., "ceph status", "cluster health"), use `Ceph Viz Agent`.
                    *   For specific component status (e.g., "osd status", "mon status", "pg status"), or resource usage ("disk usage", "pool usage"), use `Observability Agent`.

                2.  **How-To & Configuration Queries**:
                    *   If the query is a direct "how-to" question (e.g., "how to create a user"), use `Maverick Agent`.
                    *   If the query implies a need for procedural documentation or configuration steps, even if not explicitly phrased as "how-to" (e.g., "radosgw multisite sync", "configure logging", "list rbd namespaces"), use `Maverick Agent`. This agent is your go-to for finding commands, procedures, and best practices from docs.

                3.  **Performance Queries**:
                    *   For queries related to performance issues, tuning, or optimization (e.g., "slow writes", "improve read performance", "osd tuning tips"), use `Performance Agent`.

                4.  **Bug-Related Queries**:
                    *   If the query contains a specific bug ID (e.g., "details for bug #12345"), use `Bug Intelligence Agent`.

                **Agent Roster:**
                - **Ceph Viz Agent**: Overall cluster status.
                - **Observability Agent**: Detailed status of individual components (osd, mds, mgr, mon), placement groups (pg), and storage pools.
                - **Performance Agent**: Performance tuning and optimization suggestions.
                - **Bug Intelligence Agent**: Fetching details for a specific bug ID.
                - **Maverick Agent**: Your expert documentation retriever. Use it for any query that requires finding a procedure, a command, configuration guidance, or architectural information. It's the right choice for all "how-to" and implicit knowledge-seeking questions.

                Your primary task is to decompose the user's query and select the agent(s) in the correct order of execution.
                """
        ),
        backstory="You are an expert in analyzing Ceph-related queries from users and delegate tasks to the specialized agents releated to Ceph.",
        llm=gemini_llm_client(),
        allow_delegation=False,
        max_iter=3,
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
