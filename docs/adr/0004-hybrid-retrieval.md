# ADR 0004: Use dense and sparse retrieval together

## Decision

The first retrieval implementation will use two retrieval methods:

* dense vector retrieval
* BM25 sparse retrieval

Their results will be combined using Reciprocal Rank Fusion (RRF) before being passed to the reranker.

```text
Query
 ├──→ Dense retrieval ──┐
 │                      ├──→ RRF ──→ Reranker
 └──→ BM25 ─────────────┘
```

## Why

Technical documentation has two different kinds of useful matches.

Sometimes the meaning of the question matters more than the exact words. Dense
retrieval is good at finding that kind of match.

But technical questions also contain exact names, identifiers, configuration
options, and API terms.

For example:

```text
asyncio.TaskGroup
HTTPException
max_connections
PYTHONPATH
```

In those cases, lexical matching can be very useful.

Using both approaches gives us two different retrieval signals instead of
depending entirely on semantic similarity.

## Why RRF?

The dense and sparse retrievers produce ranked lists, but their scores do not
necessarily mean the same thing.

RRF lets us combine the rankings without having to make those scores directly
comparable.

It is also simple enough to understand and experiment with.

This is a starting point, not a claim that RRF is the best possible fusion
method.

## Evaluation

We will measure whether hybrid retrieval actually helps.

The main comparison will be along the lines of:

```text
Dense
   vs
Hybrid
   vs
Hybrid + Reranking
```

Retrieval metrics such as Recall@K, Precision@K, MRR, and Hit Rate will be used
to compare the approaches.

If the extra complexity of hybrid retrieval does not produce a meaningful
improvement, the evaluation should make that visible.

## Consequences

There are now two retrieval operations instead of one.

That adds some complexity and potentially some latency.

In return, we get a retrieval pipeline that can handle both semantic similarity
and exact technical terminology.

The fusion stage will remain separate from the individual retrievers so that we
can test another fusion strategy later without changing the rest of the
retrieval pipeline.
