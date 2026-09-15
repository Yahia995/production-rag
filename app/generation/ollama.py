import httpx

from app.generation.base import GenerationResult, LLMProvider


class OllamaProvider(LLMProvider):
    """LLM provider backed by a local Ollama server."""

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434",
        client: httpx.Client | None = None,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(base_url=self.base_url, timeout=120.0)

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> GenerationResult:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        if system_prompt is not None:
            payload["system"] = system_prompt

        response = self.client.post("/api/generate", json=payload)
        response.raise_for_status()

        data = response.json()

        return GenerationResult(
            text=data["response"],
            model=self.model,
            prompt_tokens=data.get("prompt_eval_count"),
            completion_tokens=data.get("eval_count"),
        )
