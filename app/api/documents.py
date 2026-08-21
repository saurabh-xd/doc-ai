from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
from uuid import uuid4

from app.rag.ingest import ingest_pdf

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = Path("data/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Temporary local-development identity. Replace with authenticated user IDs
# before deploying the API.
DEVELOPMENT_USER_ID = "test-user"


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    document_id = str(uuid4())

    file_path = UPLOAD_DIR / f"{document_id}.pdf"

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = ingest_pdf(
        str(file_path),
        document_id,
        file.filename,
        DEVELOPMENT_USER_ID
    )

    return {
        "message": "Document uploaded successfully",
        "document_id": document_id,
        "filename": file.filename,
        "chunks": result["chunks"]
    }
