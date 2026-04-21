---
name: adk-agent-conventions
description: 'Verify Google ADK agent implementations follow project conventions for A2A communication, MCP toolset usage, Agent Engine deployment, and telemetry.'
---

# ADK Agent Conventions

Review an ADK agent implementation against the architectural conventions of this project, covering A2A communication, MCP integration, Agent Engine deployment, and observability.

## Process

1. **Verify Agent Card definition**:
   - An `AgentCard` object is defined with `name`, `description`, `version`, and `skills`
   - The card is served at `/.well-known/agent-card.json` via the A2A app
   - Protocol version is `0.3.0` and I/O modes include `text/plain`
   - Skill entries have `id`, `name`, and `description` matching actual capabilities

2. **Check MCPToolset configuration**:
   - `MCPToolset` is initialized with the correct GitHub MCP endpoint: `https://api.githubcopilot.com/mcp/`
   - Authentication uses `SseServerParams` with `GITHUB_PERSONAL_ACCESS_TOKEN` from environment
   - Only necessary tools are loaded — avoid wildcard tool inclusion
   - Acceptable tools: `search_repositories`, `search_issues`, `list_issues`, `get_pull_request`, `get_pull_request_diff`, `list_pull_request_files`

3. **Validate environment variable usage**:
   - All secrets come from `os.environ` or `load_dotenv()` — never hardcoded
   - Required vars present in `.env.example`: `GITHUB_PERSONAL_ACCESS_TOKEN`, `MODEL_NAME`, `GITHUB_AGENT_URL`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `GOOGLE_GENAI_USE_VERTEXAI`
   - `.env` is in `.gitignore`

4. **Review delegator pattern (client agent)**:
   - `RemoteA2aAgent` is initialized with `agent_card` fetched from `{GITHUB_AGENT_URL}/.well-known/agent-card.json`
   - `root_agent` uses `Agent` with clear `instruction` string describing its delegation behavior
   - Stub/fallback mode exists for local development when specialist is unavailable

5. **Check A2A server export**:
   - Specialist service exports `a2a_app` (a Starlette/FastAPI app) via `google.adk.cli.utils.get_app`
   - `Makefile` runs specialist with `uvicorn github_agent:a2a_app --host localhost --port 8001`
   - Agent card is verifiable with `curl http://localhost:8001/.well-known/agent-card.json`

6. **Verify telemetry and observability**:
   - OpenTelemetry is configured with `NO_CONTENT` capture mode (no code/prompt content in traces)
   - Feedback model includes `score`, `text`, `log_type`, `service_name`, `user_id`, `session_id`
   - GCS artifact service is wired for trace upload
   - `service.namespace` is set to `"google-hackathon"`

7. **Emit compliance report**:
   - ✅ / ❌ per convention item
   - List of gaps with the specific file and line to fix
   - Deployment readiness: LOCAL ONLY / AGENT ENGINE READY / GEMINI ENTERPRISE READY

## Key Files Reference

| Component          | Path                                           |
|--------------------|------------------------------------------------|
| Specialist agent   | `github_agent/agent.py`                        |
| Client agent       | `agent.py` or `client_agent/app/agent.py`      |
| Agent Engine app   | `client_agent/app/agent_engine_app.py`         |
| Telemetry utils    | `client_agent/app/app_utils/telemetry.py`      |
| Feedback schema    | `client_agent/app/app_utils/typing.py`         |
| Environment config | `agent08_github_a2a_agent_mcp_server/.env`     |
