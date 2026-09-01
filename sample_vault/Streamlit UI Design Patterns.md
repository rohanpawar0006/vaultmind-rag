---
title: Streamlit UI Design Patterns
tags:
  - streamlit
  - frontend
  - ui-ux
date: 2026-08-27
status: completed
---

# Streamlit UI Patterns for AI Applications

Streamlit provides a pure-Python execution model that re-runs top-to-bottom on state changes. Effective design requires mastering `st.session_state` and component separation.

## Key Design Best Practices

1. **Stateful Conversation Flow**:
   - Store messages in `st.session_state.messages = [{"role": "user"|"assistant", "content": "...", "sources": [...]}]`.
   - Iterate through history on each rerun before handling new input (`st.chat_message`).

2. **Custom Obsidian-Inspired Dark Theme**:
   - Inject targeted CSS via `st.markdown("<style>...</style>", unsafe_allow_html=True)`.
   - Background `#1E1E2E`, card panels `#2A2A3C`, and accent purple `#7C3AED`.
   - Source chips rendered with subtle outline badges for inspectable citations.

3. **Resource Caching**:
   - Cache heavy objects (embedding models, vector store connections) using `@st.cache_resource` to avoid reloading weights across user turns.

4. **Progress & Non-Blocking Feedback**:
   - Use `st.spinner("Retrieving notes & synthesizing answer...")` to indicate live pipeline execution.

See [[Architecture Overview]] and [[RAG Grounding & Hallucinations]].
