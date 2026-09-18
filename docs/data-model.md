# Data model

`CanonicalCase` owns culprit, motive, method, time, timeline, suspects, private knowledge, clues and dependencies. `PlayerState` owns visited/unlocked locations, discovered clue IDs, interviews, narrative history and completion. `player_view()` is the sole projection into a browser DTO. Presentation URLs and labels are derived; no canonical significance is serialized.

SQLite table `games(id, case_json, player_json, event)` stores one atomic snapshot per active case. Interview turns are embedded in player state for the MVP. The repository interface isolates persistence sufficiently to replace it without affecting game logic.
