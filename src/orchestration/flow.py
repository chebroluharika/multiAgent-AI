
from crewai import Agent, Task
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from llm.llm_client import gemini_llm_client
from orchestration.crew_agents import agent_factory
from orchestration.orchestrator import ceph_orchestrator
from utils.agents import AgentsEnum


class CephAgentsState(BaseModel):
    topic: str = ""
    chosen_agents: list[AgentsEnum] = []
    opinions: dict[AgentsEnum, str] = {}
    response: str = ""


def client_outcome_architect(query: str, opinions: str) -> str:
    agent = Agent(
        role="User Response Architect",
        goal="Craft helpful user responses from expert input.",
        backstory="Expert in user service and synthesizing "
        "information to create clear, friendly replies.",
        llm=gemini_llm_client(),
        allow_delegation=False,
        max_iter=2,
        max_execution_time=30,
        verbose=True,
    )

    task = Task(
        description="Generate user response from user query and "
        "expert opinions. The users are Ceph users. If expert opinions are technical and detailed enought you can use it to answer the user query. "
        "Rely on expert input only. If no input, explain to the user why are we not able to help them."
        f"User Query: {query}\nSpecialists opinions: {opinions}",
        expected_output="Friendly, accurate user response or explanation why we are not able to help them.",
        agent=agent,
    )

    outcome = task.execute_sync()

    return outcome.raw


class CephAgentsFlow(Flow[CephAgentsState]):
    llm = gemini_llm_client()

    @start()
    def schedule_orchestration(self):
        query = self.state.topic
        chosen_agents = ceph_orchestrator(query)

        self.state.chosen_agents = chosen_agents

    @listen(schedule_orchestration)
    def conduct_orchestration(self):
        opinions: dict[AgentsEnum, str] = {}
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
        return client_response


if __name__ == "__main__":
    # Bug Intelligence
    # question = "What is the bug information for bug id 12345 and is it affecting in the cluster 1?"

    # CephViz
    # question = "What is the status of the cluster 1 and cluster 2?"
    # question = "Give me cluster health of the cluster 1."

    # Observability
    # question = "Give me all disk occupation for cluster 1."

    # Maverick
    # question = "What are sync modules? And give me list of support tickets related to this?"
    question = "Find all customer portal issues that are labeled as performance"

    # Performance
    # question = "Give me some performanc   e tunables for the cluster 1 in terms of how to handle high throughput workloads?"

    flow = CephAgentsFlow()
    result = flow.kickoff(inputs={"topic": question})

    print("Question:\n", question, end="\n\n")
    print("Final Answer:\n", result, end="\n\n")
    print(
        "Agents Used:\n",
        "\n".join(map(lambda x: f"- {x.value}", flow.state.chosen_agents)),
        end="\n\n",
    )
    print(f"Flow State:\n{flow.state}", end="\n\n")
