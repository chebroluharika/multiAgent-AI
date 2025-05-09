from crewai.tools import tool

from agents.Observability.backend.metrics_operations import (
    get_cluster_health,
    get_diskoccupation,
)


@tool("GetDiskOccupationTool")
def GetDiskOccupationTool(param_topic: str) -> str:
    """Get Disk Occupation Status"""
    print("Get Disk Occupation function called")
    result = get_diskoccupation(param_topic)
    return result


@tool("GetClusterHealthTool")
def GetClusterHealthTool(param_topic: str) -> str:
    """Get Cluster Health Status"""
    print("Get Cluster Health function called")
    result = get_cluster_health(param_topic)
    return result


# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
