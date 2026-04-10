# opsCopilot

**Upload your operational documents and logs — then ask questions and get answers with source citations.**

opsCopilot is a self-hosted RAG (Retrieval-Augmented Generation) application. Drop in PDFs or text files, and an LLM will answer questions grounded exclusively in those documents, telling you exactly which chunk and page each claim comes from.

---

## Features

- **Document ingestion** — upload PDFs and plain-text files up to 25 MB; text is chunked, embedded, and indexed automatically in the background
- **Vector search** — cosine similarity search via pgvector; every query retrieves the top-K most relevant chunks
- **Cited answers** — the LLM produces Markdown answers with explicit chunk references; citations resolve to filename, page, and line numbers
- **Dual LLM support** — uses Ollama (local, default) with automatic fallback to OpenAI; drops to retrieval-only mode if no LLM is reachable
- **Feedback loop** — thumbs-up / thumbs-down per answer; stored with citation-coverage and retrieval-ratio metrics for every query
- **Authentication** — JWT-based auth; every document, query, and feedback row is scoped to the requesting user
- **Rate limiting** — sliding-window limits on uploads (10/min) and chat (30/min) per user
- **Document management** — list and delete documents from the UI; deletion cascades to embeddings and removes the file from disk
- **Evaluation dashboard** — recent query history with latency, LLM provider, and citation quality metrics

---

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI · Python 3.11 · Uvicorn |
| Database | PostgreSQL 16 + pgvector extension |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (384-dim, runs locally) |
| LLM | Ollama (`llama3.1`) · OpenAI fallback |
| Frontend | Next.js 15 · React 19 · Tailwind CSS |
| Auth | JWT HS256 · bcrypt passwords |
| Deployment | Docker Compose |

---

## Quick start

### Prerequisites

- Docker and Docker Compose
- (Optional) [Ollama](https://ollama.ai) running locally for LLM answers

### 1 — Clone & configure

```bash
git clone https://github.com/Shameer24/opsCopilot.git
cd opsCopilot
cp .env.example .env
```

Edit `.env` and set your values:

```env
JWT_SECRET=change_me_to_a_long_random_string
OPENAI_API_KEY=sk-...          # only needed if using OpenAI as LLM/embeddings provider
```

### 2 — Start everything

```bash
docker compose up --build
```

This starts three services:

| Service | Port | Description |
|---|---|---|
| `db` | 5433 | PostgreSQL 16 with pgvector |
| `backend` | 8000 | FastAPI API |
| `frontend` | 3001 | Next.js UI |

Open **http://localhost:3001** in your browser.

### 3 — (Optional) Pull an Ollama model

If you want local LLM answers instead of OpenAI:

```bash
ollama pull llama3.1
```

Ollama runs on your host and is reached from inside Docker via `host.docker.internal:11434`.

---

## Running without Docker (development)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install poetry
poetry install

# Start a local Postgres with pgvector (or adjust DATABASE_URL)
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5433/opscopilot"
export JWT_SECRET="dev-secret"

alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
# Set the API base URL
echo "NEXT_PUBLIC_API_BASE=http://localhost:8000/api" > .env.local
npm run dev        # starts on http://localhost:3001
```

---

## API reference

All endpoints are prefixed with `/api`. Protected routes require `Authorization: Bearer <token>`.

### Auth

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Create account → returns JWT |
| `POST` | `/auth/login` | Login (form-encoded) → returns JWT |

### Documents

| Method | Path | Description |
|---|---|---|
| `GET` | `/documents?skip=0&limit=50` | List your documents (paginated) |
| `POST` | `/documents/upload` | Upload a PDF or TXT file |
| `DELETE` | `/documents/{id}` | Delete a document and its embeddings |

### Chat

| Method | Path | Description |
|---|---|---|
| `POST` | `/chat/ask` | Ask a question; returns answer + citations |

Request body:
```json
{ "question": "What are the top recurring error patterns?" }
```

Response:
```json
{
  "answer_markdown": "The top patterns are ...",
  "citations": [
    {
      "chunk_id": "...",
      "document_id": "...",
      "filename": "runbook.pdf",
      "page_start": 3,
      "score": 0.872
    }
  ],
  "query_log_id": "..."
}
```

### Feedback

| Method | Path | Description |
|---|---|---|
| `POST` | `/feedback` | Submit thumbs-up / thumbs-down for a query |

### Evaluation

| Method | Path | Description |
|---|---|---|
| `GET` | `/eval/recent?limit=20` | Recent query logs with metrics |
| `GET` | `/eval/{query_log_id}` | Full detail for a single query |

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness + DB readiness probe |

---

## Configuration

All settings can be overridden with environment variables. Set them in `.env` or pass them to `docker compose`.

| Variable | Default | Description |
|---|---|---|
| `JWT_SECRET` | **required** | Secret key for signing JWTs |
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@localhost:5433/opscopilot` | Postgres connection string |
| `OPENAI_API_KEY` | — | Required if `LLM_PROVIDER=openai` or `EMBEDDINGS_PROVIDER=openai` |
| `LLM_PROVIDER` | `ollama` | `ollama` or `openai` |
| `OLLAMA_BASE_URL` | `http://host.docker.internal:11434` | Ollama endpoint |
| `OLLAMA_MODEL` | `llama3.1` | Ollama model name |
| `CHAT_MODEL` | `gpt-4.1-mini` | OpenAI model (when `LLM_PROVIDER=openai`) |
| `EMBEDDINGS_PROVIDER` | `local` | `local` (sentence-transformers) or `openai` |
| `TOP_K` | `6` | Number of chunks retrieved per query |
| `MIN_SCORE` | `0.10` | Minimum cosine similarity to include a chunk |
| `MAX_UPLOAD_MB` | `25` | Maximum upload file size |
| `RL_ASK_PER_MINUTE` | `30` | Chat rate limit per user |
| `RL_UPLOAD_PER_MINUTE` | `10` | Upload rate limit per user |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:3001` | Allowed CORS origins |

---

## Running tests

```bash
cd backend

# With a running Postgres:
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5433/opscopilot"
export JWT_SECRET="test-secret"

pytest tests/ -v
```

The test suite covers health, auth, document upload/delete, cross-user isolation, and chat endpoint shape.

---

## Project structure

```
opsCopilot/
├── backend/
│   ├── app/
│   │   ├── api/routers/      # auth, chat, documents, feedback, eval, health
│   │   ├── core/             # config, security, logging, rate limiting, errors
│   │   ├── db/               # SQLAlchemy engine + session
│   │   ├── models/           # ORM models (User, Document, Chunk, QueryLog, Feedback)
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # chunking, embeddings, ingestion, llm, retrieval, storage
│   │   ├── utils/            # hashing, ids, text, timing helpers
│   │   ├── workers/          # background ingestion task
│   │   └── main.py           # FastAPI app + middleware
│   ├── alembic/              # database migrations
│   └── tests/                # pytest suite
└── frontend/
    ├── src/
    │   ├── app/              # Next.js app-router pages
    │   │   ├── (auth)/       # login, register
    │   │   └── (app)/        # chat, documents, upload, settings
    │   ├── components/       # ChatBox, DocumentTable, CitationList, …
    │   └── lib/              # api client, auth helpers, shared types
    └── public/
```

---

## How it works

1. **Upload** — a file is stored on disk and a `Document` row is created with status `UPLOADED`
2. **Ingestion** — a background task extracts text, splits it into overlapping chunks, embeds each chunk with `all-MiniLM-L6-v2`, and stores the vectors in Postgres via pgvector; status moves to `READY`
3. **Query** — the user's question is embedded with the same model; pgvector returns the top-K closest chunks by cosine similarity
4. **Answer** — the retrieved chunks are formatted into a prompt; the LLM produces a Markdown answer that cites specific chunk IDs; citations are resolved to document metadata and returned alongside the answer
5. **Feedback** — the user rates the answer; rating and latency metrics are stored per query for future evaluation

---

## License

MIT
