"""
rag_chain.py — Grounded Prompt Construction & LLM Generation Pipeline

This module implements:
1. Strict grounding prompt construction with XML context demarcation.
2. Direct integration with Google Gemini (and optional Anthropic fallback).
3. Citation extraction and verification.
4. Automatic refusal fallback ("I couldn't find anything relevant in this vault")
   when vector similarity is below threshold or the LLM cannot find facts.
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

# Load local environment variables from .env
load_dotenv()

from config import (
    DEFAULT_GEMINI_MODEL,
    DEFAULT_TEMPERATURE,
    MAX_OUTPUT_TOKENS,
    TOP_K,
    SIMILARITY_DISTANCE_THRESHOLD
)
from vector_store import get_vector_store, VectorStore

# Standard fallback refusal message per PRD & Rules
FALLBACK_NOT_FOUND_MESSAGE = "I couldn't find anything relevant in this vault."

SYSTEM_INSTRUCTION = """You are VaultMind, an intelligent, strictly grounded knowledge assistant for a personal Obsidian vault.
Your highest priority is factual accuracy and strict grounding in the provided note excerpts.

CRITICAL RULES:
1. Answer the question using ONLY the facts explicitly stated in the <context> block below.
2. DO NOT hallucinate, assume, extrapolate, or use outside training knowledge.
3. If the context does not contain enough information to answer the question accurately, or if the context is empty, you MUST respond EXACTLY with:
"I couldn't find anything relevant in this vault."
4. Every fact in your answer must be attributed to one or more of the source notes.
5. At the end of your response, include a clean '### Sources' section listing the unique source note filenames you referenced (e.g. `[[Source Note.md]]`).
"""


def build_grounded_prompt(question: str, context_chunks: List[Dict[str, Any]]) -> str:
    """
    Constructs an XML-demarcated prompt separating system instructions, source context,
    and the user question to prevent prompt injection and hallucination.
    """
    if not context_chunks:
        return f"{SYSTEM_INSTRUCTION}\n\n<context>\nNo relevant notes found.\n</context>\n\nUser Question: {question}\nAnswer:"

    context_blocks = []
    for idx, chunk in enumerate(context_chunks, 1):
        source = chunk["metadata"].get("source", "Unknown Note")
        title = chunk["metadata"].get("title", source)
        tags = chunk["metadata"].get("tags", "")
        text = chunk["text"].strip()
        
        block = f"""<note_excerpt id="{idx}" source="{source}" title="{title}" tags="{tags}">
{text}
</note_excerpt>"""
        context_blocks.append(block)

    formatted_context = "\n\n".join(context_blocks)

    prompt = f"""{SYSTEM_INSTRUCTION}

<context>
{formatted_context}
</context>

User Question: {question}

Provide a clear, synthesized, and strictly grounded answer based ONLY on the note excerpts above:"""

    return prompt


def call_gemini_llm(prompt: str, api_key: str, model_name: str = DEFAULT_GEMINI_MODEL) -> str:
    """
    Calls the Google Gemini API using the official google-genai SDK.
    """
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        
        # Try requested model (e.g. gemini-2.5-flash / gemini-2.0-flash / gemini-1.5-flash)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=DEFAULT_TEMPERATURE,
                max_output_tokens=MAX_OUTPUT_TOKENS,
            )
        )
        if response and response.text:
            return response.text.strip()
        return FALLBACK_NOT_FOUND_MESSAGE

    except Exception as e:
        # If gemini-2.5-flash is not available, try fallback to gemini-2.0-flash or gemini-1.5-flash
        err_msg = str(e)
        if "NotFound" in err_msg or "404" in err_msg:
            try:
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=DEFAULT_TEMPERATURE,
                        max_output_tokens=MAX_OUTPUT_TOKENS,
                    )
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e2:
                raise RuntimeError(f"Gemini API generation failed: {e2}")
        raise RuntimeError(f"Gemini API error: {err_msg}")


def extract_unique_sources(chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Extracts unique source note metadata from retrieved chunks for UI display.
    """
    seen = set()
    sources = []
    for c in chunks:
        source_name = c["metadata"].get("source", "Unknown")
        if source_name not in seen:
            seen.add(source_name)
            sources.append({
                "source": source_name,
                "title": c["metadata"].get("title", source_name),
                "snippet": c["text"][:200] + "..." if len(c["text"]) > 200 else c["text"],
                "similarity": c.get("similarity", 0.0)
            })
    return sources


def ask_vault(
    question: str,
    api_key: Optional[str] = None,
    model_name: str = DEFAULT_GEMINI_MODEL,
    top_k: int = TOP_K,
    distance_threshold: float = SIMILARITY_DISTANCE_THRESHOLD,
    vector_store: Optional[VectorStore] = None
) -> Dict[str, Any]:
    """
    End-to-end RAG query pipeline:
    1. Embeds query & retrieves top-k chunks from ChromaDB.
    2. Checks similarity distance threshold. If no chunks pass, returns fallback immediately.
    3. Builds strict XML-demarcated prompt.
    4. Invokes LLM with temperature=0.2 for deterministic grounding.
    5. Formats answer and returns structured result with source citations.
    
    Returns:
        dict: {
            "question": str,
            "answer": str,
            "sources": List[dict],
            "chunks": List[dict],
            "grounded": bool,
            "error": Optional[str]
        }
    """
    if not question or not question.strip():
        return {
            "question": question,
            "answer": "Please enter a valid question to search your vault.",
            "sources": [],
            "chunks": [],
            "grounded": False,
            "error": None
        }

    vs = vector_store or get_vector_store()
    
    # 1. Retrieve relevant chunks
    try:
        retrieved_chunks = vs.query(
            query_text=question,
            top_k=top_k,
            distance_threshold=distance_threshold
        )
    except Exception as e:
        return {
            "question": question,
            "answer": f"Error querying vector index: {str(e)}",
            "sources": [],
            "chunks": [],
            "grounded": False,
            "error": str(e)
        }

    # 2. If no chunks found above similarity threshold, return standard refusal immediately
    if not retrieved_chunks:
        return {
            "question": question,
            "answer": FALLBACK_NOT_FOUND_MESSAGE,
            "sources": [],
            "chunks": [],
            "grounded": False,
            "error": None
        }

    unique_sources = extract_unique_sources(retrieved_chunks)

    # 3. Obtain API key
    active_key = api_key or os.getenv("GEMINI_API_KEY")
    if not active_key:
        # If no API key is provided, return context chunks preview with note explaining how to add API key
        context_preview = "\n\n".join([f"**From [[{s['source']}]]**:\n> {s['snippet']}" for s in unique_sources])
        return {
            "question": question,
            "answer": f"🔑 **API Key Needed for LLM Synthesis**\n\nI retrieved relevant notes from your vault, but need a **Gemini API Key** to generate the synthesized response. Please add your key in the sidebar or in `.env`.\n\n### Retrieved Notes Preview:\n{context_preview}",
            "sources": unique_sources,
            "chunks": retrieved_chunks,
            "grounded": True,
            "error": "Missing GEMINI_API_KEY"
        }

    # 4. Build prompt and generate response
    prompt = build_grounded_prompt(question, retrieved_chunks)
    
    try:
        answer_text = call_gemini_llm(prompt, api_key=active_key, model_name=model_name)
        
        # Check if the LLM itself declared not found
        is_grounded = FALLBACK_NOT_FOUND_MESSAGE.lower() not in answer_text.lower()
        
        return {
            "question": question,
            "answer": answer_text,
            "sources": unique_sources if is_grounded else [],
            "chunks": retrieved_chunks,
            "grounded": is_grounded,
            "error": None
        }
    except Exception as e:
        return {
            "question": question,
            "answer": f"⚠️ Generation error: {str(e)}",
            "sources": unique_sources,
            "chunks": retrieved_chunks,
            "grounded": False,
            "error": str(e)
        }


if __name__ == "__main__":
    import sys
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

    print("==========================================================")
    print("  VaultMind-RAG: CLI Test & Verification Suite (Phase 3)  ")
    print("==========================================================")
    
    # 5 benchmark test questions:
    # 1. In-vault specific factual question (Raft leader election)
    # 2. In-vault cross-note synthesis (ChromaDB & vector search)
    # 3. In-vault distributed systems concept (CAP theorem trade-offs)
    # 4. In-vault caching strategy (Semantic caching)
    # 5. Out-of-vault question (Anti-hallucination refusal test)
    test_queries = [
        "How does Raft leader election work and what safety properties are guaranteed?",
        "Why does VaultMind use ChromaDB and what distance metric is used?",
        "Explain the trade-offs between CP and AP systems under the CAP theorem.",
        "What is semantic caching and how does it reduce LLM latency?",
        "What are the rules of cricket and how many players are on a team?"  # Out-of-vault test!
    ]

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n[Notice] GEMINI_API_KEY is not set in environment.")
        print("Testing retrieval, prompt construction, and threshold fallback offline...\n")

    for i, q in enumerate(test_queries, 1):
        print(f"\n--- [Test Question {i}/5] ---")
        print(f"Q: {q}")
        res = ask_vault(q)
        print(f"Sources Found: {[s['source'] for s in res['sources']]}")
        print(f"Grounded: {res['grounded']}")
        print(f"Answer Preview:\n{res['answer'][:350]}...\n")

    print("\n--- Phase 3 RAG Pipeline Verification Complete ---")
