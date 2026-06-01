from vectors.vector_store import VectorStore
from vectors.embedder import Embedder
from dataclasses import dataclass


@dataclass
class SearchResult:
    """One search result — the chunk + how relevant it is"""
    text: str
    source_type: str
    source_file: str
    timestamp: str
    score: float           # 0.0 to 1.0 — higher = more relevant
    metadata: dict


class SemanticSearch:
    """
    Takes a plain English query.
    Returns ranked memory chunks by meaning.
    """

    def __init__(self):
        self.store = VectorStore()
        self.embedder = Embedder()

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """
        Search the vector DB with a natural language query.

        query  — what you're looking for
        top_k  — how many results to return
        """

        if not query.strip():
            return []

        # 1. Embed the query using the same model used for storage
        query_vector = self.embedder.embed(query)

        # 2. Ask ChromaDB for the closest matches
        raw = self.store.collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, self.store.get_count()),
            include=["documents", "metadatas", "distances"]
        )

        # 3. Parse raw results into clean SearchResult objects
        results = []
        documents = raw["documents"][0]
        metadatas = raw["metadatas"][0]
        distances = raw["distances"][0]

        for doc, meta, distance in zip(documents, metadatas, distances):
            # ChromaDB returns cosine distance (0=identical, 2=opposite)
            # Convert to similarity score (1.0 = perfect match)
            score = round(1 - (distance / 2), 4)

            results.append(SearchResult(
                text=doc,
                source_type=meta.get("source_type", "unknown"),
                source_file=meta.get("source_file", "unknown"),
                timestamp=meta.get("timestamp", ""),
                score=score,
                metadata=meta
            ))

        # Sort by score descending (best match first)
        results.sort(key=lambda r: r.score, reverse=True)
        return results

    def search_by_source(
        self, query: str, source_type: str, top_k: int = 5
    ) -> list[SearchResult]:
        """
        Search but filter by source type.
        e.g. only search inside 'chat' or only 'note'
        """
        all_results = self.search(query, top_k=top_k * 3)
        filtered = [r for r in all_results if r.source_type == source_type]
        return filtered[:top_k]

    def format_results(self, results: list[SearchResult]) -> str:
        """Pretty print results for terminal or debugging"""
        if not results:
            return "No results found."

        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"{'─'*50}")
            lines.append(f"Result #{i}  |  Score: {r.score}  |  Source: {r.source_type}")
            lines.append(f"File: {r.source_file}  |  Time: {r.timestamp[:19]}")
            lines.append(f"\n{r.text[:300]}")
            if len(r.text) > 300:
                lines.append("... [truncated]")

        lines.append(f"{'─'*50}")
        return "\n".join(lines)