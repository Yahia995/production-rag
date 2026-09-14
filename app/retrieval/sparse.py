import re
from uuid import UUID

from rank_bm25 import BM25Okapi

from app.retrieval.base import RetrievedChunk, Retriever

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_.]+")


class SparseRetriever(Retriever):
    """BM25-based lexical retriever."""

    def __init__(self) -> None:
        self._chunks: list[RetrievedChunk] = []
        self._document_ids: list[UUID] = []
        self._tokenized_corpus: list[list[str]] = []
        self._bm25: BM25Okapi | None = None
        self._filters: list[dict[str, str] | None] = []

    def index(
        self,
        chunk_id: UUID,
        document_id: UUID,
        content: str,
        page_number: int | None = None,
        section: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None:
        self._chunks.append(
            RetrievedChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                content=content,
                score=0.0,
                page_number=page_number,
                section=section,
            )
        )
        self._document_ids.append(document_id)
        self._tokenized_corpus.append(self._tokenize(content))
        self._filters.append(metadata)
        self._bm25 = None

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: dict[str, str] | None = None,
    ) -> tuple[RetrievedChunk, ...]:
        if not self._tokenized_corpus:
            return ()

        if self._bm25 is None:
            self._bm25 = BM25Okapi(self._tokenized_corpus)

        query_tokens = set(self._tokenize(query))
        scores = self._bm25.get_scores(list(query_tokens))

        candidates = [
            (index, score)
            for index, score in enumerate(scores)
            if self._matches_filters(index, filters)
            and query_tokens & set(self._tokenized_corpus[index])
        ]

        candidates.sort(key=lambda pair: pair[1], reverse=True)

        results = []

        for index, score in candidates[:top_k]:
            chunk = self._chunks[index]
            results.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    score=float(score),
                    page_number=chunk.page_number,
                    section=chunk.section,
                )
            )

        return tuple(results)
    
    def _matches_filters(
        self,
        index: int,
        filters: dict[str, str] | None,
    ) -> bool:
        if not filters:
            return True

        chunk_metadata = self._filters[index] or {}

        return all(
            chunk_metadata.get(key) == value
            for key, value in filters.items()
        )

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [token.lower() for token in _TOKEN_PATTERN.findall(text)]
