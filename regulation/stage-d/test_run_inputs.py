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

    def test_every_c_reaching_path_refuses_a_missing_date_or_cutoff(self):
        cutoff = datetime(2026, 9, 24, tzinfo=timezone.utc)
        for script, arguments, missing in (
                ('read_prescriptions.py', [], '--at, --known-through'),
                ('read_prescriptions.py', ['--at', '2026-09-24'], '--known-through'),
                ('read_notice_routes.py', ['--known-through', cutoff.isoformat()], '--at'),
                ('read_reports.py', [], '--known-through'),
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
