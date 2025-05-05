import json
from crewai import Crew,Process, Task
from agents import ObservabilityModel, observability_agent, ceph_management_agent
from tools import GetDiskOccupationTool

observability_task = Task(
    description="""Your work is to {topic} on the node asked by the user using the tools given,
                Then use the tools to extract the specific details asked about the {topic} and then return""",
    expected_output="A list of nodename, diskoccupation on the {topic} asked by the user",
    agent=observability_agent,
    tools=[GetDiskOccupationTool],
    output_json=ObservabilityModel,
)

ceph_management_task = Task(
    description="""Your work is to get {topic} on the node asked by the user using the tools given,
                Then use the tools to extract the specific details asked about the {topic} and then return""",
    expected_output="A list of clustername, status on the {topic} asked by the user",
    agent=ceph_management_agent,
    tools=[GetDiskOccupationTool],
)

# Forming the tech-focused crew with some enhanced configurations
crew = Crew(
    agents=[observability_agent, ceph_management_agent],
    tasks=[observability_task, ceph_management_task],
    verbose=True,
    memory=True,
    cache=True,
    max_rpm=100,
    share_crew=True,
    process=Process.sequential,  # Optional: Sequential task execution is default
)

datasets = [
  { 'topic':'Get disk occupation' },
  { 'topic':'Cluster Health' },
]

## start the task execution process with enhanced feedback
crew_outputs=crew.kickoff_for_each(inputs=datasets)

# Accessing the crew output
for crew_output in crew_outputs:
    print(f"Raw Output: {crew_output.raw}")
    if crew_output.json_dict:
        print(f"JSON Output: {json.dumps(crew_output.json_dict, indent=2)}")
    if crew_output.pydantic:
        print(f"Pydantic Output: {crew_output.pydantic}")
    print(f"Tasks Output: {crew_output.tasks_output}")
    print(f"Token Usage: {crew_output.token_usage}")
