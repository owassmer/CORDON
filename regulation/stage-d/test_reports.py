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


FIELDS_NONE = {'cq': None, 'accreditation': None}


def note_provider(notes, fields=FIELDS_NONE):
    """A subscription stand-in: a note request takes the next note answer, a note fields request `fields`."""
    from cordon_d.report_extraction import note_fields_schema
    answers = iter(notes) if isinstance(notes, list) else None
    def provider(**kwargs):
        if kwargs['schema'] == note_fields_schema():
            return copy.deepcopy(fields)
        value = next(answers) if answers is not None else notes
        if isinstance(value, BaseException):
            raise value
        return copy.deepcopy(value)
    return provider


def note_calls(provider):
    """The calls a stand-in received for mark notes, not for their fields."""
    from cordon_d.report_extraction import note_fields_schema
    return [c for c in provider.call_args_list if c.kwargs['schema'] != note_fields_schema()]


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
    def test_reader_separates_annotated_results_without_losing_scope_or_literal(self):
        item = block([['A', '01/06/2024', 'rilevato*', '02/06/2024'],
                      ['B', '01/06/2024', 'non rilevato†', '02/06/2024']])
        for raw, value, mark in zip(item['reading']['tables'][0]['rows'],
                                    ['rilevato', 'non rilevato'], ['*', '†']):
            raw['cells'][2].update(result_value=value, annotation=mark)
        note = dict(id='f1', role='result_qualification', page=1, locator='footnote', section=None,
                    text='* Non-accredited test', value=None, applies_to=['p1-t1/r1/c3'])
        # A split mark, like a printed one, is classified only through its note.
        rows = materialize('source', 'v', 1, [item]).rows
        self.assertEqual([(r.results[0].kind, r.results[0].cause) for r in rows],
                         [('unclassified', 'printed mark; note not recovered by the reading'),
                          ('unclassified', None)])
        item['reading']['facts'] = [note]
        rows = materialize('source', 'v', 1, [item]).rows
        # '†' is not a mark this parser knows, so it stays part of the printed result.
        self.assertEqual([r.results[0].kind for r in rows], ['detected', 'unclassified'])
        self.assertEqual([r.results[0].text for r in rows], ['rilevato*', 'non rilevato†'])
        self.assertEqual(rows[0].results[0].marks, ('*',))
        self.assertEqual(rows[0].cells[2]['result_value'], 'rilevato')
        self.assertEqual([f['text'] for f in rows[0].facts], ['* Non-accredited test'])
        self.assertEqual(rows[0].facts[0]['applies_to'], ['p1-t1/r1/c3'])
        self.assertEqual(rows[1].facts, ())
        # The same cell unsplit reads the same way: one parser for both shapes.
        del item['reading']['tables'][0]['rows'][0]['cells'][2]['result_value']
        whole = materialize('source', 'v', 1, [item]).rows[0].results[0]
        self.assertEqual((whole.kind, whole.marks), ('detected', ('*',)))

    def test_one_parser_reads_marks_with_or_without_a_separator_split_or_whole(self):
        from cordon_d.reports import printed_marks, result_marks
        self.assertEqual(printed_marks('*,a'), ('*', 'a'))
        self.assertEqual(printed_marks('* a'), ('*', 'a'))
        self.assertEqual(printed_marks('*a'), ('*', 'a'))
        self.assertIsNone(printed_marks('debole'))
        self.assertIsNone(printed_marks('†'))
        self.assertEqual(printed_marks('ᵇ'), ('b',))
        for literal in ('non rilevato*,a', 'non\nrilevato*,a', 'non rilevato* a', 'non rilevato*a'):
            with self.subTest(literal=literal):
                self.assertEqual(result_marks(literal)[1], ('*', 'a'))
                self.assertEqual(' '.join(result_marks(literal)[0].split()), 'non rilevato')
        self.assertEqual(result_marks('non rilevato*', {'result_value': 'non rilevato', 'annotation': '*,a'}),
                         ('non rilevato', ('*', 'a')))
        self.assertEqual(result_marks('rilevataa'), ('rilevata', ('a',)))
        self.assertEqual(result_marks('dubbioᵇ'), ('dubbio', ('b',)))
        self.assertIsNone(result_marks('non rilevata'))
        self.assertIsNone(result_marks('positivo debole'))
        note = lambda mark, id: {'id': id, 'role': 'result_qualification', 'page': 1, 'locator': 'footnote',
                                 'text': f'{mark} nota', 'value': None, 'applies_to': ['p1-t1/r1/c3']}
        for cell in ({'text': 'non rilevato*,a'},
                     {'text': 'non rilevato*,a', 'result_value': 'non rilevato', 'annotation': '*,a'}):
            with self.subTest(cell=cell):
                item = block([['123', '02/06/2024', 'x', '03/06/2024']])
                item['reading']['tables'][0]['rows'][0]['cells'][2] = cell
                item['reading']['facts'] = [note('*', 'n1')]
                result = materialize('hash', 'v', 1, [item]).rows[0].results[0]
                self.assertEqual((result.kind, result.cause), ('unclassified',
                                                               'printed mark; note not recovered by the reading'))
                item['reading']['facts'].append(note('a', 'n2'))
                result = materialize('hash', 'v', 1, [item]).rows[0].results[0]
                self.assertEqual((result.kind, result.marks, result.cause), ('not-detected', ('*', 'a'), None))

    def test_a_split_word_after_the_result_is_part_of_the_printed_result(self):
        item = block([['123', '02/06/2024', 'POSITIVO DEBOLE', '03/06/2024'],
                      ['124', '02/06/2024', 'POSITIVO (dopo ricampionamento)', '03/06/2024']])
        rows = item['reading']['tables'][0]['rows']
        rows[0]['cells'][2].update(result_value='POSITIVO', annotation='DEBOLE')
        rows[1]['cells'][2].update(result_value='POSITIVO', annotation='(dopo ricampionamento)')
        self.assertEqual([r.results[0].kind for r in materialize('hash', 'v', 1, [item]).rows],
                         ['unclassified', 'positive'])

    def test_result_components_require_supported_literal_and_result_column(self):
        for value, mark, index in [('non rilevato', '*', 2), ('rilevato', '', 2),
                                   ('', 'rilevato*', 2), ('A', '', 0)]:
            with self.subTest(value=value, mark=mark, index=index):
                item = block([['A', '01/06/2024', 'rilevato*', '02/06/2024']])
                item['reading']['tables'][0]['rows'][0]['cells'][index].update(result_value=value, annotation=mark)
                with self.assertRaises(ValueError):
                    materialize('source', 'v', 1, [item])
        item = block([['A', '01/06/2024', '* non rilevato', '02/06/2024']])
        item['reading']['tables'][0]['rows'][0]['cells'][2].update(result_value='non rilevato', annotation='*')
        self.assertEqual(materialize('source', 'v', 1, [item]).rows[0].results[0].kind, 'unclassified')
        item['reading']['facts'] = [{'id': 'f1', 'role': 'result_qualification', 'page': 1, 'locator': 'footnote',
                                     'text': '* nota', 'value': None, 'applies_to': ['p1-t1/r1/c3']}]
        self.assertEqual(materialize('source', 'v', 1, [item]).rows[0].results[0].kind, 'not-detected')

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

    def test_printed_date_shapes_an_abbreviated_month_an_aside_and_a_day_range(self):
        from datetime import date
        context = ((2018, 'issue'),)
        value = literal_date('08-mag-18', year_context=context)
        self.assertEqual((value.text, value.value.isoformat(), value.year_support), ('08-mag-18', '2018-05-08', ('issue',)))
        self.assertEqual(literal_date('08-mag-18').cause, 'year_not_established_by_source_context')
        self.assertEqual(literal_date('8 set. 2017').value.isoformat(), '2017-09-08')
        self.assertEqual(literal_date('31-feb-18', year_context=context).cause, 'invalid_calendar_date')
        self.assertEqual(literal_date('08-xyz-18', year_context=context).cause, 'unparsed_date_literal')
        aside = literal_date('12/2/2018 (prelievo effettuato dal Dr. Boscia)')
        self.assertEqual((aside.text, aside.value.isoformat()),
                         ('12/2/2018 (prelievo effettuato dal Dr. Boscia)', '2018-02-12'))
        days = literal_date('13-16/5/2016')
        self.assertEqual((days.value, days.cause, days.date_range), (None, None, (date(2016, 5, 13), date(2016, 5, 16))))
        self.assertEqual(literal_date('16-13/5/2016').cause, 'invalid_date_range')

    def test_italian_sampling_dates_preserve_agreement_and_real_conflict(self):
        for text, day in [('12 novembre 2021', '12/11/2021'),
                          ('25 Marzo 2017', '25/03/2017'),
                          ('25 agosto 2022', '26/08/2022')]:
            with self.subTest(text=text):
                item = block([['x', day, 'Positivo', '01/12/2024']])
                item['reading']['facts'] = [dict(id='sampling', role='sampling_date', page=1,
                    locator='cover sampling statement', text=text, value=text, applies_to=['report'])]
                row = materialize('hash', 'v', 1, [item]).rows[0]
                self.assertEqual(row.sampling_dates[1].text, text)
                if text == '25 agosto 2022':
                    self.assertIsNone(row.sampling_date)
                    self.assertEqual(row.date_cause, 'conflicting sampling-date values')
                else:
                    self.assertEqual(row.sampling_date, literal_date(day).value)
                    self.assertIsNone(row.date_cause)

    def test_missing_spelled_year_requires_unique_scoped_source_support(self):
        item = block([['x', '29 gennaio', 'Positivo', '01/02/2015']])
        fact = dict(id='sampling', role='sampling_date', page=1, locator='annex heading',
                    text='29/01/2015', value='29/01/2015', applies_to=['report'])
        item['reading']['facts'] = [fact]
        row = materialize('hash', 'v', 1, [item]).rows[0]
        self.assertEqual(row.sampling_date.isoformat(), '2015-01-29')
        self.assertEqual(row.sampling_dates[0].text, '29 gennaio')
        self.assertEqual(row.sampling_dates[0].year_support, ('b1/sampling',))
        for facts in ([], [dict(fact, applies_to=['other-table'])],
                      [fact, dict(fact, id='other', text='29/01/2016', value='29/01/2016')]):
            item['reading']['facts'] = facts
            row = materialize('hash', 'v', 1, [item]).rows[0]
            self.assertIsNone(row.sampling_date)
            self.assertIn('year_not_established_by_source_context', row.date_cause)

    def test_ranges_and_lists_constrain_but_never_supply_exact_sampling_day(self):
        for text, accepted, rejected in [('4-6 Aprile', '05/04/2017', '07/04/2017'),
                                         ('4 e 6 aprile 2017', '06/04/2017', '05/04/2017')]:
            with self.subTest(text=text):
                item = block([['x', text, 'Positivo', '10/04/2017']])
                item['reading']['facts'] = [dict(id='issue', role='report_date', page=1,
                    locator='dateline', text='24/5/2017', value='24/5/2017', applies_to=['report'])]
                row = materialize('hash', 'v', 1, [item]).rows[0]
                self.assertIsNone(row.sampling_date)
                self.assertIn('does not establish an exact day', row.date_cause)
                constraint = row.sampling_dates[0]
                self.assertEqual(constraint.text, text)
                self.assertIsNone(constraint.value)
                if text == '4-6 Aprile':
                    self.assertEqual(constraint.year_support, ('b1/issue',))
                    self.assertEqual(tuple(d.isoformat() for d in constraint.date_range),
                                     ('2017-04-04', '2017-04-06'))
                else:
                    self.assertEqual(tuple(d.isoformat() for d in constraint.listed_dates),
                                     ('2017-04-04', '2017-04-06'))
                for day in (accepted, rejected):
                    item['reading']['facts'] = item['reading']['facts'][:1] + [dict(
                        id='exact', role='sampling_date', page=1, locator='sample date',
                        text=day, value=day, applies_to=['report'])]
                    row = materialize('hash', 'v', 1, [item]).rows[0]
                    if day == accepted:
                        self.assertEqual(row.sampling_date, literal_date(day).value)
                        self.assertIsNone(row.date_cause)
                    else:
                        self.assertIsNone(row.sampling_date)
                        self.assertEqual(row.date_cause, 'conflicting sampling-date values')

    def test_invalid_unparsed_and_unsupported_date_constraints_stay_unresolved(self):
        for text, cause in [('29 febbraio 2023', 'invalid_calendar_date'),
                            ('28-31 febbraio 2024', 'invalid_calendar_date'),
                            ('6-4 aprile 2017', 'invalid_date_range'),
                            ('5/140/2017', 'unparsed_date_literal'),
                            ('4 aprile - 6 maggio 2017', 'unparsed_date_literal')]:
            with self.subTest(text=text):
                item = block([['x', '05/04/2017', 'Positivo', '10/04/2017']])
                item['reading']['facts'] = [dict(id='sampling', role='sampling_date', page=1,
                    locator='cover sampling statement', text=text, value=text, applies_to=['report'])]
                row = materialize('hash', 'v', 1, [item]).rows[0]
                self.assertEqual(row.sampling_dates[1].text, text)
                self.assertIsNone(row.sampling_date)
                self.assertEqual(row.date_cause, cause)

    def test_native_identifier_uses_source_geometry_and_preserves_original(self):
        import pymupdf
        from cordon_d.report_extraction import write_assembled
        from cordon_d.store import put_bytes
        with TemporaryDirectory() as temporary:
            store = Path(temporary)
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
            digest = put_bytes(store, path.read_bytes())
            source = store / 'blobs' / 'sha256' / digest[:2] / digest
            item = block([['ignored', '01/06/2024', 'Positivo', '02/06/2024']])
            item['reading']['tables'][0]['rows'][0]['cells'][0] = {'native_cell': 'p1-t1-r1-c1'}
            item['native_cells']['p1-t1-r1-c1'] = {'text': 'A B\n_', 'page': 1}
            before = materialize(digest, 'v', 1, [item])
            after = positioned_identifiers(before, source)
            self.assertEqual(after.rows[0].reference, 'A_ B')
            self.assertEqual(after.rows[0].cells[0]['basis'],
                             'native cell geometry order; identical non-whitespace character inventory')
            self.assertEqual(after.rows[0].cells[0]['native_text'], 'A B\n_')
            self.assertEqual(before.rows[0].reference, 'A B\n_')
            target = store / 'derived/reports/v' / digest / 'report.json'
            write_assembled(target, {'source_sha256': digest, 'extraction_version': 'v',
                                     'page_count': 1, 'assembly_complete': True, 'blocks': [item]}, store, digest)
            loaded = report(digest, store, extraction_version='v')
            self.assertEqual(loaded.rows[0].reference, 'A_ B')
            payload = json.loads(target.read_text())
            payload['blocks'][0]['native_cells']['p1-t1-r1-c1']['text'] = 'A B\n_X'
            target.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError, 'does not conserve its retained native cell'):
                report(digest, store, extraction_version='v')
            item['native_cells']['p1-t1-r1-c1']['text'] = 'different source'
            with self.assertRaisesRegex(ValueError, 'differs from its source cell'):
                write_assembled(target, {'source_sha256': digest, 'extraction_version': 'v',
                                         'page_count': 1, 'assembly_complete': True, 'blocks': [item]}, store, digest)

    def test_unreordered_positioned_identifier_keeps_native_copy_basis(self):
        import pymupdf
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / 'source.pdf'
            with pymupdf.open() as document:
                page = document.new_page()
                page.draw_rect((40, 40, 150, 100))
                page.draw_line((40, 70), (150, 70))
                page.draw_line((95, 40), (95, 100))
                for position, text in [((50, 60), '00123'), ((105, 60), 'X'),
                                       ((50, 90), 'Y'), ((105, 90), 'Z')]:
                    page.insert_text(position, text, fontsize=11)
                document.save(path)
            item = block([['00123', '01/06/2024', 'Positivo', '02/06/2024']])
            item['reading']['tables'][0]['rows'][0]['cells'][0] = {'native_cell': 'p1-t1-r1-c1'}
            item['native_cells']['p1-t1-r1-c1'] = {'text': '00123', 'page': 1}
            after = positioned_identifiers(materialize('hash', 'v', 1, [item]), path)
            cell = after.rows[0].cells[0]
            self.assertEqual(cell['text'], '00123')
            self.assertNotIn('native_text', cell)  # nothing changed; there is no second reading
            self.assertEqual(cell['basis'], 'native_cell_copy')
            self.assertEqual(cell['check'], 'geometry order agrees with the native cell')

    def test_check_says_what_the_geometry_read_found_in_each_of_its_four_outcomes(self):
        from cordon_d.reports import _geometry_outcome
        self.assertEqual(_geometry_outcome('A_ B', 'A B\n_'),
                         'geometry order applied; inventory identical')
        self.assertEqual(_geometry_outcome('00123', '00123'),
                         'geometry order agrees with the native cell')
        self.assertEqual(_geometry_outcome('', '1334933'),
                         'geometry recovered no comparable text; native cell retained')
        self.assertEqual(_geometry_outcome('  \n ', '1334933'),
                         'geometry recovered no comparable text; native cell retained')
        # A clip that read other text is a disagreement, not an absence: the remedies differ.
        self.assertEqual(_geometry_outcome('1943754\ni it CNR IPSP', '1943754'),
                         'geometry read disagrees with the retained cell; native cell retained')

    def test_a_divergent_geometry_read_keeps_the_native_cell_and_records_what_it_read(self):
        import pymupdf
        from cordon_d.reports import positioned_identifier_records
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / 'source.pdf'
            with pymupdf.open() as document:
                page = document.new_page()
                page.draw_rect((40, 40, 150, 100))
                page.draw_line((40, 70), (150, 70))
                page.draw_line((95, 40), (95, 100))
                # 'Y' sits in the row below, but its glyph box reaches into the cell's bounds.
                for position, text in [((50, 60), '00123'), ((105, 60), 'X'),
                                       ((50, 78), 'Y'), ((105, 90), 'Z')]:
                    page.insert_text(position, text, fontsize=11)
                document.save(path)
            item = block([['00123', '01/06/2024', 'Positivo', '02/06/2024']])
            item['reading']['tables'][0]['rows'][0]['cells'][0] = {'native_cell': 'p1-t1-r1-c1'}
            item['native_cells']['p1-t1-r1-c1'] = {'text': '00123', 'page': 1}
            reading = materialize('hash', 'v', 1, [item])
            record, = positioned_identifier_records(reading, path)
            self.assertEqual(record['check'],
                             'geometry read disagrees with the retained cell; native cell retained')
            self.assertEqual(record['text'], '00123')
            self.assertEqual(record['geometry_text'], '00123\nY')
            cell = positioned_identifiers(reading, path).rows[0].cells[0]
            self.assertEqual(cell['text'], '00123')
            self.assertNotIn('native_text', cell)

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

    def test_fragment_only_table_and_explicit_split_field_reach_ordinary_consumers(self):
        from copy import deepcopy
        from dataclasses import replace
        from cordon_d.reports import record_rows
        from cordon_d.findings import _host_relation
        item = block([['00123', '01/06/2024', 'Negativo', '02/06/2024']])
        data = item['reading']
        head = data['tables'][0]
        head['columns'].append({'role': 'host', 'heading': ['Host']})
        head['rows'][0]['cells'].append({'text': 'Asparagus'})
        tail = deepcopy(head)
        tail.update(id='tail', page=2, columns=[head['columns'][-1]],
                    rows=[{'id': 'r1', 'cells': [{'text': 'acutifolius'}]}])
        data['tables'].append(tail)
        data['pages'].append({'page': 2, 'disposition': 'read'})
        item['targets'].append(2)
        row_scope = head['id'] + '/' + head['rows'][0]['id']
        relation = {'role': 'record_continuation', 'text': '00123', 'value': '00123',
                    'page': 1, 'locator': row_scope + '/c1',
                    'applies_to': [row_scope, 'tail/r1']}
        data['facts'].append(relation)
        raw = materialize('hash', 'v', 2, [item])
        self.assertEqual(len(raw.rows), 2)  # Fragment has neither identifier nor result.
        with self.assertRaisesRegex(ValueError, 'conflicting fields'):
            record_rows(raw)
        field = dict(relation, role='field_continuation',
                     applies_to=[row_scope + '/c5', 'tail/r1/c1'])
        complete = replace(raw, facts=(*raw.facts, field))
        row, = record_rows(complete)
        host, = [c for c in row.cells if c['role'] == 'host']
        self.assertEqual(host['text'], 'Asparagus acutifolius')
        self.assertEqual([c['text'] for c in host['source_fragments']], ['Asparagus', 'acutifolius'])
        self.assertEqual(_host_relation(row, {'fields': {'host': {'text': 'Asparagus acutifolius'}}}),
                         'agrees on printed host')
        self.assertEqual(row.results, raw.rows[0].results)
        self.assertEqual(complete.rows, raw.rows)
        for invalid in (dict(field, applies_to=[row_scope + '/c5', 'missing']),
                        dict(field, value='another'), dict(field, page=2),
                        dict(field, applies_to=[row_scope + '/c5'] * 2)):
            with self.assertRaises(ValueError):
                record_rows(replace(raw, facts=(*raw.facts, invalid)))
        # Neither equal headings nor an unbound fragment creates a sample row.
        data['facts'].remove(relation)
        self.assertEqual(len(materialize('hash', 'v', 2, [item]).rows), 1)

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
            with patch('cordon_d.report_extraction._subscription_call') as call:
                replay = extract_report(digest, store, resume_from=saved['extraction_version'],
                    config=ExtractionConfig(provider='subscription', target_pages=1), budget=None, execute=False)
            call.assert_not_called()
            rebuilt = json.loads(replay.read_text())
            self.assertTrue(rebuilt['assembly_complete'])
            self.assertEqual(record_rows(materialize(digest, 'v', 1, rebuilt['blocks'])), rows)

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
                          'applies_to': ['p1-t1/r1', 'p2-tail/r9']}]
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

    def test_printed_id_label_is_not_part_of_the_identifier(self):
        item = block([['ID: 11200165', '01/06/2024', 'Positivo', '02/06/2024'],
                      ['1401424', '01/06/2024', 'Positivo', '02/06/2024'],
                      ['IDANDROID 12', '01/06/2024', 'Positivo', '02/06/2024'],
                      ['Id 1610615', '01/06/2024', 'Positivo', '02/06/2024']])
        rows = materialize('hash', 'v', 1, [item]).rows
        self.assertEqual(rows[0].cells[0]['identifier'], '11200165')
        self.assertEqual(rows[0].cells[0]['annotation'], 'ID:')
        self.assertEqual(rows[0].cells[0]['text'], 'ID: 11200165')
        self.assertEqual(rows[0].cells[0]['identifier_basis'],
                         'literal ID label prefix; complete cell retained')
        self.assertEqual(rows[0].identifiers, ('11200165',))
        self.assertEqual(rows[1].reference, '1401424')
        self.assertNotIn('identifier', rows[1].cells[0])
        self.assertEqual(rows[2].reference, 'IDANDROID 12')
        self.assertNotIn('identifier', rows[2].cells[0])
        self.assertEqual(rows[3].cells[0]['identifier'], '1610615')
        self.assertEqual(rows[3].cells[0]['annotation'], 'Id')
        self.assertEqual(rows[3].cells[0]['text'], 'Id 1610615')

    def test_two_identifier_cells_keep_every_value_on_the_row(self):
        item = block([['ID: 11200165', '01/06/2024', 'Positivo', '02/06/2024']])
        table = item['reading']['tables'][0]
        table['columns'].append(dict(table['columns'][0], heading=['CODICE ID']))
        table['rows'][0]['cells'].append({'text': '0147/24-1'})
        row = materialize('hash', 'v', 1, [item]).rows[0]
        self.assertIsNone(row.reference)
        self.assertEqual(row.identifiers, ('11200165', '0147/24-1'))
        self.assertEqual(row.cells[0]['text'], 'ID: 11200165')

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

    def test_unresolved_mark_scopes_need_a_matching_qualification(self):
        from cordon_d.report_extraction import unresolved_mark_scopes
        item = block([['123', '02/06/2024', 'non rilevato*', '03/06/2024']])
        reading = item['reading']
        self.assertEqual(unresolved_mark_scopes(reading, {}), ['p1-t1/r1'])
        note = {'id': 'f1', 'role': 'result_qualification', 'page': 1, 'locator': 'footnote',
                'text': '*Prova non accreditata da Accredia.', 'value': None, 'applies_to': ['p1-t1/r1']}
        reading['facts'] = [note]
        self.assertEqual(unresolved_mark_scopes(reading, {}), [])
        reading['facts'] = [dict(note, applies_to=['p1-t1/c3'])]
        self.assertEqual(unresolved_mark_scopes(reading, {}), [])
        native = {'p1-t1-r1-c3': {'text': 'rilevato*', 'page': 1}}
        reading['facts'] = []
        reading['tables'][0]['rows'][0]['cells'][2] = {'native_cell': 'p1-t1-r1-c3'}
        self.assertEqual(unresolved_mark_scopes(reading, native), ['p1-t1/r1'])
        # A mark the source reader split off needs its note just the same.
        reading['tables'][0]['rows'][0]['cells'][2] = {
            'native_cell': 'p1-t1-r1-c3', 'result_value': 'rilevato', 'annotation': '*'}
        self.assertEqual(unresolved_mark_scopes(reading, native), ['p1-t1/r1'])
        reading['facts'] = [note]
        self.assertEqual(unresolved_mark_scopes(reading, native), [])

    @staticmethod
    def _note_answer(text='* Si consiglia di ripetere il prelievo.', qualification='retest',
                     wording='Si consiglia di ripetere il prelievo', applies=('p1-t1/r1/c3',), names=False):
        return {'notes': [{'text': text, 'page': 1, 'locator': 'footnote below the table',
                           'qualification': qualification, 'qualification_text': wording,
                           'applies_to': list(applies), 'names_cells': names}]}

    def test_first_reading_with_a_mark_reads_only_its_note_and_replays_retained(self):
        import pymupdf
        from cordon_d.store import put_bytes
        from cordon_d.report_extraction import (PROMPT, NOTE_PROMPT, NOTE_FIELDS_PROMPT, note_schema,
                                                note_fields_schema, write_json)
        marked = block([['123', '01/06/2024', 'non rilevato*', '02/06/2024']])['reading']
        printed = '* Valori di ciclo quantitativo >30, si consiglia di ricampionare le piante'
        answer = self._note_answer(text=printed, wording='si consiglia di ricampionare le piante')
        stated = {'cq': {'words': 'ciclo quantitativo >30', 'relation': '>', 'values': ['30']},
                  'accreditation': None}
        with TemporaryDirectory() as directory:
            store = Path(directory)
            with pymupdf.open() as pdf:
                pdf.new_page()
                digest = put_bytes(store, pdf.tobytes())
            def fake_call(request, *, config, budget, request_id, raw_path):
                schema = request['output_config']['format']['schema']
                reading = (answer if schema == note_schema() else stated if schema == note_fields_schema()
                           else marked)
                write_json(raw_path, {'response': {'model': config.model, 'stop_reason': 'end_turn',
                                                   'content': [{'text': json.dumps(reading)}]}})
                return copy.deepcopy(reading)
            with patch('cordon_d.report_extraction._call', side_effect=fake_call) as call:
                path = extract_report(digest, store, config=ExtractionConfig(), budget=None)
            self.assertEqual(call.call_count, 3)
            # The fields request carries only the note's printed text.
            fields_request = call.call_args_list[2].args[0]
            self.assertEqual(fields_request['messages'][0]['content'],
                             [{'type': 'text', 'text': NOTE_FIELDS_PROMPT.format(note=printed)}])
            request = call.call_args_list[1].args[0]
            self.assertEqual(request['output_config']['format']['schema'], note_schema())
            self.assertEqual(request['output_config']['effort'], 'medium')
            content = request['messages'][0]['content']
            self.assertEqual([part['type'] for part in content], ['text', 'image', 'text'])
            self.assertEqual(content[0]['text'], 'PHYSICAL PAGE 1: page image')
            self.assertNotIn(PROMPT, content[-1]['text'])
            self.assertTrue(content[-1]['text'].startswith(NOTE_PROMPT.split('{mark}')[0]))
            self.assertIn('"selector": "p1-t1/r1/c3"', content[-1]['text'])
            self.assertIn('"printed_value": "non rilevato*"', content[-1]['text'])
            self.assertIn('"row_identity": ["123"]', content[-1]['text'])
            saved = json.loads(path.read_text())
            self.assertTrue(saved['assembly_complete'])
            item = saved['blocks'][0]
            self.assertEqual(item['reading']['tables'], marked['tables'])
            note = item['reading']['facts'][-1]
            self.assertEqual((note['role'], note['mark'], note['text'], note['applies_to']),
                             ('result_qualification', '*', printed, ['p1-t1/r1/c3']))
            self.assertNotIn('qualification', note)
            self.assertEqual({k: v for k, v in note['fields'].items() if k != 'request_sha256'}, stated)
            self.assertEqual(item['mark_notes'][0]['mark'], '*')
            self.assertGreater(item['mark_notes'][0]['request_bytes'], 0)
            result = report(digest, store, extraction_version=saved['extraction_version']).rows[0].results[0]
            self.assertEqual((result.kind, result.marks, result.accreditation), ('not-detected', ('*',), ()))
            self.assertEqual(result.cq, (dict(stated['cq'], note=result.cq[0]['note']),))
            def forget_assembly():
                path.unlink()
                for cached in path.parent.glob('blocks/*.json'):
                    cached.unlink()
            forget_assembly()
            with patch('cordon_d.report_extraction._call', side_effect=AssertionError('dispatch')):
                replay = extract_report(digest, store, config=ExtractionConfig(), budget=None, execute=False)
            self.assertEqual(json.loads(replay.read_text()), saved)
            forget_assembly()
            (store / 'derived/reports/responses' / f"{item['mark_notes'][0]['request_sha256']}.json").unlink()
            with patch('cordon_d.report_extraction._call', side_effect=AssertionError('dispatch')):
                replay = extract_report(digest, store, config=ExtractionConfig(), budget=None, execute=False)
            unread = json.loads(replay.read_text())
            self.assertFalse(unread['assembly_complete'])
            self.assertEqual(unread['blocks'][0]['reading'], marked)
            self.assertTrue(unread['blocks'][0]['attachment_repair_pending'].startswith('mark note reread pending: '))

    def test_note_fields_must_be_printed_in_the_note(self):
        from cordon_d.report_extraction import accepted_note_fields
        note = '** Valori di ciclo soglia >32.00; si consiglia di prelevare un ulteriore campione.'
        bound = {'words': 'ciclo soglia >32.00', 'relation': '>', 'values': ['32.00']}
        self.assertEqual(accepted_note_fields({'cq': bound, 'accreditation': None}, note),
                         {'cq': bound, 'accreditation': None})
        for cq, defect in [(dict(bound, words='ciclo soglia >35'), 'cq words must quote the note'),
                           (dict(bound, relation='between'), 'cq between needs two values'),
                           (dict(bound, values=['35']), 'cq values must be numbers printed in its words'),
                           (dict(bound, values=['circa 32']), 'cq values must be numbers printed')]:
            with self.subTest(cq=cq), self.assertRaisesRegex(ValueError, defect):
                accepted_note_fields({'cq': cq, 'accreditation': None}, note)
        printed = '*Prova non accreditata da Accredia.'
        stated = {'words': 'Prova non accreditata da Accredia', 'accredited': False, 'body': 'Accredia'}
        self.assertEqual(accepted_note_fields({'cq': None, 'accreditation': stated}, printed)['accreditation'], stated)
        with self.assertRaisesRegex(ValueError, 'accredited true or false'):
            accepted_note_fields({'cq': None, 'accreditation': dict(stated, accredited=None)}, printed)
        with self.assertRaisesRegex(ValueError, 'exactly the keys'):
            accepted_note_fields({'cq': None}, printed)

    def test_a_note_already_read_gets_only_its_fields_read_and_they_reach_the_result(self):
        marked = self._retained_block((('123', '01/06/2024', 'rilevato*', '02/06/2024'),))
        printed = '*Prova non accreditata da Accredia.'
        marked['reading']['facts'] = [{'id': 'mark-note-1', 'role': 'result_qualification', 'page': 1,
                                       'locator': 'footnote', 'section': None, 'text': printed, 'value': None,
                                       'applies_to': ['p1-t1/r1/c3'], 'mark': '*'}]
        stated = {'cq': None, 'accreditation': {'words': 'Prova non accreditata da Accredia', 'accredited': False,
                                                'body': 'Accredia'}}
        config = ExtractionConfig(provider='subscription')
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = self._note_source(store, [marked])
            with patch('cordon_d.report_extraction._subscription_call',
                       side_effect=note_provider([], fields=stated)) as provider:
                path = extract_report(digest, store, config=config, budget=None, resume_from='prior')
            self.assertEqual((provider.call_count, note_calls(provider)), (1, []))
            self.assertEqual(provider.call_args.kwargs['attachments'], [])
            saved = json.loads(path.read_text())
            self.assertTrue(saved['assembly_complete'])
            self.assertEqual(saved['blocks'][0]['request_sha256'], 'retained-request')
            result = report(digest, store, extraction_version=saved['extraction_version']).rows[0].results[0]
            self.assertEqual((result.kind, result.cq), ('detected', ()))
            self.assertEqual([{k: v for k, v in a.items() if k != 'note'} for a in result.accreditation],
                             [stated['accreditation']])

    def test_a_combined_mark_needs_a_note_for_each_of_its_marks(self):
        from cordon_d.report_extraction import unresolved_marked_cells
        def note(text, applies_to, **extra):
            return dict({'id': f'f{len(text)}', 'role': 'result_qualification', 'page': 1, 'locator': 'footnote',
                         'text': text, 'value': None, 'applies_to': applies_to}, **extra)
        item = block([['123', '02/06/2024', 'rilevato*a', '03/06/2024']])
        item['reading']['facts'] = [note('*Prova non accreditata da Accredia.', ['p1-t1/r1'])]
        self.assertEqual([c['marks'] for c in unresolved_marked_cells(item['reading'], {})], [['a']])
        item['reading']['facts'].append(note("a L'esito si riferisce al campione suddiviso in aliquote.", ['p1-t1/c3']))
        self.assertEqual(unresolved_marked_cells(item['reading'], {}), [])
        self.assertEqual(materialize('hash', 'v', 1, [item]).rows[0].results[0].kind, 'detected')
        # '**=' begins a note for '**'; a note read for its mark need not begin with it.
        item = block([['124', '02/06/2024', 'Negativo**', '03/06/2024']])
        item['reading']['facts'] = [note('**= Si consiglia di ricampionare la pianta', ['p1-t1/r1/c3'])]
        self.assertEqual(unresolved_marked_cells(item['reading'], {}), [])
        item['reading']['facts'] = [note('Prova non accreditata da Accredia**', ['p1-t1/r1/c3'], mark='**')]
        self.assertEqual(unresolved_marked_cells(item['reading'], {}), [])
        self.assertEqual(materialize('hash', 'v', 1, [item]).rows[0].results[0].kind, 'negative')

    def _note_source(self, store, blocks, page_text=None, pages=1):
        import pymupdf
        from cordon_d.store import put_bytes
        with pymupdf.open() as pdf:
            page = pdf.new_page()
            if page_text:
                for index, line in enumerate(page_text):
                    page.insert_text((72, 100 + 400 * index), line)
            for number in range(2, pages + 1):
                pdf.new_page().draw_rect((72, 72, 72 + number * 10, 90))  # Distinct scanned-like pages.
            digest = put_bytes(store, pdf.tobytes())
        read = {page for item in blocks for page in item['targets']}
        blocks = [*blocks, *({'targets': [n], 'request_sha256': f'retained-{n}', 'context_pages': [],
                              'supplied_pages': [n], 'native_cells': {}, 'native_regions': [], 'reading': {
                                  'pages': [{'page': n, 'disposition': 'read'}], 'tables': [], 'facts': [],
                                  'issues': [], 'context_pages': []}}
                             for n in range(1, pages + 1) if n not in read)]
        prior = store / 'derived/reports/prior' / digest / 'report.json'
        prior.parent.mkdir(parents=True)
        prior.write_text(json.dumps({'source_sha256': digest, 'extraction_version': 'prior',
            'page_count': pages, 'assembly_complete': True, 'blocks': blocks}))
        return digest

    def test_note_search_reads_later_pages_one_at_a_time_until_the_note_is_found(self):
        marked = self._retained_block()
        found = {'notes': [dict(self._note_answer()['notes'][0], page=3)]}
        config = ExtractionConfig(provider='subscription')
        with TemporaryDirectory() as directory:
            store = Path(directory)
            unmarked = [{'targets': [n], 'request_sha256': f'retained-{n}', 'context_pages': [], 'supplied_pages': [n],
                         'native_cells': {}, 'native_regions': [], 'reading': {
                             'pages': [{'page': n, 'disposition': 'read'}], 'tables': [], 'facts': [],
                             'issues': [], 'context_pages': []}} for n in (2, 3, 4)]
            digest = self._note_source(store, [marked, *unmarked], pages=4)
            with patch('cordon_d.report_extraction._subscription_call',
                       side_effect=note_provider([{'notes': []}, {'notes': []}, found])) as provider:
                path = extract_report(digest, store, config=config, budget=None, resume_from='prior')
            self.assertEqual(len(note_calls(provider)), 3)
            self.assertEqual([[label for _, _, label in c.kwargs['attachments']] for c in note_calls(provider)],
                             [['PHYSICAL PAGE 1: page image'], ['PHYSICAL PAGE 2: page image'],
                              ['PHYSICAL PAGE 3: page image']])
            saved = json.loads(path.read_text())
            self.assertTrue(saved['assembly_complete'])
            self.assertEqual([r['notes'] for r in saved['blocks'][0]['mark_notes']], [0, 0, 1])
            self.assertEqual(saved['blocks'][0]['reading']['facts'][-1]['page'], 3)
            self.assertIn(3, saved['blocks'][0]['supplied_pages'])

    def test_a_note_cited_on_a_page_not_shown_is_read_from_that_page(self):
        marked = self._retained_block()
        elsewhere = {'notes': [dict(self._note_answer()['notes'][0], page=3)]}
        config = ExtractionConfig(provider='subscription')
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = self._note_source(store, [marked], pages=4)
            with patch('cordon_d.report_extraction._subscription_call',
                       side_effect=note_provider([elsewhere, elsewhere])) as provider:
                path = extract_report(digest, store, config=config, budget=None, resume_from='prior')
            # The page the answer named is shown next, ahead of the ordinary order; no correction.
            self.assertEqual([[label for _, _, label in c.kwargs['attachments']] for c in note_calls(provider)],
                             [['PHYSICAL PAGE 1: page image'], ['PHYSICAL PAGE 3: page image']])
            self.assertNotIn('failed a check', note_calls(provider)[1].kwargs['prompt'])
            saved = json.loads(path.read_text())
            self.assertTrue(saved['assembly_complete'])
            records = saved['blocks'][0]['mark_notes']
            self.assertEqual([(r['notes'], r.get('cites_unshown_pages')) for r in records], [(0, [3]), (1, None)])
            note = saved['blocks'][0]['reading']['facts'][-1]
            self.assertEqual((note['page'], note['note_request_sha256']), (3, records[1]['request_sha256']))
        # A page already shown is not shown again: an answer citing it gets the one correction,
        # and the note is accepted only from the page the request showed.
        from cordon_d.report_extraction import NOTE_CORRECTION
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = self._note_source(store, [marked], pages=3)
            on_two = {'notes': [dict(elsewhere['notes'][0], page=2)]}
            answers = [{'notes': []}, {'notes': [dict(elsewhere['notes'][0], page=1)]}, on_two]
            with patch('cordon_d.report_extraction._subscription_call', side_effect=note_provider(answers)) as provider:
                path = extract_report(digest, store, config=config, budget=None, resume_from='prior')
            self.assertEqual([[label for _, _, label in c.kwargs['attachments']] for c in note_calls(provider)],
                             [['PHYSICAL PAGE 1: page image'], ['PHYSICAL PAGE 2: page image'],
                              ['PHYSICAL PAGE 2: page image']])
            cites_one = ('Mark note cites page 1, which was not supplied; a note read from the supplied source has '
                         'its physical page number, 2, whatever page number is printed on the page')
            self.assertIn(NOTE_CORRECTION.format(defect=cites_one), note_calls(provider)[2].kwargs['prompt'])
            saved = json.loads(path.read_text())
            self.assertTrue(saved['assembly_complete'])
            self.assertEqual(saved['blocks'][0]['reading']['facts'][-1]['page'], 2)
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = self._note_source(store, [marked], pages=3)
            on_one = {'notes': [dict(elsewhere['notes'][0], page=1)]}
            with patch('cordon_d.report_extraction._subscription_call',
                       side_effect=note_provider([{'notes': []}, on_one, on_one])) as provider:
                path = extract_report(digest, store, config=config, budget=None, resume_from='prior')
            self.assertEqual(len(note_calls(provider)), 3)
            saved = json.loads(path.read_text())
            self.assertFalse(saved['assembly_complete'])
            self.assertEqual(saved['blocks'][0]['attachment_repair_pending'],
                             f'mark note reread pending: {cites_one}; the note correction also failed: {cites_one}')
        # When the named page does not hold the note, the set-aside answer gets its one correction
        # from the page it was given, and its note is accepted there.
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = self._note_source(store, [marked], pages=3)
            on_one = {'notes': [dict(elsewhere['notes'][0], page=1)]}
            with patch('cordon_d.report_extraction._subscription_call',
                       side_effect=note_provider([elsewhere, {'notes': []}, elsewhere, on_one])) as provider:
                path = extract_report(digest, store, config=config, budget=None, resume_from='prior')
            calls = note_calls(provider)
            self.assertEqual([[label for _, _, label in c.kwargs['attachments']] for c in calls],
                             [['PHYSICAL PAGE 1: page image'], ['PHYSICAL PAGE 3: page image'],
                              ['PHYSICAL PAGE 1: page image'], ['PHYSICAL PAGE 1: page image']])
            self.assertEqual(calls[2].kwargs['request_id'], calls[0].kwargs['request_id'])
            self.assertIn(NOTE_CORRECTION.format(defect=(
                'Mark note cites page 3, which was not supplied; a note read from the supplied source has its '
                'physical page number, 1, whatever page number is printed on the page')), calls[3].kwargs['prompt'])
            saved = json.loads(path.read_text())
            self.assertTrue(saved['assembly_complete'])
            self.assertEqual(saved['blocks'][0]['reading']['facts'][-1]['page'], 1)

    def test_a_note_printed_anywhere_defines_its_mark_for_every_marked_cell(self):
        marked = self._retained_block((('123', '01/06/2024', 'negativo*', '02/06/2024'),
                                       ('124', '01/06/2024', 'Positivo*', '02/06/2024')))
        later = {'notes': [dict(self._note_answer(applies=('p1-t1/r1/c3',))['notes'][0], page=2)]}
        config = ExtractionConfig(provider='subscription')
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = self._note_source(store, [marked], pages=3)
            with patch('cordon_d.report_extraction._subscription_call',
                       side_effect=note_provider([{'notes': []}, later, {'notes': []}])) as provider:
                path = extract_report(digest, store, config=config, budget=None, resume_from='prior')
            self.assertEqual(len(note_calls(provider)), 3)
            saved = json.loads(path.read_text())
            self.assertTrue(saved['assembly_complete'])
            found, extended = saved['blocks'][0]['reading']['facts'][-2:]
            self.assertEqual((found['applies_to'], extended['applies_to']), (['p1-t1/r1/c3'], ['p1-t1/r2/c3']))
            self.assertEqual((extended['text'], extended['page'], extended['note_request_sha256']),
                             (found['text'], 2, found['note_request_sha256']))
            self.assertEqual(extended['scope_basis'],
                             'linked by the printed mark; the only note printed for it in the document')
            rows = report(digest, store, extraction_version=saved['extraction_version']).rows
            self.assertEqual([(r.results[0].kind, r.results[0].marks) for r in rows],
                             [('negative', ('*',)), ('positive', ('*',))])

    def test_a_mark_no_page_defines_is_recorded_as_printed_without_a_meaning(self):
        marked = self._retained_block((('123', '01/06/2024', 'negativo*', '02/06/2024'),))
        config = ExtractionConfig(provider='subscription')
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = self._note_source(store, [marked], pages=3)
            with patch('cordon_d.report_extraction._subscription_call',
                       side_effect=note_provider([{'notes': []}] * 3)) as provider:
                path = extract_report(digest, store, config=config, budget=None, resume_from='prior')
            self.assertEqual([[label for _, _, label in c.kwargs['attachments']] for c in note_calls(provider)],
                             [[f'PHYSICAL PAGE {n}: page image'] for n in (1, 2, 3)])
            saved = json.loads(path.read_text())
            self.assertTrue(saved['assembly_complete'])
            fact = saved['blocks'][0]['reading']['facts'][-1]
            self.assertEqual((fact['role'], fact['mark'], fact['text'], fact['applies_to'],
                              fact['pages_examined'], fact['scope_basis']),
                             ('result_qualification', '*', '*', ['p1-t1/r1/c3'], [1, 2, 3],
                              'the document prints the mark without a meaning'))
            # A mark printed without a meaning has no note text, so nothing reads its fields.
            self.assertNotIn('fields', fact)
            self.assertNotIn('note_request_sha256', fact)
            result = report(digest, store, extraction_version=saved['extraction_version']).rows[0].results[0]
            self.assertEqual((result.kind, result.text, result.cause, result.marks, result.cq),
                             ('negative', 'negativo*', None, ('*',), ()))

    @staticmethod
    def _retained_block(rows=(('123', '01/06/2024', 'non rilevato*', '02/06/2024'),)):
        marked = block([list(row) for row in rows])
        marked.update(request_sha256='retained-request', context_pages=[1],
                      supplied_pages=[1], native_regions=[])
        return marked

    def test_resume_resolves_a_mark_from_its_note_alone(self):
        from cordon_d.report_extraction import PROMPT
        marked = self._retained_block()
        config = ExtractionConfig(provider='subscription')
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = self._note_source(store, [marked])
            with patch('cordon_d.report_extraction._subscription_call',
                       side_effect=note_provider(self._note_answer())) as provider:
                path = extract_report(digest, store, config=config, budget=None, resume_from='prior')
            self.assertEqual(len(note_calls(provider)), 1)
            request = note_calls(provider)[-1].kwargs
            self.assertEqual(request['config'].effort, 'medium')
            self.assertEqual([(name, label) for name, _, label in request['attachments']],
                             [('note-1-page-1.png', 'PHYSICAL PAGE 1: page image')])
            self.assertTrue(request['attachments'][0][1].startswith(b'\x89PNG'))
            self.assertNotIn(PROMPT, request['prompt'])
            self.assertIn('p1-t1/r1/c3', request['prompt'])
            saved = json.loads(path.read_text())
            item = saved['blocks'][0]
            self.assertTrue(saved['assembly_complete'])
            self.assertEqual(item['request_sha256'], 'retained-request')
            self.assertEqual(item['reading']['tables'], marked['reading']['tables'])
            self.assertEqual(item['mark_notes'][0]['request_sha256'], request['request_id'])
            result = report(digest, store, extraction_version=saved['extraction_version']).rows[0].results[0]
            self.assertEqual((result.kind, result.text, result.cause, result.marks, result.cq),
                             ('not-detected', 'non rilevato*', None, ('*',), ()))

    def test_pending_note_read_leaves_assembly_unattested_until_executed(self):
        marked = self._retained_block()
        config = ExtractionConfig(provider='subscription')
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = self._note_source(store, [marked])
            with patch('cordon_d.report_extraction._subscription_call',
                       side_effect=AssertionError('dispatch')) as provider:
                path = extract_report(digest, store, config=config, budget=None,
                                      resume_from='prior', execute=False)
            provider.assert_not_called()
            saved = json.loads(path.read_text())
            self.assertFalse(saved['assembly_complete'])
            self.assertEqual(saved['blocks'][0]['attachment_repair_pending'],
                'mark note reread pending: No retained response for this mark note read; '
                'explicit execution is required')
            self.assertEqual(saved['blocks'][0]['reading'], marked['reading'])
            loaded = report(digest, store, extraction_version=saved['extraction_version'])
            self.assertIs(loaded.assembly_complete, False)
            # A notes-only execution reads the note and nothing else.
            with patch('cordon_d.report_extraction._subscription_call',
                       side_effect=note_provider(self._note_answer())) as provider:
                path = extract_report(digest, store, config=config, budget=None,
                                      resume_from='prior', execute='mark notes')
            self.assertEqual(len(note_calls(provider)), 1)
            saved = json.loads(path.read_text())
            self.assertTrue(saved['assembly_complete'])
            self.assertNotIn('attachment_repair_pending', saved['blocks'][0])

    def test_a_note_that_does_not_name_its_cells_is_linked_by_its_mark(self):
        marked = self._retained_block((('123', '01/06/2024', 'negativo*', '02/06/2024'),
                                       ('124', '01/06/2024', 'Positivo*', '02/06/2024')))
        answer = self._note_answer(text='*Prova non accreditata da Accredia.', qualification='other',
                                   wording='Prova non accreditata da Accredia', applies=())
        config = ExtractionConfig(provider='subscription')
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = self._note_source(store, [marked])
            with patch('cordon_d.report_extraction._subscription_call', side_effect=note_provider(answer)) as provider:
                path = extract_report(digest, store, config=config, budget=None, resume_from='prior')
            self.assertEqual(len(note_calls(provider)), 1)
            self.assertIn('p1-t1/r2/c3', note_calls(provider)[-1].kwargs['prompt'])
            saved = json.loads(path.read_text())
            self.assertTrue(saved['assembly_complete'])
            note = saved['blocks'][0]['reading']['facts'][-1]
            self.assertEqual(note['applies_to'], ['p1-t1/r1/c3', 'p1-t1/r2/c3'])
            self.assertEqual(note['scope_basis'], 'linked by the printed mark')
            rows = report(digest, store, extraction_version=saved['extraction_version']).rows
            self.assertEqual([(r.results[0].kind, r.results[0].marks) for r in rows],
                             [('negative', ('*',)), ('positive', ('*',))])

    def test_a_note_that_names_some_cells_leaves_the_others_pending(self):
        marked = self._retained_block((('123', '01/06/2024', 'negativo*', '02/06/2024'),
                                       ('124', '01/06/2024', 'Positivo*', '02/06/2024')))
        answer = self._note_answer(text='* Campione 123 pervenuto danneggiato.', qualification='damaged_sample',
                                   wording='pervenuto danneggiato', applies=('p1-t1/r1/c3',), names=True)
        config = ExtractionConfig(provider='subscription')
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = self._note_source(store, [marked])
            with patch('cordon_d.report_extraction._subscription_call', side_effect=note_provider(answer)):
                path = extract_report(digest, store, config=config, budget=None, resume_from='prior')
            saved = json.loads(path.read_text())
            self.assertFalse(saved['assembly_complete'])
            self.assertEqual(saved['blocks'][0]['attachment_repair_pending'],
                'mark note reread pending: no printed note for mark * recovered for p1-t1/r2/c3 '
                'from page 1 page image')
            rows = report(digest, store, extraction_version=saved['extraction_version']).rows
            self.assertEqual((rows[0].results[0].kind, rows[0].results[0].marks), ('negative', ('*',)))
            self.assertEqual((rows[1].results[0].kind, rows[1].results[0].cause),
                             ('unclassified', 'printed mark; note not recovered by the reading'))

    def test_malformed_note_answer_gets_one_correction(self):
        from cordon_d.report_extraction import NOTE_CORRECTION
        marked = self._retained_block()
        misquoted = self._note_answer(wording='Si raccomanda un nuovo prelievo')
        config = ExtractionConfig(provider='subscription')
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = self._note_source(store, [marked])
            with patch('cordon_d.report_extraction._subscription_call',
                       side_effect=note_provider([misquoted, self._note_answer()])) as provider:
                path = extract_report(digest, store, config=config, budget=None, resume_from='prior')
            self.assertEqual(len(note_calls(provider)), 2)
            correction = note_calls(provider)[1].kwargs
            defect = 'Qualification wording must quote the note'
            self.assertIn(NOTE_CORRECTION.format(defect=defect), correction['prompt'])
            self.assertEqual(correction['config'].effort, 'medium')
            self.assertEqual(correction['attachments'], note_calls(provider)[0].kwargs['attachments'])
            saved = json.loads(path.read_text())
            self.assertTrue(saved['assembly_complete'])
            record = saved['blocks'][0]['mark_notes'][0]
            self.assertEqual((record['correction_of'], record['defect'], record['request_sha256']),
                             (note_calls(provider)[0].kwargs['request_id'], defect, correction['request_id']))
        malformed = {'notes': [dict(self._note_answer()['notes'][0], applies_to=['p9-t9/r9/c9'])]}
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = self._note_source(store, [marked])
            with patch('cordon_d.report_extraction._subscription_call',
                       side_effect=note_provider([misquoted, malformed])) as provider:
                path = extract_report(digest, store, config=config, budget=None, resume_from='prior')
            self.assertEqual(len(note_calls(provider)), 2)
            saved = json.loads(path.read_text())
            self.assertFalse(saved['assembly_complete'])
            self.assertEqual(saved['blocks'][0]['attachment_repair_pending'],
                'mark note reread pending: Qualification wording must quote the note; the note correction '
                'also failed: Mark note names a cell that was not supplied')
            self.assertEqual(saved['blocks'][0]['reading'], marked['reading'])

    def test_text_layer_supplies_only_the_note_region_and_checks_its_quotation(self):
        from cordon_d.report_extraction import note_source_steps, accepted_notes
        import pymupdf
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = self._note_source(store, [self._retained_block()],
                                       page_text=['Rapporto di prova 123', '* Si consiglia di ripetere il prelievo.'])
            from cordon_d.store import blob_path
            cells = [{'cell': 'p1-t1/r1/c3', 'page': 1, 'text': 'non rilevato*', 'marks': ['*']}]
            with pymupdf.open(blob_path(store, digest)) as document:
                steps = list(note_source_steps(document, '*', cells, [], 72))
                sources = steps[0]
                self.assertEqual([(s['page'], s['kind'], s['text']) for s in sources],
                                 [(1, 'text region', '* Si consiglia di ripetere il prelievo.')])
                # If the region does not answer, the search continues with the page image.
                self.assertEqual([[(s['page'], s['kind']) for s in step] for step in steps[1:]],
                                 [[(1, 'page image')]])
                self.assertLess(sources[0]['bbox'][3] - sources[0]['bbox'][1], 40)
                check = dict(mark='*', cells=cells, sources=sources, page_text=lambda n: document[n - 1].get_text())
                self.assertEqual(accepted_notes(self._note_answer(), **check)[0]['text'],
                                 '* Si consiglia di ripetere il prelievo.')
                with self.assertRaisesRegex(ValueError, 'not printed in the text layer of page 1'):
                    accepted_notes(self._note_answer(text='* Si consiglia di ripetere il campione.',
                                                     wording='ripetere'), **check)
                with self.assertRaisesRegex(ValueError, 'does not carry its printed mark'):
                    accepted_notes(self._note_answer(text='Si consiglia di ripetere il prelievo.'), **check)
                with self.assertRaisesRegex(ValueError, 'names no supplied cell'):
                    accepted_notes(self._note_answer(applies=(), names=True), **check)

    def test_a_note_reaches_the_row_for_the_detector_as_it_does_for_the_classifier(self):
        from cordon_d.report_extraction import unresolved_mark_scopes
        note = {'id': 'f1', 'role': 'result_qualification', 'page': 1, 'locator': 'footnote',
                'text': '* Prova non accreditata da Accredia.', 'value': None,
                'applies_to': ['report']}
        reaching = {'report-wide note': [note],
                    'note on a reached statement': [dict(note, applies_to=['f2']),
                        {'id': 'f2', 'role': 'qualification', 'page': 1, 'locator': 'caption',
                         'text': 'Esiti della prova', 'value': None, 'applies_to': ['p1-t1/r1']}]}
        for reach, facts in reaching.items():
            with self.subTest(reach=reach):
                item = block([['123', '01/06/2024', 'non rilevato*', '02/06/2024']])
                item['reading']['facts'] = facts
                self.assertEqual(unresolved_mark_scopes(item['reading'], {}), [])
                row = materialize('hash', 'v', 1, [item]).rows[0]
                self.assertEqual(row.results[0].kind, 'not-detected')
                self.assertEqual(row.results[0].text, 'non rilevato*')
                self.assertIsNone(row.results[0].cause)

    def test_sospetto_does_not_trigger_mark_repair(self):
        import pymupdf
        from cordon_d.store import put_bytes
        from cordon_d.report_extraction import unresolved_mark_scopes
        reading = block([['123', '01/06/2024', 'Sospetto', '02/06/2024']])['reading']
        self.assertEqual(unresolved_mark_scopes(reading, {}), [])
        with TemporaryDirectory() as directory:
            store = Path(directory)
            with pymupdf.open() as pdf:
                pdf.new_page()
                digest = put_bytes(store, pdf.tobytes())
            with patch('cordon_d.report_extraction._call', return_value=reading) as call:
                extract_report(digest, store, config=ExtractionConfig(), budget=None)
            self.assertEqual(call.call_count, 1)

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

    def test_printed_mark_classifies_only_through_its_recovered_note(self):
        # CNR prints "non rilevato*" with "*Prova non accreditata da Accredia." below the table.
        item = block([['123', '02/06/2024', 'non rilevato*', '03/06/2024'],
                      ['124', '02/06/2024', 'rilevatoa', '03/06/2024'],
                      ['125', '02/06/2024', 'Positivo**', '03/06/2024']])
        item['reading']['facts'] = [
            {'id': 'f1', 'role': 'result_qualification', 'page': 1, 'locator': 'footnote below table',
             'text': '*Prova non accreditata da Accredia.', 'value': None, 'applies_to': ['p1-t1/r1']},
            {'id': 'f2', 'role': 'result_qualification', 'page': 1, 'locator': 'footnote below table',
             'text': "a L'esito si riferisce a ciascun campione suddiviso in aliquote.", 'value': None,
             'applies_to': ['p1-t1/c3']}]
        rows = materialize('hash', 'v', 1, [item]).rows
        first, second, third = (row.results[0] for row in rows)
        self.assertEqual((first.kind, first.text, first.cause), ('not-detected', 'non rilevato*', None))
        self.assertIn('f1', {f['id'].split('/')[-1] for f in rows[0].facts})
        self.assertEqual((second.kind, second.text), ('detected', 'rilevatoa'))
        # A mark no recovered note explains keeps the result unclassified and says why.
        self.assertEqual((third.kind, third.cause), ('unclassified', 'printed mark; note not recovered by the reading'))
        # A note is never a licence to strip: a bare literal without a mark is untouched, and a
        # word that merely ends in the marker letter is not a marked result.
        item = block([['126', '02/06/2024', 'rilevata', '03/06/2024'], ['127', '02/06/2024', 'Sospetto', '03/06/2024']])
        item['reading']['facts'] = [{'id': 'f1', 'role': 'result_qualification', 'page': 1, 'locator': 'footnote',
                                     'text': 'a nota', 'value': None, 'applies_to': ['report']}]
        rows = materialize('hash', 'v', 1, [item]).rows
        self.assertEqual([r.results[0].kind for r in rows], ['detected', 'unclassified'])
        self.assertIsNone(rows[1].results[0].cause)

    def test_a_letter_mark_equal_to_the_literals_last_letter_is_separated_once(self):
        # CNR prints the feminine "rilevataa" and "non rilevataa": the mark a follows a word
        # that itself ends in a. The mark is separated once, where the base is a result.
        item = block([['123', '02/06/2024', 'rilevataa', '03/06/2024'],
                      ['124', '02/06/2024', 'non rilevataa', '03/06/2024']])
        item['reading']['facts'] = [
            {'id': 'f1', 'role': 'result_qualification', 'page': 1, 'locator': 'footnote below table',
             'text': "a L'esito delle analisi si riferisce ai risultati ottenuti sul campione suddiviso in aliquote.",
             'value': None, 'applies_to': ['p1-t1/c3'], 'mark': 'a'}]
        rows = materialize('hash', 'v', 1, [item]).rows
        self.assertEqual([(r.results[0].kind, r.results[0].text, r.results[0].cause, r.results[0].marks)
                          for r in rows],
                         [('detected', 'rilevataa', None, ('a',)),
                          ('not-detected', 'non rilevataa', None, ('a',))])

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


    def test_tampered_native_identifier_on_assembled_reading_is_refused(self):
        import pymupdf
        from cordon_d.report_extraction import write_assembled
        from cordon_d.store import put_bytes
        with TemporaryDirectory() as temporary:
            store = Path(temporary)
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
            digest = put_bytes(store, path.read_bytes())
            item = block([['ignored', '01/06/2024', 'Positivo', '02/06/2024']])
            item['reading']['tables'][0]['rows'][0]['cells'][0] = {'native_cell': 'p1-t1-r1-c1'}
            item['native_cells']['p1-t1-r1-c1'] = {'text': 'A B\n_', 'page': 1}
            target = store / 'derived/reports/v' / digest / 'report.json'
            write_assembled(target, {'source_sha256': digest, 'extraction_version': 'v',
                                     'page_count': 1, 'assembly_complete': True, 'blocks': [item]}, store, digest)
            payload = json.loads(target.read_text())
            self.assertTrue(payload.get('positioned_identifiers'))
            payload['blocks'][0]['native_cells']['p1-t1-r1-c1']['text'] = 'A B\n_X'
            target.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError, 'does not conserve its retained native cell'):
                report(digest, store, extraction_version='v')

    def test_tampered_unreordered_native_identifier_on_assembled_reading_is_refused(self):
        import pymupdf
        from cordon_d.report_extraction import write_assembled
        from cordon_d.store import put_bytes
        with TemporaryDirectory() as temporary:
            store = Path(temporary)
            path = Path(temporary) / 'source.pdf'
            with pymupdf.open() as document:
                page = document.new_page()
                page.draw_rect((40, 40, 150, 100))
                page.draw_line((40, 70), (150, 70))
                page.draw_line((95, 40), (95, 100))
                for position, text in [((50, 60), '00123'), ((105, 60), 'X'),
                                       ((50, 90), 'Y'), ((105, 90), 'Z')]:
                    page.insert_text(position, text, fontsize=11)
                document.save(path)
            digest = put_bytes(store, path.read_bytes())
            item = block([['00123', '01/06/2024', 'Positivo', '02/06/2024']])
            item['reading']['tables'][0]['rows'][0]['cells'][0] = {'native_cell': 'p1-t1-r1-c1'}
            item['native_cells']['p1-t1-r1-c1'] = {'text': '00123', 'page': 1}
            target = store / 'derived/reports/v' / digest / 'report.json'
            write_assembled(target, {'source_sha256': digest, 'extraction_version': 'v',
                                     'page_count': 1, 'assembly_complete': True, 'blocks': [item]}, store, digest)
            payload = json.loads(target.read_text())
            record, = payload['positioned_identifiers']
            # The positioned reading of an unchanged cell is that cell's text, and the
            # read path compares against it; the majority of positioned cells are these.
            self.assertEqual(record['text'], '00123')
            self.assertEqual(record['check'], 'geometry order agrees with the native cell')
            self.assertEqual(report(digest, store, extraction_version='v').rows[0].reference, '00123')
            payload['blocks'][0]['native_cells']['p1-t1-r1-c1']['text'] = '00124'
            target.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError, 'does not conserve its retained native cell'):
                report(digest, store, extraction_version='v')

    def test_a_native_identifier_cell_whose_record_was_removed_is_refused(self):
        import pymupdf
        from cordon_d.report_extraction import write_assembled
        from cordon_d.store import put_bytes
        with TemporaryDirectory() as temporary:
            store = Path(temporary)
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
            digest = put_bytes(store, path.read_bytes())
            item = block([['ignored', '01/06/2024', 'Positivo', '02/06/2024']])
            item['reading']['tables'][0]['rows'][0]['cells'][0] = {'native_cell': 'p1-t1-r1-c1'}
            item['native_cells']['p1-t1-r1-c1'] = {'text': 'A B\n_', 'page': 1}
            target = store / 'derived/reports/v' / digest / 'report.json'
            write_assembled(target, {'source_sha256': digest, 'extraction_version': 'v',
                                     'page_count': 1, 'assembly_complete': True, 'blocks': [item]}, store, digest)
            payload = json.loads(target.read_text())
            self.assertEqual([sorted(record) for record in payload['positioned_identifiers']],
                             [['check', 'locator', 'source_bbox', 'text']])
            self.assertEqual(report(digest, store, extraction_version='v').rows[0].reference, 'A_ B')
            for absent in ([], None):  # the reading carries the key; its records were removed
                payload['positioned_identifiers'] = absent
                target.write_text(json.dumps(payload))
                with self.assertRaisesRegex(ValueError, 'without a positioned record'):
                    report(digest, store, extraction_version='v')

    def test_a_reading_assembled_before_positioned_identifiers_reads_as_unread(self):
        import pymupdf
        from cordon_d.report_extraction import write_assembled
        from cordon_d.reports import reports
        from cordon_d.store import put_bytes
        with TemporaryDirectory() as temporary:
            store = Path(temporary)
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
            digest = put_bytes(store, path.read_bytes())
            item = block([['ignored', '01/06/2024', 'Positivo', '02/06/2024']])
            item['reading']['tables'][0]['rows'][0]['cells'][0] = {'native_cell': 'p1-t1-r1-c1'}
            item['native_cells']['p1-t1-r1-c1'] = {'text': 'A B\n_', 'page': 1}
            target = store / 'derived/reports/v' / digest / 'report.json'
            write_assembled(target, {'source_sha256': digest, 'extraction_version': 'v',
                                     'page_count': 1, 'assembly_complete': True, 'blocks': [item]}, store, digest)
            payload = json.loads(target.read_text())
            # An earlier retained version carries no such key at all: unread, not fatal.
            del payload['positioned_identifiers']
            target.write_text(json.dumps(payload))
            unread = report(digest, store, extraction_version='v')
            self.assertEqual(unread, UnreadReport(digest, 'assembled before positioned identifiers '
                                                          'were derived; reassemble at this extraction version'))
            root = store / 'reports'
            root.mkdir()
            (root / 'records.json').write_text(json.dumps([
                {'url': 'https://publisher.example/a.pdf', 'captured_at': '2026-01-01T00:00:00+00:00',
                 'sha256': digest},
                {'url': 'https://publisher.example/b.pdf', 'captured_at': '2026-01-02T00:00:00+00:00',
                 'sha256': 'f' * 64}]))
            self.assertEqual([read.cause for read in reports(root, store, extraction_version='v')],
                             [unread.cause, 'declared source bytes unavailable'])

    def test_retained_cell_that_disagrees_with_source_is_refused_on_assembly(self):
        import pymupdf
        from cordon_d.report_extraction import write_assembled
        from cordon_d.store import put_bytes
        with TemporaryDirectory() as temporary:
            store = Path(temporary)
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
            digest = put_bytes(store, path.read_bytes())
            item = block([['ignored', '01/06/2024', 'Positivo', '02/06/2024']])
            item['reading']['tables'][0]['rows'][0]['cells'][0] = {'native_cell': 'p1-t1-r1-c1'}
            item['native_cells']['p1-t1-r1-c1'] = {'text': 'different source', 'page': 1}
            target = store / 'derived/reports/v' / digest / 'report.json'
            with self.assertRaisesRegex(ValueError, 'Retained native identifier differs from its source cell'):
                write_assembled(target, {'source_sha256': digest, 'extraction_version': 'v',
                                         'page_count': 1, 'assembly_complete': True, 'blocks': [item]}, store, digest)

    def test_write_assembled_refuses_a_payload_under_another_extraction_version(self):
        from cordon_d.report_extraction import write_assembled
        with TemporaryDirectory() as temporary:
            store = Path(temporary)
            digest = 'abc'
            target = store / 'derived/reports/v' / digest / 'report.json'
            with self.assertRaisesRegex(ValueError, 'never written under another extraction version'):
                write_assembled(target, {'source_sha256': digest, 'extraction_version': 'other',
                                         'page_count': 1, 'blocks': []}, store, digest)


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
