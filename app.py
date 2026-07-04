from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from fastapi.responses import Response
import time

from utils.monitoring import HTTP_REQUESTS
from auth.auth_dependencies import get_current_user
from services.chat_service import process_chat_stream

from routes.upload import router as upload_router
from routes.github import router as github_router
from routes.user import router as user_router
from routes.conversation import router as conversation_router


class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None


app = FastAPI()
REQUEST_COUNT = Counter(
    "chatbot_requests_total",
    "Total HTTP Requests"
)

REQUEST_LATENCY = Histogram(
    "chatbot_request_latency_seconds",
    "Request latency"
)

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite development
        "http://localhost:3000",  # Docker frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Routers ----------------
app.include_router(conversation_router)
app.include_router(upload_router)
app.include_router(github_router)
app.include_router(user_router)

@app.middleware("http")
async def metrics(request, call_next):

    HTTP_REQUESTS.labels(
        request.method,
        request.url.path
    ).inc()

    response = await call_next(request)

    return response
   
    
@app.get("/metrics")
def metrics():

    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
    

@app.get("/")
def home():
    REQUEST_COUNT.labels("GET", "/").inc()
    return {"message": "GenAI Chatbot Running"}


@app.post("/chat-stream")
def chat_stream(
    request: ChatRequest,
    current_user: str = Depends(get_current_user)
):
    REQUEST_COUNT.labels("POST", "/chat-stream").inc()
    return StreamingResponse(
        process_chat_stream(
            query=request.query,
            conversation_id=request.conversation_id,
            current_user=current_user,
        ),
        media_type="text/plain",
    )

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }