# Phases.md — VaultMind-RAG: Build Sprint Plan (7 Days)

## Phase 0 — Setup (Day 1, morning)
- Init GitHub repo, folder structure per Architecture.md
- Set up virtual environment, `requirements.txt`
- Create a small sample vault (15–20 markdown notes on a topic you know well, so you can sanity-check answers)
- **Done when:** repo exists, env installs cleanly, sample vault committed

## Phase 1 — Ingestion & Chunking (Day 1 afternoon – Day 2)
- Write `ingest.py`: load `.md` files from a folder or zip, strip frontmatter/wikilink syntax, keep title + path as metadata
- Write chunking function: sliding window, ~500 tokens, overlap ~50 tokens
- Test standalone: print chunk count and a few sample chunks from the sample vault
- **Done when:** running `ingest.py` on the sample vault produces a clean list of (text, metadata) chunks

## Phase 2 — Embeddings & Vector Store (Day 3)
- Write `embeddings.py`: wrap `sentence-transformers` model, embed a list of texts
- Write `vector_store.py`: init ChromaDB collection, add chunks with embeddings + metadata, query top-k by similarity
- Test standalone: embed sample vault, run a manual query, confirm sensible chunks come back
- **Done when:** a hardcoded test query returns relevant chunks from the sample vault

## Phase 3 — RAG Generation (Day 4)
- Write `rag_chain.py`: given a question, retrieve top-k, build a grounded prompt, call the LLM
- Prompt must instruct: answer only from context, cite source note filenames, say "not found" if context is insufficient
- Test standalone via a simple CLI loop before touching the UI
- **Done when:** CLI-based Q&A over the sample vault gives correct, cited, non-hallucinated answers for at least 5 test questions

## Phase 4 — UI (Day 5)
- Build `app.py` in Streamlit: file upload (or "use sample vault" toggle), chat input, chat history display, source citations shown per answer
- Wire in a "rebuild index" button for re-ingesting after a new upload
- **Done when:** full flow works locally end-to-end through the browser

## Phase 5 — Deployment (Day 6)
- Push to GitHub, connect repo to Streamlit Community Cloud
- Add API keys via Streamlit Secrets
- Test the live link fresh (incognito) exactly as an evaluator would
- **Done when:** live link works from a cold start with no local setup

## Phase 6 — Polish & Submission (Day 7)
- Write README.md: setup instructions, architecture summary, tech choices, known limitations
- Write the short "approach and technologies used" writeup for submission
- Final pass: test edge cases (empty query, gibberish query, very large vault upload)
- Submit: GitHub link + live demo link + writeup
- **Done when:** all 3 submission requirements are ready and the live link has been verified working within the last hour before sending
