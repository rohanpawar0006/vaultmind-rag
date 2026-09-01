# Rules.md — VaultMind-RAG: Build Constraints & AI Collaboration Rules

## 1. Libraries — Allowed
- `streamlit` — UI
- `sentence-transformers` — local embeddings
- `chromadb` — vector store
- `python-frontmatter`, `markdown-it-py` or plain `re` — markdown parsing/cleaning
- `anthropic` or `google-generativeai` — LLM generation (pick one, keep swappable)
- `python-dotenv` — local env var loading
- Standard library: `os`, `pathlib`, `zipfile`, `re`, `json`

## 2. Libraries — Avoid (for this MVP)
- LangChain / LlamaIndex — adds abstraction that obscures understanding of the underlying RAG mechanics; build the pipeline by hand instead
- Any paid/metered embedding API as the primary path — keep local embeddings as default so the demo never breaks on quota
- Heavy web frameworks (Flask/FastAPI + separate frontend) — unnecessary complexity for a 1-week MVP; Streamlit alone is sufficient
- Any library requiring a GPU or large model download that risks failing on Streamlit Cloud's free tier

## 3. API Key & Secrets Handling
- Never hardcode API keys in source files
- Use `.env` locally (gitignored) and Streamlit Cloud's "Secrets" manager in deployment
- `.env.example` in the repo shows required variable names with placeholder values only

## 4. Error Handling Expectations
- If the LLM API call fails (rate limit, network, bad key): show a clear in-UI error message, don't crash the app
- If a user uploads a non-.md or corrupted zip: validate and show a friendly error, don't stack-trace to the user
- If retrieval returns no relevant chunks above a similarity threshold: respond "I couldn't find anything relevant in this vault" instead of forcing the LLM to answer anyway
- Wrap all external calls (embedding, LLM, file parsing) in try/except with logging

## 5. What the AI (coding assistant) Should Do
- Build one phase at a time per Phases.md, not the whole app in one shot
- Ask before introducing a new dependency not listed in "Allowed" above
- Keep functions small and single-purpose so each piece can be tested independently
- Write inline comments explaining *why*, not just *what*, especially in the RAG/prompt logic — this needs to be explainable in an interview
- Update Memory.md at the end of each phase with what was completed and what's next

## 6. What the AI Should NOT Do
- Should not silently swap the vector store, embedding model, or LLM provider without flagging it
- Should not add authentication, multi-user support, or database persistence beyond what PRD.md scopes
- Should not fabricate sample data claims (e.g. don't claim the sample vault covers topics it doesn't)
- Should not skip error handling to "get it working" — a broken live demo fails the core submission requirement
