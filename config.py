import os
from functools import lru_cache
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ---------------- App ----------------
    APP_NAME: str = "GenAI Chatbot"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field(default="development", description="development, staging, production")
    LOG_LEVEL: str = "INFO"

    # ---------------- API / CORS ----------------
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://92.4.93.156",
    ]

    STREAM_MEDIA_TYPE: str = "text/plain"

    # ---------------- LLM ----------------
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 2048

    # ---------------- MongoDB ----------------
    MONGO_URL: str = ""
    MONGO_DB_NAME: str = "chatbot_db"
    MONGO_USER_COLLECTION: str = "users"
    MONGO_CHAT_COLLECTION: str = "chat_history"

    # ---------------- Redis ----------------
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_CACHE_TTL_SECONDS: int = 3600

    # ---------------- Auth ----------------
    SECRET_KEY: str = "CHAT_BOT"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # ---------------- Storage ----------------
    STORAGE_DIR: Path = BASE_DIR / "storage"

    UPLOAD_FOLDER: Path = BASE_DIR / "storage" / "uploads"
    REPO_FOLDER: Path = BASE_DIR / "repos"

    PDF_INDEX_PATH: Path = BASE_DIR / "storage" / "pdf_index"
    GITHUB_INDEX_PATH: Path = BASE_DIR / "storage" / "github_index"

    PDF_CHUNK_PATH: Path = BASE_DIR / "storage" / "pdf_chunks.pkl"
    GITHUB_CHUNK_PATH: Path = BASE_DIR / "storage" / "github_chunks.pkl"

    # ---------------- RAG ----------------
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    RERANKER_MODEL_NAME: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150

    VECTOR_TOP_K: int = 8
    BM25_TOP_K: int = 8
    HYBRID_TOP_K: int = 10
    RERANK_TOP_K: int = 5

    MAX_CONTEXT_CHARS: int = 12000

    # ---------------- Upload Limits ----------------
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_PDF_EXTENSIONS: List[str] = [".pdf"]

    # ---------------- GitHub RAG ----------------
    GITHUB_MAX_FILES: int = 80
    GITHUB_MAX_FILE_SIZE_KB: int = 250
    GITHUB_ALLOWED_EXTENSIONS: List[str] = [
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".md",
        ".txt",
        ".json",
        ".yml",
        ".yaml",
        ".toml",
        ".ini",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("GITHUB_ALLOWED_EXTENSIONS", "ALLOWED_PDF_EXTENSIONS", mode="before")
    @classmethod
    def parse_extension_lists(cls, value):
        if isinstance(value, str):
            return [ext.strip() for ext in value.split(",") if ext.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def ensure_directories() -> None:
    directories = [
        settings.STORAGE_DIR,
        settings.UPLOAD_FOLDER,
        settings.REPO_FOLDER,
        settings.PDF_INDEX_PATH,
        settings.GITHUB_INDEX_PATH,
        BASE_DIR / "logs",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


# ---------------- Backward-compatible constants ----------------
APP_NAME = settings.APP_NAME
APP_VERSION = settings.APP_VERSION
APP_ENV = settings.APP_ENV
LOG_LEVEL = settings.LOG_LEVEL

CORS_ORIGINS = settings.CORS_ORIGINS
STREAM_MEDIA_TYPE = settings.STREAM_MEDIA_TYPE

GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_MODEL = settings.GROQ_MODEL
LLM_TEMPERATURE = settings.LLM_TEMPERATURE
LLM_MAX_TOKENS = settings.LLM_MAX_TOKENS

MONGO_URL = settings.MONGO_URL
MONGO_DB_NAME = settings.MONGO_DB_NAME
MONGO_USER_COLLECTION = settings.MONGO_USER_COLLECTION
MONGO_CHAT_COLLECTION = settings.MONGO_CHAT_COLLECTION

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_DB = settings.REDIS_DB
REDIS_PASSWORD = settings.REDIS_PASSWORD
REDIS_CACHE_TTL_SECONDS = settings.REDIS_CACHE_TTL_SECONDS

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

PDF_INDEX_PATH = str(settings.PDF_INDEX_PATH)
GITHUB_INDEX_PATH = str(settings.GITHUB_INDEX_PATH)

PDF_CHUNK_PATH = str(settings.PDF_CHUNK_PATH)
GITHUB_CHUNK_PATH = str(settings.GITHUB_CHUNK_PATH)

UPLOAD_FOLDER = str(settings.UPLOAD_FOLDER)
REPO_FOLDER = str(settings.REPO_FOLDER)

EMBEDDING_MODEL_NAME = settings.EMBEDDING_MODEL_NAME
RERANKER_MODEL_NAME = settings.RERANKER_MODEL_NAME

CHUNK_SIZE = settings.CHUNK_SIZE
CHUNK_OVERLAP = settings.CHUNK_OVERLAP

VECTOR_TOP_K = settings.VECTOR_TOP_K
BM25_TOP_K = settings.BM25_TOP_K
HYBRID_TOP_K = settings.HYBRID_TOP_K
RERANK_TOP_K = settings.RERANK_TOP_K

MAX_CONTEXT_CHARS = settings.MAX_CONTEXT_CHARS

MAX_UPLOAD_SIZE_MB = settings.MAX_UPLOAD_SIZE_MB
ALLOWED_PDF_EXTENSIONS = settings.ALLOWED_PDF_EXTENSIONS

GITHUB_MAX_FILES = settings.GITHUB_MAX_FILES
GITHUB_MAX_FILE_SIZE_KB = settings.GITHUB_MAX_FILE_SIZE_KB
GITHUB_ALLOWED_EXTENSIONS = settings.GITHUB_ALLOWED_EXTENSIONS