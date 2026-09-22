"""Transport isolation, replay and source fidelity; no semantic certification."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pymupdf
from jsonschema.exceptions import SchemaError, ValidationError
from referencing.exceptions import Unresolvable

from cordon_d.document_subscription import read_documents, read_retained
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
        with patch('cordon_d.document_subscription._call', return_value='{"direction":"proposed"}'):
            self.read(execute=True)
        with self.assertRaises(FileNotFoundError):
            self.read(effort='medium')

    def test_native_html_keeps_complete_source_and_no_fictitious_page(self):
        html = ('<!doctype html><html><head><meta charset="utf-8"></head><body>\n'
                '<nav>Other work</nav><article><h1>Reported work</h1>\n'
                '<p>Completed before the meeting; exact day unstated.</p>'
                '<img src="https://example.invalid/photo"><script>remote()</script>'
                '</article></body></html>')
        digest = put_bytes(self.store, html.encode())
        with patch('cordon_d.document_subscription._call', return_value='{"direction":"proposed"}') as call:
            result = read_documents([digest], self.store, prompt='Read the reported work.',
                                    schema=self.schema, execute=True,
                                    source_formats={digest: 'text/html'})
            supplied, _, images, *_ = call.call_args.args
            self.assertIn(html, supplied)
            self.assertIn('No scripts are executed or linked assets supplied', supplied)
            self.assertNotIn('PHYSICAL PAGE', supplied)
            self.assertEqual(images, [])
            self.assertEqual(result['request']['source_formats'], {digest: 'text/html'})
            replay = read_documents([digest], self.store, prompt='Read the reported work.',
                                    schema=self.schema, source_formats={digest: 'text/html'})
            self.assertEqual(replay, result)
            self.assertEqual(call.call_count, 1)
            with self.assertRaises(FileNotFoundError):
                read_documents([digest], self.store, prompt='Read the reported work.',
                               schema=self.schema, source_formats={digest: 'text/plain'})

    def test_native_text_context_preserves_pdf_image_and_source_order(self):
        digest = put_bytes(self.store, b'Complete native context\nincluding its qualification.')
        captured = []

        def call(prompt, schema, images, *options):
            captured.extend(image.read_bytes() for image in images)
            return '{"direction":"proposed"}'

        with patch('cordon_d.document_subscription._call', side_effect=call):
            result = read_documents([digest, self.digests[0]], self.store, prompt='Read sources.',
                                    schema=self.schema, execute=True,
                                    source_formats={digest: 'text/plain'})
        self.assertEqual(len(captured), 1)
        self.assertLess(result['request']['prompt'].index(digest),
                        result['request']['prompt'].index(self.digests[0]))
        pdf = self.store / 'blobs/sha256' / self.digests[0][:2] / self.digests[0]
        with pymupdf.open(pdf) as document:
            self.assertEqual(captured[0], document[0].get_pixmap(dpi=180).tobytes('png'))

    def test_native_text_declaration_never_silently_changes_supplied_bytes(self):
        digest = put_bytes(self.store, b'\xffnot UTF-8')
        with patch('cordon_d.document_subscription._call') as call:
            for formats in ({'f' * 64: 'text/html'}, {digest: 'image/png'}):
                with self.assertRaises(ValueError):
                    read_documents([digest], self.store, prompt='Read.', schema=self.schema,
                                   execute=True, source_formats=formats)
            with self.assertRaises(UnicodeDecodeError):
                read_documents([digest], self.store, prompt='Read.', schema=self.schema,
                               execute=True, source_formats={digest: 'text/html'})
            call.assert_not_called()

    def test_default_presentation_preserves_original_request_identity(self):
        prompt = ('Read the act and incorporated annex.\nOriginal source images follow in '
                  'document order, then physical page order. Source hashes identify bytes, '
                  'not interpreted document relationships.\n')
        hashes = []
        for digest in self.digests:
            source = self.store / 'blobs/sha256' / digest[:2] / digest
            with pymupdf.open(source) as document:
                prompt += f'\nDOCUMENT {digest}; {len(document)} page images\n'
                for number, page in enumerate(document, 1):
                    prompt += f'PHYSICAL PAGE {number}\n{page.get_text(sort=True)}\n'
                    hashes.append(sha256(page.get_pixmap(dpi=180).tobytes('png')).hexdigest())
                prompt += 'END DOCUMENT\n'
        original = {'transport_version': 1, 'provider': 'codex-subscription',
                    'model': 'gpt-5.6-luna', 'effort': 'high', 'sources': self.digests,
                    'prompt': prompt, 'schema': self.schema, 'images': hashes, 'dpi': 180}
        with patch('cordon_d.document_subscription._call', return_value='{"direction":"proposed"}') as call:
            response = self.read(execute=True)
            self.assertEqual(response['request'], original)
            self.assertEqual(response['request_sha256'],
                             sha256(json.dumps(original, sort_keys=True).encode()).hexdigest())
            self.assertEqual(self.read(supplement_page_rotations=False), response)
            with self.assertRaises(FileNotFoundError):
                self.read(supplement_page_rotations=True)
            self.assertEqual(call.call_count, 1)

    def rotated_image_source(self, page_rotation=0):
        with pymupdf.open() as image_document:
            image_page = image_document.new_page(width=100, height=60)
            image_page.draw_rect((0, 0, 50, 60), color=None, fill=(1, 0, 0))
            image_page.draw_rect((50, 0, 100, 30), color=None, fill=(0, 0, 1))
            # The transparent quadrant becomes a PDF image mask.
            png = image_page.get_pixmap(alpha=True).tobytes('png')
        with pymupdf.open() as document:
            page = document.new_page(width=180, height=120)
            page.draw_rect(page.rect, color=None, fill=(0, 1, 0))
            for rect in ((10, 10, 110, 110), (140, 10, 160, 30)):
                page.insert_image(rect, stream=png, rotate=90, keep_proportion=False)
            page.draw_rect((30, 30, 70, 70), color=None, fill=(0, 0, 0))
            page.set_cropbox((20, 0, 170, 120))
            page.set_rotation(page_rotation)
            return put_bytes(self.store, document.tobytes())

    def test_supplemental_views_preserve_visible_page_and_attachment_provenance(self):
        digest = self.rotated_image_source()
        captured = []

        def call(prompt, schema, images, *options):
            captured.extend(image.read_bytes() for image in images)
            return '{"direction":"proposed"}'

        with patch('cordon_d.document_subscription._call', side_effect=call):
            response = read_documents([digest, self.digests[1]], self.store,
                                      prompt='Read source', schema=self.schema, dpi=72,
                                      execute=True, supplement_page_rotations=True)
        self.assertEqual(len(captured), 3)  # Both originals precede the one duplicate view.
        original, supplementary = pymupdf.Pixmap(captured[0]), pymupdf.Pixmap(captured[2])
        self.assertEqual((original.width, original.height), (150, 120))
        self.assertEqual((supplementary.width, supplementary.height), (120, 150))
        # Exact visible pixel rotation retains crop, transparent mask and black overlay.
        for y in range(original.height):
            for x in range(original.width):
                self.assertEqual(original.pixel(x, y),
                                 supplementary.pixel(original.height - 1 - y, x))
        self.assertEqual(original.pixel(25, 45), (0, 0, 0))
        self.assertEqual(original.pixel(100, 100), (0, 255, 0))
        view, = response['request']['supplemental_page_rotations']
        self.assertEqual((view['source'], view['page'], view['clockwise_degrees'],
                          view['page_rotation'], view['image_index']), (digest, 1, 90, 0, 3))
        self.assertEqual([entry['occurrence'] for entry in view['image_occurrences']], [1, 2])
        source = self.store / 'blobs/sha256' / digest[:2] / digest
        with pymupdf.open(source) as document:
            self.assertTrue(all(entry['has-mask'] for entry in document[0].get_image_info()))
            self.assertEqual([entry['transform'] for entry in view['image_occurrences']],
                             [list(entry['transform']) for entry in document[0].get_image_info()])
        self.assertEqual(view['image_sha256'], sha256(captured[2]).hexdigest())
        self.assertEqual(response['request']['images'], [sha256(png).hexdigest() for png in captured])
        self.assertIn(json.dumps(view, sort_keys=True), response['request']['prompt'])
        self.assertEqual(read_retained(response['request_sha256'], self.store), response)

    def test_page_rotation_composes_before_supplemental_rotation(self):
        for page_rotation, expected in ((0, [90]), (90, []), (180, [270]), (270, [180])):
            with self.subTest(page_rotation=page_rotation):
                digest = self.rotated_image_source(page_rotation)
                with patch('cordon_d.document_subscription._call', return_value='{"direction":"proposed"}'):
                    response = read_documents([digest], self.store, prompt='Read source',
                                              schema=self.schema, dpi=72, execute=True,
                                              supplement_page_rotations=True)
                views = response['request']['supplemental_page_rotations']
                self.assertEqual([view['clockwise_degrees'] for view in views], expected)
                self.assertTrue(all(view['page_rotation'] == page_rotation for view in views))

    def test_shear_reflection_and_nonorthogonal_placements_do_not_infer_rotation(self):
        from types import SimpleNamespace
        from cordon_d.document_subscription import _image_rotation_views
        for transform in ((1, 0, 0, 1, 0, 0), (-1, 0, 0, 1, 0, 0),
                          (0, -1, -1, 0, 0, 0), (1, 0.1, 0, 1, 0, 0),
                          (0.707, -0.707, 0.707, 0.707, 0, 0),
                          (0, -1, 1, 0.000001, 0, 0)):
            with self.subTest(transform=transform):
                page = SimpleNamespace(rotation_matrix=pymupdf.Matrix(1, 1),
                                       get_image_info=lambda: [{'transform': transform}])
                self.assertEqual(_image_rotation_views(page), {})

    def test_named_replay_preserves_original_context_and_checks_request_integrity(self):
        with patch('cordon_d.document_subscription._call', return_value='{"direction":"proposed"}') as call:
            response = self.read(execute=True)
            request_id = response['request_sha256']
            replayed = read_retained(request_id, self.store)
            self.assertEqual(replayed, response)
            self.assertEqual(call.call_count, 1)
        retained = self.store / 'derived/document-readings' / (request_id + '.json')
        altered = json.loads(retained.read_text())
        altered['request']['prompt'] = 'Different evidence'
        retained.write_text(json.dumps(altered))
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            read_retained(request_id, self.store)

    def test_concurrent_identical_requests_dispatch_once(self):
        with patch('cordon_d.document_subscription._call', return_value='{"direction":"proposed"}') as call:
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

    def test_schema_invalid_json_is_retained_and_rejected_on_every_return_path(self):
        for value in ({}, {'direction': 17}, {'direction': 'proposed', 'unexpected': True}):
            with self.subTest(value=value), TemporaryDirectory() as temporary:
                store = Path(temporary)
                document = pymupdf.open()
                document.new_page().insert_text((40, 40), 'Schema boundary')
                digest = put_bytes(store, document.tobytes())
                document.close()
                output = json.dumps(value)
                with patch('cordon_d.document_subscription._call', return_value=output) as call:
                    for execute in (True, False, True):
                        with self.assertRaises(ValidationError):
                            read_documents([digest], store, prompt='Read direction.',
                                           schema=self.schema, execute=execute)
                    self.assertEqual(call.call_count, 1)
                retained, = (store / 'derived/document-readings').glob('*.json')
                self.assertEqual(json.loads(retained.read_text())['output'], output)

    def test_invalid_schema_is_rejected_before_dispatch(self):
        self.schema = {'type': 'not-a-json-schema-type'}
        with patch('cordon_d.document_subscription._call') as call:
            with self.assertRaises(SchemaError):
                self.read(execute=True)
            call.assert_not_called()

    def test_nonfinite_numbers_are_rejected_without_retry(self):
        schema = {'type': 'object', 'properties': {'distance': {'type': 'number',
                  'minimum': 0, 'maximum': 50}}, 'required': ['distance']}
        for token in ('NaN', 'Infinity', '-Infinity', '1e999'):
            with self.subTest(token=token), TemporaryDirectory() as temporary:
                store = Path(temporary)
                source = self.store / 'blobs/sha256' / self.digests[0][:2] / self.digests[0]
                digest = put_bytes(store, source.read_bytes())
                output = '{"distance": ' + token + '}'
                with patch('cordon_d.document_subscription._call', return_value=output) as call:
                    for execute in (True, False, True):
                        with self.assertRaises(ValueError):
                            read_documents([digest], store, prompt='Read distance.',
                                           schema=schema, execute=execute)
                    self.assertEqual(call.call_count, 1)
                retained, = (store / 'derived/document-readings').glob('*.json')
                self.assertEqual(json.loads(retained.read_text())['output'], output)

        with patch('cordon_d.document_subscription._call', return_value='{"distance":25.5}') as call:
            for execute in (True, False):
                result = read_documents(self.digests, self.store, prompt='Read distance.',
                                        schema=schema, execute=execute)
                self.assertEqual(result['reading'], {'distance': 25.5})
            self.assertEqual(call.call_count, 1)

    def test_schema_references_resolve_locally_without_network_retrieval(self):
        self.schema = {'$defs': {'measure': self.schema}, '$ref': '#/$defs/measure'}
        with patch('cordon_d.document_subscription._call', return_value='{"direction":"proposed"}'), \
                patch('urllib.request.urlopen', side_effect=AssertionError('Network retrieval')) as network:
            self.assertEqual(self.read(execute=True)['reading'], {'direction': 'proposed'})
            self.assertEqual(self.read()['reading'], {'direction': 'proposed'})
            self.schema = {'$ref': 'https://example.invalid/measure-schema'}
            for execute in (True, False):
                with self.assertRaises(Unresolvable):
                    self.read(execute=execute)
            network.assert_not_called()

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
