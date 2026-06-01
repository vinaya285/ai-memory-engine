from pathlib import Path
from datetime import datetime
import uuid
import pdfplumber
from ingestion.models import MemoryChunk


class NotesIngestor:
    """
    Reads .md (markdown) and .pdf notes.
    """

    def ingest(self, file_path: str) -> list[MemoryChunk]:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".md" or suffix == ".txt":
            return self._ingest_markdown(path)
        elif suffix == ".pdf":
            return self._ingest_pdf(path)
        else:
            raise ValueError(f"Unsupported notes format: {suffix}")

    def _ingest_markdown(self, path: Path) -> list[MemoryChunk]:
        text = path.read_text(encoding="utf-8", errors="ignore")

        # Split by headings to preserve structure
        sections = self._split_by_headings(text)

        chunks = []
        for i, section in enumerate(sections):
            if section.strip():
                chunks.append(MemoryChunk(
                    id=str(uuid.uuid4()),
                    text=section.strip(),
                    source_type="note",
                    source_file=path.name,
                    timestamp=datetime.now().isoformat(),
                    metadata={"format": "markdown", "section": i}
                ))
        return chunks

    def _ingest_pdf(self, path: Path) -> list[MemoryChunk]:
        chunks = []
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and text.strip():
                    chunks.append(MemoryChunk(
                        id=str(uuid.uuid4()),
                        text=text.strip(),
                        source_type="note",
                        source_file=path.name,
                        timestamp=datetime.now().isoformat(),
                        metadata={"format": "pdf", "page": i + 1}
                    ))
        return chunks

    def _split_by_headings(self, text: str) -> list[str]:
        """Split markdown by # headings"""
        import re
        sections = re.split(r'\n(?=#{1,3} )', text)
        return sections