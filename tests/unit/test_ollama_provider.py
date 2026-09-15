from unittest.mock import MagicMock

from app.generation.ollama import OllamaProvider


def _client_with_response(json_body: dict) -> MagicMock:
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = json_body
    response.raise_for_status.return_value = None
    client.post.return_value = response

    return client


def test_generate_sends_prompt_and_model() -> None:
    client = _client_with_response({"response": "hello"})

    provider = OllamaProvider(model="llama3", client=client)
    provider.generate("what is asyncio?")

    _, kwargs = client.post.call_args
    assert kwargs["json"]["model"] == "llama3"
    assert kwargs["json"]["prompt"] == "what is asyncio?"
    assert kwargs["json"]["stream"] is False


def test_generate_includes_system_prompt_when_given() -> None:
    client = _client_with_response({"response": "hello"})

    provider = OllamaProvider(model="llama3", client=client)
    provider.generate("question", system_prompt="be concise")

    _, kwargs = client.post.call_args
    assert kwargs["json"]["system"] == "be concise"


def test_generate_omits_system_prompt_when_not_given() -> None:
    client = _client_with_response({"response": "hello"})

    provider = OllamaProvider(model="llama3", client=client)
    provider.generate("question")

    _, kwargs = client.post.call_args
    assert "system" not in kwargs["json"]


def test_generate_returns_generation_result() -> None:
    client = _client_with_response(
        {
            "response": "asyncio.TaskGroup manages tasks.",
            "prompt_eval_count": 12,
            "eval_count": 8,
        }
    )

    provider = OllamaProvider(model="llama3", client=client)
    result = provider.generate("what is TaskGroup?")

    assert result.text == "asyncio.TaskGroup manages tasks."
    assert result.model == "llama3"
    assert result.prompt_tokens == 12
    assert result.completion_tokens == 8


def test_generate_raises_on_http_error() -> None:
    client = MagicMock()
    response = MagicMock()
    response.raise_for_status.side_effect = httpx_error()
    client.post.return_value = response

    provider = OllamaProvider(model="llama3", client=client)

    import pytest

    with pytest.raises(Exception):
        provider.generate("question")


def httpx_error() -> Exception:
    import httpx

    return httpx.HTTPStatusError(
        "error",
        request=MagicMock(),
        response=MagicMock(),
    )
