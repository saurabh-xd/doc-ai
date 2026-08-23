from app.rag.retrieval.embeddings import embed_texts
from app.rag.retrieval.vector_store import get_index


def retrieve(query: str, user_id: str, top_k: int = 5):

    query_vector = embed_texts([query])[0]

    results = get_index().query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        filter={
            "user_id": {
                "$eq": user_id
            }
        }
    )

    return results.matches
