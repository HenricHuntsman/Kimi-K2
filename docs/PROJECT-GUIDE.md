# Project and folder guide

Stage: Python prototype with an opt-in local Ollama/Qwen chat backend. The Kimi-labelled wrapper and legacy REST routes remain demonstrations; no Kimi checkpoint or executable media/OS tool is implemented.

| Path | Role |
| --- | --- |
| forge_local.py | Loopback Ollama adapter and one-shot/interactive CLI |
| forge_cli.py --local | Entry to the real local adapter; default CLI stays a documentation demo |
| forge_gui.py | Web demo or opt-in Ollama chat; each web message is independent |
| forge_server.py | Separate legacy demonstration REST API |
| forge_implementation.py | Documentation loader and neutral prompt/config exporter |
| tests/ | Python regressions and Node frontend tests |
| templates/, static/ | Current chat page, local CSS and JavaScript |
| docs/local-models/ | Local Qwen setup, protocol policy and qualification limits |
| docs/*.md | Historical/reference loader inputs, not model capabilities |
| docs/design-manifests/ | Unimplemented Rust/C++/Go design targets |
| archive/ | Old project notes, UI, generated config and source bundle; excluded from fresh source packages |
| dist/, build/ | Ignored generated output |

The loader replaces state on reload and keeps docs/README.md separate from root README.md. Its prompt export indexes filenames without promoting historical headings to model capabilities. The root knowledge JSON is a historical dump; the local Qwen adapter does not consume it or send it to Ollama.

Source packaging includes the local adapter, dependencies, current UI, tests and nested docs with SHA-256 checksums. It remains a source bundle, not an installer or Linux ISO. The old tracked dist ZIP was moved to archive/source-bundles/.

35 Python and two Node tests passed locally; Ollama coverage uses a loopback HTTP fixture. No live Qwen/GPU or actual desktop browser qualification was performed. Full Linux/media builds remain explicit failures. See the [local model guide](local-models/README.md) for the next real-inference check.
