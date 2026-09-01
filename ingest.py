"""
ingest.py — Obsidian Note Ingestion, Sanitization, and Custom Sliding-Window Chunking

This module handles:
1. Loading markdown notes from directories or uploaded .zip files.
2. Sanitizing Obsidian-specific syntax (YAML frontmatter, [[wikilinks|alias]], tags, callouts, block refs).
3. Chunking documents using a sliding-window strategy with word-boundary preservation.
4. Packaging chunks with rich metadata (source note, title, tags, chunk indices).
"""

import os
import re
import zipfile
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Union
import frontmatter

from config import CHUNK_SIZE, CHUNK_OVERLAP, MIN_CHUNK_SIZE, SAMPLE_VAULT_DIR


def sanitize_obsidian_markdown(raw_content: str, fallback_title: str = "Untitled") -> Tuple[str, Dict[str, Any]]:
    """
    Parses and sanitizes raw Obsidian markdown content.
    
    1. Extracts and strips YAML frontmatter using python-frontmatter.
    2. Resolves Obsidian wikilinks:
       - [[Target Note|Custom Text]] -> 'Custom Text'
       - [[Target Note#Section|Custom Text]] -> 'Custom Text'
       - [[Target Note#Section]] -> 'Target Note'
       - [[Target Note]] -> 'Target Note'
    3. Strips image embeds: ![[image.png]] or !alt
    4. Cleans block reference IDs (^dcf834) and callout markers (> [!NOTE]).
    5. Normalizes whitespace while preserving paragraph spacing.
    
    Returns:
        tuple (cleaned_text, metadata_dict)
    """
    metadata: Dict[str, Any] = {
        "title": fallback_title,
        "tags": "",
        "frontmatter_tags": []
    }
    
    # 1. Extract YAML frontmatter
    try:
        post = frontmatter.loads(raw_content)
        content = post.content
        fm = post.metadata
        
        # Extract title from frontmatter if available
        if "title" in fm and fm["title"]:
            metadata["title"] = str(fm["title"]).strip()
            
        # Extract tags from frontmatter
        if "tags" in fm:
            if isinstance(fm["tags"], list):
                metadata["frontmatter_tags"] = [str(t).strip() for t in fm["tags"]]
                metadata["tags"] = ", ".join(metadata["frontmatter_tags"])
            elif isinstance(fm["tags"], str):
                metadata["tags"] = fm["tags"].strip()
                metadata["frontmatter_tags"] = [t.strip() for t in fm["tags"].split(",") if t.strip()]
    except Exception:
        # Fallback if frontmatter is malformed
        content = raw_content

    # If title is still default, look for the first # Heading 1 in content
    if metadata["title"] == fallback_title:
        h1_match = re.search(r"^#\s+(.+)$", content, flags=re.MULTILINE)
        if h1_match:
            metadata["title"] = h1_match.group(1).strip()

    # 2. Extract inline #tags (excluding markdown headings like # Heading)
    inline_tags = re.findall(r"(?<!\S)#([a-zA-Z0-9_\-\/]+)(?!\S)", content)
    if inline_tags:
        combined_tags = list(set(metadata["frontmatter_tags"] + inline_tags))
        metadata["tags"] = ", ".join(combined_tags)

    # 3. Strip image embeds and transclusions: ![[image.png]] or ![[note]] or ![alt](url)
    content = re.sub(r"!\[\[.*?\]\]", "", content)
    content = re.sub(r"!\[.*?\]\(.*?\)", "", content)

    # 4. Resolve Obsidian wikilinks:
    # Pattern a: [[Target#Header|Alias]] -> Alias
    content = re.sub(r"\[\[[^\]|#]+(?:#[^\]|]+)?\|([^\]]+)\]\]", r"\1", content)
    # Pattern b: [[Target#Header]] -> Target
    content = re.sub(r"\[\[([^\]|#]+)#[^\]]+\]\]", r"\1", content)
    # Pattern c: [[Target]] -> Target
    content = re.sub(r"\[\[([^\]]+)\]\]", r"\1", content)

    # 5. Clean Obsidian callout markers: '> [!NOTE]' -> '>'
    content = re.sub(r"^>\s*\[![A-Za-z0-9_-]+\]\s*", "> ", content, flags=re.MULTILINE)

    # 6. Remove block reference identifiers at end of paragraphs (e.g. ^a1b2c3d)
    content = re.sub(r"\s+\^[a-zA-Z0-9_-]+$", "", content, flags=re.MULTILINE)

    # 7. Normalize multiple blank lines to double newlines for paragraph consistency
    content = re.sub(r"\n{3,}", "\n\n", content).strip()

    return content, metadata


def chunk_document(
    text: str,
    metadata: Dict[str, Any],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> List[Dict[str, Any]]:
    """
    Custom sliding-window text chunker that preserves natural sentence and word boundaries.
    
    Why custom chunker over LangChain?
    - Transparent token/character window calculation.
    - Zero external heavy dependencies.
    - Deterministic, easily explainable during code walkthroughs.
    
    Returns a list of dicts:
    [
      {
        "id": "Note_Name_chunk_0",
        "text": "Chunk text content...",
        "metadata": {
            "source": "Note Name.md",
            "title": "...",
            "chunk_index": 0,
            "total_chunks": 3,
            "tags": "..."
        }
      },
      ...
    ]
    """
    if not text or len(text.strip()) == 0:
        return []

    # If text is smaller than chunk size, return single chunk
    if len(text) <= chunk_size:
        return [{
            "id": f"{metadata.get('source', 'doc')}_chunk_0",
            "text": text.strip(),
            "metadata": {
                **metadata,
                "chunk_index": 0,
                "total_chunks": 1
            }
        }]

    chunks_raw: List[str] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        
        if end >= text_len:
            # Reached end of text
            chunk_slice = text[start:].strip()
            if len(chunk_slice) >= MIN_CHUNK_SIZE or not chunks_raw:
                chunks_raw.append(chunk_slice)
            elif chunks_raw:
                # Merge tiny trailing fragment with previous chunk
                chunks_raw[-1] = chunks_raw[-1] + "\n\n" + chunk_slice
            break

        # Find best split boundary within the last 150 chars of the window:
        # 1. Paragraph break (\n\n)
        # 2. Sentence end (. / ? / !)
        # 3. Line break (\n)
        # 4. Word boundary (space)
        window = text[start:end]
        split_pos = -1

        # Search from the end of the window backwards
        search_zone_start = max(0, len(window) - 150)
        search_zone = window[search_zone_start:]

        # Check for paragraph break
        para_idx = search_zone.rfind("\n\n")
        if para_idx != -1:
            split_pos = search_zone_start + para_idx + 2
        else:
            # Check for sentence end followed by space or newline
            sentence_match = list(re.finditer(r"[\.\?\!]\s+", search_zone))
            if sentence_match:
                last_m = sentence_match[-1]
                split_pos = search_zone_start + last_m.end()
            else:
                # Check for line break
                newline_idx = search_zone.rfind("\n")
                if newline_idx != -1:
                    split_pos = search_zone_start + newline_idx + 1
                else:
                    # Check for space
                    space_idx = search_zone.rfind(" ")
                    if space_idx != -1:
                        split_pos = search_zone_start + space_idx + 1
                    else:
                        # Hard cut if no natural boundary
                        split_pos = len(window)

        chunk_text = text[start:start + split_pos].strip()
        if len(chunk_text) >= MIN_CHUNK_SIZE:
            chunks_raw.append(chunk_text)

        # Advance start position with overlap
        start = max(start + 1, start + split_pos - chunk_overlap)

    # Package chunks with metadata
    total_chunks = len(chunks_raw)
    result = []
    source_name = metadata.get("source", "doc")
    # Clean source_name for ID compatibility
    clean_id_prefix = re.sub(r"[^a-zA-Z0-9_-]", "_", source_name)

    for i, c_text in enumerate(chunks_raw):
        result.append({
            "id": f"{clean_id_prefix}_chunk_{i}",
            "text": c_text,
            "metadata": {
                **metadata,
                "chunk_index": i,
                "total_chunks": total_chunks
            }
        })

    return result


def load_notes_from_directory(dir_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Recursively scans a directory for markdown files (.md), parses and chunks them.
    Skips hidden directories (e.g. .obsidian, .git).
    
    Returns:
        List of chunk dictionaries ready for embedding and vector store insertion.
    """
    dir_path = Path(dir_path)
    if not dir_path.exists() or not dir_path.is_dir():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    all_chunks: List[Dict[str, Any]] = []
    
    for file_path in dir_path.rglob("*.md"):
        # Skip hidden files or folders like .obsidian, .git
        if any(part.startswith(".") for part in file_path.parts):
            continue

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                raw_text = f.read()

            rel_path = str(file_path.relative_to(dir_path))
            cleaned_text, meta = sanitize_obsidian_markdown(raw_text, fallback_title=file_path.stem)
            meta["source"] = file_path.name
            meta["relative_path"] = rel_path

            chunks = chunk_document(cleaned_text, meta)
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"[Warning] Failed to parse note {file_path.name}: {e}")

    return all_chunks


def load_notes_from_zip(zip_source: Union[str, Path, bytes]) -> List[Dict[str, Any]]:
    """
    Extracts a zip file containing markdown notes in a secure temporary directory,
    parses, cleans, and chunks all .md files.
    
    Parameters:
        zip_source: File path, Path object, or raw bytes (from Streamlit UploadedFile)
    """
    all_chunks: List[Dict[str, Any]] = []

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        temp_zip_path = temp_dir_path / "uploaded_vault.zip"

        if isinstance(zip_source, bytes):
            with open(temp_zip_path, "wb") as f:
                f.write(zip_source)
            target_zip = temp_zip_path
        else:
            target_zip = Path(zip_source)

        if not zipfile.is_zipfile(target_zip):
            raise ValueError("The provided file is not a valid zip archive.")

        # Extract contents safely
        extract_dir = temp_dir_path / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(target_zip, "r") as zip_ref:
            # Validate against zip slip vulnerability
            for member in zip_ref.namelist():
                # Avoid hidden files and dangerous directory traversals
                if member.startswith("__MACOSX") or "../" in member or member.startswith("/"):
                    continue
                zip_ref.extract(member, extract_dir)

        # Ingest extracted directory
        all_chunks = load_notes_from_directory(extract_dir)

    return all_chunks


if __name__ == "__main__":
    print(f"--- Testing VaultMind-RAG Ingestion on Sample Vault ---")
    print(f"Sample vault directory: {SAMPLE_VAULT_DIR}")
    
    chunks = load_notes_from_directory(SAMPLE_VAULT_DIR)
    
    # Calculate stats
    unique_sources = set(c["metadata"]["source"] for c in chunks)
    print(f"Total Notes Ingested: {len(unique_sources)}")
    print(f"Total Chunks Created:  {len(chunks)}")
    print(f"\n--- Sample Chunk (from {chunks[0]['metadata']['source']}) ---")
    print(f"Chunk ID: {chunks[0]['id']}")
    print(f"Title:    {chunks[0]['metadata']['title']}")
    print(f"Tags:     {chunks[0]['metadata']['tags']}")
    print(f"Text Preview:\n{chunks[0]['text'][:300]}...")
    print(f"\n--- Done Phase 1 Ingestion Check ---")
