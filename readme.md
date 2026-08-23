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
python -m pip install -r requirements.txt
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
python -m uvicorn app.main:app --reload
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
  main.py                     Creates the FastAPI app and adds routes
  api/                        HTTP endpoint modules
    auth.py                   Signup and signin endpoints
    documents.py              Upload-PDF endpoint
    chat.py                   Question-and-answer endpoint
  core/                       Shared configuration and security
    config.py                 Environment values
    database.py               Lazy Neon SQLAlchemy session factory
    security.py               Bcrypt password helpers
    auth.py                   JWT creation and validation dependency
  models/                     Neon database table models
    user.py                   User table model
  schemas/                    Pydantic request and response models
    auth.py                   Authentication schemas
    chat.py                   Chat request schema
    documents.py              Document upload response schema
  rag/
    pipeline.py               Coordinates retrieval and answer generation
    ingestion/                PDF -> text -> chunks -> Pinecone
      loader.py               Extracts text from PDF pages
      chunker.py              Splits page text into overlapping chunks
      ingest.py               Embeds and stores PDF chunks
    retrieval/                Question -> relevant chunks
      embeddings.py           Creates Gemini embeddings
      vector_store.py         Opens the Pinecone index on demand
      query_rewriter.py       Rewrites questions for search
      retriever.py            Searches Pinecone for candidate chunks
      reranker.py             Reranks candidates with Cohere
    generation/               Evidence chunks -> answer
      context.py              Builds the final evidence context
      generator.py            Streams the Gemini answer
evaluation/
  questions.json          Test questions and expected PDF pages
  evaluate_retrieval.py   Retrieval evaluation script
tests/
  test_auth.py             JWT and password helper checks
  test_chunker.py          Chunk-size and overlap checks
  test_retrieval.py        Retrieval user-filter check
```

## Retrieval evaluation

`evaluation/questions.json` contains example questions and their expected page numbers. The evaluation script reports Recall@5 for the user ID set in `EVALUATION_USER_ID`.

It currently needs a small import correction before it can run (see the known issues below). Once corrected, run it from the project root with:

```powershell
$env:EVALUATION_USER_ID="your-neon-user-uuid"
python -m evaluation.evaluate_retrieval
```

## Known limits

- Upload work (PDF parsing, embedding, and Pinecone upsert) runs inside the request. Large PDFs can block a worker and may time out.
- There is no delete-document endpoint or Pinecone cleanup yet.
- Authentication uses local JWTs; add refresh tokens, password resets, and email verification before a public deployment.
- The chat endpoint streams only answer text; it does not return source pages or document names to the client.
