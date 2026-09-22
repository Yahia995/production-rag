from prometheus_client import Counter, Histogram

rag_requests_total = Counter(
    "rag_requests_total",
    "Total number of RAG chat requests",
)

rag_request_latency_seconds = Histogram(
    "rag_request_latency_seconds",
    "End-to-end RAG request latency",
)

retrieval_latency_seconds = Histogram(
    "retrieval_latency_seconds",
    "Retrieval stage latency",
)

reranker_latency_seconds = Histogram(
    "reranker_latency_seconds",
    "Reranking stage latency",
)

llm_latency_seconds = Histogram(
    "llm_latency_seconds",
    "LLM generation latency",
)

retrieval_results_count = Histogram(
    "retrieval_results_count",
    "Number of candidates returned by retrieval",
)

ingestion_jobs_total = Counter(
    "ingestion_jobs_total",
    "Total number of ingestion jobs processed",
)

ingestion_failures_total = Counter(
    "ingestion_failures_total",
    "Total number of failed ingestion jobs",
)
