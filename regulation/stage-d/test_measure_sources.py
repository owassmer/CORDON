"""Native composition checks, distinct from whole-act semantic qualification."""
from pathlib import Path
from copy import deepcopy
from tempfile import TemporaryDirectory
import json
import unittest

import pymupdf

from cordon_d.measure_sources import (source_material, table_fields, material_context,
                                      context_matches, selected_association, CONTEXT_MARKER,
                                      native_span, field_fragment, span_overlaps)
from cordon_d.measures import MeasureReading, retained_measure, _validate_reading
from cordon_d.store import blob_path, put_bytes, store_root
from test_source_associations import source


class NativeTargetFields(unittest.TestCase):
    def test_recovered_continuation_metadata_preserves_only_identical_source_addresses(self):
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = source(store, [{'rows': [['A', 'R 1', '1/2/2025', 'OWNER A'],
                                              ['B', 'R 2', '2/2/2025', 'OWNER B']]}])
            material, _ = source_material([digest], store)
            original = material_context(material)
            row = material['tables']['S0P1T1']['rows'][2]
            row['continuation_of'] = 'S0P1T1R2'
            self.assertTrue(context_matches(original, material))
            recorded = material_context(material)
            row['continuation_of'] = 'S0P1T1R1'
            self.assertFalse(context_matches(recorded, material))
            row.pop('continuation_of')
            self.assertFalse(context_matches(recorded, material))
            material['tables']['S0P1T1']['cells']['1']['text'] = 'changed source cell'
            self.assertFalse(context_matches(original, material))

    def test_printed_native_fields_do_not_need_or_create_a_report_association(self):
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = source(store, [{
                'headings': ['ID CAMPIONE', 'SPECIE', 'LONGITUDINE', 'LATITUDINE'],
                'rows': [['A', 'Olivo', '17,123400', '40,567800'], ['B', 'Mandorlo', '', '']]}])
            material, associations = source_material([digest], store)
            fields, association = table_fields(material, 'S0P1T1', 2, {})
            self.assertIsNone(association)
            self.assertFalse(associations[0].rows)
            self.assertEqual({role: field['text'] for role, field in fields.items()},
                             dict(plant_id='A', host='Olivo', longitude='17,123400', latitude='40,567800'))
            self.assertEqual(fields['longitude']['header']['text'], 'LONGITUDINE')
            self.assertEqual(fields['longitude']['source'], digest)
            self.assertTrue(fields['longitude']['bbox'])
            self.assertNotEqual(fields['longitude']['locator'], fields['longitude']['header']['locator'])
            blank, _ = table_fields(material, 'S0P1T1', 3, {})
            self.assertEqual((blank['longitude']['text'], blank['latitude']['text']), ('', ''))
            reference, _ = table_fields(material, 'S0P1T1', 2, {'reference_plant_id': 1})
            self.assertNotIn('plant_id', reference)
            self.assertEqual(reference['reference_plant_id']['text'], 'A')
            self.assertNotIn('native_header', material_context(material))
            unselected = dict(target_scopes=[], prose_positions=[], image_positions=[])
            self.assertFalse(tuple(MeasureReading({'reading': unselected}, material, associations).targets()))

    def test_ambiguous_header_does_not_assign_native_roles(self):
        headers = ['ID CAMPIONE', 'SPECIE', 'LONGITUDINE', 'LATITUDINE']
        cases = [dict(headings=['ID CAMPIONE', 'SPECIE', 'SPECIE', 'LATITUDINE'],
                      rows=[['A', 'Olivo', 'Mandorlo', '40,5']]),
                 dict(headings=headers, rows=[['A', 'Olivo', '17,1', '40,5'], headers,
                                              ['B', 'Mandorlo', '17,2', '40,6']])]
        for spec in cases:
            with self.subTest(spec=spec), TemporaryDirectory() as directory:
                store = Path(directory)
                digest = source(store, [spec])
                material, _ = source_material([digest], store)
                fields, association = table_fields(material, 'S0P1T1', 2, {})
                self.assertFalse(fields)
                self.assertIsNone(association)
                self.assertIn('did not establish one unique',
                              material['tables']['S0P1T1']['native_field_issue'])
                self.assertNotIn('native_field_issue', material_context(material))

    def test_existing_association_and_its_field_objects_are_unchanged(self):
        with TemporaryDirectory() as directory:
            store = Path(directory)
            digest = source(store, [{
                'headings': ['ID CAMPIONE', 'RAPPORTO PROVA', 'DATA RAPPORTO PROVA',
                             'SPECIE', 'LONGITUDINE', 'LATITUDINE', 'PROPRIETARIO'],
                'widths': [55, 70, 105, 70, 70, 70, 80],
                'rows': [['A', 'R 1', '1/2/2025', 'Olivo', '17,1', '40,5', 'OWNER A']]}])
            material, associations = source_material([digest], store)
            original, = associations[0].rows
            before = deepcopy(original)
            fields, association = table_fields(material, 'S0P1T1', 2, {'addressee': 7})
            self.assertIs(association, original)
            self.assertEqual(original, before)
            for role, field in original['fields'].items():
                self.assertIs(fields[role], field)
            self.assertEqual(fields['addressee']['text'], 'OWNER A')

    def test_retained_request_gains_only_printed_fields_without_changing_source_context(self):
        store = store_root(Path(__file__).resolve())
        digest = 'cba7890acf17bfe84beacb7449e51149f67e77f6a0efb58da6fb57aab7987ab2'
        try:
            measure = retained_measure(
                'a0052a8c6a338dbb053480dc90fbbf7417bf2889cad2809e48e4479816d14ec8', store)
        except FileNotFoundError:
            self.skipTest('Retained source/response unavailable; no extraction in tests')
        # Independently viewed DDS135 Annex C, physical page 15. The table
        # prints these values but no report-reference or report-date columns.
        expected = {'1250279': ('17,32672096', '40,77161778'),
                    '1249548': ('17,3272942', '40,77127073'),
                    '1250102': ('17,32682455', '40,77134573'),
                    '1250770': ('17,32670868', '40,77135487'),
                    '1247330': ('17,29996696', '40,76160935')}
        targets = {t['reference']: t for t in measure.prescribed_targets()}
        self.assertEqual(set(targets), set(expected))
        self.assertTrue(context_matches(measure.response['request']['prompt'], measure.material))
        with pymupdf.open(blob_path(store, digest)) as original:
            for reference, coordinates in expected.items():
                target = targets[reference]
                self.assertIsNone(target['association'])
                self.assertNotIn('report_reference', target['fields'])
                self.assertNotIn('report_date', target['fields'])
                self.assertEqual(target['fields']['host']['text'], 'Olivo')
                self.assertEqual(tuple(target['fields'][role]['text'] for role in ('longitude', 'latitude')),
                                 coordinates)
                for role in ('host', 'longitude', 'latitude'):
                    field = target['fields'][role]
                    self.assertEqual((field['source'], field['page']), (digest, 15))
                    self.assertEqual(original[14].get_text(clip=pymupdf.Rect(field['bbox'])).strip(), field['text'])
        self.assertTrue(all(not matches for _, matches in measure.target_associations(store)))


class MixedSourceComposition(unittest.TestCase):
    def test_disjoint_image_row_keeps_native_table_but_overlap_and_whole_page_are_refused(self):
        with TemporaryDirectory() as directory:
            store = Path(directory)
            native = source(store, [{'rows': [['A', 'R 1', '1/2/2025', 'OWNER A']]}])
            with pymupdf.open() as image_document:
                page = image_document.new_page(width=500, height=60)
                page.insert_text((10, 30), 'B | PARCEL 7 | OWNER B', fontsize=14)
                pixels = page.get_pixmap().tobytes('png')
            for name, box in [('disjoint', (40, 300, 540, 360)),
                              ('overlap', (40, 150, 540, 210))]:
                with self.subTest(layout=name), pymupdf.open(blob_path(store, native)) as document:
                    document[0].insert_image(pymupdf.Rect(box), stream=pixels)
                    digest = put_bytes(store, document.tobytes())
                    material, associations = source_material([digest], store)
                    table_ref, = material['tables']
                    image_ref, = material['images']
                    support = [dict(source=digest, page=1, locator='raster row',
                                    quote='B | PARCEL 7 | OWNER B')]
                    values = dict(identity=dict(adopted=None), events=[], issues=[],
                        directions=[dict(id='work', mode='ordered-now', work='removal')],
                        parts=[dict(source=digest, pages=[1], role='target-table')],
                        target_scopes=[dict(table_ref=table_ref, first_row=2, last_row=2,
                            columns=[dict(role='addressee', column=4)], direction_ids=['work'],
                            meaning='native row', support=[dict(source=digest, page=1,
                                locator='native table row 2', quote='A')])],
                        prose_positions=[], image_positions=[dict(image_ref=image_ref,
                            association_ref=None, direction_ids=['work'], meaning='raster row',
                            fields=[dict(role='plant_id', transcription='B'),
                                    dict(role='parcel', transcription='7'),
                                    dict(role='addressee', transcription='OWNER B')], support=support)])
                    if name == 'overlap':
                        with self.assertRaisesRegex(ValueError, 'Use native table cells'):
                            _validate_reading(values, [digest], store, material)
                        continue
                    _validate_reading(values, [digest], store, material)
                    targets = {t['reference']: t for t in
                               MeasureReading({'reading': values}, material, associations).prescribed_targets()}
                    self.assertEqual(set(targets), {'A', 'B'})
                    self.assertIs(targets['A']['association'], associations[0].rows[0])
                    self.assertEqual(targets['B']['parcel'], '7')
                    self.assertEqual(targets['B']['fields']['plant_id']['derivation'],
                                     'model transcription of source image')
                    self.assertEqual(targets['B']['source_position']['bbox'], list(box))
                    values['image_positions'][0]['image_ref'] = 'S0P1'
                    with self.assertRaisesRegex(ValueError, 'Use native table cells'):
                        _validate_reading(values, [digest], store, material)


class NativeWordPositions(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.store = Path(temporary.name)
        self.digest = source(self.store, [dict(
            headings=['ID CAMPIONE', 'SPECIE'], widths=[240, 240],
            rows=[['SAME SAME', 'Olivo']]), dict(
            headings=['COMUNE', 'PROPRIETARIO'], widths=[240, 240],
            rows=[['Town', 'OWNER FAMILY']])])
        self.material, self.associations = source_material([self.digest], self.store)
        self.plants = self.line(['SAME', 'SAME'])
        self.host = self.line(['Olivo'])
        self.owner = self.line(['OWNER', 'FAMILY'])
        self.values = dict(identity=dict(adopted=None), events=[], issues=[], references=[],
            directions=[dict(id='work', mode='ordered-now', work='removal')],
            parts=[dict(source=self.digest, pages=[1, 2], role='target-table')],
            target_scopes=[], image_positions=[],
            prose_positions=[self.position(0), self.position(1)])

    def line(self, words):
        return next(ref for ref, line in self.material['lines'].items() if line['words'] == words)

    def span(self, ref, start=0, end=1):
        return dict(line_ref=ref, first_word=start, end_word=end)

    def position(self, start):
        return dict(fields=[dict(role='plant_id', spans=[self.span(self.plants, start, start + 1)]),
                            dict(role='host', spans=[self.span(self.host)])],
                    direction_ids=['work'], meaning='One selected printed occurrence',
                    support=[dict(source=self.digest, page=1, locator='Printed native words', quote='SAME')])

    def validate(self):
        _validate_reading(self.values, [self.digest], self.store, self.material)

    def test_cell_interior_words_keep_distinct_occurrences_and_shared_context(self):
        self.validate()
        targets = MeasureReading({'reading': self.values}, self.material,
                                 self.associations).prescribed_targets()
        self.assertEqual([t['reference'] for t in targets], ['SAME', 'SAME'])
        self.assertNotEqual(targets[0]['occurrence'], targets[1]['occurrence'])
        self.assertNotEqual(targets[0]['fields']['plant_id']['fragments'][0]['locator'],
                            targets[1]['fields']['plant_id']['fragments'][0]['locator'])
        self.assertEqual(targets[0]['fields']['host'], targets[1]['fields']['host'])
        context, _ = json.JSONDecoder().raw_decode(material_context(self.material)[len(CONTEXT_MARKER):])
        self.assertEqual(context['lines'][self.plants], ['SAME', 'SAME'])
        self.assertNotIn('word_boxes', material_context(self.material))
        fragment = native_span(self.material, self.span(self.plants))
        self.assertNotIn('word_boxes', fragment)
        self.assertNotIn('word_characters', fragment)
        self.assertEqual(fragment['bbox'], self.material['lines'][self.plants]['bbox'])

    def test_duplicate_or_overlapping_identifying_spans_are_not_new_positions(self):
        for start, end in [(0, 1), (0, 2)]:
            with self.subTest(start=start, end=end):
                self.values['prose_positions'][1]['fields'][0]['spans'] = [
                    self.span(self.plants, start, end)]
                with self.assertRaisesRegex(ValueError, 'one selection'):
                    self.validate()
        self.values['prose_positions'] = [self.position(0)]
        self.values['prose_positions'][0]['fields'][0]['spans'] *= 2
        with self.assertRaisesRegex(ValueError, 'repeated or overlapping'):
            self.validate()

    def test_native_cell_and_words_cannot_select_the_same_position_twice(self):
        self.values['target_scopes'] = [dict(table_ref='S0P1T1', first_row=2, last_row=2,
            columns=[], direction_ids=['work'], meaning='Printed cell',
            support=self.values['prose_positions'][0]['support'])]
        with self.assertRaisesRegex(ValueError, 'one selection'):
            self.validate()

    def test_table_continuation_span_does_not_occupy_other_words_on_its_line(self):
        digest = source(self.store, [dict(headings=['ID CAMPIONE', 'SPECIE'],
                                         widths=[240, 240], rows=[['', 'Olivo']])])
        with pymupdf.open(blob_path(self.store, digest)) as document:
            document.new_page().insert_text((40, 60), 'FIRST SECOND')
            self.digest = put_bytes(self.store, document.tobytes())
        self.material, self.associations = source_material([self.digest], self.store)
        line = self.line(['FIRST', 'SECOND'])
        support = [dict(source=self.digest, page=page, locator='Printed occurrence', quote=text)
                   for page, text in [(1, 'Olivo'), (2, 'FIRST SECOND')]]
        own_cell = self.material['tables']['S0P1T1']['rows'][1]['cells'][0]
        self.values = dict(identity=dict(adopted=None), directions=[], events=[], issues=[], parts=[],
            image_positions=[], target_scopes=[dict(table_ref='S0P1T1', first_row=2, last_row=2,
                columns=[dict(role='plant_id', column=1, fragments=[
                    dict(table_ref='S0P1T1', cell=own_cell), self.span(line)])],
                direction_ids=[], meaning='Continued native field', support=support)],
            prose_positions=[dict(fields=[dict(role='plant_id', spans=[self.span(line, 1, 2)])],
                                  direction_ids=[], meaning='Separate position', support=support)])
        self.validate()
        self.values['prose_positions'][0]['fields'][0]['spans'] = [self.span(line)]
        with self.assertRaisesRegex(ValueError, 'one selection'):
            self.validate()

    def test_shared_cross_page_field_requires_its_own_source_support(self):
        for position in self.values['prose_positions']:
            position['fields'].append(dict(role='addressee', spans=[self.span(self.owner, 0, 2)]))
        with self.assertRaisesRegex(ValueError, 'every selected source page'):
            self.validate()
        for position in self.values['prose_positions']:
            position['support'].append(dict(source=self.digest, page=2, locator='Shared owner',
                                            quote='OWNER FAMILY'))
        self.validate()
        targets = tuple(MeasureReading({'reading': self.values}, self.material, self.associations).targets())
        self.assertEqual([t['addressee_text'] for t in targets], ['OWNER FAMILY', 'OWNER FAMILY'])
        self.material['lines'][self.owner]['source'] = 'another-supplied-document'
        with self.assertRaisesRegex(ValueError, 'within its source document'):
            self.validate()

    def test_partial_address_context_is_neither_current_nor_legacy(self):
        complete = material_context(self.material)
        self.assertTrue(context_matches(complete, self.material))
        context, _ = json.JSONDecoder().raw_decode(complete[len(CONTEXT_MARKER):])
        del context['lines'][self.plants]
        self.assertFalse(context_matches(CONTEXT_MARKER + json.dumps(context), self.material))
        # A modified source word is never excused by compatibility.
        changed = deepcopy(self.material)
        changed['lines'][self.host]['words'] = ['another literal']
        self.assertFalse(context_matches(complete, changed))

    def test_ownership_uses_selected_words_not_the_center_of_their_line(self):
        digest = source(self.store, [dict(rows=[['A', 'R 1', '1/2/2025', 'OWNER']])])
        with pymupdf.open(blob_path(self.store, digest)) as document:
            # One native line begins outside the table and ends in its owned
            # plant cell. Its first and last words have different ownership.
            document[0].insert_text((0, 160), 'LEFT      OWNED', fontsize=10)
            self.digest = put_bytes(self.store, document.tobytes())
        self.material, self.associations = source_material([self.digest], self.store)
        line = self.line(['LEFT', 'OWNED'])
        position = dict(fields=[dict(role='parcel', spans=[self.span(line)])],
                        direction_ids=[], meaning='Outside the table',
                        support=[dict(source=self.digest, page=1, locator='Native line', quote='LEFT')])
        self.values = dict(identity=dict(adopted=None), directions=[], events=[], issues=[], parts=[],
                           target_scopes=[], image_positions=[], prose_positions=[position])
        self.validate()
        position['fields'][0]['spans'] = [self.span(line, 1, 2)]
        with self.assertRaisesRegex(ValueError, 'association owner'):
            self.validate()
        position['fields'][0]['spans'] = [self.span(line)]
        self.material['lines'][line]['word_boxes'] = None
        with self.assertRaisesRegex(ValueError, 'exact word geometry'):
            self.validate()
        self.values['prose_positions'] = []
        self.validate()  # The unselected limitation does not block other reading content.

    def test_adjacent_glyph_envelope_is_not_cell_membership_but_partial_owned_word_is(self):
        digest = source(self.store, [dict(headings=['SAME', 'OWNER'], widths=[240, 240],
                                         rows=[['SAME', 'NAME']])])
        with pymupdf.open(blob_path(self.store, digest)) as document:
            # The first word's font box grazes the next table. The second word
            # actually contributes characters to its cell despite starting outside.
            document[0].insert_text((44, 97.5), 'SAME', fontsize=10)
            document[0].insert_text((25, 130), 'CROSSING', fontsize=10)
            digest = put_bytes(self.store, document.tobytes())
        material, _ = source_material([digest], self.store)
        table, = material['tables'].values()
        adjacent = next(ref for ref, line in material['lines'].items()
                        if line['words'] == ['SAME'] and line['bbox'][1] < 100)
        span = self.span(adjacent)
        self.assertGreater(material['lines'][adjacent]['word_boxes'][0][3], table['bbox'][1])
        self.assertFalse(span_overlaps(material, span, [table]))
        self.assertEqual(field_fragment(material, span)['text'], 'SAME')
        for ref, line in material['lines'].items():
            if ref != adjacent and line['words'] in [['SAME'], ['CROSSING']]:
                self.assertTrue(span_overlaps(material, self.span(ref), [table]))
                with self.assertRaisesRegex(ValueError, 'Use source cells'):
                    field_fragment(material, self.span(ref))
        # Exact membership is necessary, not something to replace with the old
        # overlap guess when native provenance is unavailable.
        material['cell_characters'] = {}
        with self.assertRaisesRegex(ValueError, 'native cell character membership'):
            field_fragment(material, span)

    def test_retained_adjacent_continuations_and_parcels_keep_their_native_occurrences(self):
        store = store_root(Path(__file__).resolve())
        digest = '882c0020ab2ce0e55c06c9d72b36b3bd0204d02a48b6c35120c81bc050d958cd'
        if not blob_path(store, digest).exists():
            self.skipTest('Retained source store unavailable')
        material, _ = source_material([digest], store)
        for page, expected in [(58, 'CATERINA,IMMOBILIARE SANRO S.R.L.,'),
                               (62, 'ANGELA,MASTROLONARDO ROSA,MASTROLONARDO FILOMENA')]:
            fragment = field_fragment(material, self.span(f'S0P{page}L5', 0, 3))
            self.assertEqual(fragment['text'], expected)
            self.assertEqual((fragment['source'], fragment['page']), (digest, page))
        for page, cell, expected in [(43, '11', '786'), (75, '25', '39')]:
            span = self.span(f'S0P{page}L4')
            table = material['tables'][f'S0P{page}T1']
            area = dict(table['cells'][cell], source=digest, page=page)
            self.assertNotEqual(area['text'], expected)
            self.assertEqual(native_span(material, span)['text'], expected)
            self.assertFalse(span_overlaps(material, span, [area]))


class RetainedSourceComposition(unittest.TestCase):
    def test_explicit_fragments_preserve_shared_owners_across_page_breaks(self):
        store = store_root(Path(__file__).resolve())
        digest = '3b5813789b43ef0861c283175ab607fa32cfba7c1d2057a55b291aa8f8097a48'
        if not blob_path(store, digest).exists():
            self.skipTest('Retained source store unavailable')
        material, associations = source_material([digest], store)
        # DDS63 pp28–29 and 31–32: the visible shared owner cells cross the
        # page break. These are composition fixtures, not model-reading evidence.
        scopes = [dict(table_ref=ref, first_row=1, last_row=end,
                       columns=[dict(role='addressee', column=11, fragments=fragments)],
                       direction_ids=[], meaning='', support=[])
                  for ref, end, fragments in [
                      ('S0P29T1', 2, [dict(table_ref='S0P28T1', cell='127'),
                                      dict(table_ref='S0P29T1', cell='141')]),
                      ('S0P32T1', 3, [dict(table_ref='S0P31T1', cell='54'),
                                      dict(table_ref='S0P32T1', cell='131')])]]
        values = dict(target_scopes=scopes, prose_positions=[], image_positions=[])
        targets = tuple(MeasureReading({'reading': values}, material, associations).targets())
        self.assertEqual([(t['reference'], t['addressee_text'].split()) for t in targets], [
            ('1662477', ['AFFATATO', 'GIOVANNI']), ('1662474', ['AFFATATO', 'GIOVANNI']),
            ('1665471', ['PANNARALE', 'ANNA', 'CONTESSA', 'VITO', 'ONOFRIO']),
            ('1665518', ['PANNARALE', 'ANNA', 'CONTESSA', 'VITO', 'ONOFRIO']),
            ('1665224', ['PANNARALE', 'ANNA', 'CONTESSA', 'VITO', 'ONOFRIO'])])
        self.assertEqual(len(targets[0]['fields']['addressee']['fragments']), 2)
        # Without an explicit relationship the same readable blank stays blank.
        untouched, _ = table_fields(material, 'S0P29T1', 1, {'addressee': 11})
        self.assertEqual(untouched['addressee']['text'], '')

    def test_explicit_fragments_reach_an_owner_only_final_page(self):
        store = store_root(Path(__file__).resolve())
        digest = '3b5813789b43ef0861c283175ab607fa32cfba7c1d2057a55b291aa8f8097a48'
        if not blob_path(store, digest).exists():
            self.skipTest('Retained source store unavailable')
        material, _ = source_material([digest], store)
        # DDS63 pp36–37: the final page contains only the end of the shared
        # column. No new plant is supplied by its three native text lines.
        fragments = [dict(table_ref='S0P36T1', cell='130'),
                     *(dict(line_ref=f'S0P37L{i}', first_word=0, end_word=1) for i in (4, 5, 6))]
        fields, association = table_fields(material, 'S0P36T1', 12,
                                            {'addressee': 11}, {'addressee': fragments})
        self.assertEqual(association['fields']['plant_id']['text'], '1663404')
        self.assertEqual(fields['addressee']['text'].split(),
                         'CARBONARA ROSA CARBONARA FRANCESCO CARBONARA MARIA '
                         'CARBONARA VINCENZO CARBONARA MICHELE'.split())
        self.assertEqual([f['page'] for f in fields['addressee']['fragments']], [36, 37, 37, 37])
        for mutation, message in [
                ([*fragments, fragments[-1]], 'repeats'),
                (fragments[1:], 'retain its selected row cell'),
                ([fragments[0], dict(table_ref='S0P36T1', cell=material['tables']['S0P36T1']['rows'][0]['cells'][2])],
                 'already supplies this source column')]:
            with self.assertRaisesRegex(ValueError, message):
                table_fields(material, 'S0P36T1', 12, {'addressee': 11}, {'addressee': mutation})

    def test_shared_continuation_reaches_every_governed_plant_and_requires_support(self):
        store = store_root(Path(__file__).resolve())
        digest = 'c1634b3e15707cf8fbe27f08f33e343de62fd7b7e8c5146fd9a10c11b7e7475c'
        if not blob_path(store, digest).exists():
            self.skipTest('Retained source store unavailable')
        material, associations = source_material([digest], store)
        # Independently viewed DDS116 pp21–22: both 10/315 plants share one
        # long owner cell. Its owner-only continuation does not make a target.
        scope = dict(table_ref='S0P21T1', first_row=4, last_row=5,
                     columns=[dict(role='addressee', column=11, fragments=[
                         dict(table_ref='S0P21T1', cell='44'), dict(table_ref='S0P22T1', cell='71')])],
                     direction_ids=[], meaning='', support=[dict(source=digest, page=21,
                         locator='Annex 1/C, shared owner cell', quote='RUBINO MARIO')])
        values = dict(identity={'adopted': None}, directions=[], parts=[], events=[], issues=[],
                      target_scopes=[scope], prose_positions=[], image_positions=[])
        with self.assertRaisesRegex(ValueError, 'every source page'):
            _validate_reading(values, [digest], store, material)
        scope['support'].append(dict(source=digest, page=22,
                                    locator='Annex 1/C, first row', quote='RUBINO ROSA'))
        _validate_reading(values, [digest], store, material)
        targets = tuple(MeasureReading({'reading': values}, material, associations).targets())
        self.assertEqual([t['reference'] for t in targets], ['1697345', '1697339'])
        expected = ('RUBINO MARIO RUBINO MICHELE MARIA OTTOLINO VINCENZO GRANDOLFO SERAFINA '
                    'ADDANTE GIUSEPPE OTTOLINO GIOVANNI GIANNELLI ANNA MARIA ROSARIA RUBINO MICHELE '
                    'OTTOLINO GENNARO OTTOLINO NICOLA GRANDOLFO NATALE CARMELO ALESSANDRO '
                    'ADDANTE GIOVANNI RUBINO ALFREDO RUBINO ROSA RUBINO VINCENZO RUBINO ANNALISA '
                    'ADDANTE VINCENZO RUBINO ANGELA ADDANTE GIOVANNI ADDANTE MARIA OTTOLINO MARIA '
                    'GRANDOLFO MARISTELLA').split()
        for target in targets:
            self.assertEqual(target['addressee_text'].split(), expected)
            self.assertIs(target['fields']['report_reference'], target['association']['fields']['report_reference'])

    def test_explicit_fragments_reject_empty_overlapping_and_owned_text(self):
        store = store_root(Path(__file__).resolve())
        sources = ['3b5813789b43ef0861c283175ab607fa32cfba7c1d2057a55b291aa8f8097a48',
                   'c1634b3e15707cf8fbe27f08f33e343de62fd7b7e8c5146fd9a10c11b7e7475c']
        if not all(blob_path(store, digest).exists() for digest in sources):
            self.skipTest('Retained source store unavailable')
        material, _ = source_material(sources, store)
        first = dict(table_ref='S0P36T1', cell='130')
        owned_line = next(ref for ref, line in material['lines'].items()
                          if line['source'] == sources[0] and line['page'] == 36
                          and line['words'] == ['1663404'])
        for fragments, message in [
                ([first, dict(line_ref=owned_line, first_word=0, end_word=1)], 'inside a native table'),
                ([first, dict(table_ref='S1P21T1', cell='43')], 'within its source document'),
                ([first, dict(line_ref='S0P37L2', first_word=0, end_word=4),
                  dict(line_ref='S0P37L2', first_word=3, end_word=5)], 'overlapping spans')]:
            with self.assertRaisesRegex(ValueError, message):
                table_fields(material, 'S0P36T1', 12, {'addressee': 11}, {'addressee': fragments})
        with self.assertRaisesRegex(ValueError, 'no recovered source text'):
            table_fields(material, 'S0P29T1', 1, {'addressee': 11},
                         {'addressee': [dict(table_ref='S0P29T1', cell='141')]})

    def test_current_position_role_governs_reused_predecessor_fields(self):
        store = store_root(Path(__file__).resolve())
        current = '1d2e9b6111cdb33de96f1b1abeb49c1d3ad35019994404a74e59320d7850c2aa'
        predecessor = '8e90240666712b38ba635d04e195e23df9dd7fcbbf501928090a0ee96041d955'
        if not all(blob_path(store, digest).exists() for digest in (current, predecessor)):
            self.skipTest('Retained source store unavailable')
        material, associations = source_material([current, predecessor], store)
        position = dict(image_ref='S0P8', association_ref=dict(table_ref='S1P17T1', row=8),
                        fields=[dict(role='addressee', transcription='RESCINA GERARDO')],
                        meaning='', direction_ids=['work'], support=[])
        values = dict(target_scopes=[], prose_positions=[], image_positions=[position],
                      directions=[dict(id='work', mode='ordered-now', work='removal')],
                      parts=[dict(source=current, pages=[8], role='target-table'),
                             dict(source=predecessor, pages=[17], role='other')])
        reading = MeasureReading({'reading': values}, material, associations)
        target, = reading.prescribed_targets()
        self.assertEqual(target['reference'], '1804248')
        self.assertEqual(target['source_position']['source'], current)
        self.assertEqual(target['association']['source_sha256'], predecessor)
        # A predecessor's target table cannot turn current map context into an order.
        values['parts'][0]['role'] = 'map'
        values['parts'][1]['role'] = 'target-table'
        self.assertFalse(reading.prescribed_targets())

    def test_association_continuity_requires_support_for_both_source_positions(self):
        store = store_root(Path(__file__).resolve())
        try:
            proposal = retained_measure(
                'fd3259db3555db83e5d26a86abcb59c6f140c45faa2bccd08ca7d86c8ddfa48a', store)
        except FileNotFoundError:
            self.skipTest('Retained source-row reading unavailable; no extraction in tests')
        predecessor = '8e90240666712b38ba635d04e195e23df9dd7fcbbf501928090a0ee96041d955'
        sources = [*proposal.response['request']['sources'], predecessor]
        material, _ = source_material(sources, store)
        reading = deepcopy(proposal.values)
        position = next(p for p in reading['image_positions'] if any(
            f['role'] == 'plant_id' and f['transcription'] == '1804248' for f in p['fields']))
        position['association_ref'] = dict(table_ref='S1P17T1', row=8)
        position['fields'] = [f for f in position['fields'] if f['role'] == 'addressee']
        with self.assertRaisesRegex(ValueError, 'both source positions'):
            _validate_reading(reading, sources, store, material)
        position['support'].append(dict(source=predecessor, page=17,
                                        locator='Annex 1/B, infected-plant row 6', quote='1804248'))
        _validate_reading(reading, sources, store, material)

    def test_image_position_can_select_but_cannot_overwrite_an_existing_association(self):
        store = store_root(Path(__file__).resolve())
        digest = '8e90240666712b38ba635d04e195e23df9dd7fcbbf501928090a0ee96041d955'
        if not blob_path(store, digest).exists():
            self.skipTest('Retained source store unavailable')
        material, associations = source_material([digest], store)
        reference = dict(table_ref='S0P17T1', row=8)
        owned = selected_association(material, reference)
        self.assertEqual(owned['fields']['plant_id']['text'], '1804248')
        self.assertIsNone(selected_association(material, None))
        with self.assertRaisesRegex(ValueError, 'no established association'):
            selected_association(material, dict(table_ref='S0P20T2', row=3))
        with self.assertRaisesRegex(ValueError, 'outside'):
            selected_association(material, dict(table_ref='S0P17T1', row=0))
        position = dict(image_ref='S0P17', association_ref=reference,
                        fields=[dict(role='plant_id', transcription='a conflicting identity')],
                        meaning='', direction_ids=[], support=[])
        reading = MeasureReading({'reading': dict(target_scopes=[], prose_positions=[],
                                                  image_positions=[position])}, material, associations)
        with self.assertRaisesRegex(ValueError, 'already supplies'):
            tuple(reading.targets())

    def test_parcel_position_preserves_printed_section_without_filling_other_rows(self):
        store = store_root(Path(__file__).resolve())
        digest = '8e90240666712b38ba635d04e195e23df9dd7fcbbf501928090a0ee96041d955'
        if not blob_path(store, digest).exists():
            self.skipTest('Retained source store unavailable')
        material, associations = source_material([digest], store)
        # DDS43 physical page 20: Bari section A is printed for the first two
        # positions; the following Triggiano position has a blank section cell.
        scope = dict(table_ref='S0P20T2', first_row=3, last_row=5,
                     columns=[dict(role=role, column=i) for i, role in enumerate(
                         ['municipality', 'cadastral_section', 'sheet', 'parcel', 'addressee'], 1)],
                     direction_ids=[], meaning='', support=[])
        reading = MeasureReading({'reading': dict(target_scopes=[scope], prose_positions=[],
                                                  image_positions=[])}, material, associations)
        targets = tuple(reading.targets())
        self.assertEqual([(t['municipality'], t['cadastral_section'], t['sheet'], t['parcel'])
                          for t in targets], [('BARI', 'A', '72', '41'), ('BARI', 'A', '72', '149'),
                                               ('TRIGGIANO', '', '8', '124')])
        self.assertTrue(all(t['reference'] is None and t['association'] is None for t in targets))

    def test_compact_addresses_replay_existing_sources_without_ignoring_changed_values(self):
        store = store_root(Path(__file__).resolve())
        response_path = store / 'derived/document-readings/6f31e677689ecf211f5103abfa7ccd1c33c32ec9ff50130e8614b57527de764d.json'
        if not response_path.exists():
            self.skipTest('Retained whole-measure request unavailable')
        response = json.loads(response_path.read_text())
        material, _ = source_material(response['request']['sources'], store)
        prompt = response['request']['prompt']
        self.assertTrue(context_matches(prompt, material))
        compact = material_context(material)
        self.assertTrue(context_matches(compact, material))
        original, _ = json.JSONDecoder().raw_decode(prompt.split(CONTEXT_MARKER, 1)[1])
        self.assertLess(len(compact), len(json.dumps(original)))
        changed = deepcopy(material)
        changed['tables']['S0P15T1']['cells']['1']['text'] = 'a different source value'
        self.assertFalse(context_matches(prompt, changed))
        self.assertFalse(context_matches(compact, changed))

    def test_verified_split_row_keeps_one_association_and_complete_addressee(self):
        store = store_root(Path(__file__).resolve())
        digest = '44f299b0d9183377a846fd2c6e9125cbbd7d69e2edac29718b3e5112d1b1c321'
        if not blob_path(store, digest).exists():
            self.skipTest('Retained source store unavailable')
        material, associations = source_material([digest], store)
        # Independently viewed physical pages 26–27: CONSOLE / FILIPPO spans
        # the printed folios 17–18 with sample 1669920 in the preceding row.
        scopes = [dict(table_ref=ref, first_row=row, last_row=row,
                       columns=[dict(role='addressee', column=11)],
                       direction_ids=[], meaning='', support=[])
                  for ref, row in [('S0P26T1', 10), ('S0P27T1', 1)]]
        response = {'reading': dict(target_scopes=scopes, prose_positions=[], image_positions=[])}
        reading = MeasureReading(response, material, associations)
        target, = reading.targets()
        self.assertEqual(target['reference'], '1669920')
        self.assertEqual(target['addressee_text'].split(), ['CONSOLE', 'FILIPPO'])
        self.assertEqual(target['occurrence'], 'S0P26T1R10')
        owner = material['tables']['S0P26T1']['rows'][9]['association']
        self.assertIs(target['association'], owner)
        self.assertIs(target['fields']['report_reference'], owner['fields']['report_reference'])
        self.assertEqual(target['fields']['host']['text'].split(), ['Vite', 'europea', '(Vitis', 'L.)'])
        with self.assertRaisesRegex(ValueError, 'already supplies'):
            table_fields(material, 'S0P26T1', 10, {'plant_id': 10})
        with self.assertRaisesRegex(ValueError, 'already supplies this source column'):
            table_fields(material, 'S0P26T1', 10, {'addressee': 3})


if __name__ == '__main__':
    unittest.main()
