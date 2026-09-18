# Testing strategy

Backend tests cover case integrity, invalid references, dependency reachability/cycles, unlock/discovery/duplicates, NPC scope and persistence, both accusations, game-over, reset, refresh persistence, DTO leakage, injection attempts and image caching. An API playthrough exercises create → investigate → correct accusation → resolution → reset.

Frontend Vitest/jsdom covers landing, generation affordance, investigation layout, location imagery, evidence/suspect rendering, action submission, streaming and accusation modal. Responsive behavior is CSS media-query checked at build time. Playwright was not installed because browser tooling was unavailable; add it when CI provides a browser.
