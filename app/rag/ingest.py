from loader import load_pdf
from chunker import recursive_chunk_text
from embeddings import embed_text
from vector_store import index


def ingest_pdf(file_path: str, document_id: str):

    pages = load_pdf(file_path)

    vectors = []

    for page in pages:

        chunks = recursive_chunk_text(
            page["text"],
            chunk_size=500
        )

        for chunk_index, text in enumerate(chunks):

            vector = embed_text(text)

            vectors.append({
                "id": f"{document_id}-{page['page_number']}-{chunk_index}",
                "values": vector,
                "metadata": {
                    "document_id": document_id,
                    "page_number": page["page_number"],
                    "chunk_index": chunk_index,
                    "text": text
                }
            })

    index.upsert(vectors=vectors)

    print(f"Uploaded {len(vectors)} vectors.")