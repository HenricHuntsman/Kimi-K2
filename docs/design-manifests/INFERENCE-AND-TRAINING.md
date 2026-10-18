# Inference and training are separate

Local chat is implemented in forge_local.py and the opt-in GUI. See
[local Qwen setup](../local-models/README.md). This adapter calls an existing
Ollama model; it does not fine-tune, train, merge weights or execute tools.

No audited training-data extractor or trainer exists in this repository.
The previous category descriptions, source-line counts and benchmark gains
were not measured training evidence. Earlier inference-server commands were
not a valid fine-tuning workflow and are withdrawn. The originals remain in
archive/design-scripts/ for provenance.

Before implementing training: select a suitable model and actual trainer,
audit dataset licences and examples, separate held-out tasks, validate
checkpoint save/reload, and measure a reproducible baseline and candidate.
No capability count, improvement percentage or model quality is established.
