# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project

**HarborAI — Intelligent Port Operations Optimizer** (IBM BoB AI Hackathon 2026, Team Enigma)

The authoritative specification is [`docs/HARBORAI_SPEC.md`](docs/HARBORAI_SPEC.md). Read it before making architectural decisions. Track progress in [`docs/implementation-status.md`](docs/implementation-status.md); read it at the start of every session to determine current phase.

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, TypeScript, Tailwind CSS, MapLibre GL JS, Recharts |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy |
| Database | PostgreSQL |
| ML | pandas, NumPy, scikit-learn, XGBoost |
| Optimization | Google OR-Tools |
| AI | IBM BoB (dev assistant) + watsonx/MCP at runtime |
| Infra | Docker, GitHub Actions |

## Repository Structure (target)

```
src/
  backend/     # FastAPI app — main.py + api/ database/ simulation/ prediction/ optimization/ ai/ schemas/
  frontend/    # Next.js app — app/ components/ lib/ public/ styles/
docs/          # problem-statement.md  solution-overview.md  architecture.md  setup-guide.md
demo/          # screenshots/  demo-video-link.txt  live-demo-url.txt
presentation/
submission.yaml
README.md
```

## Commands (to be set up per phase)

```bash
# Backend (from src/backend/)
uvicorn main:app --reload

# Backend tests
pytest                          # all tests
pytest tests/unit/test_vessel.py -k "test_state_transition"  # single test

# Frontend (from src/frontend/)
npm run dev
npm run build
npm run lint

# ML training
python -m prediction.train      # from src/backend/

# Docker (full stack)
docker compose up
```

## Critical Engineering Rules

These come directly from the spec and must not be violated:

1. **LLM ≠ optimizer.** Never let the AI agent compute schedules or berth assignments. Use OR-Tools for all mathematical decisions.
2. **No hardcoded metrics.** All comparison numbers (before/after optimization, model accuracy) must come from actual system output — never invented.
3. **Phase discipline.** Always work on the earliest incomplete phase. Never jump ahead. Each phase must leave the project runnable.
4. **Banned technologies:** Kafka, Redis, Celery, Kubernetes, event buses, microservices, LSTM/transformers for tabular data, WebSockets (for MVP), excessive LangChain/LangGraph abstractions.
5. **Synthetic data is fine** but must be clearly labeled as simulated/synthetic in the UI and docs.
6. **Never claim an IBM service is integrated** unless it is actually configured and working.

## Backend Code Conventions

- Business logic lives in domain modules (`simulation/`, `prediction/`, `optimization/`), **not** in route handlers (`api/`).
- Pydantic schemas live in `schemas/` and are the API contract.
- SQLAlchemy models live in `database/models.py`; queries in `database/repositories.py`.
- ML artifacts (trained model, preprocessor) persist to `prediction/artifacts/`.
- Use a deterministic random seed throughout for reproducibility.
- Environment config via `.env` (see `.env.example`; never commit secrets).

## Frontend Code Conventions

- All API types defined in `lib/types.ts` — do not hardcode operational values in components.
- Vessel animation is client-side interpolation along backend-provided route points; no WebSockets.
- Map is MapLibre GL JS with GeoJSON overlays for berths, routes, vessels. Do not call it a "radar system."

## Testing

- Backend unit tests cover vessel state transitions, berth compatibility, crane/yard constraints, route scoring.
- Integration tests cover API → database, API → simulation, API → prediction, API → optimizer.
- Use `pytest -k "<test_name>"` to run a single test.
