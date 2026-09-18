from .models import CanonicalCase, CaseValidationResult


def validate_case(case: CanonicalCase) -> CaseValidationResult:
    errors: list[str] = []
    unreachable: list[str] = []
    suspect_ids = [s.id for s in case.suspects]
    location_ids = [loc.id for loc in case.locations]
    clue_ids = [clue.id for clue in case.clues]
    if suspect_ids.count(case.culprit_id) != 1:
        errors.append("culprit_id must reference exactly one suspect")
    for name, values in (("suspect", suspect_ids), ("location", location_ids), ("evidence", clue_ids)):
        if len(values) != len(set(values)):
            errors.append(f"duplicate {name} ids")
    if sum(clue.critical for clue in case.clues) < 3:
        errors.append("at least three critical clues required")
    for clue in case.clues:
        if clue.location_id not in location_ids:
            errors.append(f"clue {clue.id} references invalid location")
        missing = set(clue.prerequisites) - set(clue_ids)
        if missing:
            unreachable.append(clue.id)
    graph = {clue.id: clue.prerequisites for clue in case.clues}
    visiting: set[str] = set()
    visited: set[str] = set()

    def cycle(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(cycle(dep) for dep in graph.get(node, [])):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    if any(cycle(node) for node in graph):
        errors.append("circular clue dependency")
    for location in case.locations:
        if location.locked and location.unlock_clue_id not in clue_ids:
            errors.append(f"locked location {location.id} cannot be unlocked")
    accessible_locations = {location.id for location in case.locations if not location.locked}
    reachable_clues: set[str] = set()
    changed = True
    while changed:
        changed = False
        for clue in case.clues:
            if (
                clue.id not in reachable_clues
                and clue.location_id in accessible_locations
                and set(clue.prerequisites) <= reachable_clues
            ):
                reachable_clues.add(clue.id)
                changed = True
        for location in case.locations:
            if location.unlock_clue_id in reachable_clues and location.id not in accessible_locations:
                accessible_locations.add(location.id)
                changed = True
    unreachable += [clue.id for clue in case.clues if clue.critical and clue.id not in reachable_clues]
    for location in case.locations:
        if location.id not in accessible_locations:
            errors.append(f"locked location {location.id} is unreachable")
    return CaseValidationResult(valid=not errors and not unreachable, solvable=not errors and not unreachable, contradictions=errors, unreachable_clues=sorted(set(unreachable)))
