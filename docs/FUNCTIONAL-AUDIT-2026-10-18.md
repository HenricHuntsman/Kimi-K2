# Functional audit — 18 October 2026

Tested source: `4a80f6392969a7d6a68e6474b2eede1aa0c22d0c`.

This audit distinguishes observed behavior from source-only findings. Isolated checkout and temporary outputs; no installed models, credentials or user settings changed. Test environment: Python 3.12 virtual environment, Flask 3.1.2, Flask-CORS 6.0.1; Node.js 24.19.0 for npm entry-point checks.

## What demonstrably works

| Area | Executed evidence | Limit |
| --- | --- | --- |
| Documentation loading/statistics | Loaded 15 dictionary entries from the project's Markdown/root README; returned counts | A documentation entry is not an implemented feature |
| Prompt assembly | Returned a 5,463-character prompt | Template text, not inference; no claim that all source documentation appears in that prompt |
| Knowledge JSON export | Parsed exported JSON; each exported document's content matched the loaded dictionary | Not a trained checkpoint or a validated training dataset |
| Model configuration export | Parsed JSON; exported system prompt matched the generated prompt | Does not deploy or run vLLM |
| CLI navigation | Help, mode change, history, clear and exit handlers completed | Responses are templates |
| CLI session history | Two synthetic exchanges produced four user/assistant entries; mode change retained | In-memory behavior only, no learned memory |
| Source-ZIP helper | Created ZIP from a temporary two-file fixture; entries/CRC checked | Source packaging only, not an application installer or OS image |
| Recent GUI/wrapper integrity suite | `make test`: 12 passed | Tests verify honest demo behavior and routes, not real model/media tools |
| Hosted integrity workflow | Current source's workflow reported success on GitHub | Distinct from broad product qualification |

## Broken or misleading paths reproduced

| Path | Observed outcome |
| --- | --- |
| CLI `/stats` | AttributeError: ForgeAI has no get_all_capabilities method |
| CLI `/caps` | Same AttributeError |
| Older server `GET /api/capabilities` | HTTP 500, same missing method |
| Older server `GET /api/stats` | HTTP 500, same missing method |
| `npm run build` | Nonzero exit: build.js is absent |
| `npm test` | Exits zero by printing “Tests pass”; no tests execute |

The existing Python `make test` suite is real. The npm script is a different, vacuous entry point and must not be cited as validation.

## Demonstrations and limited helpers

The older REST server's health, system-prompt and documentation endpoints returned HTTP 200. Chat returned a demonstration string and a `success` status; this proves response handling, not model execution. It also uses a `capabilities_used` label for keyword-selected categories.

Source inspection found fixed quality scores in older code-review/book-analysis endpoints, plus template suggestions. Those routes were inspected but not qualified as actual quality evaluation. The newer GUI now uses explicit unavailable-tool responses; it is separate from `forge_server.py`.

## Manifest/source gaps

These manifest-referenced paths are absent:

- Node: `build.js`, `src/index.js`, `src/server.js`.
- Rust: `src/lib.rs`, `src/main.rs`.
- C++: `src/core/main.cpp`, `src/video/processor.cpp`.

Rust and C++ compilation were not executed; the absence is a source-inventory finding. No Go implementation files were found in the checkout. Manifests alone do not establish implemented language components.

## What we actually have

A **working Python documentation/prompt/export foundation and a tested demonstration interface**, with partially functional CLI/REST helpers. No Kimi checkpoint inference, neural training, working media editor/upscaler, measured benchmark improvement or Linux distribution was demonstrated.

Stage remains **prototype**. Existing upstream Kimi model documentation is separate from the capabilities of this lab.

## Repair order

1. Make CLI statistics and the older REST server consume the real loader/statistics API; do not invent get_all_capabilities to turn prose into fake tools.
2. Label legacy response/status fields accurately; remove fixed quality scores and unsupported completion claims.
3. Replace the vacuous npm test and missing-source build commands with explicit unsupported status or real implemented paths.
4. Preserve unused multi-language manifests as labelled design material, or implement one component with its source and tests.
5. Qualify one local-model adapter using a small model already owned/installed, with explicit errors and measured output.
6. Expand real tools only after one end-to-end local workflow passes.

No runtime code was changed by this audit; failures remain open. Tests did not exercise CUDA, actual Kimi weights, Ghidra, media processing, containers, external providers or production deployment.

## Recovery follow-up

Subsequent implementation repairs the reproduced CLI/REST statistics and documentation faults, reports demo status/empty executable tools, removes fixed quality scores, and rejects invalid payloads before session changes. The npm test entry now runs Python unittest instead of printing success. Unimplemented language manifests are preserved as design material under `docs/design-manifests/`. Added seven regressions; the combined suite passes 19 tests locally. Earlier failing observations above remain evidence of the audited base, not a claim those paths are still broken after the recovery commit.
