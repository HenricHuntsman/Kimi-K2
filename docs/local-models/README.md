# Local Qwen through Ollama

The FORGE prototype can call an already-installed local Qwen model through Ollama. This is a separate backend from the Kimi-labelled simulation. It does not load Kimi K2 weights, train a model, run code or execute the illustrative tools.

## Prepare your existing server

Use `ollama list` to select an installed model. No model is downloaded automatically. Before a prompt is sent, the client requires the local server's `/api/status` response to confirm `cloud.disabled: true`, then checks `/api/show` for local model metadata and rejects remote-backed models.

For a new foreground server process, Ollama supports:

```bash
OLLAMA_NO_CLOUD=1 ollama serve
```

If Ollama is already running, configure that server using the [official cloud-disable instructions](https://docs.ollama.com/faq#how-do-i-disable-ollamas-cloud-features) and restart it through its existing service manager. Setting the variable only on the FORGE process does not reconfigure an existing Ollama service. This repository does not modify, replace or upgrade your installed Ollama. Servers without the status API or cloud-disable confirmation are refused rather than silently used.

## CLI

From the repository root, in your Python environment:

```bash
python forge_local.py --check --model qwen2.5-coder:7b
python forge_local.py --model qwen2.5-coder:7b 'Explain this Python exception'
python forge_cli.py --local --model qwen3:8b
```

Choose a tag actually present in your `ollama list`. The default is qwen2.5-coder:7b. Interactive local chat keeps history in process memory; `/clear` resets it and `/exit` quits. Failed turns do not enter history. One-shot failures exit nonzero. `--check` checks policy and metadata, not inference. Chat history is limited to 100 messages / 128 KiB of UTF-8 text; clear or shorten it when needed. No historical documentation is silently added to prompts.

## Web UI

```bash
FORGE_BACKEND=ollama FORGE_OLLAMA_MODEL=qwen2.5-coder:7b python forge_gui.py
```

Open http://127.0.0.1:5000 . Each GUI message is independent. The page distinguishes configured backend from verified inference and displays unavailable-model/server errors. Without FORGE_BACKEND, the UI remains a labelled demo echo. The legacy `forge_server.py` routes remain demonstrations.

Optional client settings: FORGE_OLLAMA_URL (loopback HTTP only; default http://127.0.0.1:11434), FORGE_OLLAMA_TIMEOUT (positive seconds, up to 600; default 120). HTTP proxies and redirects are disabled. No cloud fallback, API keys, model downloads, server configuration changes or automatic tools are provided. Responses are capped at 2 MiB.

## Evidence and remaining checks

41 Python tests and two Node frontend tests passed locally. Tests use a real loopback HTTP fixture, not an actual Qwen model. They cover native request shape, policy refusal before prompt transmission, remote metadata rejection, redirects, proxy bypass, timeouts, response limits, CLI/GUI routing and visible frontend errors. Prompt exports no longer invent a Kimi identity or persistent learning. A repeated documentation load replaces old state rather than duplicating it.

Ollama was unreachable in this hosted workspace. Actual Qwen output, token speed, context behaviour, GPU use and desktop browser operation remain unverified. Next qualification is a successful prompt on your existing local server, followed by an interactive CLI and browser smoke test. The adapter follows [Ollama's native chat API](https://github.com/ollama/ollama/blob/main/docs/api.md) and [status/model response contracts](https://github.com/ollama/ollama/blob/main/api/types.go).

## Run a measured local smoke check

```bash
python forge_local.py --smoke --model qwen2.5-coder:7b
```

This sends only a fixed request for FORGE_LOCAL_OK. It prints JSON containing the actual answer, requested backend's returned model name, client request elapsed time and exact-match result. Exit 0 is a match; exit 2 is a completed but different answer; exit 1 is an error. Elapsed time includes policy/metadata checks and any model loading, so it is not token throughput. No files are written automatically. This is a connectivity/inference smoke check, not a quality benchmark. Tests exercise match and mismatch using the protocol fixture; real local inference remains to be run on your server.
