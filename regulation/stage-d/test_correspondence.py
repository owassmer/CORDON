from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from cordon_d.correspondence import ReferenceInventory, ReferenceReading
from cordon_d.evidence import Source, Support, file_digest


class CorrespondenceTests(TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.sources = []
        for identity, access in [('inventory', 'public'), ('cadastre', 'public'), ('title', 'controlled')]:
            path = self.root / identity
            path.write_text(identity)
            self.sources.append(Source(identity, identity, file_digest(path), 'official-record', access))
        self.now = datetime(2026, 9, 10, tzinfo=timezone.utc)
        self.fields = ('municipality', 'section', 'sheet', 'parcel')
        self.components = tuple(zip(self.fields, ('A662', 'A', '81', '340')))

    def reading(self, source, selector='row:1', *, components=None, known=True, role='published-reference'):
        return ReferenceReading(source, selector, role, self.components if components is None else components,
                                (Support(source, selector, 'The source explicitly states these reference components.'),),
                                self.now if known else None, '2025-12-31' if source == 'inventory' else None)

    def inventory(self, *readings):
        return ReferenceInventory(tuple(self.sources), readings, root=self.root)

    def matches(self, inventory, **kwargs):
        return inventory.matches(components=self.fields, known_through=self.now,
                                 left_sources=frozenset({'inventory'}), **kwargs)

    def test_repeated_source_occurrences_survive_and_partial_match_has_no_title_effect(self):
        inventory = self.inventory(self.reading('inventory'), self.reading('cadastre'),
                                   self.reading('cadastre', 'row:2'))
        matches = self.matches(inventory)
        self.assertEqual(len(matches), 2)
        self.assertEqual({r.right.selector for r in matches}, {'row:1', 'row:2'})
        self.assertEqual(matches[0].claim, 'same published reference components')
        self.assertEqual(matches[0].left.source_as_of, '2025-12-31')
        self.assertIsNone(matches[0].right.source_as_of)
        self.assertEqual(inventory.matches(components=self.fields + ('annex',), known_through=self.now), ())

    def test_missing_or_different_section_is_not_a_wildcard(self):
        missing = tuple((k, v) for k, v in self.components if k != 'section')
        different = tuple((k, 'G' if k == 'section' else v) for k, v in self.components)
        self.assertEqual(self.matches(self.inventory(self.reading('inventory'), self.reading('cadastre', components=missing))), ())
        self.assertEqual(self.matches(self.inventory(self.reading('inventory'), self.reading('cadastre', components=different))), ())

    def test_access_and_unknown_knowledge_cannot_be_upgraded(self):
        inventory = self.inventory(self.reading('inventory'), self.reading('title'),
                                   self.reading('cadastre', known=False))
        self.assertEqual(self.matches(inventory), ())
        self.assertEqual(len(self.matches(inventory, permitted_controlled_sources=frozenset({'title'}))), 1)
        before = datetime(2026, 9, 9, tzinfo=timezone.utc)
        self.assertEqual(inventory.matches(components=self.fields, known_through=before,
                                          permitted_controlled_sources=frozenset({'title'})), ())

    def test_consumption_rechecks_original_hash(self):
        inventory = self.inventory(self.reading('inventory'), self.reading('cadastre'))
        (self.root / 'cadastre').write_text('changed source')
        with self.assertRaisesRegex(ValueError, 'Source changed'):
            self.matches(inventory)

    def test_duplicate_occurrence_and_unanchored_support_are_rejected(self):
        reading = self.reading('inventory')
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.inventory(reading, reading)
        forged = ReferenceReading('inventory', 'row:99', 'published-reference', self.components,
                                  reading.support, self.now)
        with self.assertRaisesRegex(ValueError, 'own physical occurrence'):
            self.inventory(forged)
