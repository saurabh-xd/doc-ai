import logging #use logging instead of print() for application diagnostics,

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from fastapi.responses import StreamingResponse

from app.rag.pipeline import prepare_rag_context
from app.rag.generator import generate_answer
from app.core.auth import get_current_user


router = APIRouter(prefix="/chat", tags=["Chat"])  # like express router

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2_000)


@router.post("")
def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
):

    try:
        context_chunks = prepare_rag_context(
            request.question,
            current_user["id"],
        )
    except Exception as exc:
        logger.exception("Retrieval failed")
        raise HTTPException(     # fastapi error response
            status_code=502,
            detail="Document retrieval is temporarily unavailable",
        ) from exc

    def generate():
        try:
            for chunk in generate_answer(
                request.question,
                context_chunks,
            ):
                yield chunk
        except Exception:
            logger.exception("Answer generation failed")
            yield "\n\nUnable to generate an answer right now. Please try again."

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )
