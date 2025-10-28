from crewai import Agent, Task
from crewai.flow.flow import Flow, listen, start
from crewai.flow.persistence import persist

from llm.llm_client import gemini_llm_client
from orchestration.crew_agents import agent_factory
from orchestration.orchestrator import ceph_orchestrator
from orchestration.schema import CephAgentsState, LogEntry, Memory


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

    def add_log(self, level: str, agent_name: str, message: str):
        """Add a log entry to the flow state."""
        log_entry = LogEntry(level=level, agent_name=agent_name, message=message)
        self.state.logs.append(log_entry.model_dump())

    def log_agent_tools(self, agent, agent_name: str):
        """Log the tools available to an agent."""
        if hasattr(agent, "tools") and agent.tools:
            tool_names = []
            for tool in agent.tools:
                if hasattr(tool, "name"):
                    tool_names.append(tool.name)
                elif hasattr(tool, "func") and hasattr(tool.func, "__name__"):
                    tool_names.append(tool.func.__name__)

            if tool_names:
                tools_str = ", ".join(tool_names[:5])  # Show first 5 tools
                if len(tool_names) > 5:
                    tools_str += f" (and {len(tool_names) - 5} more)"
                self.add_log("info", agent_name, f"🔧 Available tools: {tools_str}")

    @start()
    def schedule_orchestration(self):
        query = self.state.topic
        memory = self.load_memory()

        # Log the query being processed
        query_preview = query[:80] + "..." if len(query) > 80 else query
        self.add_log("info", "Orchestrator", f"📝 Processing query: {query_preview}")

        self.add_log("info", "Orchestrator", "Analyzing query and selecting agents...")
        chosen_agents = ceph_orchestrator(query, memory)

        self.state.chosen_agents = [agent.value for agent in chosen_agents]

        if self.state.chosen_agents:
            agents_list = ", ".join(
                [agent.replace("_", " ").title() for agent in self.state.chosen_agents]
            )
            self.add_log(
                "success", "Orchestrator", f"✨ Selected agents: {agents_list}"
            )
        else:
            self.add_log("warning", "Orchestrator", "No agents selected for this query")

    @listen(schedule_orchestration)
    def conduct_orchestration(self):
        opinions: dict[str, str] = {}

        for agent_name in self.state.chosen_agents:
            formatted_agent_name = agent_name.replace("_", " ").title()
            try:
                # Log agent start
                self.add_log(
                    "info", formatted_agent_name, "🤖 Starting agent execution..."
                )

                # Get agent and log details
                agent = agent_factory.get_agent(agent_name)
                agent_role = getattr(agent, "role", formatted_agent_name)

                # Log agent role
                self.add_log("info", formatted_agent_name, f"👤 Role: {agent_role}")

                # Log agent goal
                agent_goal = getattr(agent, "goal", "")
                if agent_goal:
                    if len(agent_goal) > 150:
                        goal_preview = agent_goal[:150] + "..."
                    else:
                        goal_preview = agent_goal
                    self.add_log(
                        "info", formatted_agent_name, f"🎯 Goal: {goal_preview}"
                    )

                # Log available tools
                self.log_agent_tools(agent, formatted_agent_name)

                # Log query being processed
                if len(self.state.topic) > 100:
                    query_preview = self.state.topic[:100] + "..."
                else:
                    query_preview = self.state.topic
                self.add_log("info", formatted_agent_name, f"📝 Query: {query_preview}")

                # Execute the agent
                opinion = agent.kickoff(messages=self.state.topic)
                opinions[agent_name] = opinion.raw

                # Log completion with output preview
                if len(opinion.raw) > 200:
                    output_preview = opinion.raw[:200] + "..."
                else:
                    output_preview = opinion.raw
                self.add_log(
                    "info", formatted_agent_name, f"📊 Output: {output_preview}"
                )

                # Log usage metrics if available
                if hasattr(opinion, "usage_metrics") and opinion.usage_metrics:
                    metrics = opinion.usage_metrics
                    try:
                        if hasattr(metrics, "total_tokens"):
                            self.add_log(
                                "info",
                                formatted_agent_name,
                                f"📊 Tokens used: {metrics.total_tokens}",  # type: ignore
                            )
                        elif isinstance(metrics, dict) and "total_tokens" in metrics:
                            self.add_log(
                                "info",
                                formatted_agent_name,
                                f"📊 Tokens used: {metrics['total_tokens']}",
                            )
                    except Exception:
                        pass  # Skip metrics logging if format is unexpected

                # Log successful completion
                self.add_log(
                    "success", formatted_agent_name, "✅ Agent completed successfully"
                )

            except Exception as e:
                error_msg = str(e)
                print(f"\nError with {agent_name}: {error_msg}\n")
                self.add_log("error", formatted_agent_name, f"❌ Error: {error_msg}")
                continue

        self.state.opinions = opinions

    @listen(conduct_orchestration)
    def generate_client_response(self):
        self.add_log("info", "Report Generator", "📝 Generating final response...")

        # Log how many agent opinions are being synthesized
        num_opinions = len(self.state.opinions)
        self.add_log(
            "info",
            "Report Generator",
            f"📊 Synthesizing {num_opinions} agent opinion(s)",
        )

        opinions = "\n\n".join(
            [
                f"{agent_name}: {opinion}"
                for agent_name, opinion in self.state.opinions.items()
            ]
        )

        client_response = client_outcome_architect(self.state.topic, opinions)
        self.state.response = client_response

        # Log response preview
        if len(client_response) > 150:
            response_preview = client_response[:150] + "..."
        else:
            response_preview = client_response
        self.add_log("info", "Report Generator", f"📄 Response: {response_preview}")

        self.add_log(
            "success", "Report Generator", "✅ Response generated successfully"
        )
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
                logs=self.state.logs,
            ).model_dump()
        )

    def load_memory(self):
        return [Memory(**mem) for mem in self.state.memory]

    def clear_memory(self):
        self.state.memory = []
        self.state.logs = []

    def get_current_logs(self):
        """Get current execution logs."""
        return [LogEntry(**log) for log in self.state.logs]


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
