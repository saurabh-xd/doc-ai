from embeddings import embed_text
from vector_store import index


def retrieve(query: str, top_k: int = 5):

    query_vector = embed_text(query)

    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    return results.matches