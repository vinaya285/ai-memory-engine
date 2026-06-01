from sentence_transformers import SentenceTransformer


class Embedder:
    """
    Local embedder — completely free, no API key needed.
    Uses sentence-transformers running on your machine.
    """

    def __init__(self):
        print("  Loading local embedding model...")
        # Downloads once (~90MB), then cached locally forever
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        print("  ✅ Local embedder ready")

    def embed(self, text: str) -> list[float]:
        text = text.strip().replace("\n", " ")
        vector = self.model.encode(text)
        return vector.tolist()

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        cleaned = [t.strip().replace("\n", " ") for t in texts]
        vectors = self.model.encode(cleaned)
        return [v.tolist() for v in vectors]