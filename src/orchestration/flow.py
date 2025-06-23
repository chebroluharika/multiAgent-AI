from crewai import Agent, Task
from crewai.flow.flow import Flow, listen, start
from crewai.flow.persistence import persist

from llm.llm_client import gemini_llm_client
from orchestration.crew_agents import agent_factory
from orchestration.orchestrator import ceph_orchestrator
from orchestration.schema import CephAgentsState, Memory


def client_outcome_architect(query: str, opinions: str) -> str:
    agent = Agent(
        role="Response Formatter",
        goal="Format the raw text from specialist agents into a clean, human readable response for the user, with minimal alteration or summarization of the content.",
        backstory="You are a formatting expert. You take raw text and make it look good. You don't change the meaning or content, you just structure it for clarity.",
        llm=gemini_llm_client(),
        allow_delegation=False,
        max_iter=1,
        verbose=True,
    )

    task = Task(
        description=(
            "Your task is to compile the information from 'Specialists' Opinions' into a single response to the 'User Query'.\n\n"
            "**Key Instructions:**\n"
            "- **Present all details:** You MUST present all information from the specialists' opinions. Do not summarize, shorten, or simplify.\n"
            "- **No conversational text:** Do not add introductory sentences like 'Here is the information...'. Get straight to the point.\n"
            "- **Format for clarity:** Structure the final response in a clear and readable way. Use markdown (e.g., headings, lists, bold text) to organize the information.\n"
            "- **Handle empty input:** If the specialists' opinions are empty, simply state: 'No information was found to answer your query.'\n\n"
            f"**User Query:**\n{query}\n\n"
            f"**Specialists' Opinions:**\n{opinions}"
        ),
        expected_output=(
            "The final, formatted response containing all details from the specialists' opinions, structured clearly with markdown. "
            "It should start directly with the information, not with a conversational introduction."
        ),
        agent=agent,
    )

    outcome = task.execute_sync()

    return outcome.raw


class CephAgentsFlow(Flow[CephAgentsState]):
    llm = gemini_llm_client()

    @start()
    def schedule_orchestration(self):
        query = self.state.topic
        memory = self.load_memory()
        chosen_agents = ceph_orchestrator(query, memory)

        self.state.chosen_agents = [agent.value for agent in chosen_agents]

    @listen(schedule_orchestration)
    def conduct_orchestration(self):
        opinions: dict[str, str] = {}
        for agent_name in self.state.chosen_agents:
            try:
                agent = agent_factory.get_agent(agent_name)
                opinion = agent.kickoff(messages=self.state.topic)
                opinions[agent_name] = opinion.raw
                print(f"Usage Metrics: {opinion.usage_metrics}")
            except Exception as e:
                print(f"\nError with {agent_name}: {e}\n")
                continue
        self.state.opinions = opinions

    @listen(conduct_orchestration)
    def generate_client_response(self):
        opinions = "\n\n".join(
            [
                f"{agent_name}: {opinion}"
                for agent_name, opinion in self.state.opinions.items()
            ]
        )

        client_response = client_outcome_architect(self.state.topic, opinions)
        self.state.response = client_response
        self.save_memory()
        return client_response

    @persist(verbose=True)
    def save_memory(self):
        print(f"{self.state.topic = }")
        print(f"{self.state.response = }")

        self.state.memory.append(
            Memory(
                query=self.state.topic,
                response=self.state.response,
                agents=self.state.chosen_agents,
            ).model_dump()
        )

    def load_memory(self):
        return [Memory(**mem) for mem in self.state.memory]

    def clear_memory(self):
        self.state.memory = []


if __name__ == "__main__":
    # Bug Intelligence
    # question = "What is the bug information for bug id 12345 and is it affecting in the cluster 1?"
    # question = "Give me all bugs that mentions issue with ceph-deploy"

    # CephViz
    # question = "What is the status of the cluster 1 and cluster 2?"
    # question = "Give me cluster health of the cluster 1."

    # Observability
    # question = "Give me all disk occupation for cluster 1."

    # Maverick
    # question = "What are sync modules? And give me list of support tickets related to this?"
    # question = "Find all customer portal issues that are labeled as performance"

    # Performance

    flow = CephAgentsFlow()
    flow.state.memory = [
        {
            "query": "give me bug details for 12345",
            "response": """
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
        }
    ]

    question = "find more bugs related to the product mentioned in this bug"

    result = flow.kickoff(inputs={"topic": question})
    print("Question:\n", question, end="\n\n")
    print("Final Answer:\n", result, end="\n\n")
    print(
        "Agents Used:\n",
        "\n".join([f"- {x}" for x in flow.state.chosen_agents]),
        end="\n\n",
    )

    print(f"Flow State:\n{flow.state}", end="\n\n")
