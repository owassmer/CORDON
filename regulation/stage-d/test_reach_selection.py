"""Which held laboratory reports a decision's reach selects for reading (SPEC.md, "Admission")."""
import json
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from cordon_d.findings import reach_selection
from cordon_d.report_relations import READING_VERSION, path as relation_path
from test_report_relations import reading

CUTOFF = datetime(2026, 10, 1, tzinfo=timezone.utc)
START = date(2022, 9, 22)


def route(number, year, lab):
    return f'https://example.invalid/documento?nomeFile=DatiCampioniXF/PDF/RAPPORTO_PROVA_N_{number}_{year}_{lab}.pdf'


def group(day, *routes):
    member = SimpleNamespace(report_routes=tuple(('LINK_RAPPORTO', r) for r in routes))
    return SimpleNamespace(day=day, members=(member,))


class ReachSelection(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.store = Path(tempfile.mkdtemp())
        self.reports = {
            'inside': route(5, 2023, 'CNR'), 'edge': route(6, 2022, 'IAMB'), 'outside': route(7, 2021, 'UNIBA'),
            'undated': route(8, 2023, 'UNILE'), 'unrouted': route(9, 2024, 'UNIFG'), 'old': route(10, 2020, 'CRSFA'),
            'decoy': route(10, 2021, 'CRSFA'),
        }
        self.digest = {name: name.ljust(64, '0') for name in self.reports}
        (self.root / 'records.json').write_text(json.dumps([
            {'url': url, 'captured_at': '2026-09-01T00:00:00+00:00', 'sha256': self.digest[name]}
            for name, url in self.reports.items()]))
        self.groups = [
            group(date(2024, 5, 1), self.reports['inside']),
            group(date(2022, 9, 22), self.reports['edge']),            # the reach's first day is inside it
            group(date(2022, 9, 21), self.reports['outside']),         # the day before is not
            group(date(2019, 1, 1), self.reports['old'], self.reports['decoy']),
            group(None, self.reports['undated']),                      # its only routing observation has no day
        ]

    def select(self):
        return reach_selection(self.groups, self.root, self.store, start=START, known_through=CUTOFF)

    def write(self, name, relations):
        target = relation_path(self.store, self.digest[name])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({'source_sha256': self.digest[name], 'reading_version': READING_VERSION,
                                      'complete': True, 'reading': relations}))

    def test_the_route_rule_selects_by_the_latest_routing_day_and_keeps_undated_reports(self):
        pages, relationships, counts = self.select()
        expected = {self.digest[n] for n in ('inside', 'edge', 'undated', 'unrouted')}
        self.assertEqual(pages, expected)
        self.assertEqual(relationships, expected)
        self.assertEqual((counts['in_reach'], counts['undated']), (2, 2))

    def test_a_declared_predecessor_is_nominated_by_its_route_number_then_selected_once_identified(self):
        replacing = reading('5/2023', '01/05/2024', issuer='CNR',
                            previous=dict(issuer='CNR', number='10/2020', date=None, protocol=None))
        self.write('inside', replacing.relations)
        pages, relationships, counts = self.select()
        self.assertNotIn(self.digest['old'], pages)
        self.assertIn(self.digest['old'], relationships, 'a report printing the declared number and year is read')
        self.assertNotIn(self.digest['decoy'], relationships, 'the same number in another year is not')
        self.assertEqual(counts['nominated_for_relationships'], 1)
        # Once the nominated report's own reading states that identity, the reader's match resolves it.
        self.write('old', reading('10/2020', '01/02/2020', issuer='CNR').relations)
        pages, relationships, counts = self.select()
        self.assertIn(self.digest['old'], pages)
        self.assertEqual(counts['predecessors'], 1)

    def test_the_reach_moves_with_the_decision_date(self):
        later = reach_selection(self.groups, self.root, self.store, start=date(2024, 6, 1), known_through=CUTOFF)[0]
        self.assertNotIn(self.digest['inside'], later)
        self.assertNotIn(self.digest['edge'], later)


if __name__ == '__main__':
    unittest.main()
