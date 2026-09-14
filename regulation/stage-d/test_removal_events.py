"""Publication records supply exact anchors, never recipient effect or performance."""
from dataclasses import replace
from datetime import date, datetime
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from zoneinfo import ZoneInfo

from cordon_c import Snapshot
from cordon_d.calendar import national_calendar
from cordon_d.removal_events import publication_records, publication_deadline, connected_publications, parsec_publications
from cordon_d.notices import parsec_publication_declarations


class ParsecPublication(unittest.TestCase):
    def test_attachment_connection_preserves_corrections_and_predecessor_mentions(self):
        from cordon_d.store import store_root
        digest = '1c2ba8015a26fcd2770b1283c8521c8bc534d69eeb46efd990ca9d60d9479854'
        path = store_root(Path(__file__)) / 'blobs/sha256' / digest[:2] / digest
        if not path.exists():
            self.skipTest('Retained source store unavailable')
        root = Path(__file__).resolve().parents[2]
        acquisitions = json.loads((root / 'corpus/sources/removal-orders/records.json').read_text())
        # Binding-only fixtures: identities independently read on original first
        # pages. This check does not qualify their whole-measure interpretation.
        measures = [SimpleNamespace(identity=identity, adopted=date.fromisoformat(adopted),
                    response={'request': {'sources': [source]}}) for identity, adopted, source in [
            ('REG-PUGLIA-U181-DIR-2025-00201', '2025-11-24',
             'ed2da089d5285f2ec4c8b58202095bc0852cc8fb934c978c82779d3cd06d14f4'),
            ('REG-PUGLIA-U181-DIR-2026-00063', '2026-04-03',
             '92cf97a3346c10626894979321e114dd57d2c1f5edd6f473a1faa880df31dd28')]]
        kwargs = dict(publisher='Comune di Cagnano Varano',
                      source_url='https://trasparenza.parsec326.it/en/widget/web/cagnano-varano/albo-pretorio',
                      acquisitions=acquisitions)
        rows = {p.source_fields['source_fields']['Nro']: p
                for p in parsec_publications(path, measures=measures, **kwargs)}
        self.assertEqual(rows['369'].document, measures[1].identity)
        self.assertEqual(rows['369'].events[1].occurred, date(2026, 4, 10))
        self.assertEqual(rows['1109'].document, rows['1110'].document)
        self.assertNotEqual(rows['1109'].events[0].identity, rows['1110'].events[0].identity)
        self.assertTrue(all(not p.events for p in parsec_publications(path, measures=[], **kwargs)))
        from cordon_c.core import MissingInput
        class UnresolvedMeasure:
            response = {'request': {'sources': ['unresolved-source']}}

            @property
            def identity(self):
                raise MissingInput('Unrecovered issuing authority')

        mixed = list(parsec_publications(path, measures=[UnresolvedMeasure(), *measures], **kwargs))
        self.assertEqual(mixed, list(rows.values()))
        self.assertEqual(connected_publications(mixed, [UnresolvedMeasure(), *measures]),
                         connected_publications(mixed, measures))

    def test_retained_history_preserves_separate_correction_publications(self):
        from cordon_d.store import store_root
        digest = '1c2ba8015a26fcd2770b1283c8521c8bc534d69eeb46efd990ca9d60d9479854'
        path = store_root(Path(__file__)) / 'blobs/sha256' / digest[:2] / digest
        if not path.exists():
            self.skipTest('Retained source store unavailable')
        rows = list(parsec_publication_declarations(path, publisher='Comune di Cagnano Varano',
                    source_url='https://trasparenza.parsec326.it/en/widget/web/cagnano-varano/albo-pretorio'))
        self.assertEqual(len(rows), 9)
        by_number = {r.values['source_fields']['Nro']: r for r in rows}
        self.assertEqual(by_number['958'].values['declared_dates'], {
            'Data inizio pubb.': '2025-10-27', 'Data fine pubb.': '2025-11-03'})
        self.assertEqual(by_number['369'].values['declared_dates'], {
            'Data inizio pubb.': '2026-04-03', 'Data fine pubb.': '2026-04-10'})
        for number, attachment in [('1110', '3814497_ATT_000135887_31693.pdf'),
                                   ('1109', '3814484_ATT_000135886_31692.pdf')]:
            row = by_number[number]
            self.assertEqual(row.values['declared_dates']['Data fine pubb.'], '2025-12-03')
            self.assertTrue(row.values['document_routes'][0]['url'].endswith(attachment))
        self.assertIn('ERRATA CORRIGE', by_number['1110'].values['source_fields']['Oggetto'])
        self.assertNotEqual(by_number['1110'].locator, by_number['1109'].locator)
        self.assertNotIn('document', by_number['369'].values)
        self.assertNotIn('events', by_number['1110'].values)


class MunicipalPublication(unittest.TestCase):
    def read(self, row):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'register.json'
            path.write_text(json.dumps({'content': [row]}))
            return next(publication_records(path))

    def row(self):
        # Synthetic record using the publisher's native fields. Regional and
        # municipal identities/dates deliberately differ.
        return {'id': 'test-entry', 'pfoPblTpAtto': {'pfoPblEnti': {'dlNome': 'Comune di Capurso'}},
                'dlOgg': 'Sezione Osservatorio Fitosanitario DDS N. 00991 del 06/05/2024',
                'niNumAtto': '9789', 'dtAtto': '2024-05-08', 'dbStato': 'SCADUTO',
                'dtAnnul': None, 'dtIniPubl': '2024-05-08', 'dtFinPubl': '2024-05-15'}

    def test_regional_identity_does_not_come_from_incoming_protocol(self):
        p = self.read(self.row())
        self.assertEqual(p.document, 'REG-PUGLIA-U181-DIR-2024-00991')
        self.assertEqual(p.document_date, date(2024, 5, 6))
        self.assertEqual(p.source_fields['niNumAtto'], '9789')
        self.assertEqual([e.occurred for e in p.events], [date(2024, 5, 8), date(2024, 5, 15)])
        self.assertTrue(all(e.recipient is None for e in p.events))
        self.assertEqual({e.kind for e in p.events}, {'municipal-publication-start', 'municipal-publication-end'})

    def test_publication_enters_accepted_clock_with_its_scope(self):
        p = self.read(self.row())
        kwargs = dict(document=p.document, competent_publisher=p.publisher,
                      zone=ZoneInfo('Europe/Rome'), calendar=national_calendar())
        # Three calendar days ends on Saturday; C applies its accepted extension
        # and exclusive midnight convention using the supplied national baseline.
        end = publication_deadline(Snapshot.load(), 'B-CLK-DGR1866-owner-election',
                                   p.document_date, p, **kwargs)
        self.assertEqual(end, datetime(2024, 5, 21, tzinfo=ZoneInfo('Europe/Rome')))
        for change in [dict(document='another-act'), dict(competent_publisher='Comune di Triggiano')]:
            with self.assertRaises(ValueError):
                publication_deadline(Snapshot.load(), 'B-CLK-DGR1866-owner-election',
                                     p.document_date, p, **(kwargs | change))
        with self.assertRaises(ValueError):
            p.events[0].anchor(kind='recipient-notification', document=p.document,
                               recipient='named owner', precision='date')

    def test_act_link_requires_adoption_date_as_well_as_number(self):
        p = self.read(self.row())
        self.assertEqual(connected_publications([p], [SimpleNamespace(identity=p.document, adopted=p.document_date)]), (p,))
        self.assertEqual(connected_publications([p], [SimpleNamespace(identity=p.document, adopted=date(2024, 5, 8))]), ())

    def test_ambiguous_subject_and_annulment_do_not_supply_events(self):
        row = self.row()
        row['dlOgg'] += ' e DDS N. 00992 del 07/05/2024'
        p = self.read(row)
        self.assertIsNone(p.document)
        self.assertEqual(p.events, ())
        row = self.row() | {'dtAnnul': '2024-05-10'}
        self.assertEqual(self.read(row).events, ())


class RetainedMunicipalPublication(unittest.TestCase):
    """Direct register readings checked locally; CI has no source store."""
    @classmethod
    def setUpClass(cls):
        from cordon_d.store import blob_path, store_root
        cls.path = blob_path(store_root(Path(__file__).resolve()),
                            '306336cb7351e151a29fa8738f81a8694e35b54d6eeb50b5273aaacc5bbfee63')
        if not cls.path.exists():
            raise unittest.SkipTest('Retained municipal source store not present')

    def test_actual_records_and_conditional_clock_boundaries(self):
        readings = {p.document: p for p in publication_records(self.path) if p.document}
        # Expected values read directly from the retained municipal JSON and
        # checked against its linked original acts, not generated by this reader.
        expected = [
            (2024, 52, '2024-05-06', '2024-05-08', '2024-05-15', '2024-05-21', '1866'),
            (2024, 58, '2024-05-16', '2024-05-20', '2024-05-26', '2024-05-30', '1866'),
            (2024, 82, '2024-07-09', '2024-07-16', '2024-07-23', '2024-07-27', '1866'),
            (2024, 108, '2024-08-16', '2024-08-19', '2024-08-26', '2024-08-30', '1866'),
            (2024, 188, '2024-12-12', '2024-12-13', '2024-12-20', '2024-12-24', '1593'),
        ]
        for year, number, adopted, start, end, boundary, plan in expected:
            p = readings[f'REG-PUGLIA-U181-DIR-{year}-{number:05d}']
            with self.subTest(document=p.document):
                self.assertEqual(p.document_date.isoformat(), adopted)
                self.assertEqual([e.occurred.isoformat() for e in p.events], [start, end])
                result = publication_deadline(Snapshot.load(), f'B-CLK-DGR{plan}-owner-election',
                    p.document_date, p, document=p.document, competent_publisher='Comune di Capurso',
                    zone=ZoneInfo('Europe/Rome'), calendar=national_calendar())
                self.assertEqual(result.date().isoformat(), boundary)
        p = readings['REG-PUGLIA-U181-DIR-2025-00022']
        self.assertEqual(p.document_date, date(2025, 2, 15))
        self.assertEqual([e.occurred for e in p.events], [date(2025, 2, 17), date(2025, 2, 24)])


class RetainedRegionalPublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from cordon_d.store import blob_path, store_root
        cls.paths = [blob_path(store_root(Path(__file__).resolve()), h) for h in [
            'b232863e6f680c8df35ab260b14e3429a512f17837ee197df4a41ba9bc632150',
            '25a01b41e4b5911c6a32a16b8f55a99ba8528bec99d760be7d58d4eed9ecd135',
            '4c66e7b53bdba441cb4ff0b974e649dbd411834ae27fc6bf5c954b7d7853a98e',
            '822245cda207a70106222fc0627300c042a6d6dd6f9fb46a76cd91d74b9f00db']]
        if not all(p.exists() for p in cls.paths):
            raise unittest.SkipTest('Retained regional source store not present')

    def test_actual_supplement_and_containment_publications(self):
        from cordon_d.removal_events import regional_publication
        # Independently read labelled detail fields: 63's subject references 173;
        # 94's proposal identifier is 93. Neither is the published adoption number.
        expected = [(63, '2026-04-03', '2026-04-03', '2026-04-20'),
                    (94, '2026-05-26', '2026-05-27', '2026-06-11'),
                    (104, '2026-06-09', '2026-06-10', '2026-06-25'),
                    (102, '2026-06-09', '2026-06-10', '2026-06-25')]
        for path, (number, adopted, start, end) in zip(self.paths, expected):
            p = regional_publication(path)
            document = f'REG-PUGLIA-U181-DIR-2026-{number:05d}'
            self.assertEqual(p.document, document)
            self.assertEqual(p.document_date, date.fromisoformat(adopted))
            self.assertEqual(p.source_fields['Stato Pubblicazione'], 'Conclusa')
            self.assertEqual(len(p.events), 2)
            for event, kind, day in zip(p.events,
                    ['regional-publication-start', 'regional-publication-end'], [start, end]):
                self.assertEqual(event.anchor(kind=kind, document=document,
                    recipient=None, precision='date'), date.fromisoformat(day))
                for wrong in ['municipal-publication-end', 'recipient-notification', 'removal-completed']:
                    with self.assertRaises(ValueError):
                        event.anchor(kind=wrong, document=document, recipient=None, precision='date')
            with self.assertRaises(ValueError):
                publication_deadline(Snapshot.load(), 'B-CLK-DGR1075-owner-election',
                    p.document_date, p, document=document, competent_publisher=p.publisher,
                    zone=ZoneInfo('Europe/Rome'), calendar=national_calendar())
        p = regional_publication(self.paths[1])
        self.assertEqual(p.source_fields['Codice Cifra (Identificativo Proposta)'], '181/DIR/2026/00093')
        self.assertEqual(p.source_fields['Data registrazione albo pretorio'], '2026-05-27 12:15:17.545')

    def test_unregistered_identity_and_unfinished_publication(self):
        from bs4 import BeautifulSoup
        from cordon_d.removal_events import regional_publication
        soup = BeautifulSoup(self.paths[1].read_bytes(), 'html.parser')
        def set_field(label, value):
            node = next(n for n in soup.select('label') if n.get_text(strip=True) == label)
            node.find_next_sibling('span').string = value
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'detail.html'
            set_field('Numero Adozione Atto', '00999')
            path.write_text(str(soup))
            p = regional_publication(path)
            self.assertEqual(p.document, 'REG-PUGLIA-U181-DIR-2026-00999')
            self.assertEqual(len(p.events), 2)
            set_field('Stato Pubblicazione', 'Da pubblicare')
            path.write_text(str(soup))
            p = regional_publication(path)
            self.assertEqual(p.events, ())
            self.assertEqual(p.source_fields['Data Fine Pubblicazione'], '2026-06-11 23:59:59.0')
