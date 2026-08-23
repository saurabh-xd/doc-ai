# Doc AI

Doc AI is a small FastAPI service for asking questions about PDF files. Upload a PDF, then ask a question. The app finds relevant PDF text in Pinecone and uses Gemini to produce an answer.

## What happens when you use it

1. You upload a PDF.
2. The app reads its pages and splits their text into small chunks.
3. Gemini creates an embedding for each chunk.
4. The chunks are stored in Pinecone with the PDF name and page number.
5. When you ask a question, the app rewrites the question, searches Pinecone, reranks the results with Cohere, and streams a Gemini answer.

## Requirements

- Python 3.12 or newer
- A Gemini API key
- A Pinecone API key and an existing Pinecone index named `doc-ai`
- A Cohere API key

The Pinecone index must use the same vector dimension as Gemini's `gemini-embedding-001` model. The application does not create the index for you.

## Setup

From the project folder, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
COHERE_API_KEY=your_cohere_api_key
DATABASE_URL=postgresql+psycopg://user:password@your-neon-host/neondb?sslmode=require
JWT_SECRET=at-least-32-random-characters
```

For a secure value on PowerShell, generate one with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Apply the included Neon user-table migration once the database URL is set:

```powershell
alembic upgrade head
```

## Run the API

```powershell
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/docs> to use FastAPI's interactive API page.

Check that the service is running:

```text
GET http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## Use the API

### Upload a PDF

```text
POST /documents/upload
Content-Type: multipart/form-data
Field: file=<your PDF>
```

PowerShell example:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/documents/upload" -F "file=@C:\path\to\document.pdf"
```

The API saves the uploaded file in `data/documents/` with a generated filename. A successful response looks like this:

```json
{
  "message": "Document uploaded successfully",
  "document_id": "generated-id",
  "filename": "document.pdf",
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

PowerShell example:

```powershell
curl.exe -N -X POST "http://127.0.0.1:8000/chat" -H "Content-Type: application/json" -d "{\"question\": \"What is this document about?\"}"
```

The response is streamed as plain text. It is not JSON and does not currently return source information.

## Authentication setup

Upload and chat require an `Authorization: Bearer <JWT>` header. The JWT's
`sub` field is used as the Pinecone `user_id`, so users can retrieve only their
own document chunks.

The Neon `users` model, password helpers, JWT validation, migration, signup,
and signin endpoints are included. Read the short comments in
[`app/api/auth.py`](app/api/auth.py) to follow each security step.

## Project structure

```text
app/
  main.py                 Creates the FastAPI app and adds routes
  api/auth.py             Neon-backed signup and signin endpoints
  api/documents.py        Upload-PDF endpoint
  api/chat.py             Question-and-answer endpoint
  core/config.py          Environment configuration
  core/database.py        Lazy Neon SQLAlchemy session factory
  core/security.py        Bcrypt password helpers
  core/auth.py            JWT creation and validation dependency
  models/user.py          Neon user table model
  rag/
    loader.py             Extracts text from PDF pages
    chunker.py            Splits page text into chunks
    embeddings.py         Creates Gemini embeddings
    ingest.py             Stores PDF chunks in Pinecone
    retriever.py          Searches Pinecone for relevant chunks
    query_rewriter.py     Rewrites questions for search
    reranker.py           Reranks search results with Cohere
    context.py            Builds the context sent to Gemini
    generator.py          Streams the answer from Gemini
    pipeline.py           Connects retrieval, reranking, and context building
evaluation/
  questions.json          Test questions and expected PDF pages
  evaluate_retrieval.py   Retrieval evaluation script
```

## Retrieval evaluation

`evaluation/questions.json` contains example questions and their expected page numbers. The evaluation script reports Recall@5 for the user ID set in `EVALUATION_USER_ID`.

It currently needs a small import correction before it can run (see the known issues below). Once corrected, run it from the project root with:

```powershell
$env:EVALUATION_USER_ID="your-neon-user-uuid"
python -m evaluation.evaluate_retrieval
```

## Known issues and limits

- The evaluation script imports `retriever` as a standalone module even though it uses `app.rag...` imports. It should import `from app.rag.retriever import retrieve` and place the project root on the import path, or be run as a package module.
- The chunker accepts an `overlap` value but never applies it. Long text is also not recursively split with the later separators, so chunks can exceed the requested size.
- Empty PDF pages can produce empty chunks and send empty strings for embedding.
- Upload work (PDF parsing, embedding, and Pinecone upsert) runs inside the request. Large PDFs can block a worker and may time out.
- Failed uploads can leave the saved PDF on disk, and there is no delete-document endpoint or Pinecone cleanup.
- There is no file-size limit, PDF content validation, or friendly error handling for Gemini, Cohere, Pinecone, or malformed PDFs.
- Authentication uses local JWTs; add refresh tokens, password resets, and email verification before a public deployment.
- The chat endpoint streams only answer text; it does not return the source pages or document names to the client.
- There are no automated tests, and API keys/index configuration are not validated at startup with clear error messages.
