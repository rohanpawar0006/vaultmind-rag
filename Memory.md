# Memory.md — VaultMind-RAG Progress & Interview Knowledge

## 1. Project Overview
VaultMind-RAG is a lightweight, strictly-grounded RAG knowledge assistant designed for Obsidian vaults. It ingests markdown notes, parses metadata and Obsidian-specific constructs (`[[wikilinks]]`, tags, YAML frontmatter), embeds text locally via `sentence-transformers` (`all-MiniLM-L6-v2`), stores vector chunks in an embedded ChromaDB store, and delivers factually grounded answers with source citations using Google Gemini.

---

## 2. Phase Execution Status

| Phase | Description | Status | Key Deliverables |
|---|---|---|---|
| **Phase 0** | Setup & Sample Vault | **Completed** | Folder structure, `config.py`, `requirements.txt`, `.env.example`, `.gitignore`, 18 realistic sample notes |
| **Phase 1** | Ingestion & Chunking | **Completed** | `ingest.py` (zip/folder loader, frontmatter stripper, wikilink cleaner, sliding-window chunker), unit test suite in `tests/test_ingest.py` |
| **Phase 2** | Embeddings & Vector Store | **Completed** | `embeddings.py` (MiniLM wrapper), `vector_store.py` (ChromaDB persistence, cosine distance index, query top-k) |
| **Phase 3** | RAG Generation | **Completed** | `rag_chain.py` (strict grounding prompt, distance threshold cutoff, fallback triggers, source citation formatting, CLI test) |
| **Phase 4** | Streamlit UI | **Completed** | `app.py` (Obsidian dark theme, zip upload + sample toggle, interactive chat, source chips, expandable snippet inspector, index rebuild) |
| **Phase 5 & 6** | Deployment & Documentation | **Completed** | `README.md`, `Approach.md` submission writeup, end-to-end verification |

---

## 3. Key Architecture & Design Decisions
1. **Local Embeddings (`all-MiniLM-L6-v2`)**:
   - Runs locally in-memory on CPU (~80MB model, 384-dimensions).
   - Prevents quota failures, rate limits, and network latency during demos.
2. **Embedded Vector Store (ChromaDB)**:
   - In-process vector database stored at `data/chroma_db`.
   - Zero-infra setup, seamless persistence, fast cosine similarity lookup.
3. **Strict Grounding & Anti-Hallucination**:
   - System prompts forbid speculative extrapolation.
   - Distance threshold ($d > 0.70$) triggers a graceful fallback (*"I couldn't find anything relevant in this vault"*).
4. **Bundled Fallback Vault (`sample_vault/`)**:
   - 18 high-quality markdown notes covering distributed systems, consensus (Raft/Paxos), RAG engineering, and embeddings.
   - Ensures immediate evaluation without requiring the user to supply their own files.
5. **No Heavy Framework Abstractions**:
   - Built directly in Python without LangChain to maintain simplicity and crystal-clear interview explainability.

---

## 4. Verification & Testing Summary
- `tests/test_ingest.py`: Verified frontmatter extraction, wikilink normalization, callout cleaning, and sliding chunker.
- `vector_store.py`: Verified batch ingestion (26 chunks across 18 notes) and cosine similarity retrieval.
- `rag_chain.py`: Tested across 5 benchmark questions covering in-vault multi-note synthesis and out-of-vault refusal.
