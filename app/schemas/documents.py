from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str
    chunks: int
