# Project Coding Rules (Non-Obvious Only)

- **Always read `docs/implementation-status.md` first.** It tracks the current phase. Never skip ahead.
- **Route handlers are thin.** All logic belongs in domain modules (`simulation/`, `prediction/`, `optimization/`). Route handlers only call domain services and return Pydantic responses.
- **OR-Tools owns decisions.** Any berth assignment, crane allocation, or schedule computation must go through `optimization/`. The AI agent (`ai/agent.py`) may only call tools; it must never perform mathematical scheduling itself.
- **Artifacts must be persisted.** Trained model + preprocessor go to `prediction/artifacts/`. Inference loads from disk — do not retrain on every request.
- **Deterministic seed everywhere.** Synthetic data generation, simulation, and model training all use a fixed seed so the demo is reproducible.
- **Frontend receives route + timing; it interpolates.** The backend never pushes real-time position updates. The frontend computes intermediate vessel positions from the route points and schedule timing returned by the API.
- **Two parallel simulation scenarios** must coexist: `current` (unoptimized) and `optimized`. Never mutate the current scenario when running optimization — return a separate result.
- **Explanation metadata is mandatory** on every prediction and optimization response. See spec sections 22 and 9 for the required JSON shape.
