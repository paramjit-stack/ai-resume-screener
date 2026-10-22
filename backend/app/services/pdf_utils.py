
import pymupdf
from fastapi import HTTPException

MAX_FILE_SIZE = 10 * 1024 * 1024


def extract_pdf_text(content: bytes, label: str = "PDF") -> str:
    """Validate a PDF and extract its selectable text."""

    if not content:
        raise HTTPException(status_code=400, detail=f"{label} is empty.")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"{label} exceeds the 10 MB limit.",
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail=f"{label} is not a valid PDF.",
        )

    try:
        with pymupdf.open(stream=content, filetype="pdf") as pdf:
            if pdf.page_count == 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"{label} contains no pages.",
                )

            text = "\n".join(page.get_text() for page in pdf).strip()

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"{label} is damaged or cannot be read.",
        )

    if not text:
        raise HTTPException(
            status_code=422,
            detail=f"No selectable text found in {label}; OCR may be needed.",
        )

    return text
