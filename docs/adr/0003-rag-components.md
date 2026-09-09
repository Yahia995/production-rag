# ADR 0003: Keep RAG components behind interfaces

## Decision

The main RAG components will have small interfaces that separate the application
logic from specific models and infrastructure.

The important boundaries are:

```text
EmbeddingProvider
Retriever
Reranker
LLMProvider
```

Concrete implementations will sit behind these interfaces.

For example:

```text
LLMProvider
├── OllamaProvider
└── OpenAICompatibleProvider
```

And for retrieval:

```text
Retriever
├── DenseRetriever
└── SparseRetriever
```

## Why

Models and infrastructure will probably change as the project develops.

The embedding model might change because another model gives better retrieval
results. The reranker might change because we need better latency. The LLM
might change because another model performs better on the evaluation dataset.

Those changes should not force us to rewrite the rest of the application.

The interfaces also make testing easier. Individual parts of the pipeline can
be tested without having to start every external service.

## What this does not mean

This is not an attempt to build a complicated plugin system.

The interfaces should stay small and should represent things the application
actually needs.

If an abstraction makes the code harder to understand without giving us a
real benefit, we should not add it.

## Consequences

Infrastructure-specific code stays inside its own implementation.

The query pipeline depends on the interfaces instead of directly creating
embedding models, rerankers, or LLM clients.

This should make it easier to experiment with different models and
implementations later without changing the core RAG flow.
