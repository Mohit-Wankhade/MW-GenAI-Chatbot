# MW GenAI Chatbot

A production-ready Retrieval-Augmented Generation (RAG) chatbot built with FastAPI and React.

The application allows users to upload PDF documents or index GitHub repositories, then ask questions grounded in those sources using a hybrid retrieval pipeline and Groq LLMs.

---

## ✨ Features

### 🔐 Authentication

- JWT Authentication
- User Registration & Login
- Protected Routes
- Conversation ownership

---

### 📄 PDF RAG

- Upload PDF documents
- Intelligent text chunking
- FAISS Vector Index
- Source attribution
- Conversation-aware responses

---

### 💻 GitHub Repository RAG

- Clone public repositories
- Parse source code
- Code-aware chunking
- Repository indexing
- Semantic code search

---

### 🧠 Hybrid Retrieval

Instead of relying on vector search alone, the chatbot combines:

- FAISS Dense Retrieval
- BM25 Sparse Retrieval
- Cross-Encoder Re-ranking

This improves retrieval quality significantly.

---

### 💬 Conversation Management

- Persistent chat history
- MongoDB storage
- Multiple conversations
- Conversation deletion
- Context-aware follow-up questions

---

### ⚡ Performance

- Redis Response Cache
- Hybrid Retrieval
- Streaming Responses
- Optimized indexing

---

### 📊 Monitoring

- Prometheus Metrics
- Grafana Dashboard
- Health Check Endpoint
- Docker Health Checks

---

### 🐳 Production Ready

- Docker
- Docker Compose
- Nginx Reverse Proxy
- GitHub Actions CI
- Structured Logging
- Environment Variables

---

# 🏗 Tech Stack

## Backend

- FastAPI
- Python
- LangChain
- Sentence Transformers
- FAISS
- BM25
- Groq API
- MongoDB
- Redis

## Frontend

- React
- Vite
- TailwindCSS
- Axios
- React Router

## DevOps

- Docker
- Docker Compose
- Nginx
- GitHub Actions
- Prometheus
- Grafana

---

# 📂 Project Structure

```
Chatbot
│
├── auth/
├── cache/
├── db/
├── frontend/
├── github/
├── rag/
├── routes/
├── services/
├── storage/
├── utils/
│
├── app.py
├── config.py
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/<your-username>/GenAI-Chatbot.git

cd GenAI-Chatbot
```

---

## Configure Environment

Create a `.env` file.

```env
GROQ_API_KEY=YOUR_KEY

MONGO_URL=YOUR_MONGODB_URI

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

SECRET_KEY=YOUR_SECRET
ALGORITHM=HS256
```

---

## Run using Docker Compose

```bash
docker compose up --build
```

---

# 🌐 Services

| Service | URL |
|----------|---------------------------|
| Frontend | http://localhost |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Metrics | http://localhost:8000/metrics |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 |

---

# 📈 Monitoring

The project exposes Prometheus metrics including:

- HTTP Requests
- Response Time
- PDF Upload Count
- GitHub Repository Count
- Python Runtime Metrics

Metrics endpoint:

```
/metrics
```

---

# 🔒 Security

- JWT Authentication
- Password Hashing (bcrypt)
- Protected API Routes
- Environment Variables
- CORS Configuration

---

# 📸 Screenshots

Add screenshots here.

Example:

- Login
- Register
- Chat
- Upload PDF
- GitHub Indexing
- Grafana Dashboard

---

# 🚀 Future Improvements

- Kubernetes Deployment
- Streaming Tokens (SSE)
- CI/CD Deployment Pipeline
- Role Based Authentication
- Multi-LLM Support
- PostgreSQL Support
- Rate Limiting
- Vector Database Integration

---

# 👨‍💻 Author

**Mohit Wankhade**

LinkedIn:
https://www.linkedin.com/in/mohit-wankhade-a9037b205/

GitHub:
https://github.com/Mohit-Wankhade
