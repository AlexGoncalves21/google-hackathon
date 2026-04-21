"""Upload knowledge-base markdown files to GCS for Vertex AI Search ingestion.

Usage:
    python -m data_ingestion.ingest

The script reads all *.md files from docs/knowledge_base/ (relative to the
repo root) and uploads them to the GCS bucket configured in GCS_BUCKET_NAME.
Vertex AI Search's GCS Data Connector picks them up automatically on its next
scheduled sync, or you can trigger a manual import afterwards.

Required environment variables:
    GOOGLE_CLOUD_PROJECT   GCP project ID.
    GCS_BUCKET_NAME        GCS bucket connected to the Vertex AI Search datastore.

Optional environment variables:
    KNOWLEDGE_BASE_PATH    Override the default docs/knowledge_base path.
    GCS_PREFIX             Object prefix inside the bucket (default: knowledge_base).
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import storage

load_dotenv()

_REPO_ROOT = Path(__file__).parent.parent.parent
_DEFAULT_KB = _REPO_ROOT / "docs" / "knowledge_base"


def upload_knowledge_base(
    bucket_name: str,
    knowledge_base_path: Path | None = None,
    prefix: str = "knowledge_base",
) -> list[str]:
    """Upload all markdown files to GCS and return the list of uploaded URIs."""
    kb_path = knowledge_base_path or Path(
        os.getenv("KNOWLEDGE_BASE_PATH", str(_DEFAULT_KB))
    )
    md_files = sorted(kb_path.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"No markdown files found in {kb_path}")

    client = storage.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
    bucket = client.bucket(bucket_name)
    uploaded: list[str] = []

    for md_file in md_files:
        blob_name = f"{prefix}/{md_file.name}"
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(str(md_file), content_type="text/plain")
        uri = f"gs://{bucket_name}/{blob_name}"
        print(f"  uploaded {md_file.name} → {uri}")
        uploaded.append(uri)

    return uploaded


if __name__ == "__main__":
    bucket = os.environ["GCS_BUCKET_NAME"]
    prefix = os.getenv("GCS_PREFIX", "knowledge_base")
    print(f"Uploading knowledge base to gs://{bucket}/{prefix}/")
    uris = upload_knowledge_base(bucket_name=bucket, prefix=prefix)
    print(f"\nDone — {len(uris)} file(s) uploaded.")
    print(
        "\nNext step: trigger a Vertex AI Search import or wait for the scheduled "
        "GCS Data Connector sync."
    )
