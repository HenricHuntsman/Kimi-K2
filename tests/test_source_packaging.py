import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from build_system import ForgeBuilder


class SourcePackagingTests(unittest.TestCase):
    def fixture(self, directory):
        builder = ForgeBuilder()
        builder.project_root = Path(directory)
        builder.dist_dir = Path(directory) / 'dist'
        for name in ('forge_implementation.py', 'forge_server.py', 'forge_cli.py',
                     'forge_gui.py', 'forge_local.py', 'requirements.txt', 'README.md', 'LICENSE',
                     'templates/index.html', 'static/app.js', 'docs/nested/guide.md',
                     'tests/test_example.py', '.env', 'tests/__pycache__/test.pyc',
                     'static/.env', 'node_modules/secret.txt'):
            path = Path(directory) / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(name)
        return builder

    def test_bundle_contains_ui_dependencies_tests_and_nested_docs_without_secrets(self):
        with tempfile.TemporaryDirectory() as directory:
            builder = self.fixture(directory)
            archive = builder.create_distribution()
            self.assertIn('prototype_source', archive.name)
            with zipfile.ZipFile(archive) as package:
                self.assertIsNone(package.testzip())
                paths = set(package.namelist())
                self.assertTrue({'requirements.txt', 'LICENSE', 'templates/index.html',
                                 'static/app.js', 'docs/nested/guide.md',
                                 'tests/test_example.py'} <= paths)
                self.assertFalse(any('.env' in p or '__pycache__' in p or
                                     'node_modules' in p for p in paths))

    def test_missing_required_input_fails_before_writing_bundle(self):
        with tempfile.TemporaryDirectory() as directory:
            builder = self.fixture(directory)
            (Path(directory) / 'requirements.txt').unlink()
            with self.assertRaises(FileNotFoundError):
                builder.create_distribution()
            self.assertFalse(builder.dist_dir.exists())

    def test_checksum_matches_archive_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            builder = self.fixture(directory)
            archive = builder.create_distribution()
            builder.generate_checksums()
            record = json.loads((builder.dist_dir / 'checksums.json').read_text())[archive.name]
            self.assertEqual(record['sha256'], hashlib.sha256(archive.read_bytes()).hexdigest())
            self.assertEqual(record['size'], archive.stat().st_size)
