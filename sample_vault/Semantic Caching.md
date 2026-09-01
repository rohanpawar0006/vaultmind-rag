---
title: Semantic Caching
tags:
  - caching
  - llm-cost
  - performance
date: 2026-08-25
status: completed
---

# Semantic Caching for LLM Pipelines

Traditional web caching relies on exact string equality of URLs or SQL queries. In LLM applications, two queries with completely different wording can have identical semantic meaning (e.g. *"How does Raft work?"* vs *"Explain the Raft consensus protocol"*).

## How Semantic Caching Works

1. When a user submits query $Q$, calculate embedding $E(Q)$ using [[Embedding Models]].
2. Query a low-latency vector cache using approximate nearest neighbors.
3. If similarity $\text{sim}(E(Q), E(Q_{\text{cached}})) \ge \tau$ (threshold, e.g. 0.94), return the cached response immediately.
4. If miss, execute the full RAG pipeline and store $(Q, E(Q), \text{Response})$ in the cache.

## Benefits
- **Sub-10ms Response Times**: Eliminates the 1000ms–3000ms latency of LLM API roundtrips.
- **Cost Reduction**: Up to 40–70% reduction in API token expenses for frequent inquiries.
- **Resilience**: Provides high availability during LLM provider downtime.

See [[Latency vs Throughput in LLM Pipelines]] and [[Vector Databases]].
