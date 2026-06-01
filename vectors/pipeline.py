from ingestion.master_ingestor import MasterIngestor
from vectors.vector_store import VectorStore
from pathlib import Path


class IngestionPipeline:
    """
    End-to-end pipeline:
    File → MemoryChunks → Embeddings → ChromaDB
    """

    def __init__(self):
        self.ingestor = MasterIngestor()
        self.store = VectorStore()

    def ingest_file(self, file_path: str) -> int:
        """
        Ingest a single file into the vector store.
        Returns number of chunks stored.
        """
        print(f"\n📥 Ingesting: {Path(file_path).name}")

        # Step 2: file → chunks
        chunks = self.ingestor.ingest_file(file_path)
        print(f"  Parsed into {len(chunks)} chunk(s)")

        # Step 3: chunks → embeddings → ChromaDB
        self.store.add_chunks(chunks)

        return len(chunks)

    def ingest_folder(self, folder_path: str) -> int:
        """
        Ingest all supported files in a folder.
        Returns total chunks stored.
        """
        print(f"\n📂 Ingesting folder: {folder_path}")
        folder = Path(folder_path)
        total = 0

        supported = {".txt", ".md", ".pdf", ".json", ".csv", ".png", ".jpg"}

        for file in folder.iterdir():
            if file.suffix.lower() in supported:
                try:
                    count = self.ingest_file(str(file))
                    total += count
                except Exception as e:
                    print(f"  ⚠️  Skipped {file.name}: {e}")

        print(f"\n✅ Total chunks stored: {total}")
        return total

    def status(self) -> None:
        """Print current DB status"""
        count = self.store.get_count()
        print(f"\n📊 Vector DB status: {count} chunk(s) stored")