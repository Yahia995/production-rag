from dataclasses import dataclass

from app.generation.base import LLMProvider
from app.query.transformer import ConversationTurn, QueryTransformer
from app.rag.citation import Citation, extract_citations
from app.rag.context import ContextBuilder
from app.reranking.base import Reranker
from app.retrieval.base import Retriever
from app.retrieval.fusion import reciprocal_rank_fusion

_ANSWER_SYSTEM_PROMPT = (
    "Answer the question using only the numbered context below. Cite sources "
    "inline using [n] markers matching the context. If the context does not "
    "contain enough information, say so explicitly instead of guessing."
)


@dataclass(frozen=True, slots=True)
class RagAnswer:
    text: str
    citations: tuple[Citation, ...]


class RagPipeline:
    """Coordinates query transformation, retrieval, reranking, and generation."""

    def __init__(
        self,
        dense_retriever: Retriever,
        sparse_retriever: Retriever,
        reranker: Reranker,
        llm_provider: LLMProvider,
        query_transformer: QueryTransformer | None = None,
        context_builder: ContextBuilder | None = None,
        retrieval_top_k: int = 10,
        rerank_top_n: int = 5,
    ) -> None:
        self.dense_retriever = dense_retriever
        self.sparse_retriever = sparse_retriever
        self.reranker = reranker
        self.llm_provider = llm_provider
        self.query_transformer = query_transformer
        self.context_builder = context_builder or ContextBuilder()
        self.retrieval_top_k = retrieval_top_k
        self.rerank_top_n = rerank_top_n

    def answer(
        self,
        question: str,
        history: tuple[ConversationTurn, ...] = (),
        filters: dict[str, str] | None = None,
    ) -> RagAnswer:
        search_query = self._transform_query(question, history)

        dense_results = self.dense_retriever.retrieve(
            search_query, top_k=self.retrieval_top_k, filters=filters
        )
        sparse_results = self.sparse_retriever.retrieve(
            search_query, top_k=self.retrieval_top_k, filters=filters
        )

        fused = reciprocal_rank_fusion([dense_results, sparse_results])
        reranked = self.reranker.rerank(search_query, fused, top_n=self.rerank_top_n)

        context = self.context_builder.build(reranked)

        prompt = self._build_prompt(question, context.prompt_context)
        generation = self.llm_provider.generate(
            prompt=prompt,
            system_prompt=_ANSWER_SYSTEM_PROMPT,
        )

        citations = extract_citations(generation.text, context.chunks)

        return RagAnswer(text=generation.text, citations=citations)

    def _transform_query(
        self,
        question: str,
        history: tuple[ConversationTurn, ...],
    ) -> str:
        if self.query_transformer is None:
            return question

        return self.query_transformer.transform(question, history)

    @staticmethod
    def _build_prompt(question: str, context: str) -> str:
        return f"Context:\n{context}\n\nQuestion: {question}"
