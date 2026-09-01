# Approach and Technologies Used — VaultMind-RAG

- **Live Application URL**: [https://vaultmind-rag.streamlit.app/](https://vaultmind-rag.streamlit.app/)
- **GitHub Repository**: [https://github.com/rohanpawar0006/vaultmind-rag](https://github.com/rohanpawar0006/vaultmind-rag)

## 1. Problem & Product Approach
Obsidian users build extensive personal knowledge graphs over months and years. However, standard search utilities (Ctrl+F, tagging, graph view) fail when users want to synthesize cross-note concepts or ask natural-language questions.

VaultMind-RAG approaches this problem by providing an in-browser, privacy-conscious knowledge assistant. The primary product requirement was **strict grounding**: the assistant must synthesize answers solely from private vault notes, explicitly cite source files, and cleanly refuse out-of-vault questions without hallucinating facts.

---

## 2. Architecture & Technical Decisions

### A. Local-First Embeddings (`sentence-transformers` / `all-MiniLM-L6-v2`)
- **Decision**: Rather than using a metered, rate-limited cloud embedding API (like OpenAI `text-embedding-3-small` or Gemini Embeddings), we implemented a local `SentenceTransformer` pipeline using `all-MiniLM-L6-v2`.
- **Rationale**: Generates 384-dimensional normalized vectors in ~15ms on CPU. Completely removes external API costs and quota exhaustion risks, ensuring 100% demo reliability.

### B. Custom Ingestion & Obsidian Normalization Pipeline (No Frameworks)
- **Decision**: Built a dedicated markdown parser and sliding-window chunker from scratch without LangChain or LlamaIndex.
- **Rationale**: Allows precise handling of Obsidian-specific syntax:
  1. YAML frontmatter extraction into chunk metadata via `python-frontmatter`.
  2. Wikilink resolution: `[[Target Note|Custom Alias]]` $\rightarrow$ `Custom Alias`.
  3. Image/transclusion stripping and block reference cleaning.
  4. Sliding-window chunker (~500 tokens / 50 token overlap) with boundary awareness (splitting at paragraphs, sentence ends, or word boundaries).

### C. In-Process Vector Database (ChromaDB)
- **Decision**: Embedded ChromaDB with DuckDB/SQLite storage and persistent HNSW index in cosine distance space.
- **Rationale**: Zero external infrastructure or Docker setup required. Persists index across runs and enables rapid similarity queries.

### D. Grounded Prompt Engineering & Anti-Hallucination Guardrails
- **Decision**: Multi-layered defense against hallucination:
  1. **Cosine Distance Filtering**: Chunks with cosine distance $> 0.70$ (similarity $< 0.30$) are filtered out before reaching the LLM. If 0 chunks remain, an instant refusal message (*"I couldn't find anything relevant in this vault"*) is returned without making an API call.
  2. **XML Context Demarcation**: Retrieved chunks are wrapped inside `<note_excerpt>` tags with explicit attributes (`source`, `title`, `tags`).
  3. **Strict Negative Constraints**: System instructions forbid external world knowledge and require explicit note attribution.

### E. User Interface with Obsidian Dark Aesthetic
- **Decision**: Streamlit frontend customized with Obsidian's dark charcoal (`#1E1E2E`) and purple (`#7C3AED`) palette.
- **Rationale**: Includes vault upload (.zip), bundled sample vault toggle (18 pre-loaded distributed systems and RAG notes), live index stats, clickable prompt suggestions, and expandable source excerpt inspectors for complete citation transparency.
