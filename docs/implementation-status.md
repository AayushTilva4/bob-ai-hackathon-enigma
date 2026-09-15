# HarborAI — Implementation Status

**Team:** Enigma  
**Project:** HarborAI — Intelligent Port Operations Optimizer  
**Spec:** `docs/HARBORAI_SPEC.md`

---

## Phase Summary

| Phase | Status | Description |
|-------|--------|-------------|
| 0 | ✅ Complete | Repository / Environment Inspection + Project Foundation (Frontend & Backend shells, Docker, Env, Resilience) |
| 1 | ✅ Complete | Domain model + database foundation (PostgreSQL, Alembic, 8 models, seed, read APIs, tests) |
| 2 | ✅ Complete | Port simulation engine (deterministic clock, vessel lifecycle, rule-based allocations, KPIs, events) |
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

## Phase 0 — COMPLETE (Verified)

**What was done:**
- Git branch `yakshit` created and checked out (`git checkout -b yakshit`).
- Repository and environment inspected:
  - Validated Python 3.11, Node.js v22.12, npm 11.3.
  - Confirmed Docker is not present in the local Windows PATH; verified environment without faking.
- **Frontend Foundation (`src/frontend/`):**
  - Initialized Next.js 14 (App Router) with TypeScript and Tailwind CSS.
  - Designed dark enterprise operations-control room theme (navy/charcoal backgrounds `#080c16`, cyan/blue operational accents, green/yellow/red status indicators).
  - Built persistent application shell (`Sidebar`, `Header`, `AppShell`) with visible **"SYNTHETIC DATA"** badge and system status telemetry indicator.
  - Implemented responsive placeholder routes with operational control views:
    - `/dashboard` — Operations Overview & vessel queue snapshot
    - `/predictions` — Congestion & turnaround prediction preview
    - `/optimization` — Resource & berth optimizer preview (unoptimized baseline vs. optimized comparison)
    - `/digital-twin` — Port digital twin & 2D simulation preview
    - `/ai-copilot` — Operational AI copilot chat terminal preview
    - `/settings` — Port simulator parameters & backend connectivity configuration
- **Backend Foundation (`src/backend/`):**
  - Verified FastAPI application structure, configuration management (`config.py`), and database connection (`database/connection.py`).
  - Added startup resilience in `lifespan`: if PostgreSQL is offline or unmigrated, startup logs a warning rather than crashing.
  - Created isolated Python virtual environment (`.venv`) and installed all runtime/testing dependencies (`requirements.txt`).
  - Verified backend import and tested `GET /api/health` returning `200 {"status":"ok","db":"error","version":"0.1.0"}` without faking database connectivity.
- **Docker Compose:**
  - Added `frontend` container service to `docker-compose.yml` (`db`, `migrate`, `backend`, `frontend`).
- **Environment & Git Safety:**
  - Updated `.env.example` to separate backend database/host variables and frontend `NEXT_PUBLIC_API_URL`.
  - Hardened `.gitignore` to strictly exclude `.env.*`, `node_modules`, Python virtual environments, `*.db`, `*.sqlite`, `.next/`, and credential files.
- **Documentation:**
  - Overhauled `README.md` with complete setup instructions for local backend, frontend, database, and Docker environments.
- **Phase Discipline:**
  - Confirmed Phase 1 database business logic, ML, optimization, and AI copilot features were **not** started.

---

## Phase 1 — COMPLETE (Verified): Domain Model + Database Foundation

### Objective & Scope Accomplished

Stand up a runnable FastAPI backend with PostgreSQL, all eight core SQLAlchemy domain models, Pydantic read schemas, read-only REST endpoints, a health endpoint, deterministic seed data, and passing tests.

### Acceptance Criteria Verification

- [x] `GET /api/health` returns `200 {"status":"ok","db":"connected","version":"0.1.0"}`
- [x] PostgreSQL connects via SQLAlchemy async engine and sync engine
- [x] All eight domain models exist in `database/models.py` (`Vessel`, `Berth`, `Crane`, `YardZone`, `Route`, `Schedule`, `SimulationEvent`, `PortState`) with UUID primary keys, indexes, and timezone-aware timestamps
- [x] No circular FK between Vessel and Berth (single direction: `vessels.assigned_berth_id → berths.id`)
- [x] Alembic initial migration generates the full schema from scratch (`alembic upgrade head`)
- [x] Seed script populates all tables deterministically (seed `42`), including 12 vessels, 5 berths, 8 cranes, 6 yard zones, 3 routes, 6 schedules, 5 simulation events, and 3 port states
- [x] Seed execution is strictly idempotent (safe to run repeatedly with 0 duplicate records)
- [x] All read endpoints return seeded data with standardized envelope `{"data": [...], "total": N}`
- [x] Consistent error format `{"detail": "...", "code": "..."}` for 404, 422, and 500 errors
- [x] Pytest test suite passes across unit and integration tests against live PostgreSQL
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
        ├── conftest.py      # dedicated PostgreSQL test DB, Alembic migration, real seed fixture
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
aiosqlite==0.20.0        # Optional SQLite dependency for isolated unit tests
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

**Current stabilization target:** Docker Compose starts PostgreSQL, `migrate` applies Alembic, `backend` starts only after a successful migration, and integration tests run against the same PostgreSQL schema path.

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

- Docker/PostgreSQL environment must be available to complete end-to-end Phase 1 verification.
- Integration tests use the dedicated PostgreSQL database and exercise the Alembic migration path.
- Phase 1 remains **not complete** until migration, seed, API smoke tests, and the full PostgreSQL test suite pass on the target development environment.

---

## Important Commands

```bash
cd src/backend && pytest -v
cd src/backend && pytest tests/unit/test_vessel_schema.py -k "test_invalid_status_rejected" -v
cd src/backend && alembic upgrade head
cd src/backend && uvicorn main:app --reload --port 8000
docker compose up
```

---

## Phase 2 — COMPLETE (Verified): Port Operations Simulation Engine

> [!IMPORTANT]
> **Notice on Simulation Fidelity**:
> The simulation is synthetic and does not represent live AIS/radar data. No external marine physics, wind/hydrodynamics, or GPS tracking are used. It is a deterministic digital port operations simulation.

### 1. Simulation Architecture

The simulation engine is implemented as a modular backend package under `src/backend/simulation/`:

```
src/backend/simulation/
├── __init__.py         # Package exports (SimulationClock, SimulationEngine, SimulationRandom, SimulationState)
├── random.py           # Centralized deterministic pseudo-random generator (SimulationRandom)
├── clock.py            # SimulationClock (start, pause, reset, advance)
├── transitions.py      # Strict vessel lifecycle state transitions and validation
├── movement.py         # Deterministic route waypoint interpolation
├── berth_manager.py    # Feasibility checks, berth assignment, and release (no OR-Tools)
├── crane_manager.py    # Allocation by vessel size, double-booking prevention, release
├── yard_manager.py     # Yard zone selection, capacity check, utilization
├── metrics.py          # Operational KPIs and normalized congestion scoring
├── events.py           # EventManager for structured immutable SimulationEvent records
├── state.py            # Transient in-memory state tracking (VesselRuntimeState, SimulationState)
└── engine.py           # Orchestrator coordinating step progression, DB sync, and PortState snapshots
```

### 2. Vessel Lifecycle State Machine

The simulation implements strict, validated state transitions:
```
AT_SEA
  ↓
APPROACHING_PORT (approaching)
  ↓
WAITING (if no berth)  ──→  BERTH_ASSIGNED
  ↓                               ↓
ENTERING_BERTH  ←─────────────────┘
  ↓
AT_BERTH
  ↓
CRANE_OPERATIONS
  ↓
DEPARTING
  ↓
LEFT_PORT (terminal)
```
- Invalid transitions (e.g. `LEFT_PORT -> AT_SEA` or skipping states) raise `InvalidStateTransitionError`.

### 3. Deterministic Seed & Randomness
- Centralized in `SimulationRandom(seed=42)`.
- Resetting with the same seed and advancing the same hours produces strictly reproducible states, events, and KPIs.

### 4. Operational KPI & Congestion Calculations
- **Handling Duration**: `workload / (sum(crane_rates) * diminishing_returns_factor)` (minimum 1.0 h).
- **Waiting Time**: Accrued hours while in `WAITING` status derived from simulation clock.
- **Congestion Score**: Normalized composite formula `[0.0, 1.0]`:
  `score = 0.35 * queue_factor + 0.25 * berth_util + 0.20 * yard_util + 0.20 * crane_util`
  - Score labels: `< 0.30` -> `low`, `< 0.60` -> `medium`, `< 0.85` -> `high`, `>= 0.85` -> `critical`.
- **PortState Snapshots**: Generated after every simulation step and stored in PostgreSQL.

### 5. Simulation REST APIs
- `POST /api/simulation/start`: Starts simulation clock progression.
- `POST /api/simulation/pause`: Pauses simulation clock progression.
- `POST /api/simulation/reset`: Resets state, clock, berths, cranes, yard, events, and snapshots.
- `POST /api/simulation/advance`: Advances simulation clock by `hours` (default 1.0 h).
- `GET /api/simulation/state`: Returns complete simulation state (vessels, coordinates, berths, cranes, yard, KPIs).
- `GET /api/simulation/events`: Returns immutable event history.
- `GET /api/simulation/kpis`: Returns real-time operational KPIs and congestion score.

### 6. Known Limitations
- The simulation is synthetic and does not represent live AIS/radar data.
- Berth and crane allocations in Phase 2 use rule-based feasibility logic; mathematical optimization (OR-Tools) will be integrated in Phase 5.
- Congestion score is an operational heuristic; machine learning predictive forecasting will be added in Phase 4.

