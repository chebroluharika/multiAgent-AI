# Build context should be the monorepo root:
# docker build -f services/csat-api-be/Dockerfile .

########################################################################
FROM python:3.11-slim as builder

RUN pip install --no-cache-dir uv

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY ./pyproject.toml ./uv.lock ./
COPY ./src/agents ./src/agents
RUN uv sync --frozen


########################################################################
FROM python:3.11-slim as runner

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH"

COPY ./src/ /app/src

EXPOSE 8501

WORKDIR /app/src
CMD ["streamlit", "run", "frontend/app.py", "--server.port", "8501"]
