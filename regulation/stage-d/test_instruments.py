"""Row 9's instruments besides the register: the national list (L. 10/2013 Art. 7) and Art. 136 declarations.

`Rules` runs everywhere on unseen fixture records: each rule's expected answer is stated from the rule, not taken
from the reader. `HeldInstruments` runs the ordinary readers over this checkout's store and skips where the bytes are
not held; its expected answers come from reading the MASAF sheet and annexes and the PPTR layer, cited beside each.
"""
from dataclasses import replace
from datetime import date
import json
from pathlib import Path
import unittest
from unittest import mock

from cordon_d import instruments as I
from cordon_d.store import blob_path, put_bytes, store_root

ROOT = Path(__file__).resolve().parents[2]
STORE = store_root(ROOT)


def decree(number, adopted, published):
    return I.Decree(number, adopted, 'G.U. n. 1', published, ())


LISTING = decree('1', date(2018, 8, 9), date(2018, 10, 4))
DELETING = decree('2', date(2022, 7, 26), date(2022, 8, 5))


def entry(scheda='99/Z999/LE/16', x=0.0, y=0.0, species='Quercus ilex L.', listed=LISTING, deleted=None):
    return I.ListEntry(scheda, 'Lecce', 'Fixture', 'Località di prova', "40° 0' 0''", "18° 0' 0''", x, y, species,
                       'single tree', 'not printed', '400', '12,0', 'no', 'listed', None, 'fixture', listed, deleted)


class Plant:
    def __init__(self, plant, x, y, error_m=7.4, kind='in-reach positive', species=None):
        self.plant, self.x, self.y, self.error_m, self.kind, self.species = plant, x, y, error_m, kind, species


def declaration(code='PAE9999', reading='area', geometry=None, genus=None, decree_date='08-01-1973', cite=None):
    from shapely.geometry import Point
    return I.Declaration(code, None, 'Fixture', 'DICHIARAZIONE DI NOTEVOLE INTERESSE PUBBLICO DI UNA ZONA', '', decree_date,
                         'notifica del 06-04-1973', 'Istituito ai sensi della L. 1497', 'art.136, co. 1, lettera a)', ('v',),
                         geometry if geometry is not None else Point(0, 0).buffer(15), ('fixture',), reading, cite, genus)


def held(entries=(), declared=(), proposed=()):
    bound = I.list_bound([])
    return I.Instruments(list(entries), [LISTING, DELETING], bound, list(declared), [{'version': 'v'}], list(proposed))


# The held layer's object and motivation of PAE0156 (Corigliano d'Otranto) and of PAE0061 (Miggiano), verbatim.
VALONIA = ("DICHIARAZIONE DI NOTEVOLE INTERESSE PUBBLICO DI UNA ZONA IN COMUNE DI CORIGLIANO D'OTRANTO",
           "Nella zona insiste la quercia vallonea inesistente in tutto il Mediterraneo e in estinzione anche nella zona "
           "considerata. L'et approssimativa dell'albero si aggira in 350 anni, con circonferenza tronco m. 2,50, "
           "diametro chioma m. 22, altezza m.13.")
EPISCOPO = ("BOSCO PROPRIETA` EPISCOPO - MIGGIANO",
            "Complesso boscato, costituito in prevalenza da quecus Ilex e Quercus Coccifera ha conservato al sua "
            "feracit, fertilit, densit e l'originario aspetto simbiotico con gli elementi arbustivi ed erbacei della "
            "zona fitoclimatica cui appartiene")


class Rules(unittest.TestCase):

    def test_an_unseen_entry_inside_a_zone_is_admitted_with_its_instrument(self):
        # 80 m from a positive: outside 50 m, inside 50 m + the positive's 7.4 m + the list's 50 m bound.
        record = I.list_plants([entry(x=80.0)], I.list_bound([]))[0]
        found = I.placed([record], [Plant('P1', 0.0, 0.0)])
        self.assertEqual([(r.plant, p) for r, p, _, _ in found], [('99/Z999/LE/16', 'P1')])
        facts = held([entry(x=80.0)]).facts(record.x, record.y, record.error_m, record.genus, date(2026, 10, 28),
                                            own=record)
        self.assertIs(facts[I.NATIONAL]['value'], True)

    def test_an_entry_beyond_the_zone_and_both_errors_is_not_admitted(self):
        record = I.list_plants([entry(x=108.0)], I.list_bound([]))[0]
        self.assertEqual(I.placed([record], [Plant('P1', 0.0, 0.0)]), [])

    def test_an_area_declaration_gives_no_status(self):
        self.assertEqual(I.read_motivation(*EPISCOPO)[0], 'area')
        facts = held(declared=[declaration()]).facts(0.0, 0.0, 7.4, 'Quercus', date(2026, 10, 28))
        self.assertIs(facts[I.DECLARATION]['value'], False)
        self.assertIn('PAE9999', facts[I.DECLARATION]['cause'])

    def test_a_tree_the_motivation_names_gets_status(self):
        reading, cite, genus = I.read_motivation(*VALONIA)
        self.assertEqual((reading, genus), ('names a tree', 'Quercus'))
        named = declaration(reading=reading, genus=genus, cite=cite)
        record = I.declared_plants([named])[0]
        self.assertEqual([p for _, p, _, _ in I.placed([record], [Plant('P1', 60.0, 0.0)])], ['P1'])
        facts = held(declared=[named]).facts(record.x, record.y, record.error_m, record.genus, date(2026, 10, 28),
                                             own=record)
        self.assertIs(facts[I.DECLARATION]['value'], True)
        # A plant of the tree's genus within reach may be the declared tree: identity, never a definite false.
        plant = held(declared=[named]).facts(5.0, 0.0, 7.4, 'Quercus', date(2026, 10, 28))
        self.assertIsNone(plant[I.DECLARATION]['value'])
        # Its decree is of 8 January 1973 and notified on 6 April 1973: between them A decides.
        between = held(declared=[named]).facts(record.x, record.y, record.error_m, record.genus, date(1973, 2, 1),
                                               own=record)
        self.assertIsNone(between[I.DECLARATION]['value'])

    def test_a_wood_with_a_few_specimens_names_no_tree(self):
        # PAE0083's motivation as its scheda prints it (from D.M. 31/08/1970), in part, verbatim.
        wood = ("La zona predetta ha notevole interesse pubblico perché, per la sua originaria bellezza e composizione "
                "naturale, caratterizzata di macchie verdi ed essenze locali, nonché da un bosco che si sviluppa lungo "
                "parte del litorale, con piante di pino Aleppo, pino domestico e qualche esemplare di cipresso ed "
                "eucaliptus, costituisce un quadro panoramico di grande rilievo.")
        self.assertNotIn(I.read_motivation('ZONA COSTIERA', wood)[0], ('names a tree', 'names a row or group'))
        self.assertEqual(I.read_motivation('ZONA', 'Nella zona insiste un esemplare di cedro del Libano')[0],
                         'names a tree')

    def test_a_delimitation_s_road_stretch_or_circle_names_no_tree(self):
        # PAE0113's decree (D.M. 1-8-1985) delimits its woods along "la strada vicinale Piano d'Annaia (secondo
        # tronco)": a road's stretch. A trunk's measurement still names the tree.
        road = 'fino all\'incrocio con la strada vicinale Piano d\'Annaia (secondo tronco) punto F. LATO SUD: tratto F-G'
        self.assertEqual(I.read_motivation('ZONE BOSCHIVE', road + '.' * 300)[0], 'not read whole')
        self.assertEqual(I.read_motivation('ZONA', 'La zona compresa in una circonferenza di raggio m. 500.')[0], 'area')
        self.assertEqual(I.read_motivation('ZONA', 'Un leccio secolare con il tronco di m. 4,10 di giro.')[0], 'names a tree')

    def test_a_curly_apostrophe_or_a_word_broken_by_its_hyphen_mid_line_still_names_a_tree(self):
        # Tesseract prints ’; a transcription of a table cell ran its lines together, keeping "esteti-co".
        self.assertEqual(I.read_motivation('ZONA', 'Nella zona sorge l\u2019albero detto della Madonna.')[0], 'names a tree')
        self.assertEqual(I.read_motivation('ZONA', 'Nella zona insiste un esem-plare di quercia vallonea.')[:3:2],
                         ('names a tree', 'Quercus'))
        self.assertEqual(I.read_motivation('ZONA', 'La zona, con le sue masserie e i suoi muretti, ha valore esteti-co.')[0],
                         'area')

    def test_a_text_naming_trees_of_several_genera_gives_none(self):
        # PAE0093's decree (D.M. 9-7-1990) names in its villas' gardens "pini, cedri, eucalipti, querce, corbezzoli ed
        # un grande esemplare di fitolacca": the tree it names may be of any genus.
        gardens = ('con numerose essenze arboree quali pini, cedri, eucalipti, querce, corbezzoli ed un grande esemplare '
                   'di fitolacca')
        self.assertEqual(I.read_motivation('AREE E VILLE', gardens)[::2], ('names a tree', None))
        self.assertEqual(I.read_motivation(*VALONIA)[2], 'Quercus')

    def test_a_motivation_cut_at_the_field_length_is_not_read_whole(self):
        cut = 'La zona ha notevole interesse pubblico perche ' + 'x' * 220
        self.assertEqual(I.read_motivation('ZONA COSTIERA', cut)[0], 'not read whole')
        facts = held(declared=[declaration(reading='not read whole')]).facts(0.0, 0.0, 7.4, 'Olea', date(2026, 10, 28))
        self.assertIsNone(facts[I.DECLARATION]['value'])

    def test_a_tree_any_text_names_is_not_overruled_by_a_whole_text_naming_none(self):
        layer = I.read_motivation(*VALONIA)
        scheda = ('area', "the scheda's motivation names no tree, row or group", None)
        self.assertEqual(I.combined(scheda, layer)[0], 'names a tree')
        self.assertEqual(I.combined(scheda, ('not read whole', 'cut', None))[0], 'area')

    def test_an_entry_deleted_by_a_later_decree_reads_false_after_the_deletion(self):
        gone = entry(deleted=DELETING)
        self.assertEqual(I.in_force(gone, date(2021, 1, 1))[0], True)
        self.assertEqual(I.in_force(gone, date(2022, 8, 5))[0], False)
        # Between the deleting decree and its G.U. publication A decides when it takes effect.
        self.assertIsNone(I.in_force(gone, date(2022, 8, 1))[0])
        self.assertEqual(I.in_force(gone, date(2018, 1, 1))[0], False)

    def test_an_entry_no_held_annex_lists_is_unknown_not_false(self):
        self.assertIsNone(I.in_force(entry(listed=None), date(2026, 10, 28))[0])

    def test_a_plant_near_an_entry_of_another_genus_reads_false_and_of_its_genus_unknown(self):
        state = held([entry(x=20.0)])
        self.assertIs(state.facts(0.0, 0.0, 7.4, 'Olea', date(2026, 10, 28))[I.NATIONAL]['value'], False)
        self.assertIsNone(state.facts(0.0, 0.0, 7.4, 'Quercus', date(2026, 10, 28))[I.NATIONAL]['value'])
        self.assertIs(state.facts(500.0, 0.0, 7.4, 'Quercus', date(2026, 10, 28))[I.NATIONAL]['value'], False)

    def test_a_plant_in_no_instrument_reads_false_naming_the_populations_held(self):
        facts = held([entry(x=5000.0)], [declaration(geometry=None)]).facts(
            9000.0, 0.0, 7.4, None, date(2026, 10, 28), register={'identity': 'not a register tree', 'cause': 'none'})
        self.assertEqual([facts[k]['value'] for k in (I.NATIONAL, I.DECLARATION)], [False, False])
        self.assertIn('2 decree versions', facts[I.NATIONAL]['held'])
        self.assertIn('1 declarations printed by 1 PPTR versions', facts[I.DECLARATION]['held'])
        self.assertEqual(facts[I.REGISTER]['identity'], 'not a register tree')

    def test_the_list_bound_takes_the_floor_under_twenty_fixes(self):
        self.assertEqual(I.list_bound([]).error_m, 50.0)
        self.assertEqual(I.list_bound([12.0, 61.5]).error_m, 61.5)
        self.assertEqual(I.list_bound([float(i) for i in range(1, 21)]).error_m, 19.05)

    def test_the_kind_is_read_from_the_species_cell(self):
        self.assertEqual(I._genus('Insieme omogeneo di Quercus suber L.'), 'Quercus')
        self.assertEqual(next(k for k, p in I._KINDS if p.search('Insieme omogeneo di Quercus suber L.')),
                         'insieme omogeneo')


# An unseen Ministry proposal naming one tree, as a Soprintendenza's notice prints one (Art. 136(1)(a)): its albo
# periods, the owner's receipt of the communication (Art. 139(3)-(4)) and its plan at 1:2,000 are fixture values.
TREE_OBJECT = 'PROPOSTA DI DICHIARAZIONE DI NOTEVOLE INTERESSE PUBBLICO DELLA QUERCIA DI MASSERIA FIXTURA'
TREE_MOTIVATION = ("L'albero, un esemplare di quercia vallonea di circa 400 anni, con circonferenza del tronco di m 4,80, "
                   'costituisce una singolarita\' naturale di non comune bellezza')
# Herdonia's notice (SABAP-FG, 4 March 2024), its object as printed: a context, an area.
AREA_OBJECT = ('PROPOSTA DI DICHIARAZIONE DI NOTEVOLE INTERESSE PUBBLICO DEL CONTESTO “HERDONIA, AUSCULUM E ALTA VALLE DEL '
               'CARAPELLE” ai sensi dell’art. 136, co. 1, lett. c) e d)')


def proposal(obj=TREE_OBJECT, motivation=TREE_MOTIVATION, geometry=None, scale_term_m=2.0, code='PROP-FIXTURE'):
    from datetime import date as day
    reading, cite, genus = I.read_motivation(obj, motivation)
    return I.Proposal(code, 'ministry', 'Fixturia', obj, motivation, reading, cite, genus,
                      ((day(2024, 3, 11), day(2024, 6, 9), "dall'11 marzo 2024 al 9 giugno 2024"),
                       (day(2024, 3, 14), day(2024, 6, 12), 'dal 14/03/2024 al 12/06/2024')),
                      day(2024, 2, 20), {'kind': 'none'}, ('fixture',), (), geometry, scale_term_m)


class Proposals(unittest.TestCase):
    """A published proposal of declaration through the declared-tree path, with the dates C's row reads."""

    def test_a_proposal_naming_a_tree_gives_its_fact_with_its_dates(self):
        from shapely.geometry import Point
        tree = proposal(geometry=Point(55.0, 0.0).buffer(1.0))
        self.assertEqual((tree.reading, tree.genus), ('names a tree', 'Quercus'))
        # 54 m from a positive: outside 50 m, inside 50 m + the positive's 7.4 m + 1 mm at the plan's 1:2,000.
        record = I.declared_plants([tree], I.PROPOSAL)[0]
        # Its error: the drawn tree's reach from its point (about 1 m) plus 1 mm at its plan's 1:2,000, not the PPTR's.
        self.assertLess(record.error_m, 4.0)
        self.assertEqual([(r.plant, p) for r, p, _, _ in I.placed([record], [Plant('P1', 0.0, 0.0)])],
                         [('PROP-FIXTURE', 'P1')])
        instruments = held(proposed=[tree])
        own = instruments.facts(record.x, record.y, record.error_m, record.genus, date(2026, 10, 28), own=record)
        fact = own.get(I.PROPOSAL, {})
        self.assertIs(fact.get('value'), True)
        self.assertEqual({k: fact['proposals'][0][k] for k in ('proposer', 'first_publication', 'owner_communication')},
                         {'proposer': 'ministry', 'first_publication': '2024-03-11', 'owner_communication': '2024-02-20'})
        self.assertEqual([p['to'] for p in fact['proposals'][0]['periods']], ['2024-06-09', '2024-06-12'])
        # A monitored oak on the drawn tree may be it: unknown, with the same dates; one 1 km off reads false.
        near = instruments.facts(55.0, 0.0, 7.4, 'Quercus', date(2026, 10, 28)).get(I.PROPOSAL, {})
        self.assertIsNone(near.get('value', False))
        self.assertEqual(near['proposals'][0]['first_publication'], '2024-03-11')
        self.assertIs(instruments.facts(1000.0, 0.0, 7.4, 'Quercus', date(2026, 10, 28)).get(I.PROPOSAL, {}).get('value'),
                      False)

    def test_an_area_proposal_gives_no_status(self):
        area = proposal(obj=AREA_OBJECT, motivation='')
        self.assertEqual(area.reading, 'area')
        fact = held(proposed=[area]).facts(0.0, 0.0, 7.4, 'Olea', date(2026, 10, 28)).get(I.PROPOSAL, {})
        self.assertIs(fact.get('value'), False)
        self.assertIn('PROP-FIXTURE', fact['cause'])
        self.assertEqual(I.declared_plants([area], I.PROPOSAL), [])

    def test_a_proposal_naming_a_tree_no_held_plan_places_is_unknown_not_false(self):
        fact = held(proposed=[proposal()]).facts(0.0, 0.0, 7.4, 'Olea', date(2026, 10, 28)).get(I.PROPOSAL, {})
        self.assertIsNone(fact.get('value', False))
        self.assertIn('no plan that places it', fact['cause'])

    def test_a_plant_in_no_proposal_reads_false_naming_the_population_held(self):
        fact = held().facts(0.0, 0.0, 7.4, 'Olea', date(2026, 10, 28)).get(I.PROPOSAL, {})
        self.assertIs(fact.get('value'), False)
        self.assertIn('0 published proposals of declaration held', fact['held'])

    def test_a_field_is_read_only_where_its_source_prints_it(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            root, store = Path(folder) / 'root', Path(folder) / 'store'
            notice = (f'<html><body><p>Oggetto: {AREA_OBJECT}</p><p>Pubblicata all’albo pretorio del Comune di Fixturia '
                      'dall’11 marzo 2024 al 9 giugno 2024.</p><p>Comunicazione al proprietario ricevuta il '
                      '20/02/2024.</p></body></html>').encode()
            source = put_bytes(store, notice)
            record = {'proposals': [
                {'proposal': 'Herdonia-like', 'proposer': 'ministry', 'comuni': ['Fixturia'],
                 'object': {'text': AREA_OBJECT, 'source': source},
                 'motivation': {'text': None, 'cause': 'its relazione is not held'},
                 'publication': [{'text': 'dall’11 marzo 2024 al 9 giugno 2024', 'source': source}],
                 'owner_communication': {'text': 'ricevuta il 20/02/2024', 'source': source}},
                {'proposal': 'misquoted', 'proposer': 'region', 'comuni': ['Fixturia'],
                 'object': {'text': TREE_OBJECT, 'source': source}}]}
            (root / I.SOURCES).mkdir(parents=True)
            (root / I.SOURCES / 'proposals.json').write_text(json.dumps(record))
            found, _, problems = I.proposals(store, root)
        by = {p.code: p for p in found}
        self.assertEqual(by['Herdonia-like'].reading, 'area')
        self.assertEqual(by['Herdonia-like'].first_publication(), date(2024, 3, 11))
        self.assertEqual(by['Herdonia-like'].owner_communication, date(2024, 2, 20))
        self.assertIn('motivation: its relazione is not held', by['Herdonia-like'].causes)
        # An object its source does not print is not read, and the reading says so rather than naming an area.
        self.assertEqual((by['misquoted'].obj, by['misquoted'].reading), ('', 'not read whole'))
        self.assertEqual(problems, [f'misquoted: its object is not printed by the source it cites ({source[:12]})'])


def page_image_pdf(text: str) -> bytes:
    """A one-page PDF holding only an image of `text`: it has no text layer."""
    import pymupdf
    source = pymupdf.open()
    page = source.new_page(width=595, height=842)
    page.insert_textbox(pymupdf.Rect(60, 60, 535, 800), text, fontsize=11, fontname='helv')
    pixmap = page.get_pixmap(dpi=200, colorspace=pymupdf.csGRAY)
    out = pymupdf.open()
    image = out.new_page(width=595, height=842)
    image.insert_image(image.rect, stream=pixmap.tobytes('png'))
    return out.tobytes()


# An unseen decree in the form of the L. 1497/1939 decrees the G.U. prints, and its declaration as the PPTR layer prints
# one: the layer's motivation stops at its field length, so the layer alone does not read it whole.
DECREE = """DECRETO MINISTERIALE 12 marzo 1971.
Dichiarazione di notevole interesse pubblico di una zona sita nel comune di Fixturia.
IL MINISTRO PER LA PUBBLICA ISTRUZIONE
Vista la legge 29 giugno 1939, n. 1497, sulla protezione delle bellezze naturali;
Riconosciuto che {};
Decreta:
La zona sita nel territorio del comune di Fixturia ha notevole interesse pubblico ai sensi della legge 29 giugno
1939, n. 1497, ed e' quindi sottoposta a tutte le disposizioni contenute nella legge stessa.
Roma, addi' 12 marzo 1971
(4321)"""
NAMING = 'nella zona predetta insiste una quercia vallonea secolare, con circonferenza del tronco di metri 4,10'
NAMING_NONE = 'la zona predetta forma un quadro naturale di non comune bellezza panoramica, ricco di uliveti e macchia'
CUT = ('La zona ha notevole interesse pubblico perche forma un quadro naturale di non comune bellezza panoramica, con '
       'punti di vista accessibili al pubblico dai quali si gode lo spettacolo della costa e delle colline che la '
       'circondano, con le sue masserie e i suoi muretti a secco, e la vista ')


def fixture_declaration(store: Path, root: Path, decree: bytes, motivation: str = CUT):
    """The declaration PAE9001 read through `declarations` from a fixture layer page and its decree issue."""
    from cordon_d.store import put_bytes
    attributes = {'CODICE': 'PAE9001', 'COD_SITAP': None, 'COMUNE': 'FIXTURIA',
                  'OGGETTO__1': 'DICHIARAZIONE DI NOTEVOLE INTERESSE PUBBLICO DI UNA ZONA IN COMUNE DI FIXTURIA',
                  'MOTIVAZI_1': motivation, 'NUMERO_DEC': '12-03-1971', 'PUBBLICATO': 'G.U. n. 99 del 20-04-1971',
                  'ID_VINCOLI': 'Istituito ai sensi della L. 1497', 'ART_136_C': 'art.136, co. 1, lettera c)'}
    ring = [[0.0, 0.0], [0.0, 100.0], [100.0, 100.0], [100.0, 0.0], [0.0, 0.0]]
    layer = put_bytes(store, json.dumps({'features': [{'attributes': attributes, 'geometry': {'rings': [ring]}}]}).encode())
    record = {'versions': [{'version': 'fixture', 'layer': 0, 'rows': 1, 'pages': [{'sha256': layer}]}],
              'decrees': [{'url': 'fixture', 'declarations': ['PAE9001'], 'sha256': put_bytes(store, decree)}],
              'schede': {'schede': []}}
    (root / I.SOURCES).mkdir(parents=True, exist_ok=True)
    (root / I.SOURCES / 'declarations.json').write_text(json.dumps(record))
    declared, versions, _ = I.declarations(store, root)
    return declared[0], held(declared=declared)


# The locator's engine in `VisionRoute`: its OCR'd text is supplied by the test, held as Tesseract's would be, so the
# route runs where Tesseract is not installed. No fixture page is ever OCR'd with it.
FIXTURE_ENGINE = {'tesseract': 'fixture', 'leptonica': 'fixture', 'model': 'ita.traineddata', 'model_sha256': '0' * 64,
                  'pymupdf': 'fixture', 'dpi': I.OCR_DPI, 'render': I.OCR_RENDER, 'args': list(I.OCR_ARGS),
                  'reader': I.OCR_READER, 'executable': None}
# How Tesseract garbles NAMING: no tree word survives, so the OCR'd words name none.
GARBLED = 'nella zona predetta insiste una qucrcia vallonca secolare, con circonfcrenza dcl tronco di mctri 4,10'
# PAE0013's decree (D.M. 23 January 1976, Fasano) and PAE0123's (D.M. 1 August 1985), as OCR reads them.
FASANO = ("si passa quindi alla zona di Torre Canne formata da una suggestiva fascia tutta a sabbia dorata che arriva "
          "fino al confine con Ostuni e nella quale è compresa la «zona termale », unica nel lungo tratto da Margherita "
          "di Savoia (Foggia) a Santa Cesarea Terme (Lecce), il tutto con una spalliera di verde formata da alberi "
          "secolari di ulivo che completano felicemente l'ambiente")


def held_ocr(store: Path, digest: str, index: int, text: str):
    """The locator's text of a page, held as an OCR reading is (Tesseract's TSV, a word to a row, no ruled lines)."""
    rows = ['level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext']
    for n, line in enumerate(text.splitlines(), 1):
        rows += [f'5\t1\t1\t1\t{n}\t{k}\t{10 * k}\t{20 * n}\t9\t15\t95\t{w}' for k, w in enumerate(line.split(), 1)]
    path = I._ocr_path(store, digest, index, FIXTURE_ENGINE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'source': digest, 'page': index, 'rules': {'vertical': [], 'horizontal': []},
                                'tsv': '\n'.join(rows)}))


def held_transcription(store: Path, digest: str, index: int, text: str) -> str:
    """A transcription answer supplied by the test, kept where and as `_subscription_call` keeps one; no request."""
    import pymupdf
    request_id = I.transcription_request(pymupdf.open(blob_path(store, digest)), digest, index)[0]
    path = I.transcription_path(store, request_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'provider': 'claude-code-subscription', 'request_sha256': request_id,
                                'model': I.TRANSCRIPTION_MODEL, 'effort': I.TRANSCRIPTION_EFFORT,
                                'response': {'structured_output': {'text': text}}}))
    return request_id


class VisionRoute(unittest.TestCase):
    """OCR locates a page-image decree; D's rule reads the words of its vision transcription. Both texts are supplied
    here, so the expected answers are the fixture's own words."""

    def setUp(self):
        import tempfile
        self.directory = tempfile.TemporaryDirectory()
        self.store, self.root = Path(self.directory.name) / 'store', Path(self.directory.name) / 'root'
        engine = mock.patch.object(I, 'ocr_engine', return_value=FIXTURE_ENGINE)
        engine.start()
        self.addCleanup(engine.stop)

    def tearDown(self):
        self.directory.cleanup()

    def read(self, located: str, transcribed: str | None):
        pdf = page_image_pdf(transcribed or located)
        digest = put_bytes(self.store, pdf)
        held_ocr(self.store, digest, 0, located)
        request = transcribed is not None and held_transcription(self.store, digest, 0, transcribed)
        return (*fixture_declaration(self.store, self.root, pdf), request)

    def test_a_transcription_naming_a_tree_gives_status_and_one_naming_none_reads_area(self):
        # Tesseract's words name no tree; the transcription's do, and they are what is read.
        declaration, state, request = self.read(DECREE.format(GARBLED), DECREE.format(NAMING))
        self.assertEqual((declaration.reading, declaration.genus), ('names a tree', 'Quercus'))
        route = f'vision transcription by {I.TRANSCRIPTION_MODEL}: page 1, request {request}'
        self.assertTrue(declaration.decree['read'].startswith(f'read from the vision transcription of page 1 ({route}); '
                                                              'located by OCR (OCR: Tesseract fixture'))
        self.assertEqual(declaration.decree['transcriptions'],
                         [{'page': 1, 'model': I.TRANSCRIPTION_MODEL, 'request_sha256': request}])
        record = I.declared_plants([declaration])[0]
        facts = state.facts(record.x, record.y, record.error_m, record.genus, date(2026, 10, 28), own=record)
        self.assertIs(facts[I.DECLARATION]['value'], True)
        # Tesseract's words name a tree; the transcription's name none: an area, citing the transcription.
        declaration, state, request = self.read(DECREE.format(NAMING), DECREE.format(NAMING_NONE))
        self.assertEqual(declaration.reading, 'area')
        self.assertEqual(declaration.cite, f'the transcribed text names no tree, row or group (vision transcription by '
                                           f'{I.TRANSCRIPTION_MODEL}: page 1, request {request})')
        facts = state.facts(50.0, 50.0, 7.4, 'Olea', date(2026, 10, 28))
        self.assertEqual((facts[I.DECLARATION]['value'], 'PAE9001' in facts[I.DECLARATION]['cause']), (False, True))

    def test_a_reading_names_what_the_transcription_does_not_let_it_read(self):
        # A held answer writes "venticinque" with a Cyrillic "с" (G.U. n. 265/1975, page 12): a tree word so written
        # is not seen, and a word marked illegible is not read; the area reading names both.
        text = DECREE.format(NAMING_NONE.replace('macchia', I.ILLEGIBLE).replace('ricco', 'riсco'))
        declaration, _, _ = self.read(DECREE.format(NAMING_NONE), text)
        self.assertEqual(declaration.reading, 'area')
        self.assertTrue(declaration.cite.endswith(
            '); 1 word marked illegible; letters outside the Latin script: с (CYRILLIC SMALL LETTER ES)'))

    def test_trees_named_as_part_of_the_area_declared_give_no_status(self):
        # Owen, 2026-10-29: the coast is the thing declared; its olive hedge is one feature of it.
        declaration, state, _ = self.read(DECREE.format(FASANO), DECREE.format(FASANO))
        self.assertEqual((declaration.reading, declaration.decree['reading']), ('area', 'area'))
        self.assertIn('alberi secolari di ulivo', declaration.decree['decree_text'][0])
        self.assertIs(state.facts(50.0, 50.0, 7.4, 'Olea', date(2026, 10, 28))[I.DECLARATION]['value'], False)

    def test_an_untranscribed_page_keeps_the_ocr_reading_naming_that(self):
        declaration, _, _ = self.read(DECREE.format(GARBLED), None)
        self.assertEqual(declaration.reading, 'area')
        untranscribed = "the vision transcription of page 1 is not yet held: the words read are Tesseract's"
        self.assertTrue(declaration.cite.startswith("the OCR'd text names no tree, row or group (OCR: Tesseract fixture"))
        self.assertTrue(declaration.cite.endswith(untranscribed))
        self.assertTrue(declaration.decree['read'].startswith('read by OCR, page 1 ('))
        self.assertTrue(declaration.decree['read'].endswith(untranscribed))
        self.assertEqual([(p['page'], p['page_image']) for p in declaration.decree['located']], [(1, True)])

    def test_a_transcription_with_no_decreta_is_not_cut(self):
        # The transcription stops before the dispositive OCR located: nothing is read from it, and the cause says so.
        declaration, _, _ = self.read(DECREE.format(NAMING_NONE), DECREE.format(NAMING_NONE).split('Decreta:')[0])
        self.assertTrue(declaration.decree['read'].startswith(
            'not read: the transcription of page 1 holds the act titled as the layer\'s object but no "Decreta"'))
        self.assertNotIn('reading', declaration.decree)
        self.assertEqual(declaration.reading, 'not read whole')   # the layer's motivation, cut at its field length

    def test_a_scheda_page_image_is_read_from_its_transcription(self):
        page = ('A) ELEMENTI IDENTIFICATIVI\n"riconoscimento"\n(del valore dell\'area)\n{} (tratto dal D.M. 12-03-1971)\n'
                'art. 134, c.1 lett. c)\nNO')
        # Tesseract's words name a tree; the transcription's name none, and they are what is read.
        pdf = page_image_pdf(page.format(NAMING_NONE.capitalize()))
        digest = put_bytes(self.store, pdf)
        held_ocr(self.store, digest, 0, page.format(NAMING.capitalize()))
        request = held_transcription(self.store, digest, 0, page.format(NAMING_NONE.capitalize()))
        read = I._scheda_reading(self.store, {'sha256': digest}, 'ZONA IN COMUNE DI FIXTURIA')
        self.assertEqual(read['scheda_reading'], 'area')
        self.assertIn('ricco di uliveti e macchia', read['scheda_motivation'])
        self.assertEqual(read['scheda_transcriptions'][0]['request_sha256'], request)
        self.assertTrue(read['scheda_read'].startswith('read from the vision transcription of page 1 (vision '))


@unittest.skipUnless(I.ocr_engine(), 'Tesseract with its Italian model is not installed here (CI does not install it)')
class OcrRoute(unittest.TestCase):
    """A page image is located by OCR and, until its transcription is held, read from the OCR'd words, naming that; the
    expected answers are the fixture's own printed words."""

    def setUp(self):
        import tempfile
        self.directory = tempfile.TemporaryDirectory()
        self.store, self.root = Path(self.directory.name) / 'store', Path(self.directory.name) / 'root'

    def tearDown(self):
        self.directory.cleanup()

    def test_a_page_image_decree_naming_a_tree_gives_status_and_one_naming_none_reads_area(self):
        import pymupdf
        naming = page_image_pdf(DECREE.format(NAMING))
        self.assertEqual(pymupdf.open(stream=naming)[0].get_text(), '')   # no text layer
        declaration, state = fixture_declaration(self.store, self.root, naming)
        self.assertEqual((declaration.reading, declaration.genus), ('names a tree', 'Quercus'))
        self.assertTrue(declaration.decree['read'].startswith('read by OCR, page 1 (OCR: Tesseract'))
        self.assertTrue(declaration.decree['read'].endswith('the vision transcription of page 1 is not yet held: the '
                                                            "words read are Tesseract's"))
        record = I.declared_plants([declaration])[0]
        facts = state.facts(record.x, record.y, record.error_m, record.genus, date(2026, 10, 28), own=record)
        self.assertIs(facts[I.DECLARATION]['value'], True)
        # Naming none, the whole decree read by OCR gives an area, citing the OCR'd text and its route, never the decree.
        declaration, state = fixture_declaration(self.store, self.root, page_image_pdf(DECREE.format(NAMING_NONE)))
        self.assertEqual(declaration.reading, 'area')
        self.assertTrue(declaration.cite.startswith("the OCR'd text names no tree, row or group (OCR: Tesseract "))
        self.assertNotIn("decree's text", declaration.cite)
        facts = state.facts(50.0, 50.0, 7.4, 'Olea', date(2026, 10, 28))
        self.assertEqual((facts[I.DECLARATION]['value'], 'PAE9001' in facts[I.DECLARATION]['cause']), (False, True))

    def test_an_ocr_reading_naming_none_never_overrules_a_text_naming_a_tree(self):
        layer = 'Nella zona insiste un esemplare di quercia vallonea, con circonferenza del tronco di m. 2,50.'
        declaration, _ = fixture_declaration(self.store, self.root, page_image_pdf(DECREE.format(NAMING_NONE)), layer)
        self.assertEqual((declaration.reading, declaration.decree['reading']), ('names a tree', 'area'))

    def test_a_scheda_page_image_is_read_by_ocr_between_its_heading_and_art_134(self):
        from cordon_d.store import put_bytes
        scheda = page_image_pdf('A) ELEMENTI IDENTIFICATIVI\n"riconoscimento"\n(del valore dell\'area)\n'
                                f'{NAMING.capitalize()} (tratto dal D.M. 12-03-1971)\nart. 134, c.1 lett. c)\nNO')
        read = I._scheda_reading(self.store, {'sha256': put_bytes(self.store, scheda)}, 'ZONA IN COMUNE DI FIXTURIA')
        self.assertTrue(read['scheda_read'].startswith('read by OCR, page 1'))
        self.assertEqual((read['scheda_reading'], read['scheda_genus']), ('names a tree', 'Quercus'))
        self.assertIn('circonferenza del tronco di metri 4,10', read['scheda_motivation'])


def instruments_held():
    try:
        national = json.loads((ROOT / I.SOURCES / 'national-list.json').read_text())
        declared = json.loads((ROOT / I.SOURCES / 'declarations.json').read_text())
    except OSError:
        return False
    digests = [d['sha256'] for d in national['documents'] + national['pages'] + national['notices'] if d.get('sha256')]
    digests += [p['sha256'] for v in declared['versions'] for p in v['pages'] if p.get('sha256')]
    digests += [d['sha256'] for d in declared.get('decrees', []) + declared.get('schede', {}).get('schede', [])
                if d.get('sha256')]
    return all(blob_path(STORE, d).exists() for d in digests)


@unittest.skipUnless(instruments_held(), 'the national list or the PPTR layer captures are not in this store')
class HeldInstruments(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.entries, cls.decrees, cls.problems = I.list_entries(STORE)
        cls.by = {e.scheda: e for e in cls.entries}
        cls.declared, cls.versions, cls.declaration_problems = I.declarations(STORE)
        cls.codes = {d.code: d for d in cls.declared}

    def test_the_sheet_and_every_decree_annex_agree(self):
        # The Puglia sheet of 24/7/2026: 282 rows listed, 7 on its Eliminazioni sheet; every row is listed by one
        # decree's annex A, every deleted row by one annex B.
        self.assertEqual((len(self.entries), sum(e.sheet == 'deleted' for e in self.entries)), (289, 7))
        self.assertEqual(self.problems, [])
        self.assertTrue(all(e.listed_by for e in self.entries))
        self.assertEqual({e.scheda: e.deleted_by.number for e in self.entries if e.deleted_by},
                         {'01/E038/BA/16': '0579238', '02/E038/BA/16': '330598', '04/F631/FG/16': '0205016',
                          '08/F631/FG/16': '757', '01/G604/FG/16': '330598', '02/M132/FG/16': '330598',
                          '01/I549/LE/16': '330598'})

    def test_an_id_a_correction_changed_keeps_its_listing_decree(self):
        # DD 0205016's annex A prints 01/C514/FG/16 (Cerignola); DD 330598's annex C prints the same tree as
        # 01/I962/FG/16 (Stornara), with the same coordinates; DD 5450 prints Monte Sant'Angelo's code as F361.
        self.assertEqual(self.by['01/I962/FG/16'].listed_by.number, '0205016')
        self.assertEqual(self.by['01/I962/FG/16'].corrected_by[0].number, '330598')
        self.assertEqual(self.by['05/F631/FG/16'].listed_by.number, '5450')

    def test_each_decree_carries_its_own_date_and_its_gazette_date(self):
        by = {d.number: d for d in self.decrees}
        self.assertEqual((by['5450'].adopted, by['5450'].published), (date(2017, 12, 19), date(2018, 2, 12)))
        # The G.U. titles DD 0490928 "DECRETO 12 settembre 2023"; MASAF names it by its protocol of 18/09/2023.
        self.assertEqual((by['0490928'].adopted, by['0490928'].protocol), (date(2023, 9, 12), date(2023, 9, 18)))
        self.assertEqual((by['0364243'].adopted, by['0364243'].published), (date(2026, 7, 24), date(2026, 8, 7)))
        self.assertEqual(len(by['0364243'].sections['A']), 30)

    def test_a_deleted_entry_reads_false_after_its_deleting_decree(self):
        gone = self.by['01/I549/LE/16']   # Scorrano, deleted by DD 330598 (G.U. 5 August 2022)
        self.assertIs(I.in_force(gone, date(2022, 7, 1))[0], True)
        self.assertIs(I.in_force(gone, date(2022, 9, 1))[0], False)

    def test_the_declarations_and_their_readings(self):
        self.assertEqual(len(self.declared), 156)
        self.assertEqual((self.codes['PAE0156'].reading, self.codes['PAE0156'].genus), ('names a tree', 'Quercus'))
        for code in ('PAE0011', 'PAE0058', 'PAE0061'):   # Bosco Curto Petrizzi, Villa Frisari, Bosco Episcopo
            self.assertEqual(self.codes[code].reading, 'area', code)
        self.assertEqual(round(self.codes['PAE0156'].area_m2), 744)

    def test_a_cut_motivation_is_read_whole_from_the_scheda_or_its_decree(self):
        # PAE0081's layer motivation stops at the field; its scheda prints the D.M. of 26-03-1970 whole, ending
        # "un insieme di cose immobili avente valore estetico e tradizionale."
        ugento = self.codes['PAE0081']
        self.assertEqual((ugento.reading, ugento.decree['scheda_read']), ('area', 'read from the text layer'))
        self.assertTrue(ugento.decree['scheda_motivation'].endswith('valore estetico e tradizionale.'))
        unread = sorted(d.code for d in self.declared if d.reading == 'not read whole')
        if I.ocr_engine() is None:   # their schede's identification pages and their decrees are page images
            self.assertEqual(unread, ['PAE0016', 'PAE0017', 'PAE0033', 'PAE0049'])
            return
        # Each scheda's identification page (its third page) is located by OCR. PAE0016's is read from its vision
        # transcription (the slice); the others, until theirs are held, from the OCR'd words, naming that. The words
        # below, read by eye from the rendered page, are in each motivation, and none names a tree, a row or a group.
        for code, words in (('PAE0016', 'variamente coltivato ad olivi, mandorli e frutteti e con'),
                            ('PAE0017', 'come quelle di Lamaforca, Santa Lucia, Pilone, Rosa Marina, che'),
                            ('PAE0033', 'scarsa vegetazione di lecci, proni, melograni, querce spinose,'),
                            ('PAE0049', 'lungo il tratto che da Castro Marina va fino alla Grotta Romanelli')):
            with self.subTest(code=code):
                held = self.codes[code]
                self.assertEqual(held.decree['scheda_located']['page'], 3)
                self.assertTrue(held.decree['scheda_read'].startswith(
                    'read from the vision transcription of page 3 (vision transcription by ' if code == 'PAE0016' else
                    'read by OCR, page 3 (OCR: Tesseract'))
                self.assertIn(words, held.decree['scheda_motivation'])
                self.assertEqual((held.decree['scheda_reading'], held.reading), ('area', 'area'))
        self.assertEqual(unread, [])

    def test_a_page_image_decree_is_located_by_ocr_and_read_from_its_transcription(self):
        if I.ocr_engine() is None:
            self.skipTest('Tesseract with its Italian model is not installed here')
        # G.U. n. 265 of 6 October 1975 prints PAE0017's D.M. of 4 March 1975 on its 12th and 13th pages (pp.
        # 7020-7021), page images; its motivation, read by eye from them, names the coast and its beaches.
        ostuni = self.codes['PAE0017']
        self.assertEqual([(p['page'], p['page_image']) for p in ostuni.decree['located']], [(12, True), (13, True)])
        self.assertEqual([t['page'] for t in ostuni.decree['transcriptions']], [12, 13])
        self.assertTrue(ostuni.decree['read'].startswith(f'read from the vision transcription of page 12, 13 (vision '
                                                         f'transcription by {I.TRANSCRIPTION_MODEL}: page 12, request '))
        self.assertTrue(ostuni.decree['decree_act'][0].startswith('DECRETO MINISTERIALE 4 marzo 1975. Dichiarazione di '
                                                                   'notevole interesse pubblico di alcune zone in comune '
                                                                   'di Ostuni.'))
        self.assertIn('per le sue zone litorali, come quelle di Lamaforca, Santa Lucia, Pilone, Rosa Marina',
                      ostuni.decree['decree_text'][0])
        self.assertEqual(ostuni.decree['reading'], 'area')
        self.assertTrue(ostuni.cite.startswith('the transcribed text names no tree, row or group (vision transcription'))
        # A decree whose pages are not transcribed keeps the OCR'd words' reading, naming that (G.U. n. 30/1986, S.O. 5).
        bari = self.codes['PAE0115'].decree
        self.assertTrue(bari['read'].startswith('read by OCR, page '))
        self.assertTrue(bari['read'].endswith("is not yet held: the words read are Tesseract's"))
        # The issue held for PAE0064 (Nardo', G.U. n. 240 of 15-10-1952) prints no decree naming the comune.
        self.assertIn("its OCR'd pages hold no decree of notable public interest titled as the layer's object",
                      self.codes['PAE0064'].decree['read'])

    def test_a_decree_is_the_act_its_object_and_date_title_in_its_issue_or_a_supplement(self):
        if I.ocr_engine() is None:
            self.skipTest('Tesseract with its Italian model is not installed here')
        # PAE0042's layer prints the comune RACALE and the object "... TERRITORIO COMUNALE DI ALLISTE"; G.U. n. 132 of
        # 29-5-1970 prints two decrees of 26 March 1970, Ugento's and Alliste's: the object's is read.
        self.assertIn('territorio comumale di Alliste', self.codes['PAE0042'].decree['decree_act'][0])
        # The 57 decrees of 1 August 1985 are printed in S.O. n. 5 to G.U. n. 30 of 6-2-1986, whose index the issue's
        # own G.U. page lists; the issue itself prints only their titles.
        bari = self.codes['PAE0115'].decree
        self.assertEqual(bari['read_in'], 'https://www.gazzettaufficiale.it/eli/gu/1986/02/06/30/so/5/sg/pdf')
        self.assertIn('territorio delle Lame ad ovest e a sud-est di Bari', bari['decree_act'][0])
        # Its dispositive is OCR'd "Dccreta:"; its preamble ends there, before the delimitation it decrees.
        self.assertIn('così delimitato', bari['decree_text'][0])
        self.assertNotIn('1) Il territorio delle Lame', bari['decree_text'][0])

    def test_a_decree_with_a_text_layer_is_read_from_it(self):
        # PAE0158, the 2024 declaration of the Tiati - Teanum Apulum - Civitate context (G.U. n. 26, 1-2-2025).
        self.assertEqual(self.codes['PAE0158'].decree['read'], 'read from the text layer')
        self.assertEqual(self.codes['PAE0158'].reading, 'area')
        # G.U. n. 217 of 15-9-1999 prints in its text layer only the title of PAE0037's decree (Ceglie Messapica): the
        # decree is printed in the issue's S.O. n. 173, held (for PAE0096), page images.
        ceglie = self.codes['PAE0037'].decree
        if I.ocr_engine() is not None:
            self.assertEqual(ceglie['read_in'], 'https://www.gazzettaufficiale.it/eli/gu/1999/09/15/217/so/173/sg/pdf')
            self.assertTrue(ceglie['decree_act'][0].startswith('DECRETO 18 maggio 1999. Dichiarazione di notevole '
                                                               'interesse pubblico del centro storico di Ceglie Messapica'))


def proposals_held():
    try:
        record = json.loads((ROOT / I.SOURCES / 'proposals.json').read_text())
    except OSError:
        return False
    digests = {item['source'] for p in record.get('proposals') or ()
               for item in [p.get(k) for k in ('object', 'motivation', 'proposer_printed', 'plan', 'outcome')]
               + list(p.get('publication') or ()) if isinstance(item, dict) and item.get('source')}
    return instruments_held() and all(blob_path(STORE, d).exists() for d in digests)


@unittest.skipUnless(proposals_held(), 'the proposals or the sources they cite are not in this store')
class HeldProposals(unittest.TestCase):
    """The held proposals, read by the ordinary reader; each expected value is read from the source it cites."""

    @classmethod
    def setUpClass(cls):
        declared, _, _ = I.declarations(STORE)
        cls.proposed, cls.routes, cls.problems = I.proposals(STORE, declared=declared)
        cls.by = {p.code.split(':')[0].split(' (')[0]: p for p in cls.proposed}

    def test_every_printed_field_is_printed_by_the_source_it_cites(self):
        self.assertEqual(self.problems, [])
        self.assertEqual(sorted(self.by), ['Bari', 'Herdonia, Ausculum e Alta Valle del Carapelle', 'Ostuni',
                                           'Tiati - Teanum Apulum - Civitate e Bassa Valle del Fortore'])

    def test_each_held_proposal_protects_an_area(self):
        # Ostuni (DGR 1997/2000): the strip below the town, for its secular olives as the zone's character; Bari
        # (DD 425/2012): the central area, its object alone held; Tiati and Herdonia: contexts under Art. 136(1)(c)-(d).
        self.assertEqual({k: p.reading for k, p in self.by.items()}, dict.fromkeys(self.by, 'area'))
        fact = I.Instruments([], [], I.list_bound([]), [], [], self.proposed, self.routes).facts(
            0.0, 0.0, 7.4, 'Olea', date(2026, 10, 28))[I.PROPOSAL]
        self.assertIs(fact['value'], False)

    def test_dates_are_read_as_the_sources_print_them(self):
        # G.U. n. 26 of 1-2-2025: the albi of Casalvecchio di Puglia and San Paolo di Civitate from 11 December 2023,
        # the last to close Casalnuovo Monterotaro's on 26 March 2024; declared as PAE0158.
        tiati = self.by['Tiati - Teanum Apulum - Civitate e Bassa Valle del Fortore']
        self.assertEqual((tiati.proposer, tiati.first_publication()), ('ministry', date(2023, 12, 11)))
        self.assertEqual(max(e for _, e, _ in tiati.periods), date(2024, 3, 26))
        self.assertEqual(tiati.outcome['declaration'], 'PAE0158')
        # The other three print an ordered publication and no day of it.
        for name in ('Ostuni', 'Bari', 'Herdonia, Ausculum e Alta Valle del Carapelle'):
            self.assertIsNone(self.by[name].first_publication())
            self.assertIn('publication: no held source prints its days', self.by[name].causes)


if __name__ == '__main__':
    unittest.main()
