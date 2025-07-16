# MultiAgent-AI

**Multi-Agent System for Autonomous Ceph Cluster Management**

This project implements an intelligent, multi-agent orchestration system for monitoring, analyzing, and managing Ceph storage clusters using [CrewAI](https://github.com/joaomdmoura/crewAI). At its core, a centralized `CephOrchestrator` agent coordinates a team of specialized agents to perform real-time cluster health checks, bug triage, documentation lookups, performance monitoring, and automated recommendations.

Key Features:
- 🔍 **Cluster Status Evaluation** via CephViz Agent  
- 📊 **Performance & Disk Analysis** via Observability Agent  
- 🐞 **Bug Monitoring** via CephBugAgent (Bugzilla Integration)  
- 📚 **Ceph Docs Lookup** via CephDocAgent  
- 🧠 **Automated Health Recommendations** via CephAdvisor Agent  
- 🤖 **Hierarchical Task Planning** using CrewAI-style orchestration  


🧱 Built With:
- Python, [CrewAI](https://github.com/joaomdmoura/crewAI), LangChain Tools
- Ceph CLI + SSH, Metrics via PostgreSQL, Bugzilla API, Ceph Docs Search

## Support matrix
Python - 3.11

## Installation

1. Install `uv` package manager: https://docs.astral.sh/uv/getting-started/installation/

2. # Initialize and update all git submodules  
```bash
git submodule update --init --recursive
```

3. Sync dependencies:
```bash
uv sync
```

4. Optional - if you want to use python 3.11.x when you have multiple python versions installed.
 ``` bash
 uv venv -p 3.11
 source .venv/bin/activate
 ```

## Get the documentation

```bash
cd src/
uv run scripts/scrape_ceph_documentation.py --branch branch-you-want-to-scrape
```

## Create FAISS index

```bash
cd src/
uv run agents/maverick/src/maverick/backend/parse_documentation.py
```


## Running the backend

```bash
cd src
uv run orchestration/flow.py
```

## Running the frontend

```bash
cd src
uv run streamlit run frontend/app.py
```


# Submodule setup
git submodule add https://github.com/chebroluharika/maverick src/agents/maverick
cd src/agents
uv init --lib maverick

git submodule add https://github.com/chebroluharika/Bug-Intelligence src/agents/bug_intelligence
cd src/agents
uv init --lib bug_intelligence

git submodule add https://github.com/chebroluharika/cephViz src/agents/cephviz
cd src/agents
uv init --lib cephviz
cd cephviz
uv add -r src\cephviz\backend\requirements.txt

git submodule add https://github.com/chebroluharika/observability src/agents/observability
cd src/agents
uv init --lib observability
cd observability
uv add -r src\observability\backend\requirements.txt

git submodule add https://github.com/chebroluharika/perf src/agents/perf
cd src/agents
uv init --lib perf
cd perf
uv add -r src\perf\backend\requirements.txt

