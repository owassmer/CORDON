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
                 repeated=False, repetition_support=True, differing_repeat=False, reading_issues=(), replacement=None, association_rows=(), recovery=False,
                 identifier_display=False, monitoring_fields=None, differing_qualification=False, continued=False):
        with TemporaryDirectory() as directory, patch.dict(os.environ):
            base = Path(directory)
            store = base / 'store'; os.environ['CORDON_STORE'] = str(store)
            monitoring = base / 'monitoring'; campaign = monitoring / 'campaign'; campaign.mkdir(parents=True)
            workbook = Workbook(); sheet = workbook.active
            extra = monitoring_fields or {}
            sheet.append(['ID', 'DATA_RILEVAMENTO', 'RISULTATO', 'DOCUMENTO_CONFERMA', *extra])
            route = 'https://publisher.example/report.pdf'
            for reference, date_text in publications:
                sheet.append([reference, datetime.fromisoformat(date_text), 'POSITIVO', route, *extra.values()])
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
                if recovery:
                    captures[-1]['document_recovery'] = {
                        'url': actual_route, 'sha256': digest,
                        'established_at': '2026-01-03T00:00:00+00:00',
                        'identity': {'issuer': 'Laboratory A', 'number': '31/2024'},
                        'support': [{'source_sha256': file_digest(path), 'source_locator': 'sheet row 2',
                                     'report_page': 1, 'report_locator': 'sample 00091'}]}
            (reports / 'records.json').write_text(json.dumps(captures))
            cache = store / 'derived/reports/v' / digest / 'report.json'; cache.parent.mkdir(parents=True)
            item = block(report_rows)
            if identifier_display:
                display = copy.deepcopy(item['reading']['tables'][0])
                display['id'] = 'p1-display'
                display['columns'] = display['columns'][:1]
                for row in display['rows']:
                    row['cells'] = row['cells'][:1]
                item['reading']['tables'].append(display)
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
                if differing_qualification:
                    item['reading']['facts'].append({'id': 'qualifier', 'role': 'result_qualification',
                        'page': 1, 'locator': 'second display note', 'text': 'Risultato preliminare',
                        'applies_to': ['p1-t2']})
                if repetition_support:
                    item['reading']['facts'].append({'id': 'repeat', 'role': 'repeated_representation',
                        'page': 1, 'locator': 'shared heading', 'text': 'Risultati dei campioni',
                        'applies_to': ['p1-t1', 'p1-t2']})
            if association_rows or monitoring_fields:
                table = item['reading']['tables'][0]
                for role, value in (('latitude', '41.123456789'), ('longitude', '16.987654321'),
                                    ('host', 'Vite europea')):
                    table['columns'].append(dict(table['columns'][0], role=role, heading=[role]))
                    for row in table['rows']:
                        row['cells'].append({'text': value})
            if continued:
                table = item['reading']['tables'][0]
                tail = copy.deepcopy(table)
                tail['id'] = 'p2-tail'; tail['page'] = 2
                tail['columns'] = tail['columns'][2:]
                table['columns'] = table['columns'][:2]
                for prefix_row, tail_row in zip(table['rows'], tail['rows']):
                    tail_row['cells'] = tail_row['cells'][2:]
                    prefix_row['cells'] = prefix_row['cells'][:2]
                    identity = prefix_row['cells'][0]['text']
                    item['reading']['facts'].append({'id': 'continuation-' + prefix_row['id'],
                        'role': 'record_continuation', 'page': 1, 'locator': 'identity header',
                        'text': identity, 'value': identity,
                        'applies_to': [table['id'] + '/' + prefix_row['id'], tail['id'] + '/' + tail_row['id']]})
                item['reading']['tables'].append(tail)
                item['reading']['pages'].append({'page': 2, 'disposition': 'read'})
                item['targets'] = [1, 2]
            cache.write_text(json.dumps({'source_sha256': digest, 'extraction_version': 'v',
                'page_count': 2 if continued else 1, 'blocks': [item]}))
            from cordon_d import report_relations
            from test_report_relations import reading
            relation_cache = report_relations.path(store, digest)
            relation_cache.parent.mkdir(parents=True, exist_ok=True)
            relation_cache.write_text(json.dumps({'source_sha256': digest,
                'reading_version': report_relations.READING_VERSION, 'complete': True,
                'reading': reading().relations}))
            if second_version:
                relation_cache = report_relations.path(store, other)
                relation_cache.parent.mkdir(parents=True, exist_ok=True)
                relation_cache.write_text(json.dumps({'source_sha256': other,
                    'reading_version': report_relations.READING_VERSION, 'complete': True,
                    'reading': reading().relations}))
            if replacement:
                from cordon_d import report_relations
                from test_report_relations import reading
                successor = put_bytes(store, b'%PDF-replacement-source')
                captures.append({'url': route if replacement == 'same_route' else 'https://publisher.example/revised.pdf',
                    'captured_at': '2026-01-02T00:00:00+00:00', 'sha256': successor})
                (reports / 'records.json').write_text(json.dumps(captures))
                new_cache = cache.parents[1] / successor / 'report.json'
                new_cache.parent.mkdir(parents=True)
                payload = json.loads(cache.read_text()); payload['source_sha256'] = successor
                new_cache.write_text(json.dumps(payload))
                previous = reading().relations
                target = dict(previous['identity'])
                if replacement == 'missing_protocol':
                    target['protocol'] = '170245'
                later = reading(date='04/03/2024', previous=target,
                                effect='amends' if replacement == 'amends' else 'replaces').relations
                for key, value in ((digest, previous), (successor, later)):
                    relation_cache = report_relations.path(store, key)
                    relation_cache.parent.mkdir(parents=True, exist_ok=True)
                    relation_cache.write_text(json.dumps({'source_sha256': key,
                        'reading_version': report_relations.READING_VERSION, 'complete': True,
                        'reading': value}))
            joined = list(findings(distinct_observations(monitoring), reports, store,
                                extraction_version='v', known_through=cutoff or datetime(2026, 2, 1, tzinfo=timezone.utc),
                                association_readings=association_rows))
            if continued:
                return joined, list(reverse_rows([materialize(digest, "v", 2, [item])], joined))
            return joined

    def test_continued_record_without_complete_duplicate_reaches_consumer(self):
        joined, reverse = self.run_join([('00123', '2024-06-01')],
            [['00123', '01/06/2024', 'Positivo', '02/06/2024']], continued=True)
        self.assertEqual(joined[0]['status'], 'matched')
        self.assertEqual(len(joined[0]['matches']), 1)
        self.assertEqual(len(reverse), 2)
        self.assertTrue(all(item['observations'] for item in reverse))
        self.assertEqual(joined[0]['matches'][0]['row'].results[0].kind, 'positive')

    def test_reconciled_alternative_reaches_the_join_after_recovery_date(self):
        args = ([('00091', '2024-06-01')], [('00091', '01/06/2024', 'Positivo', '02/06/2024')])
        recovered = self.run_join(*args, missing_route=True, recovery=True)[0]
        self.assertTrue(recovered['matches'])
        self.assertTrue(recovered['links'][0]['route_recoveries'])
        earlier = self.run_join(*args, missing_route=True, recovery=True,
                               cutoff=datetime(2026, 1, 2, tzinfo=timezone.utc))[0]
        self.assertFalse(earlier['matches'])
        self.assertEqual(earlier['links'][0]['status'], 'source route not acquired at knowledge cutoff')

    def test_identifier_display_does_not_compete_as_an_analytical_result(self):
        result = self.run_join([('00091', '2024-06-01')],
            [('00091', '01/06/2024', 'Positivo', '02/06/2024')], identifier_display=True)[0]
        self.assertEqual(result['status'], 'matched')
        self.assertEqual(len(result['links'][0]['candidates']), 2)
        self.assertEqual(len(result['matches']), 1)
        display = next(c for c in result['links'][0]['candidates'] if not c['row'].results)
        self.assertTrue(display['result_cause'])

    def association(self, reference='public-9', longitude='16.98765432',
                    report_reference='31/2024 Laboratory A', host='Vite europea (Vitis L.)'):
        from types import SimpleNamespace
        fields = {key: {'text': value} for key, value in dict(plant_id=reference,
            report_reference=report_reference, report_date='01/03/2024', host=host,
            latitude='41.12345679', longitude=longitude).items()}
        return SimpleNamespace(rows=[dict(source_sha256='act-source', page=2, table=1, row=1,
            fields=fields, issues=[], basis={'kind': 'printed_header'})], issues=[], scope='native association table')

    def test_explicit_act_association_can_relate_distinct_client_code_without_aliasing(self):
        joined = self.run_join([['public-9', '2024-06-01']],
            [['client-4', '01/06/2024', 'Negativo', '02/06/2024']],
            association_rows=[self.association()])[0]
        self.assertEqual(len(joined['matches']), 1)
        match = joined['matches'][0]
        self.assertEqual(match['row'].reference, 'client-4')
        self.assertIn('derived occurrence', match['identity_basis'])
        self.assertEqual(joined['observation'].reference, 'public-9')
        self.assertEqual(match['row'].results[0].kind, 'negative')

    def test_monitoring_reference_and_published_degrees_relate_distinct_codes(self):
        fields = dict(PROT_SELGE='31/2024 Laboratory A', DATA_PROT_SELGE='01/03/2024',
                      LATITUDINE=41.12345679, LONGITUDINE=16.98765432, SPECIE='Vite europea')
        rows = [['client-4', '01/06/2024', 'Negativo', '02/06/2024']]
        joined = self.run_join([['public-9', '2024-06-01']], rows, monitoring_fields=fields)[0]
        self.assertEqual(joined['matches'][0]['row'].reference, 'client-4')
        self.assertEqual(joined['matches'][0]['row'].results[0].kind, 'negative')
        self.assertEqual(joined['matches'][0]['source_associations'][0]['source_kind'], 'monitoring publication')
        for field, value in [('DATA_PROT_SELGE', None), ('LONGITUDINE', 16.98766), ('LONGITUDINE', 17.0),
                             ('PROT_SELGE', '32/2024 Laboratory A'), ('SPECIE', 'Olea europaea')]:
            with self.subTest(field=field):
                changed = dict(fields, **{field: value})
                self.assertFalse(self.run_join([['public-9', '2024-06-01']], rows,
                                               monitoring_fields=changed)[0]['matches'])
        duplicated = self.run_join([['public-9', '2024-06-01'], ['public-10', '2024-06-01']],
                                   rows, monitoring_fields=fields)
        self.assertTrue(all(not item['matches'] for item in duplicated))
        two_rows = rows + [['client-5', '01/06/2024', 'Positivo', '02/06/2024']]
        self.assertFalse(self.run_join([['public-9', '2024-06-01']], two_rows,
                                      monitoring_fields=fields)[0]['matches'])

    def test_conflicting_act_association_is_not_selected_away(self):
        joined = self.run_join([['public-9', '2024-06-01']],
            [['client-4', '01/06/2024', 'Positivo', '02/06/2024']],
            association_rows=[self.association(), self.association(longitude='16.11111111')])[0]
        self.assertFalse(joined['matches'])
        self.assertEqual(len(joined['links'][0]['source_associations']), 2)

    def test_association_requires_source_supported_issuer_label(self):
        joined = self.run_join([['public-9', '2024-06-01']],
            [['client-4', '01/06/2024', 'Negativo', '02/06/2024']],
            association_rows=[self.association(report_reference='31/2024 Other Laboratory')])[0]
        self.assertFalse(joined['matches'])
        self.assertEqual(joined['links'][0]['source_associations'], [])

    def test_conflicting_host_withholds_administrative_correspondence(self):
        joined = self.run_join([['public-9', '2024-06-01']],
            [['public-9', '01/06/2024', 'Negativo', '02/06/2024']],
            association_rows=[self.association(host='Mandorlo (Prunus dulcis)')])[0]
        self.assertFalse(joined['matches'])
        self.assertIn('host', joined['links'][0]['candidates'][0]['association_cause'])

    def test_act_conflict_with_identical_id_is_exposed_and_withholds_match(self):
        joined = self.run_join([['public-9', '2024-06-01']],
            [['public-9', '01/06/2024', 'Positivo', '02/06/2024']],
            association_rows=[self.association(longitude='16.11111111')])[0]
        self.assertFalse(joined['matches'])
        self.assertIn('conflicts', joined['links'][0]['candidates'][0]['association_cause'])

    def test_same_report_coordinates_do_not_disambiguate_two_sample_rows(self):
        joined = self.run_join([['public-9', '2024-06-01']],
            [['client-4', '01/06/2024', 'Positivo', '02/06/2024'],
             ['client-5', '01/06/2024', 'Negativo', '02/06/2024']],
            association_rows=[self.association()])[0]
        self.assertFalse(joined['matches'])
        self.assertIn('several eligible source-row', joined['status'])

    def test_replacement_is_followed_through_original_route_and_keeps_history(self):
        joined = self.run_join([['123', '2024-06-01']],
            [['123', '01/06/2024', 'Positivo', '02/06/2024']], replacement='replaces')[0]
        self.assertEqual(len(joined['matches']), 1)
        original = next(link for link in joined['links'] if not link['replacement_chain'])
        successor = next(link for link in joined['links'] if link['replacement_chain'])
        self.assertIn('historical', original['document_cause'])
        self.assertEqual(joined['matches'][0]['key'][0], successor['sha256'])
        self.assertNotEqual(successor['sha256'], original['sha256'])

    def test_explicit_replacement_resolves_renditions_captured_on_same_route(self):
        joined = self.run_join([['123', '2024-06-01']],
            [['123', '01/06/2024', 'Positivo', '02/06/2024']], replacement='same_route')[0]
        self.assertEqual(len(joined['matches']), 1)
        self.assertFalse(any(link['rendition_ambiguity'] for link in joined['links']))

    def test_replacement_after_cutoff_does_not_rewrite_earlier_snapshot(self):
        joined = self.run_join([['123', '2024-06-01']],
            [['123', '01/06/2024', 'Positivo', '02/06/2024']], replacement='replaces',
            cutoff=datetime(2026, 1, 1, 12, tzinfo=timezone.utc))[0]
        self.assertEqual(len(joined['matches']), 1)
        self.assertFalse(joined['links'][0]['replacement_chain'])
        self.assertIsNone(joined['links'][0]['document_cause'])

    def test_amendment_does_not_silently_select_an_unamended_row(self):
        joined = self.run_join([['123', '2024-06-01']],
            [['123', '01/06/2024', 'Positivo', '02/06/2024']], replacement='amends')[0]
        self.assertFalse(joined['matches'])
        self.assertIn('amendment scope', joined['links'][0]['document_cause'])

    def test_a_unique_route_reference_and_day_match(self):
        result = self.run_join([['123', '2024-06-01']], [['123', '01/06/2024', 'Positivo', '02/06/2024']])
        self.assertEqual(result[0]['status'], 'matched')
        self.assertEqual(result[0]['matches'][0]['temporal'], 'agrees')

    def test_literal_identifier_matches_while_assignment_authority_stays_unresolved(self):
        issue = {'scope': 'p1-t1/c1 (ID)', 'cause': 'Identifier origin is unresolved.'}
        values = [['123', '01/06/2024', 'Positivo', '02/06/2024']]
        result = self.run_join([['123', '2024-06-01']], values, reading_issues=[issue])[0]
        self.assertEqual(result['status'], 'matched')
        candidate = result['links'][0]['candidates'][0]
        self.assertEqual(candidate['row'].candidate_reference, '123')
        self.assertIsNone(candidate['row'].reference)
        self.assertIsNone(candidate['identity_cause'])
        self.assertIn(issue, result['links'][0]['reading_issues'])
        item = block(values); item['reading']['issues'] = [issue]
        reverse = list(reverse_rows([materialize('hash', 'v', 1, [item])], []))[0]
        self.assertIn(issue, reverse['reading_issues'])
        self.assertTrue(reverse['row'].cells[0]['role_cause'])

    def test_repeated_representation_keeps_both_occurrences_and_requires_all_fields(self):
        args = ([['123', '2024-06-01']], [['123', '01/06/2024', 'Positivo', '02/06/2024']])
        joined = self.run_join(*args, repeated=True)[0]
        self.assertEqual(joined['status'], 'matched')
        self.assertEqual(len(joined['matches']), 2)
        self.assertNotEqual(joined['matches'][0]['key'], joined['matches'][1]['key'])
        unlabelled = self.run_join(*args, repeated=True, repetition_support=False)[0]
        self.assertEqual(unlabelled['status'], 'matched')
        self.assertEqual(len(unlabelled['matches']), 2)
        qualified = self.run_join(*args, repeated=True, differing_qualification=True)[0]
        self.assertEqual(qualified['status'], 'matched')
        self.assertEqual(sum(any(f['role'] == 'result_qualification' for f in m['row'].facts)
                             for m in qualified['matches']), 1)
        for options in ({'differing_repeat': True},):
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
