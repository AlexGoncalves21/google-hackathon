import math
import os
from pathlib import Path
from typing import Optional


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class KnowledgeBaseRetriever:
    _EMBED_MODEL = "text-embedding-004"

    def __init__(self, knowledge_base_path: Optional[str] = None):
        if knowledge_base_path is None:
            knowledge_base_path = os.getenv(
                "KNOWLEDGE_BASE_PATH",
                str(Path(__file__).parent.parent.parent / "docs" / "knowledge_base"),
            )
        self._kb_path = Path(knowledge_base_path)
        self._chunks: list[dict] = []
        self._built = False
        self._embed_model = None

    def _get_embed_model(self):
        if self._embed_model is None:
            import vertexai
            from vertexai.language_models import TextEmbeddingModel

            vertexai.init(
                project=os.getenv("GOOGLE_CLOUD_PROJECT"),
                location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
            )
            self._embed_model = TextEmbeddingModel.from_pretrained(self._EMBED_MODEL)
        return self._embed_model

    def _embed_texts(
        self, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> list[list[float]]:
        from vertexai.language_models import TextEmbeddingInput

        model = self._get_embed_model()
        inputs = [TextEmbeddingInput(text=t, task_type=task_type) for t in texts]
        return [r.values for r in model.get_embeddings(inputs)]

    def build_index(self) -> None:
        if self._built:
            return

        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        raw_chunks: list[dict] = []

        for md_file in sorted(self._kb_path.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            for chunk in splitter.split_text(text):
                raw_chunks.append({"text": chunk, "source": md_file.name})

        if not raw_chunks:
            self._built = True
            return

        # Embed in batches of 250 (Vertex AI API limit)
        batch_size = 250
        embeddings: list[list[float]] = []
        for i in range(0, len(raw_chunks), batch_size):
            batch_texts = [c["text"] for c in raw_chunks[i : i + batch_size]]
            embeddings.extend(
                self._embed_texts(batch_texts, task_type="RETRIEVAL_DOCUMENT")
            )

        for chunk, emb in zip(raw_chunks, embeddings):
            chunk["embedding"] = emb

        self._chunks = raw_chunks
        self._built = True

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        self.build_index()
        if not self._chunks:
            return []

        query_emb = self._embed_texts([query], task_type="RETRIEVAL_QUERY")[0]
        scored = [
            (_cosine_similarity(query_emb, c["embedding"]), c)
            for c in self._chunks
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {"text": c["text"], "source": c["source"], "score": round(s, 4)}
            for s, c in scored[:top_k]
        ]
