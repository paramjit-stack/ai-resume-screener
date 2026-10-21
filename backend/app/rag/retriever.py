
import re


def tokenize(text: str) -> set[str]:
    """Convert text into a set of lowercase words."""
    return set(re.findall(r"\b[a-zA-Z0-9+#.]+\b", text.lower()))


def retrieve_evidence(
    query: str,
    chunks: list[dict],
    top_k: int = 3,
) -> list[dict]:
    """Return the most relevant chunks using keyword overlap."""

    if top_k <= 0:
        return []

    query_words = tokenize(query)

    if not query_words:
        return []

    results = []

    for chunk in chunks:
        chunk_words = tokenize(chunk["text"])
        matched_words = sorted(query_words & chunk_words)

        if matched_words:
            results.append({
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "matched_words": matched_words,
                "relevance_score": round(
                    len(matched_words) / len(query_words), 2
                ),
            })

    results.sort(
        key=lambda item: (
            item["relevance_score"],
            -item["chunk_id"],
        ),
        reverse=True,
    )

    return results[:top_k]
