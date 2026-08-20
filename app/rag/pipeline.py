from app.rag.retriever import retrieve
from app.rag.generator import generate_answer
from app.rag.query_rewriter import rewrite_query
from app.rag.reranker import rerank


def ask(question: str, user_id: str):

    search_query = rewrite_query(question)

    matches = retrieve(
        search_query,
        user_id=user_id,
        top_k=20
    )

    reranked = rerank(
        search_query,
        matches,
        top_n=5
    )

    selected_matches = [
        item["match"]
        for item in reranked
    ]

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
        "search_query": search_query,
        "sources": sources
    }
