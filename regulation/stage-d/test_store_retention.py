"""What the store keeps, and the checks a kept reading must pass before it is replicated."""
import json
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

from cordon_d.store import REGENERABLE, kept, kept_problems


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class Retention(unittest.TestCase):
    def setUp(self):
        self.store = Path(tempfile.mkdtemp())
        blob = b'source bytes'
        digest = sha256(blob).hexdigest()
        (self.store / 'blobs/sha256' / digest[:2]).mkdir(parents=True)
        (self.store / 'blobs/sha256' / digest[:2] / digest).write_bytes(blob)
        request = {'prompt': 'read the clause', 'source_sha256': digest}
        self.request_id = sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        write(self.store / 'derived/document-readings' / f'{self.request_id}.json',
              json.dumps({'request_sha256': self.request_id, 'request': request, 'output': '{}'}))
        write(self.store / 'derived/document-readings' / f'{self.request_id}.lock', '')
        write(self.store / 'derived/reports/v1' / digest / 'report.json',
              json.dumps({'source_sha256': digest, 'extraction_version': 'v1', 'blocks': []}))
        write(self.store / 'derived/reports/relationships/r1' / f'{digest}.json',
              json.dumps({'source_sha256': digest, 'reading_version': 'r1', 'reading': {}}))
        write(self.store / 'derived/a-new-reader' / 'x.json', '{}')
        for folder in REGENERABLE:
            write(self.store / 'derived' / folder / 'cache.json', '{}')
        self.digest = digest

    def test_keeps_blobs_and_every_reading_outside_the_regenerable_folders(self):
        held = {p.as_posix() for p in kept(self.store)}
        self.assertIn(f'blobs/sha256/{self.digest[:2]}/{self.digest}', held)
        self.assertIn(f'derived/document-readings/{self.request_id}.json', held)
        self.assertIn(f'derived/reports/v1/{self.digest}/report.json', held)
        self.assertIn('derived/a-new-reader/x.json', held, 'a folder no one has shown regenerable is kept')
        self.assertFalse(any(p.endswith('.lock') for p in held))
        for folder in REGENERABLE:
            self.assertNotIn(f'derived/{folder}/cache.json', held)

    def test_a_symlink_is_not_kept_but_its_target_is(self):
        # The Claude CLI keeps `latest` pointing at the debug log it is writing now; it moves to each new reading.
        log = self.store / 'derived/reports/responses' / f'{self.request_id}.debug.log'
        write(log, 'debug')
        (log.parent / 'latest').symlink_to(log)
        held = {p.as_posix() for p in kept(self.store)}
        self.assertIn(f'derived/reports/responses/{self.request_id}.debug.log', held)
        self.assertNotIn('derived/reports/responses/latest', held)

    def test_whole_readings_pass(self):
        self.assertEqual(list(kept_problems(self.store)), [])

    def test_a_reading_under_another_request_fails(self):
        other = self.store / 'derived/document-readings' / ('0' * 64 + '.json')
        other.write_text((self.store / 'derived/document-readings' / f'{self.request_id}.json').read_text())
        self.assertEqual([p.name for p, _ in kept_problems(self.store)], [other.name])

    def test_a_truncated_reading_fails(self):
        write(self.store / 'derived/a-new-reader/y.json', '{"cut": ')
        self.assertEqual([p.name for p, _ in kept_problems(self.store)], ['y.json'])

    def test_an_assembly_in_another_version_fails(self):
        moved = self.store / 'derived/reports/v2' / self.digest / 'report.json'
        write(moved, (self.store / 'derived/reports/v1' / self.digest / 'report.json').read_text())
        self.assertEqual([p.parts[-3] for p, _ in kept_problems(self.store)], ['v2'])

    def test_only_limits_the_check(self):
        write(self.store / 'derived/a-new-reader/y.json', '{"cut": ')
        self.assertEqual(list(kept_problems(self.store, only=['derived/a-new-reader/x.json'])), [])


if __name__ == '__main__':
    unittest.main()
