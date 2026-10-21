
def chunk_text(
    text: str,
    chunk_size: int = 100,
    overlap: int = 20,
) -> list[dict]:
    """
    Split text into overlapping chunks of words.

    chunk_size: maximum number of words per chunk.
    overlap: number of words shared between adjacent chunks.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size."
        )

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]

        chunks.append({
            "chunk_id": len(chunks),
            "text": " ".join(chunk_words),
        })

        if end == len(words):
            break

        start = end - overlap

    return chunks
