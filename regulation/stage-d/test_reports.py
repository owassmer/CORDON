"""Structural rules of the report reader on inputs the work never saw."""
from datetime import date
import json
from pathlib import Path
import unittest

from cordon_d.findings import comparison, confirmation_candidates, document_name
from cordon_d.reports import (Result, Row, _classify, _designation, _flat_rows, _header_role, _italian_date,
                              _letter_facts, _line_rows, _merged_header, _table_rows, _transposed)

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

    def test_two_columns_of_one_assay_family_are_two_tests_when_the_laboratory_designates_them_apart(self):
        cells = [['Codice committente', 'Data rilevamento', 'ANALISI DIAGNOSTICHE SECONDO LIVELLO', None, None],
                 [None, None, 'Esito qPCR 2010', 'Esito qPCR 2006', 'Data Saggio'],
                 ['747145', '20/02/2020', 'Positivo', 'Positivo', '25/02/2020']]
        rows, _ = _table_rows(2, 'text-layer', _Table(cells), LETTER)
        first, second = rows[0].results
        self.assertEqual((first.assay, second.assay), ('Esito qPCR 2010', 'Esito qPCR 2006'))
        self.assertNotEqual(first.assay, second.assay)

    def test_a_column_designating_no_test_carries_no_designation(self):
        cells = [['Id', 'Data rilevamento', 'Esito laboratorio'],
                 ['1324584', '21/06/2022', 'Positivo']]
        rows, _ = _table_rows(2, 'text-layer', _Table(cells), LETTER)
        result, = rows[0].results
        self.assertIsNone(result.assay)

    def test_a_header_does_not_span_into_an_unheaded_or_a_symptom_column(self):
        unheaded = [['Codice committente', 'Data campionamento', 'Esito qPCR', None],
                    ['123456', '01/06/2024', 'Positivo', 'Assente']]
        header, _ = _merged_header(unheaded)
        self.assertEqual(header[3], '')  # the symptom column is not a second Esito qPCR
        rows, _ = _table_rows(2, 'text-layer', _Table(unheaded), LETTER)
        self.assertEqual([r.kind for r in rows[0].results], ['positive'])
        # A named symptom column: the span reaches it, so its own label must decide the role.
        named = [['Codice committente', 'Data campionamento', 'Esito qPCR Harper 2010', None],
                 [None, None, None, 'Sintomatologia'],
                 ['123456', '01/06/2024', 'Positivo', 'Presente']]
        rows, _ = _table_rows(2, 'text-layer', _Table(named), LETTER)
        self.assertEqual([(r.assay, r.kind) for r in rows[0].results], [('Esito qPCR Harper 2010', 'positive')])

    def test_a_column_stating_every_label_at_once_designates_no_test(self):
        flat = 'Id Data rilevamento Specie Comune ESITO ANALISI - PCR in tempo reale Harper et al., 2010 Data saggio'
        self.assertIsNone(_designation(flat, ''))
        self.assertEqual(_designation('ANALISI / Esito qPCR Harper 2010', ''), 'Esito qPCR Harper 2010')

    def test_the_subspecies_a_column_names_is_the_one_after_subsp(self):
        cells = [['Codice committente', 'Data rilevamento', 'Esito Harper et al., 2010 - X. fastidiosa subsp. multiplex'],
                 ['123456', '01/06/2024', 'Rilevata']]
        rows, _ = _table_rows(2, 'text-layer', _Table(cells), LETTER)
        self.assertEqual(rows[0].results[0].analyte, 'Xylella fastidiosa subsp. multiplex')

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

    def test_a_scanned_column_designates_no_test_and_a_sorted_letter_name_is_not_attached_to_it(self):
        letter = {'assays': ('Francis', 'Harper'), 'analytes': ('Xylella fastidiosa',), 'positives_only': False}
        text = ('231207 16/03/2018 olivo 40,50 17,55 Francavilla Negativo Positivo 28/03/2018\n'
                '231942 16/03/2018 olivo 40,53 17,63 Francavilla Positivo Positivo 28/03/2018\n'
                '232278 16/03/2018 olivo 40,53 17,63 Francavilla Positivo Positivo 28/03/2018\n')
        rows = _line_rows(2, 'ocr:ita:200dpi', text, letter)
        self.assertTrue(all(x.assay is None for r in rows for x in r.results))
        self.assertEqual([x.kind for x in rows[0].results], ['negative', 'positive'])

    def test_a_scanned_line_showing_a_second_row_states_no_result_but_a_complete_row_does(self):
        # The second line absorbed a neighbour whose own code OCR lost: four dates, one code.
        text = ('231207 16/03/2018 olivo 40,50 17,55 Negativo Positivo 28/03/2018\n'
                '155801 24/11/2017 olivo 40,50 17,61 Positivo Positivo 05/01/2018 24/11/2017 0livo 40,50 '
                '17,61 Positivo Positivo 05/01/2018\n')
        complete, absorbed = _line_rows(3, 'ocr:ita:200dpi', text, LETTER)
        self.assertEqual([x.kind for x in complete.results], ['negative', 'positive'])
        self.assertEqual(absorbed.results, ())
        self.assertTrue(absorbed.unread)
        self.assertIn('05/01/2018', absorbed.text)      # its text is kept
        # A line naming two sample codes is two rows however few results it shows. (A second
        # code that follows a date is split into its own row earlier, so this one carries none.)
        two_codes = _line_rows(4, 'ocr:ita:200dpi', '231207 olivo Positivo 231942 olivo Negativo\n', LETTER)
        self.assertEqual(len(two_codes), 1)
        self.assertEqual(two_codes[0].results, ())
        # The rule is the line's own, so one complete row on a page of one is still read.
        alone = _line_rows(5, 'ocr:ita:200dpi', text.split('\n')[0] + '\n', LETTER)
        self.assertEqual([x.kind for x in alone[0].results], ['negative', 'positive'])

    def test_a_year_run_into_the_next_word_is_not_a_second_sample(self):
        # OCR glues the year to the species (`16/03/20180lvo`) and prefixes a code with a
        # stray letter; neither shows a second row, and the row states what it prints.
        glued = _line_rows(2, 'ocr:ita:200dpi',
                           '282377   16/03/20180lvo (lea europea) 40,48 17,53 Francavila Positivo Postivo 03/04/2019\n',
                           LETTER)
        # `Postivo` is not a result word, so the row states the one result it does print.
        self.assertEqual([x.kind for x in glued[0].results], ['positive'])
        prefixed = _line_rows(3, 'ocr:ita:200dpi',
                              'L259726 04/04/2018 10livo (Olea europaea) 40,66 17,73 Positivo Positivo 07/05/2018\n',
                              LETTER)
        self.assertEqual(prefixed[0].reference, '259726')
        self.assertEqual([x.kind for x in prefixed[0].results], ['positive', 'positive'])

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

    def test_a_report_number_with_a_letter_prefix_is_not_replaced_by_the_protocol_register(self):
        facts = _letter_facts('RAPPORTO DI PROVA/TEST REPORT : N. XF 015/2024\nProt. Selge 17/2024\n')
        self.assertEqual(facts['identity'], 'Rapporto di prova XF 015/2024')
        self.assertEqual(_letter_facts('Rapporto di prova N. 89a/2024\n')['identity'], 'Rapporto di prova 89a/2024')
        self.assertEqual(_letter_facts('RAPPORTO DI PROVA N° 1038/22\n')['identity'], 'Rapporto di prova 1038/22')

    def test_a_number_the_text_layer_breaks_across_lines_is_read_whole(self):
        # The publisher's own PDF emits `XF 0 1 9 / 202 4`; the number is one number.
        broken = _letter_facts('RAPPORTO DI PROVA/TEST REPORT\n: N. \nXF\n0 1 9 / 202\n4 \nAffidamento del servizio\n')
        self.assertEqual(broken['identity'], 'Rapporto di prova XF 019/2024')
        suffixed = _letter_facts('RAPPORTO DI PROVA/TEST REPORT\n: N. \nXF\n2 1 _P /202 2\n')
        self.assertEqual(suffixed['identity'], 'Rapporto di prova XF 21_P/2022')
        # A two-digit year the publisher really prints is not widened.
        self.assertEqual(_letter_facts('Rapporto di prova N. 41/24\nM 44\nRev. 3 del 09/02/2024\n')['identity'],
                         'Rapporto di prova 41/24')

    def test_a_delivering_laboratory_in_a_sentence_is_not_the_reporting_laboratory(self):
        facts = _letter_facts('da parte del Laboratorio DAFNE consegnati il 04/06/2024\nOggetto: esiti\n')
        self.assertIsNone(facts['laboratory'])


class Comparison(unittest.TestCase):
    def results(self, *pairs):
        return tuple(Result('c', 'Esito saggio Dupas', analyte, text, _classify(text)) for analyte, text in pairs)

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


class RouteIdentity(unittest.TestCase):
    def test_one_document_is_one_document_at_either_scheme(self):
        http = 'http://webadf.sit.puglia.it/openDoc/apridocumento?nomeFile=DatiCampioniXF/PDF/RAPPORTO_PROVA_N_7.pdf'
        https = http.replace('http://', 'https://')
        self.assertEqual(document_name(http), 'RAPPORTO_PROVA_N_7.pdf')
        self.assertEqual(document_name(http), document_name(https))
        self.assertEqual(document_name('http://cartografia.sit.puglia.it/doc/xylella/x/RAPPORTO_PROVA_N_3P_2026_CNR.pdf'),
                         'RAPPORTO_PROVA_N_3P_2026_CNR.pdf')


class ArticleTwoSix(unittest.TestCase):
    """What a report hands `confirmation_facts`, and what it makes C refuse."""

    def row(self, *columns):
        results = tuple(Result(f'c{i}', designation, 'Xylella fastidiosa', text, _classify(text))
                        for i, (designation, text) in enumerate(columns))
        return Row(2, 'text-layer', '747145', 'sample', date(2020, 2, 20), 'olivo',
                   None, None, None, results, date(2020, 2, 25), 'row', False)

    def test_two_differently_designated_detected_columns_are_two_tests_on_one_sample(self):
        candidates = confirmation_candidates(self.row(('Esito qPCR 2010', 'Positivo'), ('Esito qPCR 2006', 'Positivo')),
                                             sample='747145')
        self.assertEqual(candidates['first_test'], 'Esito qPCR 2006')
        self.assertEqual(candidates['second_test'], 'Esito qPCR 2010')
        self.assertEqual(candidates['first_sample'], candidates['second_sample'])
        self.assertIsNone(candidates['first_genome_target'])

    def test_the_same_assay_on_two_dates_or_marked_a_repetition_is_one_test(self):
        for second in ('Esito qPCR Harper 2010 del 11/05/2021', 'Esito qPCR Harper 2010 (ripetizione)'):
            row = self.row(('Esito qPCR Harper 2010 del 04/05/2021', 'Positivo'), (second, 'Positivo'))
            self.assertIsNone(confirmation_candidates(row, sample='747145'), second)
        two = self.row(('Esito qPCR Harper 2010 del 04/05/2021', 'Positivo'),
                       ('Esito qPCR Ouyang 2013 del 04/05/2021', 'Positivo'))
        self.assertIsNotNone(confirmation_candidates(two, sample='747145'))

    def test_one_column_or_one_designation_or_a_negative_column_supplies_no_candidate(self):
        self.assertIsNone(confirmation_candidates(self.row(('Esito qPCR 2010', 'Positivo')), sample='747145'))
        self.assertIsNone(confirmation_candidates(self.row(('Esito qPCR', 'Positivo'), ('Esito qPCR', 'Positivo')),
                                                  sample='747145'))
        self.assertIsNone(confirmation_candidates(self.row(('Esito qPCR 2010', 'Positivo'), ('Esito qPCR 2006', 'Negativo')),
                                                  sample='747145'))
        self.assertIsNone(confirmation_candidates(self.row((None, 'Positivo'), (None, 'Positivo')), sample='747145'))

    def test_c_refuses_article_2_6_for_want_of_the_genome_target_rather_than_deciding_against_it(self):
        from cordon_c.bindings import confirmation_facts
        from cordon_c.core import Evaluation, Snapshot
        owner = json.loads((Path(__file__).resolve().parents[1] / 'stage-a/authoring-eu.json').read_text())
        rows = owner if isinstance(owner, list) else owner['provision_versions']
        article = [r for r in rows if r['stable_provision_id'] == 'EU-2020-1201:2(6)']
        snapshot = Snapshot(article, dict(clocks=[], parameters=[], dispositions=[]))
        candidates = confirmation_candidates(self.row(('Esito qPCR 2010', 'Positivo'), ('Esito qPCR 2006', 'Positivo')),
                                             sample='747145')
        facts = confirmation_facts(snapshot, date(2021, 6, 1),
                                   first_positive_annex_iv=Evaluation(True), second_positive_annex_iv=Evaluation(True),
                                   same_extract_route_appropriate=Evaluation(None),
                                   inside_demarcated_area=Evaluation(True), **candidates)
        # The two designated tests satisfy the second-test limb; the genome target the
        # report never prints leaves that limb unresolved, not refused.
        by_predicate = {predicate: value for (_, predicate), value in facts.items()}
        self.assertIs(by_predicate['second positive Annex IV molecular test on the same plant sample'
                                   ' or, where appropriate, the same plant extract'].truth, True)
        target = by_predicate['different genome target']
        self.assertIsNone(target.truth)
        self.assertIn('resolved genome-target identities', target.needs)
        self.assertEqual(facts[('EU-2020-1201:2(6):v1', 'different genome target')], target)


if __name__ == '__main__':
    unittest.main()
