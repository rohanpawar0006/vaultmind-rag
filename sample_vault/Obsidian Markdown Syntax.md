---
title: Obsidian Markdown Syntax
tags:
  - obsidian
  - markdown
  - parsing
date: 2026-08-28
status: completed
---

# Obsidian-Specific Markdown Syntax & Parsing

Obsidian extends CommonMark standard markdown with distinct personal knowledge management (PKM) syntax:

## Distinct Syntactical Constructs

1. **Internal Wikilinks**:
   - Standard: `[[Target Note]]`
   - Aliased: `[[Target Note|Custom Display Text]]`
   - Header Links: `[[Target Note#Specific Header]]`
   - Block References: `[[Target Note#^dcf834]]`

2. **YAML Frontmatter**:
   - Delimited by `---` at the top of the file. Contains metadata like `tags: [rag, vector-db]`, `date`, `aliases`, etc.

3. **Tags**:
   - Written as `#tag` or nested `#parent/child`.

4. **Callouts**:
   - Syntax: `> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`.

5. **Embeds / Transclusions**:
   - Syntax: `![[Target Image.png]]` or `![[Target Note]]`.

## Parsing Pipeline for RAG
When indexing notes in VaultMind-RAG:
- YAML frontmatter is extracted into chunk metadata via `python-frontmatter`.
- Wikilinks `[[Target Note|Alias]]` are normalized to `"Alias"` (or `"Target Note"` if no alias is specified) so the underlying prose flows naturally into [[Embedding Models]].
- Transclusions and external images are stripped to focus embedding purely on textual semantics.
