# HarborAI — Implementation Status

**Team:** Enigma  
**Project:** HarborAI — Intelligent Port Operations Optimizer  
**Spec:** `docs/HARBORAI_SPEC.md`

---

## Phase Summary

| Phase | Status | Description |
|-------|--------|-------------|
| 0 | ✅ Complete | Repository inspection + implementation planning |
| 1 | 📋 Planned | Domain model + database foundation |
| 2 | ⏳ Pending | Port simulation engine |
| 3 | ⏳ Pending | Synthetic data generation |
| 4 | ⏳ Pending | ML congestion prediction |
| 5 | ⏳ Pending | OR-Tools optimization engine |
| 6 | ⏳ Pending | 72-hour planner |
| 7 | ⏳ Pending | Digital twin / scenario simulation |
| 8 | ⏳ Pending | Frontend dashboard + map |
| 9 | ⏳ Pending | AI copilot + tools/MCP |
| 10 | ⏳ Pending | Current vs optimized demo flow |
| 11 | ⏳ Pending | Testing, documentation, demo, submission |

---

## Phase 0 — COMPLETE

**What was done:**
- Repository inspected: bare template (only `README.md`, `docs/`, `AGENTS.md`)
- No existing source code, no `submission.yaml`, no GitHub Actions yet
- Master spec read and understood (`docs/HARBORAI_SPEC.md`)
- AGENTS.md written with full project context
- Mode-specific rules written (`.bob/rules-*/AGENTS.md`)
- Implementation status document created (this file)

**Key decisions recorded:**
- Modular monolith, no microservices
- All backend under `src/backend/`, frontend deferred to Phase 8
- PostgreSQL + SQLAlchemy ORM
- Alembic for migrations
- pytest for backend tests
- Docker Compose for local dev environment

---

## Phase 1 — PLANNED (Revised): Domain Model + Database Foundation

### Objective

Stand up a runnable FastAPI backend with PostgreSQL, all eight core SQLAlchemy domain
models, Pydantic read schemas, read-only REST endpoints, a health endpoint, deterministic
seed data, and passing tests.

**Deferred to later phases — do not introduce in Phase 1:**
simulation engine, synthetic data generation, ML, XGBoost, OR-Tools, 72-hour planner,
frontend, MapLibre, AI copilot, MCP, RAG, WebSockets, repositories layer,
service layer abstractions, background workers.

### Acceptance Criteria

- [ ] `GET /api/health` returns `200 {"status":"ok","db":"connected","version":"0.1.0"}`
- [ ] PostgreSQL connects via SQLAlchemy async engine
- [ ] All eight domain models exist in `database/models.py` with correct columns, FKs, and timestamps
- [ ] No circular FK between Vessel and Berth (single direction: `vessels.assigned_berth_id → berths.id`)
- [ ] Alembic initial migration generates the full schema from scratch (`alembic upgrade head`)
- [ ] Seed script populates all tables deterministically (seed `42`)
- [ ] All read endpoints return seeded data with correct shapes
- [ ] `pytest -v` passes — unit tests for schema validation + domain logic, integration tests for every endpoint
- [ ] `uvicorn main:app --reload` starts cleanly from `src/backend/`
- [ ] `.env.example` documents all required variables
- [ ] `implementation-status.md` updated to ✅ Complete at end of phase

---

### 1. Directory Structure

```
src/
└── backend/
    ├── main.py              # FastAPI app, router registration, lifespan startup (seed)
    ├── config.py            # pydantic-settings; reads .env
    ├── requirements.txt
    ├── Dockerfile
    │
    ├── database/
    │   ├── __init__.py
    │   ├── connection.py    # async engine, SessionLocal, get_db() dependency
    │   └── models.py        # all eight SQLAlchemy ORM models
    │
    ├── schemas/
    │   ├── __init__.py
    │   ├── vessel.py
    │   ├── berth.py
    │   ├── crane.py
    │   ├── yard.py
    │   ├── route.py
    │   ├── schedule.py
    │   ├── event.py
    │   └── port.py
    │
    ├── api/
    │   ├── __init__.py
    │   ├── health.py
    │   ├── vessels.py
    │   ├── berths.py
    │   ├── cranes.py
    │   ├── yard.py
    │   ├── routes.py
    │   └── port.py
    │
    ├── seed/
    │   ├── __init__.py
    │   └── seed_data.py     # deterministic seed, random.seed(42)
    │
    └── tests/
        ├── conftest.py      # test DB (SQLite in-memory), TestClient, seed fixture
        ├── unit/
        │   ├── test_vessel_schema.py    # Pydantic validation, status/priority enums
        │   ├── test_berth_schema.py     # length/draft field constraints
        │   └── test_yard_schema.py      # utilization bounds (0–1)
        └── integration/
            ├── test_health.py
            ├── test_vessels_api.py
            ├── test_berths_api.py
            ├── test_cranes_api.py
            └── test_port_status_api.py

migrations/
├── env.py
├── script.py.mako
└── versions/
    └── 0001_initial_schema.py

docker-compose.yml
.env.example
.gitignore
```

**Removed vs. prior plan:** `logging_config.py` (use stdlib default), `database/repositories.py`
(route handlers query directly in Phase 1 — repository abstraction added only when needed),
`schemas/common.py` (inline pagination where used rather than a shared abstraction layer).

---

### 2. Database Entities and Relationships

All tables: UUID primary key, `created_at TIMESTAMPTZ DEFAULT now()`,
`updated_at TIMESTAMPTZ DEFAULT now()` (updated via SQLAlchemy `onupdate`).

#### Vessel
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | VARCHAR(120) NOT NULL | |
| vessel_type | ENUM | `container` `bulk` `tanker` `ro_ro` `general` |
| length_m | FLOAT NOT NULL | metres |
| draft_m | FLOAT NOT NULL | metres |
| container_capacity | INTEGER | nullable |
| containers_to_handle | INTEGER | nullable |
| priority | ENUM | `low` `normal` `high` `critical` DEFAULT `normal` |
| scheduled_eta | TIMESTAMPTZ | nullable |
| predicted_eta | TIMESTAMPTZ | nullable |
| actual_eta | TIMESTAMPTZ | nullable |
| status | ENUM | `at_sea` `approaching` `waiting` `berth_assigned` `entering_berth` `at_berth` `crane_operations` `departing` `left_port` DEFAULT `at_sea` |
| destination | VARCHAR(120) | nullable |
| assigned_berth_id | UUID FK → berths.id | nullable — **one-way only** |
| expected_handling_duration_h | FLOAT | nullable |
| expected_departure | TIMESTAMPTZ | nullable |
| created_at / updated_at | TIMESTAMPTZ | |

#### Berth
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | VARCHAR(60) UNIQUE NOT NULL | |
| max_vessel_length_m | FLOAT NOT NULL | |
| max_draft_m | FLOAT NOT NULL | |
| capacity | INTEGER DEFAULT 1 | |
| available_from | TIMESTAMPTZ | nullable |
| occupied_until | TIMESTAMPTZ | nullable |
| status | ENUM | `available` `occupied` `maintenance` DEFAULT `available` |
| created_at / updated_at | TIMESTAMPTZ | |

> **No `current_vessel_id` FK on Berth.** The occupancy relationship is read from
> `vessels.assigned_berth_id`. This removes the circular FK and single source of truth ambiguity.

#### Crane
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | VARCHAR(60) UNIQUE NOT NULL | |
| status | ENUM | `available` `operating` `maintenance` DEFAULT `available` |
| available_from | TIMESTAMPTZ | nullable |
| handling_rate_containers_per_h | FLOAT NOT NULL | |
| current_berth_id | UUID FK → berths.id | nullable |
| created_at / updated_at | TIMESTAMPTZ | |

#### YardZone
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | VARCHAR(60) UNIQUE NOT NULL | |
| total_capacity | INTEGER NOT NULL | |
| occupied_capacity | INTEGER NOT NULL DEFAULT 0 | |
| created_at / updated_at | TIMESTAMPTZ | |

> `utilization` is a computed property on the Pydantic schema (`occupied / total`),
> not a stored column.

#### Route
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | VARCHAR(120) UNIQUE NOT NULL | e.g. `North Channel` |
| route_points | JSONB NOT NULL | GeoJSON LineString coordinates |
| nominal_travel_time_h | FLOAT NOT NULL | |
| capacity | INTEGER DEFAULT 1 | |
| congestion_factor | FLOAT DEFAULT 0.0 | 0–1 |
| risk_factor | FLOAT DEFAULT 0.0 | 0–1 |
| created_at / updated_at | TIMESTAMPTZ | |

#### Schedule
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| vessel_id | UUID FK → vessels.id NOT NULL | |
| berth_id | UUID FK → berths.id NOT NULL | |
| planned_start | TIMESTAMPTZ NOT NULL | |
| planned_end | TIMESTAMPTZ NOT NULL | |
| crane_ids | JSONB | list of crane UUIDs (denormalised for Phase 1) |
| yard_zone_id | UUID FK → yard_zones.id | nullable |
| route_id | UUID FK → routes.id | nullable |
| waiting_time_h | FLOAT DEFAULT 0.0 | |
| status | ENUM | `draft` `active` `completed` `cancelled` DEFAULT `draft` |
| created_at / updated_at | TIMESTAMPTZ | |

#### SimulationEvent
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| simulation_time | TIMESTAMPTZ NOT NULL | wall-clock time within simulation |
| event_type | VARCHAR(60) NOT NULL | e.g. `vessel_arrived` `berth_assigned` `crane_started` |
| vessel_id | UUID FK → vessels.id | nullable |
| berth_id | UUID FK → berths.id | nullable |
| old_state | JSONB | nullable |
| new_state | JSONB | nullable |
| metadata | JSONB | nullable — extensible payload |
| created_at | TIMESTAMPTZ DEFAULT now() | (no `updated_at` — events are immutable) |

#### PortState
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| simulation_time | TIMESTAMPTZ NOT NULL | |
| berth_utilization | FLOAT NOT NULL | 0–1 |
| crane_utilization | FLOAT NOT NULL | 0–1 |
| yard_utilization | FLOAT NOT NULL | 0–1 |
| waiting_vessel_count | INTEGER NOT NULL DEFAULT 0 | |
| active_vessel_count | INTEGER NOT NULL DEFAULT 0 | |
| upcoming_arrivals_24h | INTEGER NOT NULL DEFAULT 0 | |
| congestion_risk | ENUM | `low` `medium` `high` `critical` DEFAULT `low` |
| snapshot_metadata | JSONB | extensible KPI blob |
| created_at | TIMESTAMPTZ DEFAULT now() | (snapshot log — no `updated_at`) |

**Relationship summary:**

```
vessels.assigned_berth_id  →  berths.id          (M:1, nullable, one-way)
cranes.current_berth_id    →  berths.id          (M:1, nullable)
schedules.vessel_id        →  vessels.id         (M:1)
schedules.berth_id         →  berths.id          (M:1)
schedules.yard_zone_id     →  yard_zones.id      (M:1, nullable)
schedules.route_id         →  routes.id          (M:1, nullable)
simulation_events.vessel_id→  vessels.id         (M:1, nullable)
simulation_events.berth_id →  berths.id          (M:1, nullable)
port_states                — standalone snapshot table (no FK constraints)
```

---

### 3. API Endpoints (Phase 1 — read-only)

All list responses: `{"data": [...], "total": N}`.  
Single-resource responses: bare object.  
Errors: `{"detail": "...", "code": "..."}`.

```
GET  /api/health
     → 200 {"status":"ok", "db":"connected", "version":"0.1.0"}

GET  /api/vessels                 query: status, limit(=20), offset(=0)
GET  /api/vessels/{id}            → 200 VesselRead | 404

GET  /api/berths                  query: status
GET  /api/berths/{id}             → 200 BerthRead | 404

GET  /api/cranes                  query: status
GET  /api/cranes/{id}             → 200 CraneRead | 404

GET  /api/yard                    (all zones)
GET  /api/yard/{id}               → 200 YardZoneRead | 404

GET  /api/routes
GET  /api/routes/{id}             → 200 RouteRead | 404

GET  /api/port-status             → most recent PortState snapshot
```

`Schedule` and `SimulationEvent` are **not exposed via API in Phase 1** — tables are
created and seeded so Phase 2 can write to them immediately; read endpoints added in Phase 2.

---

### 4. Python Dependencies

```
# Runtime
fastapi==0.111.0
uvicorn[standard]==0.30.1
pydantic==2.7.1
pydantic-settings==2.3.0
sqlalchemy==2.0.30
alembic==1.13.1
asyncpg==0.29.0          # async PostgreSQL driver
psycopg2-binary==2.9.9   # sync driver for Alembic env.py
python-dotenv==1.0.1

# Testing only
pytest==8.2.0
pytest-asyncio==0.23.7
httpx==0.27.0            # async TestClient
aiosqlite==0.20.0        # SQLite in-memory test DB (avoids needing Postgres for unit tests)
```

Not installed until their phases: `scikit-learn`, `xgboost`, `ortools`, `pandas`, `numpy`,
`langchain`, any IBM watsonx SDK.

---

### 5. `.env.example`

```
# Database
DATABASE_URL=postgresql+asyncpg://harborai:harborai@localhost:5432/harborai
DATABASE_URL_SYNC=postgresql+psycopg2://harborai:harborai@localhost:5432/harborai

# App
ENVIRONMENT=development
LOG_LEVEL=INFO
SEED_DB=true        # seed on startup if tables are empty
RANDOM_SEED=42

# AI — deferred (Phase 9)
# IBM_WATSONX_API_KEY=
# IBM_WATSONX_PROJECT_ID=
# IBM_WATSONX_URL=
```

---

### 6. Seed Data (deterministic, `random.seed(42)`)

| Table | Records | Notes |
|-------|---------|-------|
| `berths` | 5 | varying max length / draft |
| `cranes` | 6 | varying handling rates, some assigned to berths |
| `yard_zones` | 4 | varying capacities, partial occupancy |
| `routes` | 3 | North Channel, South Channel, Deep-water Approach |
| `vessels` | 12 | mix of types, statuses, priorities, ETAs across 72 h |
| `schedules` | 4 | draft schedules linking vessels to berths |
| `simulation_events` | 0 | table exists; Phase 2 writes events |
| `port_states` | 1 | snapshot calculated from seeded vessel distribution |

---

### 7. Verification Steps

```bash
# Start Postgres
docker compose up -d db

# Apply schema
cd src/backend
alembic upgrade head

# Start API (separate terminal)
uvicorn main:app --reload --port 8000

# Smoke test
curl http://localhost:8000/api/health
# → {"status":"ok","db":"connected","version":"0.1.0"}

curl http://localhost:8000/api/vessels | python -m json.tool   # 12 records
curl http://localhost:8000/api/port-status | python -m json.tool

# Run all tests
pytest -v

# Single test
pytest tests/unit/test_vessel_schema.py -k "test_invalid_status_rejected" -v
```

---

### 8. Files That Will Be Created / Changed

| Path | Action |
|------|--------|
| `src/backend/main.py` | create |
| `src/backend/config.py` | create |
| `src/backend/requirements.txt` | create |
| `src/backend/Dockerfile` | create |
| `src/backend/database/__init__.py` | create |
| `src/backend/database/connection.py` | create |
| `src/backend/database/models.py` | create |
| `src/backend/schemas/__init__.py` | create |
| `src/backend/schemas/vessel.py` | create |
| `src/backend/schemas/berth.py` | create |
| `src/backend/schemas/crane.py` | create |
| `src/backend/schemas/yard.py` | create |
| `src/backend/schemas/route.py` | create |
| `src/backend/schemas/schedule.py` | create |
| `src/backend/schemas/event.py` | create |
| `src/backend/schemas/port.py` | create |
| `src/backend/api/__init__.py` | create |
| `src/backend/api/health.py` | create |
| `src/backend/api/vessels.py` | create |
| `src/backend/api/berths.py` | create |
| `src/backend/api/cranes.py` | create |
| `src/backend/api/yard.py` | create |
| `src/backend/api/routes.py` | create |
| `src/backend/api/port.py` | create |
| `src/backend/seed/__init__.py` | create |
| `src/backend/seed/seed_data.py` | create |
| `src/backend/tests/conftest.py` | create |
| `src/backend/tests/unit/test_vessel_schema.py` | create |
| `src/backend/tests/unit/test_berth_schema.py` | create |
| `src/backend/tests/unit/test_yard_schema.py` | create |
| `src/backend/tests/integration/test_health.py` | create |
| `src/backend/tests/integration/test_vessels_api.py` | create |
| `src/backend/tests/integration/test_berths_api.py` | create |
| `src/backend/tests/integration/test_cranes_api.py` | create |
| `src/backend/tests/integration/test_port_status_api.py` | create |
| `migrations/env.py` | create |
| `migrations/script.py.mako` | create |
| `migrations/versions/0001_initial_schema.py` | create |
| `docker-compose.yml` | create |
| `.env.example` | create |
| `.gitignore` | create |
| `docs/implementation-status.md` | update (this file) |
| `README.md` | update — project identity + quick-start |

---

## Known Issues / Blockers

None.

---

## Important Commands

```bash
cd src/backend && pytest -v
cd src/backend && pytest tests/unit/test_vessel_schema.py -k "test_invalid_status_rejected" -v
cd src/backend && alembic upgrade head
cd src/backend && uvicorn main:app --reload --port 8000
docker compose up
```
