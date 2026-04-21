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

from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

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
    name="github_agent",
    model=os.getenv("MODEL_NAME", "gemini-2.5-pro"),
    description="An agent that uses MCP to interact with GitHub repositories, issues, and pull requests.",
    instruction=(
        "You are a specialized GitHub agent. Use the available MCP tools to help users "
        "search, explore, and manage GitHub repositories, issues, and pull requests.\n\n"
        "## Repository Tools\n"
        "- search_repositories: Search for GitHub repositories by keyword, topic, or other criteria.\n\n"
        "## Issue Tools\n"
        "- search_issues: Search for issues across GitHub using queries (e.g. repo:owner/repo is:open).\n"
        "- list_issues: List issues in a specific repository. Accepts owner, repo, and optional filters "
        "(state, labels, assignee, milestone).\n\n"
        "## Pull Request Tools\n"
        "- list_pull_requests: List PRs in a repository. Accepts owner, repo, and optional filters "
        "(state='open'|'closed'|'all', head, base, sort, direction).\n"
        "- get_pull_request: Get full details of a specific PR by owner, repo, and pull_number. "
        "Returns title, body, state, author, reviewers, labels, and merge status.\n"
        "- create_pull_request: Create a new PR. Requires owner, repo, title, head (source branch), "
        "base (target branch), and body. Optionally set draft=True or maintainer_can_modify.\n"
        "- update_pull_request: Update an existing PR's title, body, state, or base branch.\n"
        "- merge_pull_request: Merge a PR by owner, repo, and pull_number. Optionally specify "
        "merge_method ('merge'|'squash'|'rebase') and a commit message.\n"
        "- get_pull_request_files: List files changed in a PR with their patch diffs and status.\n"
        "- get_pull_request_diff: Get the full unified diff of a PR.\n"
        "- create_pull_request_review: Submit a review on a PR. Requires owner, repo, pull_number, "
        "event ('APPROVE'|'REQUEST_CHANGES'|'COMMENT'), and optionally a body and inline comments.\n\n"
        "## Guidelines\n"
        "- Always clarify owner and repo when not provided.\n"
        "- For merges and reviews, confirm intent before acting if the request is ambiguous.\n"
        "- Provide structured responses: include PR/issue numbers, titles, URLs, authors, and state.\n"
        "- When reviewing a PR, call get_pull_request_files or get_pull_request_diff first to "
        "understand the changes before submitting feedback."
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
    description="An agent that uses MCP to interact with GitHub repositories, issues, and pull requests.",
    url=GITHUB_AGENT_URL,
    version="1.1.0",
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=SUPPORTED_CONTENT_TYPES,
    default_output_modes=SUPPORTED_CONTENT_TYPES,
    skills=[
        AgentSkill(
            id="search_github_events",
            name="Search GitHub Events",
            description="Search GitHub for repositories and issues.",
            tags=["github", "repository", "issues"],
        ),
        AgentSkill(
            id="manage_pull_requests",
            name="Manage Pull Requests",
            description=(
                "List, create, update, review, and merge pull requests in a GitHub repository."
            ),
            tags=["github", "pull-request", "code-review", "merge"],
        ),
    ],
)

a2a_app = to_a2a(root_agent, agent_card=agent_card)
