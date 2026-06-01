---
title: AI Memory Reconstruction Engine
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: "1.28.0"
app_file: ui/hf_app.py
pinned: false
---
# 🧠 AI Memory Reconstruction Engine

> Rebuild forgotten context from your digital life using RAG architecture,
> vector databases, and semantic search.

---

## 🎯 What It Does

Upload your screenshots, chat exports, notes, voice memos, or browser
history — and ask the engine anything:

- *"What was I working on last week?"*
- *"What tools was I researching?"*
- *"What were my hackathon ideas?"*

The engine reconstructs a coherent memory narrative from your fragmented
digital history.

---

## 🏗️ Architecture
Raw Files (screenshots, chats, notes, browser history)
↓
Ingestion Engine  (OCR, text parsing, chunking)
↓
Embedding Model   (sentence-transformers, local + free)
↓
Vector Database   (ChromaDB, persistent on disk)
↓
Semantic Search   (cosine similarity, ranked results)
↓
Memory Reconstruction (RAG + context-aware narrative)
↓
FastAPI Backend + Streamlit Frontend
---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB |
| Semantic Search | Cosine similarity via ChromaDB |
| Reconstruction | RAG architecture |
| Backend | FastAPI |
| Frontend | Streamlit |
| OCR | Tesseract + Pillow |
| PDF parsing | pdfplumber |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/vinaya285/ai-memory-engine.git
cd ai-memory-engine
```

### 2. Set up environment
```bash
python -m venv venv
venv\Scripts\Activate.ps1   # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

### 3. Add your API key (optional — only needed for GPT reconstruction)
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 4. Run the backend
```bash
python main.py
```

### 5. Run the frontend
```bash
streamlit run ui/app.py
```

### 6. Open the app
http://localhost:8501
---

## 📁 Project Structure
ai-memory-engine/
├── ingestion/         # File parsers (chat, notes, PDF, browser, screenshots)
├── vectors/           # Embedding + ChromaDB storage
├── search/            # Semantic search engine
├── reconstruction/    # RAG memory reconstruction
├── api/               # FastAPI backend
├── ui/                # Streamlit frontend
├── data/samples/      # Sample files for testing
└── main.py            # Entry point
---

## 💡 Supported File Types

| Type | Format |
|------|--------|
| Chats | .txt |
| Notes | .md, .pdf |
| Browser History | .json, .csv |
| Screenshots | .png, .jpg |

---

## 🧠 How RAG Works Here

1. **Retrieve** — semantic search finds the most relevant memory chunks
2. **Augment** — chunks are formatted as context for the AI
3. **Generate** — AI reconstructs a coherent narrative from the fragments

---

## 👤 Author

Built by [Vinaya Bollampalli](https://github.com/vinaya285)
