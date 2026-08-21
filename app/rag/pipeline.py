from app.rag.retriever import retrieve
from app.rag.generator import generate_answer
from app.rag.query_rewriter import rewrite_query
from app.rag.reranker import rerank
from app.rag.context import build_context


def ask(question: str, user_id: str):

    search_query = rewrite_query(question)
     
      # 2. Retrieve broad candidate set
    matches = retrieve(
        search_query,
        user_id=user_id,
        top_k=20
    )
      
       # 3. Rerank
    reranked = rerank(
        search_query,
        matches,
        top_n=5
    )

      # 4. Build final context
    context_chunks = build_context(reranked)

  

    answer = generate_answer(
        question,
        context_chunks
    )

   

    return {
        "answer": answer,
        "sources": context_chunks
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

    reranked = rerank(
        search_query,
        matches,
        top_n=5
    )

    context_chunks = build_context(reranked)

    return context_chunks
