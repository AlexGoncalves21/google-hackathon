# Repository Map

## Project Root

The root of `google-hackathon` contains these notable files and directories:

- `README.md`: Main project walkthrough.
- `client_agent/`: Gemini Enterprise-facing client agent project.
- `github_agent/`: MCP-backed specialist agent service.
- `docs/knowledge_base/`: This mock documentation corpus for retrieval.

## `github_agent/`

### Files

- `github_agent/README.md`
- `github_agent/Makefile`
- `github_agent/pyproject.toml`
- `github_agent/.env.example`
- `github_agent/github_agent/__init__.py`
- `github_agent/github_agent/agent.py`

### Purpose

This folder is intended to contain the specialist GitHub agent that connects to
the GitHub MCP server and exposes an A2A interface.

## `client_agent/`

This is a standalone app at the repo root.

### Top-Level Files

- `client_agent/README.md`
- `client_agent/pyproject.toml`
- `client_agent/Makefile`
- `client_agent/.env.example`
- `client_agent/.gitignore`

### `client_agent/app/`

Important files:

- `client_agent/app/agent.py`: Main client agent logic.
- `client_agent/app/agent_engine_app.py`: Agent Engine wrapper.
- `client_agent/app/app_utils/deploy.py`: Deployment utilities.
- `client_agent/app/app_utils/telemetry.py`: Telemetry setup.
- `client_agent/app/app_utils/typing.py`: Feedback and shared typing helpers.

### Local Generated Files

During local development, `client_agent/` may also contain ignored files such
as:

- `client_agent/.env`
- `client_agent/deployment_metadata.json`
- `client_agent/uv.lock`

## File Relationship Summary

### User-Facing Project Docs

- `README.md`
- `github_agent/GITHUB_AGENT_GUIDE.md`

### Client Runtime Path

- `client_agent/app/agent.py`
- `client_agent/app/agent_engine_app.py`

### GitHub Specialist Runtime Path

- `github_agent/github_agent/agent.py`

## Important Relative Paths for Retrieval

These paths are likely to appear in user questions:

- `github_agent/github_agent/agent.py`
- `client_agent/app/agent.py`
- `client_agent/app/agent_engine_app.py`
- `client_agent/.env.example`
- `github_agent/.env.example`
- `client_agent/pyproject.toml`
- `github_agent/pyproject.toml`
