# ==============================================================================
# Installation & Setup
# ==============================================================================

install:
	uv sync

# ==============================================================================
# Data Ingestion
# ==============================================================================

# Upload docs/knowledge_base/*.md to GCS so the Vertex AI Search Data Connector
# can pick them up. Requires GCS_BUCKET_NAME and GOOGLE_CLOUD_PROJECT in .env
sync-data:
	@echo "Uploading knowledge base documents to GCS..."
	uv run python -m data_ingestion.ingest

# ==============================================================================
# Playground
# ==============================================================================

playground:
	@echo "==============================================================================="
	@echo "| Starting the RAG agent playground...                                        |"
	@echo "|                                                                             |"
	@echo "| Select the 'app' folder in ADK Web.                                         |"
	@echo "| Ask questions about the project architecture, files, or configuration.      |"
	@echo "==============================================================================="
	uv run adk web . --port 8502 --reload_agents

# ==============================================================================
# Quality
# ==============================================================================

lint:
	uv sync --dev --extra lint
	uv run ruff check . --diff
	uv run ruff format . --check --diff
