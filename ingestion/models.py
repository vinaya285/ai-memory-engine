from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MemoryChunk(BaseModel):
    """
    One unit of memory. Every source produces these.
    """
    id: str                        # unique ID
    text: str                      # the actual content
    source_type: str               # "screenshot", "chat", "note", "voice", "browser"
    source_file: str               # original filename
    timestamp: Optional[str] = None  # when it happened
    metadata: dict = {}            # any extra info

    def preview(self) -> str:
        """Short preview for debugging"""
        return f"[{self.source_type}] {self.text[:80]}..."