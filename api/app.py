from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import shutil
import os
from pathlib import Path

from api.schemas import (
    SearchRequest, SearchResponse, SearchResultResponse,
    ReconstructRequest, ReconstructResponse,
    IngestResponse, StatusResponse, ClearResponse
)
from vectors.pipeline import IngestionPipeline
from search.semantic_search import SemanticSearch
from reconstruction.free_reconstructor import FreeReconstructor


# ── App setup ────────────────────────────────────────────

app = FastAPI(
    title="AI Memory Reconstruction Engine",
    description="Rebuild forgotten context from screenshots, chats, notes, and more.",
    version="1.0.0"
)

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Shared instances (created once at startup) ───────────

pipeline = IngestionPipeline()
search_engine = SemanticSearch()
reconstructor = FreeReconstructor()


# ── Routes ───────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"message": "🧠 AI Memory Engine is running"}


@app.get("/status", response_model=StatusResponse, tags=["Health"])
def status():
    count = pipeline.store.get_count()
    return StatusResponse(
        total_chunks=count,
        status="ready" if count > 0 else "empty — ingest some files first"
    )


@app.post("/ingest", response_model=IngestResponse, tags=["Ingestion"])
async def ingest_file(file: UploadFile = File(...)):
    """
    Upload any supported file.
    The engine ingests it, embeds it, and stores it.

    Supported: .txt .md .pdf .json .csv .png .jpg
    """
    supported = {".txt", ".md", ".pdf", ".json", ".csv", ".png", ".jpg", ".jpeg"}
    suffix = Path(file.filename).suffix.lower()

    if suffix not in supported:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}. Supported: {supported}"
        )

    # Save uploaded file to a temp location
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=suffix
    ) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        chunks_created = pipeline.ingest_file(tmp_path)
        return IngestResponse(
            filename=file.filename,
            chunks_created=chunks_created,
            message=f"✅ Successfully ingested {file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)  # clean up temp file


@app.post("/search", response_model=SearchResponse, tags=["Search"])
def search(request: SearchRequest):
    """
    Semantic search across all stored memories.
    Returns ranked results by relevance.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if pipeline.store.get_count() == 0:
        raise HTTPException(
            status_code=404,
            detail="No memories stored yet. Ingest some files first."
        )

    # Filter by source type if requested
    if request.source_type:
        results = search_engine.search_by_source(
            request.query,
            request.source_type,
            request.top_k
        )
    else:
        results = search_engine.search(request.query, request.top_k)

    return SearchResponse(
        query=request.query,
        total_found=len(results),
        results=[
            SearchResultResponse(
                text=r.text,
                source_type=r.source_type,
                source_file=r.source_file,
                timestamp=r.timestamp,
                score=r.score
            )
            for r in results
        ]
    )


@app.post("/reconstruct", response_model=ReconstructResponse, tags=["Reconstruction"])
def reconstruct(request: ReconstructRequest):
    """
    Full memory reconstruction.
    Searches relevant chunks and rebuilds a coherent narrative.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if pipeline.store.get_count() == 0:
        raise HTTPException(
            status_code=404,
            detail="No memories stored yet. Ingest some files first."
        )

    result = reconstructor.reconstruct(request.query, request.top_k)

    return ReconstructResponse(
        query=result.query,
        narrative=result.narrative,
        chunks_used=result.chunks_found,
        sources=[
            SearchResultResponse(
                text=r.text,
                source_type=r.source_type,
                source_file=r.source_file,
                timestamp=r.timestamp,
                score=r.score
            )
            for r in result.sources_used
        ]
    )


@app.delete("/clear", response_model=ClearResponse, tags=["Admin"])
def clear_memories():
    """Wipe all stored memories. Use carefully."""
    pipeline.store.clear()
    return ClearResponse(message="🗑️ All memories cleared.")