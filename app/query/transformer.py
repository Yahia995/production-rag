from dataclasses import dataclass

from app.generation.base import LLMProvider

_REWRITE_SYSTEM_PROMPT = (
    "Rewrite the user's latest question into a standalone search query using "
    "the conversation history for context. Respond with only the rewritten "
    "query and nothing else."
)


@dataclass(frozen=True, slots=True)
class ConversationTurn:
    role: str
    content: str


class QueryTransformer:
    """Rewrites a follow-up question into a standalone search query."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm_provider = llm_provider

    def transform(
        self,
        question: str,
        history: tuple[ConversationTurn, ...] = (),
    ) -> str:
        if not history:
            return question

        prompt = self._build_prompt(question, history)
        result = self.llm_provider.generate(
            prompt=prompt,
            system_prompt=_REWRITE_SYSTEM_PROMPT,
        )

        rewritten = result.text.strip()

        return rewritten or question

    @staticmethod
    def _build_prompt(
        question: str,
        history: tuple[ConversationTurn, ...],
    ) -> str:
        turns = "\n".join(f"{turn.role}: {turn.content}" for turn in history)

        return f"{turns}\nuser: {question}"
