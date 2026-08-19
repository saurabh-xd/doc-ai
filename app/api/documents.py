from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil

from app.rag.ingest import ingest_pdf


router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = Path("data/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document_id = Path(file.filename).stem

    ingest_pdf(
        str(file_path),
        document_id
    )

    return {
        "message": "Document uploaded successfully",
        "document_id": document_id,
        "filename": file.filename
    }