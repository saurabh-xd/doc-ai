from fastapi import APIRouter
from pydantic import BaseModel

from fastapi.responses import StreamingResponse

from app.rag.pipeline import prepare_rag_context
from app.rag.generator import generate_answer


router = APIRouter(prefix="/chat", tags=["Chat"])

# Must match the temporary development identity used for uploads.
DEVELOPMENT_USER_ID = "test-user"


class ChatRequest(BaseModel):
    question: str


@router.post("")
def chat(request: ChatRequest):

    context_chunks = prepare_rag_context(
        request.question,
        DEVELOPMENT_USER_ID
    )

    def generate():


        for chunk in generate_answer(
            request.question,
            context_chunks
        ):
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )
