"""Transport isolation, replay and source fidelity; no semantic certification."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pymupdf

from cordon_d.document_subscription import read_documents
from cordon_d.store import put_bytes


class DocumentSubscriptionTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.store = Path(temporary.name)
        self.digests = []
        for name in ('ACT', 'ANNEX'):
            document = pymupdf.open()
            document.new_page().insert_text((40, 40), name)
            self.digests.append(put_bytes(self.store, document.tobytes()))
            document.close()
        self.schema = {'type': 'object', 'properties': {'direction': {'type': 'string'}},
                       'required': ['direction'], 'additionalProperties': False}

    def read(self, **options):
        return read_documents(self.digests, self.store, prompt='Read the act and incorporated annex.',
                              schema=self.schema, **options)

    def test_full_sources_and_caller_contract_survive_without_report_fields(self):
        with patch('cordon_d.document_subscription._call', return_value='{"direction":"proposed"}') as call:
            result = self.read(execute=True)
            text, schema, images, directory, model, effort, timeout = call.call_args.args
            self.assertEqual(schema, self.schema)
            self.assertEqual(len(images), 2)
            self.assertLess(text.index('ACT'), text.index('ANNEX'))
            for digest in self.digests:
                self.assertIn(digest, text)
            self.assertEqual((model, effort), ('gpt-5.6-luna', 'high'))
            self.assertEqual(result['request']['sources'], self.digests)
            self.assertEqual(result['reading'], {'direction': 'proposed'})
            self.assertNotIn('complete', result)
            self.assertEqual(self.read()['request_sha256'], result['request_sha256'])
            self.assertEqual(call.call_count, 1)

    def test_configuration_change_cannot_reuse_another_request(self):
        with patch('cordon_d.document_subscription._call', return_value='{}'):
            self.read(execute=True)
        with self.assertRaises(FileNotFoundError):
            self.read(effort='medium')

    def test_concurrent_identical_requests_dispatch_once(self):
        with patch('cordon_d.document_subscription._call', return_value='{}') as call:
            with ThreadPoolExecutor(max_workers=2) as pool:
                jobs = [pool.submit(self.read, execute=True) for _ in range(2)]
                results = [job.result(timeout=10) for job in jobs]
            self.assertEqual(call.call_count, 1)
            self.assertEqual(results[0]['request_sha256'], results[1]['request_sha256'])

    def test_invalid_response_is_retained_without_becoming_a_reading_or_retried(self):
        with patch('cordon_d.document_subscription._call', return_value='incomplete JSON') as call:
            for execute in (True, False):
                with self.assertRaises(json.JSONDecodeError):
                    self.read(execute=execute)
            self.assertEqual(call.call_count, 1)

    def test_transport_disables_tools_and_api_key_fallback(self):
        from types import SimpleNamespace
        from cordon_d.document_subscription import _call
        def run(command, **options):
            self.assertNotIn('OPENAI_API_KEY', options['env'])
            self.assertNotIn('CODEX_API_KEY', options['env'])
            self.assertIn('--ignore-user-config', command)
            self.assertIn('features.shell_tool=false', command)
            self.assertIn('features.multi_agent=false', command)
            self.assertEqual(options['timeout'], 15)
            Path(command[command.index('-o') + 1]).write_text('{}')
            return SimpleNamespace(returncode=0)
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'unused', 'CODEX_API_KEY': 'unused'}), \
                patch('subprocess.run', side_effect=run):
            self.assertEqual(_call('Read source', self.schema, [], self.store,
                                   'gpt-5.6-luna', 'high', 15), '{}')


if __name__ == '__main__':
    unittest.main()
