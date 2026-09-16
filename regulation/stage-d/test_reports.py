"""Offline software checks; these do not certify visual transcription accuracy."""
import copy
import json
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cordon_d.reports import literal_date, materialize, report, UnreadReport, validate_block, positioned_identifiers
from cordon_d.report_extraction import Budget, ExtractionConfig, target_reading, extract_report, OutputLimit, scan_rotation, version


def reserve_in_process(args):
    path, request = args
    try:
        Budget(Path(path), limit=.03, input_rate=2, output_rate=10, run_id='concurrent-check').reserve(request, 1000, 1000)
        return True
    except RuntimeError:
        return False


def subscription_in_process(args):
    import time
    from cordon_d.report_extraction import _subscription_call, write_json
    directory, slot = args
    directory = Path(directory)
    (directory / f'ready-{slot}').touch()
    deadline = time.monotonic() + 10
    while len(list(directory.glob('ready-*'))) < 2:
        if time.monotonic() > deadline:
            raise RuntimeError('second test process did not start')
        time.sleep(.01)
    def provider(**kwargs):
        with (directory / 'dispatches').open('a') as output:
            output.write('dispatch\n')
        time.sleep(.2)
        value = {'source': 'retained reading'}
        write_json(kwargs['raw_path'], {'provider': 'claude-code-subscription',
                                        'response': {'structured_output': value}})
        return value
    with patch('cordon_d.report_extraction._run_subscription_call', side_effect=provider):
        return _subscription_call(prompt='Read source', schema={}, digest='source', source=directory / 'source.pdf',
            config=ExtractionConfig(provider='subscription'), request_id='same-request',
            raw_path=directory / 'same-request.json')


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
    def test_explicit_unavailable_date_is_not_a_transcription_failure(self):
        item = block([['x', 'non disponibile', 'Positivo', '02/03/2024']])
        row = materialize('hash', 'v', 1, [item]).rows[0]
        self.assertEqual(row.date_cause, 'source_states_unavailable')
        self.assertEqual(row.sampling_dates[0].text, 'non disponibile')
        self.assertIsNone(row.sampling_date)

    def test_independent_subscription_runners_share_one_exact_request(self):
        from concurrent.futures import ProcessPoolExecutor
        with TemporaryDirectory() as directory:
            with ProcessPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(subscription_in_process, [(directory, 1), (directory, 2)]))
            self.assertEqual(results, [{'source': 'retained reading'}] * 2)
            self.assertEqual((Path(directory) / 'dispatches').read_text(), 'dispatch\n')

    def test_short_year_requires_unique_full_year_in_scoped_source_dates(self):
        item = block([['x', '28/02/15', 'Positivo', '02/03/2015']])
        fact = {'id': 'issue', 'role': 'report_date', 'page': 1, 'locator': 'letter date',
                'text': '9/3/2015', 'value': '9/3/2015', 'applies_to': ['report']}
        item['reading']['facts'] = [fact]
        value = materialize('hash', 'v', 1, [item]).rows[0].sampling_dates[0]
        self.assertEqual(value.text, '28/02/15')
        self.assertEqual(value.value.isoformat(), '2015-02-28')
        self.assertEqual(value.year_support, ('b1/issue',))
        for facts in ([], [dict(fact, applies_to=['other-table'])],
                      [fact, dict(fact, id='conflict', text='9/3/2115', value='9/3/2115')]):
            item['reading']['facts'] = facts
            self.assertIsNone(materialize('hash', 'v', 1, [item]).rows[0].sampling_date)
        self.assertEqual(literal_date('29/02/15', year_context=((2015, 'issue'),)).cause,
                         'invalid_calendar_date')

    def test_native_identifier_uses_source_geometry_and_preserves_original(self):
        import pymupdf
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / 'source.pdf'
            with pymupdf.open() as document:
                page = document.new_page()
                page.draw_rect((40, 40, 150, 100))
                page.draw_line((40, 70), (150, 70))
                page.draw_line((95, 40), (95, 100))
                for position, text in [((50, 60), 'A'), ((64, 60), 'B'), ((57, 61.5), '_'),
                                       ((105, 60), 'X'), ((50, 90), 'Y'), ((105, 90), 'Z')]:
                    page.insert_text(position, text, fontsize=11)
                document.save(path)
            item = block([['ignored', '01/06/2024', 'Positivo', '02/06/2024']])
            item['reading']['tables'][0]['rows'][0]['cells'][0] = {'native_cell': 'p1-t1-r1-c1'}
            item['native_cells']['p1-t1-r1-c1'] = {'text': 'A B\n_', 'page': 1}
            before = materialize('hash', 'v', 1, [item])
            after = positioned_identifiers(before, path)
            self.assertEqual(after.rows[0].reference, 'A_ B')
            self.assertEqual(after.rows[0].cells[0]['native_text'], 'A B\n_')
            self.assertEqual(before.rows[0].reference, 'A B\n_')
            item['native_cells']['p1-t1-r1-c1']['text'] = 'different source'
            with self.assertRaisesRegex(ValueError, 'differs from its source cell'):
                positioned_identifiers(materialize('hash', 'v', 1, [item]), path)

    def test_invalid_date_retains_literal_and_does_not_become_a_result(self):
        reading = materialize('hash', 'v', 1, [block([['00123', '29/02/2023', 'Positivo', '01/03/2023']])])
        row = reading.rows[0]
        self.assertEqual(row.reference, '00123')
        self.assertEqual(row.sampling_dates[0].text, '29/02/2023')
        self.assertIsNone(row.sampling_date)
        self.assertEqual(len(row.results), 1)
        self.assertEqual(row.results[0].kind, 'positive')

    def test_feminine_result_wording_keeps_literal_and_polarity(self):
        reading = materialize('hash', 'v', 1, [block([
            ['1', '01/06/2024', 'rilevata', '02/06/2024'],
            ['2', '01/06/2024', 'non rilevata', '02/06/2024']])])
        self.assertEqual([(r.results[0].text, r.results[0].kind) for r in reading.rows],
                         [('rilevata', 'detected'), ('non rilevata', 'not-detected')])

    def test_duplicate_source_rows_are_not_deduplicated_by_identifier(self):
        values = ['123', '01/06/2024', 'Negativo', '02/06/2024']
        reading = materialize('hash', 'v', 1, [block([values, values])])
        self.assertEqual(len(reading.rows), 2)
        self.assertNotEqual(reading.rows[0].locator, reading.rows[1].locator)

    def test_checked_transpose_preserves_occurrences_and_rejects_disagreement(self):
        item = block([['00123', '01/06/2024', 'Positivo', '02/06/2024'],
                      ['00456', '01/06/2024', 'Negativo', '02/06/2024']])
        source = item['reading']['tables'][0]
        transpose = {'id': 'p1-t2', 'page': 1,
            'columns': [dict(source['columns'][0], heading=['ID', r['cells'][0]['text']]) for r in source['rows']],
            'rows': [{'id': f'field{i}', 'cells': [copy.deepcopy(r['cells'][i]) for r in source['rows']]}
                     for i in range(1, 4)]}
        item['reading']['tables'].append(transpose)
        item['reading']['facts'].append({'id': 'repeat', 'role': 'repeated_representation', 'page': 1,
            'locator': 'shared heading', 'text': 'Risultati', 'applies_to': ['p1-t1', 'p1-t2']})
        reading = materialize('hash', 'v', 1, [item])
        self.assertEqual([r.reference for r in reading.rows], ['00123', '00456', '00123', '00456'])
        self.assertEqual(reading.rows[-1].results[0].kind, 'negative')
        self.assertEqual(reading.rows[-1].cells[2]['source_position']['reading_row'], 'field2')
        self.assertEqual(len(transpose['rows']), 3)  # The physical reading was not rewritten.
        transpose['rows'][1]['cells'][1]['text'] = 'Positivo'
        incomplete = materialize('hash', 'v', 1, [item])
        self.assertEqual(len(incomplete.rows), 2)
        self.assertFalse(incomplete.complete_pages)
        self.assertIn('no unique fully checked transpose', incomplete.issues[-1]['cause'])

    def test_labelled_transpose_is_derived_without_a_duplicate_declaration(self):
        item = block([['00123', '01/06/2024', 'Positivo', '02/06/2024'],
                      ['00456', '01/06/2024', 'Negativo', '02/06/2024']])
        source = item['reading']['tables'][0]
        labels = {'heading': [], 'role': 'other', 'test': None, 'analyte': None, 'support': []}
        transpose = {'id': 'p1-t2', 'page': 1,
            'columns': [labels] + [dict(source['columns'][0], heading=[r['cells'][0]['text']])
                                   for r in source['rows']],
            'rows': [{'id': f'field{i}', 'cells': [{'text': ' '.join(c['heading'])}] +
                     [copy.deepcopy(r['cells'][i]) for r in source['rows']]}
                     for i, c in enumerate(source['columns'])]}
        item['reading']['tables'].append(transpose)
        reading = materialize('hash', 'v', 1, [item])
        self.assertEqual([r.reference for r in reading.rows], ['00123', '00456', '00123', '00456'])
        self.assertEqual(reading.rows[-1].projection['companion_table'], 'p1-t1')
        transpose['rows'][2]['cells'][2]['text'] = 'Positivo'
        rejected = materialize('hash', 'v', 1, [item])
        self.assertEqual(len(rejected.rows), 2)
        self.assertFalse(rejected.complete_pages)

    def test_transposed_qualifications_use_original_sample_and_field_scopes(self):
        for labelled in (False, True):
            with self.subTest(labelled=labelled):
                item = block([['SCOPE-A', '01/06/2024', 'Positivo', '02/06/2024'],
                              ['SCOPE-B', '01/06/2024', 'Negativo', '02/06/2024']])
                source = item['reading']['tables'][0]
                columns = [dict(source['columns'][0], heading=([] if labelled else ['ID']) +
                           [row['cells'][0]['text']]) for row in source['rows']]
                offset = 2 if labelled else 1
                if labelled:
                    columns.insert(0, {'heading': [], 'role': 'other', 'support': []})
                transpose = {'id': 'p1-transpose', 'page': 1, 'columns': columns,
                    'rows': [{'id': f'field{i}', 'cells':
                             ([{'text': ' '.join(column['heading'])}] if labelled else []) +
                             [copy.deepcopy(row['cells'][i]) for row in source['rows']]}
                             for i, column in enumerate(source['columns']) if labelled or i != 0]}
                item['reading']['tables'].append(transpose)
                def note(name, scope):
                    return {'id': name, 'role': 'qualification', 'page': 1,
                            'locator': scope, 'text': name, 'applies_to': [scope]}
                item['reading']['facts'] = [
                    {'id': 'repeat', 'role': 'repeated_representation', 'page': 1,
                     'locator': 'heading', 'text': 'Risultati', 'applies_to': ['p1-t1', 'p1-transpose']},
                    note('sample-only', f'p1-transpose/c{offset}'),
                    note('field-row', 'p1-transpose/field2'),
                    note('one-cell', f'p1-transpose/field2/c{offset}'),
                    note('outside-source', 'p1-transpose/c4'),
                    note('attached-qualification', 'sample-only')]
                before = copy.deepcopy(item)
                reading = materialize('hash', 'v', 1, [item])
                self.assertEqual(item, before)
                first, second = reading.rows[-2:]
                names = lambda row: {f['text'] for f in row.facts if f['role'] == 'qualification'}
                self.assertEqual(names(first), {'sample-only', 'field-row', 'one-cell', 'attached-qualification'})
                self.assertEqual(names(second), {'field-row'})
                self.assertFalse(any(names(row) for row in reading.rows[:2]))
                sample_note = next(f for f in first.facts if f['text'] == 'sample-only')
                self.assertEqual(sample_note['applies_to'], [f'p1-transpose/c{offset}'])
                # A source-scoped date uses the same membership as its qualifications.
                item['reading']['facts'].append(dict(note('sample-date', f'p1-transpose/c{offset}'),
                    role='sampling_date', text='02/06/2024', value='02/06/2024'))
                dated = materialize('hash', 'v', 1, [item]).rows[-2:]
                self.assertIsNone(dated[0].sampling_date)
                self.assertEqual(dated[1].sampling_date.isoformat(), '2024-06-01')

    def test_reader_declared_continuation_preserves_parts_and_qualifications(self):
        from dataclasses import replace
        from cordon_d.reports import record_rows
        reading = materialize('hash', 'v', 1, [block([
            ['00123', '01/06/2024', 'Positivo', '02/06/2024']])])
        original = reading.rows[0]
        prefix = replace(original, cells=original.cells[:2], results=())
        note = {'id': 'tail-note', 'role': 'qualification', 'text': 'Solo il risultato',
                'applies_to': ['p2/tail/r1']}
        tail = replace(original, page=2, locator='p2/tail/r1', reference=None,
                       cells=original.cells[2:], sampling_dates=(), facts=(note,))
        raw = replace(reading, rows=(prefix, tail))
        self.assertEqual(record_rows(raw), (prefix, tail))  # No relationship from identical values.
        continuation = {'id': 'relation', 'role': 'record_continuation', 'value': '00123',
                        'text': '00123', 'page': 1, 'locator': prefix.cells[0]['locator'],
                        'applies_to': [prefix.locator, tail.locator]}
        declared = replace(raw, facts=(continuation,))
        assembled, = record_rows(declared)
        self.assertEqual(assembled.reference, '00123')
        self.assertEqual(assembled.cells, original.cells)
        self.assertEqual(assembled.results, original.results)
        self.assertEqual(assembled.sampling_date, original.sampling_date)
        self.assertEqual(assembled.projection['parts'], [prefix.locator, tail.locator])
        self.assertEqual(assembled.facts, (note,))
        self.assertEqual(note['applies_to'], ['p2/tail/r1'])
        self.assertEqual(declared.rows, (prefix, tail))
        self.assertFalse(tail.identifiers)
        # A client code and a laboratory code can belong to the same specimen.
        laboratory_id = dict(prefix.cells[0], role='laboratory_id', heading=['Lab ID'],
                             text='LAB-9', locator=prefix.locator + '/lab')
        with_lab = replace(declared, rows=(replace(prefix, cells=(*prefix.cells, laboratory_id)), tail))
        self.assertEqual(record_rows(with_lab)[0].laboratory_reference, 'LAB-9')
        for invalid in (
                replace(declared, rows=(prefix,)),
                replace(declared, facts=(dict(continuation, value='different'),)),
                replace(declared, facts=(dict(continuation, page=2),)),
                replace(declared, facts=(dict(continuation, text='00123 ... Positivo'),)),
                replace(declared, facts=(dict(continuation, applies_to=['report', tail.locator]),)),
                replace(declared, rows=(prefix, replace(tail, cells=(
                    dict(original.cells[1], text='02/06/2024'), *tail.cells)))),
                replace(declared, facts=(continuation, dict(continuation,
                    applies_to=[prefix.locator, 'missing'])))):
            with self.assertRaises(ValueError):
                record_rows(invalid)

    def test_swapped_source_headers_require_a_new_reader_binding(self):
        import pymupdf
        from dataclasses import replace
        from cordon_d.reports import record_rows
        original = materialize('hash', 'v', 1, [block([
            ['A', '01/06/2024', 'Positivo', '02/06/2024'],
            ['B', '01/06/2024', 'Positivo', '02/06/2024']])])
        def declared(header):
            parts, facts = [], []
            for i, identifier in enumerate(header):
                base = original.rows[i]
                prefix = replace(base, reference=identifier, cells=(dict(base.cells[0], text=identifier,
                    native_cell=f'p1-t1-r1-c{i + 2}'), base.cells[1]), results=())
                tail = replace(base, page=2, locator=f'p2/tail/r{i}', reference=None,
                               cells=base.cells[2:], sampling_dates=())
                parts.extend((prefix, tail))
                facts.append({'role': 'record_continuation', 'value': identifier, 'text': identifier, 'page': 1,
                              'applies_to': [f'native:p1-t1-r1-c{i + 2}', tail.locator]})
            return replace(original, rows=tuple(parts), facts=tuple(facts))
        def source(header, path):
            with pymupdf.open() as document:
                page = document.new_page()
                for x in (40, 140, 240, 340):
                    page.draw_line((x, 40), (x, 100))
                for y in (40, 70, 100):
                    page.draw_line((40, y), (340, y))
                for i, value in enumerate(('Id', *header)):
                    page.insert_text((45 + 100 * i, 60), value)
                for i, value in enumerate(('Date', 'same', 'same')):
                    page.insert_text((45 + 100 * i, 90), value)
                document.new_page()
                document.save(path)
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'swapped.pdf'
            source(['B', 'A'], path)
            with self.assertRaisesRegex(ValueError, 'differs from its source cell'):
                positioned_identifiers(declared(['A', 'B']), path)
            fresh = positioned_identifiers(declared(['B', 'A']), path)
            records = record_rows(fresh)
            self.assertEqual([row.reference for row in records], ['B', 'A'])
            self.assertEqual([row.results[0].text for row in records], ['Positivo', 'Positivo'])
            self.assertEqual(len(record_rows(replace(fresh, facts=()))), 4)

    def test_extraction_version_describes_loaded_code_not_later_disk_edits(self):
        expected = version(ExtractionConfig())
        with patch('pathlib.Path.read_bytes', side_effect=AssertionError('late disk read')):
            self.assertEqual(version(ExtractionConfig()), expected)

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

    def test_continuation_only_repair_preserves_retained_reading(self):
        import pymupdf
        from cordon_d.store import put_bytes
        from cordon_d.reports import record_rows
        original = block([['00123', '01/06/2024', None, None],
                          [None, None, 'Positivo', '02/06/2024']])
        proposal = {'pages': [], 'tables': [], 'context_pages': [1], 'issues': [],
                    'facts': [{'id': 'continued', 'role': 'record_continuation',
                        'page': 1, 'locator': 'header', 'text': '00123', 'value': '00123',
                        'applies_to': ['p1-t1/r1', 'p1-t1/r2']}]}
        with TemporaryDirectory() as directory:
            store = Path(directory)
            with pymupdf.open() as pdf:
                pdf.new_page()
                digest = put_bytes(store, pdf.tobytes())
            prior = store / 'derived/reports/old' / digest / 'report.json'
            prior.parent.mkdir(parents=True)
            prior.write_text(json.dumps({'source_sha256': digest, 'extraction_version': 'old',
                'page_count': 1, 'assembly_complete': True, 'blocks': [original]}))
            before = prior.read_bytes()
            with patch('cordon_d.report_extraction._subscription_call', return_value=proposal) as call:
                path = extract_report(digest, store, continuation_from='old',
                                      config=ExtractionConfig(provider='subscription'), budget=None)
            self.assertEqual(call.call_count, 1)
            self.assertIn('preserve every retained cell', call.call_args.kwargs['prompt'])
            saved = json.loads(path.read_text())
            self.assertEqual(saved['blocks'][0], original)
            self.assertEqual(prior.read_bytes(), before)
            self.assertEqual(saved['replayed_from_extraction_version'], 'old')
            rows = record_rows(materialize(digest, 'v', 1, saved['blocks']))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].results[0].kind, 'positive')

    def test_unbound_continuation_returns_to_established_reader(self):
        import pymupdf
        from cordon_d.store import put_bytes
        from cordon_d.reports import record_rows
        data = block([['00123', '01/06/2024', 'Positivo', '02/06/2024']])['reading']
        prefix = data['tables'][0]
        tail = copy.deepcopy(prefix)
        tail['id'] = 'p2-tail'; tail['page'] = 2
        prefix['columns'] = prefix['columns'][:2]
        prefix['rows'][0]['cells'] = prefix['rows'][0]['cells'][:2]
        tail['columns'] = tail['columns'][2:]
        tail['rows'][0]['cells'] = tail['rows'][0]['cells'][2:]
        data['tables'].append(tail)
        data['pages'].append({'page': 2, 'disposition': 'read'})
        data['facts'] = [{'id': 'continued', 'role': 'record_continuation',
                          'page': 1, 'locator': 'header', 'text': '00123', 'value': '00123',
                          'applies_to': ['p1-t1/r1', 'missing-part']}]
        repaired = copy.deepcopy(data)
        repaired['facts'][0]['applies_to'][-1] = 'p2-tail/r1'
        with TemporaryDirectory() as directory:
            store = Path(directory)
            with pymupdf.open() as pdf:
                pdf.new_page(); pdf.new_page()
                digest = put_bytes(store, pdf.tobytes())
            config = ExtractionConfig(provider='subscription')
            with patch('cordon_d.report_extraction._subscription_call', side_effect=[data, repaired]) as call:
                path = extract_report(digest, store, config=config, budget=None)
            self.assertEqual(call.call_count, 2)
            self.assertIn('Resolve this record-continuation binding defect', call.call_args.kwargs['prompt'])
            saved = json.loads(path.read_text())
            self.assertTrue(saved['assembly_complete'])
            reading = materialize(digest, 'v', 2, saved['blocks'])
            self.assertEqual(len(reading.rows), 2)
            self.assertEqual(len(record_rows(reading)), 1)
            self.assertEqual(record_rows(reading)[0].reference, '00123')

    def test_incomplete_page_is_reread_before_document_completion(self):
        import pymupdf
        from cordon_d.store import put_bytes
        with TemporaryDirectory() as directory:
            store = Path(directory)
            with pymupdf.open() as pdf:
                pdf.new_page()
                digest = put_bytes(store, pdf.tobytes())
            incomplete = {'pages': [{'page': 1, 'disposition': 'partly_read'}],
                          'tables': [], 'facts': [], 'issues': [], 'context_pages': []}
            complete = dict(incomplete, pages=[{'page': 1, 'disposition': 'read'}])
            config = ExtractionConfig(provider='subscription')
            with patch('cordon_d.report_extraction._subscription_call', side_effect=[incomplete, complete]) as call:
                path = extract_report(digest, store, config=config, budget=None)
                extract_report(digest, store, config=config, budget=None)
                self.assertEqual(call.call_count, 2)
                self.assertEqual(call.call_args.kwargs['config'].effort, 'high')
            self.assertTrue(json.loads(path.read_text())['assembly_complete'])
            with patch('cordon_d.report_extraction._subscription_call', return_value=incomplete):
                path.unlink()
                for cached in path.parent.glob('blocks/*.json'):
                    cached.unlink()
                with self.assertRaisesRegex(RuntimeError, 'remains incomplete'):
                    extract_report(digest, store, config=config, budget=None)
            self.assertFalse(json.loads(path.read_text())['assembly_complete'])

    def test_complete_document_response_is_not_forced_into_page_pairs(self):
        import pymupdf
        from cordon_d.store import put_bytes
        with TemporaryDirectory() as directory:
            store = Path(directory)
            with pymupdf.open() as pdf:
                for _ in range(3):
                    pdf.new_page()
                digest = put_bytes(store, pdf.tobytes())
            reading = {'pages': [{'page': n, 'disposition': 'read'} for n in (1, 2, 3)],
                       'tables': [], 'facts': [], 'issues': [], 'context_pages': []}
            config = ExtractionConfig(provider='subscription')
            with patch('cordon_d.report_extraction._subscription_call', return_value=reading) as call:
                path = extract_report(digest, store, config=config, budget=None)
                self.assertEqual(call.call_count, 1)
                saved = json.loads(path.read_text())
                self.assertEqual(saved['blocks'][0]['targets'], [1, 2, 3])
                self.assertTrue(saved['assembly_complete'])
                path.unlink()  # replay the retained block, including its complete page scope
                extract_report(digest, store, config=config, budget=None)
                self.assertEqual(call.call_count, 1)

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

    def test_interrupted_reservation_is_counted_and_cannot_be_retried(self):
        with TemporaryDirectory() as directory:
            budget = Budget(Path(directory) / 'usage.json', limit=.03, input_rate=2, output_rate=10)
            budget.reserve('lost', 1000, 1000)
            budget.retain_interrupted_reservation('lost')
            self.assertEqual(budget.entries[0]['usd'], '0.012')
            self.assertNotIn('usage', budget.entries[0])
            with self.assertRaisesRegex(RuntimeError, 'already dispatched'):
                budget.reserve('lost', 1000, 1000)
            budget.reserve('new', 1000, 1000)
            budget.retain_interrupted_reservation('new')
            with self.assertRaisesRegex(RuntimeError, 'Remaining budget'):
                budget.reserve('over-cap', 1000, 1000)

    def test_processes_cannot_oversubscribe_the_shared_cap(self):
        from concurrent.futures import ProcessPoolExecutor
        from decimal import Decimal
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'usage.json'
            with ProcessPoolExecutor(max_workers=3) as pool:
                accepted = list(pool.map(reserve_in_process, [(str(path), str(i)) for i in range(9)]))
            entries = json.loads(path.read_text())
            self.assertEqual(sum(accepted), 2)
            self.assertEqual(len(entries), 2)
            self.assertLessEqual(sum(Decimal(e['usd']) for e in entries), Decimal('.03'))
            with self.assertRaisesRegex(RuntimeError, 'unresolved billing'):
                Budget(path, limit=1, input_rate=2, output_rate=10, run_id='new-run').reserve('after-restart', 1, 1)

    def test_explicit_retry_retains_both_charges_and_cannot_repeat_automatically(self):
        with TemporaryDirectory() as directory:
            budget = Budget(Path(directory) / 'usage.json', limit=.03, input_rate=2, output_rate=10)
            budget.reserve('lost', 1000, 1000)
            budget.retain_interrupted_reservation('lost', retry=True)
            budget.reserve('lost', 1000, 1000)
            budget.dispatch_finished('lost')
            self.assertNotIn('pid', budget.entries[-1])
            self.assertEqual(len(budget.entries), 2)
            self.assertEqual(budget.entries[0]['usd'], '0.012')
            with self.assertRaisesRegex(RuntimeError, 'already dispatched'):
                budget.reserve('lost', 1000, 1000)

    def test_scan_rotation_corrects_slanted_lines_and_leaves_native_text(self):
        import pymupdf
        with pymupdf.open() as pdf:
            source = pdf.new_page(width=400, height=300)
            for y in range(40, 260, 20):
                source.draw_line((20, y), (380, y + 10), width=1)
            png = source.get_pixmap().tobytes('png')
            scan = pdf.new_page(width=400, height=300)
            scan.insert_image(scan.rect, stream=png)
            self.assertAlmostEqual(scan_rotation(scan), -1.6, delta=.15)
            scan.insert_text((20, 20), 'native text')
            self.assertEqual(scan_rotation(scan), 0)

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


class ShownPages(unittest.TestCase):
    def test_a_block_may_cite_any_page_it_was_shown_and_no_other(self):
        item = block([['101', '01/03/2024', 'Positivo', '02/03/2024']])
        item['targets'] = [2]
        item['reading']['pages'] = [{'page': 2, 'disposition': 'read'}]
        item['reading']['tables'][0]['page'] = 2
        item['reading']['context_pages'] = []
        item['reading']['facts'] = [{'id': 'f1', 'role': 'qualification', 'page': 1, 'locator': 'letter',
                                     'section': None, 'text': 'as received', 'value': None, 'applies_to': ['report']}]
        with self.assertRaisesRegex(ValueError, 'not supplied'):
            materialize('hash', 'v', 2, [copy.deepcopy(item)])
        item['supplied_pages'] = [1, 2]
        self.assertEqual(materialize('hash', 'v', 2, [item]).pages, 2)

    def test_identifier_annotation_reconstructs_the_cell_in_either_order(self):
        item = block([['*513077', '01/03/2024', 'Positivo', '02/03/2024']])
        item['reading']['tables'][0]['rows'][0]['cells'][0].update(identifier='513077', annotation='*')
        validate_block(item['reading'], targets=[1], page_count=1, native_cells={})
        item['reading']['tables'][0]['rows'][0]['cells'][0].update(annotation='(Pool)')
        with self.assertRaisesRegex(ValueError, 'reconstruct'):
            validate_block(item['reading'], targets=[1], page_count=1, native_cells={})


class RetainedResponses(unittest.TestCase):
    def test_a_failed_subscription_envelope_is_set_aside_and_never_replayed_as_a_reading(self):
        from cordon_d.report_extraction import _retained_reading
        with TemporaryDirectory() as temporary:
            raw = Path(temporary) / 'responses' / 'abc.json'
            raw.parent.mkdir()
            raw.write_text(json.dumps({'provider': 'claude-code-subscription', 'request_sha256': 'abc',
                                       'response': {'is_error': True, 'result': 'limit reached'}}))
            self.assertIsNone(_retained_reading(raw, 'claude-sonnet-5'))
            self.assertFalse(raw.exists())
            self.assertEqual(len(list((raw.parent / 'failed').glob('abc-*.json'))), 1)
            raw.write_text(json.dumps({'provider': 'claude-code-subscription', 'request_sha256': 'abc',
                                       'response': {'structured_output': {'pages': []}}}))
            self.assertEqual(_retained_reading(raw, 'claude-sonnet-5'), {'pages': []})


if __name__ == '__main__':
    unittest.main()
