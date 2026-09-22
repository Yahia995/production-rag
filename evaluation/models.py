from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class EvaluationQuestion:
    question_id: str
    question: str
    ground_truth: str
    expected_sources: tuple[str, ...] = field(default_factory=tuple)
    collection: str | None = None


@dataclass(frozen=True, slots=True)
class EvaluationDataset:
    name: str
    questions: tuple[EvaluationQuestion, ...]

    def __post_init__(self) -> None:
        if not self.questions:
            raise ValueError("EvaluationDataset must contain at least one question")

        ids = [question.question_id for question in self.questions]

        if len(ids) != len(set(ids)):
            raise ValueError("EvaluationDataset contains duplicate question_ids")
