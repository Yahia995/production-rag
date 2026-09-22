import pytest

from evaluation.models import EvaluationDataset, EvaluationQuestion


def _question(question_id: str = "q1") -> EvaluationQuestion:
    return EvaluationQuestion(
        question_id=question_id,
        question="What is connection pooling?",
        ground_truth="Connection pooling reuses database connections.",
        expected_sources=("docs/pooling.md",),
    )


def test_evaluation_question_defaults() -> None:
    question = EvaluationQuestion(
        question_id="q1",
        question="What is asyncio?",
        ground_truth="A library for asynchronous programming.",
    )

    assert question.expected_sources == ()
    assert question.collection is None


def test_evaluation_dataset_holds_questions() -> None:
    dataset = EvaluationDataset(name="python-docs", questions=(_question(),))

    assert dataset.name == "python-docs"
    assert len(dataset.questions) == 1


def test_evaluation_dataset_rejects_empty_questions() -> None:
    with pytest.raises(ValueError, match="at least one question"):
        EvaluationDataset(name="empty", questions=())


def test_evaluation_dataset_rejects_duplicate_question_ids() -> None:
    with pytest.raises(ValueError, match="duplicate question_ids"):
        EvaluationDataset(
            name="python-docs",
            questions=(_question("q1"), _question("q1")),
        )
