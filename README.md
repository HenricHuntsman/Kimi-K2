# FORGE Integration Lab — Kimi K2 / Local Qwen

A Python prototype with documentation exporters, demo interfaces and an opt-in **local Qwen chat backend through Ollama**. Stage: prototype. Qwen is a separate backend; this repository does not load or train a Kimi K2 checkpoint. Upstream model authorship remains with [Moonshot AI](https://github.com/moonshotai/Kimi-K2).

## Start

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
make test
make test-ui  # Node.js 22
```

Use an existing Ollama server with cloud features disabled and an installed model:

```bash
python forge_local.py --check --model qwen2.5-coder:7b
python forge_cli.py --local --model qwen2.5-coder:7b
FORGE_BACKEND=ollama FORGE_OLLAMA_MODEL=qwen2.5-coder:7b python forge_gui.py
```

See the [local Qwen guide](docs/local-models/README.md) for server policy, commands, model selection and limitations. The adapter requires cloud-disabled confirmation before sending prompts, accepts loopback HTTP only and has no proxy, redirect or cloud fallback. It does not download models or reconfigure Ollama.

## Current behaviour

| Component | Scope |
| --- | --- |
| Local CLI and opt-in GUI | Calls Ollama's native chat API; clear errors when unavailable; no tool execution |
| Default GUI / legacy CLI / forge_server.py | Demonstrations; not model inference |
| Documentation loader | Markdown loading and prompt/config export; historical text is not executable capability |
| Source bundle | `make dist` includes dependencies, UI, tests and nested docs with checksums; not an installer or ISO |
| Linux OS, media tools, benchmark gains | OS/media builds unimplemented; enhancement estimates remain illustrative |

**35 Python tests and two frontend tests passed locally**, using a loopback HTTP fixture for Ollama. No live Qwen inference was possible here because Ollama was unreachable. GPU performance, production checkpoints, browser operation and installation remain unqualified; check Actions for hosted results.

The GUI now uses local assets, explicit backend status and plain-text answers. Invented skill counts, neural-loading animations and 16GB performance claims were removed. Model responses are advice, not executed actions.

## Files and history

[Folder guide](docs/PROJECT-GUIDE.md) · [Earlier functional audit](docs/FUNCTIONAL-AUDIT-2026-10-18.md) · [Archive index](archive/README.md) · [Licence](LICENSE).

Older project notes, the promotional UI and the old source ZIP are preserved under archive/. Fresh output belongs in ignored dist/ and build/ folders. The historical knowledge JSON and docs remain reference material and are not automatically sent to Qwen. Exported configuration is labelled design-only until configured for an actual runtime. No RC/RTM release is established.

Updated 18 October 2026.
