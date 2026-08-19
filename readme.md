# Doc-AI

A simple Retrieval-Augmented Generation (RAG) project for PDF-based document Q&A.

This project reads PDF documents, splits them into chunks, converts each chunk into embeddings, stores them in a vector database, retrieves the most relevant chunks for a user question, and uses Gemini to generate an answer grounded in the document content.

## What this project does

1. Loads PDF files from the project data folder.
2. Splits document text into smaller chunks.
3. Creates embeddings for each chunk using Gemini.
4. Stores the embeddings in Pinecone.
5. Queries Pinecone for relevant matches.
6. Sends the retrieved context to Gemini to answer the question.

## Folder structure

```text
doc-ai/
├── app/
│   └── rag/
│       ├── chunker.py          # Splits long text into smaller chunks
│       ├── embeddings.py       # Uses Gemini embeddings for text
│       ├── generator.py        # Generates final answer using Gemini
│       ├── ingest.py           # Full ingestion flow: PDF -> chunks -> embeddings -> Pinecone
│       ├── ingestion.py        # Alternative/older ingestion helper
│       ├── loader.py           # Reads PDF pages using PyMuPDF
│       ├── pipeline.py         # Main question-answer workflow
│       ├── retriever.py        # Searches for relevant document chunks
│       ├── vector_store.py     # Pinecone index setup
│       ├── test_embeddings.py  # Embedding-related tests
│       ├── test_ingest.py      # Ingestion tests
│       ├── test_loader.py      # PDF loader tests
│       └── test_retrieval.py   # Retrieval tests
├── data/
│   └── documents/             # PDF files to ingest
├── tests/                     # General project tests / future additions
├── .env                       # Local environment variables (not committed)
├── requirements.txt           # Python dependencies
├── readme.md                  # Project documentation
└── .gitignore                 # Git ignore rules
```

## Main files explained

### app/rag/loader.py
Loads a PDF file and returns page-by-page text. It uses PyMuPDF to extract text from each page.

### app/rag/chunker.py
Breaks large text into smaller chunks so each section can be embedded and retrieved efficiently.

### app/rag/embeddings.py
Sends text to the Gemini embedding model and returns the vector representation.

### app/rag/vector_store.py
Creates and configures the Pinecone vector index used to store document embeddings.

### app/rag/ingest.py
Main ingestion logic. It loads the PDF, chunks the text, generates embeddings, and stores them in Pinecone.

### app/rag/retriever.py
Takes a user question, embeds it, and queries Pinecone for the most similar document chunks.

### app/rag/generator.py
Builds a prompt using the retrieved context and asks Gemini for the final answer.

### app/rag/pipeline.py
This is the orchestration layer. It calls retrieval and generation together to produce a final response.

### app/rag/ingestion.py
This appears to be an older or alternate ingestion helper and is not the main flow used by the project.

## Setup

1. Create a virtual environment and activate it.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

4. Add your PDF files into the `data/documents` folder.

## Example usage

```python
from app.rag.pipeline import ask

result = ask("What is this document about?")
print(result["answer"])
print(result["sources"])
```

## Notes

- The project is a lightweight example of a document Q&A RAG pipeline.
- It is designed to work with PDF documents.
- Pinecone is used as the vector store and Gemini is used for both embeddings and answer generation.

## Future improvements

- Add a proper app or API layer.
- Support multiple file formats beyond PDF.
- Improve chunking and metadata handling.
- Add a cleaner UI or web interface.
- Add more robust tests and validation.
