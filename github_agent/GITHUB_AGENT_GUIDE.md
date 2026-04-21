# GitHub Agent Guide

This guide covers the standalone GitHub specialist service in `github_agent/`.
It is the A2A backend that talks to GitHub through MCP.

The Gemini-facing agent now lives separately in the sibling `client_agent/` project.

## Architecture Overview

```text
client_agent
  -> RemoteA2aAgent
  -> github_agent
  -> GitHub MCP
  -> GitHub
```

Inside this directory, the important runtime file is:

1. **github_agent/github_agent/agent.py (The Service):**
   - Defines the specialized GitHub agent.
   - Connects to `https://api.githubcopilot.com/mcp/` with a GitHub token.
   - Loads selected GitHub tools such as `search_repositories`, `search_issues`, and `list_issues`.
   - Exposes the agent as an A2A web service.

## Setup and Configuration

### 1. Prerequisites
* Python **3.10+**
* A GitHub token in `GITHUB_PERSONAL_ACCESS_TOKEN`
* `uv`, `gcloud`, and Docker/Cloud Build access for deployment

### 2. Environment Variables
Create a `.env` file in the root of this directory (`github_agent/`). This file should contain your token and runtime settings.

```bash
# .env file
# Your GitHub Access Token
GITHUB_PERSONAL_ACCESS_TOKEN="YOUR_GITHUB_ACCESS_TOKEN_HERE"

# The generative model to use for the agents
MODEL_NAME="gemini-2.5-pro"

# The URL where the A2A service will be hosted
GITHUB_AGENT_URL="http://localhost:8001/"

# The GCP project
GOOGLE_CLOUD_PROJECT="YOUR_GCP_PROJECT"
GOOGLE_CLOUD_LOCATION="us-central1"
GOOGLE_GENAI_USE_VERTEXAI="True"
```

> **Warning:** Never hardcode your `GITHUB_PERSONAL_ACCESS_TOKEN` in the source code. The `.env` file keeps it secure and private.

## Running the Application

You will usually want two terminal windows for local development.

### Step 0: Install dependencies
First, initialize the environment and install dependencies.

```bash
uv venv
source .venv/bin/activate
uv sync
gcloud auth application-default login
```

### Step 1: Run the GitHub Agent
In your first terminal, start the local A2A service.

```bash
make run
```

### Step 2: Verify the Agent Card
In your second terminal, verify that the service is exposing its agent card.

```bash
curl http://localhost:8001/.well-known/agent-card.json
```

### Step 3: Optional Local Playground
If you want the ADK web playground for the GitHub agent itself, run:

```bash
make playground
```

If you want the end-to-end experience, start the separate sibling client in `../client_agent`.

## High-level Instructions
1. Implement and test the GitHub specialist locally.
2. Deploy this service to Cloud Run.
3. Copy the public service URL into `../client_agent/.env`.
4. Deploy the separate `client_agent` project to Agent Engine.
5. Register `client_agent` in Gemini Enterprise.
