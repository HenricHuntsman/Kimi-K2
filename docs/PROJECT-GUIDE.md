# Project and folder guide

Stage: Python demonstration prototype. No loaded Kimi checkpoint or Linux distribution is established.

| Path | Role |
| --- | --- |
| Root Python files | Documentation loader, demo CLI, Flask interfaces and packaging helper |
| tests/ | Regression checks; 22 tests passed locally, including against an extracted source bundle; earlier 19-test hosted CI passed |
| templates/, static/ | Flask demo UI |
| docs/*.md | Prompt-loader inputs as well as documentation; historical claims remain to be reconciled |
| docs/design-manifests/ | Preserved Rust/C++/Go design manifests without implemented source targets |
| Root legacy/design reports | Historical material; retained in place pending reference and prompt-input migration |
| dist/ | Existing output; not proof of a current build or bootable image |

The loader reads docs/*.md and README.md. This guide is therefore also a documentation input. Those paths were not moved during this cleanup. Source packaging now includes dependencies, UI assets, tests and nested docs, with SHA-256 checksums. It remains a source bundle rather than an installer.

Next: connect one local model adapter, qualify one real tool, then repair and test complete application packaging. OS creation is a separate unimplemented proposal.
