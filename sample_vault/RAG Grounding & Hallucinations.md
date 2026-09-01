---
title: RAG Grounding & Hallucinations
tags:
  - rag
  - prompting
  - llm-safety
date: 2026-08-19
status: completed
---

# Grounding LLMs and Mitigating Hallucinations in RAG

Hallucination in LLMs occurs when the model produces factually inaccurate or fabricated assertions with high linguistic confidence. In Retrieval-Augmented Generation (RAG), strict grounding ensures responses are backed by verified source notes.

## Anti-Hallucination Techniques

1. **Strict Negative Constraints in System Prompts**:
   - Explicitly instruct the model: *"Answer the question using ONLY the provided context notes. If the context does not contain sufficient facts to answer the question, state clearly: 'I couldn't find anything relevant in this vault.'"*
2. **Context Separation & XML/Markdown Delimiters**:
   - Wrap context chunks in identifiable tags (e.g. `<vault_note filename="Note.md">...</vault_note>`) so the model clearly demarcates ground truth from the prompt instructions.
3. **Citation Requirement**:
   - Mandate that the model reference the specific note titles for every claim it makes.
4. **Distance Threshold Fallbacks**:
   - If the vector search cosine distance exceeds a safety threshold (e.g., $d > 0.85$), bypass the LLM completely and return an instant fallback message to save token costs and prevent false reasoning.

See also [[Evaluation Metrics for RAG]] and [[Chunking Strategies]].
