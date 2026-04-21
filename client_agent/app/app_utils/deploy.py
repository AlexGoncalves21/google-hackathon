import datetime
import importlib
import inspect
import json
import logging
import os
import warnings
from typing import Any

import click
import google.auth
import vertexai
from dotenv import load_dotenv
from vertexai._genai import _agent_engines_utils
from vertexai._genai.types import AgentEngine, AgentEngineConfig

warnings.filterwarnings(
    "ignore", category=FutureWarning, module="google.cloud.aiplatform"
)
load_dotenv()


def generate_class_methods_from_agent(agent_instance: Any) -> list[dict[str, Any]]:
    """Generate method specifications from the agent register_operations output."""
    registered_operations = _agent_engines_utils._get_registered_operations(
        agent=agent_instance
    )
    class_methods_spec = _agent_engines_utils._generate_class_methods_spec_or_raise(
        agent=agent_instance,
        operations=registered_operations,
    )
    return [_agent_engines_utils._to_dict(method_spec) for method_spec in class_methods_spec]


def write_deployment_metadata(remote_agent: Any) -> None:
    """Write deployment metadata to a local file for later registration."""
    metadata = {
        "remote_agent_engine_id": remote_agent.api_resource.name,
        "deployment_target": "agent_engine",
        "is_a2a": False,
        "deployment_timestamp": datetime.datetime.now().isoformat(),
    }
    with open("deployment_metadata.json", "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)


def get_existing_agent_name_from_metadata() -> str | None:
    """Return the previously deployed Agent Engine resource name when available."""
    metadata_path = "deployment_metadata.json"
    if not os.path.exists(metadata_path):
        return None

    try:
        with open(metadata_path, encoding="utf-8") as file:
            metadata = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None

    if metadata.get("deployment_target") != "agent_engine":
        return None

    return metadata.get("remote_agent_engine_id")


def print_deployment_success(remote_agent: Any, location: str, project: str) -> None:
    """Print the post-deploy summary and playground link."""
    resource_name_parts = remote_agent.api_resource.name.split("/")
    agent_engine_id = resource_name_parts[-1]
    project_number = resource_name_parts[1]
    playground_url = (
        "https://console.cloud.google.com/vertex-ai/agents/agent-engines/"
        f"locations/{location}/agent-engines/{agent_engine_id}/playground?project={project}"
    )

    print("\n✅ Deployment successful!")
    service_account = remote_agent.api_resource.spec.service_account
    if service_account:
        print(f"Service Account: {service_account}")
    else:
        default_sa = (
            f"service-{project_number}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"
        )
        print(f"Service Account: {default_sa}")
    print(f"\n📊 Open Console Playground: {playground_url}\n")


def configure_runtime_env(location: str, project: str) -> dict[str, str]:
    """Prepare the local and remote env vars required by the deployed agent."""
    main_agent_base_url = (
        os.getenv("MAIN_AGENT_BASE_URL") or os.getenv("GITHUB_AGENT_URL")
    )
    if not main_agent_base_url:
        raise click.ClickException(
            "Set MAIN_AGENT_BASE_URL or GITHUB_AGENT_URL before deploying the client agent."
        )

    normalized_base_url = main_agent_base_url.rstrip("/")
    model_name = os.getenv("MODEL_NAME", "gemini-2.5-pro")
    use_vertex_ai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "True")

    # Keep the current process and the remote runtime aligned.
    os.environ["MAIN_AGENT_BASE_URL"] = normalized_base_url
    os.environ["GITHUB_AGENT_URL"] = normalized_base_url
    os.environ["MODEL_NAME"] = model_name
    os.environ["GOOGLE_CLOUD_PROJECT"] = project
    os.environ["GOOGLE_CLOUD_LOCATION"] = location
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = use_vertex_ai

    return {
        "MODEL_NAME": model_name,
        "MAIN_AGENT_BASE_URL": normalized_base_url,
        "GITHUB_AGENT_URL": normalized_base_url,
    }


@click.command()
@click.option("--project", default=None, help="GCP project ID.")
@click.option("--location", default="us-central1", help="GCP region.")
@click.option(
    "--display-name",
    default="Client Agent",
    help="Display name for the agent engine.",
)
@click.option(
    "--description",
    default=(
        "Gemini Enterprise-facing client agent that delegates GitHub tasks "
        "to a remote A2A specialist."
    ),
    help="Description of the agent.",
)
@click.option(
    "--source-packages",
    multiple=True,
    default=["./app"],
    help="Source packages to deploy.",
)
@click.option(
    "--entrypoint-module",
    default="app.agent_engine_app",
    help="Python module path for the agent entrypoint.",
)
@click.option(
    "--entrypoint-object",
    default="agent_engine",
    help="Name of the agent instance at module level.",
)
@click.option(
    "--requirements-file",
    default="app/app_utils/.requirements.txt",
    help="Path to requirements.txt file.",
)
def deploy_agent_engine_app(
    project: str | None,
    location: str,
    display_name: str,
    description: str,
    source_packages: tuple[str, ...],
    entrypoint_module: str,
    entrypoint_object: str,
    requirements_file: str,
) -> AgentEngine:
    """Deploy the agent engine app to Vertex AI Agent Engine."""
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    if not project:
        _, project = google.auth.default()

    env_vars = configure_runtime_env(location=location, project=project)

    click.echo("\n🚀 Deploying Client Agent to Vertex AI Agent Engine...")

    client = vertexai.Client(project=project, location=location)
    vertexai.init(project=project, location=location)

    module = importlib.import_module(entrypoint_module)
    agent_instance = getattr(module, entrypoint_object)
    if inspect.iscoroutine(agent_instance):
        import asyncio

        agent_instance = asyncio.run(agent_instance)

    class_methods_list = generate_class_methods_from_agent(agent_instance)
    config = AgentEngineConfig(
        display_name=display_name,
        description=description,
        source_packages=list(source_packages),
        entrypoint_module=entrypoint_module,
        entrypoint_object=entrypoint_object,
        class_methods=class_methods_list,
        env_vars=env_vars,
        requirements_file=requirements_file,
        min_instances=1,
        max_instances=10,
        resource_limits={"cpu": "4", "memory": "8Gi"},
        container_concurrency=9,
        agent_framework="google-adk",
    )

    existing_agent_name = get_existing_agent_name_from_metadata()
    if existing_agent_name:
        click.echo(
            f"Updating existing agent from deployment metadata: {display_name} "
            "(this can take 3-5 minutes)..."
        )
        remote_agent = client.agent_engines.update(
            name=existing_agent_name,
            config=config,
        )
    else:
        existing_agents = list(client.agent_engines.list())
        matching_agents = [
            agent
            for agent in existing_agents
            if agent.api_resource.display_name == display_name
        ]

        action = "Updating" if matching_agents else "Creating"
        click.echo(f"{action} agent: {display_name} (this can take 3-5 minutes)...")

        if matching_agents:
            remote_agent = client.agent_engines.update(
                name=matching_agents[0].api_resource.name,
                config=config,
            )
        else:
            remote_agent = client.agent_engines.create(config=config)

    write_deployment_metadata(remote_agent)
    print_deployment_success(remote_agent, location, project)
    return remote_agent


if __name__ == "__main__":
    deploy_agent_engine_app()
