---
title: Prompt Engineering Patterns
tags:
  - prompting
  - llm
  - system-prompts
date: 2026-08-31
status: completed
---

# Prompt Engineering Patterns for Grounded RAG

Carefully structured prompts are critical for enforcing deterministic behavior and preventing hallucinations in knowledge retrieval systems.

## Key Prompt Components

1. **System Persona & Role Definition**:
   Establishes the identity of the AI as a strict, factual assistant dedicated to referencing private notes.

2. **Negative Constraints ("Refusal Criteria")**:
   Explicit rules forcing the model to refuse speculative answers:
   *"Do NOT make assumptions, synthesize unverified claims, or extrapolate outside the provided notes. If the note excerpts do not contain the answer, say: 'I couldn't find anything relevant in this vault.'"*

3. **Demarcated Context Injection**:
   Using clear XML/Markdown tags to separate system instructions from dynamic user notes:
   ```markdown
   === CONTEXT FROM VAULT ===
   [Note: Raft Protocol.md]
   ...
   ==========================
   ```

4. **Citation Format Mandate**:
   Specifying the exact format for citations (e.g. `[Source: Note Name.md]`).

See [[RAG Grounding & Hallucinations]] and [[Streamlit UI Design Patterns]].
