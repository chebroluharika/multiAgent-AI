from crewai import Agent
from dotenv import load_dotenv

from agents.bugIntelligence.app import tools as bugintelligence_tools
from agents.CephViz.agent import tools as ceph_tools
from agents.maverick.frontend.ceph_troubleshooting_assistant import (
    tools as maverick_tools,
)
from agents.Observability.backend.agent import tools as observability_tools
from agents.perf.frontend.app import tools as performance_tools
from llm.llm_client import gemini_llm_client
from utils.agents import AgentBuilder, AgentFactory, AgentsEnum

load_dotenv()


BUG_INTELLIGENCE_AGENT = Agent(
    role="Bug Intelligence Agent",
    goal="Get the bug details for a given bug ID",
    verbose=True,
    backstory=("Expert in understanding bug details from Bugzilla"),
    tools=AgentBuilder.create_tools(
        tool_names=["get_bug_details",
                    "get_all_bugs_details_fast"],
        langchain_tools=bugintelligence_tools,
    ),  # type: ignore  # noqa: PGH003
    allow_delegation=False,
    llm=gemini_llm_client(),
    max_iter=3,
)


OBSERVABILITY_AGENT = Agent(
    role="Monitor from Ceph Cluster metrics",
    goal="Get the monitoring metrics of the Ceph cluster",
    verbose=True,
    backstory=(
        "Expert in understanding metrics inside Ceph Cluster and providing suggestion"
    ),
    tools=AgentBuilder.create_tools(
        tool_names=[
            "get_diskoccupation",
            "check_degraded_pgs",
            "check_recent_osd_crashes",
            "get_high_latency_osds",
            "get_ceph_daemon_counts",
        ],
        langchain_tools=observability_tools,
    ),  # type: ignore  # noqa: PGH003
    allow_delegation=False,
    llm=gemini_llm_client(),
    max_iter=3,
)


CEPHVIZ_AGENT = Agent(
    role="Ceph Viz Agent",
    goal="Get the status of the Ceph cluster in detailed format",
    verbose=True,
    backstory=(
        "You are an AI operator responsible for executing tasks on Ceph clusters"
        "and returning detailed, structured summaries of results"
    ),
    tools=AgentBuilder.create_tools(
        tool_names=[
            "get_cluster_status",
            "get_cluster_health",
            "osd_status",
            "list_filesystems",
            "get_filesystem_metadata",
            "get_filesystem_info",
            "list_mds_nodes",
            "get_mds_perf",
            "list_filesystem_clients",
            "get_active_mds",
            "get_filesystem_performance",
            "get_mds_memory_usage",
            "get_cephfs_metadata_pool_usage",
        ],
        langchain_tools=ceph_tools,
    ),  # type: ignore  # noqa: PGH003
    allow_delegation=False,
    # llm=openai_llm_client(),
    # llm=groq_llm_client(),
    llm=gemini_llm_client(),
    max_iter=3,
)


PERFORMANCE_AGENT = Agent(
    role="Performance Agent",
    goal="Get the relevant suggestions on cluster performance tunings",
    verbose=True,
    backstory=(
        "Expert in understanding metrics inside Ceph Cluster and providing suggestions for performance tuning"
    ),
    tools=AgentBuilder.create_tools(
        tool_names=[
            "get_ceph_status",
            "recommend_perf_tunables_low_latency_dbs",
            "recommend_perf_tunables_high_throughput",
            "recommend_perf_tunables_vm_storage",
            "recommend_perf_tunables_big_data",
            "recommend_perf_tunables_object_workloads",
        ],
        langchain_tools=performance_tools,
    ),  # type: ignore  # noqa: PGH003
    allow_delegation=False,
    llm=gemini_llm_client(),
    max_iter=3,
)

MAVERICK_AGENT = Agent(
    role="Maverick Agent",
    goal="Get the relevant documentation, support pages, and RedHat Customer Portal (KCS) related to Ceph clusters and provide the best possible answer to the user query",
    verbose=True,
    backstory=(
        "Expert in finding relevant documentation, support pages, and RedHat Customer Portal (KCS) related to Ceph clusters"
    ),
    tools=AgentBuilder.create_tools(
        tool_names=[
            "search_document",
            "check_kcs",
            "search_support_pages",
        ],
        langchain_tools=maverick_tools,
    ),  # type: ignore  # noqa: PGH003
    allow_delegation=False,
    llm=gemini_llm_client(),
    max_iter=3,
)

agent_factory = AgentFactory()
agent_factory.add_agent(AgentsEnum.CEPHVIZ, CEPHVIZ_AGENT)
agent_factory.add_agent(AgentsEnum.OBSERVABILITY, OBSERVABILITY_AGENT)
agent_factory.add_agent(AgentsEnum.BUG_INTELLIGENCE, BUG_INTELLIGENCE_AGENT)
agent_factory.add_agent(AgentsEnum.MAVERICK, MAVERICK_AGENT)
agent_factory.add_agent(AgentsEnum.PERFORMANCE, PERFORMANCE_AGENT)

if __name__ == "__main__":
    # print(
    #     agent_factory.get_agent(AgentsEnum.BUG_INTELLIGENCE).kickoff(
    #         messages="What is the bug details for bug id 12345?"
    #     )
    # )

    # print(
    #     agent_factory.get_agent(AgentsEnum.CEPHVIZ).kickoff(
    #         messages="What is the cluster status?"
    #     )
    # )

    # print(
    #     agent_factory.get_agent(AgentsEnum.OBSERVABILITY).kickoff(
    #         messages="What is the disk occupation in the cluster?"
    #     )
    # )

    # print(
    #     agent_factory.get_agent(AgentsEnum.PERFORMANCE).kickoff(
    #         messages="What is the performance of the cluster?"
    #     )
    # )

    print(
        agent_factory.get_agent(AgentsEnum.MAVERICK).kickoff(
            messages="How to configure the sync modules in multisite?"
        )
    )
