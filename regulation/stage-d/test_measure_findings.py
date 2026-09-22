"""Discriminating checks for the measure-to-existing-finding bridge."""
from datetime import date
from dataclasses import replace
from types import SimpleNamespace
import unittest

from cordon_d.measure_findings import measure_findings
from cordon_d.measures import MeasureReading
from cordon_d.reports import Row, Result


def target(reference='A', *, occurrence='position:1', **values):
    fields = dict(host='Olivo', latitude='40,76160935', longitude='17,29996696')
    fields.update(values)
    return dict(reference=reference, occurrence=occurrence,
                fields={role: {'text': text} for role, text in fields.items()})


def measure(*targets, identity='act-one'):
    return SimpleNamespace(identity=identity, prescribed_targets=lambda: targets)


def finding(reference='A', digest='report-one', *, day=date(2021, 10, 21),
            locator='p2/t1/r1', status='matched', **values):
    fields = dict(identifier=reference, host='Olivo', latitude='40,76160935',
                  longitude='17,29996696')
    fields.update(values)
    row = Row(locator, 2, reference, None, (),
              tuple(dict(role=role, text=text) for role, text in fields.items()),
              (Result(locator + '/result', ('Esito',), 'PCR', 'Xylella fastidiosa',
                      'Positivo', 'positive', None, ()),),
              ({'role': 'note', 'text': 'The cover and table disagree on municipality.'},))
    observation = SimpleNamespace(reference=reference,
                                  identity=('observation', reference, day.isoformat()))
    match = dict(key=(digest, locator), row=row, reading_complete=status == 'matched',
                 temporal='agrees')
    reading_issues = ({'cause': 'Cover/table municipality disagreement'},)
    joined = dict(observation=observation, status=status, matches=[match],
                  links=[dict(sha256=digest, candidates=[match], reading_issues=reading_issues)],
                  ambiguities=[])
    reverse = dict(sha256=digest, row=row, observations=[observation.identity],
                   reading_issues=reading_issues)
    return joined, reverse


def population(*digests):
    return {digest: dict(cause=None, references=['source-supported reference'],
                         report_identity={'number': digest}) for digest in digests}


def report_reading(digest, number, *, corrections=()):
    return SimpleNamespace(sha256=digest, issues=(), relations=dict(
        identity=dict(issuer='IAMB', issuer_labels=[], number=number,
                      date='2021-11-02', protocol=None),
        reading_complete=True, corrections=list(corrections)))


def native_target(reference='A', *, occurrence='position:1', number='18b'):
    position = target(reference, occurrence=occurrence)
    position['association'] = dict(fields=dict(position['fields'],
        report_reference={'text': 'IAMB ' + number}, report_date={'text': '02/11/2021'}))
    return position


def owned_population(targets, readings, references=()):
    owner = SimpleNamespace(prescribed_targets=lambda: targets,
                            values={'references': references}, response={})
    return MeasureReading.report_population(owner, readings)


class MeasureFindings(unittest.TestCase):
    def test_native_report_scope_survives_without_document_selections(self):
        first = native_target()
        second = native_target(occurrence='position:2', number='20')
        readings = [report_reading('report-one', '18b'), report_reading('report-two', '20')]
        # A compound recital selection cannot override either row's native report.
        refs = [dict(relationship='laboratory-evidence', documents=[{'source': 'report-two'}])]
        bound = owned_population((first, second), readings, refs)
        self.assertEqual(bound['report-one']['target_occurrences'], ('position:1',))
        self.assertEqual(bound['report-two']['target_occurrences'], ('position:2',))
        self.assertIs(bound['report-one']['references'][0]['association'], first['association'])
        self.assertEqual(bound['report-two']['references'][1]['target_occurrences'], ())
        self.assertEqual(set(owned_population((first, second), readings)), set(bound))

        joined, reverse = finding(digest='report-two')
        outputs = measure_findings(measure(first, second), report_population=bound,
                                   findings=[joined], report_rows=[reverse])
        self.assertEqual(outputs[0]['status'], 'unresolved')
        self.assertEqual(len(outputs[0]['candidates']), 1)
        self.assertIn('source report binding does not apply to this prescribed position',
                      outputs[0]['causes'])
        self.assertEqual(outputs[1]['status'], 'matched')

    def test_native_scope_follows_only_owned_whole_report_replacements(self):
        native = native_target()
        prose = dict(target('B', occurrence='prose:1'), association=None)
        old = report_reading('report-one', '18b')
        correction = dict(predecessor=old.relations['identity'], effect='replaces',
                          scope='whole report', changed_columns=[], support=[{'page': 1}])
        new = report_reading('report-two', '20', corrections=[correction])
        refs = [dict(relationship='laboratory-evidence', documents=[{'source': 'report-two'}])]
        bound = owned_population((native, prose), [old, new], refs)
        self.assertEqual(bound['report-one']['target_occurrences'], ('position:1',))
        self.assertEqual(bound['report-two']['target_occurrences'], ('position:1', 'prose:1'))
        native_binding, selection_binding = bound['report-two']['references']
        self.assertIs(native_binding['association'], native['association'])
        self.assertEqual(native_binding['replacement_chain'][0]['successor'], 'report-two')
        self.assertEqual(selection_binding['target_occurrences'], ('prose:1',))
        correction['effect'] = 'amends'
        self.assertEqual(owned_population((native, prose), [old, new], refs)
                         ['report-two']['target_occurrences'], ('prose:1',))

    def test_no_native_reference_cannot_become_a_global_identifier_match(self):
        native = native_target(number='missing')
        prose = dict(target('B', occurrence='prose:1'), association=None)
        readings = [report_reading('report-one', '18b')]
        refs = [dict(relationship='laboratory-evidence', documents=[{'source': 'report-one'}])]
        bound = owned_population((native, prose), readings, refs)
        self.assertEqual(bound['report-one']['target_occurrences'], ('prose:1',))
        self.assertEqual(owned_population((native, prose), readings), {})

    def test_source_bound_match_retains_entire_existing_evidence(self):
        position = target()
        joined, reverse = finding()
        bound = population('report-one')
        output, = measure_findings(measure(position), report_population=bound,
                                   findings=[joined], report_rows=[reverse])
        self.assertEqual(output['status'], 'matched')
        self.assertIs(output['target'], position)
        candidate, = output['matches']
        self.assertIs(candidate['finding'], joined)
        self.assertIs(candidate['match'], joined['matches'][0])
        self.assertIs(candidate['report_binding'], bound['report-one'])
        self.assertIs(candidate['reverse_rows'][0], reverse)
        self.assertEqual(candidate['coordinate_relation'], 'agrees at published decimal precision')
        self.assertEqual(candidate['host_relation'], 'agrees on printed host')
        self.assertTrue(candidate['match']['row'].facts)
        self.assertTrue(candidate['reverse_rows'][0]['reading_issues'])

    def test_identical_identifier_and_place_cannot_escape_bound_report_population(self):
        joined, reverse = finding()
        output, = measure_findings(measure(target()), report_population=population('another-report'),
                                   findings=[joined], report_rows=[reverse])
        self.assertEqual(output['status'], 'unresolved')
        self.assertFalse(output['candidates'])
        self.assertFalse(output['matches'])

    def test_unknown_host_equivalence_and_coordinate_conflicts_do_not_attach(self):
        for fields, reason in [({'host': 'Prunus dulcis'}, 'host unresolved label equivalence'),
                               ({'longitude': '18,29996696'}, 'coordinates conflicts'),
                               ({'latitude': None}, 'coordinates unresolved')]:
            with self.subTest(fields=fields):
                joined, reverse = finding(**fields)
                output, = measure_findings(measure(target()),
                    report_population=population('report-one'), findings=[joined], report_rows=[reverse])
                self.assertEqual(output['status'], 'unresolved')
                self.assertFalse(output['matches'])
                self.assertEqual(len(output['candidates']), 1)
                self.assertTrue(any(reason in cause for cause in output['causes']))

    def test_unresolved_binding_and_native_field_reading_are_not_source_absence(self):
        joined, reverse = finding()
        for binding_cause, field_issue in [('report identity reading incomplete', None),
                                          (None, 'Native header unavailable')]:
            with self.subTest(binding_cause=binding_cause, field_issue=field_issue):
                bound = population('report-one')
                bound['report-one']['cause'] = binding_cause
                position = target()
                if field_issue:
                    position['native_field_issue'] = field_issue
                output, = measure_findings(measure(position), report_population=bound,
                                           findings=[joined], report_rows=[reverse])
                self.assertFalse(output['matches'])
                self.assertEqual(len(output['candidates']), 1)
                self.assertIn(binding_cause or field_issue, output['causes'])

    def test_unresolved_ordinary_candidates_survive_without_becoming_matches(self):
        joined, reverse = finding()
        joined['matches'] = []
        joined['status'] = 'observation has several eligible source-row occurrences'
        output, = measure_findings(measure(target()), report_population=population('report-one'),
                                   findings=[joined], report_rows=[reverse])
        self.assertFalse(output['matches'])
        self.assertEqual(len(output['candidates']), 1)
        self.assertIs(output['candidates'][0]['finding'], joined)

    def test_forward_and_reverse_ambiguities_are_distinct(self):
        first, reverse_first = finding()
        second, reverse_second = finding(digest='report-two', day=date(2021, 10, 22))
        output, = measure_findings(measure(target()),
            report_population=population('report-one', 'report-two'),
            findings=[first, second], report_rows=[reverse_first, reverse_second])
        self.assertFalse(output['matches'])
        self.assertEqual(len(output['candidates']), 2)
        self.assertIn('the prescribed position has several eligible findings', output['causes'])
        reverse_first['observations'].append(second['observation'].identity)
        output, = measure_findings(measure(target()), report_population=population('report-one'),
                                   findings=[first], report_rows=[reverse_first])
        self.assertFalse(output['matches'])
        self.assertIn('reverse report occurrence is not unique to this observation', output['causes'])

    def test_duplicate_target_positions_never_collapse_and_other_acts_stay_independent(self):
        joined, reverse = finding()
        position = target()
        kwargs = dict(report_population=population('report-one'), findings=[joined], report_rows=[reverse])
        outputs = measure_findings(measure(position, dict(position)), **kwargs)
        self.assertEqual(len(outputs), 2)
        self.assertTrue(all(not output['matches'] for output in outputs))
        self.assertTrue(all('the finding has several prescribed positions in this act'
                            in output['causes'] for output in outputs))
        for identity in ('initial-act', 'correcting-act'):
            output, = measure_findings(measure(position, identity=identity), **kwargs)
            self.assertEqual(output['status'], 'matched')

    def test_ambiguous_position_remains_a_competitor_for_another_position(self):
        first, reverse_first = finding()
        second, reverse_second = finding(reference='B', digest='report-two')
        match = second['matches'][0]
        # One printed row can carry more than one source identifier. Both remain
        # candidate evidence; an unresolved position must not release its rival.
        row = replace(match['row'], cells=match['row'].cells + ({'role': 'identifier', 'text': 'A'},))
        match['row'] = row
        reverse_second['row'] = row
        outputs = measure_findings(measure(target('A'), target('B', occurrence='position:2')),
            report_population=population('report-one', 'report-two'),
            findings=[first, second], report_rows=[reverse_first, reverse_second])
        self.assertFalse(outputs[0]['matches'])
        self.assertFalse(outputs[1]['matches'])
        self.assertIn('the finding has several prescribed positions in this act', outputs[1]['causes'])

    def test_existing_repeated_displays_stay_with_one_finding(self):
        joined, reverse = finding()
        duplicate, reverse_duplicate = finding(locator='p3/t1/r1')
        joined['matches'].extend(duplicate['matches'])
        joined['links'].extend(duplicate['links'])
        output, = measure_findings(measure(target()), report_population=population('report-one'),
                                   findings=[joined], report_rows=[reverse, reverse_duplicate])
        self.assertEqual(output['status'], 'matched')
        self.assertEqual(len(output['matches']), 2)
        self.assertTrue(all(candidate['finding'] is joined for candidate in output['matches']))

    def test_incomplete_reading_stays_provisional_and_absent_reverse_stays_unresolved(self):
        joined, reverse = finding(status='provisional-match')
        output, = measure_findings(measure(target()), report_population=population('report-one'),
                                   findings=[joined], report_rows=[reverse])
        self.assertEqual(output['status'], 'provisional-match')
        self.assertTrue(output['matches'])
        output, = measure_findings(measure(target()), report_population=population('report-one'),
                                   findings=[joined], report_rows=[])
        self.assertEqual(output['status'], 'unresolved')
        self.assertFalse(output['matches'])

    def test_actual_measure_selection_excludes_inactive_and_map_positions(self):
        reading = dict(
            identity=dict(authority='puglia-osservatorio', number='1', adopted='2021-11-09'),
            directions=[dict(id='removal', mode='ordered-now', work='removal')],
            parts=[dict(source='act', pages=[1, 2], role='target-table'),
                   dict(source='act', pages=[3], role='map')],
            target_scopes=[], prose_positions=[], image_positions=[])
        for page, reference, directions in [(1, 'A', ['removal']), (2, 'B', []), (3, 'C', ['removal'])]:
            reading['image_positions'].append(dict(
                image_ref=str(page), association_ref=None,
                fields=[dict(role='plant_id', transcription=reference)],
                direction_ids=directions, meaning='source position', support=[]))
        actual = MeasureReading({'reading': reading},
            dict(images={}, pages={str(page): dict(source='act', page=page) for page in (1, 2, 3)}), ())
        pairs = [finding(reference=ref, locator='p2/t1/' + ref) for ref in ('A', 'B', 'C')]
        self.assertEqual(len(tuple(actual.targets())), 3)
        outputs = measure_findings(actual, report_population=population('report-one'),
                                    findings=[pair[0] for pair in pairs], report_rows=[pair[1] for pair in pairs])
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0]['target']['reference'], 'A')
        self.assertEqual(outputs[0]['status'], 'matched')


if __name__ == '__main__':
    unittest.main()
