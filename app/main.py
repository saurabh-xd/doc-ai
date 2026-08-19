from fastapi import FastAPI

from app.api.documents import router as documents_router
from app.api.chat import router as chat_router



app = FastAPI(
    title="AI Document Intelligence",
    version="1.0.0"
)


app.include_router(documents_router)
app.include_router(chat_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}