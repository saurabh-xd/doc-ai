from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
import logging
from pathlib import Path
from uuid import uuid4

from app.rag.ingest import ingest_pdf
from app.core.auth import get_current_user

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = Path("data/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    header = await file.read(5)
    if header != b"%PDF-":
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF")

    document_id = str(uuid4())

    file_path = UPLOAD_DIR / f"{document_id}.pdf"

    try:
        bytes_written = len(header)
        with file_path.open("wb") as buffer:
            buffer.write(header)
            while content := await file.read(1024 * 1024):
                bytes_written += len(content)
                if bytes_written > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail="PDF files must be 20 MB or smaller",
                    )
                buffer.write(content)

        result = ingest_pdf(
            str(file_path),
            document_id,
            file.filename,
            current_user["id"],
        )
    except ValueError as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except HTTPException:
        file_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        file_path.unlink(missing_ok=True)
        logger.exception("Document ingestion failed")
        raise HTTPException(
            status_code=502,
            detail="Document processing is temporarily unavailable",
        ) from exc
    finally:
        await file.close()

    return {
        "message": "Document uploaded successfully",
        "document_id": document_id,
        "filename": file.filename,
        "chunks": result["chunks"]
    }
