# 🐛 GitHub Agent (ADK + A2A + Custom MCP Server)

This project demonstrates how to build a specialized Google ADK (Agent Development Kit) agent that interacts with the GitHub API.

It uses the **MCP (Multi-Capability Platform)** to securely fetch information (like repositories and issues) and exposes these capabilities to other agents via **A2A (Agent-to-Agent)** communication.

---

## 🔧 Architecture Overview

This project consists of two main components that run separately:

1.  **`github_agent/agent.py` (The Service 📡):**
    * This is the server component that defines the specialized GitHub agent.
    * It uses `MCPToolset` to connect to the GitHub MCP endpoint (`https://api.githubcopilot.com/mcp/`) using a Personal Access Token.
    * It selectively loads specific GitHub tools: `search_repositories`, `search_issues`, and `list_issues`.
    * It wraps this logic in an ADK `Agent` and exposes it as a web service using `to_a2a` on port 8001.

2.  **`agent.py` (The Client 🖥️):**
    * This is the client component that consumes the service.
    * It defines a `RemoteA2aAgent` that points to the `github_agent`'s auto-generated agent card URL.
    * It creates a `root_agent` that is instructed to **delegate** any GitHub-related tasks to the remote `github_agent`.

---

## ⚙️ Setup and Configuration

### 1. Prerequisites

* Python **3.10+**
* **Important:** This agent requires `google-adk[a2a]==1.18.0` which is defined in `solution_agent08_github_a2a_agent_mcp_server/pyproject.toml`.
* Create a GitHub token `GITHUB_PERSONAL_ACCESS_TOKEN` [here](https://github.com/settings/tokens).
  For more details, refer to the GitHub personal access tokens [documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token).

### 2. Environment Variables

Create a `.env` file in the root of the project directory, i.e. in `solution_agent08_github_a2a_agent_mcp_server`. This file must contain your GitHub token and the model name.

```env
# .env file

# Your GitHub Access Token
GITHUB_PERSONAL_ACCESS_TOKEN="YOUR_GITHUB_ACCESS_TOKEN_HERE"

# The generative model to use for the agents
MODEL_NAME="gemini-2.5-pro"

# The URL where the agent service will be hosted
GITHUB_AGENT_URL="http://localhost:8001/"

# The GCP project.
GOOGLE_CLOUD_PROJECT="YOUR_GCP_PROJECT"
GOOGLE_CLOUD_LOCATION="us-central1"
GOOGLE_GENAI_USE_VERTEXAI="True"
```

**Warning**: Never hardcode your `GITHUB_PERSONAL_ACCESS_TOKEN` in the source code. The .env file keeps it secure and private.

---

## 🚀 Running the Application
You will need three separate terminal windows for this process.

### Step 0: Install dependencies
First, initialize the `uv` environment.

```bash
uv venv
```

Then, activate the environment.

```bash
source .venv/bin/activate
```

Finally, install dependencies.

```bash
uv sync
```

Make sure to be authenticated to Google Cloud with `gcloud auth application-default login`

### Step 1: Run the GitHub Agent (Server)
In your first terminal, run the `github_agent/agent.py` file using uvicorn. This starts the web server that exposes your agent via A2A.

```bash
make run
```

You should see output from `uvicorn` indicating the server is running.

```
INFO:     Started server process [315551]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8001 (Press CTRL+C to quit)
```

### Step 2: Verify the Agent Card (Optional but Recommended)
In your second terminal, you can verify that the agent is correctly exposing its "agent card" (its A2A configuration).

```bash
curl http://localhost:8001/.well-known/agent-card.json
```
✅ You should see a JSON output similar to this, confirming the agent is online:


```json
{
  "capabilities": {
    "streaming": false
  },
  "defaultInputModes": [
    "text",
    "text/plain"
  ],
  "defaultOutputModes": [
    "text",
    "text/plain"
  ],
  "description": "An agent that uses MCP to interact with GitHub.",
  "name": "GithubAgent-A2A",
  "preferredTransport": "JSONRPC",
  "protocolVersion": "0.3.0",
  "skills": [
    {
      "description": "Search GitHub for specific events such as repositories and issues.",
      "id": "search_github_events",
      "name": "Search GitHub Events",
      "tags": [
        "github",
        "repository",
        "code"
      ]
    }
  ],
  "url": "http://localhost:8001/",
  "version": "1.0.0"
}
```

### 💻 Step 3: Run the Web Client and Interact

In your third terminal, launch the web client from the **project root** (`adk-hackathon-bundle`):

```bash
uv run --project solution_agent08_github_a2a_agent_mcp_server/ adk web
```

---

Open this URL in your web browser to access the chat interface.

You can now interact with the agent. When you ask a GitHub-related question, the `root_agent` (which you're interacting with) will automatically forward the request to the `github_agent` service. This service will then use its `MCP tools` to get the answer.

![github agent example](../img/github_agent.png)
![github agent trace](../img/github_agent_trace.png)


## High-level instructions

 - Use the tools above to come up with an agent, you can use the specification above for agent instruction
 - Test the agent locally (`uv run --project solution_agent08_github_a2a_agent_mcp_server/ adk web`)
 - Deploy the agent to Agent Engine
 - Test the deployed version of the agent
 - Link the agent to a Gemini Enterprise application
 - Make sure it works in Gemini Enterprise as well
