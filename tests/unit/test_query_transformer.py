from unittest.mock import MagicMock

from app.generation.base import GenerationResult
from app.query.transformer import ConversationTurn, QueryTransformer


def test_transform_returns_question_unchanged_without_history() -> None:
    llm_provider = MagicMock()

    transformer = QueryTransformer(llm_provider)
    result = transformer.transform("What is connection pooling?")

    assert result == "What is connection pooling?"
    llm_provider.generate.assert_not_called()


def test_transform_rewrites_question_using_history() -> None:
    llm_provider = MagicMock()
    llm_provider.generate.return_value = GenerationResult(
        text="How do I configure connection pooling?",
        model="test-model",
    )

    history = (
        ConversationTurn(role="user", content="What is connection pooling?"),
        ConversationTurn(role="assistant", content="It reuses connections."),
    )

    transformer = QueryTransformer(llm_provider)
    result = transformer.transform("How do I configure it?", history)

    assert result == "How do I configure connection pooling?"
    llm_provider.generate.assert_called_once()


def test_transform_includes_history_and_question_in_prompt() -> None:
    llm_provider = MagicMock()
    llm_provider.generate.return_value = GenerationResult(
        text="rewritten query",
        model="test-model",
    )

    history = (ConversationTurn(role="user", content="What is asyncio?"),)

    transformer = QueryTransformer(llm_provider)
    transformer.transform("How does it work?", history)

    _, kwargs = llm_provider.generate.call_args
    assert "What is asyncio?" in kwargs["prompt"]
    assert "How does it work?" in kwargs["prompt"]


def test_transform_falls_back_to_original_question_on_empty_response() -> None:
    llm_provider = MagicMock()
    llm_provider.generate.return_value = GenerationResult(text="  ", model="test-model")

    history = (ConversationTurn(role="user", content="What is asyncio?"),)

    transformer = QueryTransformer(llm_provider)
    result = transformer.transform("How does it work?", history)

    assert result == "How does it work?"
