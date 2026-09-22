"""Adapter mechanics; synthetic source components do not qualify an actual clause."""
import contextlib
from copy import deepcopy
from datetime import date, datetime
import io
import json
from pathlib import Path
import unittest
from zoneinfo import ZoneInfo

from cordon_c import MissingInput, Snapshot, evaluate
from cordon_c.bindings import noncommencement_facts
from cordon_c.quantities import clock_boundary
from cordon_c.temporal import WorkingCalendar
from cordon_d.prescription_terms import CLOCK, measure_prescribed_term
from test_prescription_candidate import verified_candidate_snapshot


class ComponentInterface:
    """The adapter consumes this owner interface, not a second source schema."""
    def __init__(self, result):
        self.result = result

    def commencement_components(self, direction_id):
        if direction_id != self.result['direction']['id']:
            raise ValueError('Select one existing direction')
        return self.result


class PrescriptionTerms(unittest.TestCase):
    at = date(2026, 9, 8)
    zone = ZoneInfo('Europe/Rome')

    @classmethod
    def setUpClass(cls):
        with contextlib.redirect_stdout(io.StringIO()):
            cls.snapshot = verified_candidate_snapshot()

    def setUp(self):
        self.component = dict(trigger='noncommencement', performance='concrete-commencement',
            required_actor='the notified owners', commencement_work='the prescribed infected plants',
            commencement_direction_ids=['initial-work'], commitment='will-direct',
            period=dict(magnitude='3', unit='days', bound='within-maximum',
                        literal='within a maximum of three days', anchor='notification',
                        anchor_statement='of completed notification'),
            support=[dict(source='a' * 64, page=7, locator='operative point 6',
                          quote='Source clause fixture only.')])
        self.direction = dict(id='unregistered-direction', mode='conditional-order', work='removal',
                              scope='A distinct coercive population', recipients='the executing body')
        self.reading = dict(direction=self.direction, components=(self.component,), cause=None,
                            readings=({'request_sha256': 'b' * 64, 'components': [self.component]},),
                            issues=())
        self.measure = ComponentInterface(self.reading)
        self.context = dict(targets=({'occurrence': 'source-owned-target'},),
                            recipient_evidence=(), operative_relationship_evidence=())
        self.arguments = dict(document='explicit-operative-document', recipient='explicit-recipient',
                              commencement_work='explicit-work-context', source_context=self.context)
        self.calendar = WorkingCalendar(date(2026, 1, 1), date(2027, 1, 1), frozenset(), frozenset({5, 6}))

    def bind(self, **changes):
        return measure_prescribed_term(self.snapshot, self.at, self.measure,
            'unregistered-direction', 0, **(self.arguments | changes))

    def test_unseen_term_retains_source_and_explicit_context_without_a_facts(self):
        result = self.bind()
        self.assertEqual((str(result['term'].magnitude), result['term'].unit), ('3', 'calendar_days'))
        self.assertEqual(result['term'].document, 'explicit-operative-document')
        self.assertIs(result['direction'], self.direction)
        self.assertIs(result['component'], self.component)
        self.assertIs(result['source_context'], self.context)
        self.assertIs(result['readings'], self.reading['readings'])
        self.assertIn('operative point 6', result['term'].clause)
        self.assertEqual(set(result), {'term', 'quantity', 'direction', 'component', 'readings', 'issues', 'source_context'})

    def test_boundary_and_temporal_facts_do_not_establish_remaining_a_predicates(self):
        term = self.bind()['term']
        anchor = datetime(2026, 9, 4, 12, tzinfo=self.zone)
        boundary = clock_boundary(self.snapshot, CLOCK, self.at, anchor,
                                  prescribed_term=term, zone=self.zone, calendar=self.calendar)
        self.assertEqual(boundary, datetime(2026, 9, 8, tzinfo=self.zone))
        facts = noncommencement_facts(self.snapshot, CLOCK, self.at, prescribed_term=term,
            notification=anchor, evaluated_at=datetime(2026, 9, 9, tzinfo=self.zone),
            qualifying_commencements={}, commencement_records_complete=True,
            zone=self.zone, calendar=self.calendar)
        result = evaluate(self.snapshot, 'SOURCE-CLAUSE:notification-noncommencement-direction', self.at, facts)
        self.assertIsNone(result.truth)
        self.assertIsNone(result.effect)
        self.assertTrue(any('legally sufficient notification' in need for need in result.needs))

    def test_different_source_forms_cannot_borrow_the_notification_clock(self):
        for owner, field, value in [('component', 'trigger', 'other'),
                                    ('component', 'performance', 'completion'),
                                    ('component', 'commitment', 'may-direct'),
                                    ('period', 'anchor', 'other'),
                                    ('period', 'bound', 'other')]:
            with self.subTest(field=field):
                target = self.component if owner == 'component' else self.component['period']
                old = target[field]
                target[field] = value
                with self.assertRaisesRegex(ValueError, 'outside this'):
                    self.bind()
                target[field] = old

    def test_missing_absent_and_conflicting_readings_are_not_a_zero_day_term(self):
        for components, cause in [(None, 'not-recovered: old contract'),
                                  (None, 'conflict: selected readings disagree'), ((), None)]:
            with self.subTest(cause=cause):
                self.reading.update(components=components, cause=cause)
                with self.assertRaises(MissingInput):
                    self.bind()

    def test_unresolved_or_missing_period_components_retain_their_causes(self):
        original = deepcopy(self.component['period'])
        for field, value in [('magnitude', None), ('unit', 'unresolved'), ('bound', 'unresolved')]:
            self.component['period'] = original | {field: value}
            with self.assertRaises(MissingInput):
                self.bind()
        self.component['period'] = deepcopy(original)
        self.component['period'].pop('bound')
        with self.assertRaisesRegex(MissingInput, 'bound is unavailable'):
            self.bind()
        self.component['period'] = None
        with self.assertRaisesRegex(MissingInput, 'Source-stated commencement period'):
            self.bind()

    def test_original_or_corrected_document_relationship_is_never_inferred(self):
        for field, message in [('document', 'operative prescription document relationship'),
                               ('recipient', 'recipient context'),
                               ('commencement_work', 'commencement-work context')]:
            with self.subTest(field=field):
                with self.assertRaisesRegex(MissingInput, message):
                    self.bind(**{field: None})

    def test_source_unit_selects_counting_family_without_caller_calendar_choice(self):
        for source, unit in [('days', 'calendar_days'), ('working-days', 'working_days'),
                              ('hours', 'hours'), ('months', 'months'), ('years', 'years')]:
            self.component['period']['unit'] = source
            self.assertEqual(self.bind()['term'].unit, unit)
        self.component['period']['unit'] = 'other'
        with self.assertRaisesRegex(ValueError, 'no supported counting convention'):
            self.bind()

    def test_unsupported_quantities_and_component_selection_remain_rejected(self):
        for magnitude in ('0', '-1', '1.5', 'Infinity'):
            self.component['period']['magnitude'] = magnitude
            with self.assertRaises(ValueError):
                self.bind()
        for index in (-1, 1, True):
            with self.assertRaisesRegex(ValueError, 'Select one existing'):
                measure_prescribed_term(self.snapshot, self.at, self.measure,
                    'unregistered-direction', index, **self.arguments)

    def test_accepted_base_does_not_acquire_the_unaccepted_clock(self):
        root = Path(__file__).resolve().parents[2]
        read = lambda relative: json.loads((root / relative).read_text())
        accepted = Snapshot(read('regulation/stage-a/authoring-eu.json') +
                            read('regulation/jurisdiction/canonical/authoring.json'),
                            read('regulation/stage-b/clocks-and-parameters.json'))
        with self.assertRaisesRegex(MissingInput, 'not available in the supplied A/B snapshot'):
            measure_prescribed_term(accepted, self.at, self.measure,
                'unregistered-direction', 0, **self.arguments)


if __name__ == '__main__':
    unittest.main()
