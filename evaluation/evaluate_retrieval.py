import json
from pathlib import Path
import sys

# Allow importing modules from app/rag
ROOT_DIR = Path(__file__).resolve().parents[1]
RAG_DIR = ROOT_DIR / "app" / "rag"

sys.path.append(str(RAG_DIR))

from retriever import retrieve


QUESTIONS_FILE = Path(__file__).parent / "questions.json"

USER_ID = "test-user"
TOP_K = 5


def evaluate_question(question_data):

    question = question_data["question"]
    expected_pages = set(question_data["expected_pages"])

    matches = retrieve(
        query=question,
        user_id=USER_ID,
        top_k=TOP_K
    )

    retrieved_pages = [
        match.metadata["page_number"]
        for match in matches
    ]

    hit = any(
        page in expected_pages
        for page in retrieved_pages
    )

    return {
        "question": question,
        "expected_pages": list(expected_pages),
        "retrieved_pages": retrieved_pages,
        "hit": hit
    }


def main():

    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        questions = json.load(file)

    results = []

    for question_data in questions:

        result = evaluate_question(question_data)

        results.append(result)

        print("\nQuestion:")
        print(result["question"])

        print("Expected pages:", result["expected_pages"])
        print("Retrieved pages:", result["retrieved_pages"])
        print("Hit:", result["hit"])

    successful = sum(
        result["hit"]
        for result in results
    )

    total = len(results)

    recall_at_k = successful / total if total else 0

    print("\n====================")
    print(f"Recall@{TOP_K}: {recall_at_k:.2%}")
    print("====================")


if __name__ == "__main__":
    main()

def evaluate_with_reranking(question_data):

    question = question_data["question"]
    expected_pages = set(question_data["expected_pages"])

    matches = retrieve(
        query=question,
        user_id=USER_ID,
        top_k=20
    )

    reranked = rerank(
        question,
        matches,
        top_n=5
    )

    retrieved_pages = [
        item["match"].metadata["page_number"]
        for item in reranked
    ]

    hit = any(
        page in expected_pages
        for page in retrieved_pages
    )

    return hit    