# Copyright 2025 Google, LLC. This software is provided as-is, without
# warranty or representation for any use or purpose. Your use of it is
# subject to your agreement with Google.

# Licensed under the Apache License, Version 2.0 (the "License");

# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
from pathlib import Path
from typing import Any

import yaml
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)
PROMPTS_PATH = Path(__file__).resolve().parent / "prompts" / "agent.yaml"


def _load_agent_config() -> dict[str, Any]:
    with PROMPTS_PATH.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


AGENT_CONFIG = _load_agent_config()

# --- Logging ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- GitHub Config ---
GITHUB_AGENT_URL = os.getenv("GITHUB_AGENT_URL", "http://localhost:8001").rstrip("/")
GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()

SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

# --- MCP Config ---
MCP_URL = "https://api.githubcopilot.com/mcp/"
TOOLS = [
    # Repository tools
    "search_repositories",
    # Issue tools (read-only)
    "search_issues",
    "list_issues",
    # Pull request tools
    "list_pull_requests",
    "get_pull_request",
    "create_pull_request",
    "merge_pull_request",
    "get_pull_request_files",
    "get_pull_request_diff",
    "create_pull_request_review",
    "update_pull_request",
]

if not GITHUB_TOKEN:
    raise RuntimeError(
        "GITHUB_PERSONAL_ACCESS_TOKEN is required to start the GitHub A2A service."
    )

root_agent = Agent(
    name=AGENT_CONFIG["agent"]["name"],
    model=os.getenv("MODEL_NAME", "gemini-2.5-pro"),
    description="An agent that uses MCP to interact with GitHub.",
    instruction=(
        "You are a specialized GitHub agent. Use the available MCP tools to help users "
        "search and explore GitHub repositories and issues.\n\n"
        "Available tools:\n"
        "- search_repositories: Search for GitHub repositories by keyword or topic\n"
        "- search_issues: Search for issues across GitHub\n"
        "- list_issues: List issues in a specific repository\n\n"
        "Always provide clear, structured responses. Include repository names, URLs, "
        "and relevant details when available."
    ),
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=MCP_URL,
                headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
            ),
            tool_filter=TOOLS,
        )
    ],
)

agent_card = AgentCard(
    name="GithubAgent-A2A",
    description="An agent that uses MCP to interact with GitHub.",
    url=GITHUB_AGENT_URL,
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=SUPPORTED_CONTENT_TYPES,
    default_output_modes=SUPPORTED_CONTENT_TYPES,
    skills=[
        AgentSkill(
            id="search_github_events",
            name="Search GitHub Events",
            description="Search GitHub for specific events such as repositories and issues.",
            tags=["github", "repository", "code"],
        )
    ],
)

a2a_app = to_a2a(root_agent, agent_card=agent_card)
