from pathlib import Path
from app.rag.loader import load_pdf
from app.rag.chunker import recursive_chunk_text
from app.rag.embeddings import embed_text
from app.rag.vector_store import index

def ingest_pdf(
    file_path: str,
    document_id: str,
    filename: str
):
    pages = load_pdf(file_path)

    chunks = []

    for page in pages:

        page_chunks = recursive_chunk_text(
            page["text"],
            chunk_size=500
        )

        for chunk_index, text in enumerate(page_chunks):

            chunks.append({
                "text": text,
                "page_number": page["page_number"],
                "chunk_index": chunk_index
            })

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = embed_texts(texts)

    vectors = []

    for chunk, embedding in zip(chunks, embeddings):

        vector_id = (
            f"{document_id}-"
            f"{chunk['page_number']}-"
            f"{chunk['chunk_index']}"
        )

        vectors.append({
            "id": vector_id,
            "values": embedding,
            "metadata": {
                "document_id": document_id,
                "filename": filename,
                "page_number": chunk["page_number"],
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"]
            }
        })

    index.upsert(vectors=vectors)

    return {
        "document_id": document_id,
        "chunks": len(vectors)
    }