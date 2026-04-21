FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

RUN pip install --no-cache-dir uv==0.8.13

COPY pyproject.toml uv.lock README.md ./
COPY github_agent ./github_agent
COPY skills ./skills

RUN uv sync --frozen --no-dev

EXPOSE 8080

CMD ["uvicorn", "github_agent:a2a_app", "--host", "0.0.0.0", "--port", "8080"]
