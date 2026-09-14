"""Joins through actual release fixtures and the accepted observation grouping."""
from datetime import datetime, timezone
import json
import copy
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from openpyxl import Workbook
from cordon_d.findings import findings, confirmation_inputs, report_rows as reverse_rows
from cordon_d.reports import materialize
from cordon_d.monitoring import distinct_observations
from cordon_d.store import file_digest, put_bytes
from test_reports import block


class JoinIdentity(unittest.TestCase):
    def run_join(self, publications, report_rows, *, missing_route=False, two_results=False, second_version=False, cutoff=None,
                 repeated=False, repetition_support=True, differing_repeat=False, reading_issues=()):
        with TemporaryDirectory() as directory, patch.dict(os.environ):
            base = Path(directory)
            store = base / 'store'; os.environ['CORDON_STORE'] = str(store)
            monitoring = base / 'monitoring'; campaign = monitoring / 'campaign'; campaign.mkdir(parents=True)
            workbook = Workbook(); sheet = workbook.active
            sheet.append(['ID', 'DATA_RILEVAMENTO', 'RISULTATO', 'DOCUMENTO_CONFERMA'])
            route = 'https://publisher.example/report.pdf'
            for reference, date_text in publications:
                sheet.append([reference, datetime.fromisoformat(date_text), 'POSITIVO', route])
            path = campaign / 'release.xlsx'; workbook.save(path)
            (campaign / 'releases.json').write_text(json.dumps([
                {'url': 'https://publisher.example/release.xlsx', 'path': path.name, 'sha256': file_digest(path)}]))
            reports = base / 'reports'; reports.mkdir()
            digest = put_bytes(store, b'%PDF-test-source')
            actual_route = 'https://other.example/report.pdf' if missing_route else route
            captures = [{'url': actual_route, 'captured_at': '2026-01-01T00:00:00+00:00', 'sha256': digest}]
            if second_version:
                other = put_bytes(store, b'%PDF-second-rendition')
                captures.append({'url': route, 'captured_at': '2026-01-02T00:00:00+00:00', 'sha256': other})
            if missing_route:
                captures.append({'url': route, 'captured_at': '2026-01-01T00:00:00+00:00', 'error': 'HTTP 404'})
            (reports / 'records.json').write_text(json.dumps(captures))
            cache = store / 'derived/reports/v' / digest / 'report.json'; cache.parent.mkdir(parents=True)
            item = block(report_rows)
            item['reading']['issues'] = list(reading_issues)
            if two_results:
                table = item['reading']['tables'][0]
                table['columns'].append(dict(table['columns'][2], heading=['Esito B'], test='Esito B'))
                for row in table['rows']:
                    row['cells'].append({'text': 'Positivo'})
            if repeated:
                duplicate = copy.deepcopy(item['reading']['tables'][0])
                duplicate['id'] = 'p1-t2'
                if differing_repeat:
                    duplicate['rows'][0]['cells'][3]['text'] = '03/06/2024'
                item['reading']['tables'].append(duplicate)
                if repetition_support:
                    item['reading']['facts'].append({'id': 'repeat', 'role': 'repeated_representation',
                        'page': 1, 'locator': 'shared heading', 'text': 'Risultati dei campioni',
                        'applies_to': ['p1-t1', 'p1-t2']})
            cache.write_text(json.dumps({'source_sha256': digest, 'extraction_version': 'v',
                'page_count': 1, 'blocks': [item]}))
            return list(findings(distinct_observations(monitoring), reports, store,
                                extraction_version='v', known_through=cutoff or datetime(2026, 2, 1, tzinfo=timezone.utc)))

    def test_a_unique_route_reference_and_day_match(self):
        result = self.run_join([['123', '2024-06-01']], [['123', '01/06/2024', 'Positivo', '02/06/2024']])
        self.assertEqual(result[0]['status'], 'matched')
        self.assertEqual(result[0]['matches'][0]['temporal'], 'agrees')

    def test_uncertain_identifier_stays_candidate_with_issues_in_both_directions(self):
        issue = {'scope': 'p1-t1/c1 (ID)', 'cause': 'Identifier origin is unresolved.'}
        values = [['123', '01/06/2024', 'Positivo', '02/06/2024']]
        result = self.run_join([['123', '2024-06-01']], values, reading_issues=[issue])[0]
        self.assertFalse(result['matches'])
        candidate = result['links'][0]['candidates'][0]
        self.assertEqual(candidate['row'].candidate_reference, '123')
        self.assertIsNone(candidate['row'].reference)
        self.assertTrue(candidate['identity_cause'])
        self.assertIn(issue, result['links'][0]['reading_issues'])
        item = block(values); item['reading']['issues'] = [issue]
        reverse = list(reverse_rows([materialize('hash', 'v', 1, [item])], []))[0]
        self.assertIn(issue, reverse['reading_issues'])
        self.assertTrue(reverse['row'].cells[0]['role_cause'])
        with self.assertRaises(ValueError):
            confirmation_inputs(result, result_pair=[('hash', 'a'), ('hash', 'b')], qualification={})

    def test_repeated_representation_keeps_both_occurrences_and_requires_all_fields(self):
        args = ([['123', '2024-06-01']], [['123', '01/06/2024', 'Positivo', '02/06/2024']])
        joined = self.run_join(*args, repeated=True)[0]
        self.assertEqual(joined['status'], 'matched')
        self.assertEqual(len(joined['matches']), 2)
        self.assertNotEqual(joined['matches'][0]['key'], joined['matches'][1]['key'])
        for options in ({'repetition_support': False}, {'differing_repeat': True}):
            rejected = self.run_join(*args, repeated=True, **options)[0]
            self.assertFalse(rejected['matches'])
            self.assertIn('several eligible source-row', rejected['status'])

    def test_same_filename_never_substitutes_for_a_failed_route(self):
        result = self.run_join([['123', '2024-06-01']], [['123', '01/06/2024', 'Positivo', '02/06/2024']], missing_route=True)
        self.assertEqual(result[0]['matches'], [])
        self.assertTrue(result[0]['links'][0]['alternative_candidates'])

    def test_multiple_captured_renditions_do_not_choose_the_readable_one(self):
        result = self.run_join([['123', '2024-06-01']],
            [['123', '01/06/2024', 'Positivo', '02/06/2024']], second_version=True)[0]
        self.assertFalse(result['matches'])
        self.assertTrue(all(link['rendition_ambiguity'] for link in result['links']))

    def test_capture_after_knowledge_cutoff_is_not_available(self):
        result = self.run_join([['123', '2024-06-01']],
            [['123', '01/06/2024', 'Positivo', '02/06/2024']],
            cutoff=datetime(2025, 12, 31, tzinfo=timezone.utc))[0]
        self.assertFalse(result['matches'])
        self.assertEqual(result['links'][0]['status'], 'source route not acquired at knowledge cutoff')

    def test_one_undated_row_cannot_match_two_observation_days(self):
        result = self.run_join([['123', '2024-06-01'], ['123', '2024-06-02']],
                               [['123', None, 'Positivo', '02/06/2024']])
        self.assertTrue(all(not item['matches'] for item in result))
        self.assertTrue(all('several eligible observation' in item['status'] for item in result))

    def test_dated_row_does_not_discard_an_undated_competitor(self):
        result = self.run_join([['123', '2024-06-01']], [
            ['123', '01/06/2024', 'Positivo', '02/06/2024'], ['123', None, 'Negativo', '02/06/2024']])
        self.assertEqual(result[0]['matches'], [])
        self.assertIn('several eligible source-row', result[0]['status'])

    def test_unique_undated_relationship_preserves_independent_result_evidence(self):
        from cordon_c.core import Evaluation
        joined = self.run_join([['123', '2024-06-01']],
            [['123', None, 'Positivo', '02/06/2024']], two_results=True)[0]
        self.assertEqual(joined['status'], 'provisional-match')
        pair = [(joined['matches'][0]['key'][0], r.locator) for r in joined['matches'][0]['row'].results]
        inputs = confirmation_inputs(joined, result_pair=pair, qualification={'first_annex_iv': Evaluation(True)})
        self.assertTrue(inputs['first_positive_annex_iv'].truth)
        self.assertIsNone(inputs['second_positive_annex_iv'].truth)
        self.assertTrue(joined['matches'][0]['date_cause'])
        joined['matches'][0]['reading_complete'] = False
        inputs = confirmation_inputs(joined, result_pair=pair, qualification={
            'first_annex_iv': Evaluation(True), 'inside_demarcated_area': Evaluation(True)})
        self.assertIsNone(inputs['first_positive_annex_iv'].truth)
        self.assertTrue(any('unread report scope' in need for need in inputs['first_positive_annex_iv'].needs))
        self.assertTrue(inputs['inside_demarcated_area'].truth)
        negative = self.run_join([['123', '2024-06-01']],
            [['123', None, 'Negativo', '02/06/2024']], two_results=True)[0]
        negative['matches'][0]['reading_complete'] = False
        pair = [(negative['matches'][0]['key'][0], r.locator) for r in negative['matches'][0]['row'].results]
        self.assertIsNone(confirmation_inputs(negative, result_pair=pair,
            qualification={'first_annex_iv': Evaluation(True)})['first_positive_annex_iv'].truth)

    def test_contradictory_day_is_exposed_without_a_match(self):
        result = self.run_join([['123', '2024-06-01']], [['123', '02/06/2024', 'Positivo', '03/06/2024']])
        self.assertEqual(result[0]['matches'], [])
        self.assertEqual(result[0]['links'][0]['candidates'][0]['temporal'], 'conflicts')

    def test_monitoring_reused_id_is_not_repaired_by_digit_width(self):
        result = self.run_join([['123456', '2024-06-01'], ['123456', '2024-06-01']],
                               [['123456', '01/06/2024', 'Positivo', '02/06/2024']])
        self.assertEqual(len(result), 2)
        self.assertTrue(all(not item['matches'] for item in result))


    def test_ordinary_join_reaches_c_without_inventing_qualified_identities(self):
        from cordon_c import core
        from cordon_c.bindings import confirmation_facts
        from datetime import date
        joined = self.run_join([['123', '2024-06-01']],
            [['123', '01/06/2024', 'Positivo', '02/06/2024']], two_results=True)[0]
        pair = tuple((joined['matches'][0]['key'][0], r.locator) for r in joined['matches'][0]['row'].results)
        inputs = confirmation_inputs(joined, result_pair=pair, qualification={})
        self.assertIsNone(inputs['first_test'])
        self.assertIsNone(inputs['first_positive_annex_iv'].truth)
        owner = Path(core.__file__).resolve().parents[2] / 'stage-a/authoring-eu.json'
        data = json.loads(owner.read_text())
        rows = data if isinstance(data, list) else data['provision_versions']
        snapshot = core.Snapshot([r for r in rows if r['stable_provision_id'] == 'EU-2020-1201:2(6)'],
                                 dict(clocks=[], parameters=[], dispositions=[]))
        facts = confirmation_facts(snapshot, date(2024, 6, 1), **inputs)
        self.assertTrue(any(value.needs for value in facts.values()))


if __name__ == '__main__':
    unittest.main()
