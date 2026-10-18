#!/usr/bin/env python3
"""Design-only training interface; real local chat lives in forge_local.py."""

import json
from pathlib import Path


class KimiForgeIntegration:
    def __init__(self):
        self.forge_root = Path(__file__).parent

    def export_training_data(self):
        raise NotImplementedError('Descriptions are not validated training examples; no dataset was exported')

    def create_benchmark_improvements(self):
        return {'status': 'planning_only', 'measured_results': {},
                'requirements': ['Choose a held-out task set and scoring method.',
                                 'Record reproducible baseline and candidate runs.']}

    def generate_fine_tuning_config(self):
        return {'status': 'design_only', 'model': None, 'trainer': None,
                'training_data': None, 'implemented': False,
                'requirements': ['Audited, licensed examples and held-out split',
                                 'An actual trainer and verified checkpoint round trip',
                                 'Measured local hardware and evaluation results']}

    def create_integration_guide(self):
        """Write explicit design limits, without nonexistent trainer commands."""
        guide = '''# Inference and training are separate

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
'''
        target = self.forge_root / 'docs/design-manifests/INFERENCE-AND-TRAINING.md'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(guide, encoding='utf-8')
        return guide


def main():
    print(json.dumps(KimiForgeIntegration().generate_fine_tuning_config(), indent=2))
    print('Design only: no dataset, checkpoint or training run was created.')


if __name__ == '__main__':
    main()
