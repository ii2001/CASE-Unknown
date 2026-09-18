# UI/UX specification

Tokens: ink `#070a0e`, panel `#0d1219`, raised `#141b24`, paper `#e9e4d8`, amber `#d8a94f`, danger `#b7473e`; 4px radius; 8px-derived spacing; IBM Plex Mono metadata with Noto Sans KR body. Motion is restricted to streamed text and native state transitions.

Implemented components: CTA/ghost/icon-like buttons, location navigation, case progress, evidence/photo cards, suspect dossier cards, system narration, streaming live region, empty/loading/error states, accusation and resolution modals. Desktop uses the requested three-column workspace. Tablet suppresses the board; mobile becomes one investigation column with bottom navigation.

Design frame specification (for later Pencil import): `00_Foundations`, `01_Landing`, `02_New_Case_Setup`, `03_Case_Introduction`, `04_Investigation_Main`, `05_Location_View`, `06_Suspect_Dossier`, `07_Evidence_Detail`, `08_Case_Board`, `09_Accusation`, `10_Case_Solved`, `11_Case_Failed`, `12_Settings`, `13_Responsive`. The running frontend is the current visual source because raw `.pen` JSON must not be fabricated without Pencil tooling.
