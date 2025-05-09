from enum import Enum

from crewai import Agent
from crewai.tools.base_tool import Tool as CrewTool

# from crewai.tools import BaseTool as CrewTool
from langchain_core.tools import Tool as LangChainTool


class AgentsEnum(Enum):
    BUG_INTELLIGENCE = "bug_intelligence"
    CEPHVIZ = "cephviz"
    OBSERVABILITY = "observability"
    PERFORMANCE = "performance"
    MAVERICK = "maverick"


class AgentFactory:
    def __init__(self):
        self.agents: dict[AgentsEnum, Agent] = {}

    def get_agent(self, agent_name: AgentsEnum):
        return self.agents[agent_name]

    def add_agent(self, agent_name: AgentsEnum | str, agent: Agent):
        if isinstance(agent_name, str):
            agent_name = AgentsEnum(agent_name)

        self.agents[agent_name] = agent

    def remove_agent(self, agent_name: AgentsEnum | str):
        if isinstance(agent_name, str):
            agent_name = AgentsEnum(agent_name)

        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found")
        del self.agents[agent_name]

    def get_all_agents(self):
        return self.agents

    def get_agent_names(self):
        return [agent_name.value for agent_name in self.agents]


class AgentBuilder:
    @staticmethod
    def create_tools(tool_names: list[str], langchain_tools: list[LangChainTool]):
        return [
            CrewTool.from_langchain(lang_tool)
            for lang_tool in langchain_tools
            if lang_tool.func.__name__ in tool_names
        ]
