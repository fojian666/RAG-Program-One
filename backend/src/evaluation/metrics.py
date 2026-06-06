def precision_at_k(relevant: set[str], ranked_ids: list[str], k: int) -> float:
    if k <= 0:
        return 0.0
    top_k = ranked_ids[:k]
    if not top_k:
        return 0.0
    return len(relevant.intersection(top_k)) / len(top_k)


def recall_at_k(relevant: set[str], ranked_ids: list[str], k: int) -> float:
    if not relevant:
        return 0.0
    top_k = set(ranked_ids[:k])
    return len(relevant.intersection(top_k)) / len(relevant)

