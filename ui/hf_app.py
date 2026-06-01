import streamlit as st
from pathlib import Path
import tempfile
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vectors.pipeline import IngestionPipeline
from search.semantic_search import SemanticSearch
from reconstruction.free_reconstructor import FreeReconstructor

# ── Config ───────────────────────────────────────────────

st.set_page_config(
    page_title="AI Memory Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ── Initialize engines (cached so they load once) ────────

@st.cache_resource
def load_engines():
    pipeline = IngestionPipeline()
    search_engine = SemanticSearch()
    reconstructor = FreeReconstructor()
    return pipeline, search_engine, reconstructor

with st.spinner("Loading AI engine... (first load takes ~60 seconds)"):
    pipeline, search_engine, reconstructor = load_engines()

# ── Source icons ─────────────────────────────────────────

SOURCE_ICONS = {
    "chat": "💬",
    "note": "📝",
    "browser": "🌐",
    "screenshot": "🖼️",
    "voice": "🎙️",
    "unknown": "📄"
}

# ── Sidebar ──────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🧠 Memory Engine")
    st.markdown("---")

    count = pipeline.store.get_count()
    st.metric("Memories Stored", count)

    st.markdown("---")
    top_k = st.slider("Results to retrieve", 1, 10, 5)

    st.markdown("---")
    if st.button("🗑️ Clear All Memories", use_container_width=True):
        pipeline.store.clear()
        st.warning("All memories cleared.")
        st.rerun()

    st.markdown("---")
    st.caption("AI Memory Reconstruction Engine\nBuilt with RAG + ChromaDB")

# ── Main ─────────────────────────────────────────────────

st.markdown('<p class="main-title">🧠 AI Memory Reconstruction Engine</p>',
            unsafe_allow_html=True)
st.markdown('<p class="subtitle">Rebuild forgotten context from your digital life</p>',
            unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📥 Ingest", "🔍 Search", "🧠 Reconstruct"])

# ════════════════════════════════════════════════════════
# TAB 1 — INGEST
# ════════════════════════════════════════════════════════

with tab1:
    st.markdown("### Upload Memory Sources")
    st.caption("Supported: .txt .md .pdf .json .csv")

    uploaded_files = st.file_uploader(
        "Drop your files here",
        accept_multiple_files=True,
        type=["txt", "md", "pdf", "json", "csv"]
    )

    if uploaded_files:
        if st.button("⚡ Ingest All Files", use_container_width=True):
            progress = st.progress(0)
            total_chunks = 0

            for i, file in enumerate(uploaded_files):
                with st.spinner(f"Ingesting {file.name}..."):
                    try:
                        # Save to temp file
                        suffix = Path(file.name).suffix
                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix=suffix
                        ) as tmp:
                            tmp.write(file.read())
                            tmp_path = tmp.name

                        chunks = pipeline.ingest_file(tmp_path)
                        total_chunks += chunks
                        os.unlink(tmp_path)
                        st.success(f"✅ {file.name} → {chunks} chunks")
                    except Exception as e:
                        st.error(f"❌ {file.name}: {e}")

                progress.progress((i + 1) / len(uploaded_files))

            st.success(f"Done! {total_chunks} total chunks stored.")
            st.rerun()

    # Sample data loader
    st.markdown("---")
    st.markdown("#### 🧪 No files? Use sample data")
    if st.button("Load Sample Data", use_container_width=True):
        sample_dir = Path("data/samples")
        if sample_dir.exists():
            total = 0
            for f in sample_dir.iterdir():
                try:
                    chunks = pipeline.ingest_file(str(f))
                    total += chunks
                    st.write(f"✅ {f.name} → {chunks} chunks")
                except Exception as e:
                    st.write(f"⚠️ {f.name}: {e}")
            st.success(f"Loaded {total} chunks total")
            st.rerun()
        else:
            st.error("data/samples/ not found")

# ════════════════════════════════════════════════════════
# TAB 2 — SEARCH
# ════════════════════════════════════════════════════════

with tab2:
    st.markdown("### Semantic Search")
    st.caption("Find memories by meaning — not just keywords")

    query = st.text_input(
        "What are you looking for?",
        placeholder="e.g. what tools was I researching?"
    )

    if st.button("🔍 Search", use_container_width=True) and query:
        if pipeline.store.get_count() == 0:
            st.warning("No memories stored. Ingest some files first.")
        else:
            with st.spinner("Searching..."):
                results = search_engine.search(query, top_k=top_k)

                if not results:
                    st.warning("No results found.")
                else:
                    st.success(f"Found {len(results)} result(s)")
                    for i, r in enumerate(results, 1):
                        icon = SOURCE_ICONS.get(r.source_type, "📄")
                        score_color = (
                            "🟢" if r.score > 0.75
                            else "🟡" if r.score > 0.5
                            else "🔴"
                        )
                        with st.expander(
                            f"{icon} Result #{i} — {r.source_file} "
                            f"{score_color} {r.score}",
                            expanded=(i == 1)
                        ):
                            st.caption(f"Source: {r.source_type} | Time: {r.timestamp[:19]}")
                            st.write(r.text)

# ════════════════════════════════════════════════════════
# TAB 3 — RECONSTRUCT
# ════════════════════════════════════════════════════════

with tab3:
    st.markdown("### 🧠 Memory Reconstruction")
    st.caption("Ask anything — the engine rebuilds what you were doing")

    col1, col2, col3 = st.columns(3)
    ex1 = col1.button("What was I working on?")
    ex2 = col2.button("What tools was I researching?")
    ex3 = col3.button("Any hackathon ideas?")

    if ex1:
        recon_query = "What was I working on?"
    elif ex2:
        recon_query = "What tools was I researching?"
    elif ex3:
        recon_query = "Any hackathon ideas?"
    else:
        recon_query = ""

    recon_query = st.text_input(
        "Or type your own question:",
        value=recon_query,
        placeholder="e.g. What decisions did I make about my project?"
    )

    if st.button("🧠 Reconstruct Memory", use_container_width=True) and recon_query:
        if pipeline.store.get_count() == 0:
            st.warning("No memories stored. Ingest some files first.")
        else:
            with st.spinner("Reconstructing your memory..."):
                result = reconstructor.reconstruct(recon_query, top_k)
                st.markdown("#### 📖 Reconstructed Memory")
                st.info(result.narrative)

                st.markdown(f"#### 📎 Sources ({result.chunks_found} chunks)")
                for r in result.sources_used:
                    icon = SOURCE_ICONS.get(r.source_type, "📄")
                    with st.expander(
                        f"{icon} [{r.source_type}] {r.source_file} — score: {r.score}"
                    ):
                        st.write(r.text)