from prometheus_client import Counter, Gauge, Histogram


# -----------------------------
# HTTP Requests
# -----------------------------

HTTP_REQUESTS = Counter(
    "chatbot_http_requests_total",
    "Total HTTP requests.",
    ["method", "endpoint"],
)


HTTP_REQUEST_LATENCY = Histogram(
    "chatbot_http_request_latency_seconds",
    "HTTP request latency in seconds.",
    ["method", "endpoint"],
)


# -----------------------------
# Chat Requests
# -----------------------------

CHAT_REQUESTS = Counter(
    "chatbot_chat_requests_total",
    "Total chat requests.",
)


CHAT_ERRORS = Counter(
    "chatbot_chat_errors_total",
    "Total chat errors.",
)


CHAT_RESPONSE_TIME = Histogram(
    "chatbot_response_time_seconds",
    "Chat response generation time in seconds.",
    buckets=(0.5, 1, 2, 5, 10, 20, 30, 60, 120),
)


# -----------------------------
# Uploads
# -----------------------------

PDF_UPLOADS = Counter(
    "chatbot_pdf_uploads_total",
    "Total successfully indexed PDF uploads.",
)


PDF_UPLOAD_FAILURES = Counter(
    "chatbot_pdf_upload_failures_total",
    "Total failed PDF upload/indexing attempts.",
)


# -----------------------------
# GitHub Repositories
# -----------------------------

GITHUB_REPOS = Counter(
    "chatbot_github_repositories_total",
    "Total successfully indexed GitHub repositories.",
)


GITHUB_REPO_FAILURES = Counter(
    "chatbot_github_repository_failures_total",
    "Total failed GitHub repository indexing attempts.",
)


# -----------------------------
# Redis Cache
# -----------------------------

CACHE_HITS = Counter(
    "chatbot_cache_hits_total",
    "Redis cache hits.",
)


CACHE_MISSES = Counter(
    "chatbot_cache_misses_total",
    "Redis cache misses.",
)


# -----------------------------
# RAG / Retrieval
# -----------------------------

RAG_RETRIEVALS = Counter(
    "chatbot_rag_retrievals_total",
    "Total RAG retrieval calls.",
)


RAG_RETRIEVAL_FAILURES = Counter(
    "chatbot_rag_retrieval_failures_total",
    "Total failed RAG retrieval calls.",
)


RAG_RETRIEVED_DOCUMENTS = Histogram(
    "chatbot_rag_retrieved_documents",
    "Number of documents retrieved per RAG query.",
    buckets=(0, 1, 2, 3, 5, 8, 10, 15, 20),
)


# -----------------------------
# Index State
# -----------------------------

PDF_CHUNKS_TOTAL = Gauge(
    "chatbot_pdf_chunks_total",
    "Current number of stored PDF chunks.",
)


GITHUB_CHUNKS_TOTAL = Gauge(
    "chatbot_github_chunks_total",
    "Current number of stored GitHub chunks.",
)


def update_pdf_chunks_total(value: int) -> None:
    PDF_CHUNKS_TOTAL.set(max(0, int(value or 0)))


def update_github_chunks_total(value: int) -> None:
    GITHUB_CHUNKS_TOTAL.set(max(0, int(value or 0)))