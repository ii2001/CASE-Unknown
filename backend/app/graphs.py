from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from .config import Settings
from .demo_case import demo_case
from .engine import execute, route_action
from .models import CanonicalCase, CaseValidationResult, PlayerAction, PlayerState
from .providers import ModelRole, get_text_model
from .validation import validate_case


class GenerationState(TypedDict, total=False):
    genre: str
    case: CanonicalCase
    validation: CaseValidationResult
    attempts: int
    error: str


def build_case_generation_graph(settings: Settings):
    def generate(state: GenerationState):
        if settings.use_mock_llm:
            case = demo_case(state["genre"])
        else:
            model = get_text_model(ModelRole.CASE_GENERATOR, CanonicalCase, settings)
            case = model.invoke(
                "Create a Korean-language detective case. Exactly 3 suspects, 4 locations, "
                "6-8 clues, >=3 critical clues, one culprit, one false alibi and one red herring. "
                "Every critical clue must be reachable through acyclic prerequisites. Images must "
                "never contain extra evidence. Genre: " + state["genre"]
            )
        return {"case": case, "attempts": state.get("attempts", 0) + 1}

    def deterministic_validate(state: GenerationState):
        return {"validation": validate_case(state["case"])}

    def llm_logic_validate(state: GenerationState):
        if settings.use_mock_llm or not state["validation"].valid:
            return {}
        model = get_text_model(ModelRole.CASE_VALIDATOR, CaseValidationResult, settings)
        result = model.invoke(
            "Check logical solvability, contradictions, unreachable clues and hidden-solution "
            "leakage. Do not rewrite the case.\n" + state["case"].model_dump_json()
        )
        return {"validation": result}

    def repair(state: GenerationState):
        if settings.use_mock_llm:
            case = demo_case(state["genre"])
        else:
            model = get_text_model(ModelRole.CASE_GENERATOR, CanonicalCase, settings)
            case = model.invoke(
                "Repair this case using the validation findings. Preserve its premise and return "
                "a complete case.\nCASE:\n" + state["case"].model_dump_json()
                + "\nVALIDATION:\n" + state["validation"].model_dump_json()
            )
        return {"case": case, "attempts": state.get("attempts", 0) + 1}

    def route(state: GenerationState):
        if state["validation"].valid:
            return "done"
        if state["attempts"] >= settings.max_generation_attempts:
            return "failed"
        return "repair"

    graph = StateGraph(GenerationState)
    graph.add_node("generate_case", generate)
    graph.add_node("deterministic_validate", deterministic_validate)
    graph.add_node("llm_logic_validate", llm_logic_validate)
    graph.add_node("repair_case", repair)
    graph.add_edge(START, "generate_case")
    graph.add_edge("generate_case", "deterministic_validate")
    graph.add_edge("deterministic_validate", "llm_logic_validate")
    graph.add_conditional_edges("llm_logic_validate", route, {"done": END, "repair": "repair_case", "failed": END})
    graph.add_edge("repair_case", "deterministic_validate")
    return graph.compile()


class InvestigationState(TypedDict, total=False):
    case: CanonicalCase
    player: PlayerState
    text: str
    action: PlayerAction
    narrative: str


def build_investigation_graph():
    graph = StateGraph(InvestigationState)
    graph.add_node("load_game_state", lambda state: {})
    graph.add_node("classify_player_action", lambda state: {"action": route_action(state["text"], state["case"])})
    graph.add_node("execute_deterministic_action", lambda state: {"narrative": execute(state["case"], state["player"], state["action"])})
    graph.add_node("generate_narrative", lambda state: {})
    graph.add_node("checkpoint", lambda state: {})
    graph.add_edge(START, "load_game_state")
    graph.add_edge("load_game_state", "classify_player_action")
    graph.add_edge("classify_player_action", "execute_deterministic_action")
    graph.add_edge("execute_deterministic_action", "generate_narrative")
    graph.add_edge("generate_narrative", "checkpoint")
    graph.add_edge("checkpoint", END)
    return graph.compile()
