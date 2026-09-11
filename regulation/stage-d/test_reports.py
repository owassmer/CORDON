"""Structural rules of the report reader on inputs the work never saw."""
from datetime import date
import unittest

from cordon_d.findings import comparison
from cordon_d.reports import (Result, _classify, _flat_rows, _header_role, _italian_date, _letter_facts,
                              _line_rows, _merged_header, _table_rows, _transposed)

LETTER = {'assays': ('qPCR',), 'analytes': ('Xylella fastidiosa',), 'positives_only': False}


class _Table:
    """The one method `_table_rows` uses of a PyMuPDF table."""
    def __init__(self, cells):
        self.cells = cells

    def extract(self):
        return self.cells


class HeaderReading(unittest.TestCase):
    def test_spanning_headers_merge_only_under_their_own_parent(self):
        cells = [['Codice univoco', 'Codice committente', 'data campionamento', 'ANALISI MOLECOLARE', None, None, None],
                 [None, None, None, 'Esito saggio Dupas', None, None, 'Data prova'],
                 [None, None, None, 'fastidiosa', 'multiplex', 'pauca', None],
                 ['1_EXP', '123456', '01/06/2024', 'Non rilevata', 'Rilevata', 'Non rilevata', '05/06/2024']]
        header, data = _merged_header(cells)
        self.assertEqual(header[3], 'ANALISI MOLECOLARE / Esito saggio Dupas / fastidiosa')
        self.assertEqual(header[5], 'ANALISI MOLECOLARE / Esito saggio Dupas / pauca')
        self.assertEqual(header[6], 'ANALISI MOLECOLARE / Data prova')  # 'pauca' must not spill under 'Data prova'
        self.assertEqual(len(data), 1)

    def test_publisher_reference_outranks_laboratory_code_and_subspecies_is_not_species(self):
        self.assertEqual(_header_role('Codice committente'), 'reference')
        self.assertEqual(_header_role('Id'), 'reference')
        self.assertEqual(_header_role('ID giornaliero'), 'daily-id')
        self.assertEqual(_header_role('Codice univoco campione'), 'reference-secondary')
        self.assertEqual(_header_role('DATI IDENTIFICATIVI CAMPIONE'), 'identifying-text')
        self.assertEqual(_header_role('ANALISI PER IDENTIFICAZIONE DELLA SOTTOSPECIE / Esito / pauca'), 'result')
        self.assertEqual(_header_role('Specie'), 'species')
        for h in ('Data fine prova', 'Data inizio prova', 'Data Saggio', 'Data/Ora esito laboratorio'):
            self.assertEqual(_header_role(h), 'result_date', h)
        self.assertEqual(_header_role('Data rilevamento'), 'sampling_date')

    def test_a_result_cell_holding_several_rows_results_states_none_of_them(self):
        cells = [['CODICE ID', 'DATI IDENTIFICATIVI CAMPIONE', 'TECNICA', 'ESITO'],
                 ['0219/24 - 1', 'Olea Europaea | ID: 11200189 | 13/02/2024', 'Real time PCR', 'Presente\nPresente\nAssente'],
                 ['0219/24 - 2', 'Olea Europaea | ID: 11200188 | 13/02/2024', 'Real time PCR', 'Presente'],
                 ['0219/24 - 3', 'Olea Europaea | ID: 11200187 | 13/02/2024', 'Real time PCR', '']]
        rows, _ = _table_rows(2, 'text-layer', _Table(cells), LETTER)
        self.assertEqual([r.reference for r in rows], ['11200189', '11200188', '11200187'])
        self.assertEqual([r.results[0].kind for r in rows], ['unread', 'detected', 'unread'])
        self.assertEqual([r.unread for r in rows], [True, False, True])
        self.assertEqual(rows[0].reference_kind, 'in-cell')

    def test_a_transposed_table_is_recognized_only_when_its_first_column_is_the_id_and_its_columns_are_codes(self):
        cells = [['Id', '1644899', '1645134'], ['Data rilevamento', '28/02/2024', '28/02/2024'], ['Esito laboratorio', 'Positivo', 'Positivo']]
        turned = _transposed(cells)
        self.assertEqual(turned[0], ['Id', 'Data rilevamento', 'Esito laboratorio'])
        self.assertEqual(turned[1], ['1644899', '28/02/2024', 'Positivo'])
        self.assertIsNone(_transposed([['Id', 'Data'], ['1644899', '28/02/2024']]))


class FlatReading(unittest.TestCase):
    def test_one_cell_per_line_text_is_read_by_id_then_date_and_other_codes_do_not_start_rows(self):
        text = ('Rapporto di prova N. 10_POSITIVI del 08 Ottobre 2021\nId\nData rilevamento\nCodice squadra\nSpecie\n'
                'Latitudine\nLongitudine\nLaboratorio\nEsito laboratorio\nCodice Busta\nZona\n'
                '1213722\n29/09/2021\n293945\nOlivo (Olea europaea)\n40,75069\n17,53865\nUNIFG\nPositivo\n3094150\nZONA EX CONTENIMENTO\n'
                '1214774\n29/09/2021\n293945\nOlivo (Olea europaea)\n40,7448\n17,49369\nUNIFG\nNegativo\n3093933\nZONA\n')
        rows = _flat_rows(2, 'text-layer', text, LETTER)
        self.assertEqual([r.reference for r in rows], ['1213722', '1214774'])
        self.assertEqual([r.reference_kind for r in rows], ['sample', 'sample'])
        self.assertEqual([x.kind for r in rows for x in r.results], ['positive', 'negative'])
        self.assertEqual(rows[0].sampling_date, date(2021, 9, 29))
        self.assertEqual(_flat_rows(1, 'text-layer', 'Nome\n1213722\n29/09/2021\nPositivo\n', LETTER), [])  # no Id/Data header


class LineReading(unittest.TestCase):
    def test_a_scanned_row_wrapped_over_two_lines_is_one_row_and_a_postal_code_is_not(self):
        text = ('Al Dirigente\n70121 BARI\nProt. n. 4567/2019\n'
                '|_231207| 16/03/2018|olivo (Olea europaea) | 40,50517402|17,55548313|Francavilla\n'
                'Fontana _ [Positivo — [Negativo | 28/03/2018]\n'
                '|_231942| 16/03/2018|olivo (Olea europaea) | 40,53063735|17,63763517|Francavilla Fontana\n')
        rows = _line_rows(2, 'ocr:ita:200dpi', text, LETTER)
        self.assertEqual([r.reference for r in rows], ['231207', '231942'])
        first, second = rows
        self.assertEqual(first.sampling_date, date(2018, 3, 16))
        self.assertEqual([x.kind for x in first.results], ['positive', 'negative'])
        self.assertEqual(first.result_date, date(2018, 3, 28))
        self.assertTrue(second.unread)          # no result token could be read
        self.assertEqual(second.results, ())

    def test_a_code_after_a_result_date_on_the_same_line_starts_the_next_row(self):
        text = ('152210 23/11/2017 olivo (Olea europaea) 40,50461114 17,61432543 oria Positivo Positivo 05/01/2018) 152257/\n'
                '23/11/2017 olivo (Olea europaea) 40,50461 17,61432 oria Negativo Negativo 05/01/2018\n')
        rows = _line_rows(3, 'ocr:ita:200dpi', text, LETTER)
        self.assertEqual([r.reference for r in rows], ['152210', '152257'])
        self.assertEqual([x.kind for x in rows[1].results], ['negative', 'negative'])

    def test_ocr_noise_is_unread_not_a_result_and_an_impossible_date_is_none(self):
        self.assertEqual(_classify('rostivo'), 'unread')
        self.assertEqual(_classify('Non rilevata'), 'not-detected')
        rows = _line_rows(3, 'ocr:ita:200dpi', '156972 31/11/2017 0lvo Positivo Positivo 05/01/2018\n', LETTER)
        self.assertIsNone(rows[0].sampling_date)
        self.assertFalse(rows[0].unread)


class LetterReading(unittest.TestCase):
    def test_identity_count_delivery_and_assays_are_read_literally(self):
        facts = _letter_facts('Laboratorio multisito CNR-IPSP\nRapporto di Prova 100M/2024\nBari\n25/06/2024\n'
                              'campioni consegnati in data 20/06/2024, n. 50 campioni analizzati con il metodo MP01 (Harper et al. 2010) '
                              'e saggio Dupas per Xylella fastidiosa sottospecie multiplex')
        self.assertEqual(facts['identity'], 'Rapporto di prova 100M/2024')
        self.assertEqual(facts['stated_sample_count'], 50)
        self.assertEqual(facts['laboratory'], 'Laboratorio multisito CNR-IPSP')
        self.assertEqual(facts['report_date'], date(2024, 6, 25))
        self.assertEqual(_italian_date(facts['delivery_text']), date(2024, 6, 20))
        self.assertIn('Dupas', facts['assays'])
        self.assertIn('Xylella fastidiosa sottospecie multiplex', facts['analytes'])
        self.assertEqual(_italian_date('1 Dicembre 2017'), date(2017, 12, 1))
        self.assertFalse(facts['positives_only'])

    def test_a_positives_only_title_and_an_ocr_garbled_subject_are_read_from_the_letter(self):
        facts = _letter_facts('Rapporto di prova n. 11. - Positivi/ IAMB – 28 settembre 2023\nId\nData\n')
        self.assertTrue(facts['positives_only'])
        self.assertEqual(facts['identity'], 'Rapporto di prova 11')
        garbled = _letter_facts('Oggetto: accertamento della presenza di Xy/ella fastidiosa, mediante qgPCR\n')
        self.assertEqual(garbled['analytes'], ('Xylella fastidiosa',))
        self.assertEqual(_classify('Xy/ella'), 'unread')  # tolerance is for the subject, never a result

    def test_a_delivering_laboratory_in_a_sentence_is_not_the_reporting_laboratory(self):
        facts = _letter_facts('da parte del Laboratorio DAFNE consegnati il 04/06/2024\nOggetto: esiti\n')
        self.assertIsNone(facts['laboratory'])


class Comparison(unittest.TestCase):
    def results(self, *pairs):
        return tuple(Result('c', 'Dupas', analyte, text, _classify(text)) for analyte, text in pairs)

    def test_comparison_happens_at_the_level_the_report_states(self):
        subsp = self.results(('Xylella fastidiosa subsp. fastidiosa', 'Non rilevata'),
                             ('Xylella fastidiosa subsp. multiplex', 'Rilevata'),
                             ('Xylella fastidiosa subsp. pauca', 'Non rilevata'))
        self.assertEqual(comparison('published-positive', 'Positivi - Campioni 2024 sub. multiplex', subsp), 'agree at subspecies')
        self.assertEqual(comparison('published-positive', 'Positivi - Campioni 2024 sub. pauca', subsp), 'disagree at subspecies')
        self.assertEqual(comparison('published-positive', 'Positivi - Campioni 2021', subsp), 'not comparable')
        species = self.results(('Xylella fastidiosa', 'Rilevata'))
        self.assertEqual(comparison('published-positive', 'Positivi - Campioni 2024 sub. multiplex', species), 'agree at species')
        plain = self.results(('Xylella fastidiosa', 'Positivo'), ('Xylella fastidiosa', 'Positivo'))
        self.assertEqual(comparison('published-positive', 'Positivi - Campioni 2021', plain), 'agree at species')
        self.assertEqual(comparison('published-negative', 'Olivo - Campioni 2021', plain), 'disagree at species')
        self.assertEqual(comparison('published-positive', 'Positivi - Campioni 2021', self.results(('Xylella fastidiosa', 'rostivo'))), 'not comparable')
        self.assertEqual(comparison('published-pending', 'Positivi - Campioni 2021', plain), 'not comparable')
        self.assertEqual(comparison('published-positive', 'Positivi - Campioni 2021', self.results((None, 'Positivo'))), 'not comparable')


if __name__ == '__main__':
    unittest.main()
