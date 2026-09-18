import asyncio
import json
import logging
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

from .config import get_settings
from .engine import accuse, initial_state
from .graphs import build_case_generation_graph, build_investigation_graph
from .images import ensure_case_images
from .models import AccusationRequest, ActionRequest, NewCaseRequest
from .repository import CaseRepository
from .views import player_view

settings = get_settings()
repo = CaseRepository(settings.database_url)
case_graph = build_case_generation_graph(settings)
investigation_graph = build_investigation_graph()
app = FastAPI(title="CASE: UNKNOWN", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
logger = logging.getLogger("case_unknown.requests")


@app.middleware("http")
async def log_request(request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    logger.info("%s %s %s %.0fms", request.method, request.url.path, response.status_code, (time.perf_counter() - started) * 1000)
    return response


def load(case_id: str):
    try:
        return repo.load(case_id)
    except KeyError as exc:
        raise HTTPException(404, "Case not found") from exc


@app.get("/api/health")
def health():
    return {"status": "ok", "mock": settings.use_mock_llm}


@app.get("/api/config/public")
def public_config():
    return {"image_provider": settings.image_provider, "mock_mode": settings.use_mock_llm, "latest_case_id": repo.latest_id()}


@app.post("/api/cases", status_code=201)
def create_case(request: NewCaseRequest):
    result = case_graph.invoke({"genre": request.genre}, {"recursion_limit": settings.max_graph_steps})
    if not result["validation"].valid:
        raise HTTPException(422, "Could not generate a solvable case")
    case = result["case"]
    player = initial_state(case)
    ensure_case_images(case, settings)
    repo.save(case, player, case.introduction)
    return player_view(case, player)


@app.get("/api/cases/{case_id}")
def get_case(case_id: str):
    return player_view(*load(case_id))


@app.get("/api/cases/{case_id}/evidence")
def evidence(case_id: str):
    return get_case(case_id)["evidence"]


@app.get("/api/cases/{case_id}/suspects")
def suspects(case_id: str):
    return get_case(case_id)["suspects"]


@app.get("/api/cases/{case_id}/locations")
def locations(case_id: str):
    return get_case(case_id)["locations"]


@app.post("/api/cases/{case_id}/actions")
def action(case_id: str, request: ActionRequest):
    case, player = load(case_id)
    if request.request_id and request.request_id in player.processed_request_ids:
        return {"narrative": repo.event(case_id), "case": player_view(case, player)}
    result = investigation_graph.invoke({"case": case, "player": player, "text": request.text}, {"recursion_limit": settings.max_graph_steps})
    if request.request_id:
        player.processed_request_ids.append(request.request_id)
    repo.save(case, player, result["narrative"])
    return {"narrative": result["narrative"], "case": player_view(case, player)}


@app.post("/api/cases/{case_id}/accuse")
def accusation(case_id: str, request: AccusationRequest):
    case, player = load(case_id)
    narrative = accuse(case, player, request.suspect_id, request.reasoning)
    repo.save(case, player, narrative)
    return {"narrative": narrative, "case": player_view(case, player)}


@app.post("/api/cases/{case_id}/reset")
def reset(case_id: str):
    case, _ = load(case_id)
    player = initial_state(case)
    repo.save(case, player, case.introduction)
    return player_view(case, player)


@app.get("/api/cases/{case_id}/events/stream")
async def stream(case_id: str):
    text = repo.event(case_id)
    async def events():
        for word in text.split():
            yield f"data: {json.dumps({'chunk': word + ' '}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.025)
        yield "event: done\ndata: {}\n\n"
    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


@app.get("/assets/{case_id}/{name}")
def asset(case_id: str, name: str):
    if "/" in case_id or "/" in name or ".." in case_id or ".." in name:
        raise HTTPException(400, "Invalid asset path")
    path = settings.data_dir / case_id / "images" / name
    if not path.exists():
        matches = list(path.parent.glob(f"{path.stem}.*"))
        if not matches:
            raise HTTPException(404, "Asset not found")
        path = matches[0]
    media_type = {".svg": "image/svg+xml", ".webp": "image/webp", ".png": "image/png"}.get(path.suffix)
    return FileResponse(Path(path), media_type=media_type, headers={"Cache-Control": "public, max-age=31536000, immutable"})
