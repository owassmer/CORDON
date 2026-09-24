"""Albo records attach to an order only by the identity they print: number, year, date and issuing office.

Rows are ARIF's OpenWeb albo export (2026-09-24 window), shortened; the JCityGov
detail and the posted-document heading are Taranto's 14/12/2021 posting of DDS
168/2021. Held adoption dates are the orders' own readings.
"""
from datetime import date
import unittest

from cordon_d.albo_postings import (jcitygov_posting, openweb_rows, posted_document_events, printed_orders,
                                    register_events)

HELD = {'REG-PUGLIA-U181-DIR-2021-00122': date(2021, 10, 28), 'REG-PUGLIA-U181-DIR-2021-00128': date(2021, 11, 4),
        'REG-PUGLIA-U181-DIR-2021-00141': date(2021, 11, 18), 'REG-PUGLIA-U181-DIR-2021-00168': date(2021, 12, 14),
        'REG-PUGLIA-U181-DIR-2021-00167': date(2021, 12, 14)}
CSV = ('Tipo,numero atto,Data atto,Oggetto,Inizio pubblicazione,Fine pubblicazione,Ente,Ufficio,Importo presunto\n'
       'Delibere Del Direttore Generale,138,22/02/2022,"Regime di aiuto per i proprietari che hanno eseguito '
       'estirpazione, adempiendo a prescrizione di abbattimento della Regione Puglia Sezione Osservatorio '
       'Fitosanitario. DDS 122/2021 Carparelli Maria.",28/02/2022,15/03/2022,,,\n'
       'Delibere Del Direttore Generale,275,28/03/2023,"Note di prescrizione abbattimento n. 128 del  04/11/2021 '
       '&#8211; n. 141 del 19/11/2021 &#8211; n. 1773 del 10/02/2020 Regime di aiuto ... Sezione Osservatorio '
       'Fitosanitario.",28/03/2023,12/04/2023,,,\n'
       'Delibere Del Direttore Generale,18,19/01/2021,"Acquisto di cavalletti n. 122 del 28/10/2021",'
       '19/01/2021,03/02/2021,,,\n').encode()
DETAIL = ('<html><body>Dettaglio Atto Categoria DETERMINAZIONI Data di registro 14/12/2021 Anno di registro 2021 '
          'Numero di registro 12097 Anno protocollo 2021 Mittente Comune di Taranto Ente richiedente Comune di '
          'Taranto Oggetto PRESCRIZIONE DI MISURE DI ESTIRPAZIONE IN AGRO DI TARANTO Data esecutività 21/12/2021 '
          'Periodo Pubblicazione 14/12/2021 - 31/12/2026 Provenienza Interna</body></html>').encode()


def identity(**act):
    base = dict(issuer='SEZIONE OSSERVATORIO FITOSANITARIO', act_kind='ATTO DIRIGENZIALE', number='168',
                date_words='14/12/2021', adopted='2021-12-14', code='181_DIR_2021_00168',
                subject='Prescrizione di misure di estirpazione', page=1)
    return dict(request=dict(sources=['e' * 64]), reading=dict(acts=[dict(base, **act)], issues=[]))


class AlboPostings(unittest.TestCase):
    def test_printed_identities_keep_their_printed_dates(self):
        self.assertEqual([(n, y, d) for n, y, d, _ in printed_orders('DDS 115/2021 e DDS135/2021; n. 00005 DEL '
                                                                         '31.01.2023')],
                         [(115, 2021, None), (135, 2021, None), (5, 2023, date(2023, 1, 31))])

    def test_an_executor_act_attaches_by_number_year_date_and_issuer(self):
        events, unattached = register_events(openweb_rows(CSV), source='a' * 64, publisher='ARIF', role='executor',
                                             held=HELD)
        # Aid to owners who removed the plants is a lead to their removal, not the executor's act of removal.
        self.assertEqual(sorted((e.document, e.kind, e.occurred) for e in events), [
            ('REG-PUGLIA-U181-DIR-2021-00122', 'aid-liquidation-for-performed-removal', date(2022, 2, 22)),
            ('REG-PUGLIA-U181-DIR-2021-00128', 'executor-act-naming-order', date(2023, 3, 28))])
        causes = {(u['instrument'], u['cause']) for u in unattached}
        self.assertIn(('REG-PUGLIA-U181-DIR-2021-00141', "the printed date is not the held order's adoption date"),
                      causes)
        self.assertIn(('REG-PUGLIA-U181-DIR-2020-01773', 'names an order D does not hold'), causes)
        # The third row prints no issuing office: its number is not an order's identity.
        self.assertFalse(any(u['row'] == 4 for u in unattached))

    def test_every_identity_an_issuer_row_prints_is_attached_or_unattached_with_its_cause(self):
        # ARIF DDG 360 del 09/04/2024 and DDG 1038 del 26/09/2024, shortened: the export cuts the first
        # subject inside the issuer; the second prints "DDS 138 DEL" and a bare "00114 del".
        held = dict(HELD, **{'REG-PUGLIA-U181-DIR-2022-00102': date(2022, 9, 15),
                             'REG-PUGLIA-U181-DIR-2022-00089': date(2022, 8, 24),
                             'REG-PUGLIA-U181-DIR-2023-00138': date(2023, 12, 1),
                             'REG-PUGLIA-U181-DIR-2023-00114': date(2023, 10, 16)})
        data = ('Tipo,numero atto,Data atto,Oggetto,Inizio pubblicazione,Fine pubblicazione,Ente,Ufficio\n'
                'Delibere Del Direttore Generale,360,09/04/2024,"Note prescrizione abbattimenti N. 102 del '
                '15/09/2022 – N. 89 del 24/082022 - Regime di aiuto per i proprietari che hanno eseguito '
                'estirpazione di piante di olivo, adempiendo a prescrizione di abbattimento della Regione Puglia '
                'Sezione Osservatorio Fitosanita",10/04/2024,25/04/2024,,\n'
                'Delibere Del Direttore Generale,1038,26/09/2024,"Note di prescrizione abbattimento DDS 138 DEL '
                '01/12/2023 - 00114 del 16/10/2023 - Regime di aiuto per i proprietari/conduttori che hanno '
                'eseguito estirpazione di piante, adempiendo a prescrizione di abbattimento della Regione Puglia '
                'Sezione Osservatorio Fitosanitario. Impegno e liquidazione.",02/10/2024,17/10/2024,,\n'
                'Delibere Del Direttore Generale,361,09/04/2024,"Note prescrizione N. 102 del 15/09/2022 della '
                'Regione Puglia Sezione Osserv",10/04/2024,25/04/2024,,\n').encode()
        events, unattached = register_events(openweb_rows(data), source='a' * 64, publisher='ARIF',
                                             role='executor', held=held)
        self.assertEqual(sorted((e.document[-10:], e.kind) for e in events), [
            ('2022-00102', 'aid-liquidation-for-performed-removal'),
            ('2023-00114', 'aid-liquidation-for-performed-removal'),
            ('2023-00138', 'aid-liquidation-for-performed-removal')])
        self.assertEqual([(u['row'], u['words'], u['cause']) for u in unattached],
                         [(2, 'N. 89 del 24/082022', 'the printed date is not a readable date')])
        # An issuer cut before "fitosanitario" is not printed: the third row is not considered.
        self.assertFalse(any(u['row'] == 4 for u in unattached))

    def test_a_municipal_register_row_is_a_posting_with_its_declared_interval(self):
        events, _ = register_events(openweb_rows(CSV), source='a' * 64, publisher='Comune', role='municipal',
                                    held=HELD)
        kinds = sorted((e.kind, e.occurred) for e in events if e.document.endswith('00122'))
        self.assertEqual(kinds, [('municipal-publication-end', date(2022, 3, 15)),
                                 ('municipal-publication-start', date(2022, 2, 28))])

    def test_a_posted_scan_attaches_by_the_identity_it_prints_and_a_retention_end_stays_open(self):
        posting = jcitygov_posting(DETAIL)
        self.assertEqual((posting['period_start'], posting['period_end_words']), (date(2021, 12, 14), '31/12/2026'))
        events, unattached = posted_document_events(identity(), posting, detail_source='d' * 64,
                                                    publisher='Comune di Taranto', held=HELD)
        self.assertEqual([(e.document, e.kind, e.occurred) for e in events],
                         [('REG-PUGLIA-U181-DIR-2021-00168', 'municipal-publication-start', date(2021, 12, 14))])
        self.assertIn('interval open', events[0].support.reading)
        self.assertEqual(unattached, [])
        other = posted_document_events(identity(issuer='COMUNE DI TARANTO - DIREZIONE'), posting,
                                       detail_source='d' * 64, publisher='Comune di Taranto', held=HELD)
        self.assertEqual(other[0], [])
        # DDS 4/2022's posted heading prints its date inside the number field.
        held = dict(HELD, **{'REG-PUGLIA-U181-DIR-2022-00004': date(2022, 2, 8)})
        four = posted_document_events(identity(number='N. 4 del 08/02/2022 del Registro delle Determinazioni',
                                               date_words='08/02/2022', adopted='2022-02-08'), posting,
                                      detail_source='d' * 64, publisher='Comune di Taranto', held=held)
        self.assertEqual([e.document for e in four[0]], ['REG-PUGLIA-U181-DIR-2022-00004'])
        wrong_day = posted_document_events(identity(adopted='2021-12-15', date_words='15/12/2021'), posting,
                                           detail_source='d' * 64, publisher='Comune di Taranto', held=HELD)
        self.assertEqual(wrong_day[0], [])


if __name__ == '__main__':
    unittest.main()
