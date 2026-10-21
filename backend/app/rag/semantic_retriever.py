
from functools import lru_cache

from sentence_transformers import SentenceTransformer, util


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Load the semantic model once, when it is first needed."""
    return SentenceTransformer(
        "all-MiniLM-L6-v2",
        device="cpu",
    )


def retrieve_semantic_evidence(
    query: str,
    chunks: list[dict],
    top_k: int = 3,
) -> list[dict]:
    """
    Retrieve resume chunks based on semantic similarity.
    """

    if top_k <= 0 or not query.strip() or not chunks:
        return []

    # Ignore empty chunks.
    valid_chunks = [
        chunk for chunk in chunks
        if chunk.get("text", "").strip()
    ]

    if not valid_chunks:
        return []

    # Load the model only when semantic retrieval is needed.
    model = get_model()

    # Convert the query and resume passages into vectors.
    query_embedding = model.encode(
        query,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )

    chunk_texts = [chunk["text"] for chunk in valid_chunks]

    chunk_embeddings = model.encode(
        chunk_texts,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )

    # Compare the query vector with every chunk vector.
    similarities = util.cos_sim(
        query_embedding,
        chunk_embeddings,
    )[0]

    ranked_indices = similarities.argsort(
        descending=True
    )[:top_k]

    results = []

    for index in ranked_indices:
        position = int(index.item())
        score = float(similarities[position].item())
        chunk = valid_chunks[position]

        results.append({
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "relevance_score": round(score, 4),
            "retrieval_method": "semantic",
        })

    return results
