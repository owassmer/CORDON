"""Source-selected report context remains constrained by each native target row."""
from copy import deepcopy
from dataclasses import replace
from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from cordon_d.findings import findings, report_rows
from cordon_d.measure_findings import measure_findings
from cordon_d.measures import MeasureReading
from cordon_d.reports import LiteralDate, Report, Result, Row
from test_report_relations import reading as relationship


def target(reference='public-one', occurrence='act:p12:r1', *, number='471/2024',
           report_date='19/10/2024', **changes):
    fields = dict(plant_id=reference, report_reference=number, report_date=report_date,
                  host='Olivo', latitude='40,86349595', longitude='17,34850436')
    fields.update(changes)
    association = dict(source_sha256='act', page=12, table=1, row=1,
                       fields={role: {'text': text} for role, text in fields.items()})
    return dict(reference=reference, occurrence=occurrence, fields=association['fields'],
                association=association)


def report(digest='report-one', *, issuer='Laboratory A', number='471/24',
           issued='19/10/2024', reference='client-one', host='Olivo',
           latitude='40.86349595', complete=True):
    fields = dict(identifier=reference, host=host, latitude=latitude, longitude='17.34850436')
    row = Row('p2/table/r1', 2, reference, None,
        (LiteralDate('29/09/2024', date(2024, 9, 29), None),),
        tuple(dict(role=role, text=text, heading=[role], locator='p2/table/r1/' + role)
              for role, text in fields.items()),
        (Result('p2/table/r1/result', ('Esito',), 'PCR', 'Xylella fastidiosa',
                'Non rilevato', 'not-detected', None, ()),),
        ({'role': 'qualification', 'text': 'Source qualification retained.'},))
    return Report(digest, 'version', 2, (row,), (), (), frozenset({1, 2}),
                  relationship(number, issued, issuer=issuer).relations, complete)


def reference(*digests):
    return dict(relationship='laboratory-evidence', identity_literal='source recital',
        support=[dict(source='act', page=2, quote='stated issuing laboratory and report')],
        documents=[dict(source=digest, support=[
            dict(source='act', page=2, quote='stated issuing laboratory and report'),
            dict(source=digest, page=1, quote='report issuer, number and date')])
            for digest in digests])


def measure(targets, references=()):
    return SimpleNamespace(identity='act', prescribed_targets=lambda: tuple(targets),
                           values={'references': references}, response={})


def population(owner, reports):
    return MeasureReading.report_population(owner, reports)


def observation(reference='public-one', digest='report-one'):
    route = 'https://publisher.example/' + digest + '.pdf'
    member = SimpleNamespace(report_routes=(('report', route),), coordinates=None,
                             carried=(), result='published-positive', subspecies=None)
    return SimpleNamespace(reference=reference, identity=(reference, '2024-09-29'),
        day=date(2024, 9, 29), correlatable=True, report_routes=(route,), members=(member,))


def join(groups, reports, bindings=None):
    readings = {r.sha256: r for r in reports}
    captures = {'https://publisher.example/' + digest + '.pdf': [{'sha256': digest}]
                for digest in readings}
    with patch('cordon_d.findings._captures', return_value=captures), \
         patch('cordon_d.findings.load_relations', side_effect=lambda store, digest, **kw: readings[digest].relations), \
         patch('cordon_d.findings.report', side_effect=lambda digest, store, **kw: readings[digest]):
        return list(findings(groups, Path('reports'), Path('store'), extraction_version='version',
                    known_through=datetime(2026, 1, 1, tzinfo=timezone.utc), report_bindings=bindings))


class MeasureReportContext(unittest.TestCase):
    def test_explicit_selection_composes_bare_row_and_preserves_original_evidence(self):
        position, reading, citation = target(), report(), reference('report-one')
        original = deepcopy(position)
        owner = measure([position], [citation])
        self.assertEqual(population(measure([position]), [reading]), {})
        bindings = population(owner, [reading])
        binding = bindings['report-one']
        self.assertEqual(binding['target_occurrences'], (position['occurrence'],))
        support = binding['references'][-1]
        self.assertIs(support['association'], position['association'])
        self.assertIs(support['reference'], citation)
        self.assertIs(support['selection'], citation['documents'][0])
        self.assertEqual(position, original)

        group = observation()
        self.assertFalse(join([group], [reading])[0]['matches'])
        joined = join([group], [reading], bindings)
        match, = joined[0]['matches']
        self.assertIn('derived occurrence correspondence', match['identity_basis'])
        self.assertEqual(match['row'].identifiers, ('client-one',))
        self.assertEqual(joined[0]['observation'].reference, 'public-one')
        self.assertEqual(match['row'].results[0].kind, 'not-detected')
        self.assertEqual(match['comparisons'][0]['verdict'], 'disagree')
        self.assertIs(match['source_associations'][0]['fields'], position['association']['fields'])
        self.assertIs(match['source_associations'][0]['report_binding'], support)
        outputs = measure_findings(owner, report_population=bindings, findings=joined,
                                   report_rows=report_rows([reading], joined))
        self.assertEqual(outputs[0]['status'], 'matched')
        self.assertEqual(outputs[0]['matches'][0]['match']['row'].facts, reading.rows[0].facts)

    def test_context_never_overrides_the_complete_native_reference_or_date(self):
        reading = report()
        for number, day in [('472/2024', '19/10/2024'), ('471/2024', '20/10/2024'),
                            ('471/1924', '19/10/2024'), ('471/2024 Laboratory B', '19/10/2024'),
                            ('Rapporto di prova N. 471/2024', '19/10/2024'),
                            ('471/2024', ''), ('471/2024', None)]:
            with self.subTest(number=number, day=day):
                owner = measure([target(number=number, report_date=day)], [reference('report-one')])
                binding = population(owner, [reading])['report-one']
                self.assertEqual(binding['target_occurrences'], ())
                self.assertFalse(join([observation()], [reading], {'report-one': binding})[0]['matches'])
        short = target(number='471/24')
        full = report(number='471/2024')
        self.assertEqual(population(measure([short], [reference('report-one')]), [full])
                         ['report-one']['target_occurrences'], (short['occurrence'],))

    def test_ambiguous_context_does_not_disable_another_rows_explicit_reference(self):
        bare = target()
        explicit = target('public-two', 'act:p12:r2', number='471/24 Laboratory A')
        first, second = report(), report('report-two', issuer='Laboratory B')
        owner = measure([bare, explicit], [reference('report-one', 'report-two')])
        bindings = population(owner, [first, second])
        self.assertIsNone(bindings['report-one']['cause'])
        self.assertEqual(bindings['report-one']['target_occurrences'], (explicit['occurrence'],))
        self.assertEqual(bindings['report-two']['target_occurrences'], ())
        for binding in bindings.values():
            ambiguous, = [s for s in binding['references'] if s.get('cause')]
            self.assertEqual(ambiguous['target_occurrences'], (bare['occurrence'],))
            self.assertIn('several explicitly selected documents', ambiguous['cause'])
        joined = join([observation(), observation('public-two')], [first, second], bindings)
        self.assertFalse(joined[0]['matches'])
        self.assertIs(joined[0]['links'][0]['report_binding'], bindings['report-one'])
        self.assertEqual(joined[1]['status'], 'matched')
        self.assertEqual(joined[1]['matches'][0]['key'][0], 'report-one')

    def test_duplicate_citations_to_one_source_are_not_competing_documents(self):
        owner = measure([target()], [reference('report-one'), reference('report-one')])
        bindings = population(owner, [report()])
        self.assertEqual(bindings['report-one']['target_occurrences'], ('act:p12:r1',))
        self.assertEqual(len([s for s in bindings['report-one']['references']
                              if s.get('association')]), 2)
        self.assertEqual(join([observation()], [report()], bindings)[0]['status'], 'matched')

    def test_bound_context_cannot_escape_its_report_or_observation(self):
        first, second = report(), report('report-two')
        bindings = population(measure([target()], [reference('report-one')]), [first, second])
        for group in [observation(digest='report-two'), observation('another-public-id')]:
            with self.subTest(identity=group.identity, route=group.report_routes):
                self.assertFalse(join([group], [first, second], bindings)[0]['matches'])

    def test_reading_limit_host_and_coordinate_conflict_remain_effective(self):
        position = target()
        for reading in [report(host='Prunus dulcis'), report(latitude='40.8')]:
            with self.subTest(host=reading.rows[0].cells[1], latitude=reading.rows[0].cells[2]):
                bindings = population(measure([position], [reference('report-one')]), [reading])
                self.assertFalse(join([observation()], [reading], bindings)[0]['matches'])
        reading = report()
        cells = tuple(dict(c, role='other') if c['role'] == 'latitude' else c
                      for c in reading.rows[0].cells)
        unread = replace(reading, rows=(replace(reading.rows[0], cells=cells),))
        bindings = population(measure([position], [reference('report-one')]), [unread])
        self.assertFalse(join([observation()], [unread], bindings)[0]['matches'])
        incomplete = report(complete=False)
        bindings = population(measure([position], [reference('report-one')]), [incomplete])
        self.assertEqual(join([observation()], [incomplete], bindings)[0]['status'], 'provisional-match')

    def test_reverse_ambiguity_and_repeated_targets_cannot_become_links(self):
        reading = report()
        owner = measure([target(), target('public-two', 'act:p12:r2')], [reference('report-one')])
        bindings = population(owner, [reading])
        joined = join([observation(), observation('public-two')], [reading], bindings)
        self.assertTrue(all(not item['matches'] for item in joined))
        repeated = measure([target(), target(occurrence='act:p12:r2')], [reference('report-one')])
        bindings = population(repeated, [reading])
        joined = join([observation()], [reading], bindings)
        outputs = measure_findings(repeated, report_population=bindings, findings=joined,
                                   report_rows=report_rows([reading], joined))
        self.assertTrue(all(item['status'] == 'unresolved' for item in outputs))

    def test_resolved_replacement_preserves_context_scope_but_amendment_does_not_extend_it(self):
        old = report()
        new = report('report-two', number='472/24', issued='20/10/2024')
        new = replace(new, relations=relationship('472/24', '20/10/2024',
            previous=old.relations['identity']).relations)
        owner = measure([target()], [reference('report-one')])
        bindings = population(owner, [old, new])
        self.assertEqual(bindings['report-two']['target_occurrences'], ('act:p12:r1',))
        joined = join([observation()], [old, new], bindings)
        self.assertEqual({m['key'][0] for m in joined[0]['matches']}, {'report-two'})
        new.relations['corrections'][0]['effect'] = 'amends'
        self.assertNotIn('report-two', population(owner, [old, new]))


if __name__ == '__main__':
    unittest.main()
