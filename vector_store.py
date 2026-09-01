"""
vector_store.py — ChromaDB Vector Store Client and Similarity Search Manager

Why ChromaDB?
1. Embedded in-process vector store requiring zero external Docker/cloud infrastructure.
2. Direct disk persistence at `data/chroma_db/`.
3. Fast HNSW (Hierarchical Navigable Small World) index for sub-millisecond cosine retrieval.
"""

import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import chromadb
from chromadb.config import Settings

from config import (
    CHROMA_DB_DIR,
    COLLECTION_NAME,
    TOP_K,
    SIMILARITY_DISTANCE_THRESHOLD
)
from embeddings import embed_texts, embed_query


class VectorStore:
    """
    Manages persistent ChromaDB vector collections, chunk ingestion, and similarity queries.
    """

    def __init__(self, persist_dir: Path = CHROMA_DB_DIR, collection_name: str = COLLECTION_NAME):
        self.persist_dir = Path(persist_dir)
        self.collection_name = collection_name
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB persistent client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.get_or_create_collection(self.collection_name)

    def get_or_create_collection(self, collection_name: str, reset: bool = False):
        """
        Retrieves or initializes the ChromaDB collection configured for cosine similarity.
        """
        if reset:
            try:
                self.client.delete_collection(name=collection_name)
            except Exception:
                pass

        # Use cosine distance space
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def reset(self):
        """Wipes the current collection to re-index fresh notes."""
        self.collection = self.get_or_create_collection(self.collection_name, reset=True)

    def add_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 64) -> int:
        """
        Embeds chunks and indexes them into ChromaDB in batches.
        
        Parameters:
            chunks: List of chunk dictionaries containing 'id', 'text', and 'metadata'.
            
        Returns:
            Number of indexed chunks.
        """
        if not chunks:
            return 0

        total_chunks = len(chunks)
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i : i + batch_size]
            
            ids = [item["id"] for item in batch]
            documents = [item["text"] for item in batch]
            
            # Sanitize metadata for ChromaDB (flat primitive types only)
            metadatas = []
            for item in batch:
                meta = item.get("metadata", {}).copy()
                # ChromaDB requires metadata values to be str, int, float, or bool
                clean_meta = {}
                for k, v in meta.items():
                    if isinstance(v, (str, int, float, bool)):
                        clean_meta[k] = v
                    elif isinstance(v, list):
                        clean_meta[k] = ", ".join(str(x) for x in v)
                    else:
                        clean_meta[k] = str(v)
                metadatas.append(clean_meta)

            # Compute embeddings via local model
            embeddings = embed_texts(documents)

            # Upsert into ChromaDB
            self.collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )

        return total_chunks

    def query(
        self,
        query_text: str,
        top_k: int = TOP_K,
        distance_threshold: float = SIMILARITY_DISTANCE_THRESHOLD
    ) -> List[Dict[str, Any]]:
        """
        Executes semantic similarity search for a user query.
        
        Parameters:
            query_text: User's natural language question.
            top_k: Max chunks to retrieve.
            distance_threshold: Maximum cosine distance threshold to filter irrelevant chunks.
            
        Returns:
            List of retrieved chunks with text, metadata, cosine distance, and similarity score.
        """
        if not query_text or not query_text.strip():
            return []

        # Generate query embedding
        query_embedding = embed_query(query_text.strip())

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, max(1, self.collection.count())),
            include=["documents", "metadatas", "distances"]
        )

        retrieved: List[Dict[str, Any]] = []
        
        if not results or not results["documents"] or not results["documents"][0]:
            return []

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]
        ids = results["ids"][0]

        for chunk_id, doc, meta, dist in zip(ids, documents, metadatas, distances):
            # With cosine space, distance in [0, 2], where 0 is identical
            # Similarity score = 1.0 - distance
            similarity = max(0.0, 1.0 - dist)

            # Keep chunk if within relevance distance threshold
            if dist <= distance_threshold:
                retrieved.append({
                    "id": chunk_id,
                    "text": doc,
                    "metadata": meta,
                    "distance": float(dist),
                    "similarity": float(similarity)
                })

        return retrieved

    def get_stats(self) -> Dict[str, Any]:
        """
        Returns stats about indexed notes and chunks.
        """
        count = self.collection.count()
        if count == 0:
            return {"total_chunks": 0, "total_notes": 0, "note_sources": []}

        # Fetch all metadatas to find unique note sources
        data = self.collection.get(include=["metadatas"])
        sources = set()
        if data and "metadatas" in data and data["metadatas"]:
            for m in data["metadatas"]:
                if m and "source" in m:
                    sources.add(m["source"])

        return {
            "total_chunks": count,
            "total_notes": len(sources),
            "note_sources": sorted(list(sources))
        }


# Singleton instance helper
_vector_store_instance = None

def get_vector_store() -> VectorStore:
    """Returns the singleton VectorStore instance."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance


if __name__ == "__main__":
    from ingest import load_notes_from_directory
    from config import SAMPLE_VAULT_DIR

    print("--- Testing Phase 2: Vector Store Ingestion & Retrieval ---")
    vs = get_vector_store()
    print("Resetting test collection...")
    vs.reset()

    print(f"Ingesting sample vault from {SAMPLE_VAULT_DIR}...")
    sample_chunks = load_notes_from_directory(SAMPLE_VAULT_DIR)
    indexed_count = vs.add_chunks(sample_chunks)
    print(f"Indexed {indexed_count} chunks successfully.")

    stats = vs.get_stats()
    print(f"Vector Store Stats: {stats['total_notes']} notes, {stats['total_chunks']} chunks.")

    # Test Query 1: Raft vs Paxos
    test_q1 = "How does Raft leader election work and how does it achieve consensus?"
    print(f"\nQuery: '{test_q1}'")
    results1 = vs.query(test_q1, top_k=3)
    for idx, res in enumerate(results1, 1):
        print(f"[{idx}] Source: {res['metadata']['source']} | Score: {res['similarity']:.4f} (dist: {res['distance']:.4f})")
        print(f"    Snippet: {res['text'][:150]}...\n")

    assert len(results1) > 0, "Should retrieve relevant chunks for Raft question"
    top_source = results1[0]["metadata"]["source"]
    assert "Raft" in top_source or "Consensus" in top_source, f"Expected Raft note, got {top_source}"
    print("[PASS] Query 1 retrieval passed.")

    # Test Query 2: Vector Databases
    test_q2 = "What vector database is used and what are its properties?"
    print(f"\nQuery: '{test_q2}'")
    results2 = vs.query(test_q2, top_k=3)
    for idx, res in enumerate(results2, 1):
        print(f"[{idx}] Source: {res['metadata']['source']} | Score: {res['similarity']:.4f} (dist: {res['distance']:.4f})")
    assert any("Vector Databases.md" in r["metadata"]["source"] for r in results2)
    print("[PASS] Query 2 retrieval passed.")

    print("\n--- Phase 2 Vector Store Verification Completed Successfully! ---")
