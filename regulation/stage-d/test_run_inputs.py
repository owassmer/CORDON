"""The run states its evaluation context and grant; verify.py fails when a default returns."""
from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock
import json
import shutil
import subprocess
import sys
import unittest

from cordon_d import case_prescriptions, notice_routes, reports, source_associations
from cordon_d.evidence import Evidence
from cordon_d.findings import findings
import verify

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'scripts'))
import read_notice_routes  # noqa: E402
import read_prescriptions  # noqa: E402
import read_reports  # noqa: E402


class RunInputTests(unittest.TestCase):
    def test_verify_requires_a_supplier_and_fails_when_the_grant_defaults_to_empty(self):
        verify.verify()
        with TemporaryDirectory() as directory:
            owner = Path(directory)
            for name in ('contracts.json', 'predicate-contracts.json', 'additional-input-contracts.json',
                         'source-bindings.json'):
                shutil.copy(HERE / name, owner / name)
            contracts = json.loads((owner / 'contracts.json').read_text())
            for contract in contracts['contracts']:
                contract.pop('run_input', None)
            (owner / 'contracts.json').write_text(json.dumps(contracts))
            with mock.patch.object(verify, 'D', owner), \
                    self.assertRaisesRegex(ValueError, 'neither a source binding nor a run input'):
                verify.verify()

        def view(self, *, context, event_date, known_through, permitted_controlled_sources=frozenset()):
            raise AssertionError('not called')
        with mock.patch.object(Evidence, 'view', view), \
                self.assertRaisesRegex(ValueError, 'permitted_controlled_sources has a default'):
            verify.verify()

    def test_verify_surfaces_a_missing_dependency_as_itself(self):
        def missing(name, package=None):
            raise ModuleNotFoundError("No module named 'cordon_c'", name='cordon_c')
        with mock.patch.object(verify.importlib, 'import_module', missing), \
                self.assertRaisesRegex(ModuleNotFoundError, "'cordon_c'"):
            verify.require_run_parameters('cordon_d.evidence.Evidence.view', ['known_through'], 'evaluation-context')

    def test_verify_fails_when_the_prescription_cutoff_defaults_to_none(self):
        def c_result(snapshot, record, at, *, evaluated_at=None, **held):
            raise AssertionError('not called')
        with mock.patch.object(case_prescriptions, 'c_result', c_result), \
                self.assertRaisesRegex(ValueError, 'evaluated_at has a default'):
            verify.verify()

    def test_verify_fails_when_reports_read_every_held_record_by_default(self):
        def every_report(root, store, *, extraction_version, known_through=None):
            raise AssertionError('not called')
        with mock.patch.object(reports, 'reports', every_report), \
                self.assertRaisesRegex(ValueError, 'known_through has a default'):
            verify.verify()

    def test_an_original_captured_after_the_cutoff_is_left_out(self):
        cutoff = datetime(2025, 7, 14, 10, tzinfo=timezone.utc)
        before, after = '2025-07-01T09:00:00+00:00', '2026-09-14T01:17:59+00:00'
        orders = [dict(sha256='a' * 64, captured_at=before, url='https://example.invalid/DDS_117_2025.pdf'),
                  dict(sha256='b' * 64, captured_at=after, url='https://example.invalid/DDS_22_2026.pdf'),
                  dict(sha256='c' * 64, captured_at=after, url='https://example.invalid/DDS_5_2025.pdf'),
                  dict(sha256='c' * 64, captured_at=before, url='https://example.invalid/DDS_5_2025.pdf')]
        events = [dict(sha256='d' * 64, captured_at=after, kind='publication', url='https://example.invalid/albo'),
                  dict(sha256='e' * 64, captured_at=before, kind='event', url='https://example.invalid/tar')]
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for name, records in (('removal-orders', orders), ('removal-events', events)):
                (root / 'corpus/sources' / name).mkdir(parents=True)
                (root / 'corpus/sources' / name / 'records.json').write_text(json.dumps(records))
            postings = root / 'postings.json'
            postings.write_text(json.dumps(dict(events={'X-2025-117': [
                dict(kind='municipal-publication-start', publisher='Comune', source='d' * 64, occurred='2025-07-02'),
                dict(kind='municipal-publication-start', publisher='Comune', source='a' * 64,
                     occurred='2025-07-02')]})))
            with mock.patch.object(read_prescriptions, 'ROOT', root):
                self.assertEqual([digest for _, digest, _ in read_prescriptions.population(cutoff)],
                                 ['a' * 64, 'c' * 64])
                self.assertEqual(len(list(read_prescriptions.population(datetime(2026, 9, 24, tzinfo=timezone.utc)))),
                                 3)
                intervals, left_out = read_notice_routes.load_postings([postings], cutoff)
                judgments = root / 'judgments.json'
                judgments.write_text(json.dumps([dict(liveness_closures={'X-2025-117': [
                    dict(effect='annulled', since='2025-07-10', decision=dict(source='e' * 64)),
                    dict(effect='suspended', since='2025-07-11', decision=dict(source='d' * 64))]})]))
                closures = read_prescriptions.load_closures(judgments, cutoff)
            self.assertEqual([c['effect'] for c in closures['X-2025-117']], ['annulled'])
            self.assertEqual([i['sources'] for i in intervals['X-2025-117']], [['a' * 64]])
            self.assertEqual([e['source'] for e in left_out], ['d' * 64])

    def test_held_acts_and_certificates_after_the_cutoff_are_left_out(self):
        cutoff = datetime(2025, 7, 14, 10, tzinfo=timezone.utc)
        early, late = 'corpus/early.txt', 'corpus/late.txt'
        chosen = [dict(path=early, instruments=['X-2025-117']), dict(path=late, instruments=['X-2025-117'])]
        dates = {early: datetime(2025, 7, 1, tzinfo=timezone.utc), late: datetime(2026, 9, 4, tzinfo=timezone.utc)}
        read = []

        def read_act(path, root, store, **options):
            read.append(path)
            return dict(request_sha256='0' * 64, reading=dict(identity={}, relationships=[], issues=[]))
        from cordon_d import held_acts, removal_events
        with mock.patch.object(held_acts, 'selected', return_value=(chosen, 2)), \
                mock.patch.object(held_acts, 'read_act', read_act), \
                mock.patch.object(held_acts, 'stated_changes', return_value=[]), \
                mock.patch.object(read_prescriptions, 'admitted_at', return_value=dates):
            _, report = read_prescriptions.held_act_changes([], None, None, dict(execute=False), cutoff)
        self.assertEqual(read, [early])
        self.assertEqual([item['path'] for item in report['not_held_by_cutoff']], [late])
        # A git failure raises: "could not date" is not "not held".
        with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(128, 'git')), \
                self.assertRaises(subprocess.CalledProcessError):
            read_prescriptions.admitted_at([early])
        # A publication certificate whose source was captured after the cutoff is not read.
        before, after = '2025-07-01T09:00:00+00:00', '2026-09-14T01:17:59+00:00'
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for name, records in (('removal-orders', [dict(sha256='a' * 64, captured_at=before, url='https://x.invalid/a')]),
                                  ('removal-events', [dict(sha256='b' * 64, captured_at=after, kind='event',
                                                           url='https://x.invalid/b')])):
                (root / 'corpus/sources' / name).mkdir(parents=True)
                (root / 'corpus/sources' / name / 'records.json').write_text(json.dumps(records))
            readings = root / 'store/derived/document-readings'
            readings.mkdir(parents=True)
            for stem, source in (('held-certificate', 'a' * 64), ('later-certificate', 'b' * 64)):
                (readings / f'{stem}.json').write_text(json.dumps(dict(request=dict(
                    prompt='Read this publication certificate.', sources=[source]))))
            attested = []
            with mock.patch.object(read_prescriptions, 'ROOT', root), \
                    mock.patch.object(removal_events, 'retained_publication_attestation',
                                      lambda stem, store: attested.append(stem)), \
                    mock.patch.object(removal_events, 'connect_publication_attestation',
                                      lambda attestation, declarations, acquisitions: None), \
                    mock.patch.object(removal_events, 'connected_publications', lambda publications, measures: []):
                _, failures = read_prescriptions.held_events([], root / 'store', cutoff)
            self.assertEqual((attested, failures), (['held-certificate'], []))

    def test_a_join_is_refused_while_a_monitoring_release_postdates_the_cutoff(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / 'monitoring'
            (root / 'campaign').mkdir(parents=True)
            (root / 'campaign/releases.json').write_text(json.dumps([dict(
                url='https://x.invalid/CAMP.xlsx', path='CAMP.xlsx', captured_at='2025-07-01T09:00:00+00:00')]))
            layer = root / 'sit/Operationals2/Service/1'
            layer.mkdir(parents=True)
            (layer / 'layer.json').write_text('{}')
            (layer / 'release.json').write_text(json.dumps(dict(
                url='https://x.invalid/MapServer/1', captured_through='2026-09-10T21:31:39+00:00')))
            for flag in ('--join-summary', '--join-output'):
                with self.subTest(flag=flag):
                    run = subprocess.run([sys.executable, str(ROOT / 'scripts/read_reports.py'),
                                          '--monitoring-root', str(root), flag, str(Path(directory) / 'out.json'),
                                          '--known-through', '2025-07-14T12:00:00+02:00'],
                                         capture_output=True, text=True, timeout=300)
                    self.assertEqual(run.returncode, 2, run.stderr[-600:])
                    self.assertIn('1 retained monitoring releases were captured after --known-through', run.stderr)
                    self.assertIn('https://x.invalid/MapServer/1', run.stderr)
            self.assertEqual(read_reports.monitoring_captured_after(root, datetime(2026, 9, 11, tzinfo=timezone.utc)), [])

    def test_every_c_reaching_path_refuses_a_missing_date_or_cutoff(self):
        cutoff = datetime(2026, 9, 24, tzinfo=timezone.utc)
        for script, arguments, missing in (
                ('read_prescriptions.py', [], '--at, --known-through'),
                ('read_prescriptions.py', ['--at', '2026-09-24'], '--known-through'),
                ('read_notice_routes.py', ['--known-through', cutoff.isoformat()], '--at'),
                ('read_reports.py', ['--join-summary', '/nonexistent/summary.json'], '--known-through'),
                ('read_reports.py', ['--join-output', '/nonexistent/join.jsonl'], '--known-through'),
                ('read_prescriptions.py', ['--at', '2026-09-24', '--known-through', cutoff.isoformat(),
                                           '--records', '/nonexistent/records.json'],
                 '--permitted-controlled-sources'),
                ('read_reports.py', ['--known-through', '2026-09-24T00:00:00'], 'timezone-aware')):
            with self.subTest(script=script, arguments=arguments):
                run = subprocess.run([sys.executable, str(ROOT / 'scripts' / script), *arguments],
                                     capture_output=True, text=True, timeout=300)
                self.assertEqual(run.returncode, 2, run.stderr[-600:])
                self.assertIn(missing if missing != 'timezone-aware' else 'invalid run_instant value', run.stderr)
        held = object.__new__(Evidence)
        refusals = (
            (TypeError, lambda: held.view(context='c', event_date=date(2024, 9, 2), known_through=cutoff)),
            (TypeError, lambda: held.view(context='c', event_date=date(2024, 9, 2), known_through=cutoff,
                                          permitted_controlled_sources=None)),
            (TypeError, lambda: case_prescriptions.c_result(None, {}, date(2024, 9, 2))),
            (ValueError, lambda: case_prescriptions.c_result(None, {}, date(2024, 9, 2), evaluated_at=None)),
            (TypeError, lambda: case_prescriptions.c_result(None, {}, None, evaluated_at=cutoff)),
            (TypeError, lambda: notice_routes.c_result(None, {}, None)),
            (TypeError, lambda: list(reports.reports(ROOT, ROOT, extraction_version='v'))),
            (ValueError, lambda: list(reports.reports(ROOT, ROOT, extraction_version='v', known_through=None))),
            (TypeError, lambda: list(source_associations.associations(ROOT, ROOT))),
            (ValueError, lambda: list(source_associations.associations(ROOT, ROOT, known_through=None))),
            (TypeError, lambda: findings((), ROOT, ROOT, extraction_version='v')))
        for index, (error, call) in enumerate(refusals):
            with self.subTest(path=index), self.assertRaises(error):
                call()


if __name__ == '__main__':
    unittest.main()
