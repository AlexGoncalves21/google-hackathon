# ==============================================================================
# Installation & Setup
# ==============================================================================

install:
	uv sync

# ==============================================================================
# Playground Targets
# ==============================================================================

playground:
	@echo "==============================================================================="
	@echo "| 🚀 Starting the GitHub client playground...                                 |"
	@echo "|                                                                             |"
	@echo "| 🔍 Select the 'app' folder in ADK Web.                                      |"
	@echo "| 💡 This client delegates GitHub work to the remote A2A agent.               |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

# ==============================================================================
# Deployment
# ==============================================================================

clean-package-artifacts:
	find app -name '__pycache__' -type d -prune -exec rm -rf {} +
	find app -name '*.pyc' -delete
	find app -name '.DS_Store' -delete

deploy:
	$(MAKE) clean-package-artifacts
	(uv export --no-hashes --no-header --no-dev --no-emit-project --no-annotate > app/app_utils/.requirements.txt 2>/dev/null || \
	uv export --no-hashes --no-header --no-dev --no-emit-project > app/app_utils/.requirements.txt) && \
	uv run -m app.app_utils.deploy \
		--source-packages=./app \
		--entrypoint-module=app.agent_engine_app \
		--entrypoint-object=agent_engine \
		--requirements-file=app/app_utils/.requirements.txt

backend: deploy

# ==============================================================================
# Quality
# ==============================================================================

lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run ty check .

# ==============================================================================
# Gemini Enterprise Integration
# ==============================================================================

register-gemini-enterprise:
	@uvx agent-starter-pack@0.41.1 register-gemini-enterprise
