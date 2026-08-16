from loader import load_pdf
from chunker import chunk_text


def ingest_pdf(file_path: str, document_id: str):

    pages = load_pdf(file_path)

    chunks = []

    for page in pages:

        page_chunks = chunk_text(page["text"])

        for chunk_index, text in enumerate(page_chunks):

            chunks.append({
                "text": text,
                "metadata": {
                    "document_id": document_id,
                    "page_number": page["page_number"],
                    "chunk_index": chunk_index
                }
            })

    return chunks