# API contract

- `POST /api/cases` creates and validates a case.
- `GET /api/cases/{id}` returns only the player-safe projection.
- `POST /api/cases/{id}/actions` classifies and executes natural language.
- `GET /api/cases/{id}/events/stream` streams the last committed narrative.
- `GET /api/cases/{id}/{evidence|suspects|locations}` returns safe subsets.
- `POST /api/cases/{id}/accuse` ends the case and then exposes resolution.
- `POST /api/cases/{id}/reset` restores initial player state.
- `GET /api/config/public`, `GET /api/health` expose non-secret status.

All request text is Pydantic-limited. Missing cases return 404. Hidden fields are absent—not redacted strings—before resolution.
