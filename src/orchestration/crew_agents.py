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
    role="Ceph Bugzilla Specialist",
    goal="Fetch and provide detailed information about a specific Ceph bug from Bugzilla using its ID.",
    verbose=True,
    backstory="You are a specialized agent with deep knowledge of the Ceph Bugzilla tracker. Your sole purpose is to retrieve comprehensive details for any given bug ID, including its status, severity, and history.",
    tools=AgentBuilder.create_tools(
        tool_names=["get_bug_details", "get_all_bugs_details_fast"],
        langchain_tools=bugintelligence_tools,
    ),  # type: ignore  # noqa: PGH003
    allow_delegation=False,
    llm=gemini_llm_client(),
    max_iter=3,
)


OBSERVABILITY_AGENT = Agent(
    role="Ceph Observability Specialist",
    goal="Provide detailed real-time monitoring data for specific Ceph components like OSDs, PGs, and pools. Your focus is on granular metrics, not high-level health.",
    verbose=True,
    backstory="You are an expert in Ceph's monitoring and metrics systems. You can query for specific operational data points, such as disk occupation, degraded PGs, OSD latency, and daemon counts, to help administrators diagnose issues at a granular level.",
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
    role="Ceph Cluster Health Analyst",
    goal="Provide a high-level overview of the Ceph cluster's health and status. You are the first stop for a quick health check.",
    verbose=True,
    backstory="You are an experienced Ceph administrator AI that specializes in providing a bird's-eye view of the cluster's overall status. You answer general health queries like 'what's the cluster status?' to give a quick, comprehensive summary.",
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
    role="Ceph Performance Tuning Expert",
    goal="Analyze Ceph cluster performance and provide actionable tuning recommendations for specific workloads (e.g., low-latency, high-throughput, object storage).",
    verbose=True,
    backstory="You are a seasoned Ceph performance engineer. You have extensive knowledge of Ceph's performance characteristics and can recommend specific configuration changes to optimize for different use cases, from VM storage to big data analytics.",
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
    role="Ceph Documentation and Knowledge Expert",
    goal="Find and retrieve precise information from Ceph documentation, support articles, and knowledge bases to answer 'how-to', configuration, and procedural questions.",
    verbose=True,
    backstory="You are the ultimate Ceph librarian and guide. When an administrator needs to know how to perform a task, configure a feature, or understand a concept, you are the go-to resource. You excel at interpreting terse queries and finding the exact command or procedure they need from the official documentation and support channels.",
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
