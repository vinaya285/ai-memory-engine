from pathlib import Path
from ingestion.models import MemoryChunk
from ingestion.chat_ingestor import ChatIngestor
from ingestion.notes_ingestor import NotesIngestor
from ingestion.browser_ingestor import BrowserIngestor


class MasterIngestor:
    """
    Single entry point. Give it any file, it figures out what to do.
    """

    def __init__(self):
        self.chat = ChatIngestor()
        self.notes = NotesIngestor()
        self.browser = BrowserIngestor()

        # Map extensions to ingestors
        self.extension_map = {
            ".txt": self.chat,
            ".md": self.notes,
            ".pdf": self.notes,
            ".json": self.browser,
            ".csv": self.browser,
        }

    def ingest_file(self, file_path: str) -> list[MemoryChunk]:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix in [".png", ".jpg", ".jpeg", ".webp"]:
            # Screenshot — import here to avoid tesseract errors if not installed
            from ingestion.screenshot_ingestor import ScreenshotIngestor
            return [ScreenshotIngestor().ingest(file_path)]

        ingestor = self.extension_map.get(suffix)
        if not ingestor:
            raise ValueError(f"No ingestor found for: {suffix}")

        result = ingestor.ingest(file_path)

        # Some ingestors return a single chunk, others return a list
        return result if isinstance(result, list) else [result]

    def ingest_folder(self, folder_path: str) -> list[MemoryChunk]:
        """Ingest all supported files in a folder"""
        folder = Path(folder_path)
        all_chunks = []

        supported = {".txt", ".md", ".pdf", ".json", ".csv", ".png", ".jpg", ".jpeg"}

        for file in folder.iterdir():
            if file.suffix.lower() in supported:
                print(f"  Ingesting: {file.name}")
                try:
                    chunks = self.ingest_file(str(file))
                    all_chunks.extend(chunks)
                except Exception as e:
                    print(f"  ⚠️  Skipped {file.name}: {e}")

        return all_chunks