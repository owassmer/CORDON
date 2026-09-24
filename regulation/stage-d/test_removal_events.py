"""Publication records supply exact anchors, never recipient effect or performance."""
from dataclasses import replace
from datetime import date
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from cordon_d.removal_events import publication_records, connected_publications, parsec_publications, domino_publication
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
        captures = json.loads((root / 'corpus/sources/removal-events/records.json').read_text())
        acquisitions += [r for r in captures if r.get('sha256') == digest]
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
        for captured, expected in [('2026-04-02T12:00:00+00:00', []),
                                   ('2026-04-10T12:00:00+00:00', ['municipal-publication-start'])]:
            earlier = [dict(r, captured_at=captured) if r.get('sha256') == digest else r
                       for r in acquisitions]
            declarations = list(parsec_publications(path, measures=measures,
                                **dict(kwargs, acquisitions=earlier)))
            row = next(p for p in declarations if p.source_fields['source_fields']['Nro'] == '369')
            self.assertEqual([e.kind for e in row.events], expected)
            self.assertEqual(row.source_fields['declared_dates']['Data fine pubb.'], '2026-04-10')

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


class DominoPublication(unittest.TestCase):
    def read(self, *, captured='2026-03-20T12:00:00+00:00', status='NO',
             duplicate_period=False, measures=None, acquired=True):
        from cordon_d.evidence import file_digest
        period = '<tr><td>In Pubblicazione</td><td></td><td>dal 03/07/2026 al 03/14/2026</td></tr>'
        with TemporaryDirectory() as directory:
            path = Path(directory)/'detail.html'
            path.write_text('''<table>
<tr><td>Protocollo Generale</td><td></td><td>20269876543</td></tr>
<tr><td>Tipo Provvedimento</td><td></td><td>Avviso</td></tr>
<tr><td>Ente/Amministrazione</td><td></td><td>Regional office</td></tr>
<tr><td>Oggetto</td><td></td><td>DDS999/2026 amends DDS998/2025</td></tr>
<tr><td>N. Repertorio Albo</td><td></td><td>2026/Albo/9991</td></tr>''' + period +
                f'<tr><td>In Pubblicazione</td><td></td><td>{status}</td></tr>' +
                (period if duplicate_period else '') + '''</table>
<a href="/native/$FILE/unknown.pdf">Original document</a>
<a href="/native/$FILE/other.pdf">Certificato di Pubblicazione</a>''')
            captures = [{'sha256': file_digest(path), 'captured_at': captured}]
            if acquired:
                captures += [{'url': 'https://example.org/native/$FILE/unknown.pdf', 'sha256': 'principal'},
                             {'url': 'https://example.org/native/$FILE/other.pdf', 'sha256': 'attachment'}]
            # An unrelated timestamp cannot qualify or break this declaration.
            captures += [{'sha256': 'unrelated', 'captured_at': 'unrecognized'}]
            measures = [self.measure()] if measures is None else measures
            return domino_publication(path, publisher='Unseen municipality',
                source_url='https://example.org/detail', measures=measures, acquisitions=captures)

    def measure(self, source='principal', identity='issued-act', adopted=date(2026, 3, 5)):
        return SimpleNamespace(identity=identity, adopted=adopted,
                               response={'request': {'sources': [source]}})

    def test_only_acquired_original_identity_supplies_document_events(self):
        p = self.read()
        self.assertEqual((p.document, p.document_date), ('issued-act', date(2026, 3, 5)))
        self.assertEqual([e.occurred for e in p.events], [date(2026, 3, 7), date(2026, 3, 14)])
        self.assertTrue(all(e.document == p.document and e.recipient is None for e in p.events))
        self.assertTrue(all(e.support.source == p.support.source for e in p.events))
        self.assertIsNone(p.source_fields['attachment_issue'])
        self.assertEqual(p.source_fields['source_fields']['Protocollo Generale'], '20269876543')
        self.assertEqual(len(p.source_fields['document_routes']), 2)
        self.assertEqual(connected_publications([p], [self.measure(identity='another-act')]), ())
        with self.assertRaises(ValueError):
            p.events[0].anchor(kind='recipient-notification', document=p.document,
                               recipient='named-owner', precision='date')
        for measures, acquired, cause in [
                ([self.measure(source='not-the-linked-original')], True, 'qualified measure identity'),
                ([], True, 'qualified measure identity'),
                ([self.measure()], False, 'no held source acquisition'),
                ([self.measure(), self.measure('attachment', 'another-act')], True, 'competing'),
                ([self.measure(), self.measure(adopted=date(2026, 3, 6))], True, 'competing')]:
            with self.subTest(cause=cause):
                row = self.read(measures=measures, acquired=acquired)
                self.assertIsNone(row.document)
                self.assertEqual(row.events, ())
                self.assertIn(cause, row.source_fields['attachment_issue'])
                self.assertEqual(row.source_fields['declared_dates']['Data fine pubb.'], '2026-03-14')
        from cordon_c.core import MissingInput
        class Unqualified:
            response = {'request': {'sources': ['principal']}}

            @property
            def identity(self):
                raise MissingInput('Issuing authority not recovered')

        self.assertIsNone(self.read(measures=[Unqualified()]).document)

    def test_future_missing_capture_active_status_and_duplicate_period_refuse_end(self):
        for captured, kinds in [(None, []), ('2026-03-06T12:00:00+00:00', []),
                                ('2026-03-07T12:00:00+00:00', ['municipal-publication-start']),
                                ('2026-03-14T12:00:00+00:00', ['municipal-publication-start']),
                                ('2026-03-15T12:00:00+00:00',
                                 ['municipal-publication-start', 'municipal-publication-end'])]:
            with self.subTest(captured=captured):
                self.assertEqual([e.kind for e in self.read(captured=captured).events], kinds)
        for status in ['SI', 'unrecognized', '']:
            p = self.read(status=status)
            self.assertEqual([e.kind for e in p.events], ['municipal-publication-start'])
            self.assertEqual(p.source_fields['publication_status'], status)
        p = self.read(duplicate_period=True)
        self.assertEqual(p.events, ())
        self.assertEqual(len(p.source_fields['source_fields']['In Pubblicazione']), 3)
        self.assertIn('one native', p.source_fields['date_issues']['In Pubblicazione'])


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

    def test_publication_is_not_recipient_notification(self):
        p = self.read(self.row())
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

    def test_actual_records(self):
        readings = {p.document: p for p in publication_records(self.path) if p.document}
        # Expected values read directly from the retained municipal JSON and
        # checked against its linked original acts, not generated by this reader.
        expected = [
            (2024, 52, '2024-05-06', '2024-05-08', '2024-05-15'),
            (2024, 58, '2024-05-16', '2024-05-20', '2024-05-26'),
            (2024, 82, '2024-07-09', '2024-07-16', '2024-07-23'),
            (2024, 108, '2024-08-16', '2024-08-19', '2024-08-26'),
            (2024, 188, '2024-12-12', '2024-12-13', '2024-12-20'),
        ]
        for year, number, adopted, start, end in expected:
            p = readings[f'REG-PUGLIA-U181-DIR-{year}-{number:05d}']
            with self.subTest(document=p.document):
                self.assertEqual(p.document_date.isoformat(), adopted)
                self.assertEqual([e.occurred.isoformat() for e in p.events], [start, end])
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


class PublicationAttestation(unittest.TestCase):
    """Synthetic source/consumer boundaries, not qualifications of actual certificates."""
    def setUp(self):
        import pymupdf
        from cordon_d.store import put_bytes
        from cordon_d.removal_events import PUBLICATION_ATTESTATION_SCHEMA
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.store = Path(temporary.name)
        with pymupdf.open() as pdf:
            pdf.new_page().insert_text((30, 30), 'Publication certificate; completed interval.')
            pdf.new_page().insert_text((30, 30), 'Printed signature claim, not verified.')
            self.source = put_bytes(self.store, pdf.tobytes())
        self.reading = dict(publisher=self.value('Unseen municipality'),
            register_reference=self.value('2026/Albo/9876'), document_reference='DDS 991 of 6 May 2024',
            act=dict(authority=self.value('puglia-osservatorio'), number=self.value('991'),
                     adopted=self.value('2024-05-06')),
            period=dict(start=self.value('2024-05-08'), end=self.value('2024-05-15'),
                        coverage='completed-interval', statement='Publication is certified from 8 to 15 May.',
                        qualification=None, support=[self.cite()]),
            signer=self.value('Example signer'), signature_statement=self.value('Printed signature claim'),
            issued_on=self.value(), issues=[], support=[self.cite()])
        self.response = dict(request=dict(sources=[self.source], schema=PUBLICATION_ATTESTATION_SCHEMA),
                             request_sha256='a'*64, reading=self.reading)

    def cite(self):
        return dict(source=self.source, page=1, locator='publication clause',
                    quote='completed interval')

    def value(self, value=None, cause='source-not-stated'):
        return dict(value=value, cause=cause if value is None else None,
                    support=[] if value is None else [self.cite()])

    def read(self):
        from cordon_d.removal_events import _attestation
        return _attestation(self.response, self.store)

    def declaration(self, **changes):
        from cordon_d.evidence import Support
        from cordon_d.removal_events import Publication
        return replace(Publication('native-row', 'Unseen municipality',
            'REG-PUGLIA-U181-DIR-2024-00991', date(2024, 5, 6),
            dict(source_fields={'N. Repertorio Albo': '2026/Albo/9876'},
                 document_routes=[{'url': 'https://example.org/exact-attachment'}],
                 declared_dates={'Data inizio pubb.': '2024-05-08', 'Data fine pubb.': '2024-05-15'}),
            (), Support('native-hash', 'native-row', 'Register declaration')), **changes)

    def connect(self, publication, declarations, acquisitions=None):
        from cordon_d.removal_events import connect_publication_attestation
        return connect_publication_attestation(publication, declarations,
            acquisitions=acquisitions if acquisitions is not None else [
                {'url': 'https://example.org/exact-attachment', 'sha256': self.source}])

    def test_certified_interval_without_issuance_or_continuity_phrase(self):
        p = self.read()
        self.assertEqual([e.occurred for e in p.events], [date(2024, 5, 8), date(2024, 5, 15)])
        self.assertIsNone(p.source_fields['attestation']['issued_on']['value'])
        self.assertEqual(p.source_fields['provenance'], 'model_proposed_reading')
        self.assertEqual(p.source_fields['request_sha256'], self.response['request_sha256'])
        self.assertTrue(all(e.support.source == self.source and e.recipient is None for e in p.events))
        self.assertEqual(connected_publications([p], [SimpleNamespace(identity=p.document,
                         adopted=date(2024, 5, 7))]), ())
        with self.assertRaises(ValueError):
            p.events[0].anchor(kind='recipient-notification', document=p.document,
                               recipient='owner', precision='date')

    def test_unresolved_act_keeps_interval_and_uses_existing_exact_native_attachment(self):
        self.reading['act'] = {key: self.value() for key in ('authority', 'number', 'adopted')}
        p = self.read()
        self.assertIsNone(p.document)
        self.assertFalse(p.events)
        self.assertEqual(p.source_fields['attestation']['period']['end']['value'], '2024-05-15')
        declaration = self.declaration()
        bound = self.connect(p, [declaration])
        self.assertEqual(bound.document, declaration.document)
        self.assertEqual(len(bound.events), 2)
        self.assertIs(bound.source_fields['declarations'][0], declaration)
        self.assertIsNone(p.document)
        unresolved = self.connect(p, [self.declaration(document=None, document_date=None)])
        self.assertIsNone(unresolved.document)
        self.assertIn('no resolved principal', unresolved.source_fields['attachment_issues'][0]['cause'])
        for row, captures in [(declaration, []), (self.declaration(publisher='Other municipality'), None)]:
            result = self.connect(p, [row], captures)
            self.assertIsNone(result.document)
            self.assertFalse(result.events)
            self.assertTrue(result.source_fields['attachment_issues'])
        wrong = self.declaration()
        wrong.source_fields['source_fields']['N. Repertorio Albo'] = '2026/Albo/9877'
        self.assertIsNone(self.connect(p, [wrong]).document)

    def test_component_and_competing_identity_conflicts_refuse_without_erasing_certified_period(self):
        p = self.read()
        wrong = self.declaration(document='REG-PUGLIA-U181-DIR-2024-00992')
        for rows in [[wrong], [self.declaration(), wrong],
                     [self.declaration(document_date=date(2024, 5, 7))]]:
            result = self.connect(p, rows)
            self.assertIsNone(result.document)
            self.assertFalse(result.events)
            self.assertTrue(result.source_fields['attachment_issues'])
            self.assertEqual(result.source_fields['attestation']['period'], self.reading['period'])
        self.reading['act']['authority'] = self.value('other')
        self.assertIsNone(self.connect(self.read(), [self.declaration()]).document)
        self.reading['act']['authority'] = self.value()
        self.reading['act']['adopted'] = self.value()
        self.reading['act']['number'] = self.value('992')
        self.assertIsNone(self.connect(self.read(), [self.declaration()]).document)

    def test_unrelated_native_occurrence_does_not_erase_independent_certificate_identity(self):
        self.reading['document_reference'] += '; supplements DDS 990 and DDS 989'
        p = self.read()
        self.assertEqual({e.document for e in p.events}, {'REG-PUGLIA-U181-DIR-2024-00991'})
        unrelated = self.declaration(publisher='Another municipality', document='another-act')
        connected = self.connect(p, [unrelated, self.declaration()])
        self.assertEqual(connected.document, p.document)
        self.assertEqual(len(connected.events), 2)
        self.assertEqual(len(connected.source_fields['attachment_issues']), 1)
        self.assertEqual(self.connect(p, [unrelated], []).events, p.events)

    def test_period_conflict_is_local_and_native_status_does_not_override_certificate(self):
        declaration = self.declaration()
        declaration.source_fields['declared_dates']['Data fine pubb.'] = '2024-05-16'
        result = self.connect(self.read(), [declaration])
        self.assertEqual([e.kind for e in result.events], ['municipal-publication-start'])
        self.assertIn('end', result.source_fields['period_conflicts'])
        self.assertEqual(result.source_fields['attestation']['period']['end']['value'], '2024-05-15')
        self.assertEqual(declaration.source_fields['declared_dates']['Data fine pubb.'], '2024-05-16')
        declaration = self.declaration()
        declaration.source_fields['publication_status'] = 'SI'
        self.assertEqual(len(self.connect(self.read(), [declaration]).events), 2)
        captures = [{'url': 'https://example.org/exact-attachment', 'sha256': self.source,
                     'captured_at': '2024-05-14T12:00:00+00:00'}]
        self.assertEqual([e.kind for e in self.connect(self.read(), [declaration], captures).events],
                         ['municipal-publication-start'])

    def test_partial_unknown_and_nonactual_records_remain_distinct(self):
        self.reading['period']['coverage'] = 'partial-publication'
        self.reading['period']['qualification'] = 'Posting interrupted before completion.'
        self.assertEqual([e.kind for e in self.read().events], ['municipal-publication-start'])
        for coverage in ['blank-form', 'intended', 'unresolved']:
            self.reading['period']['coverage'] = coverage
            self.assertFalse(self.read().events)
        self.reading['period']['coverage'] = 'completed-interval'
        self.reading['period']['end'] = self.value(cause='not-recovered')
        self.assertEqual([e.kind for e in self.read().events], ['municipal-publication-start'])
        self.assertEqual(self.read().source_fields['attestation']['period']['end']['cause'], 'not-recovered')
        self.reading['period']['end'] = self.value('2024-05-07')
        self.assertFalse(self.read().events)
        self.assertEqual(set(self.read().source_fields['period_conflicts']), {'start', 'end'})

    def test_source_boundary_rejects_missing_causes_unsupported_dates_and_other_pages(self):
        from copy import deepcopy
        original = deepcopy(self.reading)
        mutations = [lambda r: r['period']['end'].update(value=None, cause=None),
                     lambda r: r['period']['end'].update(support=[]),
                     lambda r: r['period']['end'].update(value='2024-02-30'),
                     lambda r: r['support'][0].update(source='b'*64),
                     lambda r: r['support'][0].update(page=3),
                     lambda r: r['support'][0].update(quote='')]
        for mutate in mutations:
            self.response['reading'] = deepcopy(original)
            mutate(self.response['reading'])
            with self.assertRaises(ValueError):
                self.read()

    def test_retained_capture_day_qualifies_each_endpoint_before_any_connection(self):
        from hashlib import sha256
        from cordon_d.removal_events import retained_publication_attestation
        request = self.response['request']
        identity = sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        target = self.store/'derived/document-readings'/f'{identity}.json'
        target.parent.mkdir(parents=True)
        for captured, expected in [('2024-05-07T12:00:00+00:00', []),
                                  ('2024-05-14T12:00:00+00:00', ['municipal-publication-start']),
                                  ('2024-05-14T22:30:00+00:00',
                                   ['municipal-publication-start', 'municipal-publication-end'])]:
            with self.subTest(captured=captured):
                target.write_text(json.dumps(dict(request=request, request_sha256=identity,
                    captured_at=captured, output=json.dumps(self.reading))))
                result = retained_publication_attestation(identity, self.store)
                self.assertEqual([e.kind for e in result.events], expected)
                self.assertEqual(result.source_fields['reading_captured_at'], captured)
                self.assertEqual(result.source_fields['attestation']['period']['end']['value'], '2024-05-15')
                self.assertEqual([e.kind for e in self.connect(result, [self.declaration()]).events], expected)

    def test_conflicts_belong_to_existing_components_and_cannot_be_filled_by_attachment(self):
        from copy import deepcopy
        original = deepcopy(self.reading)
        for aspect in ['period.start', 'period.end', 'act.authority', 'act.number', 'act.adopted']:
            with self.subTest(aspect=aspect):
                self.response['reading'] = deepcopy(original)
                reading = self.response['reading']
                reading['issues'] = [dict(aspect=aspect, cause='conflict', detail='Two explicit source values disagree.')]
                with self.assertRaisesRegex(ValueError, 'conflicting component'):
                    self.read()
                group, key = aspect.split('.')
                reading[group][key] = self.value(cause='conflict')
                publication = self.read()
                expected = ([] if group == 'act' else
                            ['municipal-publication-' + ('end' if key == 'start' else 'start')])
                self.assertEqual([e.kind for e in publication.events], expected)
                connected = self.connect(publication, [self.declaration()])
                self.assertEqual([e.kind for e in connected.events], expected)
                if group == 'act':
                    self.assertIsNone(connected.document)
                    self.assertIn('cannot resolve', connected.source_fields['attachment_issues'][0]['cause'])
                self.assertEqual(connected.source_fields['attestation'][group][key]['cause'], 'conflict')

    def test_coverage_conflict_and_unaddressed_conflict_are_not_decorative_issues(self):
        self.reading['issues'] = [dict(aspect='period.coverage', cause='conflict',
                                      detail='Completion is disputed within the source.')]
        with self.assertRaisesRegex(ValueError, 'coverage must remain unresolved'):
            self.read()
        self.reading['period']['coverage'] = 'unresolved'
        self.assertFalse(self.read().events)
        self.reading['issues'][0]['aspect'] = 'some prose about an end date'
        with self.assertRaisesRegex(ValueError, 'exact existing component path'):
            self.read()
        self.reading['period']['coverage'] = 'completed-interval'
        self.reading['issues'] = [dict(aspect='signature verification', cause='not-supplied',
                                      detail='No cryptographic verification result was supplied.')]
        self.assertEqual(len(self.read().events), 2)
        self.reading['signature_statement'] = self.value(cause='conflict')
        self.reading['issues'].append(dict(aspect='signature_statement', cause='conflict',
                                          detail='Signature descriptions disagree.'))
        self.assertEqual(len(self.read().events), 2)

    def test_retained_replay_does_not_dispatch_or_supply_a_principal(self):
        from hashlib import sha256
        from unittest.mock import patch
        from cordon_d.removal_events import retained_publication_attestation
        request = self.response['request']
        identity = sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        target = self.store/'derived/document-readings'/f'{identity}.json'
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps(dict(request=request, request_sha256=identity,
                                         output=json.dumps(self.reading))))
        with patch('cordon_d.document_subscription.read_documents', side_effect=AssertionError('No dispatch')):
            replay = retained_publication_attestation(identity, self.store)
        self.assertEqual(len(replay.events), 2)
        self.assertEqual(replay.source_fields['request_sha256'], identity)
        target.write_text(target.read_text().replace(identity, 'b'*64))
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            retained_publication_attestation(identity, self.store)
