"""Protocol tests against a loopback fixture, not real model inference."""
import contextlib
import io
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import time
import unittest
from unittest.mock import patch

from forge_local import LocalModelError, LocalOllama, main
import forge_gui
import forge_cli


class LocalOllamaTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.cloud_disabled = True
        self.show = {'model_info': {'general.architecture': 'qwen2'}}
        self.answer = {'model': 'qwen2.5-coder:7b', 'done': True,
                       'message': {'role': 'assistant', 'content': 'Fixture answer'}}
        self.status_code = 200
        self.redirect = False
        self.delay = 0
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                self.respond(None)

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                self.respond(body)

            def respond(self, body):
                owner.calls.append((self.path, body))
                if owner.delay:
                    time.sleep(owner.delay)
                if owner.redirect:
                    self.send_response(302)
                    self.send_header('Location', '/leak')
                    self.end_headers()
                    return
                value = ({'cloud': {'disabled': owner.cloud_disabled}}
                         if self.path == '/api/status' else owner.show
                         if self.path == '/api/show' else owner.answer)
                self.send_response(owner.status_code)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                try:
                    self.wfile.write(json.dumps(value).encode())
                except BrokenPipeError:
                    pass

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={'poll_interval': 0.01}, daemon=True)
        self.thread.start()
        self.addCleanup(self.cleanup_server)
        self.endpoint = f'http://127.0.0.1:{self.server.server_port}'
        self.client = LocalOllama(endpoint=self.endpoint)

    def cleanup_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_chat_uses_native_local_api_without_proxy_tools_or_streaming(self):
        with patch.dict(os.environ, {'http_proxy': 'http://192.0.2.1:1',
                                    'HTTP_PROXY': 'http://192.0.2.1:1', 'NO_PROXY': ''}):
            result = self.client.chat([{'role': 'user', 'content': 'hello'}])
        self.assertEqual(result['message'], 'Fixture answer')
        self.assertFalse(result['demo'])
        self.assertEqual([c[0] for c in self.calls], ['/api/status', '/api/show', '/api/chat'])
        payload = self.calls[-1][1]
        self.assertFalse(payload['stream'])
        self.assertNotIn('tools', payload)

    def test_cloud_policy_fails_before_prompt_is_sent(self):
        self.cloud_disabled = False
        with self.assertRaisesRegex(LocalModelError, 'cloud disabled'):
            self.client.chat([{'role': 'user', 'content': 'private fixture'}])
        self.assertEqual(self.calls, [('/api/status', None)])

    def test_remote_model_or_missing_metadata_never_receives_chat(self):
        for info in [{'remote_host': 'https://example.com', 'model_info': {'a': 1}},
                     {'remote_model': 'remote', 'model_info': {'a': 1}}, {}]:
            with self.subTest(info=info):
                self.show = info
                self.calls.clear()
                with self.assertRaises(LocalModelError):
                    self.client.chat([{'role': 'user', 'content': 'hello'}])
                self.assertNotIn('/api/chat', [c[0] for c in self.calls])

    def test_redirect_is_not_followed(self):
        self.redirect = True
        with self.assertRaisesRegex(LocalModelError, 'redirect'):
            self.client.check_local()
        self.assertEqual(self.calls, [('/api/status', None)])

    def test_http_error_and_timeout_are_explicit(self):
        self.status_code = 404
        with self.assertRaisesRegex(LocalModelError, 'HTTP 404'):
            self.client.check_local()
        with contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(main(['--endpoint', self.endpoint, '--check']), 1)
        self.assertIn('HTTP 404', errors.getvalue())
        self.status_code = 200
        self.delay = 0.1
        with self.assertRaisesRegex(LocalModelError, 'timed out'):
            LocalOllama(endpoint=self.endpoint, timeout=0.01).check_local()

    def test_invalid_input_and_cloud_names_fail_before_network(self):
        for messages in [[], [{}], [{'role': 'tool', 'content': 'x'}],
                         [{'role': 'user', 'content': ''}],
                         [{'role': 'user', 'content': '\ud800'}],
                         [{'role': 'user', 'content': 'x' * (128 * 1024 + 1)}]]:
            with self.subTest(messages=str(messages)[:50]), self.assertRaises(LocalModelError):
                self.client.chat(messages)
        for model in ['qwen:cloud', 'qwen-cloud', 'bad name']:
            with self.assertRaises(LocalModelError):
                LocalOllama(model=model)
        for endpoint in ['https://example.com', 'http://192.0.2.1',
                         'http://127.0.0.1:0', 'http://user@localhost',
                         'http://localhost/api', 'http://localhost?x=1']:
            with self.assertRaises(LocalModelError):
                LocalOllama(endpoint=endpoint)
        self.assertEqual(self.calls, [])

    def test_incomplete_tool_only_and_oversized_answers_are_rejected(self):
        original = self.answer
        for answer in [[], {'done': False},
                       {**original, 'message': {'role': 'assistant', 'content': ''}},
                       {**original, 'message': {**original['message'], 'tool_calls': [{}]}},
                       {**original, 'remote_host': 'https://example.com'}]:
            self.answer = answer
            with self.subTest(answer=answer), self.assertRaises(LocalModelError):
                self.client.chat([{'role': 'user', 'content': 'hello'}])
        self.answer = original
        self.client.max_response = 100
        with self.assertRaisesRegex(LocalModelError, '2 MiB'):
            self.client.chat([{'role': 'user', 'content': 'hello'}])

    def test_cli_check_and_one_shot_run_the_real_adapter(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(['--endpoint', self.endpoint, '--check']), 0)
            self.assertEqual(main(['--endpoint', self.endpoint, 'hello']), 0)
            with patch.object(sys, 'argv', ['forge_cli.py', '--local', '--endpoint', self.endpoint, 'hello']):
                self.assertEqual(forge_cli.main(), 0)
        self.assertIn('Fixture answer', output.getvalue())
        self.assertIn('"inference_verified": false', output.getvalue())

    def test_gui_local_mode_never_falls_back_to_demo(self):
        env = {'FORGE_BACKEND': 'ollama', 'FORGE_OLLAMA_URL': self.endpoint}
        with patch.dict(os.environ, env), patch.object(forge_gui, 'init_forge'):
            client = forge_gui.app.test_client()
            result = client.post('/api/chat', json={'message': 'hello'})
            self.assertEqual(result.status_code, 200)
            self.assertFalse(result.get_json()['demo'])
            self.cloud_disabled = False
            failure = client.post('/api/chat', json={'message': 'hello'})
            self.assertEqual(failure.status_code, 503)
            self.assertNotIn('message', failure.get_json())
            self.assertFalse(failure.get_json()['inference_verified'])

    def test_smoke_report_measures_one_request_and_does_not_claim_model_quality(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(['--endpoint', self.endpoint, '--smoke']), 2)
        report = json.loads(output.getvalue())
        self.assertEqual(report['status'], 'smoke_mismatch')
        self.assertFalse(report['model_quality_verified'])
        self.assertEqual(report['tools_executed'], 0)
        self.assertGreaterEqual(report['request_elapsed_seconds'], 0)
        self.answer['message']['content'] = 'FORGE_LOCAL_OK'
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(['--endpoint', self.endpoint, '--smoke']), 0)
        self.assertEqual(json.loads(output.getvalue())['status'], 'smoke_passed')


if __name__ == '__main__':
    unittest.main()
