# Project Architecture Rules (Non-Obvious Only)

- **Hard architectural boundary: ML predicts, OR-Tools decides, simulation validates, LLM explains.** These roles must not bleed into each other. Planning any feature that crosses these boundaries is a design error.
- **Modular monolith — not microservices.** All backend code lives in one deployable unit under `src/backend/`. Do not plan service splits.
- **Optimization result is separate from the current schedule.** The system maintains the live (possibly suboptimal) port state and an optimization result side-by-side. Applying the optimized plan is an explicit operator action.
- **Frontend vessel animation has no backend push.** The entire animation loop runs client-side using route geometry + start/end times from the REST API. Planning real-time features requires reconsideration of this constraint.
- **Priority ordering for limited time (from spec section 32):**
  - P0: backend + simulation + synthetic data + ML + OR-Tools + frontend dashboard + comparison
  - P1: AI copilot + what-if + explainability
  - P2: route optimization + secondary ML model + richer UI + RAG
- **Each phase must leave the project runnable.** Never plan a phase that breaks the running state of the prior phase.
- **Banned technologies (non-negotiable):** Kafka, Redis, Celery, Kubernetes, LSTM/transformers for tabular prediction, WebSockets in MVP, deep microservice splits.
