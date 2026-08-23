import os
import cohere
from dotenv import load_dotenv

load_dotenv()

client = cohere.ClientV2(
    api_key=os.getenv("COHERE_API_KEY")
)


def rerank(
    query: str,
    matches,
    top_n: int = 5
):

    documents = [
        match.metadata["text"]
        for match in matches
    ]

    response = client.rerank(
        model="rerank-v4.0-pro",
        query=query,
        documents=documents,
        top_n=top_n
    )

    reranked = []

    for result in response.results:

        match = matches[result.index]

        reranked.append({
            "match": match,
            "score": result.relevance_score
        })

    return reranked