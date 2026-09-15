"You are working inside the existing official IBM BoB hackathon repository.

First inspect the complete repository before making major changes.

Read:
- README.md
- submission.yaml
- all existing files/folders
- GitHub Actions/workflows
- any existing documentation

Do not delete or replace official template files without understanding their purpose.

This repository belongs to Team Enigma and the project is HarborAI.

Use the full HarborAI implementation specification provided below as the source of truth.

IMPORTANT:
Do not attempt to build the entire project in one pass.

Work phase-by-phase.

First complete:
PHASE 0 — repository inspection and implementation planning
PHASE 1 — domain model + database foundation

Before coding:
1. Inspect the repository.
2. Determine what the template already provides.
3. Create/update docs/implementation-status.md.
4. Decide the minimal repository structure required by the HarborAI specification.
5. Preserve the hackathon submission structure.

Then implement Phase 1 completely:
- PostgreSQL configuration
- SQLAlchemy setup
- Pydantic schemas
- core domain models
- database connection
- basic FastAPI application
- health endpoint
- initial vessel/berth/crane/yard/port-state APIs
- environment configuration
- basic database initialization/migration approach

Do NOT implement ML, optimization, AI copilot, RAG, or frontend yet.

After implementation:
- run the backend
- verify database connectivity
- run relevant tests
- fix errors
- update docs/implementation-status.md
- stop.

Do not proceed to Phase 2 until Phase 1 is actually working.

from pathlib import Path

prompt = r'''# MASTER IMPLEMENTATION PROMPT — HARBORAI
## IBM BoB AI Innovation Hackathon 2026 — Team Enigma

You are the lead software architect, ML engineer, backend engineer, frontend engineer, optimization engineer, and integration engineer for this project.

Your job is to take the existing hackathon repository and build the complete HarborAI prototype from the current state to a submission-ready working system.

Do not treat this as a brainstorming task. Treat it as an implementation task.

The project must be built incrementally in phases, but this single prompt contains the complete product requirements, architecture, technical decisions, implementation rules, acceptance criteria, and end-state. Do not repeatedly ask the user to restate requirements.

==================================================
0. PRODUCT
==================================================

Team name:
Enigma

Product name:
HarborAI — Intelligent Port Operations Optimizer

Problem:
Port operators must coordinate vessel arrivals, berth availability, cranes, yard capacity, and changing operational conditions. Congestion is often discovered reactively. The system should help operators understand future operational pressure, plan proactively, optimize resources, and compare operational plans.

Core concept:

KNOWN DATA
→ vessel schedules, vessel characteristics, berth constraints, crane availability, yard capacity, port rules

PREDICTION
→ estimate uncertain/future operational conditions and congestion risk

OPTIMIZATION
→ determine the best feasible berth/crane/routing/scheduling decisions

SIMULATION
→ test what happens when a plan is executed or conditions change

AI COPILOT
→ explain the system, invoke tools, answer operator questions, and perform what-if analysis

Do NOT make the LLM responsible for mathematical scheduling decisions.

The separation is mandatory:

ML:
"What is likely to happen?"

Optimization:
"What should we do?"

Simulation:
"What happens if we do it?"

LLM/Agent:
"How do I interact with and understand the system?"

==================================================
1. IMPLEMENTATION PHILOSOPHY
==================================================

Build a modular monolith. Do not create unnecessary microservices.

Prioritize:
1. working end-to-end flow
2. realistic operational logic
3. actual ML where useful
4. actual optimization
5. explainability
6. polished demo
7. documentation and validation

Avoid unnecessary technologies unless there is a concrete implementation need.

Do NOT introduce:
- Kafka
- Redis
- Celery
- Kubernetes
- event buses
- microservices
- deep-learning models
- LSTM/transformers for tabular prediction
- real AIS infrastructure
- complicated real-time streaming
- excessive LangChain/LangGraph abstractions
- WebSockets for the initial MVP

Client-side vessel animation and ordinary REST APIs are sufficient for the prototype.

The system is a simulated port operations platform, not a real maritime navigation or live AIS tracking system.

Synthetic data is acceptable and should be presented honestly as simulated/synthetic data.

==================================================
2. TARGET ARCHITECTURE
==================================================

Frontend:
- Next.js
- TypeScript
- Tailwind CSS
- MapLibre GL JS
- Recharts

Backend:
- Python
- FastAPI
- Pydantic
- SQLAlchemy

Database:
- PostgreSQL

ML:
- pandas
- NumPy
- scikit-learn
- XGBoost

Optimization:
- Google OR-Tools

AI:
- IBM BoB
- MCP-style tool integration where supported by the actual environment
- IBM-supported AI/watsonx technology actually configured in the final implementation

Infrastructure:
- Docker
- GitHub Actions

Do not claim an IBM technology was used until it is actually configured and working.

==================================================
3. REPOSITORY REQUIREMENTS
==================================================

Preserve the official hackathon repository/template structure.

Expected high-level structure:

src/
  frontend/
  backend/

docs/
  problem-statement.md
  solution-overview.md
  architecture.md
  setup-guide.md

demo/
  screenshots/
  demo-video-link.txt
  live-demo-url.txt

presentation/
submission.yaml
README.md

Do not delete or overwrite official template files without understanding their purpose.

Inspect the existing repository before making structural changes.

If the template already provides files/folders, adapt to them rather than creating conflicting alternatives.

==================================================
4. DEVELOPMENT PHASES
==================================================

Implement the project in the following phases.

PHASE 0 — REPOSITORY AND ENVIRONMENT INSPECTION
PHASE 1 — DOMAIN MODEL + DATABASE
PHASE 2 — PORT SIMULATION ENGINE
PHASE 3 — SYNTHETIC DATA GENERATION
PHASE 4 — ML CONGESTION PREDICTION
PHASE 5 — OPTIMIZATION ENGINE
PHASE 6 — 72-HOUR PLANNER
PHASE 7 — DIGITAL TWIN / SCENARIO SIMULATION
PHASE 8 — FRONTEND DASHBOARD + MAP
PHASE 9 — AI COPILOT + TOOLS/MCP
PHASE 10 — CURRENT VS OPTIMIZED DEMO FLOW
PHASE 11 — TESTING, DOCUMENTATION, DEMO, SUBMISSION VALIDATION

Do not jump ahead and create disconnected mock features.

Each phase must leave the project runnable.

==================================================
5. PHASE 0 — INSPECT FIRST
==================================================

Before writing major code:

1. Inspect all current files.
2. Inspect package files and environment configuration.
3. Inspect submission.yaml.
4. Inspect GitHub Actions.
5. Inspect existing README and docs.
6. Identify existing frontend/backend scaffolding.
7. Avoid unnecessary rewrites.
8. Create a short implementation plan in docs/architecture.md if it does not exist.

After inspection, proceed with implementation without asking the user to re-explain the project.

==================================================
6. PHASE 1 — DOMAIN MODEL
==================================================

Create these core entities.

VESSEL
Fields should include, as appropriate:
- id
- name
- vessel_type
- length
- draft
- container_capacity
- containers_to_handle
- priority
- scheduled_eta
- predicted_eta
- actual_eta when simulated
- destination
- status
- current_position
- assigned_berth
- assigned_route
- expected_handling_duration
- expected_departure
- created_at / timestamps as needed

BERTH
Fields:
- id
- name
- max_vessel_length
- max_draft
- capacity
- available_from
- occupied_until
- status
- current_vessel_id
- supported_cranes

CRANE
Fields:
- id
- name
- status
- available_from
- handling_rate
- current_berth
- capabilities if needed

YARD ZONE
Fields:
- id
- name
- total_capacity
- occupied_capacity
- utilization
- supported_container_types if implemented

ROUTE
Fields:
- id
- name
- route_points / GeoJSON path
- nominal_travel_time
- capacity
- congestion_factor
- risk_factor

SCHEDULE
Fields:
- vessel_id
- berth_id
- start_time
- end_time
- crane_assignment
- yard_zone
- route
- waiting_time
- status

SIMULATION EVENT
Fields:
- timestamp
- event_type
- vessel_id
- berth_id if relevant
- old_state
- new_state
- metadata

PORT STATE
Track:
- current simulation time
- berth utilization
- crane utilization
- yard utilization
- waiting vessels
- active vessels
- upcoming arrivals
- congestion risk
- other dashboard metrics

Use relational relationships and constraints through PostgreSQL/SQLAlchemy.

==================================================
7. PHASE 2 — PORT SIMULATION ENGINE
==================================================

Implement a deterministic and reproducible port simulation.

Vessel lifecycle:

AT_SEA
→ APPROACHING_PORT
→ WAITING/ANCHOR
→ BERTH_ASSIGNED
→ ENTERING_BERTH
→ AT_BERTH
→ CRANE_OPERATIONS
→ DEPARTING
→ LEFT_PORT

Simulation responsibilities:
- advance simulation time
- update vessel position along predefined route points
- update vessel state
- assign/release berth occupancy
- allocate/release cranes
- update yard utilization
- calculate waiting time
- calculate handling time
- create simulation events
- update port KPIs

Use predefined port approach routes rather than real marine physics.

Vessel movement:
- backend stores route and timing
- frontend interpolates vessel position for smooth animation
- if schedule changes, the frontend receives the updated route/timing and adjusts the animation

Simulation must support:
- start
- pause
- reset
- advance
- run for a configured duration

Use a deterministic random seed for dataset/demo reproducibility.

==================================================
8. PHASE 3 — SYNTHETIC DATA GENERATOR
==================================================

Generate realistic synthetic operational data instead of random meaningless values.

Generate many historical scenarios containing:
- vessel arrival schedules
- actual arrival deviations
- container volumes
- vessel characteristics
- berth availability
- crane availability
- handling durations
- waiting times
- berth utilization
- crane utilization
- yard utilization
- queue length
- operational delays
- congestion labels / congestion measures
- route conditions if used

Generate enough variability to avoid a trivial model.

Create:
- generator
- schema validation
- CSV/Parquet export as practical
- training dataset creation command
- seed control
- documented assumptions

The synthetic generator should be driven by operational relationships.

Examples:
- more containers generally increase handling time
- more cranes generally reduce handling time, within reasonable diminishing returns
- high berth utilization increases waiting probability
- high crane utilization increases delays
- high yard utilization creates operational pressure
- clustered arrivals create queue pressure

Do not create labels using only a direct copy of one input threshold such that the ML task becomes meaningless.

==================================================
9. PHASE 4 — ML MODEL
==================================================

Build ONE strong and defensible primary ML model first.

Primary task:
Predict future port congestion risk.

The model should estimate:
congestion_probability between 0 and 1

and provide a risk label:
LOW / MEDIUM / HIGH / CRITICAL

Possible features:
- vessels_arriving_next_6h
- vessels_arriving_next_12h
- vessels_arriving_next_24h
- total_incoming_containers
- berth_utilization
- available_berths
- crane_utilization
- available_cranes
- yard_utilization
- queue_length
- average_handling_time
- recent_waiting_time
- high_priority_vessel_count
- other meaningful features generated by the simulator

Do not use irrelevant features.

MODEL:
- baseline: Logistic Regression or simple tree baseline
- main model: XGBoost classifier
- preprocessing must be reproducible
- train/validation/test split must be defined
- persist trained model and preprocessing artifacts
- implement inference service
- expose FastAPI endpoint

Example endpoint:
POST /api/prediction/congestion

Input:
structured port state/features

Output:
{
  "congestion_probability": 0.83,
  "risk_level": "HIGH",
  "prediction_horizon_hours": 12,
  "top_factors": [...]
}

Evaluation:
- precision
- recall
- F1
- ROC-AUC
- confusion matrix

Because missing a real congestion event can be costly, pay attention to recall.

Explainability:
Return top contributing features using feature importance or SHAP if SHAP can be added cleanly.

Do not fabricate model metrics.
Only display metrics generated by the actual trained model.

OPTIONAL MODEL:
Only after the congestion model is working, add a handling-time regression model if time permits.

Handling-time target:
expected_handling_duration

Possible features:
- vessel type
- container volume
- cranes assigned
- historical handling performance
- operational conditions

If implemented, expose:
POST /api/prediction/handling-time

Do not let an unfinished optional model block the rest of the project.

==================================================
10. PHASE 5 — OPTIMIZATION ENGINE
==================================================

Implement actual optimization using Google OR-Tools.

The optimizer is responsible for decisions, not prediction.

Inputs:
- vessels
- expected/predicted ETA
- expected handling durations
- berth constraints
- crane availability
- yard capacity
- route information
- vessel priorities
- planning horizon

Decisions:
- berth assignment
- start time
- end time
- crane allocation
- yard assignment
- route selection where appropriate

Objective:
minimize a weighted combination of:
- total vessel waiting time
- late departure penalties
- berth idle time
- crane idle time
- yard overload penalty
- route congestion/risk penalty

Constraints:
- vessel length must fit berth
- draft must fit berth
- berth cannot handle overlapping incompatible assignments
- crane count cannot exceed availability
- crane availability windows must be respected
- yard capacity cannot be exceeded
- vessel operations must occur after arrival
- handling duration must be respected
- high-priority vessels receive appropriate preference
- route capacity and restrictions must be respected if route optimization is used

Return a structured optimization result.

Example:
POST /api/optimization/run

Return:
- objective score
- vessel assignments
- berth assignments
- crane assignments
- routes
- start/end times
- waiting time
- explanation metadata
- comparison with current schedule

Do not use the LLM to solve this mathematical problem.

==================================================
11. PHASE 6 — ROUTE OPTIMIZATION
==================================================

Use a small number of predefined port approach routes.

Example:
- North Channel
- South Channel
- Deep-water Approach

Each route can have:
- nominal time
- capacity
- congestion factor
- risk factor

Compute an operational route score.

A possible formulation:
route_cost =
travel_time
+ congestion_penalty
+ risk_penalty

Choose the best feasible route.

Do not attempt global maritime navigation.

==================================================
12. PHASE 7 — 72-HOUR PLANNER
==================================================

Generate a schedule over a 72-hour horizon.

Break the horizon into planning windows as appropriate:
0–6h
6–12h
12–24h
24–48h
48–72h

For each vessel:
- expected arrival
- expected handling duration
- feasible berths
- predicted resource pressure
- berth assignment
- crane assignment
- yard requirement
- expected departure
- waiting time

Return a machine-readable 72-hour plan.

Expose:
POST /api/planning/72h

The final system must be able to show the plan visually.

==================================================
13. PHASE 8 — DIGITAL TWIN + WHAT-IF SIMULATION
==================================================

Provide two important scenarios.

SCENARIO A:
current operational plan

SCENARIO B:
optimized plan

Allow comparison of:
- total waiting time
- average waiting time
- number of delayed vessels
- peak berth utilization
- peak crane utilization
- peak yard utilization
- congestion probability/risk

Implement at least two what-if scenarios:

1. Vessel delay:
"What happens if vessel X arrives 2 hours late?"

2. Berth disruption:
"What happens if Berth 3 becomes unavailable?"

Preferred flow:
user request
→ scenario parameter
→ run simulation
→ recompute relevant schedule/metrics
→ return structured comparison
→ AI explains the result

==================================================
14. PHASE 9 — FRONTEND
==================================================

Build a polished dark-mode operations dashboard inspired by a modern port control center.

Main UI areas:

1. Header
- product name
- simulation clock
- system status
- AI copilot entry

2. KPI cards
- active vessels
- vessels waiting
- berth utilization
- crane utilization
- yard utilization
- congestion risk

3. Main port map
Use MapLibre GL JS.

Show:
- port geometry
- berths
- approach routes
- vessels
- vessel status
- selected vessel details
- congestion overlays if practical

Use a geographic basemap plus custom GeoJSON operational overlays.

Do not call the map a radar system.
Use terms such as:
"Port Operations Map"
"Live Port Digital Twin"

4. Forecast panel
Show:
- congestion probability
- forecast horizon
- high-risk berths/times
- top contributing factors

5. Schedule panel
Show:
- current schedule
- optimized schedule
- 72-hour timeline

6. Optimization panel
Buttons/actions:
- Run Optimization
- Apply Optimized Plan
- Compare Plans

7. Scenario panel
Inputs/actions:
- delay vessel
- disable berth
- run scenario
- compare result

8. AI Copilot
Chat panel with:
- natural-language questions
- tool-driven answers
- structured recommendation cards where appropriate

Vessel animation:
- simulate movement along predefined route
- interpolate smoothly in browser
- do not require WebSockets

==================================================
15. PHASE 10 — AI COPILOT + TOOLS
==================================================

Expose system functionality as structured tools.

Core tools:
- get_port_status
- get_vessel_status
- get_berth_status
- get_crane_status
- get_congestion_forecast
- get_72h_plan
- run_optimization
- get_optimization_result
- simulate_scenario
- compare_plans

The AI agent can:
- understand natural-language intent
- choose appropriate tools
- call tools
- interpret returned data
- answer grounded questions
- explain recommendations
- summarize the 72-hour situation

Example user questions:
"Why will congestion peak tonight?"
"Why did the optimizer move Horizon?"
"What happens if Horizon arrives two hours late?"
"What if Berth 3 becomes unavailable?"
"Which berth is the biggest bottleneck?"
"Give me the next 24-hour operations brief."

Agent behavior:
1. Do not fabricate operational facts.
2. Use tools for current/derived operational data.
3. Explain based on actual returned results.
4. Never invent optimization output.
5. Do not directly override optimization constraints.
6. Keep answers concise but operationally useful.

==================================================
16. PHASE 11 — OPTIONAL RAG
==================================================

RAG is optional and should only be added after the core system works.

Knowledge base may contain:
- berth specifications
- vessel restrictions
- crane specifications
- operating rules
- safety/operational procedures

Use retrieval for domain knowledge, not numerical optimization.

Example:
"Why can't Horizon use Berth 5?"

The system retrieves:
Berth 5 max vessel length
Horizon vessel length

Then explains the incompatibility.

Do not let RAG become the project's centerpiece.

==================================================
17. API DESIGN
==================================================

Use clean REST APIs.

Suggested endpoints:

GET  /api/health
GET  /api/vessels
GET  /api/vessels/{id}
GET  /api/berths
GET  /api/cranes
GET  /api/yard
GET  /api/port-status

POST /api/simulation/start
POST /api/simulation/pause
POST /api/simulation/reset
POST /api/simulation/advance

POST /api/prediction/congestion
POST /api/prediction/handling-time      # optional

POST /api/optimization/run
GET  /api/optimization/result

POST /api/planning/72h

POST /api/scenarios/run
POST /api/scenarios/compare

POST /api/copilot/query

Adjust names if existing template conventions are different, but keep the separation clear.

==================================================
18. BACKEND CODE ORGANIZATION
==================================================

Preferred structure:

src/backend/
  main.py

  api/
    vessels.py
    berths.py
    cranes.py
    port.py
    simulation.py
    prediction.py
    optimization.py
    planning.py
    scenarios.py
    copilot.py

  database/
    connection.py
    models.py
    repositories.py

  simulation/
    engine.py
    vessel.py
    berth.py
    crane.py
    yard.py
    events.py
    routes.py

  prediction/
    features.py
    dataset.py
    train.py
    infer.py
    explain.py
    artifacts/

  optimization/
    berth_optimizer.py
    crane_optimizer.py
    route_optimizer.py
    planner.py
    objectives.py
    constraints.py

  ai/
    agent.py
    prompts.py
    tools.py
    schemas.py

  schemas/
    vessel.py
    port.py
    prediction.py
    optimization.py
    simulation.py

  config.py
  logging_config.py
  requirements.txt

Use clear boundaries.
Keep business logic out of route handlers.

==================================================
19. FRONTEND ORGANIZATION
==================================================

Preferred structure:

src/frontend/
  app/
  components/
    dashboard/
    map/
    vessels/
    schedule/
    forecast/
    optimization/
    scenarios/
    copilot/
    ui/
  lib/
    api.ts
    types.ts
    simulation.ts
  public/
  styles/

Use strongly typed API models.

Do not hardcode operational values into UI components when they should come from APIs.

==================================================
20. DATA / SIMULATION REALISM
==================================================

The port should not feel random.

Use:
- realistic time ranges
- vessel classes
- varying container volumes
- different handling rates
- different berth capabilities
- crane constraints
- realistic queue formation
- varied demand peaks
- resource contention
- reproducible scenarios

Create one "demo stress scenario" specifically designed to produce visible congestion.

Create one "normal scenario."

Create a predictable "optimized scenario" where the optimizer measurably improves the plan.

Do not cherry-pick fake before/after numbers in the UI. Calculate them from actual simulation/optimization output.

==================================================
21. DEMO SCENARIO
==================================================

The primary demo journey should be:

STEP 1
Open dashboard.
Port looks mostly normal.

STEP 2
System shows future demand and congestion forecast.

Example presentation only:
"High congestion risk expected between 20:00 and 01:00."

STEP 3
Operator opens the forecast and sees:
- upcoming vessel cluster
- high berth utilization
- high crane utilization
- yard pressure
- top contributing factors

STEP 4
Operator clicks:
RUN AI OPTIMIZATION

STEP 5
Optimizer produces:
- berth reassignments
- crane reallocations
- route recommendations
- 72-hour plan

STEP 6
Click:
COMPARE PLANS

Show real calculated changes.

STEP 7
Run the optimized simulation.

STEP 8
Show reduced waiting / delays / resource pressure.

STEP 9
Operator asks copilot:
"Why was Horizon moved?"

Agent retrieves optimization data and explains.

STEP 10
Operator asks:
"What happens if Horizon arrives two hours late?"

Agent runs the scenario and explains the new impact.

This is the primary end-to-end demo path.

==================================================
22. EXPLAINABILITY
==================================================

Every prediction and optimization result should provide machine-readable explanation metadata.

Prediction example:
{
  "risk_level": "HIGH",
  "probability": 0.83,
  "top_factors": [
    {"feature": "arrivals_next_6h", "impact": "..."},
    {"feature": "berth_utilization", "impact": "..."}
  ]
}

Optimization example:
{
  "vessel": "Horizon",
  "old_berth": "B2",
  "new_berth": "B4",
  "reasons": [
    "B2 would remain occupied beyond Horizon's arrival window",
    "B4 has compatible dimensions",
    "assignment reduces expected queue delay"
  ]
}

These explanations must be derived from actual system data.

==================================================
23. ENVIRONMENT VARIABLES
==================================================

Create:
.env.example

Likely values:
DATABASE_URL
AI_API_KEY
IBM-related configuration required by the actual chosen integration
MODEL_PATH if useful
ENVIRONMENT

Never commit secrets.

Add appropriate .gitignore entries.

==================================================
24. ERROR HANDLING
==================================================

Implement useful errors.

Examples:
- invalid vessel ID
- incompatible berth
- unavailable crane
- insufficient yard capacity
- invalid scenario
- optimization infeasible
- ML model unavailable
- AI service unavailable

The frontend should show actionable error messages.

==================================================
25. TESTING
==================================================

At minimum implement:

Backend unit tests for:
- vessel state transitions
- berth compatibility
- crane availability
- yard capacity
- route scoring
- prediction input validation
- optimization feasibility
- scenario calculations

Integration tests for:
- API → database
- API → simulation
- API → prediction
- API → optimizer

Frontend smoke test:
- dashboard loads
- API connection works
- vessel data renders
- optimization action works
- copilot panel loads

Do not add a huge testing framework for its own sake.

==================================================
26. DOCUMENTATION
==================================================

Create/update:

docs/problem-statement.md
- explain the operational problem
- user/persona
- pain points
- challenge alignment

docs/solution-overview.md
- explain HarborAI
- prediction → optimization → simulation → AI flow

docs/architecture.md
- architecture diagram in Mermaid if appropriate
- component responsibilities
- data flow
- APIs
- model flow
- optimization flow
- AI tool flow

docs/setup-guide.md
- prerequisites
- exact install commands
- environment variables
- database setup
- model setup
- run commands
- verification steps
- common errors

The setup guide must be tested from a clean environment.

==================================================
27. README
==================================================

Use the existing official README template.

Final README should contain:
- HarborAI title
- Team Enigma
- AI track
- team details
- problem statement
- solution
- key features
- tech stack
- repository structure
- exact run instructions
- demo links/files
- honest limitations
- strongest technical point

Do not claim unsupported features.

==================================================
28. IBM BOB INTEGRATION
==================================================

IBM BoB must be genuinely used during development and, where appropriate, surfaced in the solution workflow.

Do not simply mention "IBM Bob" in the README.

Use Bob for:
- codebase understanding
- implementation assistance
- code review
- architecture support
- debugging
- integration assistance

Where hackathon rules and available services support a runtime AI integration, configure the actual supported IBM AI technology and document it accurately.

Never claim a service is integrated unless the project actually uses it.

==================================================
29. GITHUB / SUBMISSION
==================================================

Maintain:
- public official-template repository
- meaningful commit history
- no secrets
- clean README
- working GitHub Actions
- submission.yaml correctly populated
- demo artifacts
- screenshots
- presentation

Before submission:
- install from clean state
- run backend
- run frontend
- verify database
- verify ML model
- verify optimization
- verify simulation
- verify AI tool flow
- run GitHub Actions
- ensure green validation
- ensure README links work

==================================================
30. IMPLEMENTATION STRATEGY FOR TOKEN EFFICIENCY
==================================================

You must minimize unnecessary context and repeated work.

Rules:

1. Read files once when possible.
2. Reuse existing code instead of recreating it.
3. Do not regenerate entire files when patching a small section.
4. Do not create duplicate implementations.
5. Keep a concise implementation state in:
   docs/implementation-status.md

That file should contain:
- completed phases
- current phase
- next phase
- known issues
- important commands
- important architecture decisions

At the beginning of a new task:
1. inspect implementation-status.md
2. inspect only relevant files
3. implement the next required change
4. run targeted tests
5. update implementation-status.md

Do not repeatedly explain the entire architecture in generated output.

==================================================
31. PHASE ACCEPTANCE CRITERIA
==================================================

PHASE 1 DONE WHEN:
- database connects
- core models exist
- basic APIs work

PHASE 2 DONE WHEN:
- simulation can advance
- vessels change state
- resources are occupied/released

PHASE 3 DONE WHEN:
- reproducible synthetic dataset exists
- data has meaningful variation
- training command works

PHASE 4 DONE WHEN:
- real model trains
- evaluation metrics exist
- inference API works
- prediction explanation exists

PHASE 5 DONE WHEN:
- optimizer produces feasible schedules
- berth constraints work
- crane constraints work
- yard constraints work

PHASE 6 DONE WHEN:
- 72-hour schedule is generated and retrievable

PHASE 7 DONE WHEN:
- current vs optimized scenario can be simulated and compared

PHASE 8 DONE WHEN:
- dashboard displays actual backend data
- map displays vessels/berths
- simulation animation works

PHASE 9 DONE WHEN:
- AI copilot can call system tools
- answers are grounded in tool outputs
- at least two what-if scenarios work

PHASE 10 DONE WHEN:
- primary demo journey works end-to-end

PHASE 11 DONE WHEN:
- repository is submission-ready
- setup guide works
- screenshots/demo exist
- validation passes

==================================================
32. PRIORITY RULE FOR LIMITED TIME
==================================================

If time becomes limited, prioritize in this exact order:

P0:
- backend
- simulation
- synthetic data
- ML prediction
- OR-Tools optimization
- one 72-hour plan
- frontend dashboard
- current vs optimized comparison

P1:
- AI copilot with tool calling
- what-if scenarios
- explainability

P2:
- polished animations
- route optimization
- handling-time secondary model
- richer charts
- RAG

P3:
- anything that does not improve the core demo

Never sacrifice a functioning core flow for optional features.

==================================================
33. IMPORTANT ENGINEERING CONSTRAINTS
==================================================

Do not:
- hardcode optimized output as if it came from the optimizer
- hardcode ML prediction numbers into the UI
- let the LLM invent operational facts
- fake model accuracy
- fake real-time data
- claim live AIS
- claim production-grade port integration
- add irrelevant AI technologies just for marketing

Do:
- use deterministic simulation
- use real model inference
- use real OR-Tools optimization
- calculate comparisons from real outputs
- keep synthetic data clearly labeled
- expose structured data to the AI agent
- make the demo reproducible

==================================================
34. FINAL QUALITY BAR
==================================================

The finished system should feel like a coherent product, not a collection of demos.

The judge should be able to understand:

1. What problem exists?
2. What does HarborAI predict?
3. What does the optimizer decide?
4. How does simulation validate the decision?
5. What role does AI play?
6. What changed after optimization?
7. Why is the architecture technically credible?

A successful final flow should be:

PORT STATE
→ PREDICTION
→ OPTIMIZATION
→ SIMULATION
→ COMPARISON
→ AI EXPLANATION

When implementing, prefer a small number of strong, complete features over many incomplete ones.

==================================================
35. START NOW
==================================================

Start by inspecting the current repository and template.

Do not ask the user to restate the requirements above.

Determine the current implementation state.

Then:
1. create/update docs/implementation-status.md
2. implement the earliest incomplete phase
3. run tests or verification
4. fix issues
5. update implementation-status.md
6. stop at the end of the completed phase

When the user asks to continue, resume from implementation-status.md and proceed to the next phase.

Do not jump randomly between phases.
Do not rebuild already-working components.
Do not replace a working implementation merely to use a different library.

The goal is a working submission-ready HarborAI prototype with real simulation, ML prediction, optimization, scenario analysis, and an AI copilot.
'''

path = Path("/mnt/data/MASTER_IMPLEMENTATION_PROMPT_HARBORAI.md")
path.write_text(prompt, encoding="utf-8")
print(path)
"