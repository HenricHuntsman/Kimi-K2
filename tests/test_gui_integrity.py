import contextlib
import io
from pathlib import Path
import tempfile
import unittest
import runpy
from unittest.mock import patch

import forge_gui
from forge_implementation import ForgeAI


class GuiIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        (Path(self.directory.name) / 'example.md').write_text('Historical proposal')
        self.previous = forge_gui.forge
        self.addCleanup(setattr, forge_gui, 'forge', self.previous)
        with contextlib.redirect_stdout(io.StringIO()):
            forge_gui.forge = ForgeAI(self.directory.name).initialize()
        self.client = forge_gui.app.test_client()

    def test_init_reports_document_counts_not_implemented_capabilities(self):
        response = self.client.get('/api/init')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'demonstration')
        self.assertFalse(data['model_loaded'])
        self.assertEqual(data['documents_loaded'], 2)  # fixture plus root README
        self.assertEqual(data['total_capabilities'], 0)

    def test_tools_never_return_fabricated_success_or_quality(self):
        for tool in ['code-review', 'book-analyze', 'image-upscale', 'video-edit', 'missing']:
            with self.subTest(tool=tool):
                response = self.client.post('/api/tools/' + tool, json={})
                self.assertEqual(response.status_code, 404 if tool == 'missing' else 501)
                data = response.get_json()
                self.assertFalse(data['executed'])
                self.assertTrue(data['demo'])
                self.assertNotIn('85%', data['result'])
                self.assertNotIn('92/100', data['result'])

    def test_chat_identifies_echo_and_rejects_invalid_payloads(self):
        response = self.client.post('/api/chat', json={'message': 'hello'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('DEMO', response.get_json()['message'])
        self.assertFalse(response.get_json()['model_loaded'])
        for payload in [None, [], {'message': 5}, {'message': 'hello', 'mode': []}]:
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post('/api/chat', json=payload).status_code, 400)

    def test_documentation_endpoint_reads_real_loader_content(self):
        response = self.client.get('/api/documentation/example.md')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['content'], 'Historical proposal')
        self.assertEqual(self.client.get('/api/documentation/missing.md').status_code, 404)

    def test_catalogue_and_skill_counts_do_not_invent_implementations(self):
        self.assertEqual(self.client.get('/api/capabilities').get_json(), {})
        self.assertEqual(self.client.get('/api/skills').get_json()['total'], 0)

    def test_development_entry_point_binds_loopback_without_debug(self):
        with patch('flask.Flask.run') as run, contextlib.redirect_stdout(io.StringIO()):
            runpy.run_module('forge_gui', run_name='__main__')
        run.assert_called_once_with(debug=False, host='127.0.0.1', port=5000)


if __name__ == '__main__':
    unittest.main()
