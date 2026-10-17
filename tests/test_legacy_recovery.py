import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from forge_cli import ForgeCLI
from forge_implementation import ForgeAI
import forge_server


class LegacyRecoveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        (Path(temporary.name) / 'example.md').write_text('Recovery fixture')
        with contextlib.redirect_stdout(io.StringIO()):
            self.forge = ForgeAI(temporary.name).initialize()
        previous = forge_server.forge
        self.addCleanup(setattr, forge_server, 'forge', previous)
        forge_server.forge = self.forge
        forge_server.conversation_history.clear()
        self.addCleanup(forge_server.conversation_history.clear)
        self.client = forge_server.app.test_client()

    def test_cli_stats_and_caps_use_existing_documentation_api(self):
        cli = ForgeCLI()
        cli.forge = self.forge
        with contextlib.redirect_stdout(io.StringIO()) as output:
            cli.handle_command('/stats')
            cli.handle_command('/caps')
        self.assertIn('Documentation entries loaded: 2', output.getvalue())
        self.assertIn('Implemented executable tools: 0', output.getvalue())

    def test_rest_stats_and_capabilities_no_longer_raise_missing_api(self):
        stats = self.client.get('/api/stats')
        self.assertEqual(stats.status_code, 200)
        self.assertEqual(stats.get_json()['documentation']['files_loaded'], 2)
        capabilities = self.client.get('/api/capabilities')
        self.assertEqual(capabilities.status_code, 200)
        self.assertEqual(capabilities.get_json()['capabilities'], [])

    def test_documentation_contains_loaded_content(self):
        response = self.client.get('/api/documentation')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['total_files'], 2)
        self.assertIn('Recovery fixture', [d['content'] for d in data['documents']])

    def test_chat_history_preserves_real_session_without_fake_tool_use(self):
        response = self.client.post('/api/chat', json={'message': 'write code', 'session_id': 'fixture'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'demonstration')
        self.assertEqual(response.get_json()['capabilities_used'], [])
        history = self.client.get('/api/sessions/fixture/history').get_json()
        self.assertEqual(history['message_count'], 2)
        self.assertEqual(history['messages'][0]['content'], 'write code')
        self.client.delete('/api/sessions/fixture')
        self.assertEqual(self.client.get('/api/sessions/fixture/history').status_code, 404)

    def test_code_review_retains_real_text_checks_without_quality_score(self):
        data = self.client.post('/api/code-review', json={'code': '# TODO\npass'}).get_json()
        self.assertIsNone(data['quality_score'])
        self.assertEqual(data['lines_reviewed'], 2)
        self.assertEqual(data['issues'][0]['type'], 'todo')

    def test_book_counts_do_not_invent_quality_or_sequel_potential(self):
        data = self.client.post('/api/book-writing/analyze', json={'content': 'one two\n\nthree'}).get_json()
        self.assertEqual(data['statistics']['word_count'], 3)
        self.assertEqual(data['statistics']['paragraph_count'], 2)
        self.assertIsNone(data['quality_score'])
        self.assertIsNone(data['sequel_potential'])

    def test_invalid_payloads_are_rejected_before_session_changes(self):
        for route, payload in [('/api/chat', []), ('/api/chat', {'message': 'x', 'session_id': []}), ('/api/code-review', {'code': []}), ('/api/book-writing/analyze', {'content': 5})]:
            with self.subTest(route=route, payload=payload):
                self.assertEqual(self.client.post(route, json=payload).status_code, 400)
        self.assertEqual(forge_server.conversation_history, {})


if __name__ == '__main__':
    unittest.main()
