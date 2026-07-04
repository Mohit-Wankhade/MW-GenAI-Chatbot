from prometheus_client import Counter, Histogram

# -----------------------------
# HTTP Requests
# -----------------------------

HTTP_REQUESTS = Counter(
    "chatbot_http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint"]
)

# -----------------------------
# Chat Requests
# -----------------------------

CHAT_REQUESTS = Counter(
    "chatbot_chat_requests_total",
    "Total Chat Requests"
)

# -----------------------------
# Uploads
# -----------------------------

PDF_UPLOADS = Counter(
    "chatbot_pdf_uploads_total",
    "Total PDF Uploads"
)

# -----------------------------
# GitHub Repositories
# -----------------------------

GITHUB_REPOS = Counter(
    "chatbot_github_repositories_total",
    "Indexed GitHub Repositories"
)

# -----------------------------
# Redis
# -----------------------------

CACHE_HITS = Counter(
    "chatbot_cache_hits_total",
    "Redis Cache Hits"
)

CACHE_MISSES = Counter(
    "chatbot_cache_misses_total",
    "Redis Cache Misses"
)

# -----------------------------
# Chat Latency
# -----------------------------

CHAT_RESPONSE_TIME = Histogram(
    "chatbot_response_time_seconds",
    "Chat Response Time"
)