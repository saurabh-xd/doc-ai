from retriever import retrieve
from generator import generate_answer


def ask(question: str):

    matches = retrieve(question, top_k=5)

    answer = generate_answer(
        question,
        matches
    )

    sources = [
        {
            "page": match.metadata["page_number"],
            "text": match.metadata["text"],
            "score": match.score
        }
        for match in matches
    ]

    return {
        "answer": answer,
        "sources": sources
    }