# Project and folder guide

Stage: Python demonstration prototype. No loaded Kimi checkpoint or Linux distribution is established.

| Path | Role |
| --- | --- |
| Root Python files | Documentation loader, demo CLI, Flask interfaces and packaging helper |
| tests/ | Regression checks; 19 tests previously passed locally and in hosted CI |
| templates/, static/ | Flask demo UI |
| docs/*.md | Prompt-loader inputs as well as documentation; historical claims remain to be reconciled |
| docs/design-manifests/ | Preserved Rust/C++/Go design manifests without implemented source targets |
| Root legacy/design reports | Historical material; retained in place pending reference and prompt-input migration |
| dist/ | Existing output; not proof of a current build or bootable image |

The loader reads docs/*.md and README.md. This guide is therefore also a documentation input. Those paths were not moved during this cleanup. Source packaging currently includes only selected root Python files, docs/*.md and README.md; it is not a complete installable application package.

Next: connect one local model adapter, qualify one real tool, then repair and test complete application packaging. OS creation is a separate unimplemented proposal.
