# Preserved historical material

Moved on 18 October 2026. These files retain their original blobs and Git history. Old capability counts, completion claims, model identities and build-success statements are not current validation. Relative links, commands and directory listings describe the old repository layout.

## Project notes

- [BUILDER_README.md](project-notes/BUILDER_README.md)
- [FORGE_KIMI_MARRIAGE.md](project-notes/FORGE_KIMI_MARRIAGE.md)
- [IMPLEMENTATION_README.md](project-notes/IMPLEMENTATION_README.md)
- [KIMI_K2_ENHANCEMENT_PLAN.md](project-notes/KIMI_K2_ENHANCEMENT_PLAN.md)
- [README.legacy.md](project-notes/README.legacy.md)
- [ROADMAP.md](project-notes/ROADMAP.md)
- [TRANSFORMATION_REPORT.md](project-notes/TRANSFORMATION_REPORT.md)

## Previous UI and outputs

- legacy-ui/ holds the promotional splash JavaScript/CSS and the old HTML template. They are not loaded by the current UI; the historical HTML references external assets.
- generated-inputs/ preserves the old model configuration export. It is not deployment configuration.
- source-bundles/ preserves the original 2025 source ZIP and its old checksum file. No ISO or installer is established by that archive; checksum metadata is retained as historical input, not revalidated release evidence.

Fresh generated output belongs under ignored dist/ and build/. These archives are excluded from the prototype source bundle. See the [current README](../README.md) and [local Qwen guide](../docs/local-models/README.md).

## Withdrawn training/benchmark proposals

The original kimi_enhancement_toolkit.py and kimi_forge_integration.py are preserved byte-for-byte as .py.txt under design-scripts/. They contained unmeasured benchmark gains, source/capability counts, category descriptions presented as training examples, and unsupported fine-tuning instructions. They are historical text, not an executable training workflow. Current root modules return unknown results/design status or explicit NotImplementedError. No fine-tuning, model improvement or benchmark result is established by either version.
