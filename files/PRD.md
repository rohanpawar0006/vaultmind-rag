# PRD.md — VaultMind-RAG (Obsidian Vault RAG Knowledge Assistant)

## 1. Problem Statement
People who take notes in Obsidian accumulate hundreds of markdown files over time and lose the ability to quickly recall or connect what they've written. Manual search (Ctrl+F, tags, backlinks) doesn't answer natural-language questions or synthesize across multiple notes.

## 2. Goal
Build an MVP that lets a user ask natural-language questions about their own Obsidian vault and receive answers grounded in their notes, with citations back to the source file(s).

## 3. Target User
- Primary: the evaluator/interviewer testing this as a Build Sprint submission
- Secondary (real-world framing): an Obsidian user (student, researcher, engineer) with a vault of 20–500+ notes who wants to query their own knowledge base conversationally

## 4. Core Features (MVP scope — must have)
1. Load a vault: either upload a `.zip` of markdown files or use a bundled sample vault (fallback for demo reliability)
2. Parse and chunk notes, preserving note title/filename as metadata
3. Embed chunks and store in a vector database
4. Accept a natural-language question via a chat-style UI
5. Retrieve top-k relevant chunks and generate a grounded answer using an LLM
6. Show which note(s) the answer was drawn from (citation/source links)
7. Handle "not found in vault" gracefully (don't hallucinate an answer if nothing relevant is retrieved)

## 5. Explicitly Out of Scope (for MVP)
- Live sync with an actual Obsidian install / plugin
- Multi-user accounts or auth
- Editing or writing back to the vault
- Support for non-markdown attachments (images, PDFs, canvases)
- Real-time re-indexing on file change (re-index is a manual "rebuild index" button instead)

## 6. Success Criteria
- Deployed, publicly accessible link works at time of submission
- A user can upload/select a vault, ask at least 3 different questions, and get relevant, cited answers
- Answers are grounded (no fabricated facts not present in the notes)
- Repo has a clear README explaining setup, architecture, and how to run locally

## 7. Stretch Goals (only if time remains after MVP is solid)
- Highlight the exact matched passage within the cited note
- Support follow-up/multi-turn questions with conversation memory
- Simple relevance score or "confidence" indicator shown to the user
