"""Row 9, protected status, read at C's consumers.

`TheRecordAsPrinted` runs everywhere: the surveyor's notes of held plants, copied verbatim from the monitoring
views, read by D and carried through PR #32's rows. `HeldSources` runs the ordinary reader over this checkout's
store (register capture, list acts, removal orders, monitoring stream) and skips where those bytes are not held.
Expected answers come from reading the layer, the acts and the notes, not from the reader.
"""
import dataclasses
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

    def test_a_monumental_term_followed_by_a_number_is_read_as_the_note_prints_it(self):
        # Held on order plant d132e9fe6300: the one held reference to another tree does not read "states".
        note = 'fuori buffer monumentale n.0086552. zona contenimento'  # verbatim
        reading = read_note(note)
        self.assertEqual((reading.reading, reading.cause), ('unclear', 'names the term without stating it of the plant'))
        self.assertIsNone(characteristics_finding(record(note)).truth)
        # Held own-tag forms: the plant's own tag after "pianta monumentale" (order plant a9976f5f7efe; positive
        # 1608670, whose number the note-code rule reads as its paired entry 213340) states.
        for note in ('Pianta monumentale n. 0010852', 'pianta monumentale n 0044620'):  # verbatim
            with self.subTest(note=note):
                reading = read_note(note)
                self.assertEqual((reading.reading, reading.cite.lower()), ('states', 'pianta monumentale'))
                self.assertIs(characteristics_finding(record(note)).truth, True)

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

    def test_a_leading_separator_is_read_only_directly_after_the_quantity(self):
        # Order plant b4b95b9f1934's held "dim. ,9": no unit before the value, which is kept as printed.
        m, = measurements("pianta non cartellinata con caratteristiche di monumentalita'' dim. ,9")
        self.assertEqual((m.quantity, m.value, m.unit, m.diameter_cm), ('dim.', ',9', 'no unit printed', None))
        # After a unit, a leading separator is an abbreviation's point, not the value's: 'cm.120' is never 1.20 cm
        # and 'cm.80' never 0.80 cm. No held note has this form; the diameter is not read, so C reads unknown.
        for note in ('diametro cm.120', 'diametro cm.80 a 1,30 m da terra', 'diametro mt.1,20 a 1,30 m da terra'):
            with self.subTest(note=note):
                m, = measurements(note)
                self.assertEqual((m.value, m.diameter_cm), (protection.NOT_READ, None))
                self.assertEqual(protection.diameter_inputs(record(note))[0]['diameter_cm'], None)

    def test_a_diameter_named_without_a_value_is_not_read_not_unprinted(self):
        # No held note names the diameter without a value the reader reads; this is a variant.
        m, = measurements('diametro fusto cm 110')
        self.assertEqual((m.quantity, m.value, m.diameter_cm), ('diametro', protection.NOT_READ, None))
        self.assertTrue(m.cause.startswith(protection.NOT_READ))
        self.assertEqual(protection.diameter_inputs(record('diametro fusto cm 110')),
                         ({'diameter_cm': None, 'measured_height_cm': None},))
        self.assertEqual(measurements('codice regione puglia 0158595'), ())

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


# --- naming records (PR #48) -------------------------------------------------------------------------------------
# Every plant, entry and record here is a FIXTURE (identifiers 92xxxxx and 99xxxx, `fixture: true`) in the shape of a
# real row of PR #30's rows: P1 is negative olive 11200168's (comune None, one candidate entry, d 17.48 m); P2 is
# 11200171's (four candidates, among them P1's); P3 and P4 are the order plants that also hold P1's entry; P5 is
# 10201162's ("not a register tree", an entry 33.98 m away, d 30.55 m); P6 is 10201158's (an entry 38.7 km away);
# P7 and P8 carry one reference at two dates (10600377's); P9 is 1606667's (its note's tag decides its entry). The
# rows are built by PR #30's own functions over the fixture register; the expected identities and rules below are
# written out by hand from the fixture points, not taken from the code under test.

ROME = __import__('zoneinfo').ZoneInfo('Europe/Rome')
CUTOFF = __import__('datetime').datetime(2025, 9, 30, 18, tzinfo=ROME)
GRANT = frozenset({'f' * 64})
P1, P2, P5, P6, P9, Q9 = '9200168', '9200171', '9201162', '9201158', '9206667', '9206668'
P3, P4 = 'feedfeed0003@17.27520121,40.80000000', 'feedfeed0004@17.27503727,40.80000000'
P7, P8, P11, P12 = '9200377@2023-03-07', '9200377@2024-03-07', '9200300', '9200400'
REPEATED = '990202_22_310_072030'


def entry(oid, key, card, comune, x, y, label='DGR 995/2024'):
    return protection.Entry('listed', oid, key, card, label, None, comune, '17', '175', x, y, date(2022, 5, 3), 'e' * 64)


REGISTER = [
    entry('993516', 'UM993771', '993858', 'MONOPOLI', 100000.0, 200015.47, 'DGR 1993/2022'),  # batch bound 10.08 m
    entry('993538', 'UM993538', '993538', 'MONOPOLI', 100000.0, 200034.49),                   # 1.73 m from P2
    entry('993540', 'UM993540', '993540', 'MONOPOLI', 100014.79, 200032.76),                  # 14.79 m from P2
    entry('993818', 'UM993818', '993818', 'MONOPOLI', 99986.18, 200032.76),                   # 13.82 m from P2
    entry('995494', 'UM995994', '13', 'Castellana Grotte ', 110033.98, 200000.0),             # 33.98 m from P5
    entry('992012', '990994_28_68_074012', '0990994', 'OSTUNI', 156049.57, 185899.45),      # 38,709.13 m from P6
    entry('997001', 'UM997001', '997001', 'MONOPOLI', 130005.0, 200000.0),                    # P7 and P8's candidate
    entry('999001', '990101_21_300_072030', '0990101', 'MONOPOLI', 140002.0, 200000.0),     # P9's tag
    entry('999004', '990404_21_301_072030', '0990404', 'MONOPOLI', 140015.0, 200000.0),     # 15 m from P9
    entry('991102', REPEATED, '0990202', 'MONOPOLI', 150005.0, 200000.0),
    entry('991103', REPEATED, '0990303', 'MONOPOLI', 190000.0, 210000.0),
    entry('991201', 'UM991201', '996213', "NARDO'", 170005.0, 200000.0),
    entry('991202', 'UM991202', '996213', 'NARDO`', 180000.0, 210000.0),
    entry('991301', 'UM991301', '991301', 'MONOPOLI', None, None),                             # prints no point
]
# (kind, comune, x, y, notes, observations, coincides_with)
PLANTS = {
    P1: ('negative olive', None, 100000.0, 200000.0, (), [[P1, '2024-02-13']], []),
    P2: ('in-reach positive', 'MONOPOLI', 100000.0, 200032.76, (), [[P2, '2024-02-13']], []),
    P3: ('order plant', 'MONOPOLI', 100010.0, 200015.47, (), [['9100003', '2022-06-17']], ['9100003']),
    P4: ('order plant', 'MONOPOLI', 99990.0, 200015.47, (), [['9100004', '2022-06-17']], ['9100004']),
    P5: ('negative olive', None, 110000.0, 200000.0, (), [[P5, '2023-01-18']], []),
    P6: ('negative olive', None, 120000.0, 200000.0, (), [[P6, '2023-01-18']], []),
    P7: ('in-reach positive', 'MONOPOLI', 130000.0, 200000.0, (), [['9200377', '2023-03-07']], []),
    P8: ('in-reach positive', 'MONOPOLI', 130000.5, 200000.0, (), [['9200377', '2024-03-07']], []),
    P9: ('in-reach positive', 'MONOPOLI', 140000.0, 200000.0,
         ('sintomi assenti. pianta monumentale censita targhetta n. 0990101',), [[P9, '2023-05-02']], []),
    Q9: ('negative olive', None, 140004.0, 200000.0, (), [[Q9, '2023-05-02']], []),
    P11: ('negative olive', None, 150000.0, 200000.0, (), [[P11, '2023-05-02']], []),
    P12: ('negative olive', None, 170000.0, 200000.0, (), [[P12, '2023-05-02']], []),
}
ERROR_M = 7.4


def bound(e):
    from types import SimpleNamespace
    return SimpleNamespace(error_m=10.08 if e.label == 'DGR 1993/2022' else 23.15)


def fixture_rows():
    """PR #30's rows for the fixture plants, from its own note-code rule and candidates."""
    notes = {p: (comune, x, y, n, tuple(map(tuple, obs))) for p, (_, comune, x, y, n, obs, _) in PLANTS.items()}
    codes = protection.note_codes(notes, REGISTER, lambda plant, e: ERROR_M + bound(e).error_m)
    plants = []
    for plant, (kind, comune, x, y, _, observations, coincides) in PLANTS.items():
        named = [c for c in codes if c.plant == plant]
        located = [e for e in REGISTER if e.x is not None]
        cand = protection.candidates(plant, x, y, ERROR_M, located, bound, named)
        plants.append(dict(plant=plant, kind=kind, order=None, coincides_with=coincides, comune=comune,
                           point=dict(x=x, y=y, crs='EPSG:32633', error_m=ERROR_M), observations=observations,
                           codes=[dict(code=c.code, entry=c.entry, cause=c.cause) for c in named],
                           candidates={'not a register tree': True, 'identity': cand.identity, 'rule': cand.rule,
                                       'entries': [dict(entry=e, distance_m=dm, d_m=d) for e, dm, d in cand.entries],
                                       'd': f"the plant's error_m {ERROR_M} m + the entry's batch bound"}))
    return dict(plants=plants, zone_entries=[dict(entry=e.oid, qualification=dict(error_m=bound(e).error_m))
                                             for e in REGISTER])


def naming(name, *groups, source='f' * 64, occurred=date(2025, 8, 20)):
    """A landscape record (a lodging) whose groups print a plant's identifiers."""
    return dict(record=name, kind='landscape-lodging', document=f'FIXTURE protocol {name}', source=source,
                selector=f'fixture:{name}', reading='FIXTURE landscape-lodging: not a fact about any plant',
                plants=[list(g) for g in groups], occurred=occurred.isoformat(), complete=True,
                recipient='Regione Puglia, Sezione Tutela e valorizzazione del paesaggio (FIXTURE)', fixture=True)


def ref(value):
    return dict(sample=value)


def tag(value, comune='Monopoli'):
    return dict(card=value, comune=comune)


class NamingRecords(unittest.TestCase):
    """Row 9 decides an identity from an Osservatorio record that names it (`protection.named_rows`)."""

    @classmethod
    def setUpClass(cls):
        cls.rows = fixture_rows()
        identities = {p['plant']: p['candidates']['identity'] for p in cls.rows['plants']}
        candidates = {p['plant']: [e['entry'] for e in p['candidates']['entries']] for p in cls.rows['plants']}
        # PR #30's rule on the fixture, read from the points: P1 has one candidate, P2 four, P3 and P4 hold P1's;
        # P5 and P6 have none within 30.55 m; P9's note names entry 999001.
        assert candidates[P1] == ['993516'] and sorted(candidates[P2]) == ['993516', '993538', '993540', '993818']
        assert '993516' in candidates[P3] and '993516' in candidates[P4], candidates
        assert identities == {P1: 'unknown', P2: 'unknown', P3: 'unknown', P4: 'unknown', P5: 'not a register tree',
                              P6: 'not a register tree', P7: 'unknown', P8: 'unknown', P9: '999001', Q9: 'unknown',
                              P11: 'unknown', P12: 'unknown'}, identities

    def run_rows(self, *records, grant=GRANT):
        return protection.named_rows(self.rows, REGISTER, list(records), evaluated_at=CUTOFF,
                                     permitted_controlled_sources=grant, zone=ROME)

    def plant(self, out, name):
        return next(p for p in out['plants'] if p['plant'] == name)

    def candidate(self, out, plant, entry):
        return next(e for e in self.plant(out, plant)['candidates']['entries'] if e['entry'] == entry)

    def test_a_record_naming_the_one_candidate_decides_it_and_the_other_plants_keep_it_marked(self):
        out = self.run_rows(naming('n-1', [ref(P1), tag('993858')]))
        p1 = self.plant(out, P1)['candidates']
        self.assertEqual((p1['identity'], p1['rule']), ('993516', 'record n-1 (group 1) prints monitoring reference '
                         f'{P1}, card 993858 (Monopoli), which names entry 993516 at 15.47 m, within d 17.48 m'))
        self.assertEqual(p1['named'], [dict(record='n-1', group=1, printed=f'monitoring reference {P1}, card 993858 '
                                            '(Monopoli)', plants=[P1], entries=['993516'], cause='entry within d',
                                            conflict=None, distance_m=15.47, d_m=17.48, fixture=True)])
        # The entry stays a candidate of every other plant that holds it, marked; their identities do not move.
        for other in (P2, P3, P4):
            with self.subTest(plant=other):
                self.assertEqual(self.plant(out, other)['candidates']['identity'], 'unknown')
                self.assertIn('993516', [e['entry'] for e in self.plant(out, other)['candidates']['entries']])
                self.assertEqual(self.candidate(out, other, '993516')['named_for'], [
                    dict(plants=[P1], record='n-1', group=1, cause='entry within d')])
        self.assertNotIn('named_for', self.candidate(out, P2, '993538'))
        # Nothing else moves.
        for before, after in zip(self.rows['plants'], out['plants']):
            if before['plant'] not in (P1, P2, P3, P4):
                self.assertIs(after, before)
        self.assertEqual([n['record'] for n in out['naming_records']], ['n-1'])

    def test_a_record_naming_one_of_several_candidates_decides_it(self):
        out = self.run_rows(naming('n-1', [tag('993540'), ref(P2)]))
        self.assertEqual(self.plant(out, P2)['candidates']['identity'], '993540')
        self.assertIn('which names entry 993540 at 14.79 m, within d 30.55 m',
                      self.plant(out, P2)['candidates']['rule'])
        # A COD names its entry as a card does.
        out = self.run_rows(naming('n-1', [ref(P2), dict(cod='UM993538')]))
        self.assertEqual(self.plant(out, P2)['candidates']['identity'], '993538')

    def test_an_entry_beyond_d_within_50_m_makes_the_identity_unknown_and_never_decides(self):
        out = self.run_rows(naming('n-1', [ref(P5), tag('13', 'Castellana Grotte')]))
        p5 = self.plant(out, P5)['candidates']
        self.assertEqual((p5['identity'], p5['rule'], p5['entries']), (
            'unknown', 'unknown between entry 995494 and "not a register tree": entry beyond d: record n-1 (group 1) '
            f'prints monitoring reference {P5}, card 13 (Castellana Grotte), which names entry 995494 at 33.98 m, '
            'beyond d 30.55 m', []))
        # An entry that prints no point: its distance is not known, so it is not taken to be another tree.
        out = self.run_rows(naming('n-1', [ref(P1), tag('991301')]))
        self.assertEqual(self.plant(out, P1)['candidates']['rule'],
                         'unknown between entry 991301, the entries within d and "not a register tree": entry prints '
                         f'no point: record n-1 (group 1) prints monitoring reference {P1}, card 991301 (Monopoli), '
                         'which names entry 991301, which prints no point')

    def test_an_entry_beyond_50_m_is_a_conflict_and_the_identity_is_unchanged(self):
        out = self.run_rows(naming('n-1', [ref(P6), tag('0990994', 'Ostuni')]))
        p6 = self.plant(out, P6)['candidates']
        self.assertEqual((p6['identity'], p6['rule']), ('not a register tree', 'no entry within d'))
        self.assertEqual([(n['entries'], n['cause'], n['distance_m'], n['d_m']) for n in p6['named']],
                         [(['992012'], 'entry not a candidate', 38709.13, 30.55)])

    def test_a_repeated_cod_or_a_card_repeated_in_its_comune_names_nothing(self):
        for group, entries in (([ref(P11), dict(cod=REPEATED)], ['991102', '991103']),
                               ([ref(P12), tag('996213', 'Nardò')], ['991201', '991202'])):
            with self.subTest(group=group):
                out = self.run_rows(naming('n-1', group))
                plant = self.plant(out, group[0]['sample'])['candidates']
                self.assertEqual(plant['identity'], 'unknown')
                self.assertEqual([(n['entries'], n['cause']) for n in plant['named']],
                                 [(entries, 'names several entries')])

    def test_an_entry_named_for_several_plants_decides_for_none(self):
        out = self.run_rows(naming('n-1', [ref(P1), tag('993858')]), naming('n-2', [ref('9100003'), tag('993858')]))
        for plant, own, other in ((P1, 'n-1', P3), (P3, 'n-2', P1)):
            with self.subTest(plant=plant):
                rule = self.plant(out, plant)['candidates']['rule']
                self.assertTrue(rule.startswith('unknown between the entries within d and "not a register tree": '
                                                'named for several plants: record ' + own), rule)
                self.assertIn(f'record {"n-2" if own == "n-1" else "n-1"} (group 1) names it for plant {other} '
                              '(entry within d)', rule)
        # Another plant's note naming the entry blocks it too: P9's note names 999001, 2 m from Q9.
        out = self.run_rows(naming('n-1', [ref(Q9), tag('0990101')]))
        self.assertEqual(self.plant(out, Q9)['candidates']['rule'],
                         'unknown between the entries within d and "not a register tree": named for several plants: '
                         f'record n-1 (group 1) prints monitoring reference {Q9}, card 0990101 (Monopoli), which names '
                         f"entry 999001 at 2.0 m, within d 30.55 m; plant {P9}'s note prints code 0990101, which "
                         'names it')

    def test_a_note_and_a_record_naming_one_entry_for_two_plants_leave_both_unknown(self):
        """The order plant 0e92c74d4485's shape: its note names entry 33450, and a record pairs another plant's
        reference with 33450's COD. As two notes printing one code name nothing, both plants are unknown."""
        out = self.run_rows(naming('n-1', [ref(Q9), dict(cod='990101_21_300_072030')]))
        self.assertEqual(self.plant(out, P9)['candidates']['rule'],
                         'unknown between the entries within d and "not a register tree": named for several plants: '
                         'its note prints code 0990101, which names entry 999001; record n-1 (group 1) names it for '
                         f'plant {Q9} (entry within d)')
        self.assertEqual(self.plant(out, Q9)['candidates']['identity'], 'unknown')
        self.assertNotIn('named', self.plant(out, P9)['candidates'])
        self.assertEqual(self.candidate(out, P9, '999001')['named_for'],
                         [dict(plants=[Q9], record='n-1', group=1, cause='entry within d')])
        # So does a record naming it for a plant beyond 50 m, or for a reference that names no plant: either part
        # of such a record may be the mistyped one.
        for group, cause in (([ref(P6), tag('0990101')], 'entry not a candidate'),
                             ([ref('9299999'), tag('0990101')], 'reference names no plant')):
            with self.subTest(cause=cause):
                rule = self.plant(self.run_rows(naming('n-1', group)), P9)['candidates']['rule']
                self.assertTrue(rule.startswith('unknown between the entries within d and "not a register tree": named '
                                                'for several plants: its note prints code 0990101'), rule)
                self.assertTrue(rule.endswith(f'({cause})'), rule)
        # A record that names the note's entry for the plant itself agrees with it, and decides it with the note.
        out = self.run_rows(naming('n-1', [ref(P9), tag('0990101')]))
        self.assertEqual(self.plant(out, P9)['candidates']['identity'], '999001')
        # Outside the grant, the record withholds the plant's results, as it could leave it unknown.
        out = self.run_rows(naming('n-1', [ref(Q9), tag('0990101')], source='e' * 64))
        self.assertEqual((self.plant(out, P9)['candidates']['identity'], self.plant(out, P9)['candidates']['needs']),
                         ('999001', ['authorized evidence for landscape-lodging record n-1']))

    def test_a_group_whose_parcel_or_other_identifier_disagrees_decides_nothing(self):
        """The rest of a group only vetoes the entry its tag or COD names (`protection.parcel_agrees`)."""
        group = [ref(P1), tag('993858')]
        for printed, cause in (([dict(comune='Monopoli', foglio='99', particella='999')], "record's parcel disagrees"),
                               ([dict(comune='Fasano', foglio='17', particella='175')], "record's parcel disagrees"),
                               ([dict(cod='990994_28_68_074012')], "record's identifiers disagree"),
                               ([dict(cod=REPEATED)], "record's identifiers disagree"),
                               ([tag('999999')], "record's identifiers disagree")):
            with self.subTest(printed=printed):
                p1 = self.plant(self.run_rows(naming('n-1', group + printed)), P1)['candidates']
                self.assertEqual(p1['identity'], 'unknown')
                self.assertTrue(p1['rule'].startswith('unknown between the entries within d and "not a register '
                                                      f'tree": {cause}: record n-1 (group 1) prints monitoring '
                                                      f'reference {P1}, card 993858 (Monopoli), '), p1['rule'])
                self.assertEqual([n['conflict'] for n in p1['named'] if n['entries'] == ['993516']], [cause])
        # A parcel that is the entry's own, its comune folded as `place` folds it, or no parcel, changes nothing.
        for printed in ([dict(comune=" monopoli ", foglio='17', particella='0175')], [dict(cod='UM993771')], []):
            with self.subTest(printed=printed):
                p1 = self.plant(self.run_rows(naming('n-1', group + printed)), P1)['candidates']
                self.assertEqual(p1['identity'], '993516')
        # An entry that prints no parcel cannot confirm one.
        register = [dataclasses.replace(e, particella=' ') if e.oid == '993516' else e for e in REGISTER]
        out = protection.named_rows(self.rows, register, [naming('n-1', group + [dict(comune='Monopoli', foglio='17',
                                                                                      particella='175')])],
                                    evaluated_at=CUTOFF, permitted_controlled_sources=GRANT, zone=ROME)
        self.assertIn(""""not a register tree": entry's parcel cannot confirm the record's: record n-1""",
                      self.plant(out, P1)['candidates']['rule'])
        # Beyond d, it stays unknown across the entry, with both causes.
        out = self.run_rows(naming('n-1', [ref(P5), tag('13', 'Castellana Grotte'),
                                           dict(comune='Castellana Grotte', foglio='1', particella='1')]))
        self.assertTrue(self.plant(out, P5)['candidates']['rule'].startswith(
            'unknown between entry 995494 and "not a register tree": entry beyond d, record\'s parcel disagrees: '))

    def test_rows_a_run_wrote_are_refused(self):
        """Only rows in the shape `rows` writes without records are taken (`protection.as_written`): a run's rows
        carry identities its records decided, which no later run may take as PR #30's."""
        run = self.run_rows(naming('n-1', [ref(P1), tag('993858')]))
        ungranted = self.run_rows(naming('n-1', [ref(P1), tag('993858')], source='e' * 64))
        plant = dict(named=self.plant(run, P1), named_for=self.plant(run, P2), needs=self.plant(ungranted, P1))
        for key, rows, where in (('naming_records', run, 'the rows'),
                                 ('run', dict(self.rows, run={}), 'the rows'),
                                 ('unread', dict(self.rows, unread=[]), 'the rows'),
                                 ('source', dict(self.rows, plants=[dict(self.rows['plants'][0], source='x')]),
                                  f'plant {P1}'),
                                 ('named', dict(self.rows, plants=[plant['named']]), f"plant {P1}'s candidates"),
                                 ('needs', dict(self.rows, plants=[plant['needs']]), f"plant {P1}'s candidates"),
                                 ('named_for', dict(self.rows, plants=[plant['named_for']]),
                                  f"plant {P2}'s candidate 993516")):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, f"{where} carries '{key}', which that shape"):
                protection.named_rows(rows, REGISTER, [], evaluated_at=CUTOFF, permitted_controlled_sources=GRANT,
                                      zone=ROME)

    def test_records_that_disagree_decide_nothing(self):
        out = self.run_rows(naming('n-1', [ref(P2), tag('993540')]), naming('n-2', [ref(P2), tag('993818')]))
        rule = self.plant(out, P2)['candidates']['rule']
        self.assertTrue(rule.startswith('unknown between the entries within d and "not a register tree": records '
                                        'disagree: record n-1'), rule)
        self.assertIn('names entry 993818 at 13.82 m, within d 30.55 m', rule)

    def test_a_record_and_the_note_that_disagree_decide_nothing(self):
        out = self.run_rows(naming('n-1', [ref(P9), tag('0990404')]))
        self.assertEqual(self.plant(out, P9)['candidates']['rule'],
                         'unknown between the entries within d and "not a register tree": record and note disagree: '
                         f'record n-1 (group 1) prints monitoring reference {P9}, card 0990404 (Monopoli), which names '
                         'entry 999004 at 15.0 m, within d 30.55 m; its note prints code 0990101, which names entry '
                         '999001')
        # A record that agrees with the note keeps the entry, and both are named.
        out = self.run_rows(naming('n-1', [ref(P9), tag('0990101')]))
        self.assertEqual(self.plant(out, P9)['candidates']['identity'], '999001')
        self.assertTrue(self.plant(out, P9)['candidates']['rule'].endswith(
            'its note prints code 0990101, which names entry 999001'))

    def test_a_reference_naming_separate_plants_decides_nothing_and_is_reported(self):
        out = self.run_rows(naming('n-1', [ref('9200377'), tag('997001')]))
        for plant in (P7, P8):
            with self.subTest(plant=plant):
                candidates = self.plant(out, plant)['candidates']
                self.assertEqual(candidates['identity'], 'unknown')
                self.assertEqual([(n['plants'], n['entries'], n['cause']) for n in candidates['named']],
                                 [([P7, P8], ['997001'], 'reference names separate plants')])
        # A reference that names no plant decides nothing either, and blocks the entry for another plant.
        out = self.run_rows(naming('n-1', [ref('9299999'), tag('993858')]), naming('n-2', [ref(P1), tag('993858')]))
        self.assertIn('named for several plants', self.plant(out, P1)['candidates']['rule'])
        self.assertIn('record n-1 (group 1) names it for plants none held here (reference names no plant)',
                      self.plant(out, P1)['candidates']['rule'])

    def test_a_record_outside_the_grant_names_nothing(self):
        out = self.run_rows(naming('n-1', [ref(P1), tag('993858')], source='e' * 64))
        p1 = self.plant(out, P1)['candidates']
        self.assertEqual((p1['identity'], p1.get('needs')), ('unknown', ['authorized evidence for landscape-lodging '
                                                                         'record n-1']))
        self.assertNotIn('named', p1)
        self.assertNotIn('named_for', self.candidate(out, P2, '993516'))
        # It could leave entry 993516 named for several plants, so each plant holding it among its candidates gets
        # the need too, and no identity moves.
        for other in (P2, P3, P4):
            with self.subTest(plant=other):
                self.assertEqual(self.plant(out, other)['candidates'].get('needs'),
                                 ['authorized evidence for landscape-lodging record n-1'])
                self.assertEqual(self.plant(out, other)['candidates']['identity'], 'unknown')
        self.assertEqual((out['naming_records'], out['ungranted']), ([], [dict(
            record='n-1', kind='landscape-lodging', need='authorized evidence for landscape-lodging record n-1')]))
        # It reaches only a plant a granted version could change: not one whose card repeats in its comune (P12
        # holds 991201, one of the two entries card 996213 names in Nardò, and a granted version names nothing), nor
        # one whose entry lies beyond 50 m (P6); one beyond d within 50 m (P5) or printing no point (P1) is reached.
        for group, reached in (([ref(P12), tag('996213', 'Nardò')], []), ([ref(P6), tag('0990994', 'Ostuni')], []),
                               ([ref(P11), dict(cod=REPEATED)], []),
                               ([ref(P5), tag('13', 'Castellana Grotte')], [P5]), ([ref(P1), tag('991301')], [P1])):
            with self.subTest(group=group):
                out = self.run_rows(naming('n-1', group, source='e' * 64))
                self.assertEqual([p['plant'] for p in out['plants'] if p['candidates'].get('needs')], reached)
                self.assertEqual(out['ungranted'][0]['record'], 'n-1')
                granted = self.run_rows(naming('n-1', group))
                changed = [p['plant'] for p, q in zip(self.rows['plants'], granted['plants'])
                           if (p['candidates']['identity'], p['candidates']['rule']) !=
                           (q['candidates']['identity'], q['candidates']['rule'])]
                self.assertEqual(changed, reached)

    def test_a_record_after_the_cutoff_refuses_the_set_and_no_record_changes_nothing(self):
        with self.assertRaisesRegex(ValueError, 'Record n-2 .* states occurred 2025-10-01, later than the evaluation'):
            self.run_rows(naming('n-1', [ref(P1), tag('993858')]),
                          naming('n-2', [ref(P2), tag('993540')], source='e' * 64, occurred=date(2025, 10, 1)))
        self.assertIs(self.run_rows(), self.rows)
        with self.assertRaises(TypeError):
            self.run_rows(naming('n-1', [ref(P1), tag('993858')]), grant={'f' * 64})

    def test_one_reader_of_a_printed_card(self):
        """The register's comune variants are one comune, and a text card is read as printed (`Register`)."""
        register = protection.Register(REGISTER + [entry('991302', 'APP_996213', 'APP_996213', "NARDO'", 175000.0,
                                                         200000.0)])
        for printed, comune in (('996213', 'Nardò'), ('0996213', " nardo' "), ('996213', 'NARDO`')):
            self.assertEqual([e.oid for e in register.card(printed, comune)], ['991201', '991202'])
        self.assertEqual([e.oid for e in register.card('app_996213', 'Nardò')], ['991302'])
        self.assertEqual([e.oid for e in register.cod(f' {REPEATED} ')], ['991102', '991103'])
        # The note-code rule reads the same way: a monitoring record's NARDÒ is the register's NARDO'.
        code, = protection.note_codes({'9200500': ('NARDÒ', 175002.0, 200000.0, ('targhetta n. 0991399',))},
                                      REGISTER + [entry('991399', 'UM991399', '991399', "NARDO'", 175000.0, 200000.0)],
                                      lambda plant, e: 30.55)
        self.assertEqual((code.entry, code.cause), ('991399', 'names entry'))


class ReadProtectionRun(unittest.TestCase):
    """`read_protection.py --records`: the run states its decision, cutoff and grant, and its rows are its own."""

    def test_the_run_is_stated_and_its_rows_never_go_to_the_shared_file(self):
        import sys
        import tempfile
        from unittest import mock
        sys.path.insert(0, str(ROOT / 'scripts'))
        import read_protection
        stated = ['--records', '/nonexistent.json', '--decision', '2025-09-01', '--known-through', CUTOFF.isoformat(),
                  '--permitted-controlled-sources']
        for argv in (stated[:4] + stated[6:], stated[:2] + stated[4:], stated[:6], stated[2:] + ['--out', '/tmp/x'],
                     stated[:5] + ['2025-09-30T18:00:00'] + stated[6:]):
            with self.subTest(argv=argv), mock.patch('sys.stderr'), self.assertRaises(SystemExit):
                read_protection.arguments(argv)
        self.assertEqual(read_protection.arguments(stated)[1].permitted_controlled_sources, [])
        self.assertIsNone(read_protection.arguments([])[1].decision)
        with tempfile.TemporaryDirectory() as store:
            records = Path(store) / 'records.json'
            records.write_text(json.dumps([naming('n-1', [ref(P1), tag('993858')], occurred=date(2025, 10, 1))]))
            run = ['--records', str(records)] + stated[2:]
            with mock.patch.object(read_protection, 'store_root', return_value=Path(store)), \
                    mock.patch.object(protection, 'read', side_effect=AssertionError('the store is not read')):
                # A run's rows never go to the shared rows folder.
                with mock.patch('sys.stderr'), self.assertRaises(SystemExit):
                    read_protection.main(run + ['--out', f'{store}/derived/protected-status/run.json'])
                # A record after the cutoff refuses the set before the store is read.
                with self.assertRaisesRegex(ValueError, 'later than the evaluation'):
                    read_protection.main(run + ['--out', f'{store}/run.json'])
            self.assertFalse((Path(store) / 'derived').exists())

    def test_a_runs_rows_fed_back_through_read_landscape_are_refused(self):
        """`read_protection.py --records --out X` writes a run's rows, whose identities rest on that run's records;
        `read_landscape.py --rows X` refuses them, so a grant cannot attach through a record outside its own run."""
        import sys
        import tempfile
        from unittest import mock
        sys.path.insert(0, str(ROOT / 'scripts'))
        import read_landscape
        import read_protection
        rows = fixture_rows()
        rows.update(zone_entries=[dict(e, layer='listed') for e in rows['zone_entries']], reference_fixes=[], bounds={},
                    survey_batches=[], unread_deletions=[])
        result = dict(bounds={}, batches={}, entries={e.oid: e for e in REGISTER})
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            (folder / 'naming.json').write_text(json.dumps([naming('n-1', [ref(P1), tag('993858')])]))
            (folder / 'grant.json').write_text(json.dumps([naming('d-1', [tag('993858')])]))
            stated = ['--known-through', CUTOFF.isoformat(), '--permitted-controlled-sources', 'f' * 64]
            with mock.patch.object(read_protection, 'store_root', return_value=folder), \
                    mock.patch.object(protection, 'read', return_value=result), \
                    mock.patch.object(protection, 'rows', return_value=rows), mock.patch('sys.stdout'):
                read_protection.main(['--records', str(folder / 'naming.json'), '--decision', '2025-09-01',
                                      '--out', str(folder / 'run.json')] + stated)
            written = json.loads((folder / 'run.json').read_text())
            self.assertEqual(next(p for p in written['plants'] if p['plant'] == P1)['candidates']['identity'], '993516')
            argv = ['read_landscape.py', '--records', str(folder / 'grant.json'), '--plants', P1, '--at', '2025-09-01',
                    '--rows', str(folder / 'run.json')] + stated
            with mock.patch.object(sys, 'argv', argv), mock.patch.object(read_landscape, 'store_root', return_value=folder), \
                    mock.patch.object(read_landscape, 'register', return_value=REGISTER), mock.patch('sys.stdout'), \
                    self.assertRaisesRegex(ValueError, "the rows carries 'naming_records', which that shape does not"):
                read_landscape.main()

    def test_verify_holds_named_rows_to_the_run_inputs(self):
        """`contracts.json` names `protection.named_rows` as a run-input entry point: neither its cutoff nor its grant
        may have a default."""
        from unittest import mock
        import verify
        verify.verify()

        def cutoff_defaulted(rows, register, supplied, *, permitted_controlled_sources, zone, bound_of=None,
                             evaluated_at=CUTOFF):
            raise AssertionError('not called')

        def grant_defaulted(rows, register, supplied, *, evaluated_at, zone, bound_of=None,
                            permitted_controlled_sources=frozenset()):
            raise AssertionError('not called')
        for name, fake in (('evaluated_at', cutoff_defaulted), ('permitted_controlled_sources', grant_defaulted)):
            with self.subTest(name=name), mock.patch.object(protection, 'named_rows', fake), \
                    self.assertRaisesRegex(ValueError, f'{name} has a default on cordon_d.protection.named_rows'):
                verify.verify()


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
        # Every bound names the reference fixes it is computed from.
        self.assertEqual(bounds[batch].observations, tuple(f.observation for f in fixes if not f.dropped and f.batch == batch))
        self.assertTrue(all(len(b.observations) == len(wide) for b in small))

    def test_the_2011_census_batch_and_its_check_is_not_run_under_20_fixes(self):
        # The recitals of DGR 1358/2012, DGR 357/2013, DGR 2227/2013 and DGR 1417/2013 name the SIT srl systematic
        # survey. DGR 2227/2013's also name the Comune di Casarano's request for 226 trees, and DGR 1417/2013's the
        # Comune di Maruggio's for 83 (read from the acts' own pages).
        acts = self.result['acts']
        self.assertIn((protection.SIT, 127719), acts['DGR 1358/2012'].surveys)
        self.assertIn((protection.SIT, 172340), acts['DGR 357/2013'].surveys)
        self.assertIn((protection.SIT, 1783), acts['DGR 2227/2013'].surveys)
        self.assertIn((protection.SIT, 1238), acts['DGR 1417/2013'].surveys)
        self.assertEqual((acts['DGR 2227/2013'].requests, acts['DGR 1417/2013'].requests),
                         ((('Casarano', 226),), (('Maruggio', 83),)))
        # The census batch holds the dated SIT groups of three labels. DGR 1417/2013's SIT trees print no survey date,
        # cannot be told from Maruggio's 83 by date, and stay under their label; its rule says so.
        labels = {protection._canonical(self.result['entries'][o].label)
                  for o, b in self.result['batches'].items() if b == protection.SIT}
        self.assertEqual(labels, {'DGR 1358/2012', 'DGR 357/2012', 'DGR 2227/2013'})
        rules = {r.split(':')[0]: r for r in self.result['batch_rules']}
        rule = rules['label DGR 1417/2013, survey group survey date not recorded']
        self.assertIn('a municipal request, Comune di Maruggio (83), which this reader does not separate', rule)
        self.assertIn("cannot tell the survey's entries from the request's by date", rule)
        self.assertTrue(rule.endswith('batch: DGR 1417/2013, survey date not recorded'))
        rule = rules['label DGR 2227/2013, survey group 2012..2012']
        self.assertIn('a municipal request, Comune di Casarano (226), which this reader does not separate', rule)
        self.assertIn(f'{protection.SIT} is the one source they name whose entries print survey dates', rule)
        self.assertTrue(rule.endswith(f'batch: {protection.SIT}'))
        own = [f.residual_m for f in self.result['fixes'] if not f.dropped and f.batch == protection.SIT]
        self.assertLess(len(own), protection.MIN_FIXES)
        bound = self.result['bounds'][protection.SIT]
        self.assertTrue(bound.applies.startswith('register-wide'))
        # The tolerance is read from the held capitolato d'oneri, Art. 3 point 4, not written as a figure.
        metres, quotation, _ = protection.contract_terms(STORE)
        self.assertEqual(metres, 1.0)
        self.assertIn('ricevitore satellitare GPS differenziale', quotation)
        self.assertIn(quotation, bound.check)
        self.assertIn(f'Not checked: the census has {len(own)} fixes, under 20, and takes the register-wide bound',
                      bound.check)
        self.assertIn(f"own 95th percentile, {float(numpy.percentile(own, 95)):.2f} m", bound.check)
        self.assertEqual([b for b in self.result['bounds'].values() if b.check], [bound])

    def test_the_2011_check_compares_the_tolerance_from_20_census_fixes(self):
        # The census has 19 held fixes, so this branch has not run on the held batch. Twenty held fixes, taken as
        # the census's, reach it: the census's own bound, compared with 1.00 m plus the fixes' own error.
        kept = [f for f in self.result['fixes'] if not f.dropped]
        census = [dataclasses.replace(f, batch=protection.SIT) for f in kept[:protection.MIN_FIXES]]
        contract = protection.contract_terms(STORE)
        bound = protection.batch_bounds(census, {protection.SIT}, set(), contract_batch={protection.SIT},
                                        contract=contract)[protection.SIT]
        own = [f.distance_m + f.observation_error_m for f in census]
        self.assertEqual((bound.applies, bound.fixes), (protection.SIT, 20))
        self.assertEqual(bound.error_m, round(float(numpy.percentile(own, 95)), 2))
        tolerance = contract[0] + max(f.observation_error_m for f in census)
        excess = bound.error_m - tolerance
        self.assertIn(f"{tolerance:.2f} m; the census's own bound is {bound.error_m:.2f} m: " +
                      ('within' if excess <= 0 else f'exceeded by {excess:.2f} m') +
                      '. The measured bound stands either way.', bound.check)
        self.assertIn(contract[1], bound.check)
        self.assertNotIn('Not checked', bound.check)
        # One fix fewer is not checked.
        bound = protection.batch_bounds(census[:-1], {protection.SIT}, set(), contract_batch={protection.SIT},
                                        contract=contract)[protection.SIT]
        self.assertIn('Not checked: the census has 19 fixes, under 20', bound.check)

    def test_both_layers_are_kept_and_no_parcel_screen_or_survey_finding_is_emitted(self):
        held = [e for e in self.result['entries'].values() if e.layer in ('listed', 'provisional')]
        self.assertEqual(len(held), 341428 + 569)  # layer 0's ids overlap layer 1's; both layers are kept
        out = protection.rows(self.result)
        self.assertNotIn('gross_error_screen', out)
        entry = out['zone_entries'][0]
        self.assertFalse({'parcel_screen', 'survey_finding'} & set(entry))
        # The printed cadastral reference stays, as printed.
        e = self.result['entries'][entry['entry']]
        self.assertEqual((entry['comune'], entry['foglio'], entry['particella']), (e.comune, e.foglio, e.particella))
        # The qualification carries its date and its sources.
        q = entry['qualification']
        self.assertEqual(q['date'], DECISION.isoformat())
        self.assertEqual(q['sources']['entry_point'], entry['source'])
        self.assertIn(entry['batch'], q['sources']['reference_fixes'])
        self.assertEqual(len(q['sources']['reference_fix_error']), 3)
        # The method and the 2011 check are emitted once, under bounds; each entry points to them.
        for entry in out['zone_entries']:
            q, at = entry['qualification'], f"bounds[{entry['batch']!r}]"
            self.assertEqual((q['method'], q['check']),
                             (f'{at}.method', f'{at}.check' if out['bounds'][entry['batch']]['check'] else None))
        self.assertTrue(all('monitoring residuals' in b['method'] for b in out['bounds'].values()))
        self.assertIn('Not checked', out['bounds'][protection.SIT]['check'])

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
