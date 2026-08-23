def recursive_chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap must be at least zero and smaller than chunk_size")

    text = text.strip()
    if not text:
        return []

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
    """Split text into bounded chunks, preferring natural break points.

    Each following chunk starts with up to ``overlap`` characters from the
    preceding one so information at chunk boundaries is not lost.
    """
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        if end < len(text):
            window = text[start:end]
            split_at = 0
            for separator in separators:
                if not separator:
                    continue
                position = window.rfind(separator)
                if position != -1:
                    split_at = max(split_at, position + len(separator))

            # Avoid producing a zero-length chunk when no separator occurs.
            if split_at:
                end = start + split_at

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break
        start = max(end - overlap, start + 1)

    return chunks
