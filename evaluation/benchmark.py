from dataclasses import dataclass

from app.retrieval.base import Retriever
from evaluation.models import EvaluationDataset
from evaluation.retrieval_metrics import (
    hit_rate,
    mean_reciprocal_rank,
    precision_at_k,
    recall_at_k,
)


@dataclass(frozen=True, slots=True)
class RetrievalBenchmarkResult:
    configuration_name: str
    recall_at_k: float
    precision_at_k: float
    mrr: float
    hit_rate: float
    question_count: int


def run_retrieval_benchmark(
    configuration_name: str,
    retriever: Retriever,
    dataset: EvaluationDataset,
    top_k: int = 10,
) -> RetrievalBenchmarkResult:
    recalls: list[float] = []
    precisions: list[float] = []
    mrrs: list[float] = []
    hit_rates: list[float] = []

    for question in dataset.questions:
        retrieved = retriever.retrieve(
            question.question,
            top_k=top_k,
            filters=(
                {"collection": question.collection}
                if question.collection is not None
                else None
            ),
        )

        retrieved_sources = [str(chunk.document_id) for chunk in retrieved]
        expected_sources = list(question.expected_sources)

        recalls.append(recall_at_k(retrieved_sources, expected_sources))
        precisions.append(precision_at_k(retrieved_sources, expected_sources))
        mrrs.append(mean_reciprocal_rank(retrieved_sources, expected_sources))
        hit_rates.append(hit_rate(retrieved_sources, expected_sources))

    question_count = len(dataset.questions)

    return RetrievalBenchmarkResult(
        configuration_name=configuration_name,
        recall_at_k=sum(recalls) / question_count,
        precision_at_k=sum(precisions) / question_count,
        mrr=sum(mrrs) / question_count,
        hit_rate=sum(hit_rates) / question_count,
        question_count=question_count,
    )
