from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MONGO_URL = os.getenv("MONGO_URL", "")

PDF_INDEX_PATH = "storage/pdf_index"
GITHUB_INDEX_PATH = "storage/github_index"

PDF_CHUNK_PATH = "storage/pdf_chunks.pkl"
GITHUB_CHUNK_PATH = "storage/github_chunks.pkl"

UPLOAD_FOLDER = "storage/uploads"
REPO_FOLDER = "repos"

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

SECRET_KEY = os.getenv("SECRET_KEY", "CHATBOT_KEY")
ALGORITHM = "HS256"
