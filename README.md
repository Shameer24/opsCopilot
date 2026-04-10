# opsCopilot

![CI](https://github.com/Shameer24/opsCopilot/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-PostgreSQL-336791?logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

**Upload your operational documents and logs — ask questions and get answers with source citations.**

opsCopilot is a self-hosted RAG (Retrieval-Augmented Generation) application. Drop in PDFs or text files; an LLM answers questions grounded exclusively in those documents, citing the exact chunk, page, and line number each claim comes from.

> 🔗 **[Live Demo](https://opscopilot.vercel.app)** — try it without signing up

---

## Features

- **Document ingestion** — upload PDFs and plain-text files up to 25 MB; text is chunked, embedded with a local sentence-transformer, and indexed in pgvector automatically in the background
- **Semantic search** — cosine similarity search retrieves the top-K most relevant chunks per query
- **Cited answers** — the LLM produces Markdown answers with explicit chunk references that resolve to filename, page, and line numbers
- **Dual LLM** — OpenAI (`gpt-4.1-mini`) or Ollama (local `llama3.1`); drops to retrieval-only mode if no LLM is reachable
- **Document management** — list, status-track, and delete documents from the UI; deletion cascades to embeddings and removes the file from disk
- **Feedback loop** — thumbs-up / thumbs-down per answer, stored alongside citation-coverage and retrieval-ratio metrics for every query
- **Evaluation dashboard** — recent query history with latency, LLM provider, and citation quality metrics
- **Auth** — JWT-based; every document, query, and feedback row is scoped to the requesting user
- **Rate limiting** — sliding-window limits on uploads (10/min) and chat (30/min) per user
- **Production-ready** — request logging middleware, health probe with DB check, startup env validation, paginated endpoints

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                             │
│                    Next.js 15 · Tailwind                    │
└───────────────────────┬─────────────────────────────────────┘
                        │ REST / JSON
┌───────────────────────▼─────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │  /auth   │  │ /docs    │  │  /chat   │  │  /eval     │  │
│  └──────────┘  └────┬─────┘  └────┬─────┘  └────────────┘  │
│                     │             │                          │
│              ┌──────▼──────┐  ┌───▼──────────────────────┐  │
│              │  Ingestion  │  │       RAG Pipeline        │  │
│              │  · chunk    │  │  1. embed question        │  │
│              │  · embed    │  │  2. pgvector search       │  │
│              │  · store    │  │  3. LLM answer + cite     │  │
│              └──────┬──────┘  └───┬──────────────────────┘  │
└─────────────────────┼─────────────┼────────────────────────-┘
                      │             │
         ┌────────────▼─────────────▼────────────┐
         │       PostgreSQL 16 + pgvector         │
         │  documents · chunks · users · logs     │
         └───────────────────────────────────────-┘
                      │
         ┌────────────▼─────────┐    ┌─────────────────────┐
         │  sentence-transformers│    │  OpenAI / Ollama     │
         │  all-MiniLM-L6-v2    │    │  (answer generation) │
         │  (local, 384-dim)    │    └─────────────────────-┘
         └──────────────────────┘
```

---

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI · Python 3.11 · Uvicorn |
| Database | PostgreSQL 16 + pgvector |
| Embeddings | `all-MiniLM-L6-v2` (384-dim, runs locally — no API cost) |
| LLM | OpenAI `gpt-4.1-mini` · Ollama `llama3.1` (local fallback) |
| Frontend | Next.js 15 · React 19 · Tailwind CSS |
| Auth | JWT HS256 · bcrypt passwords |
| Deployment | Docker Compose · Render · Vercel · Supabase |

---

## Quick start (Docker)

```bash
git clone https://github.com/Shameer24/opsCopilot.git
cd opsCopilot

cp .env.example .env
# Edit .env — set JWT_SECRET and OPENAI_API_KEY

docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3001 |
| Backend API | http://localhost:8000/api |
| API docs (Swagger) | http://localhost:8000/docs |

---

## Free cloud deployment (Supabase + Render + Vercel)

This stack is entirely free — no credit card required for Supabase or Vercel.

### Step 1 — Database: Supabase

1. Create a free project at [supabase.com](https://supabase.com)
2. In **Database → Extensions**, enable `vector`
3. In **Project Settings → Database**, copy the **Session mode** connection string:
   ```
   postgresql+psycopg://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
   ```
4. Run migrations once from your local machine:
   ```bash
   DATABASE_URL="<supabase-url>" alembic upgrade head
   ```

### Step 2 — Backend: Render

1. Create a free account at [render.com](https://render.com)
2. **New → Web Service → Connect your GitHub repo**
3. Set the root directory to `backend`, runtime to **Docker**
4. Add environment variables in the Render dashboard:
   ```
   DATABASE_URL    = <supabase session-mode URL>
   JWT_SECRET      = <a long random string>
   OPENAI_API_KEY  = <your key>
   LLM_PROVIDER    = openai
   CORS_ORIGINS    = https://your-app.vercel.app
   ```
5. Deploy — Render will run migrations automatically via the Dockerfile CMD
6. Note your backend URL: `https://opscopilot-backend.onrender.com`

> **Note:** Render's free tier spins down after 15 min of inactivity. The first request after sleep takes ~30 seconds. This is normal for portfolio demos.

### Step 3 — Frontend: Vercel

1. Import the repo at [vercel.com/new](https://vercel.com/new)
2. Set the **root directory** to `frontend`
3. Add one environment variable:
   ```
   NEXT_PUBLIC_API_BASE = https://opscopilot-backend.onrender.com/api
   ```
4. Deploy — Vercel handles the Next.js build automatically

---

## Running locally (without Docker)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install poetry && poetry install

export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5433/opscopilot"
export JWT_SECRET="dev-secret"
export OPENAI_API_KEY="sk-..."

alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_BASE=http://localhost:8000/api" > .env.local
npm run dev   # → http://localhost:3001
```

---

## API reference

All endpoints are prefixed `/api`. Protected routes require `Authorization: Bearer <token>`.

### Auth

| Method | Path | Body | Description |
|---|---|---|---|
| `POST` | `/auth/register` | `{email, password}` | Create account → JWT |
| `POST` | `/auth/login` | form: `username` + `password` | Login → JWT |

### Documents

| Method | Path | Description |
|---|---|---|
| `GET` | `/documents?skip=0&limit=50` | List your documents (paginated) |
| `POST` | `/documents/upload` | Upload PDF or TXT (multipart) |
| `DELETE` | `/documents/{id}` | Delete document + embeddings |

### Chat

| Method | Path | Description |
|---|---|---|
| `POST` | `/chat/ask` | RAG query → answer + citations |

```json
// Request
{ "question": "What are the top recurring error patterns?" }

// Response
{
  "answer_markdown": "The top patterns are **OOM kills** (doc 1, p.3) and ...",
  "citations": [
    { "filename": "runbook.pdf", "page_start": 3, "score": 0.872, ... }
  ],
  "query_log_id": "..."
}
```

### Feedback & Evaluation

| Method | Path | Description |
|---|---|---|
| `POST` | `/feedback` | Submit thumbs-up/down for a query |
| `GET` | `/eval/recent?limit=20` | Recent query logs with metrics |
| `GET` | `/eval/{id}` | Full detail for one query |
| `GET` | `/health` | Liveness + DB readiness probe |

---

## Configuration

All settings can be overridden with environment variables.

| Variable | Default | Description |
|---|---|---|
| `JWT_SECRET` | **required** | HS256 signing key (use a long random string) |
| `DATABASE_URL` | postgres @ localhost:5433 | SQLAlchemy connection string |
| `OPENAI_API_KEY` | — | Required when `LLM_PROVIDER=openai` |
| `LLM_PROVIDER` | `ollama` | `openai` or `ollama` |
| `OLLAMA_BASE_URL` | `http://host.docker.internal:11434` | Ollama endpoint |
| `OLLAMA_MODEL` | `llama3.1` | Ollama model name |
| `CHAT_MODEL` | `gpt-4.1-mini` | OpenAI model |
| `EMBEDDINGS_PROVIDER` | `local` | `local` (sentence-transformers) or `openai` |
| `TOP_K` | `6` | Chunks retrieved per query |
| `MIN_SCORE` | `0.10` | Minimum cosine similarity threshold |
| `MAX_UPLOAD_MB` | `25` | Maximum file size |
| `RL_ASK_PER_MINUTE` | `30` | Chat rate limit per user |
| `RL_UPLOAD_PER_MINUTE` | `10` | Upload rate limit per user |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:3001` | Allowed origins |

---

## Tests

```bash
cd backend

export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5433/opscopilot"
export JWT_SECRET="test-secret"

pytest tests/ -v
```

The test suite covers: health probe, user registration, duplicate detection, wrong-password rejection, document upload, document delete, cross-user isolation, chat endpoint shape, and eval history.

CI runs the full suite on every push via GitHub Actions (see `.github/workflows/ci.yml`).

---

## Project structure

```
opsCopilot/
├── .github/workflows/ci.yml     # GitHub Actions — lint + test on every push
├── backend/
│   ├── app/
│   │   ├── api/routers/         # auth · chat · documents · feedback · eval · health
│   │   ├── core/                # config · security · logging · rate limiting · errors
│   │   ├── db/                  # SQLAlchemy engine + session factory
│   │   ├── models/              # ORM — User · Document · Chunk · QueryLog · Feedback
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── services/            # chunking · embeddings · ingestion · llm · retrieval · storage
│   │   ├── utils/               # hashing · ids · text · timing
│   │   ├── workers/             # background ingestion task
│   │   └── main.py              # FastAPI app + CORS + request logging middleware
│   ├── alembic/                 # database migrations
│   └── tests/                   # pytest integration suite
├── frontend/
│   └── src/
│       ├── app/                 # Next.js app-router pages
│       │   ├── (auth)/          # login · register
│       │   └── (app)/           # chat · documents · upload · settings
│       ├── components/          # ChatBox · DocumentTable · CitationList · …
│       └── lib/                 # typed API client · auth helpers · shared types
├── docker-compose.yml           # local all-in-one stack
├── render.yaml                  # Render deployment config
└── .env.example                 # all supported environment variables with comments
```

---

## How it works

1. **Upload** — file saved to disk; `Document` row created with status `UPLOADED`
2. **Ingestion** (background) — text extracted from PDF/TXT → split into overlapping 2,200-char chunks → each chunk embedded with `all-MiniLM-L6-v2` → vectors stored in pgvector; status → `READY`
3. **Query** — user's question embedded with the same model; pgvector returns top-K chunks by cosine similarity above the min-score threshold
4. **Answer** — retrieved chunks packed into a prompt; LLM returns Markdown with explicit chunk IDs; citations resolved to document metadata (filename, page, line) and returned with the answer
5. **Feedback** — user rates the answer; citation-coverage and retrieval-ratio metrics logged per query for evaluation

---

## License

MIT
