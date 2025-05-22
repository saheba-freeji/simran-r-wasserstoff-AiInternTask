from pathlib import Path
from typing import Dict, Any
import pdfplumber
import pytesseract
from PIL import Image
import docx

class DocumentParser:
    def __init__(self):
        pass


    def parse_file(self, file_path: str) -> Dict[str, Any]:
        ext = Path(file_path).suffix.lower()

        if ext == ".pdf":
            return self._parse_pdf(file_path)
        elif ext in [".png", ".jpg", ".jpeg", ".tiff"]:
            return self._parse_image(file_path)
        elif ext == ".docx":
            return self._parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _parse_pdf(self, file_path: str) -> Dict[str, Any]:
        content = []
        pages = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    paragraphs = text.strip().split('\n\n')
                    for p_idx, para in enumerate(paragraphs):
                        if para.strip():
                            content.append(para.strip())
                            pages.append({"page": i + 1, "paragraph": p_idx + 1})
        
        return {
            "type": "pdf",
            "text": "\n\n".join(content),
            "source": Path(file_path).name,
            "page_count": len(content),
            "pages": pages
        }

    def _parse_image(self, file_path: str) -> Dict[str, Any]:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return {
            "type": "image",
            "text": text.strip(),
            "source": Path(file_path).name
        }

    def _parse_docx(self, file_path: str) -> Dict[str, Any]:
        doc = docx.Document(file_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return {
            "type": "docx",
            "text": "\n".join(paragraphs),
            "source": Path(file_path).name,
            "paragraphs": len(paragraphs)
        }