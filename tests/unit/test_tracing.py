from opentelemetry import trace

from app.core.tracing import configure_tracing, get_tracer


def test_configure_tracing_sets_tracer_provider() -> None:
    configure_tracing()

    provider = trace.get_tracer_provider()

    assert provider is not None


def test_configure_tracing_is_idempotent() -> None:
    configure_tracing()
    first_provider = trace.get_tracer_provider()

    configure_tracing()
    second_provider = trace.get_tracer_provider()

    assert first_provider is second_provider


def test_get_tracer_returns_tracer() -> None:
    configure_tracing()

    tracer = get_tracer("test")

    assert tracer is not None
