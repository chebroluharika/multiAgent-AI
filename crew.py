import json

from crewai import Crew, Process, Task

from agents import ObservabilityModel, ceph_management_agent, observability_agent
from llm.llm_client import groq_llm_client
from orchestrator.orchestrator import ceph_orchestrator

observability_task = Task(
    description="""Your work is to {topic} on the node asked by the user using the tools given,
                Then use the tools to extract the specific details asked about the {topic} and then return""",
    expected_output="A list of nodename, diskoccupation on the {topic} asked by the user",
    agent=observability_agent,
    output_json=ObservabilityModel,
)

ceph_management_task = Task(
    description="""Your work is to get {topic} on the node asked by the user using the tools given,
                Then use the tools to extract the specific details asked about the {topic} and then return""",
    expected_output="A list of clustername, status on the {topic} asked by the user",
    agent=ceph_management_agent,
)

# Forming the tech-focused crew with some enhanced configurations
crew = Crew(
    agents=[observability_agent, ceph_management_agent],
    tasks=[observability_task, ceph_management_task],
    verbose=True,
    cache=True,
    max_rpm=100,
    share_crew=True,
    manager_agent=ceph_orchestrator,
    manager_llm=groq_llm_client("groq/llama3-70b-8192"),
    chat_llm=groq_llm_client("groq/llama3-70b-8192"),
    # planning=True,
    planning_llm=groq_llm_client("groq/llama3-70b-8192"),
    process=Process.hierarchical,
    function_calling_llm=groq_llm_client("groq/llama3-70b-8192"),
)

if __name__ == "__main__":
    datasets = [
        {"topic": "What is the disk occupation?"},
        # {"topic": "What is the cluster health?"},
    ]

    ## start the task execution process with enhanced feedback
    crew_outputs = crew.kickoff_for_each(inputs=datasets)

    # Accessing the crew output
    for crew_output in crew_outputs:
        print(f"Raw Output: {crew_output.raw}")
        if crew_output.json_dict:
            print(f"JSON Output: {json.dumps(crew_output.json_dict, indent=2)}")
        if crew_output.pydantic:
            print(f"Pydantic Output: {crew_output.pydantic}")
        print(f"Tasks Output: {crew_output.tasks_output}")
        print(f"Token Usage: {crew_output.token_usage}")
