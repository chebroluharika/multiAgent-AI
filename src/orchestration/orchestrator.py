from textwrap import dedent
from typing import cast

from crewai import Agent, Task

from llm.llm_client import gemini_llm_client
from orchestration.schema import Memory, OrchestratorPlan


def ceph_orchestrator(topic: str, memory: list[Memory]):
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

                5.  **Follow-up & Conversational Queries**:
                    *   If the query is a follow-up or ambiguous on its own (e.g., "what about osd.3?", "how can I fix that?"), you **MUST** use the `Previous Ceph User Queries` to understand the full context before choosing an agent.

                **Agent Roster:**
                - **Ceph Viz Agent**: Overall cluster status.
                - **Observability Agent**: Detailed status of individual components (osd, mds, mgr, mon), placement groups (pg), and storage pools.
                - **Performance Agent**: Performance tuning and optimization suggestions.
                - **Bug Intelligence Agent**: Fetching details for a specific bug ID.
                - **Maverick Agent**: Your expert documentation retriever. Use it for any query that requires finding a procedure, a command, configuration guidance, or architectural information. It's the right choice for all "how-to" and implicit knowledge-seeking questions.

                Your primary task is to decompose the user's query, considering previous conversation history for context, and select the agent(s) in the correct order of execution.
                """
        ),
        backstory="You are an expert in analyzing Ceph-related queries, including follow-up questions. You leverage conversation history to understand user intent and delegate tasks to the appropriate specialized agents.",
        llm=gemini_llm_client(),
        allow_delegation=False,
        max_iter=3,
        verbose=True,
    )
    memory_string = "\n".join(
        [f"User Query: {mem.query}\nBot Response: {mem.response}" for mem in memory]
    )
    task = Task(
        description=dedent(
            f"""Evaluate the user's Ceph-related query, taking into account the conversation history for context.
                Identify which Ceph agents are best suited to address the 
                task. Provide only a list of agent names that should be executed in order.
                Exclude agents who are not relevant to the Ceph context. 
                If no agent is needed, return an empty list.\n\n
                Ceph User Query: {topic}
                Conversation History (Previous User Queries and Bot Responses):
                {memory_string}"""
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
    print(
        ceph_orchestrator(
            "find more bugs related to this product",
            [
                Memory(
                    query="give me bug details for 12345",
                    response="""
Here are the details for bug ID 12345:

*   **Assigned to:** bero@redhat.com
*   **Creator:** shishz@alum.rpi.edu
*   **Product:** Red Hat Linux
*   **Component:** rhs-printfilters
*   **Status:** CLOSED
*   **Resolution:** RAWHIDE
*   **Summary:** ps-to-printer.fpi
*   **Creation Time:** 06/16/2000
*   **Last Change Time:** 10/08/2024
*   **Comments:**
    *   comment\_0:
        *   time: 10/08/2024
        *   creation\_time: 10/08/2024
        *   creator: fluekearehana@gmail.com
        *   bug\_comments: whenever this problem appears, I often play browser game to cool down my mind <https://getawayshootout.io>
        *   comment\_count: 4
    *   comment\_1:
        *   time: 10/08/2024
        *   creation\_time: 10/08/2024
        *   creator: fluekearehana@gmail.com
        *   bug\_comments: whenever this problem appears, I often play browser game to cool down my mind <https://getawayshootout.io>
        *   comment\_count: 4
    *   comment\_2:
        *   time: 10/08/2024
        *   creation\_time: 10/08/2024
        *   creator: fluekearehana@gmail.com
        *   bug\_comments: whenever this problem appears, I often play browser game to cool down my mind <https://getawayshootout.io>
        *   comment\_count: 4
    *   comment\_4:
        *   time: 10/08/2024
        *   creation\_time: 10/08/2024
        *   creator: fluekearehana@gmail.com
        *   bug\_comments: whenever this problem appears, I often play browser game to cool down my mind <https://getawayshootout.io>
        *   comment\_count: 4
""",
                )
            ],
        )
    )
