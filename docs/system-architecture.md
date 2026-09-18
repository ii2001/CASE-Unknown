# System architecture

```mermaid
flowchart LR
  Vue[Vue + Pinia] -->|safe REST DTO| API[FastAPI]
  Vue -->|SSE narrative chunks| API
  API --> IG[InvestigationGraph]
  API --> CG[CaseGenerationGraph]
  IG --> Engine[Deterministic engine]
  CG --> Validate[Deterministic validation]
  API --> Repo[(SQLite JSON repository)]
  Repo --> Truth[Canonical truth]
  API --> Images[Cached SVG images]
  Providers[Gemini adapter] -. optional .-> CG
```

The repository is deliberately a small SQLite adapter, not an ORM. Canonical case and player state are separate Pydantic documents stored transactionally in one row. A refresh loads player state by case ID. State is committed before streaming begins.

```mermaid
flowchart TB
  Truth[Server canonical case] --> Engine
  Engine --> Known[Player-known state]
  Known --> DTO[PlayerCaseView]
  DTO --> Browser
  Truth -. never before resolution .-> Browser
```
