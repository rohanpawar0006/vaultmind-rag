---
title: Latency vs Throughput in LLM Pipelines
tags:
  - performance
  - latency
  - throughput
  - llm-ops
date: 2026-08-30
status: completed
---

# Latency vs Throughput in LLM & RAG Pipelines

Optimizing AI serving infrastructure requires distinct trade-offs between end-to-end response time (Latency) and total completed queries per unit time (Throughput).

## Latency Breakdown in a RAG Query

A standard RAG query latency consists of four sequential stages:
1. **Preprocessing & Embedding**: Query embedding latency using local CPU/GPU (~10–30ms with [[Embedding Models]] like `all-MiniLM-L6-v2`).
2. **Vector Index Lookup**: ANN search in [[Vector Databases]] like ChromaDB (~2–15ms).
3. **Time to First Token (TTFT)**: LLM prefill time over context chunks (~200–800ms depending on prompt length).
4. **Inter-Token Latency (ITL)**: Autoregressive token generation speed (typically 30–80 tokens/sec).

## Optimization Levers
- **Local vs Cloud Embeddings**: Local embeddings eliminate external network roundtrips.
- **Semantic Caching**: Implements immediate return for similar queries (see [[Semantic Caching]]).
- **Chunk Size Tuning**: Smaller, focused chunks reduce LLM prompt prefill time.
