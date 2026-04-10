# app/services/embeddings.py
from __future__ import annotations
from typing import List

from app.core.config import settings


class LocalSentenceTransformerBackend:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_text(self, text: str) -> List[float]:
        model = self._get_model()
        vec = model.encode(text, normalize_embeddings=True)
        try:
            import numpy as np
            if isinstance(vec, np.ndarray):
                vec = vec.reshape(-1).tolist()
        except Exception:
            pass
        return [float(x) for x in vec]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        model = self._get_model()
        vecs = model.encode(texts, normalize_embeddings=True)
        try:
            import numpy as np
            if isinstance(vecs, np.ndarray):
                vecs = vecs.tolist()
        except Exception:
            pass
        return [[float(x) for x in row] for row in vecs]


class EmbeddingClient:
    def __init__(self):
        self.local_backend = LocalSentenceTransformerBackend(settings.LOCAL_EMBEDDING_MODEL)

    @property
    def model_name(self) -> str:
        if settings.EMBEDDINGS_PROVIDER == "openai":
            return settings.EMBEDDING_MODEL
        return f"local-{settings.LOCAL_EMBEDDING_MODEL.split('/')[-1]}"

    def embed_text(self, text: str) -> List[float]:
        if settings.EMBEDDINGS_PROVIDER == "openai":
            if not settings.OPENAI_API_KEY:
                raise RuntimeError("OPENAI_API_KEY missing but EMBEDDINGS_PROVIDER=openai")
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            resp = client.embeddings.create(model=settings.EMBEDDING_MODEL, input=text)
            return [float(x) for x in resp.data[0].embedding]
        return self.local_backend.embed_text(text)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if settings.EMBEDDINGS_PROVIDER == "openai":
            if not settings.OPENAI_API_KEY:
                raise RuntimeError("OPENAI_API_KEY missing but EMBEDDINGS_PROVIDER=openai")
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            resp = client.embeddings.create(model=settings.EMBEDDING_MODEL, input=texts)
            return [[float(x) for x in d.embedding] for d in resp.data]
        return self.local_backend.embed_texts(texts)


embedding_client = EmbeddingClient()