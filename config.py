"""
config.py — Global Configuration & Constants for VaultMind-RAG

Centralized settings for chunking, embeddings, ChromaDB vector store,
retrieval thresholds, and LLM generation.
"""

from pathlib import Path
import os

# Base paths
BASE_DIR = Path(__file__).resolve().parent
SAMPLE_VAULT_DIR = BASE_DIR / "sample_vault"
DATA_DIR = BASE_DIR / "data"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"
COLLECTION_NAME = "obsidian_vault_notes"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

# Chunking Configuration (approx ~500 tokens, 50 tokens overlap)
# Using character-based chunking with word boundaries: ~3-4 chars per token
CHUNK_SIZE = 1200  # characters (~300-400 words / ~400-500 tokens)
CHUNK_OVERLAP = 200  # characters (~50 words / ~50-70 tokens)
MIN_CHUNK_SIZE = 80  # discard tiny residual chunks

# Embeddings Configuration
# Local sentence-transformers model (fast, free, offline, 384-dimensional)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Retrieval Configuration
TOP_K = 4  # Number of relevant chunks retrieved per question
SIMILARITY_DISTANCE_THRESHOLD = 0.70  # Max cosine distance (similarity >= 0.30) to filter irrelevant chunks
MIN_SIMILARITY_SCORE = 0.30  # Minimum similarity score required

# LLM Generation Configuration
# Default to Google Gemini Flash (high quality, fast response)
DEFAULT_GEMINI_MODEL = "gemini-3.6-flash"
DEFAULT_TEMPERATURE = 0.2  # Low temperature for strict factual grounding
MAX_OUTPUT_TOKENS = 1024
