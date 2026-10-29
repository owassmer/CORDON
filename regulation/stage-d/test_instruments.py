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

from cordon_d import instruments as I
from cordon_d.store import blob_path, store_root

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


def held(entries=(), declared=()):
    bound = I.list_bound([])
    return I.Instruments(list(entries), [LISTING, DELETING], bound, list(declared), [{'version': 'v'}])


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

    def test_a_cut_motivation_is_read_whole_from_the_scheda_or_stays_unread(self):
        # PAE0081's layer motivation stops at the field; its scheda prints the D.M. of 26-03-1970 whole, ending
        # "un insieme di cose immobili avente valore estetico e tradizionale."
        ugento = self.codes['PAE0081']
        self.assertEqual((ugento.reading, ugento.decree['scheda_read']), ('area', 'read from the text layer'))
        self.assertTrue(ugento.decree['scheda_motivation'].endswith('valore estetico e tradizionale.'))
        # The four schede whose identification page is an image, and whose decrees are page images.
        self.assertEqual(sorted(d.code for d in self.declared if d.reading == 'not read whole'),
                         ['PAE0016', 'PAE0017', 'PAE0033', 'PAE0049'])

    def test_a_decree_with_a_text_layer_is_read_from_it(self):
        # PAE0158, the 2024 declaration of the Tiati - Teanum Apulum - Civitate context (G.U. n. 26, 1-2-2025).
        self.assertEqual(self.codes['PAE0158'].decree['read'], 'read from the text layer')
        self.assertEqual(self.codes['PAE0158'].reading, 'area')
        # G.U. n. 217 of 15-9-1999 prints in its text layer only the title of PAE0037's decree (Ceglie Messapica).
        self.assertIn('only its title', self.codes['PAE0037'].decree['read'])


if __name__ == '__main__':
    unittest.main()
