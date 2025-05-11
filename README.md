# MultiAgent-AI

## Installation

Install `uv` package manager: https://docs.astral.sh/uv/getting-started/installation/

Sync dependencies:
```bash
uv sync
```

## Get the documentation

```bash
cd src/
uv run scripts/scrape_ceph_documentation.py
```

## Create FAISS index

```bash
cd src/
uv run agents/maverick/backend/parse_documentation.py
```

## Running the code

```bash
cd src
uv run orchestration/flow.py
```