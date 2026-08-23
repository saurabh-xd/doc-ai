def remove_duplicate_chunks(chunks):

    seen = set()
    unique = []

    for chunk in chunks:

        text = chunk["text"].strip()

        if text in seen:
            continue

        seen.add(text)
        unique.append(chunk)

    return unique

def build_context(
    reranked_results,
    min_score: float = 0.5
):
    selected = []

    for result in reranked_results:

        if result["score"] < min_score:
            continue

        match = result["match"]

        selected.append({
            "text": match.metadata["text"],
            "filename": match.metadata["filename"],
            "page_number": match.metadata["page_number"],
            "document_id": match.metadata["document_id"],
            "score": result["score"]
        })

    return remove_duplicate_chunks(selected)