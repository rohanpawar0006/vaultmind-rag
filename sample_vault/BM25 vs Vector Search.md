---
title: BM25 vs Vector Search
tags:
  - search
  - bm25
  - vector-search
  - hybrid-search
date: 2026-08-26
status: completed
---

# Sparse (BM25) vs Dense (Vector) Search

Information retrieval systems employ two complementary paradigms for finding relevant documents:

## 1. Sparse Lexical Search (BM25 / TF-IDF)
- Matches exact tokens, keywords, error codes, and unique identifiers (e.g. `ERR_CONN_REFUSED`, `UUID-4881`).
- Uses Term Frequency-Inverse Document Frequency (TF-IDF) scoring penalizing high-frequency background words.
- *Limitation*: Vocabulary mismatch problem (cannot understand synonyms, e.g. "car" vs "automobile").

## 2. Dense Semantic Search (Vector Embeddings)
- Represents passages as continuous vectors using [[Embedding Models]].
- Captures abstract conceptual meaning, paraphrase detection, and multilingual relationships.
- *Limitation*: Can struggle with rare technical terms, exact version numbers, and short queries without semantic context.

## 3. Hybrid Search with Reciprocal Rank Fusion (RRF)
Combining both approaches yields optimal retrieval accuracy:
$$RRF\_Score(d) = \sum_{m \in \{\text{BM25}, \text{Vector}\}} \frac{1}{k + \text{Rank}_m(d)}$$
where $k \approx 60$.

For simple markdown vaults, vector search alone provides strong recall when chunk sizes are balanced per [[Chunking Strategies]].
