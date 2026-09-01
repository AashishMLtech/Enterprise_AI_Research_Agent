# Enterprise AI Research Agent

An assignment-grade, evidence-first research platform scaffold. The system keeps deterministic controls in charge of validation, access, budgets, retrieval, context sizing, and verification; LLMs are used only for language tasks.

## Technology stack

- Frontend: React 18, Vite 5, TypeScript, Tailwind CSS, `pdfjs-dist`
- Backend: Python 3.14, FastAPI, Pydantic 2, LangGraph
- Database: PostgreSQL, pgvector, SQLAlchemy, `psycopg[binary,pool]`, PostgreSQL full-text search
- AI: Groq provider abstraction, tiered routing, Sentence-Transformers embeddings, `tiktoken`
- Ingestion: Newspaper3k (`newspaper3k`) for normalized web text, PDF parsing in workers
- Jobs and cache: Redis with lightweight workers
- Operations: Docker Compose, Pytest, structured logging, OpenTelemetry-ready boundaries

## Current scope

This project is currently a demo research agent focused specifically on banking and retail. It is designed to answer research questions within those two industries using configured vocabulary, guardrails, retrieved evidence, and AI-assisted synthesis.

The current implementation is intentionally limited in scope for demonstration purposes. The configuration-driven architecture can be extended to support additional industries or research topics in the future by adding new industry configurations and retrieval sources.

## Quick start

```bash
py -3.14 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
cd frontend
npm install
cd ..
docker compose up --build
```

The API is available at `http://localhost:8000`, with interactive docs at `/docs`. Copy `.env.example` to a local `.env` and provide credentials before enabling external providers. Never commit `.env`.

## Safety design

The request path is:

`validation -> injection/PII checks -> industry OOD gate -> budget/access controls -> retrieval -> compact context -> synthesis -> deterministic verification`

OOD detection is implemented as a deterministic configuration-aware gate. It compares query terms and retrieved document metadata against the active industry's configured vocabulary and source categories. If the query or evidence is out of distribution, synthesis is blocked and the API returns an explicit insufficient-evidence result.

## Repository structure

- `backend/app/`: FastAPI application, guardrails, retrieval, ingestion, LLM contracts, and orchestration boundaries
- `frontend/`: React/Vite UI shell with research, trace, and evidence areas
- `configs/industries/`: industry vocabulary, source priorities, and OOD thresholds
- `tests/`: guardrail and contract tests

## Extension guide

- New industry: add `configs/industries/<name>.yaml`; do not add industry branches to core workflow code.
- New model: implement `ModelProvider` under `backend/app/llm/` and register it in `configs/models.yaml`.
- New data source: implement the connector protocol under `backend/app/tools/` and register it in configuration.
- New retrieval method: implement the retrieval protocol under `backend/app/retrieval/`.

## Development

```bash
python --version
pip install -r requirements.txt
python -m pytest
python -m uvicorn app.main:app --app-dir backend --reload
```

Dependencies are pinned to versions with Python 3.14 Windows wheels where native extensions are involved. The PostgreSQL adapter uses Psycopg 3 via `psycopg[binary,pool]`, which is the modern replacement for `psycopg2-binary` and supports Python 3.14 without requiring local PostgreSQL build tools.

This scaffold intentionally avoids Kafka, Kubernetes, and other production-only infrastructure while keeping boundaries ready for later upgrades.
