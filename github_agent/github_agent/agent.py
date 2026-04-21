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
import pathlib
from pathlib import Path
from typing import Any

import yaml
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

SKILLS_DIR = pathlib.Path(__file__).resolve().parent.parent / "skills"

adk_agent_conventions = load_skill_from_dir(SKILLS_DIR / "adk-agent-conventions")

commit_impact_analysis = load_skill_from_dir(SKILLS_DIR / "commit-impact-analysis")

conventional_commits = load_skill_from_dir(SKILLS_DIR / "conventional-commits")

github_issue_triage = load_skill_from_dir(SKILLS_DIR / "github-issue-triage")

review_pr_changes = load_skill_from_dir(SKILLS_DIR / "review-pr-changes")

security_change_review = load_skill_from_dir(SKILLS_DIR / "security-change-review")

my_skill_toolset = skill_toolset.SkillToolset(
    skills=[
        adk_agent_conventions,
        commit_impact_analysis,
        conventional_commits,
        github_issue_triage,
        review_pr_changes,
        security_change_review,
    ]
)

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
    "search_pull_requests",
    "pull_request_read",
    "create_pull_request",
    "merge_pull_request",
    "update_pull_request",
    "pull_request_review_write",
    "add_reply_to_pull_request_comment",
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
        "Always provide clear, structured responses. Include repository names, URLs, "
        "and relevant details when available."
        "For the procedures use your skills to analyze commit impacts, triage issues, review PR changes, and ensure security best practices."
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
        "- search_pull_requests: Search PRs across GitHub using queries (e.g. repo:owner/repo is:open).\n"
        "- pull_request_read: Get full details of a specific PR by owner, repo, and pullNumber. "
        "Returns title, body, state, author, reviewers, labels, changed files, and diff.\n"
        "- create_pull_request: Create a new PR. Requires owner, repo, title, head (source branch), "
        "base (target branch), and body. Optionally set draft=True or maintainer_can_modify.\n"
        "- update_pull_request: Update an existing PR's title, body, state, or base branch.\n"
        "- merge_pull_request: Merge a PR by owner, repo, and pullNumber. Optionally specify "
        "merge_method ('merge'|'squash'|'rebase') and a commit message.\n"
        "- pull_request_review_write: Submit a review on a PR. Requires owner, repo, pullNumber, "
        "event ('APPROVE'|'REQUEST_CHANGES'|'COMMENT'), and optionally a body and inline comments. "
        "Always call pull_request_read first to understand the changes before reviewing.\n"
        "- add_reply_to_pull_request_comment: Reply to an existing review comment on a PR.\n\n"
        "## Guidelines\n"
        "- Always clarify owner and repo when not provided.\n"
        "- For merges and reviews, confirm intent before acting if the request is ambiguous.\n"
        "- Provide structured responses: include PR/issue numbers, titles, URLs, authors, and state.\n"
        "- Before submitting a review, always read the PR with pull_request_read first."
    ),
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=MCP_URL,
                headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
            ),
            tool_filter=TOOLS,
        ),
        my_skill_toolset,
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
            description="Epertise in Github event search and analysis, providing insights into repository activities, issue trends, and pull request dynamics.",
            tags=["github", "repository", "code"],
        )
    ],
)

a2a_app = to_a2a(root_agent, agent_card=agent_card)
