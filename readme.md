# Doc AI - Notes

Small PDF question-answering API using FastAPI, Gemini, and Pinecone.

## How it works

1. Upload a PDF to `POST /documents/upload`.
2. The app reads each PDF page and splits its text into chunks.
3. Gemini creates an embedding for every chunk.
4. The chunks and embeddings are stored in the `doc-ai` Pinecone index.
5. Send a question to `POST /chat`.
6. The app embeds the question, finds the closest chunks in Pinecone, and Gemini writes an answer from those chunks.

## Setup

Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

Pinecone must have an index named `doc-ai` whose vector dimension matches Gemini's `gemini-embedding-001` model.

## Run the API

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

Health check:

```text
GET http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## API notes

### Upload a PDF

```text
POST /documents/upload
Content-Type: multipart/form-data
Field: file=<your PDF>
```

The file is saved in `data/documents/` with a generated ID. Its original filename is stored as Pinecone metadata.

Example response:

```json
{
  "message": "Document uploaded successfully",
  "document_id": "generated-id",
  "filename": "notes.pdf",
  "chunks": 12
}
```

### Ask a question

```text
POST /chat
Content-Type: application/json
```

Request body:

```json
{
  "question": "What is this document about?"
}
```

The response contains `answer` plus `sources`. Each source includes its PDF filename, page number, chunk number, similarity score, and text.

## Important code notes

- `embed_texts(texts)` takes a `list[str]` and returns `list[list[float]]`.
- For one search question, use `embed_texts([query])[0]`: Pinecone needs one vector, not a list of vectors.
- Use package imports such as `from app.rag.embeddings import embed_texts` when running with Uvicorn from the project root.
- The server connects to Pinecone during startup, so an invalid API key, missing index, or no network connection will prevent the app from starting.

## Key files

```text
app/main.py              FastAPI app and routers
app/api/documents.py     PDF upload endpoint
app/api/chat.py          Question endpoint
app/rag/loader.py        Extracts text from PDFs
app/rag/chunker.py       Splits page text into chunks
app/rag/embeddings.py    Creates Gemini embeddings
app/rag/ingest.py        Upload pipeline: PDF -> chunks -> Pinecone
app/rag/retriever.py     Finds relevant chunks in Pinecone
app/rag/generator.py     Creates the final Gemini answer
app/rag/pipeline.py      Combines retrieval and generation
app/rag/vector_store.py  Creates the Pinecone index client
```
