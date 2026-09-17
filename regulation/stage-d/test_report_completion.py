"""Consumer regressions for replacement ancestry and persisted assembly failure.

Provider responses are fixtures; no network call or source-transcription claim.
"""
import copy
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pymupdf
from openpyxl import Workbook

from cordon_c.core import Evaluation
from cordon_d.findings import findings, confirmation_inputs, report_rows
from cordon_d.monitoring import distinct_observations
from cordon_d import report_relations
from cordon_d.report_extraction import ExtractionConfig, extract_report, version
from cordon_d.reports import report
from cordon_d.store import file_digest, put_bytes
from test_report_relations import reading
from test_reports import block


class ReportCompletion(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.base = Path(directory.name)
        self.store = self.base / 'store'
        environment = patch.dict(os.environ, CORDON_STORE=str(self.store))
        environment.start()
        self.addCleanup(environment.stop)
        self.reports = self.base / 'reports'
        self.reports.mkdir()
        self.monitoring = self.base / 'monitoring'
        (self.monitoring / 'campaign').mkdir(parents=True)
        self.captures = []
        self.identities = {}

    def add_report(self, label, *, predecessors=(), item=None, number=None, date='01/03/2024'):
        number = number or label + '/2024'
        with pymupdf.open() as pdf:
            pdf.new_page().insert_text((40, 40), 'Laboratory A ' + number + ' ' + date)
            digest = put_bytes(self.store, pdf.tobytes())
        route = 'https://publisher.example/' + label + '.pdf'
        self.captures.append({'url': route, 'sha256': digest,
                              'captured_at': '2026-01-01T00:00:00+00:00'})
        relations = reading(number=number, date=date).relations
        for predecessor in predecessors:
            relations['corrections'].extend(reading(previous=self.identities[predecessor]).relations['corrections'])
        self.identities[label] = relations['identity']
        target = report_relations.path(self.store, digest)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({'source_sha256': digest, 'reading_version': report_relations.READING_VERSION,
                                      'complete': True, 'reading': relations}))
        target = self.store / 'derived/reports/v' / digest / 'report.json'
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps({'source_sha256': digest, 'extraction_version': 'v',
            'page_count': 1, 'assembly_complete': True,
            'blocks': [item or block([['00123', '01/06/2024', 'Positivo', '02/06/2024']])]}))
        return digest, route, target

    def join(self, route, revision='v'):
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(['ID', 'DATA_RILEVAMENTO', 'RISULTATO', 'DOCUMENTO_CONFERMA'])
        sheet.append(['00123', datetime(2024, 6, 1), 'POSITIVO', route])
        target = self.monitoring / 'campaign/release.xlsx'
        workbook.save(target)
        (target.parent / 'releases.json').write_text(json.dumps([{
            'url': 'https://publisher.example/release.xlsx', 'path': target.name,
            'sha256': file_digest(target)}]))
        (self.reports / 'records.json').write_text(json.dumps(self.captures))
        return list(findings(distinct_observations(self.monitoring), self.reports, self.store,
            extraction_version=revision, known_through=datetime(2026, 2, 1, tzinfo=timezone.utc)))[0]

    def test_replacement_fork_survives_descendants_from_every_entry_route(self):
        a, route_a, _ = self.add_report('A')
        b, route_b, _ = self.add_report('B', predecessors=['A'])
        c, route_c, _ = self.add_report('C', predecessors=['A'])
        for route in (route_a, route_b, route_c):
            with self.subTest(phase='direct fork', route=route):
                self.assertEqual(self.join(route)['matches'], [])
        d, route_d, _ = self.add_report('D', predecessors=['C'])
        for route in (route_a, route_b, route_c, route_d):
            with self.subTest(phase='extended fork', route=route):
                joined = self.join(route)
                self.assertEqual(joined['matches'], [])
                self.assertTrue(any('competing' in (link['document_cause'] or '') for link in joined['links']))
        # E expressly replaces BOTH surviving branches. No date or route resolves it.
        e, route_e, _ = self.add_report('E', predecessors=['B', 'D'])
        for route in (route_a, route_b, route_c, route_d, route_e):
            with self.subTest(phase='explicit reconciliation', route=route):
                joined = self.join(route)
                self.assertEqual(joined['status'], 'matched')
                self.assertEqual({m['key'][0] for m in joined['matches']}, {e})

    def test_unread_successor_still_disqualifies_replaced_report(self):
        a, route, _ = self.add_report('A')
        b, _, payload = self.add_report('B', predecessors=['A'])
        payload.unlink()
        joined = self.join(route)
        self.assertEqual(joined['matches'], [])
        self.assertEqual({link['sha256'] for link in joined['links']}, {a, b})

    def test_unrelated_rows_are_not_materialized(self):
        a, route, _ = self.add_report('A')
        self.add_report('Unrelated')
        with patch('cordon_d.findings.report', wraps=report) as loader:
            joined = self.join(route)
        self.assertEqual(joined['status'], 'matched')
        self.assertEqual([call.args[0] for call in loader.call_args_list], [a])

    def test_ordinary_replacement_chain_remains_usable(self):
        a, route_a, _ = self.add_report('A')
        c, route_c, _ = self.add_report('C', predecessors=['A'])
        d, route_d, _ = self.add_report('D', predecessors=['C'])
        for route in (route_a, route_c, route_d):
            with self.subTest(route=route):
                joined = self.join(route)
                self.assertEqual(joined['status'], 'matched')
                self.assertEqual({m['key'][0] for m in joined['matches']}, {d})

    def test_potential_predecessor_in_ancestry_remains_consequential(self):
        a, route_a, _ = self.add_report('A')
        a2, _, _ = self.add_report('A2', number='A/2024', date='02/03/2024')
        b, route_b, _ = self.add_report('B', predecessors=['A'])
        d, route_d, _ = self.add_report('D', predecessors=['B'])
        c, route_c, _ = self.add_report('C', predecessors=['A'])
        target = report_relations.path(self.store, c)
        payload = json.loads(target.read_text())
        previous = payload['reading']['corrections'][0]['predecessor']
        previous['date'] = None
        previous['component_support']['date'] = []
        target.write_text(json.dumps(payload))
        sources = {digest: report(digest, self.store, extraction_version='v') for digest in (a, a2, b, c, d)}
        edge, = [e for e in report_relations.correspondences(sources) if e['successor'] == c]
        self.assertEqual(set(edge['candidates']), {a, a2})
        self.assertEqual(edge['status'], 'unresolved')
        for route in (route_a, route_b, route_c, route_d):
            with self.subTest(phase='ambiguous predecessor', route=route):
                joined = self.join(route)
                self.assertEqual(joined['matches'], [])
                self.assertTrue(any(link['document_cause'] for link in joined['links']))
        # A source-supported date identifies the other A, outside D's ancestry.
        payload['reading']['corrections'][0]['predecessor'] = self.identities['A2']
        target.write_text(json.dumps(payload))
        for route in (route_a, route_b, route_d):
            with self.subTest(phase='disjoint predecessor', route=route):
                self.assertEqual({m['key'][0] for m in self.join(route)['matches']}, {d})
        # Restoring uncertainty is also resolvable by explicit whole-report reconciliation.
        payload['reading']['corrections'][0]['predecessor'] = previous
        target.write_text(json.dumps(payload))
        e, route_e, _ = self.add_report('E', predecessors=['C', 'D'])
        for route in (route_a, route_b, route_c, route_d, route_e):
            with self.subTest(phase='explicit reconciliation', route=route):
                joined = self.join(route)
                self.assertEqual(joined['status'], 'matched')
                self.assertEqual({m['key'][0] for m in joined['matches']}, {e})

    def test_unresolved_amendment_scope_is_not_erased_by_descendants(self):
        a, route_a, _ = self.add_report('A')
        b, route_b, _ = self.add_report('B', predecessors=['A'])
        d, route_d, _ = self.add_report('D', predecessors=['B'])
        c, _, _ = self.add_report('C', predecessors=['A'])
        target = report_relations.path(self.store, c)
        payload = json.loads(target.read_text())
        payload['reading']['corrections'][0]['effect'] = 'amends'
        target.write_text(json.dumps(payload))
        for route in (route_a, route_b, route_d):
            with self.subTest(route=route):
                self.assertEqual(self.join(route)['matches'], [])

    def test_failed_continuation_producer_cannot_supply_complete_consumer_evidence(self):
        for failure in ('issue', 'no facts', None):
            with self.subTest(failure=failure):
                item = block([['00123', '01/06/2024', 'Positivo', '02/06/2024']])
                table = item['reading']['tables'][0]
                table['columns'].append(dict(table['columns'][2], heading=['Esito B'], test='Esito B'))
                table['rows'][0]['cells'].append({'text': 'Positivo'})
                tail = copy.deepcopy(table)
                tail['id'] = 'p1-tail'
                tail['columns'] = [dict(table['columns'][2], heading=['Esito C'], test='Esito C')]
                tail['rows'][0]['cells'] = [{'text': 'Negativo'}]
                item['reading']['tables'].append(tail)
                digest, route, prior = self.add_report('repair-' + str(failure), item=item)
                original = prior.read_bytes()
                response = {'pages': [], 'tables': [], 'context_pages': [1], 'issues': [], 'facts': []}
                if failure == 'issue':
                    response['issues'] = [{'scope': 'report', 'cause': 'required record continuation remains unresolved'}]
                elif failure is None:
                    response['facts'] = [{'id': 'continuation', 'role': 'record_continuation', 'page': 1,
                        'locator': 'identity header', 'text': '00123', 'value': '00123',
                        'applies_to': ['p1-t1/r1', 'p1-tail/r1']}]
                config = ExtractionConfig(provider='subscription')
                with patch('cordon_d.report_extraction._subscription_call', return_value=response):
                    if failure:
                        with self.assertRaisesRegex(ValueError, 'relationships remain unresolved'):
                            extract_report(digest, self.store, config=config, budget=None, continuation_from='v')
                    else:
                        extract_report(digest, self.store, config=config, budget=None, continuation_from='v')
                revision = version(config)
                saved = json.loads((self.store / 'derived/reports' / revision / digest / 'report.json').read_text())
                self.assertEqual(prior.read_bytes(), original)
                self.assertEqual(saved['blocks'][0], item)
                self.assertEqual(saved['blocks'][-1]['targets'], [])
                self.assertIs(saved['assembly_complete'], failure is None)
                loaded = report(digest, self.store, extraction_version=revision)
                self.assertEqual(loaded.complete_pages, frozenset({1}))
                self.assertTrue(loaded.relations['reading_complete'])
                self.assertEqual(len(loaded.rows), 2)
                self.assertEqual(len(loaded.rows[0].results), 2)
                self.assertEqual(loaded.rows[1].results[0].kind, 'negative')
                self.assertIs(loaded.assembly_complete, failure is None)
                joined = self.join(route, revision)
                self.assertEqual(joined['status'], 'provisional-match' if failure else 'matched')
                candidate, = joined['matches']
                self.assertIs(candidate['reading_complete'], failure is None)
                self.assertIs(candidate['assembly_complete'], failure is None)
                pair = [(digest, r.locator) for r in candidate['row'].results[:2]]
                inputs = confirmation_inputs(joined, result_pair=pair, qualification={
                    'first_annex_iv': Evaluation(True), 'second_annex_iv': Evaluation(True),
                    'inside_demarcated_area': Evaluation(True)})
                for side in ('first', 'second'):
                    value = inputs[side + '_positive_annex_iv']
                    self.assertIs(value.truth, None if failure else True)
                    if failure:
                        self.assertTrue(any('assembly' in need for need in value.needs))
                self.assertTrue(inputs['inside_demarcated_area'].truth)
                reverse = list(report_rows([loaded], [joined]))
                self.assertEqual(len(reverse), 2)
                self.assertTrue(reverse[0]['observations'])
                self.assertEqual(bool(reverse[1]['observations']), failure is None)
                # The unchanged, separately completed version remains usable.
                self.assertEqual(self.join(route)['status'], 'matched')

    def test_missing_assembly_attestation_is_not_completion(self):
        digest, route, target = self.add_report('legacy')
        payload = json.loads(target.read_text())
        del payload['assembly_complete']
        target.write_text(json.dumps(payload))
        joined = self.join(route)
        self.assertEqual(joined['status'], 'provisional-match')
        self.assertIsNone(joined['matches'][0]['assembly_complete'])
        self.assertFalse(joined['matches'][0]['reading_complete'])


if __name__ == '__main__':
    unittest.main()
