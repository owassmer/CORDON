"""Offline software checks; these do not certify visual transcription accuracy."""
import copy
import json
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cordon_d.reports import literal_date, materialize, report, UnreadReport, validate_block
from cordon_d.report_extraction import Budget, ExtractionConfig, target_reading, extract_report, OutputLimit


def block(rows):
    roles = [('publisher_id', 'ID'), ('sampling_date', 'Data rilevamento'),
             ('result', 'Esito A'), ('test_date', 'Data saggio')]
    columns = [{'role': role, 'heading': [label], 'test': label if role == 'result' else None,
                'analyte': 'Xylella fastidiosa' if role == 'result' else None,
                'support': [{'page': 1, 'locator': 'table heading', 'text': label}]}
               for role, label in roles]
    data = {'pages': [{'page': 1, 'disposition': 'read'}], 'context_pages': [1],
            'facts': [], 'issues': [], 'tables': [{'id': 'p1-t1', 'page': 1, 'columns': columns,
            'rows': [{'id': f'r{i}', 'cells': [{'text': x} if x is not None else
                     {'text': None, 'cause': 'not_recovered'} for x in values]}
                     for i, values in enumerate(rows, 1)]}]}
    return {'targets': [1], 'reading': data, 'native_cells': {}}


class LiteralReport(unittest.TestCase):
    def test_invalid_date_retains_literal_and_does_not_become_a_result(self):
        reading = materialize('hash', 'v', 1, [block([['00123', '29/02/2023', 'Positivo', '01/03/2023']])])
        row = reading.rows[0]
        self.assertEqual(row.reference, '00123')
        self.assertEqual(row.sampling_dates[0].text, '29/02/2023')
        self.assertIsNone(row.sampling_date)
        self.assertEqual(len(row.results), 1)
        self.assertEqual(row.results[0].kind, 'positive')

    def test_duplicate_source_rows_are_not_deduplicated_by_identifier(self):
        values = ['123', '01/06/2024', 'Negativo', '02/06/2024']
        reading = materialize('hash', 'v', 1, [block([values, values])])
        self.assertEqual(len(reading.rows), 2)
        self.assertNotEqual(reading.rows[0].locator, reading.rows[1].locator)

    def test_native_value_is_copied_and_unknown_reference_fails(self):
        item = block([['123', '01/06/2024', 'Positivo', '02/06/2024']])
        item['reading']['tables'][0]['rows'][0]['cells'][0] = {'native_cell': 'cell1'}
        with self.assertRaises(ValueError):
            materialize('hash', 'v', 1, [item])
        item['native_cells']['cell1'] = {'text': '00123', 'page': 1}
        self.assertEqual(materialize('hash', 'v', 1, [item]).rows[0].reference, '00123')

    def test_dropped_target_page_wrong_width_and_causeless_null_fail(self):
        original = block([['123', '01/06/2024', 'Positivo', '02/06/2024']])
        mutations = []
        item = copy.deepcopy(original); item['reading']['pages'] = []; mutations.append(item)
        item = copy.deepcopy(original); item['reading']['tables'][0]['rows'][0]['cells'].pop(); mutations.append(item)
        item = copy.deepcopy(original); item['reading']['tables'][0]['rows'][0]['cells'][0] = {'text': None}; mutations.append(item)
        for item in mutations:
            with self.assertRaises(ValueError):
                materialize('hash', 'v', 1, [item])

    def test_context_disposition_is_excluded_but_missing_target_still_fails(self):
        item = block([['123', '01/06/2024', 'Positivo', '02/06/2024']])
        item['reading']['pages'].append({'page': 2, 'disposition': 'read'})
        reading = target_reading(item['reading'], [1], [2])
        self.assertEqual([p['page'] for p in reading['pages']], [1])
        with self.assertRaises(ValueError):
            target_reading(item['reading'], [1], [])
        item['reading'] = target_reading(item['reading'], [3], [1, 2])
        with self.assertRaises(ValueError):
            materialize('hash', 'v', 3, [item])

    def test_partial_assembly_exposes_unread_pages(self):
        reading = materialize('hash', 'v', 3, [block([['123', '01/06/2024', 'Positivo', '02/06/2024']])])
        self.assertEqual(reading.complete_pages, {1})
        self.assertEqual(reading.issues[-1]['scope'], 'pages 2,3')

    def test_support_cannot_cite_an_unseen_page(self):
        item = block([['123', '01/06/2024', 'Positivo', '02/06/2024']])
        item['reading']['tables'][0]['columns'][2]['support'][0]['page'] = 2
        # Nominating a future context page does not mean it was supplied.
        item['reading']['context_pages'] = [2]
        with self.assertRaisesRegex(ValueError, 'not supplied'):
            materialize('hash', 'v', 2, [item])
        item['context_pages'] = [2]
        self.assertEqual(len(materialize('hash', 'v', 2, [item]).rows), 1)

    def test_nonliteral_fact_component_cannot_supply_a_date(self):
        item = block([['123', None, 'Positivo', '02/06/2024']])
        item['reading']['facts'] = [{'id': 'f1', 'role': 'sampling_date', 'page': 1,
            'locator': 'letter', 'text': 'Prelievo non leggibile', 'value': '01/06/2024',
            'applies_to': ['report']}]
        reading = materialize('hash', 'v', 1, [item])
        self.assertIsNone(reading.rows[0].sampling_date)
        self.assertIn('value_cause', reading.facts[0])
        self.assertEqual(item['reading']['facts'][0]['value'], '01/06/2024')

    def test_completed_extraction_reuses_cache_without_provider_access(self):
        import pymupdf
        from cordon_d.store import put_bytes
        with TemporaryDirectory() as directory:
            store = Path(directory)
            with pymupdf.open() as pdf:
                pdf.new_page()
                digest = put_bytes(store, pdf.tobytes())
            reading = {'pages': [{'page': 1, 'disposition': 'read'}], 'tables': [],
                       'facts': [], 'issues': [], 'context_pages': []}
            with patch('cordon_d.report_extraction._call', return_value=reading) as call:
                first = extract_report(digest, store, config=ExtractionConfig(), budget=None)
                second = extract_report(digest, store, config=ExtractionConfig(), budget=None)
            self.assertEqual(first, second)
            self.assertEqual(call.call_count, 1)
            self.assertEqual(call.call_args.args[0]['output_config']['effort'], 'medium')
            self.assertTrue(json.loads(first.read_text())['assembly_complete'])

    def test_output_limit_splits_target_pages_without_accepting_truncation(self):
        import pymupdf
        from cordon_d.store import put_bytes
        with TemporaryDirectory() as directory:
            store = Path(directory)
            with pymupdf.open() as pdf:
                for _ in range(4):
                    pdf.new_page()
                digest = put_bytes(store, pdf.tobytes())
            def page(number):
                return {'pages': [{'page': number, 'disposition': 'read'}], 'tables': [],
                        'facts': [], 'issues': [], 'context_pages': []}
            with patch('cordon_d.report_extraction._call', side_effect=[OutputLimit('truncated'), page(1), page(2), page(3), page(4)]) as call:
                path = extract_report(digest, store, config=ExtractionConfig(), budget=None)
            payload = json.loads(path.read_text())
            self.assertEqual([b['targets'] for b in payload['blocks']], [[1], [2], [3], [4]])
            self.assertTrue(payload['assembly_complete'])
            self.assertEqual(call.call_count, 5)

    def test_qualifier_of_a_statement_reaches_row_without_broadening_scope(self):
        item = block([['123', '01/06/2024', 'Positivo', '02/06/2024']])
        item['reading']['facts'] = [
            {'id': 'f1', 'role': 'client_statement', 'page': 1, 'locator': 'letter',
             'text': 'Client information', 'applies_to': ['report']},
            {'id': 'f2', 'role': 'qualification', 'page': 1, 'locator': 'footnote',
             'text': 'Client responsibility', 'applies_to': ['f1']}]
        row = materialize('hash', 'v', 1, [item]).rows[0]
        self.assertEqual([f['id'] for f in row.facts], ['b1/f1', 'b1/f2'])
        self.assertEqual(row.facts[1]['applies_to'], ['b1/f1'])

    def test_analyte_cannot_supply_a_distinct_test_designation(self):
        item = block([['123', '01/06/2024', 'Positivo', '02/06/2024']])
        item['reading']['tables'][0]['columns'][2]['test'] = 'Xylella fastidiosa'
        result = materialize('hash', 'v', 1, [item]).rows[0].results[0]
        self.assertIsNone(result.assay)
        self.assertIn('repeats analyte', result.assay_cause)
        self.assertEqual(result.text, 'Positivo')

    def test_section_qualifier_follows_its_fields_without_becoming_report_wide(self):
        item = block([['123', '01/06/2024', 'Positivo', '02/06/2024']])
        item['reading']['facts'] = [
            {'id': 'client', 'role': 'sampler', 'page': 1, 'locator': 'letter',
             'text': 'Campionatore: Committente', 'section': 'p1/DATI CLIENTE§',
             'applies_to': ['p1-t1']},
            {'id': 'q', 'role': 'qualification', 'page': 1, 'locator': 'footnote',
             'text': '§ Dati forniti dal cliente', 'section': None,
             'applies_to': ['section:p1/DATI CLIENTE§']},
            {'id': 'unrelated', 'role': 'qualification', 'page': 1, 'locator': 'other section',
             'text': 'Altra qualifica', 'section': None,
             'applies_to': ['section:p1/DATI LABORATORIO']}]
        row = materialize('hash', 'v', 1, [item]).rows[0]
        self.assertEqual([f['id'] for f in row.facts], ['b1/client', 'b1/q'])
        self.assertEqual(row.facts[1]['applies_to'], ['section:p1/DATI CLIENTE§'])

    def test_section_without_a_physical_occurrence_is_retained_unattached(self):
        item = block([['123', '01/06/2024', 'Positivo', '02/06/2024']])
        item['reading']['facts'] = [{'id': 'f1', 'role': 'note', 'page': 1,
            'locator': 'letter', 'text': 'Client statement', 'section': 'DATI CLIENTE',
            'applies_to': ['report']}]
        fact = materialize('hash', 'v', 1, [item]).facts[0]
        self.assertNotIn('section', fact)
        self.assertEqual(fact['section_reading'], 'DATI CLIENTE')
        self.assertIn('unattached', fact['section_cause'])

    def test_exact_section_marks_link_without_confusing_double_or_reused_marks(self):
        from cordon_d.reports import link_section_marks
        facts = [
            {'page': 1, 'text': 'Prelievo', 'section': 'p1/CLIENTE§', 'applies_to': ['report']},
            {'page': 1, 'text': '§ Dati del cliente', 'applies_to': []},
            {'page': 1, 'text': '§§ Altra nota', 'applies_to': []},
            {'page': 2, 'text': '§ Nota di un altro documento', 'applies_to': []}]
        link_section_marks(facts)
        self.assertEqual(facts[1]['applies_to'], ['section:p1/CLIENTE§'])
        self.assertEqual(facts[1]['scope_derivations'][0]['marker'], '§')
        self.assertEqual(facts[2]['applies_to'], [])
        self.assertEqual(facts[3]['applies_to'], [])
        ambiguous = copy.deepcopy(facts)
        ambiguous[1]['applies_to'] = []
        ambiguous.append({'page': 1, 'text': '§ Nota diversa', 'applies_to': []})
        link_section_marks(ambiguous)
        self.assertEqual(ambiguous[1]['applies_to'], [])

    def test_literal_pool_suffix_keeps_full_cell_and_does_not_strip_other_suffixes(self):
        item = block([['00123\n(Pool)', '01/06/2024', 'Positivo', '02/06/2024'],
                      ['00124 (Field)', '01/06/2024', 'Positivo', '02/06/2024']])
        rows = materialize('hash', 'v', 1, [item]).rows
        self.assertEqual(rows[0].reference, '00123')
        self.assertEqual(rows[0].cells[0]['text'], '00123\n(Pool)')
        self.assertEqual(rows[0].cells[0]['annotation'], '(Pool)')
        self.assertEqual(rows[1].reference, '00124 (Field)')

    def test_sampling_attachment_gets_one_reread_and_can_remain_unresolved(self):
        import pymupdf
        from cordon_d.store import put_bytes
        initial = block([['123', None, 'Positivo', '02/06/2024']])['reading']
        initial['facts'] = [{'id': 'f1', 'role': 'sampling_date', 'page': 1,
            'locator': 'letter', 'text': 'Prelievo: 01/06/2024', 'value': '01/06/2024',
            'section': 'p1/DATI CLIENTE', 'applies_to': ['section:p1/DATI CLIENTE']}]
        for resolved in (True, False, None):
            revised = copy.deepcopy(initial)
            if resolved:
                revised['facts'][0]['applies_to'] = ['report']
            with TemporaryDirectory() as directory:
                store = Path(directory)
                with pymupdf.open() as pdf:
                    pdf.new_page()
                    digest = put_bytes(store, pdf.tobytes())
                responses = [initial, RuntimeError('cap reached') if resolved is None else revised]
                with patch('cordon_d.report_extraction._call', side_effect=responses) as call:
                    if resolved is None:
                        with self.assertRaisesRegex(RuntimeError, 'cap reached'):
                            extract_report(digest, store, config=ExtractionConfig(), budget=None)
                        path = next(store.glob('derived/reports/*/*/report.json'))
                    else:
                        path = extract_report(digest, store, config=ExtractionConfig(), budget=None)
                        extract_report(digest, store, config=ExtractionConfig(), budget=None)
                self.assertEqual(call.call_count, 2)
                repair_request = call.call_args_list[1].args[0]
                self.assertEqual(repair_request['output_config']['effort'], 'high')
                self.assertNotIn('01/06/2024', json.dumps(repair_request))
                payload = json.loads(path.read_text())
                if resolved is None:
                    self.assertFalse(payload['assembly_complete'])
                    self.assertEqual(len(payload['blocks'][0]['reading']['tables'][0]['rows']), 1)
                    self.assertEqual(payload['blocks'][0]['attachment_repair_pending'], 'cap reached')
                else:
                    self.assertIn('prior_request_sha256', payload['blocks'][0])
                if resolved is False:
                    self.assertIn('after one source reread', payload['blocks'][0]['reading']['issues'][-1]['cause'])

    def test_extra_model_region_is_not_promoted_into_detector_evidence(self):
        item = block([['123', '01/06/2024', 'Positivo', '02/06/2024']])
        item['native_regions'] = [{'id': 'n1', 'page': 1}]
        item['reading']['pages'][0]['regions'] = [
            {'native_table': name, 'disposition': 'represented', 'output_tables': ['p1-t1']}
            for name in ['n1', 'invented']]
        reading = materialize('hash', 'v', 1, [item])
        self.assertIn('absent from the supplied detector', reading.issues[0]['cause'])
        item['reading']['pages'][0]['regions'].pop(0)
        with self.assertRaises(ValueError):
            materialize('hash', 'v', 1, [item])

    def test_cache_rebuild_cannot_even_access_provider_credentials(self):
        from cordon_d.report_extraction import _call
        with patch('cordon_d.report_extraction.credential') as credential:
            with self.assertRaises(RuntimeError):
                _call({}, config=ExtractionConfig(), budget=None, request_id='missing', raw_path=Path('unused'))
            credential.assert_not_called()

    def test_table_header_page_is_supplied_to_a_later_continuation(self):
        import pymupdf
        from cordon_d.store import put_bytes
        with TemporaryDirectory() as directory:
            store = Path(directory)
            with pymupdf.open() as pdf:
                for _ in range(5):
                    pdf.new_page()
                digest = put_bytes(store, pdf.tobytes())
            first = block([['123', '01/06/2024', 'Positivo', '02/06/2024']])['reading']
            first['pages'] = [{'page': 1, 'disposition': 'read'}, {'page': 2, 'disposition': 'read'}]
            first['tables'][0]['page'] = 2
            continuation = copy.deepcopy(first)
            continuation['pages'] = [{'page': 3, 'disposition': 'read'}, {'page': 4, 'disposition': 'read'}]
            continuation['tables'][0].update(page=4, id='p4-t1')
            last = {'pages': [{'page': 5, 'disposition': 'read'}], 'tables': [],
                    'facts': [], 'issues': [], 'context_pages': []}
            with patch('cordon_d.report_extraction._call', side_effect=[first, continuation, last]) as call:
                extract_report(digest, store, config=ExtractionConfig(), budget=None)
            texts = [c.get('text', '') for c in call.call_args_list[-1].args[0]['messages'][0]['content']]
            self.assertIn('PHYSICAL PAGE 2: CONTEXT ONLY', texts)
            self.assertIn('PHYSICAL PAGE 4: CONTEXT ONLY', texts)
            self.assertIn('PHYSICAL PAGE 5: TARGET', texts)

    def test_cache_miss_does_not_call_a_provider(self):
        with TemporaryDirectory() as directory:
            value = report('missing', Path(directory), extraction_version='v')
        self.assertIsInstance(value, UnreadReport)

    def test_budget_reserves_before_dispatch_and_retains_uncertain_requests(self):
        with TemporaryDirectory() as directory:
            budget = Budget(Path(directory) / 'usage.json', limit=1, input_rate=2, output_rate=10)
            with self.assertRaises(RuntimeError):
                budget.reserve('too-large', 1000, 200000)
            budget.reserve('pending', 1000, 1000)
            with self.assertRaises(RuntimeError):
                budget.reserve('retry', 1000, 1000)
            budget.settle('pending', {'input_tokens': 1000, 'output_tokens': 100})
            budget.reserve('next', 1000, 1000)

    def test_annotated_identifier_keeps_qualification_and_exact_id_component(self):
        item = block([['00123 (Pool)', '01/06/2024', 'Positivo', '02/06/2024']])
        cell = item['reading']['tables'][0]['rows'][0]['cells'][0]
        cell.update(identifier='00123', annotation='(Pool)')
        row = materialize('hash', 'v', 1, [item]).rows[0]
        self.assertEqual(row.reference, '00123')
        self.assertEqual(row.cells[0]['text'], '00123 (Pool)')
        cell['identifier'] = '123'
        with self.assertRaises(ValueError):
            materialize('hash', 'v', 1, [item])

    def test_shared_sampling_date_reaches_rows_without_becoming_test_date(self):
        item = block([['123', None, 'Positivo', '02/06/2024']])
        item['reading']['tables'][0]['columns'][1]['role'] = 'other'
        item['reading']['facts'] = [{'id': 'f1', 'role': 'sampling_date', 'page': 1,
            'locator': 'client sampling field', 'text': 'Prelievo: 01/06/2024',
            'value': '01/06/2024', 'applies_to': ['report']}]
        row = materialize('hash', 'v', 1, [item]).rows[0]
        self.assertEqual(row.sampling_date.isoformat(), '2024-06-01')
        self.assertEqual(len(row.results), 1)
        self.assertEqual(literal_date('29/02/2023').cause, 'invalid_calendar_date')
        self.assertEqual(literal_date('last Tuesday').cause, 'unparsed_date_literal')

    def test_an_omitted_detected_table_cannot_claim_page_coverage(self):
        item = block([['123', '01/06/2024', 'Positivo', '02/06/2024']])
        item['native_regions'] = [{'id': 'n1', 'page': 1}]
        with self.assertRaises(ValueError):
            materialize('hash', 'v', 1, [item])
        item['reading']['pages'][0]['regions'] = [{'native_table': 'n1',
            'disposition': 'not_recovered', 'output_tables': [], 'cause': 'unreadable'}]
        with self.assertRaises(ValueError):
            materialize('hash', 'v', 1, [item])
        item['reading']['pages'][0]['disposition'] = 'partly_read'
        self.assertEqual(materialize('hash', 'v', 1, [item]).complete_pages, frozenset())


if __name__ == '__main__':
    unittest.main()
