"""A subscription usage limit stops every reader of the shared transport and is never a reading limit.

The six readers that share `cordon_d.document_subscription` are driven here with a
usage-limit reply from the subscription CLI itself (`subprocess.run` patched), so the
classification under test is the transport's own. Each reader must raise `UsageLimit`,
retain nothing, and its driver must stop instead of writing the failure as an entry's cause.
"""
import importlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pymupdf

from cordon_d import albo_postings, case_prescriptions, held_acts, judgments, notice_routes, removal_events
from cordon_d.document_subscription import TransportFailure, UsageLimit, claude_failure
from cordon_d.store import put_bytes

ROOT = Path(__file__).resolve().parents[2]
CLAUDE_LIMIT = SimpleNamespace(returncode=1, stderr='', stdout=json.dumps(
    {'type': 'result', 'subtype': 'success', 'is_error': True,
     'result': "You've hit your session limit · resets 5pm (Europe/Rome)"}))
CODEX_LIMIT = SimpleNamespace(returncode=1, stdout='',
                              stderr="ERROR: You've hit your usage limit. Try again at 5:00 PM.")
GA = ('<ga><h:div xmlns:h="http://www.w3.org/1999/xhtml">'
      '<h:div>Il Tribunale Amministrativo Regionale per la Puglia pronuncia la presente sentenza.</h:div>'
      '<h:div>Annulla la determinazione n. 12 del 3 marzo 2024.</h:div></h:div></ga>')


def pdf(text):
    document = pymupdf.open()
    document.new_page().insert_text((72, 72), text)
    data = document.tobytes()
    document.close()
    return data


def script(name):
    sys.path.insert(0, str(ROOT / 'scripts'))
    try:
        return importlib.import_module(name)
    finally:
        sys.path.remove(str(ROOT / 'scripts'))


class UsageLimitStopsEveryReader(unittest.TestCase):
    def setUp(self):
        self._directory = TemporaryDirectory()
        self.store = Path(self._directory.name)
        self.order = put_bytes(self.store, pdf('Determinazione n. 51 del 24/03/2026. Si ordina la rimozione.'))
        self.decision = put_bytes(self.store, GA.encode())

    def tearDown(self):
        self._directory.cleanup()

    def retained(self):
        return sorted(p.name for p in (self.store / 'derived/document-readings').glob('*.json'))

    def stops(self, reply, read):
        with patch('cordon_d.document_subscription.subprocess.run', return_value=reply) as run:
            with self.assertRaises(UsageLimit):
                read()
        self.assertEqual(run.call_count, 1)  # one request, then the stop: no retry
        self.assertEqual(self.retained(), [])  # nothing retained, so nothing replays as a reading

    def test_the_transport_classifies_a_limit_as_the_subscription_s_not_the_source_s(self):
        reading, error = claude_failure(1, CLAUDE_LIMIT.stdout, '')
        self.assertIsNone(reading)
        self.assertIsInstance(error, UsageLimit)
        self.assertIsInstance(error, TransportFailure)
        retries = json.dumps({'is_error': True, 'subtype': 'error_max_structured_output_retries', 'result': ''})
        self.assertNotIsInstance(claude_failure(1, retries, '')[1], TransportFailure)

    def test_albo_postings_stops(self):
        self.stops(CODEX_LIMIT, lambda: albo_postings.posted_identity(self.order, self.store, execute=True))

    def test_case_prescriptions_stops(self):
        self.stops(CLAUDE_LIMIT, lambda: case_prescriptions.read_prescription(self.order, self.store, execute=True))

    def test_notice_routes_stops(self):
        self.stops(CLAUDE_LIMIT, lambda: notice_routes.read_notice_route(self.order, self.store, execute=True))

    def test_judgments_stops(self):
        self.stops(CLAUDE_LIMIT, lambda: judgments.read_judgment(self.decision, self.store, execute=True))
        self.stops(CLAUDE_LIMIT, lambda: judgments.read_disposition(self.decision, self.store, execute=True))

    def test_held_acts_stops(self):
        with TemporaryDirectory() as root:
            (Path(root) / 'act.txt').write_text('DETERMINAZIONE n. 7 del 2024\fModifica la DET 51/2026.\n')
            self.stops(CLAUDE_LIMIT, lambda: held_acts.read_act('act.txt', root, self.store, execute=True))

    def test_removal_events_only_replays_so_no_limit_can_reach_it(self):
        with patch('cordon_d.document_subscription.subprocess.run', return_value=CLAUDE_LIMIT) as run:
            with self.assertRaises(FileNotFoundError):
                removal_events.retained_publication_attestation('0' * 64, self.store)
        run.assert_not_called()
        self.assertEqual(self.retained(), [])

    def test_the_drivers_stop_rather_than_record_the_limit_as_an_entry_s_cause(self):
        limit = UsageLimit("Claude subscription usage limit: You've hit your session limit")
        read_judgments = script('read_judgments')
        with patch.object(read_judgments, 'read_judgment', side_effect=limit), self.assertRaises(UsageLimit):
            read_judgments.read_one((self.decision, 'u'), dict(execute=False), held={})
        with patch.object(read_judgments, 'store_root', return_value=self.store), \
                patch.object(read_judgments, 'read_disposition', side_effect=limit), self.assertRaises(UsageLimit):
            read_judgments.read_disposition_one((self.decision, 'u'), dict(execute=False), {}, {})
        read_notice_routes = script('read_notice_routes')
        read_notice_routes._WORKER.update(store=self.store, snapshot=None, postings={})
        with patch.object(read_notice_routes, 'read_notice_route', side_effect=limit), self.assertRaises(UsageLimit):
            read_notice_routes.read_one(('DET 51/2026', self.order, 'u'), dict(execute=False), None)
        read_prescriptions = script('read_prescriptions')
        read_prescriptions._WORKER.update(store=self.store, snapshot=None)
        with patch.object(read_prescriptions, 'read_prescription', side_effect=limit), self.assertRaises(UsageLimit):
            read_prescriptions.read_one(('DET 51/2026', self.order, 'u'), dict(execute=False), None)
        with patch.object(held_acts, 'selected', return_value=([dict(path='act.txt', instruments=[])], 1)), \
                patch.object(held_acts, 'read_act', side_effect=limit), self.assertRaises(UsageLimit):
            read_prescriptions.held_act_changes([], None, self.store, dict(execute=False))
        with self.assertRaises(SystemExit) as stop:
            read_prescriptions.stopped(limit)
        self.assertEqual(stop.exception.code, 3)

    def test_a_reading_failure_still_becomes_the_entry_s_cause(self):
        read_judgments = script('read_judgments')
        with patch.object(read_judgments, 'read_judgment', side_effect=RuntimeError('no reading')):
            entry = read_judgments.read_one((self.decision, 'u'), dict(execute=False), held={})
        self.assertEqual(entry['cause'], 'RuntimeError: no reading')


if __name__ == '__main__':
    unittest.main()
