def recall_at_k(retrieved_sources: list[str], expected_sources: list[str]) -> float:
    if not expected_sources:
        return 0.0

    retrieved_set = set(retrieved_sources)
    expected_set = set(expected_sources)

    hits = retrieved_set & expected_set

    return len(hits) / len(expected_set)


def precision_at_k(retrieved_sources: list[str], expected_sources: list[str]) -> float:
    if not retrieved_sources:
        return 0.0

    retrieved_set = set(retrieved_sources)
    expected_set = set(expected_sources)

    hits = retrieved_set & expected_set

    return len(hits) / len(retrieved_sources)


def mean_reciprocal_rank(retrieved_sources: list[str], expected_sources: list[str]) -> float:
    expected_set = set(expected_sources)

    for rank, source in enumerate(retrieved_sources, start=1):
        if source in expected_set:
            return 1.0 / rank

    return 0.0


def hit_rate(retrieved_sources: list[str], expected_sources: list[str]) -> float:
    expected_set = set(expected_sources)
    retrieved_set = set(retrieved_sources)

    return 1.0 if retrieved_set & expected_set else 0.0
