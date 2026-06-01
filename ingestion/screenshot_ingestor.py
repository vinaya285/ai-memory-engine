import pytesseract
from PIL import Image
from pathlib import Path
from datetime import datetime
import uuid
from ingestion.models import MemoryChunk


class ScreenshotIngestor:
    """
    Reads a screenshot image and extracts text using OCR.
    """

    def __init__(self):
        # If on Windows and tesseract isn't in PATH, set it manually:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass

    def ingest(self, file_path: str) -> MemoryChunk:
        path = Path(file_path)

        # Open image and run OCR
        image = Image.open(path)
        extracted_text = pytesseract.image_to_string(image).strip()

        if not extracted_text:
            extracted_text = "[Screenshot contained no readable text]"

        return MemoryChunk(
            id=str(uuid.uuid4()),
            text=extracted_text,
            source_type="screenshot",
            source_file=path.name,
            timestamp=datetime.now().isoformat(),
            metadata={"width": image.width, "height": image.height}
        )