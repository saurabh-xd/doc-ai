from app.rag.retriever import retrieve
from app.rag.generator import generate_answer
from app.rag.query_rewriter import rewrite_query
from app.rag.reranker import rerank
from app.rag.context import build_context


def ask(question: str, user_id: str):
    context_chunks = prepare_rag_context(question, user_id)

    answer = generate_answer(
        question,
        context_chunks,
    )

   

    return {
        "answer": answer,
        "sources": context_chunks,
    }

def prepare_rag_context(
    question: str,
    user_id: str
):

    search_query = rewrite_query(question)

    matches = retrieve(
        search_query,
        user_id=user_id,
        top_k=20
    )

    if not matches:
        return []

    reranked = rerank(
        search_query,
        matches,
        top_n=5
    )

    context_chunks = build_context(reranked)

    return context_chunks
