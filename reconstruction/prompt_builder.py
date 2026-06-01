from search.semantic_search import SearchResult


class PromptBuilder:
    """
    Builds the prompt sent to GPT for memory reconstruction.
    Formats retrieved chunks as context, then asks GPT to reconstruct.
    """

    SYSTEM_PROMPT = """You are an AI Memory Reconstruction Engine.

Your job is to help users remember and reconstruct context from their 
digital life — their chats, notes, screenshots, and browser history.

When given memory fragments, you:
1. Identify the core theme or activity they were focused on
2. Reconstruct a clear, coherent narrative of what happened
3. Surface key decisions, ideas, or action items buried in the fragments
4. Connect dots across different sources (chat + notes + browser)
5. Present it in a warm, helpful tone — like a smart assistant catching you up

Always be specific. Use actual details from the memory fragments.
Never make up information not present in the fragments.
If context is thin, say so honestly."""

    def build(self, query: str, results: list[SearchResult]) -> list[dict]:
        """
        Build the full message list for the GPT API call.

        Returns a list of messages in OpenAI format:
        [{"role": "system", ...}, {"role": "user", ...}]
        """

        # Format each memory chunk clearly
        context_blocks = []
        for i, result in enumerate(results, 1):
            block = f"""--- Memory Fragment #{i} ---
Source: {result.source_type.upper()} | File: {result.source_file}
Time: {result.timestamp[:19] if result.timestamp else 'Unknown'}
Relevance Score: {result.score}

{result.text}
"""
            context_blocks.append(block)

        context_text = "\n".join(context_blocks)

        user_message = f"""I need help reconstructing my memory around this:

"{query}"

Here are the relevant memory fragments retrieved from my digital history:

{context_text}

Please reconstruct what I was working on, thinking about, or doing.
Be specific, use the actual details from the fragments, and connect
any patterns you notice across the different sources."""

        return [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]

    def build_summary_prompt(self, results: list[SearchResult]) -> list[dict]:
        """
        Build a prompt for summarizing ALL stored memories.
        Used for the 'What have I been up to?' feature.
        """

        context_blocks = []
        for i, result in enumerate(results, 1):
            block = f"""--- Fragment #{i} | {result.source_type.upper()} ---
{result.text[:200]}
"""
            context_blocks.append(block)

        context_text = "\n".join(context_blocks)

        user_message = f"""Based on these memory fragments from my digital life,
give me a high-level summary of what I've been focused on recently.

{context_text}

What are the main themes, projects, and ideas I've been working on?"""

        return [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]