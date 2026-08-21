from fastapi import APIRouter
from pydantic import BaseModel

from app.rag.pipeline import ask
from fastapi.responses import StreamingResponse

from app.rag.pipeline import prepare_rag_context
from app.rag.generator import stream_answer


router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str


@router.post("")
def chat(request: ChatRequest):

    context_chunks = prepare_rag_context(
        request.question,
        request.user_id
    )

    def generate():


        for chunk in stream_answer(
            request.question,
            context_chunks
        ):
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )

    result = ask(request.question)

    return result