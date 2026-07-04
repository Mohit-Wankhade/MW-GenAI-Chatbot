from pathlib import Path
from typing import Any, Dict, List, Optional

import fitz

from utils.logger import logger


def extract_pages_from_pdf(
    pdf_path: str,
    source_name: Optional[str] = None,
    original_filename: Optional[str] = None,
    uploaded_by: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Extracts readable text page-by-page from a PDF using PyMuPDF.

    Returns:
    [
        {
            "page_number": 1,
            "text": "...",
            "source": "stored-file.pdf",
            "original_filename": "resume.pdf",
            "uploaded_by": "username"
        }
    ]
    """

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    pages: List[Dict[str, Any]] = []

    try:
        with fitz.open(str(path)) as document:
            if document.is_encrypted:
                raise ValueError("Encrypted/password-protected PDFs are not supported.")

            for page_index in range(len(document)):
                page = document[page_index]
                text = page.get_text("text") or ""
                clean_text = " ".join(text.replace("\x00", " ").split())

                if not clean_text:
                    continue

                pages.append(
                    {
                        "page_number": page_index + 1,
                        "text": clean_text,
                        "source": source_name or path.name,
                        "original_filename": original_filename or path.name,
                        "uploaded_by": uploaded_by,
                    }
                )

        logger.info(
            "Extracted text from PDF. file=%s pages_with_text=%s",
            path.name,
            len(pages),
        )

        return pages

    except Exception:
        logger.exception("Failed to extract text from PDF: %s", path)
        raise