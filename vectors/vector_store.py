import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from ingestion.models import MemoryChunk
from vectors.embedder import Embedder
import os

load_dotenv()


class VectorStore:
    """
    Stores and retrieves memory chunks using ChromaDB.
    """

    def __init__(self):
        db_path = os.getenv("CHROMA_DB_PATH", "./chroma_store")
        collection_name = os.getenv("COLLECTION_NAME", "memory_engine")

        # Connect to ChromaDB (creates the folder if it doesn't exist)
        self.client = chromadb.PersistentClient(path=db_path)

        # Get or create the collection (like a table in a normal DB)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # cosine similarity for semantic search
        )

        self.embedder = Embedder()
        print(f"✅ VectorStore connected — collection: '{collection_name}'")

    def add_chunks(self, chunks: list[MemoryChunk]) -> None:
        """
        Embed and store a list of MemoryChunks into ChromaDB.
        """
        if not chunks:
            print("⚠️  No chunks to add.")
            return

        print(f"  Embedding {len(chunks)} chunk(s)...")

        # Extract texts for batch embedding (one API call = cheaper)
        texts = [chunk.text for chunk in chunks]
        vectors = self.embedder.embed_many(texts)

        # Prepare data for ChromaDB
        ids = [chunk.id for chunk in chunks]

        metadatas = [
            {
                "source_type": chunk.source_type,
                "source_file": chunk.source_file,
                "timestamp": chunk.timestamp or "",
                **{k: str(v) for k, v in chunk.metadata.items()}
            }
            for chunk in chunks
        ]

        # Store everything in ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=vectors,
            documents=texts,
            metadatas=metadatas
        )

        print(f"  ✅ Stored {len(chunks)} chunk(s) in vector DB")

    def get_count(self) -> int:
        """How many chunks are currently stored"""
        return self.collection.count()

    def clear(self) -> None:
        """Wipe the entire collection — useful for testing"""
        self.client.delete_collection(
            os.getenv("COLLECTION_NAME", "memory_engine")
        )
        self.collection = self.client.get_or_create_collection(
            name=os.getenv("COLLECTION_NAME", "memory_engine"),
            metadata={"hnsw:space": "cosine"}
        )
        print("🗑️  Vector store cleared.")