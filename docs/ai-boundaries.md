# AI boundaries

The browser never receives canonical truth until `PlayerState.completed`. The action router outputs only `PlayerAction`; the engine verifies IDs, locks, prerequisites and game-over state. NPC context is assembled from that NPC's identity, known facts, configured lie and persisted prior turns—not the full case. Narration consumes an action result rather than the case.

Input is length-limited and injection phrases route to safe help. There is no arbitrary tool or code execution. Mock mode makes these guarantees testable without trusting a model. Real model calls require structured Pydantic output, bounded retries/timeouts and graph recursion limits.
