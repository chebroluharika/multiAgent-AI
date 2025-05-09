from crewai import Task
from crewai.tasks.conditional_task import ConditionalTask

from orchestration.crew_agents import (
    BUG_INTELLIGENCE_AGENT,
    CEPHVIZ_AGENT,
    OBSERVABILITY_AGENT,
    ObservabilityModel,
)

BUG_INTELLIGENCE_TASK = Task(
    description="""
    Input task: {topic}
    Your work is to get the bug details for the bug id asked by the user using the tools given,
    Then use the tools to extract the specific details asked about the bug id and then return""",
    expected_output="A list of bug details for the bug id asked by the user",
    agent=BUG_INTELLIGENCE_AGENT,
    # condition=TaskInputCondition(
    #     condition=lambda x: "bug" in x["topic"],
    #     true_task=BUG_INTELLIGENCE_TASK,
    #     false_task=OBSERVABILITY_TASK,
    # ),
)


OBSERVABILITY_TASK = Task(
    description="""
    Input task: {topic}
    Using correct tools, get the relevant suggestions based on ceph cluster metrics""",
    expected_output="A list of nodename, diskoccupation on the {topic} asked by the user",
    agent=OBSERVABILITY_AGENT,
    output_json=ObservabilityModel,
)

CEPHVIZ_TASK = Task(
    description="""
    Input task: {topic}
    Your work is to perform the input task on the node asked by the user using the tools given,
    Then use the tools to extract the specific details asked about the node and then return""",
    expected_output="A list of clustername, status on the {topic} asked by the user",
    agent=CEPHVIZ_AGENT,
)
