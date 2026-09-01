---
title: Embedding Models
tags:
  - embeddings
  - ml
  - sentence-transformers
date: 2026-08-18
status: completed
---

# Embedding Models for Semantic Search

Embedding models translate textual information into dense vectors where semantic proximity corresponds to geometric closeness in high-dimensional vector space.

## Model Classes

1. **Local Open-Source Models (Sentence-Transformers)**:
   - `all-MiniLM-L6-v2`: 384 dimensions, 22.7M parameters, ~80MB on disk. It delivers extraordinary speed on CPU while retaining solid semantic search performance on MTEB benchmarks.
   - `bge-small-en-v1.5` / `bge-base-en-v1.5`: High accuracy embedding models fine-tuned with contrastive learning.
   - *Why local?*: Zero API costs, no rate limits, offline execution, predictable low latency.

2. **API-Based Cloud Models**:
   - `text-embedding-004` (Google Gemini): 768 dimensions with task-specific prefixing.
   - `text-embedding-3-small` (OpenAI): 1536 dimensions with matryoshka dimensionality reduction.

## Normalization and Distance
When sentence embeddings are unit-normalized ($||v|| = 1$), dot product and cosine similarity become mathematically identical:
$$\text{Cosine}(A, B) = \frac{A \cdot B}{||A|| \times ||B||} = A \cdot B$$
This allows vector databases like [[Vector Databases]] to execute fast inner-product indexing.
