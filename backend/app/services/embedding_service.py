"""
Core AI implementation for the assignment.

This module implements semantic search from first principles:
1. Text is converted into dense vector embeddings using a local
   Sentence-Transformer model (all-MiniLM-L6-v2) -- no external LLM API call.
2. Embeddings are stored in a FAISS vector index (local vector database).
3. A query is embedded the same way and FAISS performs a nearest-neighbour
   (cosine similarity via inner product on normalized vectors) search against
   the stored document embeddings.

The index and its id->document mapping are persisted to disk so the vector
store survives server restarts.
"""
import json
import os
import threading
from typing import List, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings

VECTOR_STORE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "vector_store")
VECTOR_STORE_DIR = os.path.abspath(VECTOR_STORE_DIR)
INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "faiss.index")
MAPPING_PATH = os.path.join(VECTOR_STORE_DIR, "mapping.json")

EMBEDDING_DIM = 384  # dimensionality of all-MiniLM-L6-v2


class EmbeddingStore:
    """Singleton wrapper around a FAISS index + the embedding model."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

        # id_map: FAISS row index (int) -> {"document_id": int, "text": str, "title": str}
        self.id_map: dict = {}

        if os.path.exists(INDEX_PATH) and os.path.exists(MAPPING_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(MAPPING_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
                self.id_map = {int(k): v for k, v in raw.items()}
        else:
            # Inner product index on L2-normalized vectors == cosine similarity
            self.index = faiss.IndexFlatIP(EMBEDDING_DIM)

    def _persist(self):
        faiss.write_index(self.index, INDEX_PATH)
        with open(MAPPING_PATH, "w", encoding="utf-8") as f:
            json.dump(self.id_map, f)

    def _embed(self, texts: List[str]) -> np.ndarray:
        vectors = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        vectors = vectors.astype("float32")
        faiss.normalize_L2(vectors)
        return vectors

    def add_document(self, document_id: int, title: str, text: str) -> int:
        """Embeds the document text and appends it to the FAISS index.
        Returns the FAISS row id assigned to this document."""
        vector = self._embed([text])
        row_id = self.index.ntotal
        self.index.add(vector)
        self.id_map[row_id] = {
            "document_id": document_id,
            "title": title,
            "text": text[:1000],
        }
        self._persist()
        return row_id

    def search(self, query: str, top_k: int = 5) -> List[Tuple[dict, float]]:
        if self.index.ntotal == 0:
            return []
        query_vector = self._embed([query])
        top_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_vector, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            meta = self.id_map.get(int(idx))
            if meta:
                results.append((meta, float(score)))
        return results


def get_embedding_store() -> EmbeddingStore:
    return EmbeddingStore()
