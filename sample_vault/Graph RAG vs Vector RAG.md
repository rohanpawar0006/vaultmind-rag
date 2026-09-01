---
title: Graph RAG vs Vector RAG
tags:
  - knowledge-graphs
  - graph-rag
  - vector-rag
date: 2026-09-01
status: completed
---

# Graph RAG vs Vector RAG: Connecting the Dots

Standard vector-based RAG retrieves individual chunks based on cosine similarity. However, complex multi-hop queries spanning distant themes often require knowledge graphs.

## Comparison

| Feature | Vector RAG | Graph RAG |
|---|---|---|
| Index Structure | Flat / HNSW vector index in [[Vector Databases]] | Knowledge graph of entities & relationships |
| Retrieval Unit | Text chunks (paragraphs) | Subgraphs, entity triples & community summaries |
| Best For | Specific factual recall, passage lookup | Global summarization, multi-hop reasoning across themes |
| Computational Cost | Low (fast embedding & ANN search) | High (LLM-assisted graph extraction during indexing) |

## Obsidian's Graph View Synergy
Obsidian naturally records explicit entity links through `[[wikilinks]]` (see [[Obsidian Markdown Syntax]]). While VaultMind-RAG uses dense vector retrieval for low latency and zero external dependencies, Obsidian's internal backlinks provide the structural blueprint for future Graph RAG extensions.
