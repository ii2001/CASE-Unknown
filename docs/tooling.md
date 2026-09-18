# Tooling audit

Checked 2026-09-18 before implementation.

- Used: Ponytail (`full`) for the smallest safe architecture; shell/file tools for implementation and validation.
- Available but not applicable: Figma skills. The requested source of truth is pen.dev/Pencil, so Figma was not treated as an interchangeable format.
- Not available: web-game development skill, pen.dev/Pencil integration, browser/Playwright execution tool, system-design skill.
- Local runtimes found: Python 3.14.6, Node 26.5.0, npm 12.0.2, uv 0.11.29.
- Browser UI checks therefore use Vitest/jsdom. Playwright was not added because no browser binary/testing integration was present.
