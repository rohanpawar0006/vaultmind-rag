"""
embeddings.py — Local Embedding Model Wrapper using Sentence-Transformers

Why local embeddings over cloud embedding APIs?
1. Zero cost / zero rate limits during evaluation or testing.
2. Offline execution guarantees reliable demo performance without external dependencies.
3. Fast CPU inference using all-MiniLM-L6-v2 (384 dimensions, normalized vectors).
"""

from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL_NAME


class EmbeddingManager:
    """
    Singleton manager for loading and executing local sentence-transformer models.
    Ensures weights are loaded once in memory and reused across queries.
    """
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingManager, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        """Loads the sentence-transformers embedding model."""
        print(f"[Embeddings] Loading local embedding model '{EMBEDDING_MODEL_NAME}'...")
        # normalize_embeddings=True ensures vectors have L2 norm = 1,
        # making cosine similarity equivalent to dot product.
        self._model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print(f"[Embeddings] Model '{EMBEDDING_MODEL_NAME}' loaded successfully.")

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Embeds a list of document chunks.
        
        Parameters:
            texts: List of text strings to embed.
            batch_size: Batch processing size for efficient CPU inference.
            
        Returns:
            List of float embedding vectors (dimension 384 for all-MiniLM-L6-v2).
        """
        if not texts:
            return []
        
        # sentence-transformers encode returns numpy array
        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Embeds a single query string for vector search.
        """
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")
        
        embedding = self._model.encode(
            [query.strip()],
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )[0]
        return embedding.tolist()


# Convenience module-level functions
_embedding_manager = None

def get_embedding_manager() -> EmbeddingManager:
    """Returns the singleton EmbeddingManager instance."""
    global _embedding_manager
    if _embedding_manager is None:
        _embedding_manager = EmbeddingManager()
    return _embedding_manager

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Encodes a list of texts into normalized embedding vectors."""
    return get_embedding_manager().embed_texts(texts)

def embed_query(query: str) -> List[float]:
    """Encodes a single query string into a normalized embedding vector."""
    return get_embedding_manager().embed_query(query)


if __name__ == "__main__":
    print("--- Testing Embeddings Module ---")
    sample_texts = [
        "Raft is an understandable consensus protocol for distributed systems.",
        "ChromaDB stores high-dimensional embeddings and performs cosine search."
    ]
    embs = embed_texts(sample_texts)
    print(f"Generated {len(embs)} embeddings.")
    print(f"Embedding vector dimension: {len(embs[0])}")
    
    q_emb = embed_query("How does consensus work?")
    print(f"Query embedding dimension: {len(q_emb)}")
    
    # Cosine similarity test
    sim_raft = np.dot(q_emb, embs[0])
    sim_chroma = np.dot(q_emb, embs[1])
    print(f"Similarity to Raft text:    {sim_raft:.4f}")
    print(f"Similarity to Chroma text:  {sim_chroma:.4f}")
    assert sim_raft > sim_chroma, "Query should be more semantically similar to Raft text!"
    print("[PASS] Semantic ranking verification passed.")
