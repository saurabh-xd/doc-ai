from pathlib import Path
from app.rag.ingestion.chunker import recursive_chunk_text
from app.rag.ingestion.loader import load_pdf
from app.rag.retrieval.embeddings import embed_texts
from app.rag.retrieval.vector_store import get_index

EMBEDDING_BATCH_SIZE = 96
UPSERT_BATCH_SIZE = 100

def ingest_pdf(
    file_path: str,
    document_id: str,
    filename: str,
    user_id: str
):
    pages = load_pdf(file_path)

    chunks = []

    for page in pages:

        page_chunks = recursive_chunk_text(
            page["text"],
            chunk_size=500
        )

        for chunk_index, text in enumerate(page_chunks):
            if not text.strip():
                continue

            chunks.append({
                "text": text,
                "page_number": page["page_number"],
                "chunk_index": chunk_index
            })

    vectors = []

    if not chunks:
        raise ValueError("The PDF does not contain extractable text")

    for start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        batch = chunks[start:start + EMBEDDING_BATCH_SIZE]
        embeddings = embed_texts([chunk["text"] for chunk in batch])

        for chunk, embedding in zip(batch, embeddings):

            vector_id = (
                f"{document_id}-"
                f"{chunk['page_number']}-"
                f"{chunk['chunk_index']}"
            )

            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "user_id": user_id,
                    "document_id": document_id,
                    "filename": filename,
                    "page_number": chunk["page_number"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"]
                }
            })

    index = get_index()
    for start in range(0, len(vectors), UPSERT_BATCH_SIZE):
        index.upsert(vectors=vectors[start:start + UPSERT_BATCH_SIZE])

    return {
        "document_id": document_id,
        "chunks": len(vectors)
    }
