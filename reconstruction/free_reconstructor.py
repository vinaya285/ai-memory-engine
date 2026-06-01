from search.semantic_search import SemanticSearch, SearchResult
from reconstruction.prompt_builder import PromptBuilder
from dataclasses import dataclass


@dataclass
class ReconstructionResult:
    query: str
    narrative: str
    sources_used: list[SearchResult]
    chunks_found: int


class FreeReconstructor:
    """
    No GPT. Reconstructs memory by intelligently
    formatting and summarizing the retrieved chunks.
    Good enough for demos without any API cost.
    """

    def __init__(self):
        self.search = SemanticSearch()

    def reconstruct(
        self, query: str, top_k: int = 5
    ) -> ReconstructionResult:

        print(f"\n🔍 Searching memories for: '{query}'")
        results = self.search.search(query, top_k=top_k)

        if not results:
            return ReconstructionResult(
                query=query,
                narrative="No relevant memories found.",
                sources_used=[],
                chunks_found=0
            )

        print(f"  Found {len(results)} relevant chunk(s)")
        narrative = self._build_narrative(query, results)

        return ReconstructionResult(
            query=query,
            narrative=narrative,
            sources_used=results,
            chunks_found=len(results)
        )

    def _build_narrative(
        self, query: str, results: list[SearchResult]
    ) -> str:
        """Build a structured narrative without GPT"""

        # Group by source type
        by_source: dict[str, list[SearchResult]] = {}
        for r in results:
            by_source.setdefault(r.source_type, []).append(r)

        lines = [
            f"Here's what your memory contains about '{query}':\n"
        ]

        source_icons = {
            "chat": "💬",
            "note": "📝",
            "browser": "🌐",
            "screenshot": "🖼️",
            "voice": "🎙️"
        }

        for source_type, chunks in by_source.items():
            icon = source_icons.get(source_type, "📄")
            lines.append(f"{icon} From your {source_type.upper()}S:")

            for chunk in chunks:
                # Take first 200 chars as a clean excerpt
                excerpt = chunk.text[:200].strip()
                if len(chunk.text) > 200:
                    excerpt += "..."
                lines.append(f"  • {excerpt}")
            lines.append("")

        # Add a pattern summary
        lines.append("🔗 Pattern detected:")
        source_list = ", ".join(by_source.keys())
        lines.append(
            f"  Activity related to '{query}' appears across "
            f"your {source_list}. "
            f"Highest relevance score: {results[0].score}."
        )

        return "\n".join(lines)

    def format_output(self, result: ReconstructionResult) -> str:
        lines = [
            "\n" + "="*60,
            "🧠 MEMORY RECONSTRUCTION",
            "="*60,
            f"Query: {result.query}",
            f"Chunks used: {result.chunks_found}",
            "-"*60,
            result.narrative,
            "-"*60,
            "📎 Sources:",
        ]
        for i, src in enumerate(result.sources_used, 1):
            lines.append(
                f"  {i}. [{src.source_type}] {src.source_file} "
                f"(score: {src.score})"
            )
        lines.append("="*60)
        return "\n".join(lines)