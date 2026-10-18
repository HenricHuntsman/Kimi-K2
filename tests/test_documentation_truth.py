import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from forge_implementation import ForgeDocumentLoader, ForgeSystemPrompt


class DocumentationTruthTests(unittest.TestCase):
    def test_documentation_readme_does_not_get_overwritten_by_root_readme(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / 'README.md').write_text('Separate documentation index')
            loader = ForgeDocumentLoader(directory)
            with contextlib.redirect_stdout(io.StringIO()):
                loader.load_all_documents()
            self.assertEqual(loader.documents['docs/README.md'], 'Separate documentation index')
            self.assertIn('README.md', loader.documents)
            self.assertNotEqual(loader.documents['README.md'], loader.documents['docs/README.md'])

    def test_reloading_replaces_changed_and_deleted_documents_without_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'proposal.md'
            path.write_text('# OLD CLAIM')
            loader = ForgeDocumentLoader(directory)
            with contextlib.redirect_stdout(io.StringIO()):
                loader.load_all_documents()
                path.write_text('# NEW CLAIM')
                loader.load_all_documents()
            self.assertEqual(loader.all_content.count('# NEW CLAIM'), 1)
            self.assertNotIn('# OLD CLAIM', loader.all_content)
            path.unlink()
            with contextlib.redirect_stdout(io.StringIO()):
                loader.load_all_documents()
            self.assertNotIn('proposal.md', loader.documents)

    def test_exported_prompt_does_not_promote_historical_claims_to_capabilities(self):
        loader = ForgeDocumentLoader()
        loader.documents = {'proposal.md': '# 1450 real tools and never-reset memory'}
        prompt = ForgeSystemPrompt(loader).generate_system_prompt()
        self.assertIn('Historical document index', prompt)
        self.assertIn('proposal.md', prompt)
        self.assertNotIn('1450 real tools', prompt)
        self.assertNotIn('You are built on Kimi', prompt)
        config = ForgeSystemPrompt(loader).generate_for_vllm()
        self.assertEqual(config['status'], 'design_only')
        self.assertEqual(config['model_name'], 'unconfigured')
