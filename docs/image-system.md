# Image system

Every case contains structured image briefs and stable suspect visual identities. `placeholder` mode renders context-aware noir SVGs from brief IDs, labels and deterministic colors. Assets are written once under `data/cases/<id>/images` and served with immutable cache headers. Existing files are never regenerated.

In `google` mode, the Google GenAI client requests each brief once from `GEMINI_IMAGE_MODEL` and stores returned PNG/WebP bytes. Any request or response failure falls back per asset to SVG. Image failure cannot block case creation or logical play. Images never introduce canonical evidence.
