# HarborAI — Intelligent Port Operations Optimizer

**IBM Bank of Baroda AI Innovation Hackathon 2026**  
**Team:** Enigma  
**Problem Statement:** L1 — Container Congestion Predictor & Port Operations Optimiser  

---

## 1. Overview

HarborAI is a simulated port operations optimization platform designed to predict congestion bottlenecks, optimize berth and crane allocations, simulate what-if operational scenarios, and explain scheduling decisions through an AI copilot.

> [!IMPORTANT]
> **SIMULATED PORT OPERATIONS PLATFORM**  
> HarborAI operates entirely on synthetic data. It is **not** a live marine/AIS tracking platform or radar system. All telemetry and vessel arrival data are generated and evaluated within a simulated port environment.

### Core Architectural Separation of Concerns:
- **Machine Learning (XGBoost):** *"What is likely to happen?"* — Predicts turnaround times and congestion risk over a 72-hour horizon.
- **Optimization (Google OR-Tools):** *"What should we do?"* — Performs constraint-satisfaction mathematical optimization for berth assignments and quay crane allocations.
- **Simulation:** *"What happens if we do it?"* — Evaluates schedule execution and what-if parameter variations.
- **AI Copilot (watsonx / MCP):** *"How do we interact with and understand the system?"* — Answers operator queries, explains schedule decisions, and triggers optimization tools. *(LLMs never compute mathematical schedules directly)*.

---

## 2. Technology Stack

- **Architecture:** Modular Monolith
- **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS, Lucide React (Future: MapLibre GL JS, Recharts)
- **Backend:** Python 3.11+, FastAPI, Pydantic, SQLAlchemy, Alembic
- **Database:** PostgreSQL 16
- **ML (Future):** scikit-learn, XGBoost, pandas, NumPy
- **Optimization (Future):** Google OR-Tools
- **Infrastructure:** Docker, Docker Compose, GitHub Actions

---

## 3. Prerequisites

- **Node.js:** v18.0.0 or higher (v20+ recommended)
- **npm:** v9.0.0 or higher
- **Python:** 3.11 or higher
- **Docker & Docker Compose:** Optional for local containerized orchestration; required for containerized PostgreSQL

---

## 4. Environment Configuration

Copy `.env.example` to `.env` in the repository root:

```bash
cp .env.example .env
```

### Key Environment Variables:
| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://harborai:harborai@localhost:5432/harborai` |
| `DATABASE_URL_SYNC` | Sync PostgreSQL string for Alembic | `postgresql+psycopg2://harborai:harborai@localhost:5432/harborai` |
| `TEST_DATABASE_URL` | Dedicated PostgreSQL test database | `postgresql+asyncpg://harborai:harborai@localhost:5432/harborai_test` |
| `ENVIRONMENT` | Runtime environment (`development`, `production`) | `development` |
| `LOG_LEVEL` | Logging level (`DEBUG`, `INFO`, `WARNING`) | `INFO` |
| `SEED_DB` | Whether to seed empty database on startup | `true` |
| `RANDOM_SEED` | Deterministic random seed | `42` |
| `NEXT_PUBLIC_API_URL` | Frontend API backend target | `http://localhost:8000` |

---

## 5. Local Setup & Startup Guide

### A. Database (PostgreSQL)

Start PostgreSQL using Docker Compose:

```bash
docker compose up -d db
```

Or run a local PostgreSQL instance on port `5432` with username `harborai`, password `harborai`, and database `harborai`.

---

### B. Backend (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd src/backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Start the FastAPI development server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. Verify the health endpoint:
   ```bash
   curl http://localhost:8000/api/health
   # Returns: {"status":"ok","db":"connected"|"error","version":"0.1.0"}
   ```

---

### C. Frontend (Next.js)

1. Navigate to the frontend directory:
   ```bash
   cd src/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Next.js development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser. The application includes the dark operations-control shell with routes:
   - `/dashboard` — Operations monitoring overview
   - `/predictions` — Congestion & turnaround prediction preview
   - `/optimization` — Berth & crane allocation preview
   - `/digital-twin` — Port digital twin simulation preview
   - `/ai-copilot` — Operational assistant preview
   - `/settings` — System & simulator parameters

---

### D. Full-Stack Docker Startup

To run the full stack (PostgreSQL, Alembic migrations, FastAPI backend, and Next.js frontend) via Docker:

```bash
docker compose up --build
```

---

## 6. Testing

Run backend tests:

```bash
cd src/backend
pytest -v
```

Unit schema tests can run standalone; integration tests run against the dedicated PostgreSQL test database.

---

## 7. Current Implementation Status

See [`docs/implementation-status.md`](docs/implementation-status.md) for the phase-by-phase implementation progress.
- **Phase 0:** ✅ Complete — Repository / Environment Inspection + Project Foundation (Frontend Next.js shell & routing, Backend FastAPI & health check, Docker & environment configuration).
- **Phase 1:** ⏳ Pending — Domain model + database foundation.