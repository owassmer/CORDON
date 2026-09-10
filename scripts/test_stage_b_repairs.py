"""Regression evidence for the jointly adjudicated September 4 findings.

All acceptance acts below are synthetic and confined to temporary directories.
Passing these checks is not semantic acceptance or an exhaustive source audit.
"""
import contextlib
import copy
import csv
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import generate_stage_b as generator
import verify_stage_b as verifier
import generate_jurisdiction_step6 as jurisdiction_generator
import verify_jurisdiction_stage_a as jurisdiction_verifier
from verify_stage_a import ast_nodes, verify_result_references


class StageBRepairs(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='cordon-b-regression-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = json.loads(verifier.B.read_text())
        # This isolated baseline is synthetic, irrespective of live acceptance.
        # Bound accepted/partial fixtures below exercise the real acceptance checks.
        for manifest in self.base['closure_manifest']:
            manifest['semantic_acceptance'] = 'NOT_ASSERTED'
            for field in ('semantic_reviewer', 'acceptance_act', 'acceptance_evidence', 'accepted_content_sha256'):
                manifest[field] = None
        self.ledger = self.root / 'ledger.json'
        self.population = self.root / 'regulation/stage-b/population.json'
        self.population.parent.mkdir(parents=True)
        shutil.copyfile(verifier.POPULATION, self.population)
        self.a_paths = tuple(self.root / p for p in verifier.STAGE_A_LOGICAL)
        for src, dst in zip(verifier.STAGE_A_LOGICAL, self.a_paths):
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(verifier.ROOT / src, dst)
        self.a = {r['provision_version_id']: r for p in self.a_paths for r in json.loads(p.read_text())}
        self.view = self.check(self.base)

    def check(self, ledger):
        self.ledger.write_text(json.dumps(ledger, ensure_ascii=False))
        with patch.object(verifier, 'ROOT', self.root), contextlib.redirect_stdout(io.StringIO()):
            return verifier.main(self.ledger, self.a_paths, self.population)

    def reject(self, ledger, message):
        output = io.StringIO()
        self.ledger.write_text(json.dumps(ledger, ensure_ascii=False))
        with patch.object(verifier, 'ROOT', self.root), contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit):
                verifier.main(self.ledger, self.a_paths, self.population)
        self.assertIn(message, output.getvalue())

    def clock(self, rid, ledger=None):
        return next(r for r in (ledger if ledger is not None else self.view)['clocks'] if r['clock_id'] == rid)

    def parameter(self, rid, ledger=None):
        return next(r for r in (ledger if ledger is not None else self.view)['parameters'] if r['parameter_id'] == rid)

    def accepted_fixture(self, seams=(1, 2, 3, 4)):
        ledger = copy.deepcopy(self.base)
        population = json.loads(self.population.read_text())
        for m in ledger['closure_manifest']:
            if m['seam'] not in seams: continue
            m['semantic_acceptance'] = 'ACCEPTED'
            m['semantic_reviewer'] = 'SYNTHETIC REVIEWER — NOT OWEN'
            m['acceptance_act'] = 'ISOLATED TEST FIXTURE — NOT AN ACCEPTANCE'
            m['accepted_content_sha256'] = verifier.acceptance_fingerprint(
                ledger, m, population['seams'], self.a_paths, self.population)
            record = {'schema': 'cordon-stage-b-acceptance-v1', 'seam': m['seam'],
                      'reviewer': m['semantic_reviewer'], 'act': m['acceptance_act'],
                      'accepted_content_sha256': m['accepted_content_sha256']}
            path = self.root / f'synthetic-seam-{m["seam"]}.json'
            path.write_text(json.dumps(record))
            m['acceptance_evidence'] = {'record_path': path.name, 'record_sha256': verifier.sha(path)}
        return ledger

    def generate(self, ledger):
        self.ledger.write_text(json.dumps(ledger, ensure_ascii=False))
        with patch.object(generator, 'ROOT', self.root), patch.object(generator, 'B', self.ledger), \
                patch.object(generator, 'OUT', self.root / 'generated'), patch.object(verifier, 'ROOT', self.root), \
                contextlib.redirect_stdout(io.StringIO()):
            generator.main()
        return json.loads((self.root / 'generated/generation-status.json').read_text())

    def test_historical_owner_payload_does_not_import_orthophotos(self):
        for plan in ('343', '1866'):
            data = self.clock(f'B-CLK-DGR{plan}-owner-data')
            issuance = self.clock(f'B-CLK-DGR{plan}-prescription-issuance')
            self.assertNotIn('orthophoto', data['completion']['ref'])
            self.assertNotIn('orthophoto', issuance['anchor']['event'])
            self.assertNotIn('ortofoto', self.a[data['producer_provision_version_id']]['source_quote'])
        later = self.clock('B-CLK-DGR1593-owner-data')
        self.assertIn('orthophoto', later['completion']['ref'])
        self.assertIn('ortofoto', self.a[later['producer_provision_version_id']]['source_quote'])

    def test_reduction_clock_covers_plants_outside_mandatory_removal(self):
        c = self.clock('B-CLK-EU-5(1)(a)-immediate-sampling-and-removal')
        self.assertEqual(c['anchor']['kind'], 'event')
        self.assertIn('establishment of the infected zone', c['anchor']['event'])
        self.assertNotIn('IMMEDIATE_REMOVAL_REQUIRED', json.dumps(c['anchor']))
        self.assertIn('irrespective', c['applies_when'])
        self.assertEqual(c['completion']['ref'], 'REDUCTION_CONDITION_A_MET')
        self.assertIn('irrespective of their health status', self.a[c['producer_provision_version_id']]['source_quote'])

    def test_annual_occurrence_is_not_full_programme_completion(self):
        for version, duration in [('1', 'two'), ('2', 'one')]:
            annual = self.clock(f'B-CLK-EU-5(4)(a)-v{version}-annual-follow-up-survey')
            programme = self.clock(f'B-CLK-EU-5(4)(a)-v{version}-{duration}-year-follow-up')
            self.assertEqual(annual['completion']['kind'], 'record')
            self.assertIn('annual survey occurrence', annual['completion']['ref'])
            self.assertEqual(programme['completion']['kind'], 'a_version_performed')
            self.assertNotEqual(annual['completion'], programme['completion'])

    def test_lab_accreditation_has_its_plant_health_application_boundary(self):
        sid = 'EU-2017-625:Art.37(1,3-5):official-laboratory-designation-tuple'
        old, new = self.a[sid + ':v1'], self.a[sid + ':v2']
        self.assertEqual((old['effective_from'], old['effective_to_exclusive'], new['effective_from']),
                         ('2019-12-14', '2022-04-29', '2022-04-29'))
        self.assertNotIn('17025', json.dumps(old['condition_ast']))
        self.assertIn('17025', json.dumps(new['condition_ast']))
        for row in (old, new):
            self.assertIn('shall apply from 29 April 2022', row['source_quote'])
            self.assertIn('domestic', row['semantic_note'] + row['true_effect'])

    def test_expression_deferral_preserves_retained_status_but_blocks_wholly_deferred_routes(self):
        cid = 'B-CLK-EU-625-38(1)-immediate-result-notification'
        self.assertEqual(self.clock(cid)['consumer_decision'],
                         'EU-2017-625:Art.39:official-laboratory-audit-status')
        mutant = copy.deepcopy(self.base)
        self.clock(cid, mutant)['consumer_decision'] = 'IT-DLGS-19-2021:Art.27(3)'
        self.reject(mutant, 'consumer_decision crosses into an explicitly deferred route')

    def test_lab_analysis_and_result_notification_are_distinct(self):
        analysis = self.clock('B-CLK-DM169819-10(3)-method-compatible-analysis')
        notice = self.clock('B-CLK-EU-625-38(1)-immediate-result-notification')
        self.assertNotEqual(analysis['anchor'], notice['anchor'])
        self.assertEqual(analysis['legal_duty_owner'], 'OFFICIAL_LABORATORY')
        self.assertEqual(notice['legal_duty_owner'], 'OFFICIAL_LABORATORY')
        self.assertIn('specific arrangement', notice['applies_when'])
        self.assertIsNone(notice['magnitude'])
        producer = self.a[notice['producer_provision_version_id']]
        effects = {r['effect'] for r in producer['condition_ast']['route_table']}
        self.assertIn('IMMEDIATE_LABORATORY_NOTIFICATION_REQUIRED', effects)
        self.assertIn('LABORATORY_NOTIFICATION_UNDER_SPECIFIC_ARRANGEMENT', effects)
        audit = self.a['EU-2017-625:Art.39:official-laboratory-audit-status:v1']
        self.assertIn(producer['stable_provision_id'], audit['external_dependencies'])

    def test_historical_additional_rules_are_conditional_and_interval_bounded(self):
        for rid in ('B-PAR-LR4-5(4)-pre-LR45-vector-radius-100m',
                    'B-PAR-LR4-5(5)-pre-LR45-interim-isolation-100m'):
            r = self.parameter(rid)
            self.assertEqual(r['legal_effect'], 'CONDITIONAL')
            self.assertEqual(r['effective_to_exclusive'], '2021-12-18')
            self.assertIn('controlling Union law', r['applies_when'])
        annual = self.clock('B-CLK-LR4-4(4)-post-LR45-v2-annual-inspection')
        self.assertIn('eradication or containment', annual['anchor']['scope'])
        self.assertIsNone(annual['anchor']['opening_state'])
        for art in ('5(3)', '6(2)'):
            vid = f'PUG-LR4-2017:Art.{art}:pre-LR45-v1'
            self.assertFalse(any(p['producer_provision_version_id'] == vid for p in self.base['parameters']))

    def test_q5_and_doubtful_result_qualifiers_remain_resolved(self):
        a = next(r for r in self.a.values() if 'action-plan-15-day-unit-conflict' in r['provision_version_id'])
        self.assertNotIn('PLAN_15_DAY_CONCURRENT_OBLIGATION_ESTABLISHED', json.dumps(a['condition_ast']))
        self.assertEqual(a['authority_judgment_required'], 'NO')
        self.assertIn('does not establish a separate earlier deadline', a['true_effect'])
        for r in self.base['parameters']:
            if r['parameter_id'].startswith('B-PAR-DDS45-Cq-'):
                self.assertIn('where a doubtful result makes it applicable', r['applies_when'])

    def test_baseline_and_unaccepted_consumer_parity(self):
        self.check(self.base)
        status = self.generate(self.base)
        self.assertEqual(status['semantic_acceptance'], 'NOT_ASSERTED')
        self.assertEqual(status['accepted_seams'], [])
        self.assertEqual(status['canonical_sha256'], verifier.sha(self.ledger))
        for name in ('clocks', 'parameters'):
            with (self.root / f'generated/{name}.csv').open(newline='') as handle:
                actual = list(csv.DictReader(handle))
            self.assertEqual(actual, [{k: generator.flat(v) for k, v in r.items()} for r in self.view[name]])

    def test_report_route_boundary_preserves_deadline(self):
        sid = 'EU-2016-2031:Art.22(3):annual-survey-results-report'
        old, new = self.a[sid + ':v1'], self.a[sid + ':v2']
        self.assertEqual((old['effective_from'], old['effective_to_exclusive'], new['effective_from']),
                         ('2019-12-14', '2025-01-05', '2025-01-05'))
        self.assertNotIn('Article 103', old['source_quote'])
        self.assertEqual(old['external_dependencies'], [])
        self.assertIn('Article 103', new['source_quote'])
        reports = [r for r in self.view['clocks'] if r['producer_provision_version_id'].startswith(sid + ':')]
        for day, version in [('2024-04-30', ':v1'), ('2025-01-04', ':v1'), ('2025-01-05', ':v2'), ('2025-04-30', ':v2')]:
            applicable = [r for r in reports if r['effective_from'] <= day < (r['effective_to_exclusive'] or '9999')]
            self.assertEqual(len(applicable), 1)
            self.assertTrue(applicable[0]['producer_provision_version_id'].endswith(version))
            self.assertEqual(applicable[0]['recurrence']['calendar_deadline'], {'month': '4', 'day': '30'})

    def test_buffer_and_infected_zone_are_distinct(self):
        rid = 'B-CLK-DM348260-9.3-annual-containment-buffer-survey'
        buffer = self.clock(rid)
        infected = self.clock('B-CLK-EU-15(2)-v1-annual-containment-survey')
        self.assertIn('buffer zone', buffer['anchor']['scope'])
        self.assertIn('infected-zone parts', infected['anchor']['scope'])
        disposition = next(d for d in self.base['dispositions'] if d['ref'] == rid and d['disposition'] == 'clock')
        self.assertEqual(disposition['ref'], rid)
        self.assertEqual(buffer['recurrence']['period']['magnitude'], '1')
        m = copy.deepcopy(self.base)
        next(d for d in m['dispositions'] if d['ref'] == rid and d['disposition'] == 'clock')['ref'] = infected['clock_id']
        self.reject(m, 'minted disposition producer differs')

    def test_approved_vector_cadence_preserves_containment_scope(self):
        c = self.clock('B-CLK-DM348260-9.3-vector-investigation-containment')
        self.assertEqual(c['recurrence'], {
            'period': {'magnitude': '1', 'unit': 'years', 'bound': 'exact'},
            'occurrences_per_period': None, 'calendar_deadline': None})
        self.assertIsNone(c['window'])
        self.assertIsNone(c['note'])
        for phrase in ('annualmente', 'diversamente', 'contenimento'):
            self.assertIn(phrase, c['source_phrase'])
        for phrase in ('buffer zone', 'at least 2 km', 'social and cultural', 'higher-risk'):
            self.assertIn(phrase, c['anchor']['scope'])
        self.assertEqual(c['applies_when'], 'containment measures apply in the demarcated area')
        self.assertIn('annual vector investigations', self.a[c['producer_provision_version_id']]['true_effect'])

    def test_vector_phrase_is_source_continuation_without_page_header(self):
        c = self.clock('B-CLK-DM348260-9.3-vector-investigation-containment')
        a = self.a[c['producer_provision_version_id']]
        raw = (verifier.ROOT / a['source_paths']).read_text()
        self.assertEqual(verifier.sha(verifier.ROOT / a['source_paths']), a['source_snapshot_hashes'])
        furniture = '\fIl Ministro dell’agricoltura, della sovranità alimentare e delle foreste\n'
        start = raw.index('In particolare, nelle aree in eradicazione')
        end = raw.index('Il monitoraggio deve essere,', start)
        self.assertIn(furniture, raw[start:end])
        source_sentence = ' '.join(raw[start:end].replace(furniture, '').split())
        self.assertEqual(c['source_phrase'], source_sentence)
        self.assertIn(source_sentence, ' '.join(a['source_quote'].split()))
        self.assertNotIn(furniture, a['source_quote'])

    def test_reporting_proof_is_not_an_extra_legal_act(self):
        sid = 'EU-2016-2031:Art.22(3):annual-survey-results-report'
        reports = [c for c in self.base['clocks'] if c['producer_provision_version_id'].startswith(sid + ':')]
        self.assertEqual(len(reports), 2)
        for c in reports:
            a = self.a[c['producer_provision_version_id']]
            self.assertEqual(c['completion'], {'kind': 'a_version_performed', 'ref': a['provision_version_id']})
            self.assertIsNone(c['note'])
            self.assertIn('authoritative evidence of successful reporting', a['evidence_contract'])
            self.assertIn('not an independent legal completion condition under this provision', a['evidence_contract'])
            self.assertIn('not automatically breached', a['false_effect'])
            self.assertIn('attempted submission does not satisfy reporting', a['false_effect'])
            self.assertNotIn('UNRESOLVED', a['evidence_contract'])
            if a['provision_version_id'].endswith(':v1'):
                self.assertNotIn('Article 103', a['evidence_contract'])
            else:
                self.assertIn('Article 103', a['evidence_contract'])

    def test_incorporating_expression_resolves_both_reporting_versions(self):
        m = copy.deepcopy(self.base)
        d = next(d for d in m['dispositions'] if d['provision_version_id'] == 'EU-2020-1201:2(8):v1' and d['disposition'] == 'qualifies_clock')
        self.assertEqual(len(d['ref']), 2)
        for day, suffix in [('2024-04-30', '30-april'), ('2025-04-30', '30-april-v2')]:
            targets = [self.clock(rid) for rid in d['ref']]
            applicable = [r for r in targets if r['effective_from'] <= day < (r['effective_to_exclusive'] or '9999')]
            self.assertEqual(len(applicable), 1)
            self.assertTrue(applicable[0]['clock_id'].endswith(suffix))
        d['ref'] = d['ref'][0]
        self.reject(m, 'does not cover the producer interval')

    def test_eradication_has_its_own_operative_producer(self):
        c = self.clock('B-CLK-DM348260-9.3-annual-vector-investigation-eradication')
        a = self.a[c['producer_provision_version_id']]
        containment = self.clock('B-CLK-DM348260-9.3-vector-investigation-containment')
        self.assertNotEqual(c['producer_provision_version_id'], containment['producer_provision_version_id'])
        self.assertEqual(c['consumer_decision'], a['stable_provision_id'])
        self.assertIn('annual vector investigations throughout the eradication demarcated area', a['true_effect'])
        raw = (verifier.ROOT / a['source_paths']).read_text()
        raw = raw.replace('\fIl Ministro dell’agricoltura, della sovranità alimentare e delle foreste\n', '')
        self.assertIn(verifier.norm(a['source_quote']), verifier.norm(raw))
        self.assertIn({'provision_ref': 'EU-2020-1201:10-sub3'}, a['condition_ast']['all_of'])
        parent = self.a['EU-2020-1201:10-sub3:v1']['condition_ast']['all_of']
        self.assertIn({'result_ref': {'producer_stable_provision_id': 'EU-2020-1201:12',
                                    'allowed_effect': 'ERADICATION_MEASURES_APPLY'}}, parent)
        self.assertIn({'result_ref': {'producer_stable_provision_id': 'PUG-LR4-2017:Art.3(2)',
                                    'allowed_effect': 'OPERATIVE_LEGAL_AREA_STATE_ESTABLISHED'}}, a['condition_ast']['all_of'])
        self.assertIn('containment', self.a[containment['producer_provision_version_id']]['false_effect'])

    def test_union_obligor_does_not_automatically_become_the_region(self):
        self.assertNotIn('seat_binding', self.base['conventions'])
        for suffix in ('', '-v2'):
            c = self.clock('B-CLK-EU2031-22(3)-annual-report-30-april' + suffix)
            self.assertEqual(c['legal_duty_owner'], 'MEMBER_STATE_CONCERNED')
            self.assertIsNone(c['executor'])
        national = self.a['IT-DLGS-19-2021:Art.27(6):transmit-prior-year-results:v1']
        self.assertEqual(national['actor_role'], 'Central plant-health service')
        self.assertEqual(national['effective_from'], '2021-03-13')
        self.assertIn('Il Servizio fitosanitario centrale trasmette', national['source_quote'])

    def test_survey_completion_does_not_wait_for_reporting(self):
        c = self.clock('B-CLK-IT-31(9)-periodic-area-surveys')
        self.assertEqual(c['completion'], {'kind': 'a_version_performed', 'ref': c['producer_provision_version_id']})
        own = self.a[c['completion']['ref']]
        report = self.a['IT-DLGS-19-2021:Art.31(9):report-area-information:v1']
        self.assertIn('Conduct periodic surveys', own['true_effect'])
        self.assertIn('Communicate', report['true_effect'])
        self.assertNotIn('report', own['true_effect'].lower())

    def test_immediate_testing_does_not_become_a_prerequisite_to_removal(self):
        c = self.clock('B-CLK-EU-7(1)(e)-v2-immediate-sampling')
        self.assertIn('route avoiding point-(e) removal', c['note'])
        self.assertIn('Immediate removal does not require this sampling route', c['note'])
        self.assertNotIn('only alternative', c['note'])
        self.assertEqual(c['consequence_on_expiry'], {'kind': 'a_effect', 'ref': 'POINT_E_REMOVAL_POPULATION'})

    def test_nonsemantic_parameter_versions_are_folded_once(self):
        for article, suffix in [('15(1)', 'sampling-radius-50m'), ('5(1)', 'reduced-buffer-1km')]:
            with self.subTest(article=article):
                rid = f'B-PAR-EU-{article}-v1-{suffix}'
                for day in ('2020-09-01', '2021-10-11', '2026-09-04'):
                    rows = [p for p in self.view['parameters'] if p['consumer_decision'] == f'EU-2020-1201:{article}'
                            and p['effective_from'] <= day < (p['effective_to_exclusive'] or '9999')]
                    self.assertEqual([p['parameter_id'] for p in rows], [rid])
                successor = next(d for d in self.base['dispositions']
                                 if d['provision_version_id'] == f'EU-2020-1201:{article}:v2' and d['ref'] == rid)
                self.assertEqual(successor['disposition'], 'restates_parameter')
                m = copy.deepcopy(self.base)
                duplicate = copy.deepcopy(self.parameter(rid, m))
                duplicate.update(parameter_id=f'B-PAR-EU-{article}-v2-{suffix}',
                                 producer_provision_version_id=f'EU-2020-1201:{article}:v2')
                m['parameters'].append(duplicate)
                self.reject(m, 'duplicate parameter overlaps')

    def test_dimensions_comparators_and_bounds_reject_before_projection(self):
        cases = [
            ('B-PAR-EU-2(4a)-vector-radius-400m', ('unit',), 'km', 'normalized value is not evidenced'),
            ('B-PAR-DDS45-Cq-positive-32', ('comparator',), '>', 'normalized value is not evidenced'),
            ('B-PAR-EU-4(2)-sub1-infected-zone-50m', ('comparator',), '<=', 'comparator disagrees'),
            ('B-PAR-EU-4(2)-sub1-infected-zone-50m', ('comparator',), 'banana', 'comparator vocabulary'),
            ('B-PAR-EU-2(4)-v2-C80-p1', ('value', 'confidence_bound'), 'exact', 'normalized value is not evidenced'),
            ('B-PAR-EU-2(4)-v2-C80-p1', ('value', 'design_prevalence_bound'), 'floor', 'normalized value is not evidenced'),
            ('B-PAR-PNI2026-olea-design', ('value', 'confidence_bound'), 'floor', 'normalized value is not evidenced'),
            ('B-PAR-DGR1075-almond-band-400m', ('comparator',), '>=', 'comparator disagrees'),
        ]
        self.check(self.base)
        for rid, keys, value, message in cases:
            with self.subTest(rid=rid, keys=keys, value=value):
                m = copy.deepcopy(self.base)
                target = self.parameter(rid, m)
                for key in keys[:-1]: target = target[key]
                target[keys[-1]] = value
                self.reject(m, message)
                with self.assertRaises(SystemExit): self.generate(m)
                self.assertFalse((self.root / 'generated').exists())

    def test_scalar_qualifier_is_retained_in_the_source_phrase(self):
        p = self.parameter('B-PAR-DM2022-6.7-post-m5-inward-band-5km')
        self.assertEqual(p['source_phrase'], "almeno nell'area di 5 km")
        self.assertTrue(verifier.source_value_matches(p))
        clipped = dict(p, source_phrase='5 km')
        self.assertFalse(verifier.source_value_matches(clipped))

    def test_temporal_target_list_cannot_reverse_or_duplicate(self):
        for operation in ('reverse', 'duplicate'):
            with self.subTest(operation=operation):
                m = copy.deepcopy(self.base)
                d = next(d for d in m['dispositions'] if isinstance(d['ref'], list))
                if operation == 'reverse': d['ref'].reverse()
                else: d['ref'].append(d['ref'][0])
                self.reject(m, 'temporal target')

    def test_historical_target_covers_interval(self):
        vid = 'IT-DM-2022-XYLELLA-PLAN:§6.4:no-demarcation-two-year-follow-up:pre-m5-v1'
        m = copy.deepcopy(self.base)
        d = next(d for d in m['dispositions'] if d['provision_version_id'] == vid and d['expression'].startswith('Inoltre'))
        self.assertEqual(d['ref'], 'B-CLK-EU-5(4)(a)-v1-two-year-follow-up')
        d['ref'] = 'B-CLK-DM2022-6.4-post-m5-second-year'
        self.reject(m, 'does not cover the producer interval')

    def test_lookback_is_evidence_not_deferral(self):
        m = copy.deepcopy(self.base)
        c = self.clock('B-CLK-EU-7(1)(e)-sub2-two-year-lookback', m)
        self.assertEqual(c['completion']['kind'], 'record')
        self.assertIn('whether or not', c['anchor']['event'])
        c['completion'] = {'kind': 'a_effect', 'ref': 'IMMEDIATE_SAMPLING_DEFERRED'}
        self.reject(m, 'own evidenced condition')

    def test_minted_parameter_requires_own_disposition(self):
        m = copy.deepcopy(self.base)
        m['dispositions'] = [d for d in m['dispositions'] if d['ref'] != 'B-PAR-PNI2026-vitis-design']
        self.reject(m, 'without their own expression disposition')

    def test_parameter_cannot_target_clock(self):
        m = copy.deepcopy(self.base)
        next(d for d in m['dispositions'] if d['ref'] == 'B-PAR-EU-2(4)-v2-C80-p1')['ref'] = 'B-CLK-DM169819-14(3)-research-lab-24h'
        self.reject(m, 'target kind disagrees')

    def test_minted_expression_is_derived_and_cannot_be_reauthored(self):
        owned = [d for d in self.base['dispositions'] if d['disposition'] in ('clock', 'parameter')]
        self.assertEqual(len(owned), len(self.base['clocks']) + len(self.base['parameters']))
        for d in owned:
            self.assertNotIn('expression', d)
            target = next(r for r in self.base['clocks'] + self.base['parameters']
                          if r.get('clock_id', r.get('parameter_id')) == d['ref'])
            self.assertEqual(target['producer_provision_version_id'], d['provision_version_id'])
            self.assertIn(verifier.norm(target['source_phrase']), verifier.norm(self.a[d['provision_version_id']]['source_quote']))
        m = copy.deepcopy(self.base)
        next(d for d in m['dispositions'] if d['disposition'] == 'clock')['expression'] = 'parallel owner'
        self.reject(m, 'disposition field set')
        m = copy.deepcopy(self.base)
        next(d for d in m['dispositions'] if d['disposition'] == 'clock')['ref'] = 'missing'
        self.reject(m, 'one existing target')

    def test_spatial_restatements_resolve_quantity_and_role(self):
        regional = {f'REG-PUGLIA-U181-DIR-{suffix}:area-state-transition:v1'
                    for suffix in ('2024-00091', '2024-00092', '2024-00093', '2024-00094',
                                   '2025-00236', '2026-00004', '2026-00112')}
        national = 'IT-DM-348260-2026-XYLELLA-PLAN:§8.6:area-composition:v1'
        selected = [d for d in self.base['dispositions'] if d['disposition'] == 'restates_parameter'
                    and (d['provision_version_id'] == national or
                         d['provision_version_id'] in regional and 'cuscinetto' in d['expression'].lower())]
        self.assertEqual(len(selected), 10)
        def check(d):
            target = self.parameter(d['ref'])
            if '50 m' in d['expression']:
                expected = ('50', 'm', 'infected zone')
            elif '5 km quando' in d['expression'] and '2,5' not in d['expression']:
                expected = ('5', 'km', 'buffer zone')
            else:
                expected = ('2.5', 'km', 'buffer zone')
            self.assertEqual((target['value'], target['unit']), expected[:2])
            self.assertIn(expected[2].split()[0], target['scope']['zone_type'].lower())
        for d in selected:
            check(d)
        buffer = next(d for d in selected if d['provision_version_id'] in regional)
        wrong = buffer | {'ref': 'B-PAR-EU-4(2)-sub1-infected-zone-50m'}
        with self.assertRaises(AssertionError): check(wrong)

    def test_removal_clocks_preserve_post_exception_applicability(self):
        ids = ['B-CLK-EU-13(1)-sub1-immediate-removal', 'B-CLK-EU-13(1)-sub1-before-next-flight-season',
               'B-CLK-EU-14(1)-v1-treatment-before-removal', 'B-CLK-EU-14(1)-v2-treatment-before-removal',
               'B-CLK-DDS31-containment-48h', 'B-CLK-DDS45-containment-48h']
        for rid in ids:
            row = self.clock(rid)
            self.assertIn('13(1) baseline population', row['applies_when'])
            self.assertIn('13(2)', row['applies_when'])
            if rid.startswith('B-CLK-EU-14'):
                self.assertEqual(row['anchor']['effect'], 'ARTICLE_13_REMOVAL_STANDS')
                self.assertEqual(row['anchor']['producer_stable_provision_id'], 'EU-2020-1201:13(2)')

    def test_deduplicated_content_still_invalidates_acceptance(self):
        m = self.accepted_fixture()
        d = next(d for d in m['dispositions'] if d['disposition'] == 'clock')
        d['why'] = 'Changed adjudication of the same referenced expression'
        self.reject(m, 'content no longer matches')
        m = self.accepted_fixture()
        row = self.clock('B-CLK-EU-13(1)-sub1-immediate-removal', m)
        row['applies_when'] = 'flight season only'
        self.reject(m, 'content no longer matches')

    def test_numeric_roles_cannot_swap(self):
        for rid, fields in [('B-PAR-EU-2(4)-v2-C80-p1', ('confidence', 'design_prevalence')),
                            ('B-PAR-PNI2026-olea-medium-workload', ('samples', 'tests'))]:
            with self.subTest(rid=rid):
                m = copy.deepcopy(self.base)
                value = self.parameter(rid, m)['value']
                a, b = fields
                value[a], value[b] = value[b], value[a]
                self.reject(m, 'normalized value is not evidenced')

    def test_proportion_is_not_interchangeable_with_percent(self):
        m = copy.deepcopy(self.base)
        self.parameter('B-PAR-PNI2026-olea-design', m)['value']['confidence'] = '0.95'
        self.reject(m, 'normalized value is not evidenced')

    def test_month_order_and_wrap(self):
        m = copy.deepcopy(self.base)
        value = self.parameter('B-PAR-DDS31-eradication-no-treatment-window', m)['value']
        value['from_month'], value['to_month'] = value['to_month'], value['from_month']
        self.reject(m, 'normalized value is not evidenced')

    def test_clock_magnitude_and_units(self):
        for key, value in [('magnitude', '999'), ('unit', 'calendar_days')]:
            with self.subTest(key=key):
                m = copy.deepcopy(self.base)
                self.clock('B-CLK-DM169819-14(3)-research-lab-24h', m)[key] = value
                self.reject(m, 'clock quantity or calendar date is not evidenced')

    def test_calendar_date_validity_and_source_fidelity(self):
        for month, day in [('2', '31'), ('4', '29')]:
            with self.subTest(date=(month, day)):
                m = copy.deepcopy(self.base)
                self.clock('B-CLK-EU2031-22(3)-annual-report-30-april', m)['recurrence']['calendar_deadline'] = {'month': month, 'day': day}
                self.reject(m, 'clock quantity or calendar date is not evidenced')

    def test_cadence_and_occurrence_count(self):
        m = copy.deepcopy(self.base)
        m['clocks'][0]['recurrence']['period']['magnitude'] = '17'
        self.reject(m, 'clock quantity or calendar date is not evidenced')
        m = copy.deepcopy(self.base)
        self.clock('B-CLK-EU-5(1)(d)-vector-tests-twice-in-flight-season', m)['recurrence']['occurrences_per_period']['count'] = '3'
        self.reject(m, 'clock quantity or calendar date is not evidenced')

    def test_clock_bounds_reject_before_projection(self):
        cases = [
            ('B-CLK-DM169819-14(3)-research-lab-24h', ('bound',), 'banana', 'bound vocabulary'),
            ('B-CLK-DM169819-14(3)-research-lab-24h', ('bound',), 'floor', 'not evidenced'),
            ('B-CLK-EU-5(1)(b)-tests-once-a-year', ('recurrence', 'occurrences_per_period', 'bound'), 'exact', 'not evidenced'),
            ('B-CLK-EU-5(1)(d)-vector-tests-twice-in-flight-season', ('recurrence', 'occurrences_per_period', 'bound'), 'floor', 'not evidenced'),
            ('B-CLK-EU-2(1)-v1', ('recurrence', 'period', 'bound'), 'floor', 'not evidenced'),
            ('B-CLK-EU-5(4)(a)-v1-two-year-follow-up', ('bound',), 'exact', 'not evidenced'),
            ('B-CLK-EU-6(3)-two-year-post-lift-surveys', ('bound',), 'floor', 'not evidenced'),
        ]
        self.check(self.base)
        for rid, keys, value, message in cases:
            with self.subTest(rid=rid, keys=keys):
                m = copy.deepcopy(self.base)
                target = self.clock(rid, m)
                for key in keys[:-1]: target = target[key]
                target[keys[-1]] = value
                self.reject(m, message)
                with self.assertRaises(SystemExit): self.generate(m)
                self.assertFalse((self.root / 'generated').exists())

    def test_italian_recurrence_quantity_and_bound(self):
        c = copy.deepcopy(self.clock('B-CLK-EU-5(1)(b)-tests-once-a-year'))
        c['source_phrase'] = 'Le analisi sono effettuate a intervalli regolari e almeno due volte l’anno.'
        c['recurrence']['occurrences_per_period']['count'] = '2'
        self.assertTrue(verifier.clock_value_matches(c))
        c['recurrence']['occurrences_per_period']['bound'] = 'exact'
        self.assertFalse(verifier.clock_value_matches(c))
        c['recurrence']['occurrences_per_period'].update(count='1', bound='floor')
        self.assertFalse(verifier.clock_value_matches(c))

    def test_italian_distance_phrase_bound(self):
        p = copy.deepcopy(self.parameter('B-PAR-DGR1075-almond-band-400m'))
        p.update(source_phrase='entro la distanza di 20 km', value='20', unit='km')
        self.assertTrue(verifier.source_value_matches(p))
        p.update(kind='floor', comparator='>=')
        self.assertFalse(verifier.source_value_matches(p))

    def test_acceptance_membership_follows_producer_population(self):
        m = self.accepted_fixture((1,))
        population = json.loads(self.population.read_text())['seams']
        other = next(c for c in m['clocks'] if c['producer_provision_version_id'] in population['2'])
        other['note'] = 'Synthetic open term in an unaccepted seam.'
        self.assertEqual(self.generate(m)['semantic_acceptance'], 'PARTIAL')
        own = next(c for c in m['clocks'] if c['producer_provision_version_id'] in population['1'])
        own['note'] = 'Synthetic changed open term in the accepted seam.'
        self.reject(m, 'content no longer matches')
        with self.assertRaises(SystemExit): self.generate(m)

    def test_stated_recurrence_components_cannot_be_erased(self):
        cases = [('B-CLK-EU-2(1)-v1', 'period'),
                 ('B-CLK-EU-5(1)(b)-tests-once-a-year', 'occurrences_per_period'),
                 ('B-CLK-EU2031-22(3)-annual-report-30-april', 'calendar_deadline')]
        self.generate(self.base)
        previous = {p.name: p.read_bytes() for p in (self.root / 'generated').iterdir()}
        for rid, field in cases:
            with self.subTest(rid=rid):
                m = copy.deepcopy(self.base)
                self.clock(rid, m)['recurrence'][field] = None
                self.reject(m, 'not evidenced by source_phrase')
                with self.assertRaises(SystemExit): self.generate(m)
                self.assertEqual(previous, {p.name: p.read_bytes() for p in (self.root / 'generated').iterdir()})
        c = copy.deepcopy(self.clock('B-CLK-EU-2(1)-v1'))
        c['source_phrase'] = 'at the most appropriate time of each year'
        c['recurrence'] = {'period': None, 'occurrences_per_period': None, 'calendar_deadline': None}
        # An annual time frame in this exact phrase is still explicit; biological timing alone is not.
        self.assertFalse(verifier.clock_value_matches(c))
        c['source_phrase'] = 'at the most appropriate time of the year'
        self.assertTrue(verifier.clock_value_matches(c))
        c['source_phrase'] = 'periodicamente'
        self.assertTrue(verifier.clock_value_matches(c))

    def test_effective_dates_are_derived_not_authored(self):
        for kind in ('clocks', 'parameters'):
            for authored, view in zip(self.base[kind], self.view[kind]):
                self.assertNotIn('effective_from', authored)
                self.assertNotIn('effective_to_exclusive', authored)
                producer = self.a[view['producer_provision_version_id']]
                self.assertEqual(view['effective_from'], producer['effective_from'])
                self.assertEqual(authored, {k: v for k, v in view.items()
                                           if k not in ('effective_from', 'effective_to_exclusive')})
        m = copy.deepcopy(self.base)
        m['clocks'][0]['effective_from'] = '1900-01-01'
        self.reject(m, 'effective dates belong to the derived consumer view')
        # Fingerprints bind the authored state plus upstream bytes, regardless of projection enrichment.
        seams = json.loads(self.population.read_text())['seams']
        for manifest in self.base['closure_manifest']:
            self.assertEqual(verifier.acceptance_fingerprint(self.base, manifest, seams, self.a_paths, self.population),
                             verifier.acceptance_fingerprint(self.view, manifest, seams, self.a_paths, self.population))

    def test_changed_upstream_interval_drives_view_and_invalidates_acceptance(self):
        accepted = self.accepted_fixture()
        rid = 'B-CLK-DM169819-10(3)-method-compatible-analysis'
        vid = self.clock(rid)['producer_provision_version_id']
        path = self.a_paths[1]
        rows = json.loads(path.read_text())
        producer = next(r for r in rows if r['provision_version_id'] == vid)
        producer['effective_to_exclusive'] = '2030-01-01'
        path.write_text(json.dumps(rows, ensure_ascii=False))
        view = self.check(self.base)
        self.assertEqual(self.clock(rid, view)['effective_to_exclusive'], '2030-01-01')
        self.reject(accepted, 'content no longer matches')
        with self.assertRaises(SystemExit): self.generate(accepted)

    def test_territory_is_route_specific_not_all_laboratory_evidence(self):
        for sid in ('EU-2017-625:Art.40(1)(b):other-official-activity-derogation',
                    'EU-2017-625:Art.42:temporary-method-designation'):
            row = self.a[sid + ':v1']
            self.assertIn('same Member State', json.dumps(row['condition_ast']))
            self.assertIn('shall be located in the Member States', row['source_quote'])
        nrl = self.a['EU-2017-625:Art.100:national-reference-laboratory-status:v1']
        self.assertIn('42(2)(a) and (b)', json.dumps(nrl['condition_ast']))
        self.assertNotIn('same Member State', json.dumps(nrl['condition_ast']))
        self.assertIn('EEA contracting country', json.dumps(nrl['condition_ast']))
        self.assertIn('neither', nrl['semantic_note'])

    def test_transfer_promptness_has_its_own_endpoints_without_invalidating_results(self):
        dispatch = self.clock('B-CLK-DTU39-4.2-prompt-sample-dispatch')
        confirmation = self.clock('B-CLK-DDS31-prompt-confirmation-transfer')
        delivery = self.clock('B-CLK-DDS31-custody-same-day')
        self.assertIn('collection', dispatch['anchor']['event'])
        self.assertIn('dispatched', dispatch['completion']['ref'])
        self.assertIn('required first-level', confirmation['anchor']['event'])
        self.assertIn('delivered', confirmation['completion']['ref'])
        self.assertNotEqual(dispatch['completion'], delivery['completion'])
        self.assertNotEqual(confirmation['anchor'], delivery['anchor'])
        for clock in (dispatch, confirmation):
            self.assertIsNone(clock['magnitude'])
            self.assertEqual(clock['unit'], 'indefinite')
            self.assertEqual(clock['consequence_on_expiry'], {'kind': 'none', 'ref': None})

    def test_programme_performance_and_regularity_are_not_just_applicability_or_counts(self):
        for rid in ('B-CLK-DM2022-6.4-post-m5-second-year', 'B-CLK-DM348260-8.5-second-year'):
            c = self.clock(rid)
            self.assertEqual(c['completion']['kind'], 'record')
            self.assertIn('annual surveys performed', c['completion']['ref'])
            self.assertIn('minimum two-year', c['completion']['ref'])
            self.assertIn('not additional work', c['completion']['ref'])
        annual = self.a['PUG-LR4-2017:Art.4(4):post-LR45-v2']
        self.assertIn('same qualifying survey evidence', annual['evidence_contract'])
        self.assertNotIn('only stated period', self.clock('B-CLK-IT-31(9)-periodic-area-surveys')['note'])

    def test_population_cannot_route_rows_outside_manifest_seams(self):
        population = json.loads(self.population.read_text())
        population['seams']['5'] = population['seams'].pop('4')
        self.population.write_text(json.dumps(population))
        self.reject(self.base, 'population must partition seams 1 to 4')

    def test_generator_rejects_changed_population_membership(self):
        m = self.accepted_fixture()
        population = json.loads(self.population.read_text())
        first, second = population['seams']['1'], population['seams']['2']
        first[0], second[0] = second[0], first[0]
        self.population.write_text(json.dumps(population))
        self.reject(m, 'content no longer matches')
        with self.assertRaises(SystemExit): self.generate(m)
        self.assertFalse((self.root / 'generated').exists())

    def test_valid_synthetic_acceptance_projects(self):
        status = self.generate(self.accepted_fixture())
        self.assertEqual(status['semantic_acceptance'], 'ACCEPTED')
        self.assertEqual(status['accepted_seams'], [1, 2, 3, 4])

    def test_partial_acceptance_projects_honestly(self):
        status = self.generate(self.accepted_fixture((1,)))
        self.assertEqual(status['semantic_acceptance'], 'PARTIAL')
        self.assertEqual(status['accepted_seams'], [1])
        self.assertEqual(status['unaccepted_seams'], [2, 3, 4])

    def test_generator_rejects_stale_binding_before_writing(self):
        m = self.accepted_fixture()
        m['clocks'][0]['note'] = 'Unresolved synthetic test term.'
        self.reject(m, 'content no longer matches')
        with self.assertRaises(SystemExit): self.generate(m)
        self.assertFalse((self.root / 'generated').exists())

    def test_generator_rejects_changed_upstream_and_preserves_existing_outputs(self):
        m = self.accepted_fixture()
        self.generate(m)
        before = {p.name: p.read_bytes() for p in (self.root / 'generated').iterdir()}
        self.a_paths[0].write_bytes(self.a_paths[0].read_bytes() + b'\n')
        with self.assertRaises(SystemExit): self.generate(m)
        self.assertEqual(before, {p.name: p.read_bytes() for p in (self.root / 'generated').iterdir()})

    def test_arbitrary_hashed_document_is_not_acceptance_evidence(self):
        m = self.accepted_fixture()
        path = self.root / m['closure_manifest'][0]['acceptance_evidence']['record_path']
        path.write_text('An unrelated, correctly hashed document.\n')
        m['closure_manifest'][0]['acceptance_evidence']['record_sha256'] = verifier.sha(path)
        self.reject(m, 'not an acceptance record')
        with self.assertRaises(SystemExit): self.generate(m)

    def test_acceptance_record_must_match_seam_and_act(self):
        m = self.accepted_fixture()
        path = self.root / m['closure_manifest'][0]['acceptance_evidence']['record_path']
        record = json.loads(path.read_text()); record['seam'] = 4
        path.write_text(json.dumps(record))
        m['closure_manifest'][0]['acceptance_evidence']['record_sha256'] = verifier.sha(path)
        self.reject(m, 'does not record this content')


class StageARepairs(unittest.TestCase):
    def setUp(self):
        self.eu, self.jurisdiction = [json.loads((verifier.ROOT / p).read_text())
                                     for p in verifier.STAGE_A_LOGICAL]
        self.rows = self.eu + self.jurisdiction
        self.by = {r['provision_version_id']: r for r in self.rows}

    @staticmethod
    def condition(node, facts):
        """Bounded propositional witnesses; not the Stage C evaluator."""
        if 'not' in node:
            value = StageARepairs.condition(node['not'], facts)
            return None if value is None else not value
        for op, decisive in [('all_of', False), ('any_of', True)]:
            if op in node:
                values = [StageARepairs.condition(n, facts) for n in node[op]]
                return decisive if decisive in values else None if None in values else not decisive
        return facts.get(json.dumps(node, sort_keys=True))

    @staticmethod
    def facts(node):
        return {json.dumps(n, sort_keys=True): True for n in ast_nodes(node)
                if set(n) & {'predicate', 'provision_ref', 'result_ref'}}

    def effects(self, ast, facts):
        return {r['effect'] for r in ast['route_table'] if self.condition(r['when'], facts) is True}

    def test_cq_criteria_require_their_selected_assay_not_arbitrary_cq(self):
        row = self.by['REG-PUGLIA-U181-DIR-2025-00045:cq-analytical-result-classification:v1']
        domain = 'analytical result uses the DDS45-selected Harper et al. 2010 real-time PCR assay with the 2013 erratum'
        # Same measured value, different method: only this classifier is inapplicable.
        cases = [('valid Cq < 32', 'POSITIVE_ANALYTICAL_RESULT'),
                 ('valid Cq > 32 and < 35', 'DOUBTFUL_ANALYTICAL_RESULT'),
                 ('valid Cq > 35 or source-defined no-Cq result', 'NEGATIVE_ANALYTICAL_RESULT'),
                 ('Cq = 32', 'AUTHORITY_INTERPRETATION_REQUIRED_FOR_BOUNDARY_VALUE'),
                 ('Cq = 35', 'AUTHORITY_INTERPRETATION_REQUIRED_FOR_BOUNDARY_VALUE')]
        for value, expected in cases:
            for applicable in (True, False, None):
                facts = {json.dumps({'predicate': text}, sort_keys=True): state
                         for text, state in [(domain, applicable), (value, True),
                                             ('valid analytical evidence', True)]}
                self.assertEqual(self.effects(row['condition_ast'], facts),
                                 {expected} if applicable is True else set())
        parameters = json.loads(verifier.B.read_text())['parameters']
        for parameter in parameters:
            if parameter['producer_provision_version_id'] == row['provision_version_id']:
                self.assertIn('Harper et al. 2010', parameter['applies_when'])
                self.assertIn('2013 erratum', parameter['applies_when'])

    def test_demarcation_consumes_eu_default_without_affirmative_refusal(self):
        regional = self.by['PUG-LR4-2017:Art.3(1):v1']['condition_ast']
        for version in ('v1', 'v2'):
            eu = self.by[f'EU-2020-1201:5(3):{version}']['condition_ast']
            facts = self.facts(eu)
            choice = json.dumps({'predicate': 'the Member State decides not to establish a demarcated area immediately'}, sort_keys=True)
            for granted in (True, False, None):
                facts[choice] = granted
                exception = self.condition(eu['route_table'][0]['when'], facts)
                rf = self.facts(regional)
                for n in ast_nodes(regional):
                    if n.get('result_ref', {}).get('producer_stable_provision_id') == 'EU-2020-1201:5(3)':
                        rf[json.dumps(n, sort_keys=True)] = (exception if n['result_ref']['allowed_effect'] == 'NO_IMMEDIATE_DEMARCATION_DECIDED'
                                                          else None if exception is None else not exception)
                rf[json.dumps({'predicate': 'analytical evidence lacks official plant-level attribution, including an unresolved pooled positive'}, sort_keys=True)] = False
                expected = ({'NO_IMMEDIATE_DEMARCATION; ARTICLE_5_4_FOLLOW_UP_APPLIES'} if granted is True else
                            {'ARTICLE_4_DEMARCATION_REQUIRED'} if granted is False else set())
                self.assertEqual(self.effects(regional, rf), expected)
        self.assertNotIn('validly declines', json.dumps(regional))

    def test_regional_report_and_buffer_duties_retain_source_triggers(self):
        for vid, source in [('PUG-LR4-2017:Art.2(3):v1', 'qualora sia stato informato'),
                            ('PUG-LR4-2017:Art.3(3):v1', 'confermata nella zona cuscinetto')]:
            row = self.by[vid]
            self.assertIn(source, row['source_quote'])
            ast = row['condition_ast']
            self.assertNotEqual(ast, {'predicate': 'no additional condition'})
            for value in (True, False, None):
                self.assertIs(self.condition(ast, {json.dumps(ast, sort_keys=True): value}), value)

    def test_scientific_retention_reaches_timing_and_regional_consumers(self):
        base = self.by['EU-2020-1201:13(1):v1']['condition_ast']
        exception = self.by['EU-2020-1201:13(2):v1']['condition_ast']
        baseline_key = json.dumps({'result_ref': {'producer_stable_provision_id': 'EU-2020-1201:13(1)',
                                                 'allowed_effect': 'ARTICLE_13_BASELINE_REMOVAL_POPULATION'}}, sort_keys=True)
        standing_key = json.dumps({'result_ref': {'producer_stable_provision_id': 'EU-2020-1201:13(2)',
                                                 'allowed_effect': 'ARTICLE_13_REMOVAL_STANDS'}}, sort_keys=True)
        retained_key = json.dumps({'result_ref': {'producer_stable_provision_id': 'EU-2020-1201:13(2)',
                                                 'allowed_effect': 'SCIENTIFIC_NON_REMOVAL_DEROGATION_EXERCISED'}}, sort_keys=True)
        self.assertEqual(self.effects(base, self.facts(base)), {'ARTICLE_13_BASELINE_REMOVAL_POPULATION'})
        self.assertNotIn('ARTICLE_13_MANDATORY_REMOVAL', json.dumps(self.rows))
        consumers = [r for r in self.rows if r['stable_provision_id'] == 'EU-2020-1201:13(1)-sub1'
                     or r['provision_version_id'] == 'PUG-LR4-2017:Art.6(2):post-LR45-v2'
                     or r['stable_provision_id'].endswith(('containment-removal-population-support',
                         'containment-execution-verification', 'containment-treatment-removal-sequence'))]
        self.assertEqual(len(consumers), 6)
        for applies, eligible, granted in ((True, True, True), (True, True, False),
                                          (True, False, True), (False, True, False)):
            ef = self.facts(exception)
            ef[baseline_key] = applies
            ef[json.dumps({'predicate': 'the infected plants are in a site of plants with particular cultural and social value designated under Article 15(2)(b)'}, sort_keys=True)] = eligible
            ef[json.dumps({'predicate': 'the Member State decides, for scientific purposes, not to remove them'}, sort_keys=True)] = granted
            retained = bool(self.effects(exception, ef))
            for row in consumers:
                route = row['condition_ast']['route_table'][0]
                facts = self.facts(route['when'])
                for node in ast_nodes(route['when']):
                    if 'legally defeats this official execution verification' in node.get('predicate', ''):
                        facts[json.dumps(node, sort_keys=True)] = False
                facts.update({baseline_key: applies, standing_key: not retained, retained_key: retained})
                self.assertEqual(self.condition(route['when'], facts), applies and not retained, row['provision_version_id'])
                if retained:
                    wrong = copy.deepcopy(route['when'])
                    def erase_outcome(node):
                        if isinstance(node, dict):
                            if node.get('result_ref', {}).get('allowed_effect') == 'ARTICLE_13_REMOVAL_STANDS':
                                node.clear(); node.update({'predicate': 'no additional condition'})
                            else:
                                for value in node.values(): erase_outcome(value)
                        elif isinstance(node, list):
                            for value in node: erase_outcome(value)
                    erase_outcome(wrong)
                    facts[json.dumps({'predicate': 'no additional condition'}, sort_keys=True)] = True
                    self.assertTrue(self.condition(wrong, facts), row['provision_version_id'])
            for version in ('v1', 'v2'):
                treatment = self.by[f'EU-2020-1201:14(1):{version}']['condition_ast']
                facts = self.facts(treatment)
                facts.update({baseline_key: applies, standing_key: not retained, retained_key: retained})
                self.assertEqual(bool(self.effects(treatment, facts)), applies)

    def test_three_residual_branches_discriminate_completed_and_pending_cases(self):
        cases = [
            ('EU-2020-1201:2(6):v1', 'different genome target',
             'PRESENCE_CONFIRMED', 'SECOND_CONFIRMATORY_TEST_REQUIRED'),
            ('EU-2020-1201:13(1)-sub1:v1',
             'the specified pest is detected outside the flight season of the vector',
             'REMOVAL_BEFORE_THE_NEXT_FLIGHT_SEASON', 'REMOVAL_IMMEDIATELY_AFTER_OFFICIAL_IDENTIFICATION'),
            ('IT-DLGS-19-2021:Art.28(3):v1',
             'the Regional Plant Health Service decides the official confirmation of the finding on the diagnosis of a validly designated official laboratory (Article 14)',
             'OFFICIAL_FINDING_CONFIRMED', 'OFFICIAL_CONFIRMATION_DECISION_PENDING'),
        ]
        for vid, distinguishing_fact, complete, residual in cases:
            with self.subTest(vid=vid):
                ast = self.by[vid]['condition_ast']
                facts = self.facts(ast['route_table'][0]['when'])
                self.assertEqual(self.effects(ast, facts), {complete})
                old = copy.deepcopy(ast)
                old['route_table'][1]['when']['all_of'].pop()
                self.assertEqual(self.effects(old, facts), {complete, residual})
                key = json.dumps({'predicate': distinguishing_fact}, sort_keys=True)
                facts[key] = False
                self.assertEqual(self.effects(ast, facts), {residual})
                facts[key] = None
                self.assertNotIn(residual, self.effects(ast, facts))

    def test_inside_demarcated_area_does_not_require_second_test(self):
        ast = self.by['EU-2020-1201:2(6):v1']['condition_ast']
        facts = self.facts(ast['route_table'][2]['when'])
        facts[json.dumps({'predicate': 'area outside demarcated areas'}, sort_keys=True)] = False
        self.assertEqual(self.effects(ast, facts), {'PRESENCE_CONFIRMED'})

    def test_article41_cumulative_qualification_and_exact_exception(self):
        sid = 'EU-2017-625:Art.41:representative-method-derogation-authority'
        a41 = self.by[sid + ':v1']['condition_ast']
        method, alternatives = a41['all_of']
        regular, exception = alternatives['any_of']
        facts = self.facts(a41)
        facts[json.dumps(regular, sort_keys=True)] = False
        facts[json.dumps(exception, sort_keys=True)] = False
        self.assertFalse(self.condition(a41, facts))
        a3 = self.by['EU-2021-1353:Art.3:plant-health-partial-accreditation-derogation:v1']['condition_ast']
        eligibility = a3['route_table'][0]['when']
        delegated_facts = self.facts(eligibility)
        reference = json.dumps({'provision_ref': sid}, sort_keys=True)
        self.assertIn(reference, delegated_facts)
        delegated_facts[reference] = self.condition(a41, facts)
        self.assertFalse(self.condition(eligibility, delegated_facts))
        facts[json.dumps(exception, sort_keys=True)] = True
        delegated_facts[reference] = self.condition(a41, facts)
        self.assertTrue(self.condition(eligibility, delegated_facts))
        facts[json.dumps(method, sort_keys=True)] = False
        self.assertFalse(self.condition(a41, facts))

    def test_lab_participation_breach_is_not_an_automatic_suspension(self):
        row = self.by['IT-DTU8-REV2:official-laboratory-route-and-continuing-status:v1']
        ast = row['condition_ast']
        designation, routes, unsuspended = ast['route_table'][0]['when']['all_of']
        self.assertEqual(len(routes['any_of']), 4)
        facts = {json.dumps(designation, sort_keys=True): True,
                 json.dumps(unsuspended, sort_keys=True): True}
        for route in routes['any_of']:
            selected, qualification = route['all_of']
            for atom in (selected, qualification):
                facts[json.dumps(atom, sort_keys=True)] = 'Art.37(' in qualification['provision_ref']
        self.assertEqual(self.effects(ast, facts), {'OFFICIAL_LABORATORY_CONTINUING_STATUS_ESTABLISHED_FOR_TASK'})
        self.assertNotIn('required PT/TPS participation or', json.dumps(ast))
        self.assertIn('must suspend', row['true_effect'])
        facts[json.dumps(unsuspended, sort_keys=True)] = False
        facts[json.dumps(ast['route_table'][1]['when'], sort_keys=True)] = True
        self.assertEqual(self.effects(ast, facts), {'OFFICIAL_LABORATORY_UNAVAILABLE_FOR_TASK'})
        # Qualification must still resolve, even without an active suspension.
        facts = {json.dumps(designation, sort_keys=True): True,
                 json.dumps(unsuspended, sort_keys=True): True}
        for route in routes['any_of']:
            selected, qualification = route['all_of']
            # Another route's qualifications cannot stand in for the applicable route.
            facts[json.dumps(selected, sort_keys=True)] = 'Art.40(' in qualification['provision_ref']
            facts[json.dumps(qualification, sort_keys=True)] = 'Art.40(' not in qualification['provision_ref']
        self.assertNotIn('OFFICIAL_LABORATORY_CONTINUING_STATUS_ESTABLISHED_FOR_TASK', self.effects(ast, facts))

    def test_external_compliance_duty_does_not_require_prior_compliance(self):
        row = self.by['IT-ORD10-2025:Art.6(2):external-laboratory-continuing-compliance:v1']
        self.assertEqual(row['condition_ast'], {'provision_ref': 'IT-ORD10-2025:Art.5(1):external-designation'})
        self.assertIn('IT-DTU8-REV2:official-laboratory-route-and-continuing-status', row['external_dependencies'])
        self.assertIn('Comply with all requirements', row['true_effect'])

    def test_pni_actual_year_boundary_replaces_retired_uncertainty(self):
        parent = self.by['IT-PNI-2026:adoption-and-publication-status:v1']
        child = self.by['IT-PNI-2026:Xylella:Puglia-plant-survey-design:v1']
        self.assertEqual((parent['effective_from'], parent['effective_to_exclusive']), ('2026-01-01', '2027-01-01'))
        self.assertNotIn('CONTENT_HELD_BINDING_INTERVAL_UNRESOLVED', json.dumps(child))
        self.assertNotIn('DECISION_TIME_APPLICABILITY_UNRESOLVED', json.dumps(child))
        self.assertEqual(parent['condition_ast']['otherwise']['effect'], 'OUTSIDE_PROGRAMME_YEAR_2026')
        for route in child['condition_ast']['route_table']:
            if route['effect'].startswith('APPLY_'):
                ref = route['when']['all_of'][0]['result_ref']
                self.assertEqual(ref['allowed_effect'], 'PNI_2026_ADOPTED_AND_PUBLISHED')
        jurisdiction_verifier.verify(jurisdiction_verifier.DEFAULT_AUTHORING, False, False)

    def test_exact_results_and_declared_dependencies_reject_mutations(self):
        verify_result_references(self.rows, self.rows)
        vid = 'PUG-DGR1075-2025:§4.3.2:almond-pre-removal-vector-treatment:v1'
        child = self.by[vid]
        self.assertNotIn('PLAN_ONLY_ROUTE_INTERPRETATION_REQUIRED', json.dumps(child['condition_ast']))
        for mutation, message in [('effect', 'not emitted'), ('dependency', 'not declared'), ('shape', 'malformed')]:
            with self.subTest(mutation=mutation):
                mutant = copy.deepcopy(child)
                ref = next(n['result_ref'] for n in ast_nodes(mutant['condition_ast']) if 'result_ref' in n)
                if mutation == 'effect': ref['allowed_effect'] = 'FABRICATED_RESULT'
                elif mutation == 'dependency': mutant['external_dependencies'].remove(ref['producer_stable_provision_id'])
                else: ref['allowed_effects'] = [ref['allowed_effect']]
                with self.assertRaisesRegex(AssertionError, message):
                    verify_result_references([mutant], self.rows)

    def test_result_validation_preserves_nested_compound_and_temporal_effects(self):
        producer = {'stable_provision_id': 'P', 'provision_version_id': 'P:v1',
                    'effective_from': '2025-01-01', 'effective_to_exclusive': '2026-01-01',
                    'condition_ast': {'otherwise': {'effect': 'OLD'}}}
        current = {**producer, 'provision_version_id': 'P:v2', 'effective_from': '2026-01-01',
                   'effective_to_exclusive': '', 'condition_ast': {'otherwise': {'effect': 'A; B'}}}
        consumer = {**current, 'stable_provision_id': 'C', 'provision_version_id': 'C:v1',
                    'external_dependencies': ['P'], 'condition_ast': {'all_of': [{'not': {
                        'result_ref': {'producer_stable_provision_id': 'P', 'allowed_effect': 'A; B'}}}]}}
        verify_result_references([consumer], [producer, current])
        ref = consumer['condition_ast']['all_of'][0]['not']['result_ref']
        for bad in ['A', 'OLD']:
            ref['allowed_effect'] = bad
            with self.assertRaisesRegex(AssertionError, 'not emitted'):
                verify_result_references([consumer], [producer, current])
        ref['allowed_effect'] = 'A; B'
        with self.assertRaisesRegex(AssertionError, 'no overlapping'):
            verify_result_references([consumer], [producer])
        with self.assertRaisesRegex(AssertionError, 'producer missing'):
            verify_result_references([consumer], [])

    def test_jurisdiction_and_b_generators_reject_invalid_result_before_writes(self):
        with tempfile.TemporaryDirectory(prefix='cordon-result-regression-') as tmp:
            root = Path(tmp)
            for logical in verifier.STAGE_A_LOGICAL:
                path = root / logical
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verifier.ROOT / logical, path)
            a = root / verifier.STAGE_A_LOGICAL[1]
            out = root / 'jurisdiction-generated'
            with patch.multiple(jurisdiction_generator, ROOT=root, AUTHORING=a, OUT=out), contextlib.redirect_stdout(io.StringIO()):
                jurisdiction_generator.main()
                before = {p.name: p.read_bytes() for p in out.iterdir()}
                rows = json.loads(a.read_text())
                child = next(r for r in rows if r['stable_provision_id'] == 'PUG-DGR1075-2025:§4.3.2:almond-pre-removal-vector-treatment')
                ref = next(n['result_ref'] for n in ast_nodes(child['condition_ast']) if 'result_ref' in n)
                ref['allowed_effect'] = 'FABRICATED_RESULT'
                a.write_text(json.dumps(rows))
                with self.assertRaisesRegex(AssertionError, 'not emitted'):
                    jurisdiction_generator.main()
                self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})
            with self.assertRaisesRegex(AssertionError, 'not emitted'):
                jurisdiction_verifier.verify(a, False, False)
            b_out = root / 'b-generated'
            b_out.mkdir()
            sentinel = b_out / 'clocks.csv'
            sentinel.write_text('previous output')
            output = io.StringIO()
            with patch.multiple(generator, ROOT=root, OUT=b_out), contextlib.redirect_stdout(output):
                with self.assertRaises(SystemExit): generator.main()
            self.assertIn('not emitted', output.getvalue())
            self.assertEqual(sentinel.read_text(), 'previous output')
            self.assertEqual(list(b_out.iterdir()), [sentinel])


class Round5Repairs(unittest.TestCase):
    """Source-led counterexamples over A/B, not a Stage C evaluator."""

    def setUp(self):
        self.rows = [r for p in verifier.STAGE_A_LOGICAL
                     for r in json.loads((verifier.ROOT / p).read_text())]
        self.a = {r['provision_version_id']: r for r in self.rows}
        self.b = json.loads(verifier.B.read_text())

    @staticmethod
    def key(atom):
        return json.dumps(atom, sort_keys=True)

    @staticmethod
    def ref(sid, effect):
        return {'result_ref': {'producer_stable_provision_id': sid, 'allowed_effect': effect}}

    def result(self, ast, facts):
        if 'route_table' not in ast:
            return StageARepairs.condition(ast, facts)
        values = [StageARepairs.condition(r['when'], facts) for r in ast['route_table']]
        found = {r['effect'] for r, value in zip(ast['route_table'], values) if value is True}
        if not found and all(value is False for value in values):
            found.add(ast['otherwise']['effect'])
        return found

    def test_retention_changes_operative_removal_not_baseline_membership(self):
        def check(ast):
            facts = {k: False for k in StageARepairs.facts(ast)}
            for atom in (self.ref('EU-2020-1201:12', 'ERADICATION_MEASURES_APPLY'),
                         {'predicate': 'an infected zone established for the purpose of eradication exists'},
                         {'provision_ref': 'EU-2020-1201:7(1)(c)'}):
                facts[self.key(atom)] = True
            retained = self.key(self.ref('EU-2020-1201:7(3)', 'RETENTION_DEROGATION_EXERCISED'))
            for granted, effect in ((False, 'IMMEDIATE_REMOVAL_REQUIRED'),
                                    (True, 'NO_ARTICLE_7_1_REMOVAL_DUTY')):
                facts[retained] = granted
                self.assertEqual(self.result(ast, facts), {effect})

        for version in ('v1', 'v2'):
            ast = self.a['EU-2020-1201:7(1):' + version]['condition_ast']
            check(ast)
            mutant = copy.deepcopy(ast)
            mutant['route_table'][0]['when']['all_of'].pop()
            with self.assertRaises(AssertionError):
                check(mutant)
        for point in 'abcd':
            self.assertIn('baseline', self.a[f'EU-2020-1201:7(1)({point}):v1']['true_effect'])

    def test_point_e_deferral_and_negative_test_reach_removal_population(self):
        deferred = self.ref('EU-2020-1201:7(1)(e)-sub2',
                            'IMMEDIATE_SAMPLING_DEFERRED; ANNUAL_ARTICLE_10_SURVEY_APPLIES')
        negative = self.ref('EU-2020-1201:7(1)(e)-sub1', 'POINT_E_PLANT_NOT_REMOVED')

        def check(ast):
            for defer, tested_negative, expected in (
                    (False, False, 'POINT_E_REMOVAL_POPULATION'),
                    (True, False, 'NOT_IN_POINT_E_POPULATION'),
                    (False, True, 'NOT_IN_POINT_E_POPULATION')):
                facts = StageARepairs.facts(ast)
                facts[self.key(deferred)] = defer
                facts[self.key(negative)] = tested_negative
                self.assertEqual(self.result(ast, facts), {expected})

        ast = self.a['EU-2020-1201:7(1)(e):v2']['condition_ast']
        check(ast)
        mutant = copy.deepcopy(ast)
        mutant['route_table'][0]['when']['all_of'].remove({'not': deferred})
        with self.assertRaises(AssertionError):
            check(mutant)
        old = self.a['EU-2020-1201:7(1)(e):v1']
        self.assertNotIn('sub2', json.dumps(old['condition_ast']))
        self.assertEqual(old['effective_to_exclusive'], '2024-10-17')
        # An infected point-(a) plant remains removable independently of point (e).
        parent = self.a['EU-2020-1201:7(1):v2']['condition_ast']
        facts = {k: False for k in StageARepairs.facts(parent)}
        for atom in (self.ref('EU-2020-1201:12', 'ERADICATION_MEASURES_APPLY'),
                     {'predicate': 'an infected zone established for the purpose of eradication exists'},
                     {'provision_ref': 'EU-2020-1201:7(1)(a)'}):
            facts[self.key(atom)] = True
        self.assertEqual(self.result(parent, facts), {'IMMEDIATE_REMOVAL_REQUIRED'})

    def test_scientific_retention_does_not_exempt_removed_material(self):
        ast = self.a['EU-2020-1201:16(1):v1']['condition_ast']
        retained = self.key(self.ref('EU-2020-1201:13(2)', 'SCIENTIFIC_NON_REMOVAL_DEROGATION_EXERCISED'))
        removed = self.key({'predicate': 'the plant or parts concerned have been removed'})
        for retain, is_removed, expected in ((True, False, False), (True, True, True), (False, False, True)):
            facts = StageARepairs.facts(ast)
            facts[retained], facts[removed] = retain, is_removed
            self.assertIs(self.result(ast, facts), expected)
        for article in ('9', '16'):
            ast = self.a[f'EU-2020-1201:{article}(2):v1']['condition_ast']
            scope = self.key({'provision_ref': f'EU-2020-1201:{article}(1)'})
            facts = {k: False for k in StageARepairs.facts(ast)}
            self.assertEqual(self.result(ast, facts), {f'NO_ARTICLE_{article}_2_DESTRUCTION_ROUTE'})
            facts[scope] = True
            self.assertEqual(self.result(ast, facts), {f'FULL_DESTRUCTION_UNDER_ARTICLE_{article}_1'})
            self.assertIn('LIMITED_DESTRUCTION_DECIDED', next(iter(self.result(ast, StageARepairs.facts(ast)))))

    def test_removal_clocks_and_regional_consumers_use_operative_result(self):
        clocks = {c['clock_id']: c for c in self.b['clocks']}
        for cid in ('B-CLK-EU-7(1)-v1-immediate-removal',
                    'B-CLK-EU-8(1)-v1-treatment-before-and-during-removal',
                    'B-CLK-EU-8(1)-v2-treatment-before-and-during-removal'):
            self.assertEqual(clocks[cid]['anchor']['effect'], 'IMMEDIATE_REMOVAL_REQUIRED')
        for cid in ('B-CLK-DDS31-eradication-48h', 'B-CLK-DDS45-eradication-48h'):
            self.assertIn('IMMEDIATE_REMOVAL_REQUIRED', clocks[cid]['applies_when'])
        sampling = clocks['B-CLK-EU-7(1)(e)-v2-immediate-sampling']
        self.assertIn('IMMEDIATE_SAMPLING_DEFERRED', sampling['applies_when'])
        self.assertNotIn('sub2', str(clocks['B-CLK-EU-7(1)(e)-v1-immediate-sampling']['applies_when']))
        operative = self.ref('EU-2020-1201:7(1)', 'IMMEDIATE_REMOVAL_REQUIRED')
        for vid in ('PUG-LR4-2017:Art.5(3):post-LR45-v2',
                    'REG-PUGLIA-U181-DIR-2025-00045:eradication-removal-population-support:v1'):
            self.assertIn(operative, list(ast_nodes(self.a[vid]['condition_ast'])))
        for vid in ('REG-PUGLIA-U181-DIR-2025-00045:treatment-removal-sequence:v1',
                    'REG-PUGLIA-U181-DIR-2022-00031:eradication-treatment-removal-sequence:v1'):
            ast = self.a[vid]['condition_ast']
            facts = StageARepairs.facts(ast)
            facts[self.key(operative)] = False
            self.assertEqual(self.result(ast, facts), {'NO_ERADICATION_REMOVAL_SEQUENCE_FOR_THIS_PLANT'})

    def test_regional_almond_treatment_does_not_require_eu_zone(self):
        ast = self.a['PUG-DGR1075-2025:§4.3.2:almond-pre-removal-vector-treatment:v1']['condition_ast']

        def check(tree):
            facts = {k: False for k in StageARepairs.facts(tree)}
            facts[self.key(self.ref('PUG-DGR1075-2025:§4.3.2:mandatory-almond-400m', 'PLAN_ONLY_EFFECT_APPLIES'))] = True
            facts[self.key({'predicate': 'source pre-removal-treatment exception does not apply'})] = True
            self.assertEqual(self.result(tree, facts), {'CHEMICAL_VECTOR_TREATMENT_REQUIRED_BEFORE_ALMOND_REMOVAL'})

        check(ast)
        mutant = copy.deepcopy(ast)
        mutant['route_table'][0]['when']['all_of'].append({'provision_ref': 'EU-2020-1201:8(1)'})
        with self.assertRaises(AssertionError):
            check(mutant)
        self.assertIn('PRESERVE_EFFECTIVE_EU_ARTICLE_8_DUTY', json.dumps(ast))

    def test_plan_routes_follow_proven_legal_consequence_not_approval_proof(self):
        from itertools import product
        names = ('decisive substantive inapplicability fact proven',
                 'a proven defect legally defeats the authority or operativity of this particular regional measure',
                 'a proven defect leaves the operativity of this particular regional measure legally unsettled')
        ids = [r['provision_version_id'] for r in self.rows
               if any(route.get('effect') == 'PLAN_ONLY_EFFECT_APPLIES'
                      for route in r['condition_ast'].get('route_table', []))]
        self.assertEqual(len(ids), 6)
        for vid in ids:
            ast = self.a[vid]['condition_ast']
            for sub, defeated, unsettled in product((False, True), repeat=3):
                facts = StageARepairs.facts(ast)
                for name, value in zip(names, (sub, defeated, unsettled)):
                    facts[self.key({'predicate': name})] = value
                expected = ('PLAN_ONLY_EFFECT_SUBSTANTIVELY_NOT_APPLICABLE' if sub else
                            'PLAN_ONLY_EFFECT_AUTHORITY_NOT_ESTABLISHED' if defeated else
                            'PLAN_ONLY_EFFECT_VALIDITY_ADJUDICATION_REQUIRED' if unsettled else
                            'PLAN_ONLY_EFFECT_APPLIES')
                self.assertEqual(self.result(ast, facts), {expected}, vid)
                # A missing approval record is not one of the legally consequential predicates.
                facts[self.key({'predicate': 'approval evidence available'})] = None
                self.assertEqual(self.result(ast, facts), {expected}, vid)
            self.assertNotIn('evidence proves legally required approval/adoption absent or outside scope', json.dumps(ast))

    def test_root_substep_cannot_complete_unfinished_destruction(self):
        ast = self.a['REG-PUGLIA-U181-DIR-2022-00031:destruction-root-wood-completion:v1']['condition_ast']

        def check(tree):
            facts = {k: False for k in StageARepairs.facts(tree)}
            for name in ('plant removed under the operative branch',
                         'competent Article 9(2)/16(2) limited-destruction decision',
                         'required above-ground destruction of branches and foliage completed',
                         'wood stripped of branches and foliage retained by the owner under the source procedure',
                         'an applicable destruction performance condition is proven unsatisfied',
                         'field impracticability of whole-root extirpation',
                         'competent limited-destruction decision',
                         'root system devitalized with adequate phytosanitary treatment'):
                facts[self.key({'predicate': name})] = True
            self.assertEqual(self.result(tree, facts), {'DESTRUCTION_NOT_COMPLETE'})
            facts[self.key({'predicate': 'retained wood receives the required phytosanitary treatment'})] = True
            facts[self.key({'predicate': 'an applicable destruction performance condition is proven unsatisfied'})] = False
            self.assertEqual(self.result(tree, facts), {'LIMITED_DESTRUCTION_ROUTE_COMPLETE'})
            facts[self.key({'predicate': 'required above-ground destruction of branches and foliage completed'})] = False
            facts[self.key({'predicate': 'an applicable destruction performance condition is proven unsatisfied'})] = True
            self.assertEqual(self.result(tree, facts), {'DESTRUCTION_NOT_COMPLETE'})
            facts[self.key({'predicate': 'required above-ground destruction of branches and foliage completed'})] = True
            facts[self.key({'predicate': 'an applicable destruction performance condition is proven unsatisfied'})] = False
            # Destroyed above-ground material plus devitalised roots needs no retained wood.
            facts[self.key({'predicate': 'wood stripped of branches and foliage retained by the owner under the source procedure'})] = False
            facts[self.key({'predicate': 'retained wood receives the required phytosanitary treatment'})] = False
            facts[self.key({'predicate': 'no wood retained'})] = True
            self.assertEqual(self.result(tree, facts), {'LIMITED_DESTRUCTION_ROUTE_COMPLETE'})

        check(ast)
        mutant = copy.deepcopy(ast)
        mutant['route_table'].append({'when': {'all_of': [
            {'predicate': name} for name in ('field impracticability of whole-root extirpation',
                                            'competent limited-destruction decision',
                                            'root system devitalized with adequate phytosanitary treatment')]},
            'effect': 'LIMITED_DESTRUCTION_ROUTE_COMPLETE'})
        with self.assertRaises(AssertionError):
            check(mutant)

    def test_post_finding_populations_and_sequence_are_not_annual_sample_adequacy(self):
        dds, dgr = 'REG-PUGLIA-U181-DIR-2025-00045:', 'PUG-DGR1075-2025:'
        for part in ('pest-free-buffer', 'containment'):
            row = self.a[dds + 'post-finding-' + part + '-sampling:v1']
            facts = StageARepairs.facts(row['condition_ast'])
            facts[self.key({'predicate': 'annual statistical survey adequate'})] = True
            self.assertTrue(any('SAMPLING_REQUIRED' in effect for effect in self.result(row['condition_ast'], facts)))
            self.assertNotIn('removal completed', json.dumps(row['condition_ast']))
            self.assertIn('400 m', row['true_effect'])
        row = self.a[dgr + '§4.2.1:pest-free-extent-investigation:v1']
        for pest_free, initial_done, required in ((True, True, True), (False, True, False), (True, False, False)):
            facts = StageARepairs.facts(row['condition_ast'])
            facts[self.key({'predicate': 'the infected-plant finding arose in a pest-free area'})] = pest_free
            facts[self.key({'predicate': 'the initial 400 m-band surveillance has been completed'})] = initial_done
            self.assertEqual('PEST_FREE_FOLLOW_ON_EXTENT_INVESTIGATION_REQUIRED' in self.result(row['condition_ast'], facts), required)
        parameters = {p['parameter_id']: p for p in self.b['parameters']}
        outer = parameters['B-PAR-DDS45-post-finding-containment-outer-band-400m']
        self.assertEqual((outer['kind'], outer['value'], outer['unit']), ('exact', '400', 'm'))
        self.assertIn('50 m', outer['scope']['purpose'])
        st53 = self.a[dgr + '§4.2.2:st53-post-finding-sampling:v1']
        self.assertEqual(st53['effective_from'], '2025-07-29')
        self.assertIn('independently required', st53['true_effect'])
        self.assertIn('every hectare', self.a[dgr + '§4.2.1:post-finding-hectare-surveillance:v1']['true_effect'])

    def test_current_points_to_acceptance_owner_without_a_copied_map(self):
        current = json.loads((verifier.ROOT / 'state/CURRENT.json').read_text())
        self.assertNotIn('semantic_acceptance', current['stages']['B'])
        self.assertEqual(current['stages']['B']['canonical']['path'], str(verifier.B.relative_to(verifier.ROOT)))


class Round6Repairs(unittest.TestCase):
    """Family-scoped source counterexamples on canonical and emitted consumers."""

    setUp = Round5Repairs.setUp
    key = staticmethod(Round5Repairs.key)
    ref = staticmethod(Round5Repairs.ref)
    result = Round5Repairs.result

    def surfaces(self, row):
        yield row['condition_ast']
        folder = 'regulation/stage-a' if row['instrument_id'] == 'EU-2020-1201' else 'regulation/jurisdiction/generated'
        with (verifier.ROOT / folder / 'provision-versions.csv').open(newline='') as handle:
            emitted = next(r for r in csv.DictReader(handle) if r['provision_version_id'] == row['provision_version_id'])
        # The CSV owns no AST column; check its actual explanatory consumer fields.
        for field in ('true_effect', 'false_effect', 'semantic_note'):
            self.assertEqual(emitted[field], row[field])
        graphs = json.loads((jurisdiction_generator.OUT / 'condition-graph.json').read_text())['graphs']
        for graph in graphs:
            if graph['provision_version_id'] == row['provision_version_id']:
                yield graph['expression']

    def ordinary(self, ast):
        facts = StageARepairs.facts(ast)
        for node in ast_nodes(ast):
            if 'predicate' in node and any(s in node['predicate'] for s in ('proven', 'evidence missing', 'not yet completed')):
                facts[self.key(node)] = False
            if 'result_ref' in node:
                facts[self.key(node)] = node['result_ref']['allowed_effect'] in {
                    'CONTAINMENT_SUBSTITUTES_FOR_ERADICATION', 'ARTICLE_13_BASELINE_REMOVAL_POPULATION',
                    'ARTICLE_13_REMOVAL_STANDS', 'IMMEDIATE_REMOVAL_REQUIRED', 'ARTICLE_4_DEMARCATION_DUTY_STANDS'}
        return facts

    def test_destruction_family_requires_the_whole_selected_performance(self):
        rows = [r for r in self.rows if 'root-wood-completion' in r['stable_provision_id']]
        self.assertEqual(len(rows), 3)
        for row in rows:
            for ast in self.surfaces(row):
                def check(tree):
                    limited = next(r for r in tree['route_table'] if 'LIMITED_DESTRUCTION' in r['effect'])
                    facts = self.ordinary(tree)
                    # This physical-performance fixture assumes the limited route was chosen.
                    facts[self.key(self.ref('EU-2020-1201:16(2)', 'LIMITED_DESTRUCTION_DECIDED; WOOD_TREATED_UNDER_ARTICLE_14_1; ROOTS_REMOVED_OR_DEVITALISED'))] = True
                    for name in ('whole-root extirpation with in-situ shredding or burning of the plant and its parts completed',
                                 'no wood retained', 'root system removed'):
                        facts[self.key({'predicate': name})] = False
                    facts[self.key({'predicate': 'field impracticability of whole-root extirpation'})] = True
                    self.assertEqual(self.result(tree, facts), {limited['effect']})
                    for limb in ('required above-ground destruction of branches and foliage completed',
                                 'field impracticability of whole-root extirpation'):
                        bad = dict(facts)
                        bad[self.key({'predicate': limb})] = False
                        bad[self.key({'predicate': 'an applicable destruction performance condition is proven unsatisfied'})] = True
                        incomplete = self.result(tree, bad)
                        self.assertTrue(incomplete)
                        self.assertTrue(all('NOT_COMPLETE' in effect for effect in incomplete))
                        unknown = dict(facts); unknown[self.key({'predicate': limb})] = None
                        self.assertNotIn(limited['effect'], self.result(tree, unknown))
                    # Retaining wood is optional; roots may be left only under the source exception.
                    facts[self.key({'predicate': 'no wood retained'})] = True
                    for node in ast_nodes(tree):
                        if 'predicate' in node and ('wood retained under' in node['predicate'] or 'retained wood receives' in node['predicate']):
                            facts[self.key(node)] = False
                    self.assertEqual(self.result(tree, facts), {limited['effect']})
                check(ast)
                mutant = copy.deepcopy(ast)
                for node in ast_nodes(mutant):
                    if node.get('predicate') == 'required above-ground destruction of branches and foliage completed':
                        node['predicate'] = 'root system devitalized with adequate phytosanitary treatment'
                with self.assertRaises(AssertionError): check(mutant)

    def test_execution_record_and_verification_do_not_ignore_material_defects(self):
        rows = [r for r in self.rows if r['instrument_id'] == 'REG-PUGLIA-U181-DIR-2025-00045'
                and (r['stable_provision_id'].endswith('execution-evidence') or 'execution-verification' in r['stable_provision_id'])]
        self.assertEqual(len(rows), 4)
        for row in rows:
            for ast in self.surfaces(row):
                defect = next(n for n in ast_nodes(ast) if 'predicate' in n and 'legally defeats this official execution' in n['predicate'])
                facts = self.ordinary(ast)
                ordinary = self.result(ast, facts)
                self.assertTrue(ordinary)
                facts[self.key({'predicate': 'separate personnel-register evidence available'})] = None
                self.assertEqual(self.result(ast, facts), ordinary)
                facts[self.key(defect)] = True
                bad = self.result(ast, facts)
                if isinstance(bad, set):
                    self.assertFalse(any('EVIDENCE_COMPLETE' in e or e.startswith('VERIFY_') for e in bad))
                else: self.assertFalse(bad)
                mutant = copy.deepcopy(ast)
                for node in ast_nodes(mutant):
                    if node.get('not') == defect:
                        node.clear(); node.update({'predicate': 'unqualified proof permitted'})
                facts[self.key({'predicate': 'unqualified proof permitted'})] = True
                broken = self.result(mutant, facts)
                self.assertTrue(broken is True or any('EVIDENCE_COMPLETE' in e or e.startswith('VERIFY_') for e in broken))
                # A record defect has not rewritten the physical execution fact.
                for name in ('eradication execution occurred', 'containment execution occurred'):
                    if self.key({'predicate': name}) in facts: self.assertTrue(facts[self.key({'predicate': name})])

    def test_diagnostic_commands_expire_when_their_source_step_completes(self):
        rows = [r for r in self.rows if 'doubtful-result-route' in r['stable_provision_id'] or 'inconclusive-result-routing' in r['stable_provision_id']]
        self.assertEqual(len(rows), 3)
        for row in rows:
            for ast in self.surfaces(row):
                facts = {k: False for k in StageARepairs.facts(ast)}
                if 'DTU39' in row['instrument_id']:
                    for name in ('the initial authorized result is inconclusive or doubtful', 'the repeated result is inconclusive', 'a further result is inconclusive'):
                        facts[self.key({'predicate': name})] = True
                    expected = {'ASSIGN_SAMPLE_NOT_DETECTED_OR_ABSENT_AND_RESERVE_FURTHER_INVESTIGATION_DECISION_TO_THE_REGIONAL_SERVICE'}
                else:
                    # Earlier doubtful results remain true, but every analytical step is complete.
                    facts = self.ordinary(ast)
                    facts[self.key({'predicate': 'latest completed analytical stage resolves positive or negative on valid evidence'})] = True
                    expected = {'TERMINATE_IN_RESULTING_ANALYTICAL_CLASS'}
                self.assertEqual(self.result(ast, facts), expected)
                # Every staged command carries its own outstanding-performance condition.
                commands = [r for r in ast['route_table'] if any(r['effect'].startswith(s) for s in
                            ('REPEAT_', 'NEW_POOL_', 'TEST_', 'SEND_', 'CONFIRM_USING_', 'RESAMPLE_OR_'))]
                self.assertTrue(commands)
                for command in commands:
                    self.assertIn('not yet completed', json.dumps(command['when']))
                    # Keep that step's original result facts true while varying completion.
                    probe = {k: False for k in StageARepairs.facts(ast)}
                    for atom in ast_nodes(command['when']):
                        if set(atom) & {'predicate', 'provision_ref', 'result_ref'}:
                            probe[self.key(atom)] = True
                    terminal = {'predicate': 'latest completed analytical stage resolves positive or negative on valid evidence'}
                    probe[self.key(terminal)] = False
                    unfinished = next(n for n in ast_nodes(command['when']) if 'not yet completed' in n.get('predicate', ''))
                    self.assertIs(StageARepairs.condition(command['when'], probe), True)
                    probe[self.key(unfinished)] = False
                    self.assertIs(StageARepairs.condition(command['when'], probe), False)
                    wrong = copy.deepcopy(command['when'])
                    for n in ast_nodes(wrong):
                        if n == unfinished: n.clear(); n.update({'predicate': 'ignore completion'})
                    probe[self.key({'predicate': 'ignore completion'})] = True
                    self.assertIs(StageARepairs.condition(wrong, probe), True)

    def test_retention_common_population_covers_all_three_grounds(self):
        rows = [r for r in self.rows if r['stable_provision_id'] == 'EU-2020-1201:7(3)']
        self.assertEqual(len(rows), 3)
        for row in rows:
            for ast in self.surfaces(row):
                atoms = list(ast_nodes(ast))
                population = next(n for n in atoms if 'specified plant' in n.get('predicate', ''))
                facts = StageARepairs.facts(ast)
                for n in atoms:
                    if n.get('provision_ref') in ('EU-2020-1201:7(1)(a)', 'EU-2020-1201:7(1)(e)'):
                        facts[self.key(n)] = False
                facts[self.key(population)] = False
                self.assertNotIn('RETENTION_DEROGATION_EXERCISED', self.result(ast, facts))
                mutant = copy.deepcopy(ast)
                for n in ast_nodes(mutant):
                    if n == population: n.clear(); n.update({'predicate': 'population restriction removed'})
                facts[self.key({'predicate': 'population restriction removed'})] = True
                self.assertIn('RETENTION_DEROGATION_EXERCISED', self.result(mutant, facts))
                facts[self.key(population)] = True
                self.assertIn('RETENTION_DEROGATION_EXERCISED', self.result(ast, facts))
                if row['provision_version_id'].endswith('v3'):
                    grounds = next(n['any_of'] for n in atoms if 'any_of' in n and all('predicate' in x for x in n['any_of']))
                    self.assertEqual(len(grounds), 3)
                    for chosen in grounds:
                        for g in grounds: facts[self.key(g)] = g == chosen
                        self.assertIn('RETENTION_DEROGATION_EXERCISED', self.result(ast, facts))

    def test_demarcation_clocks_consume_the_qualified_plant_finding(self):
        clocks = [c for c in self.b['clocks'] if c['consumer_decision'] == 'EU-2020-1201:4(1)']
        self.assertEqual(len(clocks), 2)
        for clock in clocks:
            row = self.a[clock['producer_provision_version_id']]
            for ast in self.surfaces(row):
                facts = StageARepairs.facts(ast)
                plant = {'predicate': 'presence officially confirmed in plants'}
                default = self.ref('EU-2020-1201:5(3)', 'ARTICLE_4_DEMARCATION_DUTY_STANDS')
                self.assertIs(self.result(ast, facts), True)
                for qualifier in (plant, default):
                    bad = dict(facts); bad[self.key(qualifier)] = False
                    self.assertIs(self.result(ast, bad), False)
                    mutant = copy.deepcopy(ast)
                    mutant['all_of'].remove(qualifier)
                    self.assertIs(self.result(mutant, bad), True)
            self.assertEqual(clock['anchor']['medium'], 'plant')
            self.assertIn('ARTICLE_4_DEMARCATION_DUTY_STANDS', clock['applies_when'])
            self.assertIn('NO_IMMEDIATE_DEMARCATION_DECIDED', clock['applies_when'])

    def test_temporal_corrections_preserve_the_independent_regional_duty(self):
        old = self.a['PUG-LR4-2017:Art.4(2):pre-LR45-v1']
        self.assertNotIn('EU-2020-1201:1(d)', old['external_dependencies'])
        treatment = self.a['PUG-LR4-2017:Art.5(4):pre-LR45-v1']
        self.assertIn('EU-2020-1201:8(2)', treatment['higher_authority_dependencies'])
        self.assertNotIn('EU-2020-1201:8(2)(a)', treatment['external_dependencies'])
        regional = self.a['PUG-LR4-2017:Art.4(6):follow-up:v1']
        for ast in self.surfaces(regional):
            facts = StageARepairs.facts(ast)
            facts[self.key({'provision_ref': 'EU-2020-1201:2(4a)'})] = False
            self.assertIs(self.result(ast, facts), True)  # e.g. a 2022 finding
        parameters = {p['parameter_id']: p for p in self.b['parameters']}
        self.assertEqual(parameters['B-PAR-LR4-5(4)-pre-LR45-vector-radius-100m']['dependencies'],
                         treatment['higher_authority_dependencies'])
        self.assertNotIn('B-PAR-EU-5(1)(c)-v1-400m-higher-risk', parameters)
        successor = parameters['B-PAR-EU-5(1)(c)-v2-400m-higher-risk']
        self.assertEqual(self.a[successor['producer_provision_version_id']]['effective_from'], '2023-01-01')
        retired = next(d for d in self.b['dispositions'] if d['provision_version_id'] == 'EU-2020-1201:5(1)(c):v1'
                       and (d.get('expression') or '').startswith('the first 400 m'))
        self.assertEqual(retired['disposition'], 'not_a_parameter')

    def test_lab_limits_keep_actor_receipt_endpoint_and_version(self):
        clocks = {c['clock_id']: c for c in self.b['clocks']}
        expected = [('DDS45-positive-analysis-registration-return', '7', '2025-03-26', True),
                    ('DDS45-negative-analysis-registration-return', '10', '2025-03-26', True),
                    ('DDS45-cnr-analysis-return', '3', '2025-03-26', True),
                    ('DDS31-analysis-registration', '5', '2022-05-13', False),
                    ('DDS31-cnr-confirmation-return', '5', '2022-05-13', True)]
        for suffix, magnitude, start, communicates in expected:
            c = clocks['B-CLK-' + suffix]
            self.assertEqual((c['magnitude'], c['unit'], c['legal_duty_owner']), (magnitude, 'working_days', 'OFFICIAL_LABORATORY'))
            self.assertIn('receipt', c['anchor']['event'])
            self.assertEqual('communicated' in c['completion']['ref'], communicates)
            row = self.a[c['producer_provision_version_id']]
            self.assertEqual(row['effective_from'], start)
            self.assertEqual(row['effective_to_exclusive'], '2025-03-26' if 'DDS31' in suffix else '')
            self.assertTrue(verifier.clock_value_matches(c))
            mutant = copy.deepcopy(c); mutant['magnitude'] = '4'
            self.assertFalse(verifier.clock_value_matches(mutant))
        order = clocks['B-CLK-DDS31-communication-after-registration']
        self.assertEqual(order['kind'], 'ordering_constraint')
        self.assertIsNone(order['magnitude'])
        self.assertIn('database registration', order['anchor']['event'])
        self.assertIn('doubtful', clocks['B-CLK-DDS45-cnr-analysis-return']['applies_when'])
        self.assertIn('B-CLK-EU-625-38(1)-immediate-result-notification', clocks)

    def test_retired_gate_prose_is_absent_across_the_affected_families(self):
        ids = ('PUG-LR4-2017:Art.6(1)', 'REG-PUGLIA-U181-DIR-2024-00158:containment-selection',
               'IT-DM-2022-XYLELLA-PLAN:§6.4:no-demarcation-two-year-follow-up',
               'IT-DM-348260-2026-XYLELLA-PLAN:§8.5:no-demarcation-surveillance',
               'IT-DM-2022-XYLELLA-PLAN:§6.6.2:containment-vector-treatment-band-5km',
               'IT-DM-2022-XYLELLA-PLAN:§6.7:containment-surveillance-band-5km')
        for row in self.rows:
            if row['stable_provision_id'] not in ids: continue
            prose = ' '.join(row.get(k, '') for k in ('true_effect', 'false_effect', 'semantic_note'))
            for retired in ('legal-effect gate', 'block national procedural-compliance conclusions and plan-only effects',
                            'missing stricter-measure authority evidence remains unresolved', 'second year’s additional national legal effect is unresolved'):
                self.assertNotIn(retired, prose, row['provision_version_id'])

    def test_master_partition_does_not_impose_first_match_order(self):
        rows = json.loads(jurisdiction_verifier.DEFAULT_AUTHORING.read_text())
        for row in rows:
            if row['stable_provision_id'] == 'PUG-LR4-2017:Art.6(1)':
                routes = row['condition_ast']['route_table']; routes[0], routes[1] = routes[1], routes[0]
        original = Path.read_text
        def redirected(path, *args, **kwargs):
            return json.dumps(rows) if path == jurisdiction_verifier.DEFAULT_AUTHORING else original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', redirected):
            jurisdiction_verifier.verify(jurisdiction_verifier.DEFAULT_AUTHORING, False, False)


class Round7Repairs(unittest.TestCase):
    """Approved handoff, dispatch and readiness boundaries; no new workflow."""

    setUp = Round5Repairs.setUp
    key = staticmethod(Round5Repairs.key)
    result = Round5Repairs.result
    surfaces = Round6Repairs.surfaces

    def test_arif_calendar_is_a_duty_not_an_executor_selection_gate(self):
        row = self.a['REG-PUGLIA-U181-DIR-2025-00045:executor-selection:v1']
        duty = 'ARIF_DETAILED_REMOVAL_CALENDAR_COMMUNICATION_TO_OSSERVATORIO_REQUIRED'
        self.assertIn('communicate the detailed removal calendar to the Osservatorio', row['true_effect'])
        self.assertIn('communication to the Osservatorio', row['evidence_contract'])
        self.assertIn('calendario dettagliato', row['source_quote'])
        self.assertIn(verifier.norm(row['source_quote']),
                      verifier.norm((verifier.ROOT / row['source_paths']).read_text()))
        for ast in self.surfaces(row):
            # Either ARIF assignment activates the handoff duty without requiring
            # prior communication, acknowledgement, owner default or physical removal.
            for route in ast['route_table'][:3]:
                facts = {key: False for key in StageARepairs.facts(ast)}
                facts.update({key: True for key in StageARepairs.facts(route['when'])})
                effects = self.result(ast, facts)
                self.assertIn(route['effect'], effects)
                self.assertEqual(any(duty in effect for effect in effects), 'ARIF' in route['effect'])
                self.assertFalse(any('calendar' in atom.lower() for atom in StageARepairs.facts(route['when'])))
        dispositions = [d for d in self.b['dispositions'] if d['provision_version_id'] == row['provision_version_id']]
        self.assertEqual(len(dispositions), 1)
        self.assertEqual(dispositions[0]['disposition'], 'not_a_clock')
        self.assertIn('calendario dettagliato', dispositions[0]['expression'])

    def test_dds45_prompt_dispatch_stays_separate_from_cnr_receipt(self):
        clocks = {c['clock_id']: c for c in self.b['clocks']}
        dispatch = clocks['B-CLK-DDS45-prompt-positive-cnr-transfer']
        self.assertEqual(dispatch['completion'],
                         {'kind': 'record', 'ref': 'positive sample dispatched promptly to CNR-IPSP'})
        self.assertIn('inviati con sollecitudine', dispatch['source_phrase'])
        with (generator.OUT / 'clocks.csv').open(newline='') as handle:
            emitted = next(c for c in csv.DictReader(handle) if c['clock_id'] == dispatch['clock_id'])
        self.assertEqual(json.loads(emitted['completion']), dispatch['completion'])
        cnr = [c for c in clocks.values() if c['producer_provision_version_id'] == dispatch['producer_provision_version_id']
               and c['clock_id'] != dispatch['clock_id']]
        self.assertEqual(len(cnr), 1)
        self.assertIn('receipt', json.dumps(cnr[0]['anchor']).lower())
        # The predecessor also requires prompt delivery: no mechanical back-port.
        self.assertIn('delivered', clocks['B-CLK-DDS31-prompt-confirmation-transfer']['completion']['ref'])

    def test_treatment_and_wait_establish_readiness_not_removed_plants(self):
        suffixes = [('2025-00045:treatment-removal-sequence:v1', 'FLIGHT_SEASON'),
                    ('2025-00045:containment-treatment-removal-sequence:v1', 'CONTAINMENT'),
                    ('2022-00031:eradication-treatment-removal-sequence:v1', 'ERADICATION'),
                    ('2022-00031:containment-treatment-removal-sequence:v1', 'CONTAINMENT')]
        for suffix, branch in suffixes:
            row = self.a['REG-PUGLIA-U181-DIR-' + suffix]
            expected = branch + '_TREATMENT_AND_WAIT_SATISFIED_FOR_REMOVAL'
            for ast in self.surfaces(row):
                facts = {key: False for key in StageARepairs.facts(ast)}
                first = ast['route_table'][0]['when']
                facts.update({key: True for key in StageARepairs.facts(first)})
                # No performed-removal fact is supplied; the plant can still stand.
                self.assertEqual(self.result(ast, facts), {expected})
                for atom in StageARepairs.facts(first):
                    with self.subTest(owner=suffix, missing=atom):
                        missing = dict(facts, **{atom: False})
                        self.assertNotIn(expected, self.result(ast, missing))


class Round8Repairs(unittest.TestCase):
    """Bounded pass-8 counterexamples; acceptance fixtures remain synthetic."""

    setUp = Round5Repairs.setUp
    key = staticmethod(Round5Repairs.key)
    result = Round5Repairs.result
    surfaces = Round6Repairs.surfaces

    def test_existing_finding_notifications_keep_open_periodic_updates(self):
        vid = 'PUG-DGR1075-2025:§4.4:periodic-finding-notification-update:v1'
        self.assertTrue(vid in self.a, vid)
        row = self.a[vid]
        self.assertEqual(row['effective_from'], '2025-07-29')
        self.assertIn('periodicamente le notifiche già inserite', row['source_quote'])
        self.assertIn(verifier.norm(row['source_quote']),
                      verifier.norm((verifier.ROOT / row['source_paths']).read_text()))
        for ast in self.surfaces(row):
            facts = StageARepairs.facts(ast)
            self.assertEqual(self.result(ast, facts), {'EXISTING_FINDING_NOTIFICATION_UPDATE_REQUIRED'})
            for atom in facts:
                self.assertNotIn('EXISTING_FINDING_NOTIFICATION_UPDATE_REQUIRED',
                                 self.result(ast, dict(facts, **{atom: False})))
        clocks = [c for c in self.b['clocks'] if c['producer_provision_version_id'] == vid]
        self.assertEqual(len(clocks), 1)
        clock = clocks[0]
        self.assertEqual(clock['kind'], 'recurrence')
        self.assertEqual(clock['recurrence'], {'period': None, 'occurrences_per_period': None, 'calendar_deadline': None})
        self.assertEqual(clock['completion']['kind'], 'record')
        self.assertEqual(clock['consequence_on_expiry'], {'kind': 'none', 'ref': None})
        self.assertEqual(clock['legal_duty_owner'], 'REGIONAL_PLANT_HEALTH_SERVICE')
        self.assertEqual([d['ref'] for d in self.b['dispositions'] if d['provision_version_id'] == vid], [clock['clock_id']])
        population = json.loads(verifier.POPULATION.read_text())
        self.assertIn(vid, population['seams']['1'])

    def test_historical_opinion_breach_and_resolved_operativity_can_coexist(self):
        breach = self.key({'predicate': 'evidence proves no qualifying prior National Plant Health Committee opinion covers the area decision'})
        national = self.a['IT-DLGS-19-2021:Art.6(3)(g):v1']
        for ast in self.surfaces(national):
            for breached in (False, True):
                facts = StageARepairs.facts(ast); facts[breach] = breached
                effects = self.result(ast, facts)
                self.assertEqual(len(effects), 1)  # No overlapping authority/breach alternatives.
                effect = next(iter(effects))
                self.assertIn('REGIONAL_AREA_DECISION_AUTHORITY_ESTABLISHED', effect)
                self.assertEqual('PRIOR_COMMITTEE_OPINION_DUTY_BREACHED' in effect, breached)
                self.assertNotIn('VALIDITY_ADJUDICATION_REQUIRED', effect)
        area = self.a['PUG-LR4-2017:Art.3(2):post-LR45-v2']
        for ast in self.surfaces(area):
            for breached in (False, True):
                for operative, unsettled in ((True, False), (False, False), (True, True)):
                    facts = StageARepairs.facts(ast)
                    facts[breach] = breached
                    facts[self.key({'predicate': 'source act or adopted annex evidence missing'})] = False
                    facts[self.key({'predicate': 'competent act validity is proven defective with unsettled legal consequence'})] = unsettled
                    # Supply the old predicate too: resolved is not synonymous with operative.
                    facts[self.key({'predicate': 'act effectiveness and supersession state resolved'})] = True
                    facts[self.key({'predicate': 'the act has current operative effect, taking account of effectiveness, supersession and any resolved legal consequence of a proven defect'})] = operative
                    effects = self.result(ast, facts)
                    self.assertEqual('OPERATIVE_LEGAL_AREA_STATE_ESTABLISHED' in effects,
                                     operative and not unsettled)
                    self.assertEqual(any('ADJUDICATION_REQUIRED' in e for e in effects), unsettled)

    def test_testing_completion_does_not_require_a_favorable_result(self):
        suffixes = ('EU-5(1)(b)-tests-once-a-year', 'EU-5(1)(c)-v1-first-year-survey',
                    'EU-5(1)(c)-v2-first-year-survey', 'EU-5(1)(d)-vector-tests-twice-in-flight-season',
                    'EU-7(3)(a)-annual-retention-testing')
        clocks = {c['clock_id']: c for c in self.b['clocks']}
        with (generator.OUT / 'clocks.csv').open(newline='') as handle:
            emitted = {c['clock_id']: c for c in csv.DictReader(handle)}
        for suffix in suffixes:
            c = clocks['B-CLK-' + suffix]
            self.assertEqual(c['completion']['kind'], 'record')
            self.assertIn('results recorded', c['completion']['ref'])
            self.assertIn('irrespective of result', c['completion']['ref'])
            self.assertEqual(json.loads(emitted[c['clock_id']]['completion']), c['completion'])
            # Performance is the record, not the favorable A conclusion. Untested
            # populations lack that record; positive tests do not satisfy A eligibility.
            a = self.a[c['producer_provision_version_id']]
            facts = StageARepairs.facts(a['condition_ast'])
            favorable = [atom for atom in facts if any(term in atom for term in
                         ('not infected', 'no other', 'pest absent', 'no vectors'))]
            self.assertTrue(favorable, c['clock_id'])
            facts.update({atom: False for atom in favorable})
            self.assertIs(StageARepairs.condition(a['condition_ast'], facts), False)
        v1 = clocks['B-CLK-EU-5(1)(c)-v1-first-year-survey']['completion']['ref']
        v2 = clocks['B-CLK-EU-5(1)(c)-v2-first-year-survey']['completion']['ref']
        self.assertNotIn('90%', v1); self.assertNotIn('400 m', v1)
        for term in ('90%', '1%', '400 m', '2.5 km'):
            self.assertIn(term, v2)
        self.assertIn('Annex IV', clocks['B-CLK-EU-7(3)(a)-annual-retention-testing']['completion']['ref'])

    def test_direct_cnr_handoff_is_not_an_exclusive_choice(self):
        row = self.a['REG-PUGLIA-U181-DIR-2025-00045:positive-sample-cnr-return:v1']
        for ast in self.surfaces(row):
            self.assertNotIn('route_table', ast)
            for entry, receipt in ((False, False), (True, False), (False, True), (True, True)):
                facts = {self.key({'predicate': 'positive sample enters the source CNR-IPSP route'}): entry,
                         self.key({'predicate': 'CNR-IPSP receives the positive sample under the source route'}): receipt}
                self.assertIs(self.result(ast, facts), entry or receipt)
        clocks = {c['clock_id']: c for c in self.b['clocks']}
        self.assertEqual(clocks['B-CLK-DDS45-prompt-positive-cnr-transfer']['completion']['ref'],
                         'positive sample dispatched promptly to CNR-IPSP')
        self.assertIn('receipt', clocks['B-CLK-DDS45-cnr-analysis-return']['anchor']['event'])
        self.assertIn('following receipt', row['true_effect'])

    def test_isolated_baseline_survives_partial_and_full_live_acceptance(self):
        for seams in ((1,), (1, 2, 3, 4)):
            fixture = StageBRepairs(); fixture.setUp()
            self.addCleanup(fixture.doCleanups)
            accepted = fixture.accepted_fixture(seams)
            fixture.check(accepted)  # The production verifier validates the bound act.
            original = Path.read_text
            def redirected(path, *args, **kwargs):
                return json.dumps(accepted) if path == verifier.B else original(path, *args, **kwargs)
            isolated = StageBRepairs(); self.addCleanup(isolated.doCleanups)
            with patch.object(Path, 'read_text', redirected):
                isolated.setUp()
            self.assertTrue(all(m['semantic_acceptance'] == 'NOT_ASSERTED' for m in isolated.base['closure_manifest']))
            for m in isolated.base['closure_manifest']:
                for field in ('semantic_reviewer', 'acceptance_act', 'acceptance_evidence', 'accepted_content_sha256'):
                    self.assertIsNone(m[field])
            isolated.test_baseline_and_unaccepted_consumer_parity()
            ownership = Round5Repairs(); ownership.setUp(); ownership.b = accepted
            ownership.test_current_points_to_acceptance_owner_without_a_copied_map()


class Round9Repairs(unittest.TestCase):
    """Source-defined scenarios, not positive fixtures inferred from authored conditions."""

    setUp = Round5Repairs.setUp
    key = staticmethod(Round5Repairs.key)
    ref = staticmethod(Round5Repairs.ref)
    result = Round5Repairs.result
    surfaces = Round6Repairs.surfaces
    DDS45 = 'REG-PUGLIA-U181-DIR-2025-00045:'
    DDS31 = 'REG-PUGLIA-U181-DIR-2022-00031:'
    ERADICATION = ('EU-2020-1201:7(1)', 'IMMEDIATE_REMOVAL_REQUIRED')
    CONTAINMENT = (
        ('PUG-LR4-2017:Art.6(1)', 'CONTAINMENT_SUBSTITUTES_FOR_ERADICATION'),
        ('EU-2020-1201:13(1)', 'ARTICLE_13_BASELINE_REMOVAL_POPULATION'),
        ('EU-2020-1201:13(2)', 'ARTICLE_13_REMOVAL_STANDS'))

    def scenario(self, predicates=(), results=(), provisions=()):
        # Unspecified inputs stay unknown. Neither the tree nor its omissions supply facts.
        facts = {self.key({'predicate': p}): True for p in predicates}
        facts.update({self.key(self.ref(*r)): True for r in results})
        facts.update({self.key({'provision_ref': p}): True for p in provisions})
        return facts

    def set_predicates(self, facts, **values):
        facts.update({self.key({'predicate': p}): value for p, value in values.items()})

    def test_effectiveness_routes_reach_election_without_a_second_notice_gate(self):
        # Article 21-bis; DGR1075 4.5(e)-(g): valid election during publication.
        prefix = 'IT-L241-A21BIS:Art.21-bis(1):'
        routes = (
            ('individual-communication-effect:v1', {
                'the act restricts the recipient’s legal sphere': True,
                'a valid immediate-effect exception applies': False,
                'the communication to that recipient has been effected, including in the forms prescribed for notification to the unreachable in the cases provided by the code of civil procedure': True}, True),
            ('mass-publicity-route:v1', {
                'recipient number makes personal communication particularly burdensome for the exact act': True,
                'the suitable publicity established by the administration for that act has been completed': True}, True),
            ('motivated-immediate-effect:v1', {
                'the restrictive measure is sanctioning': False,
                'the measure contains a reasoned immediate-effect clause': True}, False),
            ('urgent-cautionary-effect:v1', {
                'the restrictive measure is cautionary': True,
                'the restrictive measure is urgent': True}, False))
        row = self.a['PUG-DGR1075-2025:§4.5:owner-election-execution:v1']

        def check(tree):
            for suffix, source_facts, notice in routes:
                for producer in self.surfaces(self.a[prefix + suffix]):
                    inputs = self.scenario(); self.set_predicates(inputs, **source_facts)
                    effective = 'ACT_EFFECTIVE_AGAINST_RECIPIENT' in self.result(producer, inputs)
                    self.assertTrue(effective, suffix)
                    for election in (True, False, None):
                        facts = self.scenario()
                        self.set_predicates(facts, **{
                            'substantive prescription is valid and effective against the recipient': effective,
                            'valid owner self-execution or ARIF election': election,
                            'valid recipient notice': notice,
                            'decisive substantive inapplicability fact proven': False,
                            'a proven defect legally defeats the authority or operativity of this particular regional measure': False,
                            'a proven defect leaves the operativity of this particular regional measure legally unsettled': False})
                        self.assertEqual('PLAN_ONLY_EFFECT_APPLIES' in self.result(tree, facts), election is True)
                        # A valid election cannot itself establish recipient effectiveness.
                        self.set_predicates(facts, **{'substantive prescription is valid and effective against the recipient': None})
                        self.assertNotIn('PLAN_ONLY_EFFECT_APPLIES', self.result(tree, facts))

        for ast in self.surfaces(row):
            check(ast)
            mutant = copy.deepcopy(ast)
            mutant['route_table'][0]['when']['all_of'].append({'predicate': 'valid recipient notice'})
            with self.assertRaises(AssertionError): check(mutant)
        for suffix, _, _ in routes:
            self.assertIn(prefix + suffix.removesuffix(':v1'), row['external_dependencies'])
        election_clock = next(c for c in self.b['clocks'] if c['clock_id'] == 'B-CLK-DGR1075-owner-election')
        self.assertIn('whichever of its routes', election_clock['applies_when'])

    def test_notice_cure_does_not_accelerate_silence_or_authorize_coercion(self):
        # DGR1075 4.5(h) and D.lgs.19 Art.33(2) retain independent prerequisites.
        row = self.a['PUG-DGR1075-2025:§4.5:silence-route:v1']
        for ast in self.surfaces(row):
            for publication, window in ((False, False), (True, False), (True, True)):
                facts = self.scenario()
                self.set_predicates(facts, **{
                    'substantive prescription is valid and effective against the recipient': True,
                    'valid recipient notice': publication, 'completed election window': window,
                    'affirmative no-response evidence': True,
                    'decisive substantive inapplicability fact proven': False,
                    'a proven defect legally defeats the authority or operativity of this particular regional measure': False,
                    'a proven defect leaves the operativity of this particular regional measure legally unsettled': False})
                self.assertEqual('PLAN_ONLY_EFFECT_APPLIES' in self.result(ast, facts), publication and window)
                self.set_predicates(facts, **{'affirmative no-response evidence': None})
                self.assertNotIn('PLAN_ONLY_EFFECT_APPLIES', self.result(ast, facts))
        for prefix in (self.DDS31, self.DDS45):
            for ast in self.surfaces(self.a[prefix + 'obstruction-remedy-route:v1']):
                facts = self.scenario(['effective prescription', 'documented opposition or obstruction',
                                      'competent Osservatorio attribution of Prefect request',
                                      'documented and recorded access denial or impediment',
                                      'competent Osservatorio attribution of the Prefect request'])
                self.assertIsNot(self.result(ast, facts), True)

    def test_every_treatment_readiness_path_observes_its_applicable_wait(self):
        # DDS45 Part VII 1/2; DDS31 Part VII 1/2. Treated plants remain standing.
        paths = (
            (self.DDS45 + 'treatment-removal-sequence:v1', [
                'operative eradication branch', 'removal occurs during event-time vector flight season',
                'required Article 8 treatment completed'], [self.ERADICATION]),
            (self.DDS45 + 'treatment-removal-sequence:v1', [
                'operative eradication branch', 'event-time evidence establishes removal outside vector flight season',
                'broader Article 8 all-stage treatment duty and appropriate timing satisfied',
                'required Article 8 treatment completed'], [self.ERADICATION]),
            (self.DDS45 + 'containment-treatment-removal-sequence:v1',
                ['required Article 14 treatment completed'], self.CONTAINMENT),
            (self.DDS31 + 'eradication-treatment-removal-sequence:v1',
                ['operative eradication branch', 'authorized-product vector treatment completed in the infected zone'], [self.ERADICATION]),
            (self.DDS31 + 'containment-treatment-removal-sequence:v1',
                ['treatment directed at the plants and their surroundings completed'], self.CONTAINMENT))

        def check(tree, predicates, refs):
            for elapsed in (12, 48, None):
                facts = self.scenario(predicates + ['required treatment completed'], refs)
                self.set_predicates(facts, **{
                    'regional 48-hour wait completed': None if elapsed is None else elapsed >= 48,
                    'the resolved event-time treatment route establishes that no pre-removal treatment triggering the regional 48-hour wait is applicable': False,
                    'evidence proves 48-hour wait not satisfied': elapsed == 12,
                    '48-hour wait evidence missing': elapsed is None})
                result = self.result(tree, facts)
                ready = any('SATISFIED_FOR_REMOVAL' in e or e == 'OUTSIDE_FLIGHT_REMOVAL_ROUTE_LEGALLY_RESOLVED' for e in result)
                self.assertEqual(ready, elapsed == 48)
                self.assertFalse(any('REMOVAL_SEQUENCE_COMPLETE' in e for e in result))
                if elapsed == 48:
                    self.assertFalse(any('NONCOMPLIANT' in e or 'WAIT_EVIDENCE_REQUIRED' in e for e in result))
                elif vid.startswith(self.DDS45):
                    self.assertTrue(any(('WAIT_EVIDENCE_REQUIRED' if elapsed is None else 'SEQUENCE_NONCOMPLIANT') in e for e in result))

        for vid, predicates, refs in paths:
            for ast in self.surfaces(self.a[vid]):
                check(ast, predicates, refs)
                if 'event-time evidence establishes removal outside vector flight season' in predicates:
                    mutant = copy.deepcopy(ast)
                    limbs = mutant['route_table'][1]['when']['all_of'][1]['all_of']
                    limbs[:] = [limb for limb in limbs if 'any_of' not in limb]
                    with self.assertRaises(AssertionError): check(mutant, predicates, refs)

    def test_outside_flight_nonapplicability_is_affirmative_not_missing_evidence(self):
        # Article 8 and DDS45's qualified seasonal route: no invented treatment event.
        row = self.a[self.DDS45 + 'treatment-removal-sequence:v1']
        nonapplicable = 'the resolved event-time treatment route establishes that no pre-removal treatment triggering the regional 48-hour wait is applicable'

        def check(tree):
            for resolved in (True, False, None):
                facts = self.scenario([
                    'operative eradication branch', 'event-time evidence establishes removal outside vector flight season',
                    'broader Article 8 all-stage treatment duty and appropriate timing satisfied'], [self.ERADICATION])
                self.set_predicates(facts, **{nonapplicable: resolved, 'regional 48-hour wait completed': None,
                                            'required treatment completed': False})
                self.assertEqual('OUTSIDE_FLIGHT_REMOVAL_ROUTE_LEGALLY_RESOLVED' in self.result(tree, facts), resolved is True)
                self.set_predicates(facts, **{'broader Article 8 all-stage treatment duty and appropriate timing satisfied': None})
                self.assertNotIn('OUTSIDE_FLIGHT_REMOVAL_ROUTE_LEGALLY_RESOLVED', self.result(tree, facts))

        for ast in self.surfaces(row):
            check(ast)
            mutant = copy.deepcopy(ast)
            mutant['route_table'][1]['when']['all_of'].append({'predicate': 'regional 48-hour wait completed'})
            with self.assertRaises(AssertionError): check(mutant)
            mutant = copy.deepcopy(ast)
            for node in ast_nodes(mutant):
                if node.get('predicate') == nonapplicable:
                    node.clear(); node.update({'not': {'predicate': 'required treatment completed'}})
            with self.assertRaises(AssertionError): check(mutant)

    def test_treatment_family_preserves_retention_and_predecessor_conflict(self):
        controls = []
        for prefix, name in ((self.DDS45, 'treatment-removal-sequence'), (self.DDS31, 'eradication-treatment-removal-sequence')):
            controls.append((prefix + name + ':v1', self.scenario(results=[
                ('EU-2020-1201:7(1)', 'NO_ARTICLE_7_1_REMOVAL_DUTY')]), 'NO_ERADICATION_REMOVAL_SEQUENCE_FOR_THIS_PLANT'))
        controls.extend([
            (self.DDS31 + 'eradication-treatment-removal-sequence:v1', self.scenario([
                'operative eradication branch', 'removal performed without pre-treatment under the categorical November–March instruction'],
                [self.ERADICATION]), 'LEGAL_CONFLICT_WITH_ARTICLE_8_TREATMENT_DUTY'),
            (self.DDS31 + 'containment-treatment-removal-sequence:v1', self.scenario([
                'removal performed without pre-treatment under the categorical November–March instruction'], self.CONTAINMENT),
                'LEGAL_CONFLICT_WITH_ARTICLE_14_TREATMENT_DUTY')])
        for prefix in (self.DDS31, self.DDS45):
            controls.extend([
                (prefix + 'containment-treatment-removal-sequence:v1', self.scenario(results=[self.CONTAINMENT[0],
                    ('EU-2020-1201:13(2)', 'SCIENTIFIC_NON_REMOVAL_DEROGATION_EXERCISED')]),
                    'SCIENTIFIC_RETENTION; NO_CONTAINMENT_REMOVAL_REQUIREMENT; PRESERVE_ARTICLE_14_TREATMENT'),
                (prefix + 'containment-treatment-removal-sequence:v1', self.scenario(results=[
                    ('PUG-LR4-2017:Art.6(1)', 'ERADICATION_CONTROLS')]), 'CONTAINMENT_CHILD_NOT_APPLICABLE; ERADICATION_CONTROLS')])
        for vid, facts, expected in controls:
            for ast in self.surfaces(self.a[vid]): self.assertIn(expected, self.result(ast, facts))

    def test_risk_choice_and_performance_compose_across_destruction_family(self):
        # EU 9(2)/16(2), DDS45/DDS31 root alternatives, DGR1075 4.3.4.
        rows = (
            (self.DDS45 + 'root-wood-completion:v1', '9', 'competent Article 9(2) risk decision limits destruction', ['operative eradication branch']),
            (self.DDS45 + 'containment-root-wood-completion:v1', '16', None, []),
            (self.DDS31 + 'destruction-root-wood-completion:v1', '9', 'competent Article 9(2)/16(2) limited-destruction decision', ['plant removed under the operative branch']))

        def check(tree, article, decision_predicate, base):
            for risk, choice in ((True, True), (True, False), (True, None), (False, True)):
                facts = self.scenario(provisions=['EU-2020-1201:' + article + '(1)'])
                self.set_predicates(facts, **{'risk level permits': risk,
                    'the authority concludes the plants pose no risk of further spread': risk,
                    'the Member State decides to limit destruction to branches and foliage': choice})
                eu = self.a['EU-2020-1201:' + article + '(2):v1']['condition_ast']
                effects = self.result(eu, facts)
                selected = any('LIMITED_DESTRUCTION_DECIDED' in e for e in effects)
                self.assertEqual(selected, risk and choice is True)
                selection_state = None if risk and choice is None else selected
                for physical in (True, False, None):
                    # Without permission, the known absence of full destruction is itself unmet performance.
                    unmet = not risk or choice is False or physical is False
                    f = self.scenario(base + ['no wood retained', 'root system removed'],
                                      self.CONTAINMENT if article == '16' else (),
                                      ['EU-2020-1201:8(1)', 'EU-2020-1201:14(1)'])
                    self.set_predicates(f, **{
                        'whole-root extirpation with in-situ shredding or burning of the plant and its parts completed': False,
                        'required above-ground destruction of branches and foliage completed': physical,
                        'competent Article 16(2) no-further-spread conclusion': risk,
                        'an applicable destruction performance condition is proven unsatisfied': unmet})
                    if decision_predicate: self.set_predicates(f, **{decision_predicate: selection_state})
                    f[self.key(self.ref('EU-2020-1201:16(2)', 'LIMITED_DESTRUCTION_DECIDED; WOOD_TREATED_UNDER_ARTICLE_14_1; ROOTS_REMOVED_OR_DEVITALISED'))] = selection_state
                    result = self.result(tree, f)
                    completed = any('LIMITED_DESTRUCTION' in e and 'COMPLETE' in e for e in result)
                    self.assertEqual(completed, selected and physical is True)
                    if unmet: self.assertTrue(any('NOT_COMPLETE' in e for e in result))
                    elif physical is None: self.assertFalse(any('NOT_COMPLETE' in e for e in result))

        for vid, article, predicate, base in rows:
            for ast in self.surfaces(self.a[vid]):
                check(ast, article, predicate, base)
                # Full destruction does not require permission for the unused limited alternative.
                full = self.scenario(base + ['no wood retained',
                    'whole-root extirpation with in-situ shredding or burning of the plant and its parts completed'],
                    self.CONTAINMENT if article == '16' else (), ['EU-2020-1201:' + article + '(1)'])
                self.assertTrue(any('FULL_DESTRUCTION_COMPLETE' in e for e in self.result(ast, full)))
                if article == '16':
                    mutant = copy.deepcopy(ast)
                    for node in ast_nodes(mutant):
                        if node.get('result_ref', {}).get('producer_stable_provision_id') == 'EU-2020-1201:16(2)':
                            node.clear(); node.update({'predicate': 'competent Article 16(2) no-further-spread conclusion'})
                    with self.assertRaises(AssertionError): check(mutant, article, predicate, base)
                    mutant = copy.deepcopy(ast)
                    mutant['route_table'][1]['when']['all_of'].append({'predicate': 'separate limited-destruction approval document'})
                    with self.assertRaises(AssertionError): check(mutant, article, predicate, base)

    def test_area_endpoints_require_the_finding_specific_performance(self):
        # LR4 3(3) is a modification duty; EU4 can be satisfied by an adequate existing area.
        # Facts below are stipulated legal outcomes, not a geometry or completion evaluator.
        region = 'B-CLK-LR4-3(3)-modify-on-buffer-finding'
        eu_ids = ['B-CLK-EU-4(1)-v1-demarcate', 'B-CLK-EU-4(1)-v2-demarcate']
        eu_record = 'operative demarcation satisfying the Article 4 duty for the triggering official plant finding is established'
        performed = 'PUG-LR4-2017:Art.3(3):v1'
        with (verifier.ROOT / 'regulation/stage-b/generated/clocks.csv').open() as handle:
            emitted = {r['clock_id']: r for r in csv.DictReader(handle)}

        def check(clock):
            regional = clock['clock_id'] == region
            # Existing area only; adequate old area (EU only); one consequent modification.
            cases = [(False, False), (True, True)] if regional else [(False, False), (True, False), (True, True)]
            for adequate, modified in cases:
                evidence = {('a_effect', 'OPERATIVE_LEGAL_AREA_STATE_ESTABLISHED'): True,
                            ('a_version_performed', performed): modified,
                            ('record', eu_record): adequate}
                actual = evidence.get((clock['completion']['kind'], clock['completion']['ref']))
                self.assertEqual(actual, modified if regional else adequate)

        for cid in [region] + eu_ids:
            clock = next(c for c in self.b['clocks'] if c['clock_id'] == cid)
            self.assertEqual(clock['completion'], json.loads(emitted[cid]['completion']))
            for endpoint in (clock['completion'], json.loads(emitted[cid]['completion'])):
                surface = dict(clock, completion=endpoint); check(surface)
                mutant = copy.deepcopy(surface)
                mutant['completion'] = {'kind': 'a_effect', 'ref': 'OPERATIVE_LEGAL_AREA_STATE_ESTABLISHED'}
                with self.assertRaises(AssertionError): check(mutant)
            if cid in eu_ids:
                self.assertIn('NO_IMMEDIATE_DEMARCATION_DECIDED', clock['applies_when'])
                self.assertIn('fresh act is not required', clock['note'])


class Round10Repairs(unittest.TestCase):
    """Bounded source scenarios and prose-contract regressions, not Stage C execution."""

    setUp = Round5Repairs.setUp
    key = staticmethod(Round5Repairs.key)
    result = Round5Repairs.result
    surfaces = Round6Repairs.surfaces
    scenario = Round9Repairs.scenario
    set_predicates = Round9Repairs.set_predicates
    LR = 'PUG-LR4-2017:Art.8(5):protected-uninfected-retention'
    POLICY = 'the operative regional retention policy covers this individually qualifying plant'
    DDS45 = Round9Repairs.DDS45
    DDS31 = Round9Repairs.DDS31

    def emitted(self, row):
        with (jurisdiction_generator.OUT / 'provision-versions.csv').open(newline='') as handle:
            result = next(r for r in csv.DictReader(handle)
                          if r['provision_version_id'] == row['provision_version_id'])
        for field in ('true_effect', 'false_effect', 'evidence_contract', 'semantic_note', 'modality', 'authority_judgment_kind'):
            self.assertEqual(result[field], row[field])
        return result

    def qualifying_tree(self, ground='c'):
        # DGR538/343/1593/1075 apply a policy; the individual still meets EU 7(3).
        facts = self.scenario([
            'official protected/value designation',
            'the olive is listed as monumental under L.R. 14/2007 Article 2', self.POLICY],
            provisions=['EU-2020-1201:7(3)(a)', 'EU-2020-1201:7(3)(b)'])
        for point in 'abcde':
            facts[self.key({'provision_ref': f'EU-2020-1201:7(1)({point})'})] = point == ground
        self.set_predicates(facts, **{
            'evidence proves independent Article 7(1)(a) or (e) ground': False,
            'competent authority validly declines to exercise the discretion': False,
            'the competent authority validly declines to exercise the discretion': False,
            'applicable regional policy and competent case-specific retention decision': False,
            'the applicable regional plan exercises the Article 7(3) discretion (DGR 538/2021 from 6 April 2021) and a competent case-specific retention decision is taken': False})
        return facts

    def test_policy_application_needs_eligibility_not_a_second_choice(self):
        for version in ('pre-LR45-v1', 'post-LR45-v2'):
            row = self.a[self.LR + ':' + version]
            self.emitted(row)
            self.assertEqual(row['modality'], 'shall not')
            self.assertNotIn('discretion', row['authority_judgment_kind'])

            def check(tree):
                for ground in 'bcd':
                    facts = self.qualifying_tree(ground)
                    self.assertIn('ARTICLE_7_3_RETENTION_VALIDLY_EXERCISED', self.result(tree, facts))
                    designation = ('the olive is listed as monumental under L.R. 14/2007 Article 2'
                                   if version.startswith('pre') else 'official protected/value designation')
                    requirements = [{'predicate': designation}, {'predicate': self.POLICY},
                                    {'provision_ref': 'EU-2020-1201:7(3)(a)'},
                                    {'provision_ref': 'EU-2020-1201:7(3)(b)'}]
                    for requirement in requirements:
                        for value in (False, None):
                            probe = dict(facts); probe[self.key(requirement)] = value
                            self.assertNotIn('ARTICLE_7_3_RETENTION_VALIDLY_EXERCISED', self.result(tree, probe))
                    for independent in 'ae':
                        probe = dict(facts)
                        probe[self.key({'provision_ref': f'EU-2020-1201:7(1)({independent})'})] = True
                        self.assertNotIn('ARTICLE_7_3_RETENTION_VALIDLY_EXERCISED', self.result(tree, probe))

            for ast in self.surfaces(row):
                check(ast)
                extra_gate = copy.deepcopy(ast)
                extra_gate['route_table'][0]['when']['all_of'][-1] = {
                    'predicate': 'applicable regional policy and competent case-specific retention decision'}
                with self.assertRaises(AssertionError): check(extra_gate)
                for index in (1, 2, 3, 4, 5):
                    missing_requirement = copy.deepcopy(ast)
                    missing_requirement['route_table'][0]['when']['all_of'].pop(index)
                    with self.assertRaises(AssertionError): check(missing_requirement)

    def test_effective_policy_reaches_plans_and_nonexercise_remains(self):
        regional = self.a[self.LR + ':post-LR45-v2']
        for plan in ('1593-2024', '1075-2025'):
            row = self.a['PUG-DGR' + plan + ':Art7(3)-policy:v1']
            self.emitted(row)
            self.assertEqual(row['modality'], 'shall not')
            self.assertIn('not additional retention discretion', row['authority_judgment_kind'])
            for ast in self.surfaces(row):
                for covered in (True, False, None):
                    facts = self.qualifying_tree(); facts[self.key({'predicate': self.POLICY})] = covered
                    resolved = 'ARTICLE_7_3_RETENTION_VALIDLY_EXERCISED' in self.result(regional['condition_ast'], facts)
                    consumer = self.scenario(['effective plan interval',
                        'this plan interval chooses to exercise the eligible Article 7(3) discretion'])
                    consumer[self.key({'provision_ref': self.LR})] = resolved
                    self.set_predicates(consumer, **{
                        'decisive substantive inapplicability fact proven': False,
                        'a proven defect legally defeats the authority or operativity of this particular regional measure': False,
                        'a proven defect leaves the operativity of this particular regional measure legally unsettled': False})
                    self.assertEqual('PLAN_ONLY_EFFECT_APPLIES' in self.result(ast, consumer), covered is True)
        for plan in ('538-2021', '343-2022'):
            row = self.a['PUG-DGR' + plan + ':Art7(3)-policy:v1']
            # The historic AST was already correct; its descriptive consumers must agree.
            for surface in (row, self.emitted(row)):
                def check_policy(value):
                    self.assertEqual(value['modality'], 'shall not')
                    self.assertIn('no additional discretionary authorization', value['true_effect'])
                    self.assertIn('coverage by this effective retention policy', value['evidence_contract'])
                    self.assertNotIn('competent decision', value['evidence_contract'])
                    self.assertEqual(value['authority_judgment_kind'],
                                     'individual qualification and event-time retention policy application')
                check_policy(surface)
                for field, old in (('modality', 'may'), ('true_effect', 'Permit case-specific retention of a qualifying plant.'),
                                   ('evidence_contract', 'Final listed status, competent decision, annual testing.'),
                                   ('authority_judgment_kind', 'protected-value retention decision')):
                    mutant = dict(surface); mutant[field] = old
                    with self.assertRaises(AssertionError): check_policy(mutant)
            facts = self.scenario(['effective plan interval', 'official protected status',
                                   'official negative result', 'continuing Article 7(3) conditions'])
            for ast in self.surfaces(row):
                self.assertIs(self.result(ast, facts), True)
                facts[self.key({'predicate': 'continuing Article 7(3) conditions'})] = False
                self.assertIs(self.result(ast, facts), False)
        row = self.a['PUG-DGR1866-2022:Art7(3)-policy:v1']
        self.assertIn('non si applica la deroga', ' '.join(row['source_quote'].split()))
        facts = self.scenario(['effective plan interval',
            'officially recognized monumental olive in the 50 m infected zone that tested negative'])
        for ast in self.surfaces(row):
            self.assertEqual(self.result(ast, facts),
                {'ARTICLE_7_3_RETENTION_NOT_EXERCISED; ARTICLE_7_REMOVAL_APPLIES'})
        for version in ('pre-LR45-v1', 'post-LR45-v2'):
            facts = self.qualifying_tree(); facts[self.key({'predicate': self.POLICY})] = False
            self.set_predicates(facts, **{'competent authority validly declines to exercise the discretion': True,
                                         'the competent authority validly declines to exercise the discretion': True})
            for ast in self.surfaces(self.a[self.LR + ':' + version]):
                self.assertEqual(self.result(ast, facts), {'REMOVAL_DUTY_CONTINUES'})

    def test_infected_alternative_preserves_its_actual_authorization(self):
        row = self.a['PUG-LR4-2017:Art.8(7bis):infected-piana-alternative-boundary:v1']
        self.assertIn('risultati infetti', row['source_quote'])
        self.assertIn('autorizzati dall’Osservatorio', row['source_quote'])
        for surface in (row, self.emitted(row)):
            def check_contract(contract):
                self.assertNotIn('negative', contract)
                self.assertNotIn('annual testing', contract)
                for term in ('infection', 'Piana', 'higher-law derogation', 'Osservatorio authorization', 'vector controls', 'branch-specific testing'):
                    self.assertIn(term, contract)
            check_contract(surface['evidence_contract'])
            with self.assertRaises(AssertionError):
                check_contract('Final listed status, official negative result, competent decision, annual testing and vector-treatment evidence.')
        conditions = ('exact higher-law derogation', 'qualifying branch and site', 'competent Osservatorio authorization')
        for ast in self.surfaces(row):
            facts = self.scenario(conditions)
            self.assertIs(self.result(ast, facts), True)
            for condition in conditions:
                for value in (False, None):
                    probe = dict(facts); probe[self.key({'predicate': condition})] = value
                    self.assertIsNot(self.result(ast, probe), True)
                    mutant = copy.deepcopy(ast); mutant['all_of'].remove({'predicate': condition})
                    self.assertIs(self.result(mutant, probe), True)

    def test_new_species_analysis_is_performance_not_an_activation_gate(self):
        row = self.a[self.DDS45 + 'positive-sample-cnr-return:v1']
        source = (verifier.ROOT / row['source_paths']).read_text()
        paragraph = source[source.index('In caso di campione positivo individuato in una nuova specie,'):
                           source.index('3. COMUNICAZIONE RISULTATI ANALISI')].strip()
        self.assertIn(paragraph, row['source_quote'])
        for surface in (row, self.emitted(row)):
            # These are regressions on an authored prose contract, not a method-selection engine.
            def check_contract(value):
                for term in ('For a positive in a new species', 'not among the specified species',
                             'Xylella present in its demarcated area', 'required subspecies identification is MLST under Yuan'):
                    self.assertIn(term, value['true_effect'])
                self.assertIn('qualifying new-species route requires the MLST/Yuan subspecies report', value['evidence_contract'])
            check_contract(surface)
            for field in ('true_effect', 'evidence_contract'):
                mutant = dict(surface); mutant[field] = mutant[field].replace('MLST', 'Dupas')
                with self.assertRaises(AssertionError): check_contract(mutant)
        for ast in self.surfaces(row):
            for sending, received in ((True, False), (False, True), (True, True), (False, False)):
                facts = self.scenario()
                self.set_predicates(facts, **{'positive sample enters the source CNR-IPSP route': sending,
                    'CNR-IPSP receives the positive sample under the source route': received})
                self.assertIs(self.result(ast, facts), sending or received)
            self.assertFalse(any('MLST' in n.get('predicate', '') for n in ast_nodes(ast)))
        clock = next(c for c in self.b['clocks'] if c['clock_id'] == 'B-CLK-DDS45-cnr-analysis-return')
        with (generator.OUT / 'clocks.csv').open(newline='') as handle:
            emitted = next(c for c in csv.DictReader(handle) if c['clock_id'] == clock['clock_id'])
        for completion in (clock['completion'], json.loads(emitted['completion'])):
            def check_completion(value):
                self.assertIn(row['stable_provision_id'], value['ref'])
                self.assertIn('Applicable source-route analysis', value['ref'])
            check_completion(completion)
            with self.assertRaises(AssertionError):
                check_completion({'ref': 'CNR-IPSP analysis completed and result communicated to the Osservatorio'})
        self.assertEqual((clock['magnitude'], clock['unit']), ('3', 'working_days'))
        self.assertEqual(clock['consequence_on_expiry'], {'kind': 'none', 'ref': None})

    def test_successor_immediacy_references_the_existing_clock(self):
        version = 'EU-2020-1201:15(1):v2'
        cid = 'B-CLK-EU-15(1)-v1-immediate-50m-sampling'
        self.assertIn('immediately sample and test', self.a[version]['true_effect'])
        def check(dispositions):
            matches = [d for d in dispositions if d['provision_version_id'] == version
                       and d['expression'] == 'immediately sample and test']
            self.assertEqual(len(matches), 1)
            self.assertEqual((matches[0]['disposition'], matches[0]['ref']), ('implements_clock', cid))
        check(self.b['dispositions'])
        mutant = [d for d in self.b['dispositions'] if not (d['provision_version_id'] == version and d['ref'] == cid)]
        with self.assertRaises(AssertionError): check(mutant)
        with (generator.OUT / 'clocks.csv').open(newline='') as handle:
            clocks = [c for c in csv.DictReader(handle) if c['clock_id'] == cid]
        self.assertEqual(len(clocks), 1)
        self.assertEqual((clocks[0]['effective_from'], clocks[0]['effective_to_exclusive']), ('2020-08-20', ''))

    def test_eight_notes_keep_operative_distinctions_without_review_history(self):
        expected = {
            'PUG-LR4-2017:Art.4(3):laboratory:post-LR45-v2': ('required accreditation', 'suspension', 'missing separate designation evidence'),
            self.DDS45 + 'sample-custody-transfer:v1': ('not a laboratory representative', 'Articles 20/24'),
            self.DDS45 + 'eradication-removal-population-support:v1': ('retains removal-population', 'Articles 20/24'),
            self.DDS45 + 'containment-removal-population-support:v1': ('retains the containment removal decision', 'Articles 20/24'),
            self.DDS45 + 'pest-free-positive-routing:v1': ('different genome region', 'Bari-seat designation is not inferred', 'missing separate designation evidence'),
            self.DDS31 + 'pest-free-buffer-pool-confirmation:v1': ('35 known specified species', 'repeat/extraction', 'lateness alone does not defeat confirmation'),
            self.DDS31 + 'sample-custody-transfer:v1': ('open or unsealed bags', 'Acceptance is separate', 'Articles 20/24'),
            self.DDS31 + 'execution-oversight-and-record:v1': ('not physical execution', 'Articles 20/24')}
        for vid, preserved in expected.items():
            row = self.a[vid]
            for surface in (row, self.emitted(row)):
                def check(note):
                    for retired in ('[RULED', 'seam-1 ruling', 'build-holdable', 'no held decision', 'were antecedents', 'refresh 2026'):
                        self.assertNotIn(retired, note)
                    for term in preserved: self.assertIn(term, note)
                check(surface['semantic_note'])
                with self.assertRaises(AssertionError): check(surface['semantic_note'] + ' [RULED 2026-09-01]')


class Round11Repairs(unittest.TestCase):
    """Approved scope and contract corrections, including the valid not-yet-performed state."""

    setUp = Round5Repairs.setUp
    key = staticmethod(Round5Repairs.key)
    result = Round5Repairs.result
    scenario = Round9Repairs.scenario
    set_predicates = Round9Repairs.set_predicates

    def test_proposal_work_is_deferred_without_losing_survey_dependencies(self):
        vid = 'IT-DLGS-19-2021:Art.27(3):v1'
        cid = 'B-CLK-IT-27(3)-annual-regional-proposal'
        self.assertIn('annualmente', self.a[vid]['source_quote'])
        self.assertIn('IT-PNI-2026:adoption-and-publication-status:v1', self.a)

        def check(ledger):
            self.assertNotIn(cid, {c['clock_id'] for c in ledger['clocks']})
            dispositions = [d for d in ledger['dispositions'] if d['provision_version_id'] == vid]
            self.assertEqual(len(dispositions), 1)
            self.assertEqual((dispositions[0]['expression'], dispositions[0]['aperture'], dispositions[0]['ref']),
                             ('annualmente', 'DEFERRED', None))
            for retained in ('B-CLK-EU-7(3)(a)-annual-retention-testing',
                             'B-CLK-EU-5(4)(a)-v1-annual-follow-up-survey',
                             'B-CLK-EU-5(4)(a)-v2-annual-follow-up-survey'):
                self.assertIn(retained, {c['clock_id'] for c in ledger['clocks']})
                self.assertTrue(any(d['ref'] == retained and d['aperture'] == 'IN_APERTURE'
                                    for d in ledger['dispositions']))
        check(self.b)
        with (generator.OUT / 'clocks.csv').open(newline='') as handle:
            check(dict(self.b, clocks=list(csv.DictReader(handle))))
        mutant = copy.deepcopy(self.b); mutant['clocks'].append({'clock_id': cid})
        with self.assertRaises(AssertionError): check(mutant)
        mutant = copy.deepcopy(self.b)
        next(d for d in mutant['dispositions'] if d['provision_version_id'] == vid)['aperture'] = 'IN_APERTURE'
        with self.assertRaises(AssertionError): check(mutant)
        mutant = copy.deepcopy(self.b)
        mutant['clocks'] = [c for c in mutant['clocks'] if c['clock_id'] != 'B-CLK-EU-7(3)(a)-annual-retention-testing']
        with self.assertRaises(AssertionError): check(mutant)

    def test_eu_evidence_follows_the_selected_retention_alternative(self):
        row = self.a['EU-2020-1201:7(3):v3']
        with (verifier.ROOT / 'regulation/stage-a/provision-versions.csv').open(newline='') as handle:
            emitted = next(r for r in csv.DictReader(handle) if r['provision_version_id'] == row['provision_version_id'])
        self.assertEqual(emitted['evidence_contract'], row['evidence_contract'])
        # Prose-contract regression: it does not implement evidence adjudication or Stage C.
        def check_contract(value):
            for term in ('applicable ground:', 'official historic-value designation',
                         'particular social/cultural/environmental value with unacceptable felling impact',
                         'or specific national/Union protective rules', 'both Article 7(3)(a)/(b) safeguards',
                         'exercised competent retention choice', 'applicable policy covering the individual'):
                self.assertIn(term, value)
        for contract in (row['evidence_contract'], emitted['evidence_contract']): check_contract(contract)
        with self.assertRaises(AssertionError): check_contract('the official designation and the two ongoing conditions')
        for version in ('v1', 'v2'):
            self.assertEqual(self.a['EU-2020-1201:7(3):' + version]['evidence_contract'],
                             'the official designation and the two ongoing conditions')
        grounds = ('plant officially designated as a plant with historic value',
                   'tree of particular social, cultural or environmental value whose felling would have an unacceptable impact',
                   'tree subject to specific national or Union rules for its protection')
        choice = 'the Member State decides that the individual plant need not be removed'
        for selected in grounds:
            facts = self.scenario(['individual specified plant', choice],
                provisions=['EU-2020-1201:7(1)(c)', 'EU-2020-1201:7(3)(a)', 'EU-2020-1201:7(3)(b)'])
            for point in 'abde': facts[self.key({'provision_ref': f'EU-2020-1201:7(1)({point})'})] = False
            for ground in grounds: facts[self.key({'predicate': ground})] = ground == selected
            self.assertIn('RETENTION_DEROGATION_EXERCISED', self.result(row['condition_ast'], facts))
            for requirement in ({'predicate': choice}, {'provision_ref': 'EU-2020-1201:7(3)(a)'},
                                {'provision_ref': 'EU-2020-1201:7(3)(b)'}):
                for value in (False, None):
                    probe = dict(facts); probe[self.key(requirement)] = value
                    self.assertNotIn('RETENTION_DEROGATION_EXERCISED', self.result(row['condition_ast'], probe))

    def test_election_expiry_does_not_perform_the_successor_duty(self):
        clocks = {c['clock_id']: c for c in self.b['clocks']}
        with (generator.OUT / 'clocks.csv').open(newline='') as handle:
            emitted = {c['clock_id']: c for c in csv.DictReader(handle)}
        for plan in ('538', '343', '1866', '1593', '1075'):
            election = clocks[f'B-CLK-DGR{plan}-owner-election']
            successor = clocks[f'B-CLK-DGR{plan}-silence-arif-removal']
            for consequence in (election['consequence_on_expiry'],
                                json.loads(emitted[election['clock_id']]['consequence_on_expiry'])):
                def check(value): self.assertEqual(value, {'kind': 'none', 'ref': None})
                check(consequence)
                with self.assertRaises(AssertionError):
                    check({'kind': 'a_version_performed', 'ref': successor['producer_provision_version_id']})
            for surface in (successor, emitted[successor['clock_id']]):
                anchor = json.loads(surface['anchor']) if isinstance(surface['anchor'], str) else surface['anchor']
                completion = json.loads(surface['completion']) if isinstance(surface['completion'], str) else surface['completion']
                self.assertIn('evidenced non-response', anchor['event'])
                self.assertIn('effective against that recipient', surface['applies_when'])
                self.assertEqual((surface['magnitude'], surface['unit']), ('10', 'calendar_days'))
                self.assertEqual(completion, {'kind': 'record', 'ref': 'ARIF removed the plants'})
            row = self.a[successor['producer_provision_version_id']]
            facts = self.scenario()
            self.set_predicates(facts, **{
                'valid recipient effect of the prescription': True,
                'evidenced absence of any owner communication within the source-stated post-publication window': True,
                'substantive prescription is valid and effective against the recipient': True,
                'valid recipient notice': True, 'completed election window': True, 'affirmative no-response evidence': True,
                'decisive substantive inapplicability fact proven': False,
                'a proven defect legally defeats the authority or operativity of this particular regional measure': False,
                'a proven defect leaves the operativity of this particular regional measure legally unsettled': False,
                'ARIF removed the plants': False})
            expected = 'PLAN_ONLY_EFFECT_APPLIES' if plan == '1075' else 'ARIF_SUBSTITUTE_REMOVAL_WITHIN_SOURCE_WINDOW'
            self.assertIn(expected, self.result(row['condition_ast'], facts))
            silence = ('affirmative no-response evidence' if plan == '1075' else
                       'evidenced absence of any owner communication within the source-stated post-publication window')
            for value in (False, None):
                probe = dict(facts); probe[self.key({'predicate': silence})] = value
                self.assertNotIn(expected, self.result(row['condition_ast'], probe))
        # Explicit legal-effect consequences elsewhere are not erased by this local cure.
        self.assertEqual(clocks['B-CLK-EU-7(3)(a)-annual-retention-testing']['consequence_on_expiry'],
                         {'kind': 'a_effect', 'ref': 'REMOVAL_DUTY_CONTINUES'})


class Round12Repairs(unittest.TestCase):
    setUp = Round5Repairs.setUp
    key = staticmethod(Round5Repairs.key)
    result = Round5Repairs.result
    surfaces = Round6Repairs.surfaces

    def test_custody_completion_excludes_material_assignment_failure(self):
        row = self.a['REG-PUGLIA-U181-DIR-2025-00045:sample-custody-transfer:v1']
        good = ('same-day delivery and refrigerated transport', 'authorized transporter assignment',
                'two assistants and driver digitally sign the handover record',
                'authorized transporter digitally countersigns to attest delivery to the laboratory')
        material = 'a proven personnel-authority defect legally defeats this official custody proof'
        failed = 'evidence proves a mandatory source custody condition failed'
        def check(ast):
            facts = {self.key({'predicate': p}): True for p in good}
            facts.update({self.key({'predicate': material}): False, self.key({'predicate': failed}): False})
            # An ordinary official record supplies identity/assignment; no separate extract is demanded.
            facts[self.key({'predicate': 'separate register extract supplied'})] = None
            self.assertEqual(self.result(ast, facts), {'SOURCE_SAMPLE_CUSTODY_TRANSFER_COMPLETE'})
            facts[self.key({'predicate': material})] = True
            self.assertEqual(self.result(ast, facts), {'SOURCE_SAMPLE_CUSTODY_NONCOMPLIANT'})
            self.assertTrue(facts[self.key({'predicate': good[0]})])  # Delivery still happened.
            facts[self.key({'predicate': material})] = False
            facts[self.key({'predicate': good[0]})] = False
            facts[self.key({'predicate': failed})] = True
            self.assertEqual(self.result(ast, facts), {'SOURCE_SAMPLE_CUSTODY_NONCOMPLIANT'})
            facts[self.key({'predicate': failed})] = False
            facts[self.key({'predicate': good[0]})] = None
            self.assertNotIn('SOURCE_SAMPLE_CUSTODY_TRANSFER_COMPLETE', self.result(ast, facts))
        for ast in self.surfaces(row):
            check(ast)
            mutant = copy.deepcopy(ast)
            mutant['route_table'][0]['when']['all_of'] = [{'predicate': p} for p in good]
            with self.assertRaises(AssertionError):
                check(mutant)
        clock = next(c for c in self.b['clocks'] if c['clock_id'] == 'B-CLK-DDS45-custody-same-day')
        self.assertEqual(clock['completion'], {'kind': 'a_effect', 'ref': 'SOURCE_SAMPLE_CUSTODY_TRANSFER_COMPLETE'})

    def test_nonexercise_and_crop_contracts_do_not_require_retention_safeguards(self):
        for suffix in ('Art7(3)-policy', 'st53-crop-exclusion-conflict'):
            row = self.a[f'PUG-DGR1866-2022:{suffix}:v1']
            def check(contract):
                for unrelated in ('annual testing', 'vector-treatment', 'value designation', 'competent decision'):
                    self.assertNotIn(unrelated, contract)
                self.assertTrue(contract)
            check(row['evidence_contract'])
            with self.assertRaises(AssertionError):
                check('Final listed status, official negative result, value designation, competent decision, annual testing and vector-treatment evidence.')
            for ast in self.surfaces(row):
                facts = StageARepairs.facts(ast)
                result = self.result(ast, facts)
                self.assertTrue(result)
        policy = self.a['PUG-DGR1866-2022:Art7(3)-policy:v1']
        self.assertIn('negative', policy['evidence_contract'])
        self.assertIn('50 m', policy['evidence_contract'])
        crop = self.a['PUG-DGR1866-2022:st53-crop-exclusion-conflict:v1']
        self.assertIn('Annex II', crop['evidence_contract'])
        self.assertIn('plant-specific', crop['evidence_contract'])

    def test_requirement_descriptions_and_actual_csvs_do_not_restore_known_extra_gates(self):
        emitted = {}
        for folder in ('regulation/stage-a', 'regulation/jurisdiction/generated'):
            with (verifier.ROOT / folder / 'provision-versions.csv').open(newline='') as handle:
                emitted.update({r['provision_version_id']: r for r in csv.DictReader(handle)})
        for row in self.rows:
            for field in ('evidence_contract', 'authority_judgment_kind'):
                if field in emitted[row['provision_version_id']]:
                    self.assertEqual(row[field], emitted[row['provision_version_id']][field])
                self.assertNotIn('dependency must be serialized or otherwise accepted', row[field])
            if ':case-delta:' in row['provision_version_id']:
                self.assertNotEqual(row['evidence_contract'], 'Case date, DDS 69 area state, Salento buffer subzone, official finding, operative Article 7 points 1–4 and source conflict.')
        annual = self.a['EU-2020-1201:7(3)(a):v1']
        self.assertNotIn('designated plant', annual['evidence_contract'])
        self.assertIn('Annex IV', annual['evidence_contract'])
        self.assertIn('individual plant', annual['evidence_contract'])
        self.assertEqual(self.a['EU-2020-1201:7(3):v3']['authority_judgment_kind'],
                         'retention decision on the eligible individual specified plant')
        custody = self.a['REG-PUGLIA-U181-DIR-2022-00031:sample-custody-transfer:v1']
        self.assertNotIn('laboratory acceptance', custody['evidence_contract'])
        self.assertIn('Acceptance is separate', custody['semantic_note'])
        area = self.a['REG-PUGLIA-U181-DIR-2024-00158:area-state-transition:v1']
        self.assertNotIn('national approval', area['authority_judgment_kind'])

    def test_stored_b_projection_fingerprints_detect_actual_file_and_input_drift(self):
        import verify_repository as repository
        current = json.loads((verifier.ROOT / 'state/CURRENT.json').read_text())
        with tempfile.TemporaryDirectory(prefix='cordon-stored-b-') as directory:
            root = Path(directory)
            paths = [v['path'] for v in current['stages']['A']['canonical_artifacts'].values()]
            paths += [current['stages']['B'][k]['path'] for k in ('canonical', 'population')]
            paths += ['regulation/stage-b/generated/' + name for name in
                      ('generation-status.json', 'clocks.csv', 'parameters.csv')]
            for relative in paths:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verifier.ROOT / relative, target)
            with patch.object(repository, 'ROOT', root):
                repository.verify_stage_b_projections(current)
                for name, identity, field, value in (
                        ('clocks.csv', 'clock_id', 'effective_to_exclusive', '2099-01-01'),
                        ('parameters.csv', 'parameter_id', 'value', '999')):
                    path = root / 'regulation/stage-b/generated' / name
                    original = path.read_bytes()
                    with path.open(newline='') as handle:
                        reader = csv.DictReader(handle); columns = reader.fieldnames; rows = list(reader)
                    target = next(r for r in rows if r[identity] == 'B-CLK-EU-2(1)-v1') if name == 'clocks.csv' else rows[0]
                    target[field] = value
                    with path.open('w', newline='') as handle:
                        writer = csv.DictWriter(handle, fieldnames=columns); writer.writeheader(); writer.writerows(rows)
                    with self.assertRaisesRegex(SystemExit, 'stored projection hash mismatch'):
                        repository.verify_stage_b_projections(current)
                    path.write_bytes(original)
                for relative in paths[:4]:
                    path = root / relative; original = path.read_bytes()
                    path.write_bytes(original + b' ')
                    with self.assertRaisesRegex(SystemExit, 'generation input mismatch'):
                        repository.verify_stage_b_projections(current)
                    path.write_bytes(original)
                repository.verify_stage_b_projections(current)


class Round13Repairs(unittest.TestCase):
    setUp = Round5Repairs.setUp
    key = staticmethod(Round5Repairs.key)
    result = Round5Repairs.result
    surfaces = Round6Repairs.surfaces

    def test_case_noncommencement_is_not_completion_election_or_missing_evidence(self):
        cases = [(2021, 135), (2022, 4), (2022, 6), (2023, 2), (2023, 45), (2023, 51),
                 (2023, 96), (2024, 27), (2024, 52), (2024, 138), (2024, 147),
                 (2024, 151), (2024, 188), (2025, 115), (2025, 117), (2025, 173),
                 (2025, 201), (2026, 35)]
        for year, number in cases:
            vid = f'REG-PUGLIA-U181-DIR-{year}-{number:05d}:case-delta:noncommencement-enforcement:v1'
            with self.subTest(case=vid):
                row = self.a[vid]
                self.assertIn('concreto avvio', row['source_quote'])
                self.assertIn(row['source_quote'], (verifier.ROOT / row['source_paths']).read_text())
                clock = next(c for c in self.b['clocks'] if c['producer_provision_version_id'] == vid)
                self.assertEqual((clock['magnitude'], clock['unit']), ('10', 'calendar_days'))
                self.assertIn('notification', clock['anchor']['event'])
                self.assertNotIn('election', clock['anchor']['event'])
                self.assertIn('commencement', clock['completion']['ref'])
                self.assertEqual(clock['consequence_on_expiry'], {'kind': 'none', 'ref': None})
                with (verifier.ROOT / 'regulation/stage-b/generated/clocks.csv').open(newline='') as handle:
                    emitted = next(c for c in csv.DictReader(handle) if c['clock_id'] == clock['clock_id'])
                for field, value in clock.items():
                    self.assertEqual(emitted[field], generator.flat(value))
                for ast in self.surfaces(row):
                    facts = StageARepairs.facts(ast)
                    self.assertEqual(self.result(ast, facts), {'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED'})
                    for atom in ast['route_table'][0]['when']['all_of']:
                        for value in (False, None):
                            mutant = dict(facts, **{self.key(atom): value})
                            self.assertNotIn('CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED', self.result(ast, mutant))
                            missing_guard = copy.deepcopy(ast)
                            missing_guard['route_table'][0]['when']['all_of'].remove(atom)
                            # Removing this qualification falsely authorizes the direction on the same facts.
                            self.assertIn('CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED', self.result(missing_guard, mutant))
                    # A missing completion record does not prove failure to commence.
                    facts[self.key({'predicate': 'removal completion recorded'})] = False
                    facts[self.key({'predicate': 'noncommencement of that work by the source deadline is established'})] = None
                    self.assertNotIn('CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED', self.result(ast, facts))
                self.assertIn('not a grace period', row['semantic_note'])
                self.assertIn('does not prove', row['false_effect'])

    def test_case_scope_and_inheritance_are_not_homogenized(self):
        def row(year, number):
            return self.a[f'REG-PUGLIA-U181-DIR-{year}-{number:05d}:case-delta:noncommencement-enforcement:v1']
        for year, number in ((2024, 147), (2024, 151), (2024, 188), (2025, 117)):
            r = row(year, number)
            self.assertIn('50 m', r['condition_ast']['route_table'][0]['when']['all_of'][1]['predicate'])
            self.assertIn('infected plants only', r['true_effect'])
        self.assertIn('Bisceglie infected area', row(2025, 115)['true_effect'])
        for year, number, predecessor in ((2025, 11, row(2024, 188)),
                                          (2024, 165, row(2024, 147)),
                                          (2026, 63, row(2025, 173))):
            candidates = [r for r in self.rows if r['instrument_id'] == f'REG-PUGLIA-U181-DIR-{year}-{number:05d}'
                          and ':case-delta:' in r['stable_provision_id']]
            self.assertTrue(any(predecessor['stable_provision_id'] in r['external_dependencies'] for r in candidates))
            self.assertFalse(any(c['producer_provision_version_id'] in {r['provision_version_id'] for r in candidates}
                                 and 'noncommencement' in c['clock_id'] for c in self.b['clocks']))
        self.assertFalse(any('cases mint no clock' in (d['why'] or '').lower() for d in self.b['dispositions']))


class Round13StoredStatus(unittest.TestCase):
    setUp = StageBRepairs.setUp
    check = StageBRepairs.check
    generate = StageBRepairs.generate
    accepted_fixture = StageBRepairs.accepted_fixture

    def test_all_stored_status_claims_match_validated_none_partial_and_full_acceptance(self):
        import verify_repository as repository
        output = self.root / 'regulation/stage-b/generated'
        current = {'stages': {'A': {'canonical_artifacts': {
            str(i): {'path': str(p.relative_to(self.root))} for i, p in enumerate(self.a_paths)}},
            'B': {'canonical': {'path': 'ledger.json'},
                  'population': {'path': str(self.population.relative_to(self.root))}}}}
        for seams, expected in (((), 'NOT_ASSERTED'), ((1,), 'PARTIAL'), ((1, 2, 3, 4), 'ACCEPTED')):
            ledger = self.accepted_fixture(seams)
            original = self.generate(ledger)
            self.assertEqual(original['semantic_acceptance'], expected)
            shutil.copytree(self.root / 'generated', output, dirs_exist_ok=True)
            status_path = output / 'generation-status.json'
            validated = self.check(ledger)
            with patch.object(repository, 'ROOT', self.root):
                repository.verify_stage_b_projections(current, validated)
                for field in original:
                    for mode in ('changed', 'missing'):
                        changed = copy.deepcopy(original)
                        if mode == 'missing':
                            del changed[field]
                        else:
                            changed[field] = 'FALSE STORED CLAIM'
                        status_path.write_text(json.dumps(changed))
                        with self.subTest(acceptance=expected, field=field, mode=mode):
                            with self.assertRaises(SystemExit):
                                repository.verify_stage_b_projections(current, validated)
                for changed in (dict(original, extra_claim='ACCEPTED'),
                                dict(original, unaccepted_seams=[True, 2, 3, 4])):
                    status_path.write_text(json.dumps(changed))
                    with self.assertRaises(SystemExit):
                        repository.verify_stage_b_projections(current, validated)
                status_path.write_text(json.dumps(original))
                (output / 'unexpected.csv').write_text('stale\n')
                with self.assertRaisesRegex(SystemExit, 'unrecognized_files_in_output_dir'):
                    repository.verify_stage_b_projections(current, validated)
                (output / 'unexpected.csv').unlink()
                repository.verify_stage_b_projections(current, validated)


class RecoveryHandoffRepairs(unittest.TestCase):
    """Bounded A/B witnesses, not Stage C evidence binding or runtime evaluation."""

    def setUp(self):
        self.rows = json.loads(jurisdiction_generator.AUTHORING.read_text())
        self.by = {r['provision_version_id']: r for r in self.rows}
        self.graph = json.loads((jurisdiction_generator.OUT / 'condition-graph.json').read_text())
        with (jurisdiction_generator.OUT / 'provision-versions.csv').open(newline='') as handle:
            self.csv = {r['provision_version_id']: r for r in csv.DictReader(handle)}
        self.b = json.loads(verifier.B.read_text())

    def test_confirmation_and_routing_states_compose_without_a_clean_route_gate(self):
        from itertools import product
        failed = 'evidence proves the second test was not performed on a different genome region or not by a validly designated laboratory'
        departed = 'evidence proves the confirmation departed from the national reference-laboratory routing, with unsettled legal consequence'
        unresolved = 'confirmation requirements are not yet established and no test or laboratory disqualification is proven'
        issue = 'CONFIRMATION_VALIDITY_ADJUDICATION_REQUIRED'
        key = lambda text: json.dumps({'predicate': text}, sort_keys=True)
        cases = [
            ('REG-PUGLIA-U181-DIR-2025-00045:pest-free-positive-routing:v1',
             ['pest-free geography', 'individual positive identity',
              'second molecular test on a different genome region of the same sample or extract (Article 2(6))',
              'subspecies identification where required (Article 2(7))'],
             'PEST_FREE_CONFIRMATION_EVIDENCE_ESTABLISHED', 'PEST_FREE_CONFIRMATION_NOT_ESTABLISHED',
             'PEST_FREE_CONFIRMATION_OR_SUBSPECIES_IDENTITY_EVIDENCE_REQUIRED'),
            ('REG-PUGLIA-U181-DIR-2022-00031:pest-free-buffer-pool-confirmation:v1',
             ['pest-free or buffer-zone provenance', 'positive or doubtful pool result',
              "constituent samples tested individually by a second molecular test on a different genome region (Article 2(6)); the procedure's 'different Annex IV Section A method' is the regional restatement",
              'Section B subspecies identification'],
             'PEST_FREE_BUFFER_CONFIRMATION_EVIDENCE_ESTABLISHED', 'PEST_FREE_BUFFER_CONFIRMATION_NOT_ESTABLISHED',
             'confirmation and subspecies identity unresolved')]
        for vid, requirements, established, not_established, residual in cases:
            row = self.by[vid]
            surfaces = [row['condition_ast']]
            graphs = [g for g in self.graph['graphs'] if g['provision_version_id'] == vid]
            if row['temporal_status'] == 'SUPERSEDED':
                self.assertFalse(graphs)
                self.assertIn(vid, self.graph['historical_provision_version_ids'])
            else:
                self.assertEqual(len(graphs), 1)
                self.assertEqual(graphs[0]['expression'], surfaces[0])
                surfaces.append(graphs[0]['expression'])
            for field in ('effective_from', 'effective_to_exclusive', 'true_effect', 'false_effect', 'semantic_note'):
                self.assertEqual(self.csv[vid][field], row[field].rstrip())

            def check(ast):
                for values, failure, route_evidence in product(product((True, False, None), repeat=4),
                                                               (False, True),
                                                               ('proven departure', 'documented conforming', 'unavailable')):
                    # A proven adverse fact is not established merely because route documentation is unavailable.
                    # This is its legal truth condition, not an implementation of D's evidence acquisition.
                    has_issue = route_evidence == 'proven departure'
                    confirmed = all(v is True for v in values) and not failure
                    facts = {key(p): v for p, v in zip(requirements, values)}
                    facts.update({key(failed): failure, key(departed): has_issue,
                                  key(unresolved): not confirmed and not failure})
                    expected = not_established if failure else established if confirmed else residual
                    if has_issue:
                        expected += '; ' + issue
                    matches = [r['effect'] for r in ast['route_table']
                               if StageARepairs.condition(r['when'], facts) is True]
                    self.assertLessEqual(len(matches), 1, (vid, values, failure, route_evidence, matches))
                    self.assertEqual(matches[0] if matches else ast['otherwise']['effect'], expected)

            for ast in surfaces:
                check(ast)
                mutant = copy.deepcopy(ast)
                mutant['route_table'].append({'when': {'predicate': departed}, 'effect': issue})
                with self.assertRaises(AssertionError):
                    check(mutant)
                mutant = copy.deepcopy(ast)
                for route in mutant['route_table']:
                    if route['effect'].startswith(established):
                        route['when'] = {'all_of': [route['when'], {'not': {'predicate': departed}}]}
                with self.assertRaises(AssertionError):
                    check(mutant)

    def test_audit_status_survives_without_compiling_routine_audit_work(self):
        vid = 'EU-2017-625:Art.39:official-laboratory-audit-status:v1'
        retired = 'B-CLK-EU-625-39-audit-recurrence'
        retained = 'B-CLK-EU-625-39-immediate-withdrawal'
        row = self.by[vid]
        self.assertNotIn(retired, {c['clock_id'] for c in self.b['clocks']})
        dispositions = [d for d in self.b['dispositions'] if d['provision_version_id'] == vid]
        deferred = [d for d in dispositions if d.get('expression') == 'on a regular basis']
        self.assertEqual(len(deferred), 1)
        self.assertEqual((deferred[0]['disposition'], deferred[0]['aperture'], deferred[0]['ref']),
                         ('not_a_clock', 'DEFERRED', None))
        self.assertTrue(any(d['disposition'] == 'clock' and d['ref'] == retained for d in dispositions))
        self.assertIn('on a regular basis', row['source_quote'])
        graph = next(g for g in self.graph['graphs'] if g['provision_version_id'] == vid)
        for effect in (row['true_effect'], self.csv[vid]['true_effect'], graph['true_effect']):
            self.assertNotIn('Maintain audit oversight', effect)
            for term in ('withdraw designation', 'by task', 'unremedied'):
                self.assertIn(term, effect)
        for field in ('evidence_contract', 'false_effect'):
            self.assertIn('remedial', row[field])
        with (generator.OUT / 'clocks.csv').open(newline='') as handle:
            clocks = {c['clock_id']: c for c in csv.DictReader(handle)}
        self.assertNotIn(retired, clocks)
        self.assertEqual(clocks[retained]['producer_provision_version_id'], vid)
        self.assertEqual(clocks[retained]['kind'], 'promptness_standard')


class AcceptedSurveyPromotion(unittest.TestCase):
    def test_source_parity_preserves_literal_and_reviewed_transcription_checks(self):
        base=json.loads(verifier.B.read_text())
        verifier.verify_source_parity(base)
        for mutation in ('transcribed_value','missing_transcription','literal_phrase'):
            changed=copy.deepcopy(base)
            if mutation=='transcribed_value':
                row=next(r for r in changed['parameters'] if r['parameter_id']=='B-PAR-DGR1075-T4-olive-high-samples')
                row['value']='5000'
            elif mutation=='missing_transcription':
                changed['parameters']=[r for r in changed['parameters'] if r['parameter_id']!='B-PAR-DGR1075-T4-olive-high-samples']
            else:
                row=next(r for r in changed['clocks'] if r['clock_id']=='B-CLK-DGR1075-owner-election')
                row['source_phrase']='invented deadline phrase'
            with self.subTest(mutation=mutation),contextlib.redirect_stdout(io.StringIO()),self.assertRaises(SystemExit):
                verifier.verify_source_parity(changed)


    def test_closed_c_checks_package_and_acceptance_record(self):
        import hashlib
        import verify_repository as repository
        sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory(prefix='cordon-c-acceptance-check-') as directory:
            root=Path(directory)
            code=root/'regulation/stage-c/example.py';code.parent.mkdir(parents=True)
            code.write_text('value = 1\n')
            package_hash=hashlib.sha256(('regulation/stage-c/example.py\0'+sha(code)+'\n').encode()).hexdigest()
            evidence=root/'acceptance.json'
            record={'accepted_by':'Synthetic reviewer','promoted_package_sha256':package_hash}
            evidence.write_text(json.dumps(record))
            state={'stages':{'C':{'status':'CLOSED','accepted_by':'Synthetic reviewer',
                'canonical':{'path':'regulation/stage-c','sha256':package_hash},
                'acceptance_record':{'path':'acceptance.json','sha256':sha(evidence)}}}}
            with patch.object(repository,'ROOT',root):
                repository.verify_stage_c_acceptance(state)
                code.write_text('value = 2\n')
                with self.assertRaises(SystemExit): repository.verify_stage_c_acceptance(state)
                code.write_text('value = 1\n')
                evidence.write_text(json.dumps(record)+' ')
                with self.assertRaises(SystemExit): repository.verify_stage_c_acceptance(state)


if __name__ == '__main__':
    unittest.main()
