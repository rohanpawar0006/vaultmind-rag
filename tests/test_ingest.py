"""
tests/test_ingest.py — Unit Tests for Ingestion & Sanitization Engine
"""

import io
import sys
import zipfile
from pathlib import Path

# Add project root to sys.path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingest import sanitize_obsidian_markdown, chunk_document, load_notes_from_zip, load_notes_from_directory
from config import SAMPLE_VAULT_DIR


def test_sanitize_frontmatter_and_wikilinks():
    sample_md = """---
title: Raft Consensus In-Depth
tags:
  - consensus
  - distributed-systems
date: 2026-08-01
---

# Raft Consensus In-Depth

This note connects to [[Paxos Algorithm|Classical Paxos]] and [[CAP Theorem]].
Check section [[Consistent Hashing#Ring|Hash Ring]].
Here is an image: ![[diagram.png]]
Callout note:
> [!NOTE]
> Raft decomposes consensus into leader election and log replication.
"""
    cleaned, meta = sanitize_obsidian_markdown(sample_md, fallback_title="Fallback")
    
    # Assert frontmatter parsed
    assert meta["title"] == "Raft Consensus In-Depth"
    assert "consensus" in meta["tags"]
    assert "distributed-systems" in meta["tags"]

    # Assert wikilinks converted
    assert "Classical Paxos" in cleaned
    assert "[[Paxos Algorithm" not in cleaned
    assert "CAP Theorem" in cleaned
    assert "[[CAP Theorem]]" not in cleaned
    assert "Hash Ring" in cleaned

    # Assert image embeds stripped
    assert "diagram.png" not in cleaned
    assert "![[" not in cleaned

    # Assert callout converted
    assert "[!NOTE]" not in cleaned
    assert "Raft decomposes consensus" in cleaned


def test_chunking_sliding_window():
    text = "Paragraph one is about consensus. " * 30 + "\n\n" + "Paragraph two is about vector search. " * 30
    meta = {"source": "TestNote.md", "title": "Test Note"}
    
    chunks = chunk_document(text, meta, chunk_size=500, chunk_overlap=100)
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk["metadata"]["source"] == "TestNote.md"
        assert chunk["metadata"]["title"] == "Test Note"
        assert "chunk_index" in chunk["metadata"]
        assert len(chunk["text"]) > 50


def test_zip_ingestion():
    # Create in-memory zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("Note1.md", "# First Note\nContent for note 1 with [[Note2]].")
        zf.writestr("Subfolder/Note2.md", "# Second Note\nContent for note 2 referencing [[Note1]].")

    zip_bytes = zip_buffer.getvalue()
    chunks = load_notes_from_zip(zip_bytes)

    sources = set(c["metadata"]["source"] for c in chunks)
    assert "Note1.md" in sources
    assert "Note2.md" in sources
    assert len(chunks) == 2


if __name__ == "__main__":
    print("Running ingest unit tests...")
    test_sanitize_frontmatter_and_wikilinks()
    print("[PASS] test_sanitize_frontmatter_and_wikilinks")
    test_chunking_sliding_window()
    print("[PASS] test_chunking_sliding_window")
    test_zip_ingestion()
    print("[PASS] test_zip_ingestion")
    print("All Phase 1 tests passed successfully!")
