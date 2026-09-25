"""Row 9, protected status, read at C's consumers.

`TheRecordAsPrinted` runs everywhere: the surveyor's notes of held plants, copied verbatim from the monitoring
views, read by D and carried through PR #32's rows. `HeldSources` runs the ordinary reader over this checkout's
store (register capture, list acts, removal orders, monitoring stream) and skips where those bytes are not held.
Expected answers come from reading the layer, the acts and the notes, not from the reader.
"""
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import unittest

import numpy

from cordon_c.bindings import leaves, listing_facts, trunk_diameter_facts
from cordon_c.core import Snapshot, evaluate
from cordon_d import protection
from cordon_d.protection import MonitoringRecord, characteristics_finding, measurements, read_note
from cordon_d.store import blob_path, store_root

ROOT = Path(__file__).resolve().parents[2]
STORE = store_root(ROOT)
DECISION = date(2026, 9, 22)
REACH = DECISION.replace(year=DECISION.year - 4)
FINDING = ("the plant's official monitoring record finds the monumental characteristics of L.R. 14/2007 Article 2: "
           "its MONUMENTALE_ARIF flag, or the surveyor's written finding that the plant has monumental characteristics")
PIANA = 'PUG-LR4-2017:Art.8(7bis):infected-piana-alternative-boundary'
HOLD = 'REG-PUGLIA-U181-DIR-2023-00045:case-delta:pending-monumental-recognition-hold'
DIAMETER = 'PUG-LR14-2007:Art.2(1)(a):trunk-diameter-criterion'
LISTED = 'PUG-LR14-2007:Art.5(3):definitive-listing'
PENDING = 'PUG-LR14-2007:Art.5(2):provisional-listing-pending-recognition'
VIEW = 'Piante infette-Monitoraggio 2025 sub. pauca'  # prints both fields


def record(*notes, flag=None, view=VIEW):
    readings = tuple(read_note(n) for n in notes)
    return MonitoringRecord((('ref', 'day'),), ((view, flag),) if flag else (), () if flag else (view,), (),
                            readings, (), tuple(m for r in readings for m in measurements(r.note)))


class TheRecordAsPrinted(unittest.TestCase):
    """Held notes, verbatim, through D's reading and PR #32's rows."""

    @classmethod
    def setUpClass(cls):
        cls.s = Snapshot.load(ROOT)

    def conjunct(self, rec, identity=PIANA, at=date(2025, 11, 1)):
        """The row's truth with every other conjunct held, so it is the characteristics conjunct's."""
        row = self.s.version(identity, at)
        vid = row['provision_version_id']
        facts = {(vid, p): True for p in leaves(row['condition_ast']) if p != FINDING}
        finding = characteristics_finding(rec)
        facts[(vid, FINDING)] = finding.truth if finding.truth is not None else None
        if finding.truth is None:
            del facts[(vid, FINDING)]
        inputs = protection.diameter_inputs(rec)
        if inputs:
            facts |= trunk_diameter_facts(self.s, at, **inputs[0])
        return evaluate(self.s, identity, at, facts).truth, (
            evaluate(self.s, DIAMETER, at, trunk_diameter_facts(self.s, at, **inputs[0])).effect if inputs else 'none')

    def test_held_wordings_read_states_negation_of_the_tag_does_not_negate(self):
        for note in ('sintomi sospetti. pianta monumentale censita targhetta n. 0107007',
                     'ulivo con caratteristiche di monumentalita per caratteristiche morfologiche e diametro tronco '
                     'superiore a 130 cm. non censito',
                     'targhetta non presente, con caratteristiche monumentale',
                     'caratteristiche monumentali diametro  cm 96 circa',
                     "pianta non cartellinata con caratteristiche di monumentalita'' dim. 1.1"):
            with self.subTest(note=note):
                reading = read_note(note)
                self.assertEqual(reading.reading, 'states')
                self.assertEqual(reading.note, note)  # verbatim
        for note, cause in (('nella frazione dei 50 metri compresi nelle sottomaglia non sono presenti monumentali',
                             'negated'),
                            ('codice monumentale n.  0158021', 'names the term without stating it of the plant')):
            self.assertEqual((read_note(note).reading, read_note(note).cause), ('unclear', cause))
        for note in ('diametro 90 cm ad un metro e mezzo di altezza', 'codice regione puglia 0158595'):
            self.assertEqual(read_note(note).reading, 'does not')

    def test_measurements_as_printed_with_numbers_read_from_the_words(self):
        m, = measurements('diametro 90 cm ad un metro e mezzo di altezza')  # 1901545
        self.assertEqual((m.quantity, m.value, m.unit, m.height), ('diametro', '90', 'cm', 'ad un metro e mezzo di altezza'))
        self.assertEqual((m.diameter_cm, m.measured_height_cm), (Decimal(90), Decimal(150)))
        m, = measurements("pianta non cartellinata con caratteristiche di monumentalita'' dim. 1.1")  # 1474431
        self.assertEqual((m.quantity, m.value, m.unit, m.diameter_cm), ('dim.', '1.1', 'no unit printed', None))
        self.assertIn('no unit printed', m.cause)
        m, = measurements('ulivo con caratteristiche di monumentalita per caratteristiche morfologiche e diametro '
                          'tronco superiore a 130 cm. non censito')  # 1461872
        self.assertEqual((m.quantity, m.qualifier, m.value, m.unit, m.height, m.diameter_cm, m.measured_height_cm),
                         ('diametro', 'superiore a', '130', 'cm', 'no height printed', Decimal(130), None))
        m, = measurements('caratteristiche monumentali diametro  cm 96 circa')  # order plant 0e92c74d4485, #2550
        self.assertEqual((m.qualifier, m.value, m.unit, m.height, m.diameter_cm), ('circa', '96', 'cm', 'no height printed', Decimal(96)))

    def test_a_stated_height_is_never_dropped(self):
        # A height whose number cannot be read withholds the diameter rather than letting C read 130 cm.
        m, = measurements('diametro 120 cm altezza di rilievo circa 80')
        self.assertEqual((m.height, m.diameter_cm), ('altezza di rilievo circa 80', None))
        self.assertIn('its number is not read', m.cause)
        for note, height in (('diametro 110 cm ad un metro e mezzo di altezza', Decimal(150)),
                             ('diametro 120 cm a 1,30 m da terra', Decimal(130))):
            m, = measurements(note)
            self.assertEqual(m.measured_height_cm, height, note)

    def test_named_plants_at_the_characteristics_conjunct(self):
        # 1901545: blank flag, "does not", 90 cm at 150 cm: Art. 2(1)(a) unknown, so the conjunct is unknown.
        self.assertEqual(self.conjunct(record('diametro 90 cm ad un metro e mezzo di altezza')), (None, None))
        # 1474431: "states" decides; its "dim. 1.1" (no unit) leaves Art. 2(1)(a) unknown.
        self.assertEqual(self.conjunct(record("pianta non cartellinata con caratteristiche di monumentalita'' dim. 1.1")),
                         (True, None))
        # 1892689: flag printed "1", no note.
        self.assertEqual(self.conjunct(record(flag='1')), (True, 'none'))
        # 1461872: "states", and more than 130 cm with no height: Art. 2(1)(a) met.
        self.assertEqual(self.conjunct(record('ulivo con caratteristiche di monumentalita per caratteristiche '
                                              'morfologiche e diametro tronco superiore a 130 cm. non censito')),
                         (True, 'ARTICLE_2_1_A_CRITERION_MET'))
        # A blank flag and a note that states nothing: the finding is false, and with no recorded diameter C leaves
        # the Art. 2(1)(a) branch, and so the conjunct, unknown.
        self.assertIs(characteristics_finding(record('codice regione puglia 0158595')).truth, False)
        self.assertEqual(self.conjunct(record('codice regione puglia 0158595')), (None, 'none'))
        # "unclear" leaves the finding unread.
        self.assertEqual(self.conjunct(record('codice monumentale n.  0158021')), (None, 'none'))
        # The DDS 45/2023 hold reads the same field for a negative olive.
        self.assertEqual(self.conjunct(record(flag='Si'), identity=HOLD)[0] is not False, True)

    def test_the_flag_is_kept_as_printed(self):
        self.assertEqual(record(flag='Si').flag, 'Si')
        self.assertEqual(record(flag='1').flag, '1')
        self.assertEqual(record().flag, 'blank')
        unprinted = MonitoringRecord((), (), (), ('CAMP_2014_2015.xlsx',), (), ('CAMP_2014_2015.xlsx',), ())
        self.assertEqual(unprinted.flag, 'not printed')
        self.assertIsNone(characteristics_finding(unprinted).truth)


def held():
    try:
        register = json.loads((ROOT / protection.SOURCES / 'register.json').read_text())
        acts = json.loads((ROOT / protection.SOURCES / 'acts.json').read_text())
        releases = json.loads((ROOT / 'corpus/sources/monitoring/campaign/releases.json').read_text())
    except OSError:
        return False
    digests = [p['sha256'] for layer in register['layers'] for p in layer['pages']]
    digests += [a['sha256'] for a in acts if a.get('sha256')] + [r['sha256'] for r in releases if 'sha256' in r]
    return all(blob_path(STORE, d).exists() for d in digests)


@unittest.skipUnless(held(), 'the register capture, the list acts or the monitoring releases are not in this store')
class HeldSources(unittest.TestCase):
    """The ordinary reader over every held source; nothing is chosen by a C result."""

    @classmethod
    def setUpClass(cls):
        cls.s = Snapshot.load(ROOT)
        cls.result = protection.read(STORE, DECISION, REACH)
        cls.plants = {p.plant: (p, c) for p, c in cls.result['plants']}
        cls.by_ref = {}
        for p, c in cls.result['plants']:
            for ref in p.coincides:
                cls.by_ref.setdefault(ref, (p, c))

    def status(self, entry, at):
        chain = self.result['chains'][entry]
        facts = listing_facts(self.s, at, **protection.listing_inputs(chain))
        return evaluate(self.s, LISTED, at, facts).effect, evaluate(self.s, PENDING, at, facts).effect

    def entry_labelled(self, label, survey=None):
        return next(o for o, e in self.result['entries'].items()
                    if e.label == label and e.layer == 'listed' and (survey is None or survey(e)))

    def test_a_dgr_1993_2022_tree_is_pending_then_listed(self):
        entry = self.entry_labelled('DGR 1993/2022')
        chain = self.result['chains'][entry]
        self.assertEqual((chain.provisional.act, chain.provisional.bulletin), ('DGR 1193/2021', 'n. 104 del 10-8-2021'))
        self.assertEqual((chain.definitive.act, chain.definitive.bulletin), ('DGR 1993/2022', 'n. 18 del 21-2-2023'))
        self.assertEqual(self.status(entry, date(2022, 10, 1)), ('TREE_NOT_LISTED', 'RECOGNITION_DECISION_PENDING'))
        self.assertEqual(self.status(entry, date(2023, 2, 20)), ('TREE_NOT_LISTED', 'RECOGNITION_DECISION_PENDING'))
        self.assertEqual(self.status(entry, date(2023, 2, 21)), ('TREE_LISTED', 'NO_PENDING_DECISION_FROM_THE_LIST'))

    def test_a_dgr_1491_2020_tree_and_a_dgr_345_2011_tree_show_both_acts(self):
        chain = self.result['chains'][self.entry_labelled('DGR 1491/2020')]
        self.assertIn(chain.provisional.act, ('DGR 501/2016', 'DGR 2225/2017'))
        self.assertEqual((chain.definitive.act, chain.definitive.bulletin), ('DGR 1491/2020', 'n. 133 del 22-9-2020'))
        chain = self.result['chains'][self.entry_labelled('DGR 1358/2012', lambda e: e.survey_date and e.survey_date.year == 2009)]
        self.assertEqual((chain.provisional.act, chain.provisional.published), ('DGR 345/2011', date(2011, 3, 22)))
        self.assertEqual((chain.definitive.act, chain.definitive.published), ('DGR 1358/2012', date(2012, 7, 31)))
        # CARSEGNMOT names the provisional act for the 2011-12 census, the definitive one for the 2009 survey.
        chain = self.result['chains'][self.entry_labelled('DGR 1358/2012', lambda e: e.survey_date and e.survey_date.year == 2012)]
        self.assertEqual((chain.provisional.act, chain.definitive.act), ('DGR 1358/2012', 'DGR 357/2013'))

    def test_the_2013_2015_acts_carry_the_burp_dates_their_own_pages_print(self):
        # Each act's own BURP pages, reached through BURP's act lookup, print its bulletin.
        printed = {'DGR 1008/2013': ('n. 86 del 25-06-2013', 1204), 'DGR 1417/2013': ('n. 117 del 03-09-2013', 1321),
                   'DGR 1577/2013': ('n. 128 del 30-09-2013', 163), 'DGR 2227/2013': ('n. 165 del 16-12-2013', 1990),
                   'DGR 978/2014': ('n. 80 del 23-06-2014', 200), 'DGR 143/2015': ('n. 29 del 25-02-2015', 1175),
                   'DGR 609/2015': ('n. 56 del 22-04-2015', 126)}
        acts = self.result['acts']
        self.assertEqual({name: (acts[name].bulletin, acts[name].provisional) for name in printed}, printed)
        entry = self.entry_labelled('DGR 1008/2013')
        chain = self.result['chains'][entry]
        self.assertEqual((chain.provisional.published, chain.definitive.act, chain.definitive.published, chain.complete),
                         (date(2013, 6, 25), 'DGR 501/2016', date(2016, 5, 6), True))
        self.assertEqual(self.status(entry, date(2016, 5, 5)), ('TREE_NOT_LISTED', 'RECOGNITION_DECISION_PENDING'))
        self.assertEqual(self.status(entry, date(2016, 5, 6)), ('TREE_LISTED', 'NO_PENDING_DECISION_FROM_THE_LIST'))
        held = [c for o, c in self.result['chains'].items() if self.result['entries'][o].layer != 'deleted']
        self.assertEqual(sum(1 for c in held if not c.complete), 0)

    def test_the_cent_oli_med_trees_take_dgr_1358_2012_then_dgr_357_2013(self):
        # DGR 1358/2012's recitals: SIT srl's partial list of 127,719 and "ulteriori 467 ulivi monumentali" of LIFE+
        # Cent.Oli.Med make up its provisional list; DGR 357/2013 approves that list definitively.
        undated = [o for o, e in self.result['entries'].items()
                   if e.layer == 'listed' and e.label == 'DGR 1358/2012' and e.survey == 'survey date not recorded']
        self.assertEqual(len(undated), 467)
        self.assertEqual(self.result['acts']['DGR 1358/2012'].batches, (127719, 467))
        chains = {(c.provisional.act, c.provisional.published, c.definitive.act, c.definitive.published, c.complete)
                  for c in (self.result['chains'][o] for o in undated)}
        self.assertEqual(chains, {('DGR 1358/2012', date(2012, 7, 31), 'DGR 357/2013', date(2013, 3, 27), True)})

    def test_batch_bounds_come_from_monitoring_residuals_and_recompute_by_hand(self):
        fixes, bounds = self.result['fixes'], self.result['bounds']
        dropped = [(f.observation, f.entry) for f in fixes if f.dropped]
        self.assertEqual(dropped, [('1584865', '221931')])
        monopoli = {'1650896', '1650922', '1650984', '1651071', '1651111', '1651129', '1651143'}
        kept = {f.observation: f for f in fixes if not f.dropped}
        self.assertTrue(monopoli <= set(kept))
        self.assertTrue(all(kept[o].codes and kept[o].codes[0][1] == 'no card in the comune' for o in monopoli))
        batch = next(b for b in bounds if b.startswith('DGR 1993/2022'))
        own = [f.distance_m + f.observation_error_m for f in fixes if not f.dropped and f.batch == batch]
        self.assertGreaterEqual(len(own), protection.MIN_FIXES)
        self.assertEqual(bounds[batch].error_m, round(float(numpy.percentile(own, 95)), 2))
        self.assertEqual(bounds[batch].applies, batch)
        wide = [f.distance_m + f.observation_error_m for f in fixes if not f.dropped]
        small = [b for b in bounds.values() if b.applies.startswith('register-wide')]
        self.assertTrue(small and all(b.error_m == round(float(numpy.percentile(wide, 95)), 2) for b in small))
        self.assertTrue(all('monitoring residuals' in b.method and 'parcel' not in b.method for b in bounds.values()))
        census = [b for b in bounds.values() if b.check]
        self.assertTrue(census and all('exceeded by' in b.check or 'within' in b.check for b in census))
        # The tolerance is read from the held capitolato d'oneri, Art. 3 point 4, not written as a figure.
        metres, quotation, _ = protection.contract_terms(STORE)
        self.assertEqual(metres, 1.0)
        self.assertIn('ricevitore satellitare GPS differenziale', quotation)
        self.assertTrue(all(quotation in b.check and '1.00 m plus' in b.check for b in census))

    def test_the_printed_parcel_screen_lists_every_entry_outside_it(self):
        import shapely
        screens = self.result['parcel_screen']
        held = [e for e in self.result['entries'].values() if e.layer in ('listed', 'provisional')]
        self.assertEqual(len(held), 341428 + 569)  # layer 0's ids overlap layer 1's; both layers are kept
        self.assertEqual(sorted(s.entry for s in screens), sorted(e.oid for e in held))
        self.assertTrue(all(s.distance_m is not None or s.cause for s in screens))
        counts = protection.screen_counts(screens)
        self.assertEqual(counts['inside'] + counts['outside'] + sum(counts['not_screened'].values()), len(held))
        listed = protection.rows(self.result)['gross_error_screen']
        self.assertEqual(len(listed['outside']), counts['outside'])
        self.assertEqual({r['entry'] for r in listed['outside']}, {s.entry for s in screens if s.distance_m})
        # By hand, from the captured Catasto page: entry 255604 (an AppOLEA report printed on OSTUNI 29/8).
        entry = self.result['entries']['255604']
        record = json.loads((ROOT / protection.SOURCES / protection.PARCELS).read_text())
        rings = [ring for page in record['pages'] if "'G187'" in page['where']
                 for f in json.loads(blob_path(STORE, page['sha256']).read_bytes())['features']
                 if (f['attributes']['FOGLIO'], f['attributes']['NUMERO']) == ('29', '8')
                 for ring in f['geometry']['rings']]
        by_hand = min(shapely.Point(entry.x, entry.y).distance(shapely.Polygon(r)) for r in rings)
        screen = next(s for s in screens if s.entry == '255604')
        self.assertAlmostEqual(screen.distance_m, by_hand, places=1)
        self.assertGreater(screen.distance_m, 1000)
        # The screen enters no bound.
        self.assertTrue(all('parcel' not in b.method for b in self.result['bounds'].values()))

    def test_survey_date_not_recorded_takes_the_register_wide_bound(self):
        entry = self.entry_labelled('DGR 1491/2020', lambda e: e.survey == 'survey date not recorded')
        batch = self.result['batches'][entry]
        self.assertIn('survey date not recorded', batch)
        self.assertTrue(self.result['bounds'][batch].applies.startswith('register-wide'))

    def test_identity_follows_d_and_the_note_code_rule(self):
        plant, cand = self.plants['10201272']  # blank flag, 0.94 m from entry 344631
        self.assertEqual(cand.identity, 'unknown')
        self.assertIn('344631', [e for e, _, _ in cand.entries])
        batch = self.result['bounds'][self.result['batches']['344631']]
        self.assertTrue(all(d == round(plant.error_m + batch.error_m, 2) for e, _, d in cand.entries if e == '344631'))
        plant, cand = self.plants['1606667']
        self.assertEqual(cand.identity, '340453')
        self.assertEqual(self.result['entries']['340453'].key, '107007_17_159_072030')
        plant, cand = self.plants['1584865']  # flagged, a neighbour, no record names it
        self.assertEqual(cand.identity, 'unknown')
        causes = {(c.plant, c.code): c.cause for c in self.result['codes']}
        self.assertEqual(causes[('1584865', '0158595')], 'no card in the comune')
        self.assertTrue(any(code == '0158330' and cause.startswith('printed by 3') for (_, code), cause in causes.items()))
        self.assertTrue(any(code == '0010465' and 'cards in the comune' in cause for (_, code), cause in causes.items()))

    def test_named_records_reach_the_conjunct_whatever_the_identity(self):
        cases = {'1892689': ('1', ()), '1901545': ('blank', ('does not',)), '1461872': ('blank', ('states',)),
                 '1474431': ('blank', ('states',)), '1901578': ('blank', ('unclear',)), '1585005': ('Si', ('unclear',))}
        for name, (flag, readings) in cases.items():
            plant, cand = self.plants[name]
            with self.subTest(plant=name):
                self.assertEqual(plant.record.flag, flag)
                self.assertEqual(tuple(n.reading for n in plant.record.notes), readings)
        plant, _ = self.plants['1901545']
        self.assertEqual(protection.diameter_inputs(plant.record), ({'diameter_cm': Decimal(90), 'measured_height_cm': Decimal(150)},))
        plant, _ = self.by_ref['1444810']  # order plant 7f77bcf82edd, #1018
        self.assertEqual([(n.note, n.reading) for n in plant.record.notes],
                         [('targhetta non presente, con caratteristiche monumentale', 'states')])

    def test_negative_olives_in_the_zone_carry_their_record(self):
        negatives = [p for p, _ in self.result['plants'] if p.kind == 'negative olive']
        self.assertTrue(negatives)
        self.assertTrue(all(p.record.flag in ('not printed', 'blank') or p.record.flags for p in negatives))
        self.assertTrue(all(p.record.flag_views_unprinted or p.record.flag_views_blank or p.record.flags for p in negatives))

    def test_counts_at_the_plan_stage_distance(self):
        from scipy.spatial import cKDTree
        entries = [e for e in self.result['entries'].values() if e.x is not None and e.layer != 'deleted']
        tree = cKDTree(numpy.array([[e.x, e.y] for e in entries]))
        group = [p for p, _ in self.result['plants'] if p.kind == 'in-reach positive' and not tree.query_ball_point([p.x, p.y], 8.0)]
        states = [p for p in group if any(n.reading == 'states' for n in p.record.notes)]
        unclear = [p for p in group if any(n.reading == 'unclear' for n in p.record.notes) and p not in states]
        measured = [p for p in group if p.record.measurements]
        self.assertEqual((len(states), len(unclear), len(measured), len(set(map(id, states + measured)))), (317, 2, 13, 318))

    def test_no_article_15_input_and_no_owner_names(self):
        out = json.dumps(protection.rows(self.result), ensure_ascii=False)
        self.assertNotIn('Art. 15', out)
        self.assertNotRegex(out, r'PROPRIETARIO|DIFONZO|LATILLA')


if __name__ == '__main__':
    unittest.main()
