"""
app.py — VaultMind-RAG: Obsidian Vault Knowledge Assistant
Streamlit UI with Obsidian Dark Theme, Ingestion Management, and Grounded Chat
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

import streamlit as st
from dotenv import load_dotenv

# Load local environment variables from .env
load_dotenv()

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import (
    SAMPLE_VAULT_DIR,
    CHROMA_DB_DIR,
    DEFAULT_GEMINI_MODEL,
    TOP_K,
    SIMILARITY_DISTANCE_THRESHOLD
)
from ingest import load_notes_from_directory, load_notes_from_zip
from vector_store import VectorStore, get_vector_store
from rag_chain import ask_vault, FALLBACK_NOT_FOUND_MESSAGE

# -----------------------------------------------------------------------------
# 1. Streamlit Page Configuration & Obsidian Dark Theme Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="VaultMind-RAG | Obsidian Vault Knowledge Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS adhering strictly to Design.md palette
CUSTOM_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Dark Theme */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        background-color: #1E1E2E !important;
        color: #E4E4EB !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #181825 !important;
        border-right: 1px solid #2A2A3C;
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #E4E4EB !important;
    }

    /* Card Panels */
    .vault-card {
        background-color: #2A2A3C;
        border: 1px solid #3B3B52;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    .stat-badge {
        display: inline-block;
        background: rgba(124, 58, 237, 0.2);
        color: #9D5CFF;
        border: 1px solid #7C3AED;
        padding: 4px 10px;
        border-radius: 16px;
        font-size: 13px;
        font-weight: 600;
        margin-right: 8px;
    }

    /* Primary Accent Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #9D5CFF !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #9D5CFF 0%, #7C3AED 100%) !important;
        box-shadow: 0 0 12px rgba(157, 92, 255, 0.4) !important;
        transform: translateY(-1px);
    }

    /* Chat Messages */
    .stChatMessage {
        background-color: #2A2A3C !important;
        border: 1px solid #3B3B52 !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
    }

    /* Source Citation Chip */
    .source-chip {
        display: inline-flex;
        align-items: center;
        background: rgba(124, 58, 237, 0.15);
        color: #9D5CFF !important;
        border: 1px solid #7C3AED;
        border-radius: 6px;
        padding: 3px 9px;
        font-size: 12.5px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
        margin: 4px 6px 4px 0;
    }

    .source-chip:hover {
        background: rgba(124, 58, 237, 0.3);
        border-color: #9D5CFF;
    }

    /* Code & Snippet blocks */
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        background-color: #14141E !important;
        color: #E4E4EB !important;
        border-radius: 6px;
    }

    /* Suggestion Pills */
    .suggest-btn {
        background-color: #2A2A3C;
        border: 1px solid #3B3B52;
        border-radius: 8px;
        padding: 10px 14px;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-bottom: 8px;
        font-size: 14px;
        color: #E4E4EB;
    }

    .suggest-btn:hover {
        border-color: #7C3AED;
        background-color: #32324A;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. Vector Store & State Initialization
# -----------------------------------------------------------------------------
@st.cache_resource
def get_cached_vector_store():
    """Initializes and caches the persistent ChromaDB Vector Store."""
    return get_vector_store()

vs = get_cached_vector_store()

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "indexed" not in st.session_state:
    # Auto-index sample vault on first startup if vector store is empty
    stats = vs.get_stats()
    if stats["total_chunks"] == 0 and SAMPLE_VAULT_DIR.exists():
        with st.spinner("Initializing sample vault knowledge base..."):
            chunks = load_notes_from_directory(SAMPLE_VAULT_DIR)
            vs.add_chunks(chunks)
            st.session_state.indexed = True
    else:
        st.session_state.indexed = True

if "last_query" not in st.session_state:
    st.session_state.last_query = None


# -----------------------------------------------------------------------------
# 3. Sidebar: Configuration & Vault Management
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🧠 **VaultMind-RAG**")
    st.caption("Personal Obsidian Knowledge Assistant")
    st.divider()

    # API Key Configuration
    st.markdown("### 🔑 **API Configuration**")
    env_key = os.getenv("GEMINI_API_KEY", "")
    if not env_key:
        try:
            if "GEMINI_API_KEY" in st.secrets:
                env_key = str(st.secrets["GEMINI_API_KEY"]).strip()
        except Exception:
            pass

    api_key_input = st.text_input(
        "Google Gemini API Key",
        value=env_key,
        type="password",
        placeholder="AIzaSy...",
        help="Get a free Gemini API key from https://aistudio.google.com/app/apikey"
    )
    
    # Model Selector
    model_choice = st.selectbox(
        "Generation Model",
        options=["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"],
        index=0,
        help="Gemini Flash models offer high reasoning speed and accurate grounding."
    )

    st.divider()

    # Vault Selection & Ingestion
    st.markdown("### 📚 **Vault Source**")
    vault_mode = st.radio(
        "Select Vault Source",
        options=["Bundled Sample Vault", "Upload Custom Vault (.zip)"],
        index=0
    )

    uploaded_zip = None
    if vault_mode == "Upload Custom Vault (.zip)":
        uploaded_zip = st.file_uploader(
            "Upload Obsidian Vault (.zip)",
            type=["zip"],
            help="Upload a .zip file containing your Obsidian markdown (.md) notes."
        )

    # Re-index Button
    if st.button("🔄 Rebuild / Index Vault", use_container_width=True):
        with st.spinner("Processing markdown notes and building vector embeddings..."):
            vs.reset()
            try:
                if vault_mode == "Upload Custom Vault (.zip)":
                    if uploaded_zip is None:
                        st.error("Please upload a .zip file first!")
                    else:
                        zip_bytes = uploaded_zip.getvalue()
                        chunks = load_notes_from_zip(zip_bytes)
                        if not chunks:
                            st.warning("No valid .md notes found in the uploaded zip file.")
                        else:
                            count = vs.add_chunks(chunks)
                            st.success(f"Indexed {count} chunks from {len(set(c['metadata']['source'] for c in chunks))} notes!")
                            st.session_state.messages = []
                else:
                    chunks = load_notes_from_directory(SAMPLE_VAULT_DIR)
                    count = vs.add_chunks(chunks)
                    st.success(f"Indexed {count} chunks from sample vault!")
                    st.session_state.messages = []
            except Exception as e:
                st.error(f"Ingestion failed: {str(e)}")

    st.divider()

    # Real-time Vault Stats
    current_stats = vs.get_stats()
    st.markdown("### 📊 **Vault Index Stats**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Notes", current_stats["total_notes"])
    with col2:
        st.metric("Chunks", current_stats["total_chunks"])

    if current_stats["note_sources"]:
        with st.expander(f"View Indexed Notes ({len(current_stats['note_sources'])})"):
            for note in current_stats["note_sources"]:
                st.markdown(f"- 📄 `{note}`")

    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# -----------------------------------------------------------------------------
# 4. Main Chat Interface
# -----------------------------------------------------------------------------
st.title("🧠 VaultMind-RAG")
st.markdown(
    "Ask natural-language questions about your **Obsidian Vault**. "
    "Answers are strictly grounded in your notes with verifiable source citations."
)

# Render empty-state welcome card with suggested questions
if not st.session_state.messages:
    st.markdown(
        """
        <div class="vault-card">
            <h3 style="margin-top:0; color:#9D5CFF;">⚡ Quick Start & Suggested Queries</h3>
            <p style="color:#9494A8;">Select a sample prompt below or type your own question in the chat bar:</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    suggested_queries = [
        "How does Raft leader election work and what safety properties are guaranteed?",
        "Why does VaultMind use ChromaDB and what are its key properties?",
        "Explain the trade-offs between CP and AP systems under the CAP theorem.",
        "What is semantic caching and how does it reduce LLM latency?",
        "What are the quantitative evaluation metrics for RAG pipelines?"
    ]

    cols = st.columns(2)
    for idx, prompt_text in enumerate(suggested_queries):
        target_col = cols[idx % 2]
        if target_col.button(f"💬 {prompt_text}", key=f"suggest_{idx}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": prompt_text, "sources": [], "grounded": True})
            with st.spinner("Searching notes & generating grounded answer..."):
                response = ask_vault(
                    question=prompt_text,
                    api_key=api_key_input if api_key_input else None,
                    model_name=model_choice,
                    vector_store=vs
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "sources": response.get("sources", []),
                    "chunks": response.get("chunks", []),
                    "grounded": response.get("grounded", False),
                    "error": response.get("error")
                })
            st.rerun()

# Display chat history
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    sources = msg.get("sources", [])
    chunks = msg.get("chunks", [])
    grounded = msg.get("grounded", True)

    with st.chat_message(role, avatar="🧑‍💻" if role == "user" else "🧠"):
        st.markdown(content)
        
        # If assistant answer has citations, render source chips and expandable excerpts
        if role == "assistant" and sources:
            st.markdown("---")
            st.markdown("<p style='font-size:13px; font-weight:600; color:#9494A8; margin-bottom:4px;'>📚 CITED VAULT SOURCES:</p>", unsafe_allow_html=True)
            
            # Render source chips
            chips_html = "".join([
                f'<span class="source-chip">📄 {s["source"]}</span>' for s in sources
            ])
            st.markdown(chips_html, unsafe_allow_html=True)

            # Render expandable snippets
            with st.expander(f"🔍 Inspect Matched Note Passages ({len(sources)} sources)"):
                for src in sources:
                    st.markdown(f"#### 📄 `{src['source']}` — *{src['title']}*")
                    if "similarity" in src and src["similarity"] > 0:
                        st.caption(f"Relevance Score: `{src['similarity']:.2%}`")
                    st.markdown(f"> {src['snippet']}")
                    st.markdown("---")

# User chat input
if prompt := st.chat_input("Ask a question about your Obsidian vault notes..."):
    # Append user question
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "sources": [],
        "grounded": True
    })
    
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # Generate assistant answer
    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner("Searching notes & generating grounded answer..."):
            response = ask_vault(
                question=prompt,
                api_key=api_key_input if api_key_input else None,
                model_name=model_choice,
                vector_store=vs
            )
            st.markdown(response["answer"])

            sources = response.get("sources", [])
            if sources:
                st.markdown("---")
                st.markdown("<p style='font-size:13px; font-weight:600; color:#9494A8; margin-bottom:4px;'>📚 CITED VAULT SOURCES:</p>", unsafe_allow_html=True)
                chips_html = "".join([
                    f'<span class="source-chip">📄 {s["source"]}</span>' for s in sources
                ])
                st.markdown(chips_html, unsafe_allow_html=True)

                with st.expander(f"🔍 Inspect Matched Note Passages ({len(sources)} sources)"):
                    for src in sources:
                        st.markdown(f"#### 📄 `{src['source']}` — *{src['title']}*")
                        if "similarity" in src and src["similarity"] > 0:
                            st.caption(f"Relevance Score: `{src['similarity']:.2%}`")
                        st.markdown(f"> {src['snippet']}")
                        st.markdown("---")

    # Record assistant message in history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response["answer"],
        "sources": response.get("sources", []),
        "chunks": response.get("chunks", []),
        "grounded": response.get("grounded", False),
        "error": response.get("error")
    })
