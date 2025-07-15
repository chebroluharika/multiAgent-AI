from crewai import Agent, Task
from crewai.flow.flow import Flow, listen, start
from crewai.flow.persistence import persist

from llm.llm_client import gemini_llm_client
from orchestration.crew_agents import agent_factory
from orchestration.orchestrator import ceph_orchestrator
from orchestration.schema import CephAgentsState, Memory


def client_outcome_architect(query: str, opinions: str) -> str:
    agent = Agent(
        role="Technical Report Generator",
        goal="Present a cohesive, professional technical report in markdown that answers the user's query using the information from specialist agents, without exposing internal section headings or agent names.",
        backstory=(
            "You are an expert in technical documentation and reporting. Your job is to synthesize the information provided by specialist agents into a single, cohesive, professional markdown report for the user. "
            "You must ensure all relevant technical details and nuances are included, but you should not expose internal section headings such as '[Specialist Name] Opinion' or agent names. "
            "Your report should read as a unified technical answer, not a collection of separate agent outputs."
        ),
        llm=gemini_llm_client(),
        allow_delegation=False,
        max_iter=1,
        verbose=True,
    )

    task = Task(
        description=(
            "You are to construct a cohesive technical report in markdown that answers the user's query using the information provided by specialist agents.\n\n"
            "## Instructions:\n"
            "- **Technical Report Format:** Present the answer as a single, unified technical report in markdown, with clear structure and appropriate headings.\n"
            "- **Title:** Begin with a top-level heading (e.g., '# Ceph Technical Report') and a brief section stating the user's query.\n"
            "- **Cohesive Answer:** Integrate all relevant information from the specialists' opinions into a single, readable technical answer. Do not include any internal section headings such as '[Specialist Name] Opinion' or agent names. Do not show raw agent output blocks or attribution.\n"
            "- **No Omission:** You MUST include all relevant technical details and nuances from the specialists' opinions, but present them as a unified answer.\n"
            "- **No Extra Commentary:** Do NOT add any introductory, transitional, or explanatory text beyond what is needed for a professional technical report.\n"
            "- **If opinions are empty:** If the specialists' opinions are empty, simply state: 'No information was found to answer your query.'\n\n"
            f"## User Query\n{query}\n\n"
            f"## Technical Findings\n{opinions}"
        ),
        expected_output=(
            "A markdown-formatted technical report that provides a single, cohesive answer to the user's query, integrating all relevant information from the specialists' opinions. "
            "The report must not expose internal agent names or section headings, and should read as a unified technical answer."
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

    question = """NVMe GW CLIs are not working. I am getting below error when I run any NVMe GW CLI "failed to connect to all addresses; last error: UNKNOWN: ipv4:10.0.65.114:5500: Failed to connect to remote host: Connection refused"

How to resolve this, and do we have any bugs already reported for this."""

    result = flow.kickoff(inputs={"topic": question})
    print("Question:\n", question, end="\n\n")
    print("Final Answer:\n", result, end="\n\n")
    print(
        "Agents Used:\n",
        "\n".join([f"- {x}" for x in flow.state.chosen_agents]),
        end="\n\n",
    )

    print(f"Flow State:\n{flow.state}", end="\n\n")
