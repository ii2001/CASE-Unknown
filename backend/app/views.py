from .models import CanonicalCase, PlayerState


def player_view(case: CanonicalCase, state: PlayerState) -> dict:
    resolved = state.completed
    found = set(state.discovered_clue_ids)
    return {
        "id": case.id, "title": case.title, "genre": case.genre,
        "introduction": case.introduction, "incident_summary": case.incident_summary,
        "current_location_id": state.current_location_id,
        "visited_location_ids": state.visited_location_ids,
        "unlocked_location_ids": state.unlocked_location_ids,
        "narratives": state.narratives, "completed": state.completed, "won": state.won,
        "suspects": [{"id": s.id, "name": s.name, "role": s.role, "public_profile": s.public_profile, "portrait_url": f"/assets/{case.id}/suspect-{s.id}.svg"} for s in case.suspects],
        "locations": [{"id": loc.id, "name": loc.name, "description": loc.description if loc.id in state.visited_location_ids else "미방문 구역", "locked": loc.id not in state.unlocked_location_ids, "image_url": f"/assets/{case.id}/location-{loc.id}.svg"} for loc in case.locations],
        "evidence": [{"id": c.id, "title": c.title, "category": c.category, "critical": c.critical, "description": c.player_description, "image_url": f"/assets/{case.id}/{c.visual_asset_id}.svg" if c.visual_asset_id else None} for c in case.clues if c.id in found],
        "interviews": [record.model_dump() for record in state.interviews],
        "cover_url": f"/assets/{case.id}/cover.svg",
        **({"solution": {"culprit_id": case.culprit_id, "motive": case.motive, "crime_time": case.crime_time, "crime_method": case.crime_method, "timeline": case.canonical_timeline, "summary": case.solution_summary, "missed_clues": [c.title for c in case.clues if c.id not in found]}} if resolved else {}),
    }
