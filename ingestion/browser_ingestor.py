import json
import csv
from pathlib import Path
from datetime import datetime
import uuid
from ingestion.models import MemoryChunk


class BrowserIngestor:
    """
    Reads browser history.
    Supports Chrome JSON export and generic CSV format.
    """

    def ingest(self, file_path: str) -> list[MemoryChunk]:
        path = Path(file_path)

        if path.suffix.lower() == ".json":
            return self._ingest_json(path)
        elif path.suffix.lower() == ".csv":
            return self._ingest_csv(path)
        else:
            raise ValueError(f"Unsupported browser history format: {path.suffix}")

    def _ingest_json(self, path: Path) -> list[MemoryChunk]:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        chunks = []
        # Chrome history format
        items = data if isinstance(data, list) else data.get("Browser History", [])

        for item in items:
            title = item.get("title", "Untitled")
            url = item.get("url", "")
            time_usec = item.get("time_usec", "")

            text = f"Visited: {title}\nURL: {url}"

            chunks.append(MemoryChunk(
                id=str(uuid.uuid4()),
                text=text,
                source_type="browser",
                source_file=path.name,
                timestamp=str(time_usec),
                metadata={"url": url, "title": title}
            ))

        return chunks

    def _ingest_csv(self, path: Path) -> list[MemoryChunk]:
        chunks = []
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get("title", row.get("Title", "Untitled"))
                url = row.get("url", row.get("URL", ""))
                text = f"Visited: {title}\nURL: {url}"

                chunks.append(MemoryChunk(
                    id=str(uuid.uuid4()),
                    text=text,
                    source_type="browser",
                    source_file=path.name,
                    timestamp=datetime.now().isoformat(),
                    metadata={"url": url, "title": title}
                ))
        return chunks