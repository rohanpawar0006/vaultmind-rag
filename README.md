# 🧠 VaultMind-RAG: Obsidian Vault RAG Knowledge Assistant

> An intelligent, strictly-grounded Retrieval-Augmented Generation (RAG) assistant designed for personal **Obsidian** vaults. Ask natural-language questions across hundreds of interconnected notes and receive accurate answers with verifiable source citations.

🔗 **Live Demo**: [https://vaultmind-rag.streamlit.app/](https://vaultmind-rag.streamlit.app/)

---

## 🏗️ Architecture & Pipeline

```mermaid
flowchart TD
    A[User Uploads .zip or Selects Sample Vault] --> B[Ingest & Sanitize Engine]
    B -->|Strip YAML Frontmatter & Clean [[Wikilinks]]| C[Custom Sliding-Window Chunker]
    C -->|~500 tokens, 50-token overlap| D[Sentence-Transformers all-MiniLM-L6-v2]
    D -->|384-d normalized vectors| E[(ChromaDB Persistent Vector Store)]
    
    F[User Question in Chat UI] --> G[Embed Query Vector]
    G --> H[ChromaDB Cosine Similarity Search Top-K]
    H --> I{Similarity >= 0.30?}
    I -->|No / Irrelevant| J[Instant Fallback: 'I couldn't find anything relevant']
    I -->|Yes| K[XML-Demarcated Context Injection]
    K --> L[Strict Grounding Prompt]
    L --> M[Google Gemini 2.5 Flash / 2.0 Flash]
    M --> N[Synthesized Grounded Answer + Source Chips]
```

---

## ✨ Core Features

1. **Obsidian Syntax Parser**:
   - Strips YAML frontmatter into structured metadata.
   - Normalizes Obsidian wikilinks: `[[Note|Alias]]` $\rightarrow$ `Alias`, `[[Note#Header]]` $\rightarrow$ `Note`.
   - Cleans callouts (`> [!NOTE]`), transclusions, and block references (`^dcf834`).
2. **Deterministic Sliding-Window Chunker**:
   - ~1200 character window (~400–500 tokens) with 200 character overlap (~50 tokens).
   - Intelligently splits at paragraph (`\n\n`), sentence (`. `), or word boundaries to maintain semantic integrity.
3. **Local Embedding Engine**:
   - Uses `all-MiniLM-L6-v2` via `sentence-transformers`.
   - **100% offline & free**: Zero API rate limits or costs during evaluation.
4. **Embedded Vector Database**:
   - In-process **ChromaDB** with persistent cosine distance index at `data/chroma_db/`.
5. **Strict Grounding & Anti-Hallucination**:
   - Zero hallucination guarantee: refuses out-of-vault queries with *"I couldn't find anything relevant in this vault"*.
   - Cosine distance thresholding cuts off irrelevant topics before calling the LLM.
6. **Obsidian Dark Aesthetic UI**:
   - Tailored Streamlit interface matching Obsidian's `#1E1E2E` charcoal and `#7C3AED` purple palette.
   - Interactive source citation chips with expandable matched note excerpts.
7. **Bundled Sample Vault**:
   - Includes 18 comprehensive notes on Distributed Systems (Raft, Paxos, CAP theorem, Consistent Hashing) and RAG Architecture.

---

## 🛠️ Tech Stack & Design Decisions

| Component | Choice | Why? |
|---|---|---|
| **UI** | Streamlit | Rapid interactive prototyping with native chat components. |
| **Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`) | Local CPU execution (~80MB), zero rate limits, predictable low latency. |
| **Vector Store** | ChromaDB | Zero external infrastructure, embedded local persistence, fast HNSW cosine search. |
| **LLM Generation** | Google Gemini (`gemini-2.5-flash` / `gemini-2.0-flash`) | High quality reasoning, strict instruction following, low latency. |
| **Parser** | `python-frontmatter` + regex | Clean extraction of YAML metadata and custom Obsidian wikilink normalization. |
| **Architecture** | Custom Pipeline (No LangChain) | Demonstrates deep understanding of core RAG mechanics without framework opacity. |

---

## 🚀 Quick Start (Local Setup)

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/your-username/vaultmind-rag.git
cd vaultmind-rag

# Create and activate virtual environment (optional)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy the `.env.example` file to `.env` and add your Google Gemini API key:
```bash
cp .env.example .env
```
Edit `.env`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
*(You can also input your API key directly inside the Streamlit sidebar at runtime).*

### 3. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Testing & Verification

Run the test suite standalone:

```bash
# Test Phase 1: Ingestion & Obsidian Syntax Cleaning
python tests/test_ingest.py

# Test Phase 2: Local Embeddings & ChromaDB Indexing
python vector_store.py

# Test Phase 3: RAG Retrieval & Anti-Hallucination Fallback
python rag_chain.py
```

---

## 📁 Repository Structure

```
vaultmind-rag/
├── app.py                  # Streamlit entrypoint (Obsidian Dark UI + Orchestration)
├── ingest.py               # Markdown parser, Obsidian sanitizer, sliding chunker
├── embeddings.py           # Sentence-transformers singleton wrapper
├── vector_store.py         # ChromaDB persistence, upsert, and cosine search
├── rag_chain.py            # Grounding prompt builder, Gemini LLM caller, fallback logic
├── config.py               # Centralized constants (chunk sizes, thresholds, model names)
├── sample_vault/           # 18 bundled markdown notes on distributed systems & RAG
│   ├── Raft Protocol.md
│   ├── Paxos Algorithm.md
│   ├── Vector Databases.md
│   └── ...
├── data/
│   └── chroma_db/          # Persisted ChromaDB vector index
├── tests/
│   └── test_ingest.py      # Unit tests for markdown cleaner & sliding chunker
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment template
├── Memory.md               # Build phase tracking & interview notes
└── README.md               # Comprehensive documentation
```

---

## 🔒 Security & Privacy
- **Local First**: All document parsing, chunking, and embedding generation occurs 100% locally on your machine.
- **Privacy Protected**: Only the specific top-k retrieved note excerpts relevant to your active question are transmitted to the LLM for synthesis.
