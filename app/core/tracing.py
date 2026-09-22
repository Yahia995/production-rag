from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from app.core.config import get_settings

_tracer_provider: TracerProvider | None = None


def configure_tracing() -> None:
    global _tracer_provider

    if _tracer_provider is not None:
        return

    settings = get_settings()

    resource = Resource.create({"service.name": settings.app_name})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    _tracer_provider = provider


def get_tracer(name: str) -> trace.Tracer:
    return trace.get_tracer(name)
