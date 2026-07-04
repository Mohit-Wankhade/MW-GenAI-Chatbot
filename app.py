from contextlib import asynccontextmanager
from time import perf_counter
from typing import Any, Optional

from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, ConfigDict, Field

from auth.auth_dependencies import get_current_user
from config import (
    APP_ENV,
    APP_NAME,
    APP_VERSION,
    CORS_ORIGINS,
    STREAM_MEDIA_TYPE,
    ensure_directories,
)
from routes.conversation import router as conversation_router
from routes.github import router as github_router
from routes.upload import router as upload_router
from routes.user import router as user_router
from services.chat_service import process_chat_stream
from utils.logger import logger


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(
        ...,
        min_length=1,
        max_length=6000,
        description="User query to be answered by the chatbot.",
    )
    conversation_id: Optional[str] = Field(
        default=None,
        max_length=128,
        description="Existing conversation id. If not provided, service may create/use a new one.",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_directories()
    logger.info("Starting %s v%s in %s mode", APP_NAME, APP_VERSION, APP_ENV)
    yield
    logger.info("Shutting down %s", APP_NAME)


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Production-ready GenAI chatbot with PDF RAG, GitHub RAG, memory, caching, and monitoring.",
    lifespan=lifespan,
)


# ---------------- Prometheus Metrics ----------------
HTTP_REQUESTS_TOTAL = Counter(
    "genai_chatbot_http_requests_total",
    "Total HTTP requests received by the GenAI chatbot API.",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "genai_chatbot_http_request_duration_seconds",
    "HTTP request latency in seconds.",
    ["method", "path"],
)

CHAT_STREAM_REQUESTS_TOTAL = Counter(
    "genai_chatbot_chat_stream_requests_total",
    "Total authenticated chat streaming requests.",
    ["status"],
)


# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials="*" not in CORS_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


# ---------------- Middleware ----------------
@app.middleware("http")
async def prometheus_metrics_middleware(request: Request, call_next):
    start_time = perf_counter()
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response

    finally:
        route = request.scope.get("route")
        path = getattr(route, "path", request.url.path)

        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            path=path,
            status_code=str(status_code),
        ).inc()

        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=request.method,
            path=path,
        ).observe(perf_counter() - start_time)


# ---------------- Routers ----------------
app.include_router(user_router)
app.include_router(conversation_router)
app.include_router(upload_router)
app.include_router(github_router)


# ---------------- Global Error Handler ----------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled error while processing request. method=%s path=%s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error. Please try again later.",
        },
    )


# ---------------- Core Endpoints ----------------
@app.get("/", tags=["System"])
def home():
    return {
        "message": "GenAI Chatbot API is running",
        "app": APP_NAME,
        "version": APP_VERSION,
        "environment": APP_ENV,
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "healthy",
        "app": APP_NAME,
        "version": APP_VERSION,
        "environment": APP_ENV,
    }


@app.get("/metrics", tags=["Monitoring"])
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.post("/chat-stream", tags=["Chat"])
def chat_stream(
    request: ChatRequest,
    current_user: Any = Depends(get_current_user),
):
    CHAT_STREAM_REQUESTS_TOTAL.labels(status="accepted").inc()

    return StreamingResponse(
        process_chat_stream(
            query=request.query,
            conversation_id=request.conversation_id,
            current_user=current_user,
        ),
        media_type=STREAM_MEDIA_TYPE,
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )