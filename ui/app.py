import streamlit as st
import requests
from pathlib import Path
import os

# ── Config ───────────────────────────────────────────────

API_URL = API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AI Memory Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Styling ──────────────────────────────────────────────

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
    .memory-card {
        background: #1e1e2e;
        border-left: 4px solid #6366f1;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .source-badge {
        background: #312e81;
        color: #a5b4fc;
        padding: 2px 10px;
        border-radius: 99px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .score-badge {
        background: #14532d;
        color: #86efac;
        padding: 2px 10px;
        border-radius: 99px;
        font-size: 0.75rem;
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


# ── Helper functions ─────────────────────────────────────

def check_api() -> bool:
    """Check if the backend is running"""
    try:
        r = requests.get(f"{API_URL}/", timeout=3)
        return r.status_code == 200
    except:
        return False


def get_status() -> dict:
    try:
        r = requests.get(f"{API_URL}/status", timeout=5)
        return r.json()
    except:
        return {"total_chunks": 0, "status": "API unreachable"}


def ingest_file(uploaded_file) -> dict:
    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
    r = requests.post(f"{API_URL}/ingest", files=files, timeout=60)
    return r.json()


def search_memories(query: str, top_k: int) -> dict:
    payload = {"query": query, "top_k": top_k}
    r = requests.post(f"{API_URL}/search", json=payload, timeout=30)
    return r.json()


def reconstruct_memory(query: str, top_k: int) -> dict:
    payload = {"query": query, "top_k": top_k}
    r = requests.post(f"{API_URL}/reconstruct", json=payload, timeout=60)
    return r.json()


def clear_memories() -> dict:
    r = requests.delete(f"{API_URL}/clear", timeout=10)
    return r.json()


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

    # API status
    api_ok = check_api()
    if api_ok:
        st.success("✅ API Connected")
    else:
        st.error("❌ API Offline — run `python main.py` first")

    # DB status
    status = get_status()
    st.metric("Memories Stored", status["total_chunks"])
    st.caption(status["status"])

    st.markdown("---")

    # Search settings
    st.markdown("### ⚙️ Settings")
    top_k = st.slider("Results to retrieve", 1, 10, 5)

    st.markdown("---")

    # Clear button
    if st.button("🗑️ Clear All Memories", use_container_width=True):
        result = clear_memories()
        st.warning(result.get("message", "Cleared"))
        st.rerun()

    st.markdown("---")
    st.caption("AI Memory Reconstruction Engine\nBuilt with RAG + ChromaDB")


# ── Main area ────────────────────────────────────────────

st.markdown('<p class="main-title">🧠 AI Memory Reconstruction Engine</p>',
            unsafe_allow_html=True)
st.markdown('<p class="subtitle">Rebuild forgotten context from your digital life</p>',
            unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs(["📥 Ingest", "🔍 Search", "🧠 Reconstruct"])


# ════════════════════════════════════════════════════════
# TAB 1 — INGEST
# ════════════════════════════════════════════════════════

with tab1:
    st.markdown("### Upload Memory Sources")
    st.caption("Supported: .txt .md .pdf .json .csv .png .jpg")

    uploaded_files = st.file_uploader(
        "Drop your files here",
        accept_multiple_files=True,
        type=["txt", "md", "pdf", "json", "csv", "png", "jpg", "jpeg"]
    )

    if uploaded_files:
        if st.button("⚡ Ingest All Files", use_container_width=True):
            progress = st.progress(0)
            results_log = []

            for i, file in enumerate(uploaded_files):
                with st.spinner(f"Ingesting {file.name}..."):
                    try:
                        result = ingest_file(file)
                        results_log.append({
                            "file": file.name,
                            "chunks": result.get("chunks_created", 0),
                            "status": "✅"
                        })
                    except Exception as e:
                        results_log.append({
                            "file": file.name,
                            "chunks": 0,
                            "status": f"❌ {str(e)}"
                        })

                progress.progress((i + 1) / len(uploaded_files))

            st.success(f"Done! Processed {len(uploaded_files)} file(s)")

            # Show results table
            st.markdown("#### Results")
            for r in results_log:
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.write(r["file"])
                col2.write(f"{r['chunks']} chunks")
                col3.write(r["status"])

            st.rerun()

    # Quick ingest sample data button
    st.markdown("---")
    st.markdown("#### 🧪 No files? Use sample data")
    if st.button("Load Sample Data", use_container_width=True):
        sample_dir = Path("data/samples")
        if sample_dir.exists():
            files = list(sample_dir.iterdir())
            total = 0
            for f in files:
                try:
                    with open(f, "rb") as fh:
                        result = requests.post(
                            f"{API_URL}/ingest",
                            files={"file": (f.name, fh)},
                            timeout=60
                        )
                        total += result.json().get("chunks_created", 0)
                except:
                    pass
            st.success(f"✅ Loaded sample data — {total} chunks ingested")
            st.rerun()
        else:
            st.error("data/samples/ folder not found")


# ════════════════════════════════════════════════════════
# TAB 2 — SEARCH
# ════════════════════════════════════════════════════════

with tab2:
    st.markdown("### Semantic Search")
    st.caption("Find memories by meaning — not just keywords")

    query = st.text_input(
        "What are you looking for?",
        placeholder="e.g. what tools was I researching last week?"
    )

    source_filter = st.selectbox(
        "Filter by source (optional)",
        ["All", "chat", "note", "browser", "screenshot", "voice"]
    )

    if st.button("🔍 Search", use_container_width=True) and query:
        with st.spinner("Searching memories..."):
            try:
                payload = {"query": query, "top_k": top_k}
                if source_filter != "All":
                    payload["source_type"] = source_filter

                data = search_memories(query, top_k)
                results = data.get("results", [])

                if not results:
                    st.warning("No results found. Try a different query.")
                else:
                    st.success(f"Found {len(results)} relevant memory chunk(s)")

                    for i, r in enumerate(results, 1):
                        icon = SOURCE_ICONS.get(r["source_type"], "📄")
                        score_color = (
                            "🟢" if r["score"] > 0.75
                            else "🟡" if r["score"] > 0.5
                            else "🔴"
                        )

                        with st.expander(
                            f"{icon} Result #{i} — {r['source_file']} "
                            f"{score_color} {r['score']}",
                            expanded=(i == 1)
                        ):
                            col1, col2 = st.columns([1, 1])
                            col1.caption(f"**Source:** {r['source_type']}")
                            col2.caption(f"**Time:** {r['timestamp'][:19]}")
                            st.markdown("---")
                            st.write(r["text"])

            except Exception as e:
                st.error(f"Search failed: {e}")


# ════════════════════════════════════════════════════════
# TAB 3 — RECONSTRUCT
# ════════════════════════════════════════════════════════

with tab3:
    st.markdown("### 🧠 Memory Reconstruction")
    st.caption("Ask anything — the engine rebuilds what you were doing")

    # Example queries
    st.markdown("**Try these:**")
    col1, col2, col3 = st.columns(3)
    ex1 = col1.button("What was I working on?")
    ex2 = col2.button("What tools was I researching?")
    ex3 = col3.button("Any hackathon ideas?")

    # Set query from example buttons or text input
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
        with st.spinner("Reconstructing your memory..."):
            try:
                data = reconstruct_memory(recon_query, top_k)

                if "narrative" in data:
                    # Main narrative
                    st.markdown("#### 📖 Reconstructed Memory")
                    st.info(data["narrative"])

                    # Sources
                    st.markdown(f"#### 📎 Sources Used ({data['chunks_used']} chunks)")
                    for r in data.get("sources", []):
                        icon = SOURCE_ICONS.get(r["source_type"], "📄")
                        score_color = (
                            "🟢" if r["score"] > 0.75
                            else "🟡" if r["score"] > 0.5
                            else "🔴"
                        )
                        with st.expander(
                            f"{icon} [{r['source_type']}] {r['source_file']} "
                            f"{score_color} score: {r['score']}"
                        ):
                            st.write(r["text"])
                else:
                    st.error(data.get("detail", "Reconstruction failed"))

            except Exception as e:
                st.error(f"Error: {e}")