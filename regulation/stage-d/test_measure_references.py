"""Supplied-document selection remains separate from laboratory row identity."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

import pymupdf
from jsonschema import Draft202012Validator, ValidationError

from cordon_d.measures import MeasureReading, SCHEMA, _validate_reading
from cordon_d.measure_sources import source_material
from cordon_d.store import put_bytes


class MeasureReferences(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.store = Path(self.directory.name)
        self.sources = []
        for text in ('Act cites two laboratory reports about Faggio', 'Laboratory report one',
                     'Laboratory report two'):
            with pymupdf.open() as document:
                page = document.new_page()
                page.insert_text((50, 50), text)
                self.sources.append(put_bytes(self.store, document.tobytes()))
        self.act, self.first, self.second = self.sources
        self.citation = dict(source=self.act, page=1, locator='report recital',
                             quote='Act cites two laboratory reports')
        self.reference = dict(identity_literal='two cited reports',
            relationship='laboratory-evidence', affected_payload='stated findings',
            support=[self.citation], documents=[
                dict(source=digest, support=[self.citation, dict(source=digest, page=1,
                     locator='report identity', quote=f'Laboratory report {name}')])
                for digest, name in ((self.first, 'one'), (self.second, 'two'))])
        self.reading = dict(identity=dict(adopted=None), events=[], issues=[], directions=[],
                            target_scopes=[], prose_positions=[], image_positions=[],
                            parts=[], references=[self.reference])
        self.material = dict(tables={}, lines={}, images={}, pages={})

    def validate(self, reading):
        _validate_reading(reading, self.sources, self.store, self.material)

    def test_compound_reference_requires_both_sides_of_each_document_link(self):
        self.validate(self.reading)
        for keep in (0, 1):
            with self.subTest(only_support_side=keep):
                reading = deepcopy(self.reading)
                selected = reading['references'][0]['documents'][0]
                selected['support'] = [selected['support'][keep]]
                with self.assertRaisesRegex(ValueError, 'both citing and referenced'):
                    self.validate(reading)

    def test_unsupplied_self_and_duplicate_document_selections_are_refused(self):
        for selected in ('f' * 64, self.act, self.second):
            with self.subTest(selected=selected):
                reading = deepcopy(self.reading)
                reading['references'][0]['documents'][0]['source'] = selected
                with self.assertRaises(ValueError):
                    self.validate(reading)

    def test_old_unbound_reference_is_not_resolved_by_its_prose(self):
        reading = deepcopy(self.reading)
        del reading['references'][0]['documents']
        self.validate(reading)
        measure = MeasureReading(dict(reading=reading), self.material, ())
        self.assertEqual(measure.report_population([]), {})

    def test_report_identity_and_limitations_remain_with_existing_owner(self):
        identity = dict(issuer='Laboratory', number='one', date='1/2/2025')
        relations = dict(identity=identity, reading_complete=True, corrections=[])
        issues = ({'cause': 'Cover and result table disagree'},)
        first = SimpleNamespace(sha256=self.first, relations=relations, issues=issues)
        measure = MeasureReading(dict(reading=self.reading), self.material, ())
        population = measure.report_population([first])
        self.assertEqual(set(population), {self.first, self.second})
        self.assertIs(population[self.first]['report_identity'], identity)
        self.assertIs(population[self.first]['relationship_reading'], relations)
        self.assertIs(population[self.first]['reading_issues'], issues)
        self.assertIsNone(population[self.first]['cause'])
        self.assertIn('no supplied ordinary reading', population[self.second]['cause'])
        with self.assertRaisesRegex(ValueError, 'one ordinary report reading per source'):
            measure.report_population([first, first])
        first.relations = dict(relations, reading_complete=False)
        self.assertIn('incomplete', measure.report_population([first])[self.first]['cause'])

    def test_only_owned_resolved_replacements_extend_the_cited_population(self):
        old_identity = dict(issuer='Laboratory', number='one', date='1/2/2025',
                            issuer_labels=[], protocol=None)
        new_identity = dict(old_identity, number='two', date='2/2/2025')
        first = SimpleNamespace(sha256=self.first, issues=(), relations=dict(
            identity=old_identity, reading_complete=True, corrections=[]))
        correction = dict(predecessor=old_identity, effect='replaces', scope='replaces report one',
                          changed_columns=[], support=[{'page': 1, 'text': 'replaces report one'}])
        second = SimpleNamespace(sha256=self.second, issues=(), relations=dict(
            identity=new_identity, reading_complete=True, corrections=[correction]))
        reading = deepcopy(self.reading)
        reading['references'][0]['documents'] = reading['references'][0]['documents'][:1]
        measure = MeasureReading(dict(reading=reading), self.material, ())
        population = measure.report_population([first, second])
        self.assertEqual(set(population), {self.first, self.second})
        binding, = population[self.second]['references']
        self.assertEqual(binding['selection']['source'], self.first)
        self.assertEqual(binding['replacement_chain'][0]['successor'], self.second)
        self.assertTrue(population[self.first]['cause'])
        self.assertIsNone(population[self.second]['cause'])
        correction['effect'] = 'amends'
        self.assertEqual(set(measure.report_population([first, second])), {self.first})
        second.relations['corrections'] = []
        self.assertEqual(set(measure.report_population([first, second])), {self.first})

    def test_population_schema_uses_real_native_host_fragments_and_citing_support(self):
        self.material, _ = source_material(self.sources, self.store)
        line_ref, line = next((ref, value) for ref, value in self.material['lines'].items()
                              if value['source'] == self.act and 'Faggio' in value['words'])
        start = line['words'].index('Faggio')
        claim = dict(scope='whole-report', host_fragments=[dict(
            line_ref=line_ref, first_word=start, end_word=start + 1)], support=[dict(
                source=self.act, page=1, locator='complete connecting clause',
                quote='Act cites two laboratory reports about Faggio')])
        reading = deepcopy(self.reading)
        reading['identity'] = dict(issuer='Osservatorio', authority='puglia-osservatorio',
            number='1', adopted='2025-01-01', title='Measure', support=[self.citation])
        reading['references'][0]['acts'] = []
        for selected in reading['references'][0]['documents']:
            selected['host_population'] = None
        selected = reading['references'][0]['documents'][0]
        selected['host_population'] = claim
        Draft202012Validator(SCHEMA).validate(reading)
        self.validate(reading)
        owner = MeasureReading(dict(reading=reading), self.material, ())
        host, = owner.report_population([])[self.first]['host_populations']
        self.assertEqual(host['host']['text'], 'Faggio')
        self.assertEqual(host['host']['fragments'][0]['source'], self.act)
        self.assertEqual(host['host']['fragments'][0]['locator'],
                         f'{line_ref}/words:{start}:{start + 1}')
        self.assertIs(host['claim'], claim)

        for failure in ('other-source', 'no-citing-clause', 'bad-span', 'authored-value'):
            with self.subTest(failure=failure):
                broken = deepcopy(reading)
                value = broken['references'][0]['documents'][0]['host_population']
                if failure == 'other-source':
                    other_ref = next(ref for ref, line in self.material['lines'].items()
                                     if line['source'] == self.first)
                    value['host_fragments'] = [dict(line_ref=other_ref, first_word=0, end_word=1)]
                elif failure == 'no-citing-clause':
                    value['support'] = [dict(source=self.first, page=1,
                                            locator='report', quote='Laboratory report one')]
                elif failure == 'bad-span':
                    value['host_fragments'][0]['end_word'] = 10000
                else:
                    value['host_fragments'][0]['text'] = 'invented taxonomic equivalent'
                    with self.assertRaises(ValidationError):
                        Draft202012Validator(SCHEMA).validate(broken)
                    continue
                with self.assertRaises(ValueError):
                    self.validate(broken)


if __name__ == '__main__':
    unittest.main()
