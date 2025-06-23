from enum import Enum

from pydantic import BaseModel


class AgentsEnum(Enum):
    BUG_INTELLIGENCE = "bug_intelligence"
    CEPHVIZ = "cephviz"
    OBSERVABILITY = "observability"
    PERFORMANCE = "performance"
    MAVERICK = "maverick"


class Memory(BaseModel):
    query: str = ""
    response: str = ""
    agents: list[str] = []


class CephAgentsState(BaseModel):
    topic: str = ""
    chosen_agents: list[str] = []
    opinions: dict[str, str] = {}
    response: str = ""
    memory: list[dict] = []


class OrchestratorPlan(BaseModel):
    chosen_agents: list[AgentsEnum] = []
