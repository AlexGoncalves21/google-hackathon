# Runtime Configuration

## GitHub Specialist Environment Variables

`github_agent/.env.example` defines these expected variables:

- `MODEL_NAME`
- `GITHUB_AGENT_URL`
- `GITHUB_PERSONAL_ACCESS_TOKEN`
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`
- `GOOGLE_GENAI_USE_VERTEXAI`

### Meaning of Specialist Variables

- `MODEL_NAME`: The Gemini model name for the GitHub specialist.
- `GITHUB_AGENT_URL`: The service URL for the GitHub specialist.
- `GITHUB_PERSONAL_ACCESS_TOKEN`: Personal access token for GitHub MCP access.
- `GOOGLE_CLOUD_PROJECT`: Google Cloud project identifier.
- `GOOGLE_CLOUD_LOCATION`: Vertex AI location, currently shown as
  `us-central1` in the example file.
- `GOOGLE_GENAI_USE_VERTEXAI`: Expected to be `"True"` for Vertex AI-backed
  model access.

## Specialist Service Defaults

Inside `github_agent/github_agent/agent.py`, these runtime values are important:

- `GITHUB_AGENT_URL` defaults to `http://localhost:8001/`
- `MCP_URL` is `https://api.githubcopilot.com/mcp/`
- `TOOLS` includes:
  - `search_repositories`
  - `search_issues`
  - `list_issues`

The GitHub specialist currently raises an error if
`GITHUB_PERSONAL_ACCESS_TOKEN` is missing.

## Client Agent Environment Variables

`client_agent/.env.example` defines:

- `MODEL_NAME`
- `MAIN_AGENT_BASE_URL`
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`
- `GOOGLE_GENAI_USE_VERTEXAI`

### Meaning of Client Variables

- `MAIN_AGENT_BASE_URL`: Preferred base URL of the main GitHub specialist.
- `GITHUB_AGENT_URL`: Legacy fallback env var still supported by the client.
- `GOOGLE_CLOUD_PROJECT`: Project for the client agent deployment.
- `GOOGLE_CLOUD_LOCATION`: Region for the client agent and Agent Engine.

## How the Client Finds the Remote Specialist

`client_agent/app/agent.py` requires a real specialist URL through:

- `MAIN_AGENT_BASE_URL`
- or the legacy fallback `GITHUB_AGENT_URL`

It constructs the remote agent card URL from that base URL plus the ADK A2A
well-known card path.

If no remote base URL is configured, the client raises an error instead of
falling back to a local mock specialist.

## Ports and URLs

The documentation consistently assumes the main GitHub specialist listens on
port `8001`.

Important local URLs include:

- Main specialist base URL: `http://localhost:8001`
- Agent card URL:
  `http://localhost:8001/.well-known/agent-card.json`

## Prompt Configuration

The user-facing instructions are stored in YAML:

- `client_agent/app/prompts/agent.yaml`
- `github_agent/github_agent/prompts/agent.yaml`

## Python and Dependency Expectations

### GitHub Specialist Project

The `github_agent/pyproject.toml` currently specifies:

- package name: `gitHub_a2a_agent`
- Python requirement: `>=3.10`
- dependency: `google-adk[a2a]>=1.31.0,<2.0.0`
- `uvicorn[standard]` for serving the A2A app

### Client Agent Project

The `client_agent/pyproject.toml` currently specifies:

- package name: `github-client-agent`
- Python requirement: `>=3.10,<3.14`
- ADK dependency range: `google-adk[a2a]>=1.18.0,<2.0.0`
- `PyYAML` for prompt loading
- Agent Engine dependency:
  `google-cloud-aiplatform[evaluation,agent-engines]>=1.130.0`
- logging, telemetry, and dotenv support

## Configuration Difference to Remember

The two projects do not have identical runtime requirements:

- `github_agent/` is the Cloud Run-hosted MCP specialist.
- `client_agent/` is the Agent Engine-hosted Gemini-facing delegator.
