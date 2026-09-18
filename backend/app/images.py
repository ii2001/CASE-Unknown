import hashlib
import logging
from html import escape

from .config import Settings
from .models import CanonicalCase, ImageBrief

logger = logging.getLogger(__name__)


def placeholder_svg(brief: ImageBrief) -> str:
    digest = hashlib.sha256(brief.id.encode()).hexdigest()
    accent = f"#{digest[:6]}"
    subject = escape(brief.subject)
    label = escape(brief.asset_type.upper())
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="720" viewBox="0 0 1200 720"><defs><linearGradient id="g" x2="1" y2="1"><stop stop-color="#080c12"/><stop offset="1" stop-color="{accent}" stop-opacity=".42"/></linearGradient><filter id="n"><feTurbulence baseFrequency=".8" numOctaves="3" stitchTiles="stitch"/><feBlend mode="soft-light" in="SourceGraphic"/></filter></defs><rect width="1200" height="720" fill="url(#g)"/><path d="M0 590 L230 400 410 520 690 270 940 480 1200 320V720H0Z" fill="#0d131c" opacity=".9"/><circle cx="890" cy="180" r="110" fill="{accent}" opacity=".22"/><g filter="url(#n)" opacity=".4"><rect width="1200" height="720" fill="#fff"/></g><text x="70" y="95" fill="#97a0ad" font-family="monospace" font-size="22" letter-spacing="7">CASE: UNKNOWN / {label}</text><text x="70" y="610" fill="#f4f0e6" font-family="sans-serif" font-size="56" font-weight="700">{subject}</text><rect x="70" y="640" width="110" height="4" fill="{accent}"/></svg>'''


def ensure_case_images(case: CanonicalCase, settings: Settings) -> None:
    directory = settings.data_dir / case.id / "images"
    directory.mkdir(parents=True, exist_ok=True)
    for brief in case.image_briefs:
        if any(directory.glob(f"{brief.id}.*")):
            continue
        path = directory / f"{brief.id}.svg"
        if settings.image_provider == "google" and settings.effective_gemini_api_key:
            try:
                from google import genai
                from google.genai import types

                prompt = (
                    f"Cinematic neo-noir game art. Subject: {brief.subject}. Environment: "
                    f"{brief.environment}. {brief.visual_description}. Mood: {brief.mood}. "
                    f"Camera: {brief.camera_style}. Continuity: {brief.continuity_notes}. "
                    f"Do not show: {', '.join(brief.prohibited_details)}. No text, no new clues."
                )
                response = genai.Client(api_key=settings.effective_gemini_api_key).models.generate_content(
                    model=settings.gemini_image_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
                )
                part = next(part for part in response.parts if part.inline_data)
                mime = part.inline_data.mime_type or "image/png"
                suffix = ".webp" if "webp" in mime else ".png"
                (directory / f"{brief.id}{suffix}").write_bytes(part.inline_data.data)
                continue
            except Exception as exc:  # noqa: BLE001 - every provider failure must degrade to SVG
                logger.warning("Image generation failed for %s: %s", brief.id, type(exc).__name__)
        path.write_text(placeholder_svg(brief), encoding="utf-8")
