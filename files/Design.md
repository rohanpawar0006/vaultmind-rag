# Design.md — VaultMind-RAG: Visual Design

## 1. Theme
Dark, minimal, "note-taking tool" aesthetic — evokes Obsidian itself so the connection to the source product is immediately visible to an evaluator.

## 2. Color Palette
| Role | Color | Hex |
|---|---|---|
| Background (primary) | near-black charcoal | `#1E1E2E` |
| Background (secondary/cards) | slightly lighter panel | `#2A2A3C` |
| Accent (primary) | Obsidian-purple | `#7C3AED` |
| Accent (hover/active) | lighter purple | `#9D5CFF` |
| Text (primary) | off-white | `#E4E4EB` |
| Text (secondary/muted) | gray | `#9494A8` |
| Success / grounded answer | soft green | `#4ADE80` |
| Warning / "not found in vault" | amber | `#FBBF24` |
| Source citation chip | subtle outline, accent-colored text | border `#7C3AED`, text `#9D5CFF` |

## 3. Typography
- **Headings:** `Inter` or Streamlit default sans-serif, semi-bold
- **Body/chat text:** `Inter` or system-ui, regular, 15–16px for readability
- **Code/note-source snippets:** monospace, e.g. `JetBrains Mono` or `Fira Code`, slightly smaller (13–14px), on a darker inset background

## 4. Layout
- Single-column chat interface, centered, max-width ~800px for readability
- Sidebar (left): vault upload control, "use sample vault" toggle, rebuild-index button, basic stats (number of notes/chunks indexed)
- Chat area: user messages right-aligned, assistant messages left-aligned with a small "sources" row of chip-style links underneath each answer
- Source chips expand on click to show the matched note excerpt (stretch goal)

## 5. Tone
Clean and functional over flashy — this is a developer tool, not a consumer app. Prioritize legibility and clear grounding/citation cues over decoration.
