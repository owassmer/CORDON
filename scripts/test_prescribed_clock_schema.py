"""Mechanical v7 source-clock witnesses; no fixture asserts legal acceptance."""

import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest

import verify_stage_b as verifier


def clock_fixture():
    return dict(clock_id='unregistered-clock', producer_provision_version_id='fixture:terms:v1',
                source_phrase='the prescribed term', kind='deadline', anchor={
                    'kind': 'event',
                    'event': 'legally sufficient notification of the operative prescription to this recipient',
                    'record': 'OPERATOR_RECORD'}, magnitude={'source_input': 'prescribed-term'},
                bound='exact', unit=None, recurrence=None, relation=None, window=None,
                applies_when='The exact prescribed notification and commencement clause applies.',
                legal_duty_owner='OWNER_OR_HOLDER', executor='OWNER_OR_HOLDER',
                consumer_decision='fixture:consumer', consequence_on_expiry={'kind': 'none', 'ref': None},
                completion={'kind': 'record',
                            'ref': 'concrete commencement of the removal work specified by this prescription clause'},
                note=None)


class PrescribedClockSchema(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='cordon-prescribed-clock-schema-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.ledger_path = self.root / 'ledger.json'
        self.a_paths = (self.root / 'eu.json', self.root / 'jurisdiction.json')
        self.population_path = self.root / 'population.json'
        self.provisions = [dict(provision_version_id=identity + ':v1', stable_provision_id=identity,
                                source_quote='the prescribed term; within 10 days',
                                effective_from='2020-01-01', effective_to_exclusive='', semantic_change='YES',
                                condition_ast={'predicate': 'fixture condition'})
                           for identity in ('fixture:terms', 'fixture:consumer')]
        self.population = {'seams': {'1': [r['provision_version_id'] for r in self.provisions],
                                    '2': [], '3': [], '4': []}}
        self.base = dict(schema='stage-b-essence-v7', conventions={}, clocks=[clock_fixture()], parameters=[],
                         dispositions=[
                             dict(provision_version_id='fixture:terms:v1', disposition='clock',
                                  ref='unregistered-clock', why='Synthetic source-input fixture.', aperture='IN_APERTURE'),
                             dict(provision_version_id='fixture:consumer:v1', expression='the prescribed term',
                                  disposition='not_a_clock', ref=None, why='Synthetic consumer fixture.', aperture='IN_APERTURE')],
                         closure_manifest=[dict(seam=i, title='Synthetic fixture', status='OPEN', reread=None,
                                                semantic_reviewer=None, acceptance_act=None, acceptance_evidence=None,
                                                semantic_acceptance='NOT_ASSERTED', accepted_content_sha256=None)
                                           for i in range(1, 5)])

    def check(self, ledger, *, population=None):
        self.ledger_path.write_text(json.dumps(ledger))
        self.a_paths[0].write_text('[]')
        self.a_paths[1].write_text(json.dumps(self.provisions))
        self.population_path.write_text(json.dumps(population or self.population))
        return verifier.main(self.ledger_path, self.a_paths, self.population_path)

    def reject(self, ledger, message, **kwargs):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit):
            self.check(ledger, **kwargs)
        self.assertIn(message, output.getvalue())

    def changed_clock(self, **changes):
        ledger = copy.deepcopy(self.base)
        ledger['clocks'][0].update(changes)
        return ledger

    def test_source_form_passes_all_owner_gates_without_a_case_identity_registry(self):
        with contextlib.redirect_stdout(io.StringIO()):
            view = self.check(self.base)
            changed = copy.deepcopy(self.base)
            changed['clocks'][0]['clock_id'] = 'another-unseen-clock'
            changed['dispositions'][0]['ref'] = 'another-unseen-clock'
            self.check(changed)
        self.assertEqual(view['clocks'][0]['magnitude'], {'source_input': 'prescribed-term'})
        self.assertIsNone(view['clocks'][0]['unit'])
        self.assertTrue(verifier.clock_value_matches(clock_fixture(), 'stage-b-essence-v7'))
        self.assertFalse(verifier.clock_value_matches(clock_fixture()))

    def test_v6_cannot_carry_a_source_bound_clock(self):
        changed = copy.deepcopy(self.base)
        changed['schema'] = 'stage-b-essence-v6'
        self.reject(changed, 'unsupported source-bound clock form')

    def test_discriminator_is_exact_and_cannot_hide_a_fixed_default(self):
        for magnitude in [{}, {'source_input': 'another-input'}, {'magnitude': '10'},
                          {'source_input': 'prescribed-term', 'default': '10'},
                          {'source_input': 'prescribed-term', 'magnitude': '10'}]:
            with self.subTest(magnitude=magnitude):
                changed = self.changed_clock(magnitude=magnitude)
                self.reject(changed, 'unsupported source-bound clock form')
                self.assertFalse(verifier.clock_value_matches(changed['clocks'][0], 'stage-b-essence-v7'))
        self.reject(self.changed_clock(magnitude=None), 'bound must be set iff magnitude is set')
        self.reject(self.changed_clock(magnitude='10'), 'clock quantity or calendar date is not evidenced')
        self.reject(self.changed_clock(magnitude=10), 'magnitude not numeric')

    def test_source_form_cannot_prefill_a_unit_or_change_the_period_kind(self):
        for change in [dict(unit='calendar_days'), dict(unit='hours'), dict(bound='floor'),
                       dict(kind='not_before'), dict(kind='minimum_duration'),
                       dict(relation='after'), dict(window='caller-selected window')]:
            with self.subTest(change=change):
                self.reject(self.changed_clock(**change), 'unsupported source-bound clock form')

    def test_notification_and_concrete_commencement_cannot_change_meaning(self):
        for anchor in [dict(kind='event', event='publication', record='OPERATOR_RECORD'),
                       dict(kind='event', event='completion of owner election', record='OPERATOR_RECORD'),
                       dict(kind='biological', term='flight season', place='fixture')]:
            with self.subTest(anchor=anchor):
                self.reject(self.changed_clock(anchor=anchor), 'unsupported source-bound clock form')
        for completion in [dict(kind='record', ref='completion of removal work'),
                           dict(kind='record', ref='concrete commencement of other work'),
                           dict(kind='none', ref=None)]:
            with self.subTest(completion=completion):
                self.reject(self.changed_clock(completion=completion), 'unsupported source-bound clock form')
        wrong_record = dict(clock_fixture()['anchor'], record='UNQUALIFIED_RECORD')
        self.reject(self.changed_clock(anchor=wrong_record), 'record class')

    def test_source_binding_does_not_bypass_producer_quote_consumer_or_population(self):
        for changes, expected in [
                (dict(producer_provision_version_id='missing:v1'), 'producer not in A'),
                (dict(consumer_decision='missing'), 'not a stable id'),
                (dict(source_phrase='not in the producer quote'), 'source_phrase not in producer quote')]:
            with self.subTest(changes=changes):
                self.reject(self.changed_clock(**changes), expected)
        population = copy.deepcopy(self.population)
        population['seams']['1'].remove('fixture:consumer:v1')
        self.reject(self.base, 'population is not exactly Stage A', population=population)
        changed = copy.deepcopy(self.base)
        changed['dispositions'].pop(0)
        self.reject(changed, 'disposition coverage differs from population')
        changed = copy.deepcopy(self.base)
        changed['dispositions'][0]['provision_version_id'] = 'fixture:consumer:v1'
        self.reject(changed, 'minted disposition producer differs from its target')

    def test_fixed_numeric_validation_is_identical_in_v6_and_v7(self):
        for schema in ('stage-b-essence-v6', 'stage-b-essence-v7'):
            fixed = self.changed_clock(magnitude='10', unit='calendar_days', source_phrase='within 10 days')
            fixed['schema'] = schema
            with self.subTest(schema=schema), contextlib.redirect_stdout(io.StringIO()):
                self.check(fixed)
                self.assertTrue(verifier.clock_value_matches(fixed['clocks'][0], schema))
            fixed['clocks'][0]['magnitude'] = '11'
            self.reject(fixed, 'clock quantity or calendar date is not evidenced')

    def test_accepted_v6_ledger_still_passes_unchanged(self):
        original = verifier.B.read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):
            result = verifier.main()
        self.assertEqual(result['schema'], 'stage-b-essence-v6')
        self.assertEqual(verifier.B.read_bytes(), original)
        self.assertTrue(all(not isinstance(r['magnitude'], dict) for r in result['clocks']))


if __name__ == '__main__':
    unittest.main()
