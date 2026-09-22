from dataclasses import dataclass

from app.retrieval.base import RetrievedChunk

_INJECTION_MARKERS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard previous instructions",
    "reveal the system prompt",
    "reveal your system prompt",
    "you are now",
    "new instructions:",
)


@dataclass(frozen=True, slots=True)
class ContextChunk:
    chunk: RetrievedChunk
    citation_index: int


@dataclass(frozen=True, slots=True)
class AssembledContext:
    prompt_context: str
    chunks: tuple[ContextChunk, ...]


class ContextBuilder:
    """Deduplicates, orders, and assembles retrieved chunks into a prompt."""

    def __init__(self, max_chars: int = 8000) -> None:
        self.max_chars = max_chars

    def build(self, chunks: tuple[RetrievedChunk, ...]) -> AssembledContext:
        deduplicated = self._deduplicate(chunks)
        selected = self._select_within_budget(deduplicated)

        context_chunks = tuple(
            ContextChunk(chunk=chunk, citation_index=index)
            for index, chunk in enumerate(selected, start=1)
        )

        prompt_context = self._format_prompt(context_chunks)

        return AssembledContext(
            prompt_context=prompt_context,
            chunks=context_chunks,
        )

    @staticmethod
    def _deduplicate(
        chunks: tuple[RetrievedChunk, ...],
    ) -> tuple[RetrievedChunk, ...]:
        seen: set[str] = set()
        deduplicated: list[RetrievedChunk] = []

        for chunk in chunks:
            key = str(chunk.chunk_id)

            if key in seen:
                continue

            seen.add(key)
            deduplicated.append(chunk)

        return tuple(deduplicated)

    def _select_within_budget(
        self,
        chunks: tuple[RetrievedChunk, ...],
    ) -> tuple[RetrievedChunk, ...]:
        selected: list[RetrievedChunk] = []
        total_chars = 0

        for chunk in chunks:
            proposed_total = total_chars + len(chunk.content)

            if selected and proposed_total > self.max_chars:
                break

            selected.append(chunk)
            total_chars = proposed_total

        return tuple(selected)

    @staticmethod
    def _format_prompt(context_chunks: tuple[ContextChunk, ...]) -> str:
        sections = [
            f"[{context_chunk.citation_index}] "
            f"{ContextBuilder._neutralize(context_chunk.chunk.content)}"
            for context_chunk in context_chunks
        ]

        return "\n\n".join(sections)

    @staticmethod
    def _neutralize(content: str) -> str:
        lowered = content.lower()

        for marker in _INJECTION_MARKERS:
            if marker in lowered:
                return content.replace("\n", " ")

        return content
