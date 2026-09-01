---
title: Evaluation Metrics for RAG
tags:
  - rag
  - evaluation
  - metrics
date: 2026-08-29
status: completed
---

# Quantitative Evaluation Metrics for RAG Pipelines

Evaluating RAG architectures requires measuring both the retrieval quality and generation fidelity.

## The RAG Triad Metrics

1. **Context Relevance (Retrieval Precision)**:
   - Evaluates whether the retrieved chunks are relevant to the user query without containing extraneous noise.
   - Low context relevance indicates suboptimal [[Chunking Strategies]] or low semantic alignment in [[Embedding Models]].

2. **Groundedness / Faithfulness (Generation Fidelity)**:
   - Measures whether all factual claims in the generated response can be traced back directly to the retrieved context chunks.
   - Low faithfulness indicates severe model hallucination (see [[RAG Grounding & Hallucinations]]).

3. **Answer Relevance**:
   - Assesses whether the generated response directly answers the user's specific prompt, regardless of whether context was sufficient.

## Traditional IR Metrics
- **Hit Rate @ K**: Percentage of queries where the true ground truth note was in the top-k retrieved list.
- **MRR (Mean Reciprocal Rank)**: Emphasizes ranking the correct source note in position 1.
- **NDCG@K**: Normalized Discounted Cumulative Gain accounting for graded relevance.
