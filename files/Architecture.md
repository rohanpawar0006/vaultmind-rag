# Architecture.md — VaultMind-RAG

## 1. High-Level Flow

```
User uploads vault (.zip of .md files)
        │
        ▼
[Ingestion] → parse .md, strip Obsidian syntax, extract metadata
        │
        ▼
[Chunking] → split into ~500-token overlapping chunks, tag with source note
        │
        ▼
[Embedding] → embed each chunk
        │
        ▼
[Vector Store] → store chunk embeddings + metadata (ChromaDB, persisted locally)
        │
        ▼
User asks question in chat UI
        │
        ▼
[Query Embedding] → embed the question
        │
        ▼
[Retrieval] → similarity search, top-k chunks returned
        │
        ▼
[Generation] → LLM answers using ONLY retrieved chunks as context
        │
        ▼
[Response] → answer + list of source note(s) shown in UI
```

## 2. Folder Structure

```
vaultmind-rag/
├── app.py                  # Streamlit entrypoint (UI + orchestration)
├── ingest.py                # vault loading, markdown parsing, chunking
├── embeddings.py             # embedding model wrapper
├── vector_store.py           # ChromaDB setup, add/query functions
├── rag_chain.py               # retrieval + prompt construction + LLM call
├── config.py                   # constants: chunk size, top-k, model names
├── sample_vault/                # bundled demo notes (fallback if no upload)
│   └── *.md
├── data/
│   └── chroma_db/                # persisted vector store (gitignored if large)
├── requirements.txt
├── .env.example                    # API key placeholder, never committed
├── README.md
├── PRD.md / Architecture.md / Rules.md / Phases.md / Design.md / Memory.md
```

## 3. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.13 | matches existing environment |
| UI | Streamlit | fastest path to a deployable, demoable UI |
| Markdown parsing | `python-frontmatter` + regex/`markdown-it-py` | strip frontmatter, wikilinks, tags cleanly |
| Chunking | custom sliding-window splitter | full control, easy to explain in interview |
| Embeddings | `sentence-transformers` (local, e.g. `all-MiniLM-L6-v2`) | free, no API key needed, works offline — reduces deployment risk |
| Vector store | ChromaDB (local, persisted) | zero-infra, embeds directly in the app |
| LLM (generation) | Anthropic Claude API or Google Gemini free tier | pick whichever key is available; keep swappable via config |
| Deployment | Streamlit Community Cloud | free, connects to GitHub, public URL |

## 4. Key Design Decisions
- **Local embeddings, not API embeddings**: avoids rate limits/cost during grading and removes a point of failure from the live demo.
- **Bundled sample vault**: if the evaluator doesn't upload their own notes, the app still works out of the box — this directly protects the "must be accessible and working at time of submission" requirement.
- **Strict grounding prompt**: the generation step is instructed to answer only from retrieved context and explicitly say when the vault doesn't contain the answer, to avoid hallucination.
- **Custom RAG pipeline over a framework** (e.g. no LangChain): demonstrates understanding of each step rather than framework fluency.
