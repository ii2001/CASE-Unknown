# LangGraph design

```mermaid
flowchart TD
  S([START]) --> G[generate_case]
  G --> D[deterministic_validate]
  D --> L[llm_logic_validate]
  L --> V{valid?}
  V -->|yes| E([END])
  V -->|no, under 3| R[repair_case]
  R --> D
  V -->|attempt limit| E
```

```mermaid
flowchart TD
  S([START]) --> Load[load_game_state]
  Load --> Route[classify_player_action]
  Route --> Exec[execute_deterministic_action]
  Exec --> Narrate[generate_narrative]
  Narrate --> Check[checkpoint]
  Check --> E([END])
```

Both graphs have typed state and explicit nodes. FastAPI invokes them with a recursion limit of 12. In mock mode classification is deterministic. The centralized Gemini structured-output factory is ready for the case, validator, router, NPC and narrator roles; the canonical engine remains the only mutation path.
