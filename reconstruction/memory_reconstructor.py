from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass
from search.semantic_search import SemanticSearch, SearchResult
from reconstruction.prompt_builder import PromptBuilder
import os

load_dotenv()


@dataclass
class ReconstructionResult:
    """The final output — reconstructed memory + sources used"""
    query: str
    narrative: str                  # GPT's reconstruction
    sources_used: list[SearchResult]  # chunks that informed it
    chunks_found: int


class MemoryReconstructor:
    """
    The core engine.
    Query → Search → Reconstruct → Return narrative.
    """

    def __init__(self):
        self.search = SemanticSearch()
        self.prompt_builder = PromptBuilder()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"  # cheap + smart enough

    def reconstruct(
        self, query: str, top_k: int = 5
    ) -> ReconstructionResult:
        """
        Full pipeline: query → search → GPT → narrative.
        """

        print(f"\n🔍 Searching memories for: '{query}'")

        # Step 1: Semantic search
        results = self.search.search(query, top_k=top_k)

        if not results:
            return ReconstructionResult(
                query=query,
                narrative="No relevant memories found. Try ingesting some files first.",
                sources_used=[],
                chunks_found=0
            )

        print(f"  Found {len(results)} relevant chunk(s)")
        print(f"  Top score: {results[0].score}")

        # Step 2: Build prompt
        messages = self.prompt_builder.build(query, results)

        # Step 3: Call GPT
        print("  Reconstructing memory with GPT...")
        narrative = self._call_gpt(messages)

        return ReconstructionResult(
            query=query,
            narrative=narrative,
            sources_used=results,
            chunks_found=len(results)
        )

    def summarize_all(self, sample_size: int = 20) -> str:
        """
        'What have I been up to?' — summarizes everything in the DB.
        """
        print("\n📋 Generating full memory summary...")

        # Grab a broad sample of stored memories
        results = self.search.search("projects work ideas notes", top_k=sample_size)

        if not results:
            return "No memories stored yet."

        messages = self.prompt_builder.build_summary_prompt(results)
        return self._call_gpt(messages)

    def _call_gpt(self, messages: list[dict]) -> str:
        """Make the actual API call to GPT"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7  # slight creativity for natural narrative
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Reconstruction failed: {str(e)}"

    def format_output(self, result: ReconstructionResult) -> str:
        """Pretty print the full reconstruction result"""
        lines = [
            "\n" + "="*60,
            f"🧠 MEMORY RECONSTRUCTION",
            "="*60,
            f"Query: {result.query}",
            f"Chunks used: {result.chunks_found}",
            "-"*60,
            "📖 Reconstructed Memory:",
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