from unittest.mock import MagicMock

from app.retrieval.base import RetrievedChunk
from evaluation.benchmark import run_retrieval_benchmark
from evaluation.models import EvaluationDataset, EvaluationQuestion


def _chunk(document_id: str) -> RetrievedChunk:
    from uuid import UUID, uuid4

    return RetrievedChunk(
        chunk_id=uuid4(),
        document_id=UUID(document_id),
        content="example",
        score=1.0,
    )


def test_benchmark_computes_perfect_scores_for_full_match() -> None:
    document_id = "12345678-1234-5678-1234-567812345678"

    retriever = MagicMock()
    retriever.retrieve.return_value = (_chunk(document_id),)

    dataset = EvaluationDataset(
        name="test",
        questions=(
            EvaluationQuestion(
                question_id="q1",
                question="What is X?",
                ground_truth="X is Y.",
                expected_sources=(document_id,),
            ),
        ),
    )

    result = run_retrieval_benchmark("dense", retriever, dataset)

    assert result.recall_at_k == 1.0
    assert result.hit_rate == 1.0
    assert result.mrr == 1.0
    assert result.question_count == 1


def test_benchmark_computes_zero_scores_for_no_match() -> None:
    retriever = MagicMock()
    retriever.retrieve.return_value = ()

    dataset = EvaluationDataset(
        name="test",
        questions=(
            EvaluationQuestion(
                question_id="q1",
                question="What is X?",
                ground_truth="X is Y.",
                expected_sources=("12345678-1234-5678-1234-567812345678",),
            ),
        ),
    )

    result = run_retrieval_benchmark("dense", retriever, dataset)

    assert result.recall_at_k == 0.0
    assert result.hit_rate == 0.0


def test_benchmark_passes_collection_filter() -> None:
    retriever = MagicMock()
    retriever.retrieve.return_value = ()

    dataset = EvaluationDataset(
        name="test",
        questions=(
            EvaluationQuestion(
                question_id="q1",
                question="What is X?",
                ground_truth="X is Y.",
                collection="python",
            ),
        ),
    )

    run_retrieval_benchmark("dense", retriever, dataset)

    _, kwargs = retriever.retrieve.call_args
    assert kwargs["filters"] == {"collection": "python"}


def test_benchmark_averages_across_multiple_questions() -> None:
    match_id = "12345678-1234-5678-1234-567812345678"
    no_match_id = "87654321-4321-8765-4321-876543218765"

    retriever = MagicMock()
    retriever.retrieve.side_effect = [
        (_chunk(match_id),),
        (),
    ]

    dataset = EvaluationDataset(
        name="test",
        questions=(
            EvaluationQuestion(
                question_id="q1",
                question="What is X?",
                ground_truth="X is Y.",
                expected_sources=(match_id,),
            ),
            EvaluationQuestion(
                question_id="q2",
                question="What is Z?",
                ground_truth="Z is W.",
                expected_sources=(no_match_id,),
            ),
        ),
    )

    result = run_retrieval_benchmark("dense", retriever, dataset)

    assert result.hit_rate == 0.5
    assert result.question_count == 2
