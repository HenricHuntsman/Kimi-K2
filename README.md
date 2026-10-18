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
| Linux OS, media tools, benchmark gains | OS/media builds unimplemented; training exports are unavailable and gains are not measured |

**41 Python tests and two frontend tests passed locally**, using a loopback HTTP fixture for Ollama. No live Qwen inference was possible here because Ollama was unreachable. GPU performance, production checkpoints, browser operation and installation remain unqualified; check Actions for hosted results.

The GUI now uses local assets, explicit backend status and plain-text answers. Invented skill counts, neural-loading animations and 16GB performance claims were removed. Model responses are advice, not executed actions.

## Files and history

[Folder guide](docs/PROJECT-GUIDE.md) · [Earlier functional audit](docs/FUNCTIONAL-AUDIT-2026-10-18.md) · [Archive index](archive/README.md) · [Licence](LICENSE).

Older project notes, the promotional UI and the old source ZIP are preserved under archive/. Fresh output belongs in ignored dist/ and build/ folders. The historical knowledge JSON and docs remain reference material and are not automatically sent to Qwen. Exported configuration is labelled design-only until configured for an actual runtime. No RC/RTM release is established.

Updated 18 October 2026.

## Training and measurement follow-up

The active enhancement helpers no longer invent benchmark gains or export category descriptions as training examples. Baselines remain caller-reported and unverified; measured scores and gains stay null until a real evaluation is implemented. Dataset extraction raises NotImplementedError. The generated training configuration is explicitly design-only. Originals are retained as text under archive/design-scripts/.

For one real local inference check, run `python forge_local.py --smoke --model qwen2.5-coder:7b`. The JSON report records request elapsed time and an exact-response check. Exit 0 means the marker matched, exit 2 means a completed answer differed, and exit 1 means a configuration/transport/model error. A passing smoke check is not proof of model quality, GPU performance or tool execution. The prior local-adapter commit passed hosted Python 3.11/3.14 and Node checks; consult Actions for this follow-up's result.
