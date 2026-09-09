# ADR 0002: Use Qdrant for vector search

## Decision

Use Qdrant as the vector database for dense retrieval.

PostgreSQL remains responsible for application state, while Qdrant handles
vector search and the metadata needed to perform retrieval.

## Why

The project needs more than a local vector index.

We want a real vector database that gives us:

- persistent collections
- metadata filtering
- similarity search
- a service that can run independently from the API
- a reasonable path from local development to a deployed setup

Qdrant fits that role without adding unnecessary infrastructure around the
retrieval layer.

It also gives us a clear separation between application data and vector
search data.

## Why not FAISS?

FAISS is useful for building a fast local semantic-search prototype, but that
is not the direction of this project.

The previous work this project is meant to evolve from already covers the
basic vector-search pattern. Using Qdrant lets this project demonstrate a
more production-oriented retrieval setup.

## Consequences

The local development environment will run Qdrant as a separate service.

The retrieval code should interact with Qdrant through our own retriever
interfaces rather than spreading Qdrant-specific calls throughout the
application.

If we eventually need to replace Qdrant, the rest of the RAG pipeline should
not need to know about that decision.
