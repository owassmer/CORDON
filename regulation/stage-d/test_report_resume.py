"""Resume valid source blocks without dispatching or editing their readings."""
import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import pymupdf

from cordon_d.report_extraction import ExtractionConfig, extract_report
from cordon_d.reports import report
from cordon_d.store import put_bytes
from test_reports import block


class ReportResume(unittest.TestCase):
    def fixture(self, store):
        with pymupdf.open() as pdf:
            for _ in range(3):
                pdf.new_page()
            digest = put_bytes(store, pdf.tobytes())
        retained = block([['OLD-UNIT', '01/06/2024', 'Negativo', '02/06/2024']])
        retained['targets'] = [1, 2]
        retained['reading']['pages'].append({'page': 2, 'disposition': 'read'})
        retained['request_sha256'] = 'retained-request'
        path = store / 'derived/reports/prior' / digest / 'report.json'
        path.parent.mkdir(parents=True)
        payload = {'source_sha256': digest, 'extraction_version': 'prior', 'page_count': 3,
                   'assembly_complete': False, 'blocks': [retained]}
        path.write_text(json.dumps(payload))
        return digest, path, payload

    def test_resume_preserves_valid_blocks_and_reads_only_remaining_pages(self):
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest, prior, payload = self.fixture(store)
            before = prior.read_bytes()
            response = block([['NEW-UNIT', '03/06/2024', 'Positivo', '04/06/2024']])['reading']
            response['pages'] = [{'page': 3, 'disposition': 'read'}]
            response['tables'][0].update(id='p3-t1', page=3)
            config = ExtractionConfig(provider='subscription', target_pages=1)
            with patch('cordon_d.report_extraction._subscription_call', return_value=response) as provider:
                target = extract_report(digest, store, config=config, budget=None, resume_from='prior')
            self.assertEqual(provider.call_count, 1)
            prompt = provider.call_args.kwargs['prompt']
            self.assertIn('PHYSICAL PAGE 3: TARGET', prompt)
            self.assertIn('PHYSICAL PAGE 1: CONTEXT ONLY', prompt)
            self.assertNotIn('PHYSICAL PAGE 2: TARGET', prompt)
            saved = json.loads(target.read_text())
            self.assertEqual(saved['blocks'][0], payload['blocks'][0])
            self.assertEqual(prior.read_bytes(), before)
            self.assertEqual(saved['replayed_from_extraction_version'], 'prior')
            self.assertTrue(saved['assembly_complete'])
            loaded = report(digest, store, extraction_version=saved['extraction_version'])
            self.assertEqual(loaded.complete_pages, frozenset({1, 2, 3}))
            self.assertEqual([r.reference for r in loaded.rows], ['OLD-UNIT', 'NEW-UNIT'])
            self.assertEqual([r.results[0].kind for r in loaded.rows], ['negative', 'positive'])
            with patch('cordon_d.report_extraction._subscription_call', side_effect=AssertionError('dispatch')):
                self.assertEqual(extract_report(digest, store, config=config, budget=None, resume_from='prior'), target)

    def test_resume_rejects_wrong_source_and_overlapping_or_continuation_blocks(self):
        for defect in ('source', 'overlap', 'continuation'):
            with self.subTest(defect=defect), TemporaryDirectory() as directory:
                store = Path(directory)
                digest, prior, payload = self.fixture(store)
                if defect == 'source':
                    payload['source_sha256'] = 'another-source'
                elif defect == 'overlap':
                    payload['blocks'].append(copy.deepcopy(payload['blocks'][0]))
                else:
                    payload['blocks'].append({'targets': [], 'reading': {}})
                prior.write_text(json.dumps(payload))
                before = prior.read_bytes()
                with patch('cordon_d.report_extraction._subscription_call', side_effect=AssertionError('dispatch')):
                    with self.assertRaises(ValueError):
                        extract_report(digest, store, config=ExtractionConfig(provider='subscription'),
                                       budget=None, resume_from='prior')
                self.assertEqual(prior.read_bytes(), before)
