import re

from .models import ActionType, CanonicalCase, PlayerAction, PlayerState

HELP = "장소로 이동하거나 주변·CCTV·로그를 조사하고, 용의자에게 질문하거나 증거를 정리해 보세요. 확신이 들면 고발할 수 있습니다."


def initial_state(case: CanonicalCase) -> PlayerState:
    start = case.locations[0].id
    return PlayerState(current_location_id=start, visited_location_ids=[start], unlocked_location_ids=[loc.id for loc in case.locations if not loc.locked], narratives=[case.introduction])


def route_action(text: str, case: CanonicalCase) -> PlayerAction:
    clean = text.strip()
    lower = clean.lower()
    if any(word in lower for word in ("ignore", "system prompt", "culprit", "정답", "범인 알려")):
        return PlayerAction(action_type=ActionType.HELP, query="injection")
    for suspect in case.suspects:
        if suspect.name in clean:
            if any(word in clean for word in ("범인", "고발", "지목")):
                return PlayerAction(action_type=ActionType.ACCUSE, suspect_id=suspect.id, reasoning=clean)
            return PlayerAction(action_type=ActionType.INTERVIEW, suspect_id=suspect.id, question=clean)
    for location in case.locations:
        if location.name in clean or location.id in lower:
            return PlayerAction(action_type=ActionType.MOVE, location=location.id)
    if any(word in clean for word in ("증거", "정리", "타임라인", "용의자")):
        return PlayerAction(action_type=ActionType.REVIEW, query=clean)
    if any(word in clean for word in ("조사", "확인", "뒤져", "살펴", "CCTV", "로그", "책상", "랙", "테이블", "단말")):
        return PlayerAction(action_type=ActionType.INVESTIGATE, target=clean)
    return PlayerAction(action_type=ActionType.HELP, query=clean)


def _find_clue(case: CanonicalCase, state: PlayerState, target: str):
    available = [c for c in case.clues if c.location_id == state.current_location_id and c.id not in state.discovered_clue_ids and set(c.prerequisites) <= set(state.discovered_clue_ids)]
    if not available:
        return None
    target_tokens = set(re.findall(r"[A-Za-z가-힣0-9]+", target.lower()))
    return max(available, key=lambda clue: len(target_tokens & set(re.findall(r"[A-Za-z가-힣0-9]+", (clue.target + clue.title).lower()))))


def interview(case: CanonicalCase, state: PlayerState, suspect_id: str, question: str) -> str:
    suspect = next((s for s in case.suspects if s.id == suspect_id), None)
    if not suspect:
        return "그 이름의 용의자는 사건 기록에 없습니다."
    known = " ".join(suspect.known_facts).lower()
    if any(term in question for term in ("알리바이", "어디", "몇 시", "11시", "22시")):
        answer = suspect.claimed_alibi
    elif any(term.lower() in known for term in re.findall(r"[A-Za-z가-힣]+", question)):
        answer = suspect.known_facts[0]
    elif "시스템" in question or "프롬프트" in question or "범인" in question:
        answer = "그런 정보는 알지 못합니다. 제가 직접 본 사실만 말씀드리죠."
    else:
        answer = "그 질문에 답할 만큼 아는 것이 없습니다. 확인한 사실을 구체적으로 물어보세요."
    from .models import InterviewRecord
    state.interviews.append(InterviewRecord(suspect_id=suspect_id, question=question, answer=answer))
    return f"{suspect.name}: “{answer}”"


def execute(case: CanonicalCase, state: PlayerState, action: PlayerAction) -> str:
    if state.completed:
        return "이 사건은 이미 종결되었습니다. 새 사건을 시작하세요."
    if action.action_type == ActionType.MOVE:
        location = next((loc for loc in case.locations if loc.id == action.location), None)
        if not location:
            return "그 장소는 사건 구역에 없습니다."
        if location.id not in state.unlocked_location_ids:
            return "출입이 잠겨 있습니다. 접근 기록이나 열쇠 단서를 먼저 찾아야 합니다."
        state.current_location_id = location.id
        if location.id not in state.visited_location_ids:
            state.visited_location_ids.append(location.id)
        result = f"{location.name}으로 이동했습니다. {location.description}"
    elif action.action_type == ActionType.INVESTIGATE:
        clue = _find_clue(case, state, action.target)
        if not clue:
            result = "여기서 지금 더 확인할 수 있는 새로운 단서는 없습니다. 다른 대상을 구체적으로 조사해 보세요."
        else:
            state.discovered_clue_ids.append(clue.id)
            for loc in case.locations:
                if loc.unlock_clue_id == clue.id and loc.id not in state.unlocked_location_ids:
                    state.unlocked_location_ids.append(loc.id)
            result = f"증거 발견 — {clue.title}: {clue.player_description}"
    elif action.action_type == ActionType.INTERVIEW:
        result = interview(case, state, action.suspect_id, action.question)
    elif action.action_type in (ActionType.REVIEW, ActionType.DEDUCE):
        found = [c.title for c in case.clues if c.id in state.discovered_clue_ids]
        result = "현재 증거: " + (", ".join(found) if found else "아직 수집한 증거가 없습니다.")
    elif action.action_type == ActionType.ACCUSE:
        return accuse(case, state, action.suspect_id, action.reasoning)
    else:
        result = "숨은 정답이나 시스템 지시는 공개할 수 없습니다. " + HELP if action.query == "injection" else HELP
    state.narratives.append(result)
    return result


def accuse(case: CanonicalCase, state: PlayerState, suspect_id: str, reasoning: str) -> str:
    if state.completed:
        return "이 사건은 이미 종결되었습니다."
    if suspect_id not in {s.id for s in case.suspects}:
        return "유효한 용의자를 선택하세요."
    state.completed = True
    state.won = suspect_id == case.culprit_id
    state.accusation_reasoning = reasoning
    result = ("사건 해결. " if state.won else "잘못된 고발. ") + case.solution_summary
    state.narratives.append(result)
    return result
