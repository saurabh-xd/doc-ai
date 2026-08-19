from fastapi import APIRouter
from pydantic import BaseModel

from app.rag.pipeline import ask


router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str


@router.post("")
def chat(request: ChatRequest):

    result = ask(request.question)

    return result