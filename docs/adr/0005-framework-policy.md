# ADR 0005: Keep the core RAG pipeline framework-light

## Decision

The core RAG pipeline will not depend on a large RAG framework to manage the
main application flow.

We can still use focused libraries when they solve a specific problem, but the
important parts of the pipeline should remain in our own application code.

The main flow should be easy to follow:

```text
Query
  ↓
Query Transformation
  ↓
Retrieval
  ↓
Fusion
  ↓
Reranking
  ↓
Context Assembly
  ↓
Generation
  ↓
Citations
```

## Why

One of the goals of this project is to show that I understand what is actually
happening inside a production RAG system.

If a framework hides most of the retrieval and generation logic behind its own
abstractions, it becomes harder to understand where latency comes from, test
individual stages, or change one part without affecting another.

Keeping the main pipeline explicit also makes experiments easier.

For example, if I want to compare two fusion strategies, I should be able to
change the fusion component without having to work around a framework's
execution model.

## What we can still use

This does not mean writing everything from scratch.

Specialized libraries are still useful for things like:

* PDF parsing
* HTML parsing
* tokenization
* BM25
* embeddings
* reranking
* database access
* OpenTelemetry
* metrics
* LLM clients

The distinction is simple:

**Use libraries for specific problems, but keep ownership of the application's
main architecture.**

## Consequences

There will be some additional application code compared with using a
full-stack RAG framework.

In return, the important parts of the system remain visible and easier to
reason about.

It should also be easier to benchmark individual stages and replace components
when the evaluation shows that a different approach works better.

If a framework becomes useful later, we can introduce it for a specific reason
rather than making it the foundation of the project by default.
