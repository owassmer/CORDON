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


def join(groups, reports, bindings=None, *, associations=()):
    readings = {r.sha256: r for r in reports}
    captures = {'https://publisher.example/' + digest + '.pdf': [{'sha256': digest}]
                for digest in readings}
    with patch('cordon_d.findings._captures', return_value=captures), \
         patch('cordon_d.findings.load_relations', side_effect=lambda store, digest, **kw: readings[digest].relations), \
         patch('cordon_d.findings.report', side_effect=lambda digest, store, **kw: readings[digest]):
        return list(findings(groups, Path('reports'), Path('store'), extraction_version='version',
                    known_through=datetime(2026, 1, 1, tzinfo=timezone.utc), report_bindings=bindings,
                    association_readings=associations))


def host_population():
    """Two distinct specimens, including a negative; no common-name alias is assumed."""
    first = target(host='Faggio')
    second = target('public-two', 'act:p12:r2', host='Faggio', latitude='40.87349595')
    reading = report(host='Fagus sylvatica')
    other = report(reference='client-two', host='Fagus sylvatica', latitude='40.87349595').rows[0]
    other = replace(other, locator='p2/table/r2', cells=tuple(
        dict(c, locator=c['locator'].replace('/r1/', '/r2/')) for c in other.cells))
    reading = replace(reading, rows=(reading.rows[0], other))
    citation = reference('report-one')
    citation['documents'][0]['host_population'] = dict(scope='whole-report',
        host_fragments=[dict(line_ref='act:host-words', first_word=0, end_word=1)],
        support=[dict(source='act', page=2, locator='connecting clause',
                      quote='The cited report describes the entire Faggio population.')])
    owner = measure([first, second], [citation])
    owner.material = dict(tables={}, lines={'act:host-words': dict(source='act', page=2,
        words=['Faggio'], bbox=(0, 0, 10, 10))})
    return owner, reading, [observation(), observation('public-two')]


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

    def test_whole_population_relationship_preserves_unequal_labels_and_negative_result(self):
        owner, reading, groups = host_population()
        original = deepcopy(reading)
        bindings = population(owner, [reading])
        joined = join(groups, [reading], bindings)
        self.assertEqual([f['status'] for f in joined], ['matched', 'matched'])
        for finding in joined:
            match, = finding['matches']
            self.assertEqual(set(match['host_comparisons']), {'unresolved label equivalence'})
            self.assertEqual(match['row'].results[0].kind, 'not-detected')
            self.assertEqual(match['comparisons'][0]['verdict'], 'disagree')
            self.assertFalse(finding['limitations'])
        outputs = measure_findings(owner, report_population=bindings, findings=joined,
                                   report_rows=report_rows([reading], joined))
        self.assertEqual([o['status'] for o in outputs], ['matched', 'matched'])
        for output in outputs:
            candidate, = output['matches']
            self.assertEqual(candidate['host_relation'], 'unresolved label equivalence')
            self.assertIs(candidate['population_correspondence'],
                          candidate['match']['population_correspondence'])
        self.assertEqual(reading, original)
        self.assertEqual([t['fields']['host']['text'] for t in owner.prescribed_targets()],
                         ['Faggio', 'Faggio'])
        # An independently established literal identifier keeps its stronger basis.
        row = reading.rows[0]
        row = replace(row, reference='public-one', cells=tuple(
            dict(c, text='public-one') if c['role'] == 'identifier' else c for c in row.cells))
        reading = replace(reading, rows=(row, reading.rows[1]))
        joined = join(groups, [reading], population(owner, [reading]))
        self.assertEqual([f['status'] for f in joined], ['matched', 'matched'])
        self.assertIn('literal identifier equality', joined[0]['matches'][0]['identity_basis'])

    def test_equal_counts_and_unique_coordinates_do_not_create_an_unread_population_claim(self):
        owner, reading, groups = host_population()
        del owner.values['references'][0]['documents'][0]['host_population']
        joined = join(groups, [reading], population(owner, [reading]))
        self.assertTrue(all(not f['matches'] for f in joined))
        self.assertTrue(all(f['links'][0]['candidates'][0]['host_comparisons']
                           == ['unresolved label equivalence'] for f in joined))

    def test_subset_and_unread_image_claim_cannot_expand_to_whole_report(self):
        for scope, fragments in [('selected-occurrences', True), ('unresolved', True),
                                 ('whole-report', False)]:
            with self.subTest(scope=scope, fragments=fragments):
                owner, reading, groups = host_population()
                claim = owner.values['references'][0]['documents'][0]['host_population']
                claim['scope'] = scope
                if not fragments:
                    claim['host_fragments'] = []
                bindings = population(owner, [reading])
                joined = join(groups, [reading], bindings)
                self.assertTrue(all(not f['matches'] for f in joined))
                self.assertTrue(joined[0]['links'][0]['population_correspondence']['causes'])
                outputs = measure_findings(owner, report_population=bindings, findings=joined,
                                           report_rows=report_rows([reading], joined))
                for output in outputs:
                    candidate, = output['candidates']
                    self.assertIs(candidate['population_correspondence'],
                                  candidate['match']['population_correspondence'])
                    self.assertTrue(set(candidate['population_correspondence']['causes'])
                                    <= set(output['causes']))

    def test_extra_unmapped_negative_and_omitted_observation_prevent_population_closure(self):
        for extra_row in (False, True):
            with self.subTest(extra_row=extra_row):
                owner, reading, groups = host_population()
                if extra_row:
                    extra = replace(reading.rows[1], locator='p2/table/extra')
                    reading = replace(reading, rows=(*reading.rows, extra))
                else:
                    groups = groups[:1]
                joined = join(groups, [reading], population(owner, [reading]))
                self.assertTrue(all(not f['matches'] for f in joined))
                self.assertIn('every report record', ' '.join(
                    joined[0]['links'][0]['population_correspondence']['causes']))

    def test_mixed_unread_and_conflicting_host_populations_remain_unresolved(self):
        for failure in ('report-host', 'target-host', 'report-field', 'target-field', 'claims'):
            with self.subTest(failure=failure):
                owner, reading, groups = host_population()
                if failure.startswith('report'):
                    row = reading.rows[1]
                    cells = tuple(dict(c, **({'text': 'Quercus robur'} if failure == 'report-host'
                                            else {'reading_issues': ['field unread']}))
                                  if c['role'] == 'host' else c for c in row.cells)
                    reading = replace(reading, rows=(reading.rows[0], replace(row, cells=cells)))
                elif failure.startswith('target'):
                    field = owner.prescribed_targets()[1]['fields']['host']
                    field.update({'text': 'Quercia'} if failure == 'target-host'
                                 else {'role_cause': 'host qualification unresolved'})
                else:
                    other = deepcopy(owner.values['references'][0])
                    other['documents'][0]['host_population']['host_fragments'][0]['line_ref'] = 'other-host'
                    owner.material['lines']['other-host'] = dict(source='act', page=2,
                        words=['Quercia'], bbox=(0, 10, 10, 20))
                    owner.values['references'].append(other)
                joined = join(groups, [reading], population(owner, [reading]))
                self.assertTrue(all(not f['matches'] for f in joined))

    def test_pre_host_competitors_dates_and_reading_limits_cannot_be_overridden(self):
        for failure in ('coordinates', 'same-count-wrong-coordinate', 'rival-observation',
                        'assembly', 'sampling-date', 'measure-coverage'):
            with self.subTest(failure=failure):
                owner, reading, groups = host_population()
                if failure in {'coordinates', 'same-count-wrong-coordinate'}:
                    value = '40.86349595' if failure == 'coordinates' else '42.00000000'
                    row = reading.rows[1]
                    row = replace(row, cells=tuple(dict(c, text=value) if c['role'] == 'latitude'
                                                   else c for c in row.cells))
                    reading = replace(reading, rows=(reading.rows[0], row))
                elif failure == 'rival-observation':
                    rival = observation()
                    rival.identity = ('distinct-observation', '2024-09-29')
                    groups.append(rival)
                elif failure == 'assembly':
                    reading = replace(reading, assembly_complete=False)
                elif failure == 'sampling-date':
                    groups[1].day = date(2024, 9, 30)
                else:
                    owner.values['issues'] = [dict(source='act', page=None, aspect='coverage',
                                                  detail='A target annex is unread')]
                joined = join(groups, [reading], population(owner, [reading]))
                self.assertTrue(all(not f['matches'] for f in joined))

    def test_population_claim_is_not_inherited_by_replacement_or_another_measure(self):
        owner, old, groups = host_population()
        new = replace(old, sha256='report-two', relations=relationship('472/24', '20/10/2024',
            previous=old.relations['identity']).relations)
        bindings = population(owner, [old, new])
        self.assertNotIn('host_populations', bindings['report-two'])
        self.assertTrue(all(not f['matches'] for f in join(groups, [old, new], bindings)))

        bindings = population(owner, [old])
        joined = join(groups, [old], bindings)
        other = deepcopy(bindings)
        other['report-one']['request_sha256'] = 'another-retained-reading'
        outputs = measure_findings(owner, report_population=other, findings=joined,
                                   report_rows=report_rows([old], joined))
        self.assertTrue(all(not o['matches'] for o in outputs))

    def test_scoped_assertion_cannot_waive_another_associations_host_disagreement(self):
        owner, reading, groups = host_population()
        association = deepcopy(owner.prescribed_targets()[0]['association'])
        association['fields']['report_reference']['text'] = '471/24 Laboratory A'
        association['fields']['host']['text'] = 'Quercia'
        other_source = SimpleNamespace(rows=[association], issues=[], scope={})
        joined = join(groups, [reading], population(owner, [reading]), associations=[other_source])
        self.assertTrue(all(not f['matches'] for f in joined))
        self.assertIn('another source association host', ' '.join(
            joined[0]['links'][0]['population_correspondence']['causes']))

    def test_unrelated_context_and_independently_bound_target_issues_do_not_spill(self):
        owner, reading, groups = host_population()
        other = report('report-two', number='999/24', reference='unrelated-client')
        position = target('unrelated-target', 'act:p15:r1', number='999/24', host='Quercia')
        position['association']['page'] = 15
        original_targets = owner.prescribed_targets()
        owner.prescribed_targets = lambda: (*original_targets, position)
        owner.values['references'].append(reference('report-two'))
        owner.values['issues'] = [dict(source='unrelated-context', page=None, aspect='coverage'),
                                 dict(source='act', page=15, aspect='targets')]
        bindings = population(owner, [reading, other])
        self.assertEqual(bindings['report-one']['measure_population_issues'], ())
        self.assertTrue(all(f['status'] == 'matched' for f in join(groups, [reading, other], bindings)))
        owner.values['issues'].append(dict(source='act', page=16, aspect='targets'))
        joined = join(groups, [reading, other], population(owner, [reading, other]))
        self.assertTrue(all(not f['matches'] for f in joined))
        self.assertIn('unresolved issues', ' '.join(
            joined[0]['links'][0]['population_correspondence']['causes']))


if __name__ == '__main__':
    unittest.main()
