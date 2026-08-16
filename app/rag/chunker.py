def recursive_chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
):
    separators = [
        "\n\n",   # paragraph
        "\n",     # line
        ". ",     # sentence
        " ",      # word
        ""        # character
    ]

    return _split_text(
        text,
        separators,
        chunk_size,
        overlap
    )


def _split_text(
    text: str,
    separators: list[str],
    chunk_size: int,
    overlap: int
):
    if len(text) <= chunk_size:
        return [text]

    separator = separators[0]

    if separator == "":
        pieces = list(text)
    else:
        pieces = text.split(separator)

    chunks = []
    current = ""

    for piece in pieces:

        candidate = (
            current + separator + piece
            if current
            else piece
        )

        if len(candidate) <= chunk_size:
            current = candidate

        else:
            if current:
                chunks.append(current)

            current = piece

    if current:
        chunks.append(current)

    return chunks