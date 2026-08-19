from app.rag.retriever import retrieve
from app.rag.generator import generate_answer


def ask(question: str):

    matches = retrieve(
        question,
        top_k=5
    )

    answer = generate_answer(
        question,
        matches
    )

    sources = []

    for match in matches:

        sources.append({
            "document_id": match.metadata["document_id"],
            "filename": match.metadata["filename"],
            "page_number": match.metadata["page_number"],
            "chunk_index": match.metadata["chunk_index"],
            "score": match.score,
            "text": match.metadata["text"]
        })

    return {
        "answer": answer,
        "sources": sources
    }
