# BE — SkyDesk AI backend

FastAPI + LangGraph agent for the Saffron Air (fictional) IT helpdesk.
LLM: Groq (`openai/gpt-oss-20b`) · Data: MongoDB Atlas · RAG: Pinecone (hosted embedding + rerank).

## Setup

Python 3.11.9 (see `.python-version`).

```bash
cd BE
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `BE/.env` (never commit it) with these keys:

| Key | Example / meaning |
|---|---|
| `APP_NAME`, `APP_VERSION` | `SkyDesk AI`, `0.1.0` |
| `GROQ_API_KEY` | from console.groq.com |
| `GROQ_MODEL` | `openai/gpt-oss-20b` |
| `GROQ_TEMPERATURE`, `GROQ_TIMEOUT`, `GROQ_MAX_RETRIES`, `GROQ_REASONING_EFFORT` | `0`, `60`, `2`, `low` |
| `MONGODB_URI`, `MONGODB_DB` | Atlas connection string, `skydesk` |
| `SLA_HOURS` | `{"P1": 4, "P2": 8, "P3": 24, "P4": 72}` |
| `SIMILAR_TICKETS_LIMIT` | `5` |
| `AGENT_RETRY_ATTEMPTS` | `3` |
| `PINECONE_API_KEY`, `PINECONE_INDEX` | from app.pinecone.io, `saffron-it-kb` |
| `PINECONE_CLOUD`, `PINECONE_REGION` | `aws`, `us-east-1` |
| `PINECONE_EMBED_MODEL`, `PINECONE_EMBED_DIMENSION`, `PINECONE_RERANK_MODEL` | `llama-text-embed-v2`, `1024`, `bge-reranker-v2-m3` |
| `RAG_KB_DIR`, `RAG_CHUNK_SIZE`, `RAG_CHUNK_OVERLAP`, `RAG_TOP_K`, `RAG_TOP_N` | `data/kb`, `800`, `200`, `8`, `3` |

Load the knowledge base into Pinecone (once, and after editing `data/kb/`):

```bash
python -m scripts.ingest_kb
```

Run the API:

```bash
uvicorn main:app --reload --port 8000     # docs at http://localhost:8000/docs
```

## Layout

```
main.py                 FastAPI app, registers routers
app/config/settings.py  reads .env
app/core/               llm_client.py (Groq), domain.py (teams, categories, priorities, statuses)
app/db/                 mongo.py (Atlas), vector_store.py (Pinecone)
app/api/                HTTP endpoints for the frontend
app/services/           business logic shared by API routes and agent tools
app/tools/              one file per LLM tool
app/agent/              LangGraph state, nodes and graph
app/prompts/            system prompts
data/kb/                knowledge base documents (RAG source)
scripts/ingest_kb.py    chunks data/kb and stores it in Pinecone
```

Agent graph: `START -> classify_issue (first message) -> resolve_issue <-> tools -> END`.
Chat memory and paused approvals are stored in MongoDB by the LangGraph checkpointer.

## Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /agent/chat` | Employee message to the agent (`employee_id`, `message`, `thread_id`) |
| `GET /tickets`, `GET /tickets/{id}`, `PATCH /tickets/{id}` | Ticket list, detail, update |
| `GET /approvals`, `POST /approvals/{id}/decision` | Pending approvals; approve/reject resumes the agent |
| `GET /employees`, `GET /employees/{id}` | Employee directory |
| `GET /knowledge/search?q=` | Test RAG retrieval |
| `POST /llm/ask` | Test the LLM |
| `GET /health` | API + MongoDB status |
