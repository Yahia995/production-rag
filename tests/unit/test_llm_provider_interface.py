import pytest

from app.generation.base import GenerationResult, LLMProvider


def test_llm_provider_is_abstract() -> None:
    with pytest.raises(TypeError):
        LLMProvider()  # type: ignore[abstract]


def test_llm_provider_requires_generate_implementation() -> None:
    class IncompleteProvider(LLMProvider):
        pass

    with pytest.raises(TypeError):
        IncompleteProvider()  # type: ignore[abstract]


def test_llm_provider_implementation_can_be_used() -> None:
    class TestProvider(LLMProvider):
        def generate(
            self,
            prompt: str,
            system_prompt: str | None = None,
        ) -> GenerationResult:
            return GenerationResult(text="answer", model="test-model")

    provider = TestProvider()
    result = provider.generate("question")

    assert isinstance(provider, LLMProvider)
    assert result.text == "answer"
    assert result.model == "test-model"


def test_generation_result_is_immutable() -> None:
    result = GenerationResult(text="answer", model="test-model")

    with pytest.raises(AttributeError):
        result.text = "changed"  # type: ignore[misc]


def test_generation_result_defaults() -> None:
    result = GenerationResult(text="answer", model="test-model")

    assert result.prompt_tokens is None
    assert result.completion_tokens is None
