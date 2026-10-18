import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from kimi_enhancement_toolkit import KimiEnhancementToolkit, main as enhancement_main
from kimi_forge_integration import KimiForgeIntegration, main as integration_main


class TrainingTruthTests(unittest.TestCase):
    def test_reported_baselines_never_become_invented_scores_or_gains(self):
        result = KimiEnhancementToolkit().evaluate_improvements({'zero': 0, 'example': 50, 'max': 100})
        for name, score in [('zero', 0), ('example', 50), ('max', 100)]:
            self.assertEqual(result[name]['reported_baseline'], score)
            self.assertFalse(result[name]['baseline_verified'])
            self.assertEqual(result[name]['status'], 'not_measured')
            for key in ['measured_score', 'estimated_improvement', 'new_score', 'percentile_gain']:
                self.assertIsNone(result[name][key])
        self.assertIsNone(KimiEnhancementToolkit()._estimate_improvement('unknown'))

    def test_invalid_baselines_fail_instead_of_fabricating_results(self):
        for value in [[], {'': 1}, {'x': True}, {'x': float('nan')}, {'x': float('inf')},
                      {'x': -1}, {'x': 101}, {'x': 10 ** 1000}, {'x': '50'}]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                KimiEnhancementToolkit().evaluate_improvements(value)

    def test_unimplemented_training_exports_do_not_write_files(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'dataset.json'
            integrator = KimiForgeIntegration()
            integrator.forge_root = Path(directory)
            for action in [integrator.export_training_data,
                           KimiEnhancementToolkit().extract_training_data,
                           lambda: KimiEnhancementToolkit().create_fine_tuning_dataset(str(target))]:
                with self.assertRaises(NotImplementedError):
                    action()
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_design_exports_and_guide_do_not_claim_a_working_trainer(self):
        with tempfile.TemporaryDirectory() as directory:
            integrator = KimiForgeIntegration()
            integrator.forge_root = Path(directory)
            config = integrator.generate_fine_tuning_config()
            self.assertFalse(config['implemented'])
            self.assertIsNone(config['trainer'])
            self.assertIsNone(config['model'])
            guide = integrator.create_integration_guide()
            self.assertIn('does not fine-tune', guide)
            self.assertNotIn('--training-data', guide)
            self.assertNotIn('benchmark_runner.py', guide)
            self.assertEqual(integrator.create_benchmark_improvements()['measured_results'], {})

    def test_script_entrypoints_report_design_status_without_creating_outputs(self):
        for action in [enhancement_main, integration_main]:
            with contextlib.redirect_stdout(io.StringIO()) as output:
                action()
            self.assertNotIn('INTEGRATION COMPLETE', output.getvalue())
            self.assertIn('No model was trained' if action == enhancement_main else 'Design only', output.getvalue())


if __name__ == '__main__':
    unittest.main()
