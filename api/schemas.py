from pydantic import BaseModel
from typing import Optional


# ── Request models ───────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    source_type: Optional[str] = None  # filter by source if needed


class ReconstructRequest(BaseModel):
    query: str
    top_k: int = 5


# ── Response models ──────────────────────────────────────

class SearchResultResponse(BaseModel):
    text: str
    source_type: str
    source_file: str
    timestamp: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultResponse]
    total_found: int


class ReconstructResponse(BaseModel):
    query: str
    narrative: str
    chunks_used: int
    sources: list[SearchResultResponse]


class IngestResponse(BaseModel):
    filename: str
    chunks_created: int
    message: str


class StatusResponse(BaseModel):
    total_chunks: int
    status: str


class ClearResponse(BaseModel):
    message: str