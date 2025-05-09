import json

from crewai import Crew, Process, Task
from crewai.flow.flow import Flow, listen, router, start

from llm.llm_client import groq_llm_client, openai_llm_client
from orchestration.crew_agents import (
    BUG_INTELLIGENCE_AGENT,
    CEPHVIZ_AGENT,
    OBSERVABILITY_AGENT,
)
from orchestration.orchestrator import CEPH_ORCHESTRATOR
from orchestration.tasks import (
    BUG_INTELLIGENCE_TASK,
    CEPHVIZ_TASK,
    OBSERVABILITY_TASK,
)

crew = Crew(
    agents=[
        BUG_INTELLIGENCE_AGENT,
        OBSERVABILITY_AGENT,
    ],
    tasks=[OBSERVABILITY_TASK, BUG_INTELLIGENCE_TASK],
    verbose=True,
    cache=True,
    # max_rpm=3,
    # share_crew=True,
    manager_agent=CEPH_ORCHESTRATOR,
    # manager_llm=openai_llm_client(),
    # manager_llm=groq_llm_client(),
    # chat_llm=openai_llm_client(),
    planning=True,
    memory=True,
    # planning_llm=openai_llm_client(),
    process=Process.hierarchical,
    # function_calling_llm=openai_llm_client(),
)

if __name__ == "__main__":
    datasets = [
        # {"topic": "What is the disk occupation?"},
        {"topic": "What is the bug details for bug id 12345?"},
        # {"topic": "What is the cluster health?"},
    ]

    ## start the task execution process with enhanced feedback
    crew_outputs = crew.kickoff(
        # inputs={"topic": "What is the bug details for bug id 12345?"}
        inputs={"topic": "What is the disk occupation for cluster 1?"}
    )

    print(crew_outputs)

    # Accessing the crew output
    for crew_output in crew_outputs:
        print(f"Raw Output: {crew_output.raw}")
        if crew_output.json_dict:
            print(f"JSON Output: {json.dumps(crew_output.json_dict, indent=2)}")
        if crew_output.pydantic:
            print(f"Pydantic Output: {crew_output.pydantic}")
        print(f"Tasks Output: {crew_output.tasks_output}")
        print(f"Token Usage: {crew_output.token_usage}")
