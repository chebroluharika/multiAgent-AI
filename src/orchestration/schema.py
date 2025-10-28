from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AgentsEnum(Enum):
    BUG_INTELLIGENCE = "bug_intelligence"
    CEPHVIZ = "cephviz"
    OBSERVABILITY = "observability"
    PERFORMANCE = "performance"
    MAVERICK = "maverick"


class LogEntry(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    level: str = "info"  # info, success, error, warning
    agent_name: str = ""
    message: str = ""


class Memory(BaseModel):
    query: str = ""
    response: str = ""
    agents: list[str] = []
    logs: list[dict] = []


class CephAgentsState(BaseModel):
    topic: str = ""
    chosen_agents: list[str] = []
    opinions: dict[str, str] = {}
    response: str = ""
    memory: list[dict] = []
    logs: list[dict] = []


class OrchestratorPlan(BaseModel):
    chosen_agents: list[AgentsEnum] = []
