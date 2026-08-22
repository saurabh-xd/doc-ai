from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.documents import router as documents_router
from app.api.chat import router as chat_router



app = FastAPI(
    title="AI Document Intelligence",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#This attaches the routes from both modules into the main app.
app.include_router(documents_router)
app.include_router(chat_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}