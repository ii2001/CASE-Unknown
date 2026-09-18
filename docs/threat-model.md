# Threat model

Assets at risk are the solution, API key and state integrity. Attackers are players inspecting traffic, sending prompt injection, guessing tool commands, replaying requests or traversing asset paths. Controls: safe DTO allow-list; server-only environment; deterministic command executor; no model-issued writes; ID validation; request length bounds; completed-state guard; traversal rejection; scoped NPC facts; structured output; cached images.

Known MVP limits: no authentication, so anyone with a case UUID can act on it; duplicate concurrent action idempotency is not yet keyed; JSON snapshots use last-write-wins. Add sessions, per-action idempotency keys and optimistic versioning before shared/public deployment.
