# FORGE Integration Lab — Kimi K2

A Python prototype for loading documentation, exporting prompts/configuration, and exploring demonstration CLI and Flask interfaces. **Stage: prototype.** It does not load a Kimi checkpoint or execute the advertised media/OS tools. It is independent of [Moonshot AI's Kimi-K2](https://github.com/moonshotai/Kimi-K2).

## Run and check

Use Python 3.11 or 3.14, as in CI:

~~~bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
make test
python forge_cli.py
# Alternative demonstration interfaces:
python forge_gui.py
python forge_server.py
~~~

Run one interface at a time. Both Flask entry points default to loopback; these are development demos, without production authentication qualification.

## What works and what remains

| Component | Verified scope | Remaining work |
| --- | --- | --- |
| Documentation loader | Markdown loading, prompt/config export | Reconcile historical claims in prompt inputs |
| CLI | Basic history, modes, stats and capabilities responses | Real local model adapter |
| Flask GUI and legacy REST API | Tested demo routes, input validation, explicit unavailable-tool results | Real inference, tool execution and deployment qualification |
| Source packaging | Includes Python, dependencies, UI assets, tests and nested documentation; SHA-256 manifest | Fresh-environment installation and desktop packaging qualification |
| Model/tool integration | Explicit simulation; zero executable registered tools | Implement and test one local model/tool workflow |
| Linux OS/video editor | Explicitly unimplemented | Separate implementations and end-to-end tests |

The expanded suite has **22 local passing tests**, including archive contents, omitted cache/hidden files, missing inputs and checksum verification. Previous hosted CI passed 19 tests; see Actions for the expanded suite's result. These checks do not establish inference, a professional editor, a bootable OS or measured benchmark gains. Enhancement-toolkit gains remain hard-coded estimates.

## Package the prototype sources

~~~bash
make dist
~~~

This writes a clearly labelled prototype source ZIP and checksums under dist/. It is not an installer or ISO. Unimplemented full builds and system installation return nonzero; dependency installation errors propagate. The original source-packaging omissions are repaired in this pass.

## Files and history

[Folder guide](docs/PROJECT-GUIDE.md) · [Earlier functional audit](docs/FUNCTIONAL-AUDIT-2026-10-18.md) · [Historical README](README.legacy.md) · [Licence](LICENSE).

The earlier audit records failures subsequently repaired; use this README and current tests for present behaviour. Root Python files are active; templates/ and static/ hold UI assets; tests/ holds checks. docs/*.md and README.md are prompt-loader inputs. Unimplemented Rust/C++/Go manifests are preserved under docs/design-manifests/. Older capability counts, completion percentages and quality scores are not verified results.

Updated 18 October 2026. No RC/RTM qualification.
