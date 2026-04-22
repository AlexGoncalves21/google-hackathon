.PHONY: run

PROJECT_ID ?= $(shell gcloud config get-value project 2>/dev/null)
REGION ?= europe-west4
SERVICE_NAME ?= github-a2a-agent
PORT ?= 8001
HOST ?= 0.0.0.0
MODEL_NAME ?= gemini-2.5-pro
GITHUB_TOKEN_SECRET_NAME ?= github-personal-access-token
SERVICE_VISIBILITY ?= private
CLIENT_INVOKER_SERVICE_ACCOUNT ?=

run:
	@echo "Starting application on http://localhost:$(PORT)..."
	uv run uvicorn github_agent:a2a_app --host $(HOST) --port $(PORT)

# --- Commands from Agent Starter Pack ---

backend: deploy

build-inspector-if-needed:
	@if [ -d "tools/a2a-inspector" ] && [ ! -f "tools/a2a-inspector/frontend/public/script.js" ]; then \
		echo "🔨 Building inspector frontend..."; \
		cd tools/a2a-inspector/frontend && npm run build; \
	fi

deploy:
	@test -n "$(PROJECT_ID)" || (echo "No GCP project configured. Run 'gcloud config set project <project-id>' first."; exit 1)
	@test -n "$$GITHUB_PERSONAL_ACCESS_TOKEN" || (echo "Export GITHUB_PERSONAL_ACCESS_TOKEN before deploying."; exit 1)
	@gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com aiplatform.googleapis.com secretmanager.googleapis.com --project "$(PROJECT_ID)"
	@printf "%s" "$$GITHUB_PERSONAL_ACCESS_TOKEN" | \
		(gcloud secrets describe "$(GITHUB_TOKEN_SECRET_NAME)" --project "$(PROJECT_ID)" >/dev/null 2>&1 || \
		gcloud secrets create "$(GITHUB_TOKEN_SECRET_NAME)" --replication-policy=automatic --project "$(PROJECT_ID)") >/dev/null
	@printf "%s" "$$GITHUB_PERSONAL_ACCESS_TOKEN" | \
		gcloud secrets versions add "$(GITHUB_TOKEN_SECRET_NAME)" --data-file=- --project "$(PROJECT_ID)" >/dev/null
	@RUNTIME_SERVICE_ACCOUNT=$$(gcloud run services describe "$(SERVICE_NAME)" --project "$(PROJECT_ID)" --region "$(REGION)" --format='value(spec.template.spec.serviceAccountName)' 2>/dev/null); \
	if [ -z "$$RUNTIME_SERVICE_ACCOUNT" ]; then \
		PROJECT_NUMBER=$$(gcloud projects describe "$(PROJECT_ID)" --format='value(projectNumber)'); \
		RUNTIME_SERVICE_ACCOUNT="$$PROJECT_NUMBER-compute@developer.gserviceaccount.com"; \
	fi; \
	gcloud secrets add-iam-policy-binding "$(GITHUB_TOKEN_SECRET_NAME)" \
		--project "$(PROJECT_ID)" \
		--member="serviceAccount:$$RUNTIME_SERVICE_ACCOUNT" \
		--role="roles/secretmanager.secretAccessor" >/dev/null
	@echo "Deploying $(SERVICE_NAME) to Cloud Run in $(REGION) with $(SERVICE_VISIBILITY) access..."
	@AUTH_FLAG=""; \
	if [ "$(SERVICE_VISIBILITY)" = "public" ]; then \
		AUTH_FLAG="--allow-unauthenticated"; \
	else \
		AUTH_FLAG="--no-allow-unauthenticated"; \
	fi; \
	gcloud run deploy "$(SERVICE_NAME)" \
		--project "$(PROJECT_ID)" \
		--region "$(REGION)" \
		--source . \
		$$AUTH_FLAG \
		--set-env-vars "MODEL_NAME=$(MODEL_NAME),GOOGLE_CLOUD_PROJECT=$(PROJECT_ID),GOOGLE_CLOUD_LOCATION=$(REGION),GOOGLE_GENAI_USE_VERTEXAI=True" \
		--set-secrets "GITHUB_PERSONAL_ACCESS_TOKEN=$(GITHUB_TOKEN_SECRET_NAME):latest"
	@SERVICE_URL=$$(gcloud run services describe "$(SERVICE_NAME)" --project "$(PROJECT_ID)" --region "$(REGION)" --format='value(status.url)'); \
	gcloud run services update "$(SERVICE_NAME)" \
		--project "$(PROJECT_ID)" \
		--region "$(REGION)" \
		--update-env-vars "GITHUB_AGENT_URL=$$SERVICE_URL" \
		--update-secrets "GITHUB_PERSONAL_ACCESS_TOKEN=$(GITHUB_TOKEN_SECRET_NAME):latest" >/dev/null && \
	echo "" && \
	echo "✅ Cloud Run deployment successful" && \
	echo "Service URL: $$SERVICE_URL" && \
	echo "Agent Card: $$SERVICE_URL/.well-known/agent-card.json" && \
	echo "GitHub token stored in Secret Manager secret: $(GITHUB_TOKEN_SECRET_NAME)"
	@if [ "$(SERVICE_VISIBILITY)" != "public" ]; then \
		if [ -n "$(CLIENT_INVOKER_SERVICE_ACCOUNT)" ]; then \
			gcloud run services add-iam-policy-binding "$(SERVICE_NAME)" \
				--project "$(PROJECT_ID)" \
				--region "$(REGION)" \
				--member="serviceAccount:$(CLIENT_INVOKER_SERVICE_ACCOUNT)" \
				--role="roles/run.invoker" >/dev/null && \
			echo "Granted roles/run.invoker to $(CLIENT_INVOKER_SERVICE_ACCOUNT)"; \
		else \
			echo "⚠️  Cloud Run is private. Grant roles/run.invoker to the client runtime service account before invoking this service."; \
		fi; \
	fi

grant-client-invoker:
	@test -n "$(PROJECT_ID)" || (echo "No GCP project configured. Run 'gcloud config set project <project-id>' first."; exit 1)
	@test -n "$(CLIENT_INVOKER_SERVICE_ACCOUNT)" || (echo "Set CLIENT_INVOKER_SERVICE_ACCOUNT=<service-account-email>."; exit 1)
	@gcloud run services add-iam-policy-binding "$(SERVICE_NAME)" \
		--project "$(PROJECT_ID)" \
		--region "$(REGION)" \
		--member="serviceAccount:$(CLIENT_INVOKER_SERVICE_ACCOUNT)" \
		--role="roles/run.invoker" >/dev/null
	@echo "Granted roles/run.invoker to $(CLIENT_INVOKER_SERVICE_ACCOUNT)"

eval:
	@echo "==============================================================================="
	@echo "| Running Agent Evaluation                                                    |"
	@echo "==============================================================================="
	uv sync --dev --extra eval
	uv run adk eval ./github_agent $${EVALSET:-tests/eval/evalsets/basic.evalset.json} \
		$(if $(EVAL_CONFIG),--config_file_path=$(EVAL_CONFIG),$(if $(wildcard tests/eval/eval_config.json),--config_file_path=tests/eval/eval_config.json,))

eval-all:
	@echo "==============================================================================="
	@echo "| Running All Evalsets                                                        |"
	@echo "==============================================================================="
	@for evalset in tests/eval/evalsets/*.evalset.json; do \
		echo ""; \
		echo "▶ Running: $$evalset"; \
		$(MAKE) eval EVALSET=$$evalset || exit 1; \
	done
	@echo ""
	@echo "✅ All evalsets completed"

inspector: setup-inspector-if-needed build-inspector-if-needed
	@echo "==============================================================================="
	@echo "| 🔍 A2A Protocol Inspector                                                  |"
	@echo "==============================================================================="
	@echo "| 🌐 Inspector UI: http://localhost:5001                                     |"
	@echo "|                                                                             |"
	@echo "| 💡 Testing a Deployment:                                                    |"
	@echo "|    Use the Agent Card URL from 'make deploy' output                        |"
	@echo "|                                                                             |"
	@echo "|    🔐 Auth: Expand 'Authentication & Headers', select 'Bearer Token',       |"
	@echo "|       and paste a Cloud Run identity token for the deployed service URL    |"
	@echo "|                                                                             |"
	@echo "| ℹ️  Note: This service is deployed on Cloud Run, not Agent Engine.         |"
	@echo "==============================================================================="
	@echo ""
	cd tools/a2a-inspector/backend && uv run app.py

install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.8.13/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync --dev

lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run ty check .

playground:
	@echo "==============================================================================="
	@echo "| 🚀 Starting your agent playground...                                        |"
	@echo "|                                                                             |"
	@echo "| 💡 Try asking: Find open issues about MCP in google/adk-python.            |"
	@echo "|                                                                             |"
	@echo "| 🔍 IMPORTANT: Select the 'github_agent' folder to interact with your agent. |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

smoke-card:
	@curl -fsS "http://localhost:$(PORT)/.well-known/agent-card.json"

setup-dev-env:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)

setup-inspector-if-needed:
	@if [ ! -d "tools/a2a-inspector" ]; then \
		echo "" && \
		echo "📦 First-time setup: Installing A2A Inspector..." && \
		echo "" && \
		mkdir -p tools && \
		git clone --quiet https://github.com/a2aproject/a2a-inspector.git tools/a2a-inspector && \
		(cd tools/a2a-inspector && git -c advice.detachedHead=false checkout --quiet 893e4062f6fbd85a8369228ce862ebbf4a025694) && \
		echo "📥 Installing Python dependencies..." && \
		(cd tools/a2a-inspector && uv sync --quiet) && \
		echo "📥 Installing Node.js dependencies..." && \
		(cd tools/a2a-inspector/frontend && npm install --silent) && \
		echo "🔨 Building frontend..." && \
		(cd tools/a2a-inspector/frontend && npm run build --silent) && \
		echo "" && \
		echo "✅ A2A Inspector setup complete!" && \
		echo ""; \
	fi

test:
	uv sync --dev
	uv pip install pytest
	PYTHONPATH=. uv run python -m pytest tests/unit && PYTHONPATH=. uv run python -m pytest tests/integration
