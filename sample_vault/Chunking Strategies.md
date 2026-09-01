---
title: Chunking Strategies
tags:
  - chunking
  - rag
  - preprocessing
date: 2026-08-17
status: completed
---

# Chunking Strategies for Knowledge Retrieval

Chunking is the process of breaking long unstructured documents into smaller segments suitable for processing by [[Embedding Models]] and LLMs with limited context windows.

## Core Chunking Methods

1. **Fixed-Size Sliding Window**:
   - Chunks are determined by character or token count with a fixed overlap window (e.g. 500 tokens with 50-token overlap).
   - *Advantage*: Deterministic chunk lengths, preventing model context overflow.
   - *Disadvantage*: Can split a sentence or table across chunk boundaries.

2. **Sentence & Paragraph Splitting**:
   - Splits on natural language boundaries (`\n\n`, `. `, `? `, `! `).
   - Preserves semantic cohesion of ideas.

3. **Hierarchical / Header-Based Chunking**:
   - Splits documents along Markdown header hierarchies (`#`, `##`, `###`).
   - Retains context paths (e.g. `Architecture > Storage > ChromaDB`) in the chunk metadata.

## Sliding Window Parameters in VaultMind
In VaultMind-RAG, we use a sliding window of ~1200 characters (~400-500 tokens) with a 200-character overlap (~50 tokens). The overlap ensures that sentences crossing boundary edges are not lost to retrieval.
