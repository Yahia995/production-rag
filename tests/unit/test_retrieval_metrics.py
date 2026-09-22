from evaluation.retrieval_metrics import (
    hit_rate,
    mean_reciprocal_rank,
    precision_at_k,
    recall_at_k,
)


def test_recall_at_k_full_match() -> None:
    assert recall_at_k(["a", "b"], ["a", "b"]) == 1.0


def test_recall_at_k_partial_match() -> None:
    assert recall_at_k(["a"], ["a", "b"]) == 0.5


def test_recall_at_k_no_expected_sources() -> None:
    assert recall_at_k(["a"], []) == 0.0


def test_precision_at_k_full_precision() -> None:
    assert precision_at_k(["a", "b"], ["a", "b"]) == 1.0


def test_precision_at_k_partial_precision() -> None:
    assert precision_at_k(["a", "b", "c"], ["a"]) == 1 / 3


def test_precision_at_k_no_retrieved_results() -> None:
    assert precision_at_k([], ["a"]) == 0.0


def test_mrr_first_position() -> None:
    assert mean_reciprocal_rank(["a", "b"], ["a"]) == 1.0


def test_mrr_second_position() -> None:
    assert mean_reciprocal_rank(["b", "a"], ["a"]) == 0.5


def test_mrr_no_match() -> None:
    assert mean_reciprocal_rank(["b", "c"], ["a"]) == 0.0


def test_hit_rate_with_match() -> None:
    assert hit_rate(["a", "b"], ["b"]) == 1.0


def test_hit_rate_without_match() -> None:
    assert hit_rate(["a"], ["b"]) == 0.0
