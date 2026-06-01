from pathlib import Path
from datetime import datetime
import uuid
from ingestion.models import MemoryChunk


class ChatIngestor:
    """
    Reads plain text chat exports.
    Works with WhatsApp, Telegram, Slack exports, or any .txt chat.
    Splits into chunks so large chats don't become one massive blob.
    """

    def __init__(self, chunk_size: int = 500):
        self.chunk_size = chunk_size  # characters per chunk

    def ingest(self, file_path: str) -> list[MemoryChunk]:
        path = Path(file_path)
        raw_text = path.read_text(encoding="utf-8", errors="ignore")

        # Split into manageable chunks
        chunks = self._split_text(raw_text)

        memory_chunks = []
        for i, chunk in enumerate(chunks):
            memory_chunks.append(MemoryChunk(
                id=str(uuid.uuid4()),
                text=chunk.strip(),
                source_type="chat",
                source_file=path.name,
                timestamp=datetime.now().isoformat(),
                metadata={"chunk_index": i, "total_chunks": len(chunks)}
            ))

        return memory_chunks

    def _split_text(self, text: str) -> list[str]:
        """Split text into chunks of roughly chunk_size characters"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1

            if current_length >= self.chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks