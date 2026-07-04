# MW GenAI Chatbot

A production-ready **Retrieval-Augmented Generation chatbot** built with **FastAPI, React, MongoDB, Redis, FAISS, BM25, Cross-Encoder reranking, Docker, Nginx, Prometheus, and Grafana**.

The application allows authenticated users to upload PDF documents or index public GitHub repositories, then ask questions grounded in those sources using a hybrid RAG pipeline and Groq LLMs.

---

## Architecture

![Architecture](assets/architecture.png)

---

## Features

### Authentication

* User registration and login
* JWT-based authentication
* Password hashing with bcrypt
* Protected backend routes
* Protected frontend routes
* Conversation ownership validation

---

### PDF RAG

* Upload and index PDF documents
* Extract text page-by-page using PyMuPDF
* Metadata-rich chunking with page numbers
* FAISS vector indexing
* BM25 sparse retrieval
* Source attribution with file name and page number
* Multi-PDF chunk persistence

---

### GitHub Repository RAG

* Index public GitHub repositories
* Clone repositories safely
* Skip unsupported, binary, large, and unnecessary files
* Code-aware chunking
* Semantic code search
* Source attribution with repository and file path
* Multi-repository chunk persistence

---

### Hybrid Retrieval Pipeline

The chatbot uses a multi-stage retrieval pipeline:

1. Dense retrieval using FAISS
2. Sparse retrieval using BM25
3. Result fusion and deduplication
4. Cross-Encoder reranking
5. Context construction for the LLM

This improves answer quality compared to vector search alone.

---

### Conversation Management

* Persistent chat history
* Multiple conversations per user
* Rename conversations
* Delete conversations
* Conversation-aware follow-up questions
* MongoDB-based message storage

---

### Performance

* Streaming LLM responses
* Redis response caching
* Lazy model loading
* Chunk deduplication
* Optimized FAISS index updates
* Dockerized services

---

### Monitoring and Observability

* Prometheus metrics endpoint
* Grafana support
* HTTP request metrics
* Chat latency metrics
* Upload and indexing metrics
* Redis cache hit/miss metrics
* Docker health checks
* Structured logging

---

## Tech Stack

### Backend

* FastAPI
* Python
* LangChain
* Sentence Transformers
* Cross-Encoder reranking
* FAISS
* BM25
* Groq API
* MongoDB
* Redis
* PyMuPDF
* JWT authentication

### Frontend

* React
* Vite
* Tailwind CSS
* Axios
* React Router
* React Markdown
* Syntax highlighting

### DevOps

* Docker
* Docker Compose
* Nginx reverse proxy
* Prometheus
* Grafana
* Oracle Cloud deployment ready

---

## Project Structure

```bash
Chatbot/
├── app.py
├── config.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── prometheus.yml
├── README.md
├── assets/
│   └── architecture.png
├── auth/
├── cache/
├── db/
├── github/
├── rag/
├── routes/
├── services/
├── storage/
├── utils/
├── frontend/
└── nginx/
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
APP_ENV=development

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant

MONGO_URL=your_mongodb_connection_string
MONGO_DB_NAME=chatbot_db

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

SECRET_KEY=replace_with_a_strong_secret_key
ALGORITHM=HS256

CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost,http://127.0.0.1:5173,http://127.0.0.1:3000
```


---

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/Mohit-Wankhade/GenAI-Chatbot.git
cd GenAI-Chatbot
```

### 2. Start the full stack using Docker Compose

```bash
docker compose up --build
```

### 3. Open the application

| Service      | URL                        |
| ------------ | -------------------------- |
| Frontend     | http://localhost           |
| Backend API  | http://localhost:8000      |
| Swagger Docs | http://localhost:8000/docs |
| Prometheus   | http://localhost:9090      |
| Grafana      | http://localhost:3001      |

Default Grafana login, if unchanged:

```txt
Username: admin
Password: admin
```

---

## Recommended Testing Flow Before GitHub Push

Before pushing updates to GitHub, test the project locally.

### 1. Build containers

```bash
docker compose build
```

### 2. Start containers

```bash
docker compose up -d
```

### 3. Check running containers

```bash
docker compose ps
```

### 4. Check backend health

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

### 5. Check logs

```bash
docker compose logs -f backend
```

### 6. Test in browser

Open:

```txt
http://localhost
```

Then test:

* Register user
* Login
* Upload PDF
* Ask PDF-based question
* Index GitHub repository
* Ask code-based question
* Rename conversation
* Delete conversation
* Check Prometheus metrics
* Check Grafana access

### 7. Stop containers

```bash
docker compose down
```

---

## GitHub Update Flow

After local testing works successfully:

```bash
git status
git add .
git commit -m "Improve production-ready RAG chatbot architecture"
git push origin main
```

---

## Deployment Plan

The recommended deployment order is:

1. Test locally with Docker Compose
2. Push stable code to GitHub
3. SSH into Oracle Cloud VM
4. Install Docker and Docker Compose on the VM
5. Clone the repository on the VM
6. Create the production `.env` file
7. Start containers using Docker Compose
8. Open firewall/security list ports
9. Access the app using the VM public IP
10. Optionally attach a domain and enable HTTPS

---

## Oracle Cloud Deployment

### 1. SSH into the VM

```bash
ssh -i /path/to/private-key.key ubuntu@your_public_ip
```

### 2. Clone the repository

```bash
git clone https://github.com/Mohit-Wankhade/GenAI-Chatbot.git
cd GenAI-Chatbot
```

### 3. Create `.env`

```bash
nano .env
```

Add production values:

```env
APP_ENV=production

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant

MONGO_URL=your_mongodb_connection_string
MONGO_DB_NAME=chatbot_db

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

SECRET_KEY=replace_with_a_strong_secret_key
ALGORITHM=HS256

CORS_ORIGINS=http://your_public_ip
```

### 4. Prepare runtime folders

```bash
mkdir -p storage repos logs
sudo chown -R 1000:1000 storage repos logs
```

### 5. Build and run

```bash
docker compose up -d --build
```

### 6. Check containers

```bash
docker compose ps
```

### 7. Check logs

```bash
docker compose logs -f backend
```

### 8. Access the app

```txt
http://your_public_ip
```

---

## API Endpoints

### Authentication

| Method | Endpoint         | Description                 |
| ------ | ---------------- | --------------------------- |
| POST   | `/auth/register` | Register a new user         |
| POST   | `/auth/login`    | Login and receive JWT token |
| GET    | `/auth/me`       | Get current user            |

### Chat

| Method | Endpoint       | Description             |
| ------ | -------------- | ----------------------- |
| POST   | `/chat-stream` | Stream chatbot response |

### Conversation

| Method | Endpoint                      | Description                      |
| ------ | ----------------------------- | -------------------------------- |
| POST   | `/conversation/new`           | Create new conversation          |
| GET    | `/conversation`               | List user conversations          |
| GET    | `/conversation/{id}/messages` | Get messages from a conversation |
| PUT    | `/conversation/{id}`          | Rename conversation              |
| DELETE | `/conversation/{id}`          | Delete conversation              |

### Upload

| Method | Endpoint      | Description          |
| ------ | ------------- | -------------------- |
| POST   | `/upload/pdf` | Upload and index PDF |

### GitHub

| Method | Endpoint        | Description                    |
| ------ | --------------- | ------------------------------ |
| POST   | `/github/index` | Index public GitHub repository |

### Monitoring

| Method | Endpoint   | Description        |
| ------ | ---------- | ------------------ |
| GET    | `/health`  | Health check       |
| GET    | `/metrics` | Prometheus metrics |

---

## Monitoring

Prometheus scrapes backend metrics from:

```txt
backend:8000/metrics
```

Available metric categories include:

* HTTP requests
* Request latency
* Chat requests
* Chat response time
* PDF uploads
* GitHub repository indexing
* Redis cache hits
* Redis cache misses
* RAG retrieval metrics

---

## Security

Implemented security features:

* JWT authentication
* Password hashing
* Protected API routes
* Conversation ownership checks
* File type validation
* Upload size limits
* Safe GitHub URL validation
* Environment-based secrets
* Nginx reverse proxy
* Non-root backend Docker container

Recommended future security improvements:

* Refresh tokens
* Rate limiting
* HTTPS with Let's Encrypt
* Role-based access control
* Request audit logs
* Per-user document isolation

---

## Sample Files

This repository includes two sample PDFs for testing the PDF RAG pipeline and 1 txt file having sample github repos:

```txt
samples/sample.pdf
samples/sample2.pdf
samples/sample_github_repo.txt

---

## Future Improvements

* HTTPS with domain support
* Server-Sent Events for cleaner streaming
* Per-user isolated vector indexes
* Background indexing jobs
* Document deletion and reindexing
* RAG evaluation metrics
* Multi-LLM provider support
* PostgreSQL option
* Kubernetes deployment
* CI/CD deployment pipeline
* Admin dashboard
* Advanced file type support

---

## Resume Highlights

This project demonstrates:

* Full-stack GenAI application development
* Production-grade RAG architecture
* Hybrid search using FAISS and BM25
* Cross-Encoder reranking
* Streaming LLM responses
* Authentication and protected routes
* MongoDB conversation memory
* Redis caching
* Dockerized microservice-style deployment
* Nginx reverse proxy
* Prometheus and Grafana monitoring
* Cloud deployment readiness

---

## Author

**Mohit Wankhade**

LinkedIn:
https://www.linkedin.com/in/mohit-wankhade-a9037b205/

GitHub:
https://github.com/Mohit-Wankhade


