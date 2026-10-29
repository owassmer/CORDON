"""Row 10: the landscape proceeding's record reaches C's Art. 33(1), 146(5) and 146(8) through the ordinary caller.

Every record, register entry and monitoring plant here is a FIXTURE (`fixture: true`, identifiers 99xxxxx and
91xxxxx): invented in the shapes PR #30's rows show. A is positive 1606667's shape: a monitored olive whose note
prints the census tag of the one entry it is (340453; COD 107007_17_159_072030, card 0107007, MONOPOLI fg 17 p.lla
159), with another entry within d. D is negative olive 11200168's, the shape of every negative olive with a register
candidate: its identity is "unknown", with one candidate entry within d (343516; COD UM351771, card 903858, MONOPOLI
fg 17 p.lla 175). E1 and E2 carry one monitoring reference at two dates (10600377's shape); G is an order plant whose
`coincides_with` holds a monitoring reference (1314059's). None is a fact about a real plant or proceeding. PR #30's
identity is computed by PR #30's own functions (`protection.note_codes`, `protection.candidates`) over the fixture
register; the attachment reads only that identity.

Expected needs are the strings the probe of C's rows returned (PR #37's plan), written out here, not taken from the
code under test. The clock's end is counted by hand: 45 calendar days from Tuesday 17 June 2025 end on Friday
1 August 2025, so C's exclusive boundary is 2 August 00:00 in Rome. Distances are counted by hand from the fixture
points (D at x 701000, entry 990004 at x 700015, the same y: 985 m).
"""
import copy
import dataclasses
from datetime import date, datetime
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest import mock
from zoneinfo import ZoneInfo

from cordon_c.core import Snapshot, evaluate
from cordon_d import landscape, protection
from cordon_d.calendar import national_calendar
from cordon_d.case_prescriptions import supplied_records
from cordon_d.landscape import (APPLICATION, DECISION, GRANTED, NOT_SUPPLIED, OPINION, RECEIVED, ROUTE, RULE, UNION,
                                UPSTREAM, landscape_results)
import verify

ROOT = Path(__file__).resolve().parents[2]
ROME = ZoneInfo('Europe/Rome')
AT = date(2025, 9, 1)
CUTOFF = datetime(2025, 9, 30, 18, tzinfo=ROME)
GRANT = frozenset({'f' * 64})
LODGED = date(2025, 6, 17)
DUE = datetime(2025, 8, 2, tzinfo=ROME)
DECIDED = date(2025, 8, 20)
AFTER = date(2025, 9, 2)
V33 = 'IT-DLGS-19-2021:Art.33(1):uninfected-protected-plant-removal:v1'
NEED = {
    'grant': f'predicate: {V33} :: the required landscape authorization has been granted',
    'union': f'predicate: {V33} :: removal complies with applicable Union obligations',
    'measure': f'predicate: {V33} :: a valid measure requires plant removal in the exact demarcated area',
    'status': f'predicate: {V33} :: the plant has monumental or historic-interest legal status',
    'infection': f'predicate: {V33} :: infection is currently established in the plant',
}
EDGE = 'complete landscape application submitted'
ROUTE_NEED = ('predicate: IT-DLGS42-A146:Art.146(5):regional-decision-owner:v1 :: the applicable '
              'superintendent-opinion route is resolved')
RECEIPT_NEED = ('predicate: IT-DLGS42-A146:Art.146(8):superintendent-opinion:v1 :: the superintendent receives the '
                'complete acts for the landscape-authorization application')
# A and B are register entries by their note's tag; B's entry shares its COD with an entry elsewhere. C is not a
# register tree. D is "unknown", with one candidate entry. E1 and E2 carry reference 9100005; G carries 9100006.
A, B, C, D = '9100001', '9100002', '9100003', '9100004'
E1, E2, G = '9100005@2023-03-07', '9100005@2024-03-07', 'feedfeedfeed@17.30000000,40.80000000'
REPEATED = '990202_22_310_072030'
SUPERINTENDENT = 'Soprintendenza ABAP per la città metropolitana di Bari (FIXTURE)'
AUTHORITY = 'Regione Puglia, Sezione Tutela e valorizzazione del paesaggio (FIXTURE)'


def entry(oid, key, card, foglio, particella, x, y):
    return protection.Entry('listed', oid, key, card, 'DGR 357/2012', None, 'MONOPOLI', foglio, particella, x, y,
                            date(2012, 11, 13), 'e' * 64)


REGISTER = [entry('990001', '990101_21_300_072030', '0990101', '21', '300', 700000.0, 4500000.0),
            entry('990004', '990404_21_301_072030', '0990404', '21', '301', 700015.0, 4500000.0),
            entry('990002', REPEATED, '0990202', '22', '310', 700500.0, 4500000.0),
            entry('990003', REPEATED, '0990303', '22', '311', 705000.0, 4505000.0),
            entry('990005', 'UM990505', '990505', '23', '400', 701015.0, 4500000.0)]
PLANTS = {A: ('MONOPOLI', 700002.0, 4500000.0, ('sintomi assenti. pianta monumentale censita targhetta n. 0990101',)),
          B: ('MONOPOLI', 700501.0, 4500000.0, ('pianta monumentale targhetta n. 0990202',)),
          C: ('MONOPOLI', 720000.0, 4520000.0, ()),
          D: ('MONOPOLI', 701000.0, 4500000.0, ()),
          E1: ('MONOPOLI', 730000.0, 4530000.0, ()),
          E2: ('MONOPOLI', 730000.0, 4530000.0, ()),
          G: ('MONOPOLI', 740000.0, 4540000.0, ())}
SEEN = {E1: ('order plant', [['9100005', '2023-03-07']], []), E2: ('negative olive', [['9100005', '2024-03-07']], []),
        G: ('order plant', [['9100006', '2022-06-17']], ['9100006'])}
ERROR_M, BOUND = 7.4, SimpleNamespace(error_m=23.15)


def pr30_rows():
    """PR #30's rows for the fixture plants, with the identity its own note-code rule and candidates give."""
    codes = protection.note_codes(PLANTS, REGISTER, lambda plant, e: ERROR_M + BOUND.error_m)
    rows = []
    for plant, (comune, x, y, notes) in PLANTS.items():
        named = [c for c in codes if c.plant == plant]
        cand = protection.candidates(plant, x, y, ERROR_M, REGISTER, lambda e: BOUND, named)
        kind, observations, coincides = SEEN.get(plant, ('negative olive', [[plant, '2025-05-12']], []))
        rows.append(dict(plant=plant, kind=kind, order=None, coincides_with=coincides, comune=comune,
                         point=dict(x=x, y=y, crs='EPSG:32633', error_m=ERROR_M), observations=observations,
                         codes=[dict(code=c.code, entry=c.entry, cause=c.cause) for c in named],
                         candidates={'not a register tree': True, 'identity': cand.identity, 'rule': cand.rule,
                                     'entries': [dict(entry=e, distance_m=dm, d_m=d) for e, dm, d in cand.entries]}))
    return dict(plants=rows, zone_entries=[])


def record(name, kind, plants, occurred, **fields):
    return dict(record=name, kind=kind, document=f'FIXTURE protocol {name}', source='f' * 64,
                selector=f'fixture:{name}', reading=f'FIXTURE {kind}: not a fact about any plant or proceeding',
                plants=plants, occurred=occurred.isoformat(), fixture=True, **fields)


def sample(ref):
    return dict(sample=ref)


def tag(card, comune='Monopoli'):
    return dict(card=card, comune=comune)


def parcel(foglio, particella, comune='Monopoli'):
    return dict(comune=comune, foglio=foglio, particella=particella)


def on(*identifiers):
    """One plant, named by the identifiers the record prints for it."""
    return [list(identifiers)]


def decision(name, plants, outcome='granted', occurred=DECIDED, kind='removal', conditions=(), issuer=AUTHORITY):
    return record(name, 'landscape-decision', plants, occurred, outcome=outcome, intervention_kind=kind,
                  intervention="espianto dell'ulivo monumentale non infetto ai sensi dell'art. 33, c. 1",
                  procedure='procedimento ordinario, art. 146 D.lgs. 42/2004', conditions=list(conditions),
                  issuer=issuer)


def lodging(name, plants, complete=True, occurred=LODGED, recipient=AUTHORITY):
    return record(name, 'landscape-lodging', plants, occurred, complete=complete, recipient=recipient)


def route(name, plants, resolved=True, occurred=date(2025, 7, 30)):
    return record(name, 'landscape-opinion-route', plants, occurred, resolved=resolved,
                  route='parere della Soprintendenza ai sensi dell\'art. 146, c. 8')


def received(name, plants, complete=True, occurred=date(2025, 6, 24), recipient=SUPERINTENDENT):
    return record(name, 'landscape-acts-received', plants, occurred, complete=complete, recipient=recipient)


def ungranted(item):
    return dict(item, source='e' * 64)


def need(item):
    return f"authorized evidence for {item['kind']} record {item['record']}"


# The owning units' values for Art. 33(1)'s three upstream conjuncts (FIXTURES).
SETTLED = {UPSTREAM[0]: True, UPSTREAM[1]: True, UPSTREAM[2]: False}


class LandscapeRecords(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Snapshot.load(ROOT)
        cls.rows = pr30_rows()
        identities = {p['plant']: p['candidates']['identity'] for p in cls.rows['plants']}
        # PR #30's identity, from its own rules: A is entry 990001 only through its tag (990004 is also within d);
        # D is unknown between entry 990005 and "not a register tree".
        assert identities == {A: '990001', B: '990002', C: 'not a register tree', D: 'unknown',
                              E1: 'not a register tree', E2: 'not a register tree', G: 'not a register tree'}, \
            identities
        entries = {p['plant']: {e['entry'] for e in p['candidates']['entries']} for p in cls.rows['plants']}
        assert entries[A] == {'990001', '990004'} and entries[D] == {'990005'}, entries

    def run_caller(self, supplied, plants=(A, B, C, D), at=AT, upstream=None, evaluated_at=CUTOFF, grant=GRANT,
                   **options):
        return landscape_results(self.s, at, list(plants), supplied, evaluated_at=evaluated_at,
                                 permitted_controlled_sources=grant, rows=self.rows, register=REGISTER, zone=ROME,
                                 calendar=national_calendar(), upstream=upstream, **options)

    def art33(self, supplied, plant=A, settled=True, at=AT):
        run = self.run_caller(supplied, at=at, upstream={plant: SETTLED} if settled else None)
        return run['plants'][plant]['results'][RULE], run

    def causes(self, run):
        return [(u['record'], u['group'], u['cause']) for u in run['unattached']]

    def test_a_plant_with_no_record_gets_Cs_unknown_with_the_probed_needs(self):
        run = self.run_caller([])
        for plant in (A, B, C, D):
            result = run['plants'][plant]['results'][RULE]
            self.assertIsNone(result.truth)
            self.assertEqual(result.needs, set(NEED.values()))
        result, _ = self.art33([])
        self.assertIsNone(result.truth)
        self.assertEqual(result.needs, {NEED['grant'], NEED['union']})
        # An upstream conjunct not supplied adds its need as C lists it.
        partial = self.run_caller([], upstream={A: {UPSTREAM[0]: True, UPSTREAM[2]: False}})
        self.assertEqual(partial['plants'][A]['results'][RULE].needs, {NEED['grant'], NEED['union'], NEED['status']})
        self.assertEqual((run['unattached'], run['elsewhere'], run['ungranted']), ([], [], []))
        self.assertIn(UNION, run['not_supplied'])
        self.assertIn(APPLICATION, run['not_supplied'])
        # The caller evaluates exactly the three rows; Art. 146(2) is not among them.
        self.assertEqual(set(run['plants'][A]['results']), {RULE, DECISION, OPINION})

    def test_art_146_2_states_what_separates_it_from_146_5_and_146_8(self):
        cause = NOT_SUPPLIED[APPLICATION]
        for part in ('Art. 146(5) and 146(8)', '"the proposed intervention requires landscape authorization" is the '
                     "statute's own meaning", 'which D does not supply', '"the property or area has legally protected '
                     'landscape status" would need the PPTR reads that ruling makes unneeded',
                     f'only through the performance edge "{EDGE}", which a lodging stated complete fills'):
            self.assertIn(part, cause)

    def test_a_grant_fills_the_conjunct_from_the_decisions_date_with_its_procedure_conditions_and_issuer(self):
        for outcome, conditions in (('granted', ()), ('granted-with-conditions',
                                                       ('Il reimpianto di un ulivo della stessa cultivar entro 90 '
                                                        'giorni.', 'La conservazione del materiale legnoso.'))):
            with self.subTest(outcome=outcome):
                result, run = self.art33([decision('d-1', on(sample(A)), outcome, conditions=conditions)])
                self.assertIsNone(result.truth)
                self.assertEqual(result.needs, {NEED['union']})
                plant = run['plants'][A]
                self.assertIs(plant['facts'][RULE][GRANTED], True)
                self.assertEqual(plant['decision']['occurred'], DECIDED)
                self.assertEqual(plant['decision']['procedure'], 'procedimento ordinario, art. 146 D.lgs. 42/2004')
                self.assertEqual(plant['decision']['conditions'], list(conditions))
                self.assertEqual(plant['decision']['issuer'], AUTHORITY)
                self.assertTrue(plant['fixture'])
                # From the decision's date: the day before, the grant is still C's need.
                before, _ = self.art33([decision('d-1', on(sample(A)), outcome, conditions=conditions)],
                                       at=date(2025, 8, 19))
                self.assertEqual(before.needs, {NEED['grant'], NEED['union']})
                # What the caller passed, with the Union value no D reader supplies, opens C's route.
                facts = {(V33, p): v for p, v in plant['facts'][RULE].items()} | {(V33, UNION): True}
                self.assertEqual(evaluate(self.s, RULE, AT, facts).effect, self.s.versions[V33]['true_effect'])
        # An issuer the record does not print is carried as null; D judges no competence either way.
        _, run = self.art33([decision('d-1', on(sample(A)), issuer=None)])
        self.assertIsNone(run['plants'][A]['decision']['issuer'])
        self.assertIs(run['plants'][A]['facts'][RULE][GRANTED], True)

    def test_a_denial_makes_it_false(self):
        for settled in (True, False):
            result, _ = self.art33([decision('d-1', on(sample(A)), 'denied')], settled=settled)
            self.assertIs(result.truth, False)
            self.assertEqual(result.effect, self.s.versions[V33]['false_effect'])

    def test_a_same_day_grant_and_denial_supply_nothing(self):
        result, run = self.art33([decision('d-1', on(sample(A))), decision('d-2', on(sample(A)), 'denied')])
        self.assertEqual(result.needs, {NEED['grant'], NEED['union']})
        self.assertNotIn(GRANTED, run['plants'][A]['facts'][RULE])
        self.assertIsNone(run['plants'][A]['decision'])
        self.assertEqual(run['plants'][A]['reported'], [dict(
            records=['d-1', 'd-2'], cause='records of 2025-08-20 state different values; the caller does not choose')])
        # Who decided is reported beside the result: one day's decisions printing different issuers supply nothing.
        result, _ = self.art33([decision('d-1', on(sample(A))),
                                decision('d-2', on(sample(A)), issuer='Comune (FIXTURE)')])
        self.assertEqual(result.needs, {NEED['grant'], NEED['union']})
        # A later day's decision decides.
        later, _ = self.art33([decision('d-1', on(sample(A))), decision('d-2', on(sample(A)), 'denied',
                                                                          occurred=date(2025, 8, 25))])
        self.assertIs(later.truth, False)

    def test_nothing_but_a_decision_for_the_plant_and_its_removal_fills_the_grant(self):
        for name, supplied in (
                ('an opinion alone', [route('r-1', on(sample(A)))]),
                ('a pending application', [lodging('l-1', on(sample(A))), received('a-1', on(sample(A)))]),
                ('a replant-only consent', [decision('d-1', on(sample(A)), kind='replanting-only')]),
                ('a grant for another project', [decision('d-1', on(sample(A)), kind='other')]),
                ('a grant for another plant', [decision('d-1', on(sample(C)))])):
            with self.subTest(name):
                result, run = self.art33(supplied)
                self.assertIsNone(result.truth)
                self.assertEqual(result.needs, {NEED['grant'], NEED['union']})
                self.assertNotIn(GRANTED, run['plants'][A]['facts'][RULE])
        _, run = self.art33([decision('d-1', on(sample(A)), kind='replanting-only')])
        self.assertIn('not this removal; it fills nothing', run['plants'][A]['reported'][0]['cause'])
        # The grant for C fills C's grant, not A's.
        run = self.run_caller([decision('d-1', on(sample(C)))])
        self.assertIs(run['plants'][C]['facts'][RULE][GRANTED], True)

    def test_a_decision_printing_the_card_or_tag_attaches_through_PR30s_identity(self):
        for printed in ([tag('0990101')], [tag('990101', 'MONOPOLI ')], [dict(cod='990101_21_300_072030')],
                        [tag('0990101'), parcel('21', '300')], [sample(A), dict(cod='990101_21_300_072030')]):
            with self.subTest(printed=printed):
                result, run = self.art33([decision('d-tag', [printed])])
                self.assertEqual(run['unattached'], [])
                self.assertEqual(run['plants'][A]['records'], ['d-tag'])
                self.assertEqual(result.needs, {NEED['union']})
        # The neighbouring entry's tag names its own entry, which is no plant's identity nor an "unknown" plant's
        # candidate: no match.
        run = self.run_caller([decision('d-tag', on(tag('0990404')))])
        self.assertEqual(self.causes(run), [('d-tag', 1, 'no match')])
        self.assertEqual(run['plants'][A]['results'][RULE].needs, set(NEED.values()))

    def test_a_repeated_cod_stays_unattached_and_fills_nothing(self):
        empty = self.run_caller([], upstream={B: SETTLED})
        run = self.run_caller([decision('d-cod', on(dict(cod=REPEATED)))], upstream={B: SETTLED})
        self.assertEqual(self.causes(run), [('d-cod', 1, 'several matches')])
        self.assertEqual(run['unattached'][0]['identifiers'][0]['entries'], ['990002', '990003'])
        for plant in (A, B, C, D):
            self.assertEqual(run['plants'][plant]['results'], empty['plants'][plant]['results'])
            self.assertEqual(run['plants'][plant]['records'], [])
        # The same COD qualifies B's tag, since B's entry is one of the entries it names.
        run = self.run_caller([decision('d-cod', on(dict(cod=REPEATED), tag('0990202')))], upstream={B: SETTLED})
        self.assertEqual(run['plants'][B]['records'], ['d-cod'])

    def test_unattached_causes(self):
        for printed, cause in (([sample('9199999')], 'no match'),
                               ([sample(A), sample(C)], 'identifiers in conflict'),
                               ([tag('0990101'), sample(C)], 'identifiers in conflict'),
                               ([tag('0990101'), parcel('22', '310')], 'identifiers in conflict'),
                               ([parcel('21', '300')], 'several matches'),
                               ([sample('9100005')], 'several matches'),
                               ([tag('0990101', 'Fasano')], 'no match'),
                               ([tag('0990101'), sample('9199999')], 'identity undecided')):
            with self.subTest(printed=printed):
                run = self.run_caller([decision('d-x', [printed])])
                self.assertEqual([u['cause'] for u in run['unattached']], [cause])
                self.assertTrue(all(run['plants'][p]['records'] == [] for p in (A, B, C, D)))
        run = self.run_caller([decision('d-x', on(sample(A), sample(C)))])
        self.assertEqual(run['unattached'][0]['detail'], [f'monitoring reference {A} names plant {A}',
                                                          f'monitoring reference {C} names plant {C}'])
        # A reference beside a card is a naming record for row 9: it names A's note entry 990001 for C, 28 km away,
        # or for no plant, so A is unknown (`protection.identity`) and the card names only a candidate of it.
        run = self.run_caller([decision('d-x', on(tag('0990101'), sample(C)))])
        self.assertEqual(run['unattached'][0]['detail'], [
            f'card 0990101 (Monopoli) names entry 990001, 28284.27 m from plant {C}; row 9 found no entry within d of '
            'it'])
        self.assertEqual(run['plants'][A]['identity']['identity'], 'unknown')
        run = self.run_caller([decision('d-x', on(sample(A), tag('0990101', 'Fasano'), sample('9199999')))])
        self.assertEqual(run['unattached'][0]['detail'], [
            'card 0990101 (Fasano) names no register entry held here',
            f"monitoring reference 9199999 names no plant, not plant {A}"])
        # A card naming no register entry blocks for every plant: the index finding none is not evidence that no
        # tree carries it.
        for plant in (A, C, D):
            with self.subTest(plant=plant):
                run = self.run_caller([decision('d-x', on(sample(plant), tag('0990101', 'Fasano')))])
                self.assertEqual(self.causes(run), [('d-x', 1, 'identifiers in conflict')])

    def test_a_card_is_read_as_the_register_prints_it(self):
        """A non-numeric census card (the register prints APP_618213 as SCHEDAN and COD alike) names its entry, and a
        comune's printed variants (NARDO', NARDO`, Nardò) are one comune."""
        register = REGISTER + [protection.Entry('listed', '990006', 'APP_990606', 'APP_990606', 'DGR 1193/2021', None,
                                                "NARDO'", '13', '370', 760000.0, 4460000.0, date(2021, 7, 19),
                                                'e' * 64)]
        run = landscape_results(self.s, AT, [C, D], [decision('d-1', on(sample(C), tag('APP_990606', 'Nardò'))),
                                                    decision('d-2', on(sample(D), dict(cod='APP_990606')))],
                                evaluated_at=CUTOFF, permitted_controlled_sources=GRANT, rows=self.rows,
                                register=register, zone=ROME, calendar=national_calendar())
        self.assertEqual(self.causes(run), [('d-1', 1, 'identifiers in conflict'), ('d-2', 1, 'identifiers in conflict')])
        for item in run['unattached']:
            self.assertTrue(item['detail'][0].split(' names entry ')[1].startswith('990006, '), item['detail'])
        identities = landscape.Identities(self.rows, register)
        for card, comune in (('APP_990606', "NARDO`"), ('app_990606', 'Nardò'), ('APP_990606', "NARDO'")):
            with self.subTest(card=card, comune=comune):
                self.assertEqual(identities.read((('card', card), ('comune', comune)))['entries'], ['990006'])

    def test_a_negative_olive_whose_identity_is_unknown(self):
        """The 11200168 shape. A card or COD beside the plant's own monitoring reference is a naming record: row 9
        decides the candidate it names (`protection.named_rows`), and the record attaches through that identity. A
        parcel beside the reference names no entry: the identity stays unknown and the parcel is unchecked. The card
        or COD alone stays unattached, naming the entry and the plant it is a candidate of, unless a record in the
        same run names the plant."""
        rows = copy.deepcopy(self.rows)
        for printed, identity in (([sample(D), tag('990505')], '990005'), ([sample(D), dict(cod='UM990505')], '990005'),
                                  ([sample(D), parcel('23', '400')], 'unknown')):
            with self.subTest(printed=printed):
                result, run = self.art33([decision('d-1', [printed])], plant=D)
                self.assertEqual(run['unattached'], [])
                self.assertEqual(run['plants'][D]['records'], ['d-1'])
                self.assertEqual(result.needs, {NEED['union']})
                self.assertEqual(run['plants'][D]['identity'], dict(
                    identity=identity, references=[D], candidates=['990005'] if identity == 'unknown' else []))
                self.assertEqual(run['plants'][D]['reported'], [] if identity != 'unknown' else [dict(
                    record='d-1', cause='parcel Monopoli fg 23 p.lla 400 not checked: row 9 holds no parcel for a '
                                        'plant whose identity is not an entry')])
        # The parcel the group also prints is not entry 990005's (fg 23 p.lla 400): row 9 does not decide from it
        # (`protection.parcel_agrees`, the reader row 10 holds a parcel to), so the group does not attach, and a
        # record printing only the card stays identity undecided.
        run = self.run_caller([decision('d-1', on(tag('990505'), sample(D), parcel('17', '175'))),
                               lodging('l-1', on(tag('990505')))])
        self.assertEqual(self.causes(run), [('d-1', 1, 'identifiers in conflict'), ('l-1', 1, 'identity undecided')])
        self.assertEqual(run['unattached'][0]['detail'], [
            f'row 9 reads this group as naming entry 990005 for plant {D} and does not decide it: unknown between the '
            'entries within d and "not a register tree": record\'s parcel disagrees: record d-1 (group 1) prints card '
            f'990505 (Monopoli), monitoring reference {D}, parcel Monopoli fg 17 p.lla 175, which names entry 990005 '
            'at 15.0 m, within d 30.55 m'])
        self.assertEqual((run['plants'][D]['identity']['identity'], run['plants'][D]['records']), ('unknown', []))
        # Its own parcel, its comune as the register's folds, agrees.
        run = self.run_caller([decision('d-1', on(tag('990505'), sample(D), parcel('23', '0400', ' MONOPOLI'))),
                               lodging('l-1', on(tag('990505')))])
        self.assertEqual((run['unattached'], run['plants'][D]['records']), ([], ['d-1', 'l-1']))
        # A record printing only the card attaches once a record of the same run names the plant (the plan's
        # "done means" for 11200168 and card 903858), and is identity undecided without one.
        run = self.run_caller([decision('d-1', on(sample(D), tag('990505')), occurred=date(2025, 8, 1)),
                               lodging('l-1', on(tag('990505')))])
        self.assertEqual(run['unattached'], [])
        self.assertEqual(run['plants'][D]['records'], ['d-1', 'l-1'])
        self.assertEqual(self.causes(self.run_caller([lodging('l-1', on(tag('990505')))])),
                         [('l-1', 1, 'identity undecided')])
        # Beside a key naming a decided plant's entry, an undecided one is not the cause.
        run = self.run_caller([decision('d-1', on(tag('990505'), dict(cod=REPEATED)))])
        self.assertEqual(self.causes(run), [('d-1', 1, 'several matches')])
        for printed in ([tag('990505')], [dict(cod='UM990505')], [tag('990505'), parcel('23', '400')]):
            with self.subTest(printed=printed):
                result, run = self.art33([decision('d-1', [printed])], plant=D)
                self.assertEqual(self.causes(run), [('d-1', 1, 'identity undecided')])
                self.assertEqual(run['unattached'][0]['detail'], [
                    f'entry 990005 is no plant\'s row 9 identity; it is a candidate of the "unknown" plants {[D]}'])
                self.assertEqual(result.needs, {NEED['grant'], NEED['union']})
        # A register entry that is not among its candidates names another monumental tree, held as a plant or not:
        # a conflict, named with its distance.
        run = self.run_caller([decision('d-1', on(sample(D), tag('0990404')))])
        self.assertEqual(self.causes(run), [('d-1', 1, 'identifiers in conflict')])
        self.assertEqual(run['unattached'][0]['detail'], [
            f"card 0990404 (Monopoli) names entry 990004, 985.0 m from plant {D}, not within d; row 9's candidates "
            "are ['990005']"])
        self.assertEqual(run['plants'][D]['identity']['identity'], 'unknown')
        # A repeated COD naming another plant's identity entry among others conflicts too.
        run = self.run_caller([decision('d-1', on(sample(D), dict(cod=REPEATED)))])
        self.assertEqual(self.causes(run), [('d-1', 1, 'identifiers in conflict')])
        self.assertEqual(self.rows, rows)

    def test_a_register_entry_against_a_decided_plant_or_one_that_is_not_a_register_tree(self):
        # A is decided as entry 990001 by its note: a card-only record naming entry 990004, though within d of it,
        # is not its identity.
        run = self.run_caller([decision('d-1', on(tag('0990404'), parcel('21', '301')))])
        self.assertEqual(self.causes(run), [('d-1', 1, 'no match')])
        run = self.run_caller([decision('d-1', on(dict(cod=REPEATED), sample(A)))])
        self.assertEqual(self.causes(run), [('d-1', 1, 'identifiers in conflict')])
        self.assertEqual(run['unattached'][0]['detail'], [
            f"COD {REPEATED} names entry 990002; plant {A}'s row 9 identity is entry 990001; "
            f"COD {REPEATED} names entry 990003; plant {A}'s row 9 identity is entry 990001"])
        # The reference with entry 990004's card is a naming record that disagrees with A's note: row 9 leaves A
        # unknown (`protection.identity`), and the group it does not decide does not attach, though 990004 is now
        # among the candidates of an unknown plant. A is 13.0 m from 990004 (x 700002 and 700015); d is 30.55 m.
        run = self.run_caller([decision('d-1', on(sample(A), tag('0990404')))])
        self.assertEqual(self.causes(run), [('d-1', 1, 'identifiers in conflict')])
        rule = ('unknown between the entries within d and "not a register tree": record and note disagree: record d-1 '
                f'(group 1) prints monitoring reference {A}, card 0990404 (Monopoli), which names entry 990004 at '
                '13.0 m, within d 30.55 m; its note prints code 0990101, which names entry 990001')
        self.assertEqual(run['unattached'][0]['detail'], [
            f'row 9 reads this group as naming entry 990004 for plant {A} and does not decide it: {rule}'])
        self.assertEqual(run['plants'][A]['identity']['identity'], 'unknown')
        self.assertEqual(run['plants'][A]['records'], [])
        # A record naming A's note entry for another plant (C's reference beside entry 990001's COD; C lies 28 km
        # away) leaves A unknown, as two notes printing one code do: a decision printing only that COD names an
        # entry of an unknown plant, and attaches to no plant.
        run = self.run_caller([lodging('l-1', on(sample(C), dict(cod='990101_21_300_072030'))),
                               decision('d-2', on(dict(cod='990101_21_300_072030')))])
        self.assertEqual(self.causes(run), [('l-1', 1, 'identifiers in conflict'), ('d-2', 1, 'identity undecided')])
        self.assertEqual((run['plants'][A]['identity']['identity'], run['plants'][A]['records']), ('unknown', []))
        # C has no entry within d: any register entry disagrees with row 9, named with its distance.
        run = self.run_caller([decision('d-1', on(sample(C), tag('990505')))])
        self.assertEqual(self.causes(run), [('d-1', 1, 'identifiers in conflict')])
        detail = run['unattached'][0]['detail'][0]
        self.assertTrue(detail.startswith('card 990505 (Monopoli) names entry 990005, ') and
                        detail.endswith(f' m from plant {C}; row 9 found no entry within d of it'), detail)
        # A parcel is checked through a decided plant's entry; for any other plant it neither blocks nor decides.
        self.assertEqual(self.run_caller([decision('d-1', on(sample(A), parcel('21', '300')))])['plants'][A]['records'],
                         ['d-1'])
        run = self.run_caller([decision('d-1', on(sample(A), parcel('21', '301')))])
        self.assertEqual(run['unattached'][0]['detail'], [
            f"parcel Monopoli fg 21 p.lla 301 is not the parcel of entry 990001, plant {A}'s row 9 identity"])
        self.assertEqual(self.run_caller([decision('d-1', on(sample(C), parcel('9', '9')))])['plants'][C]['records'],
                         ['d-1'])
        # An identity entry that prints no parcel cannot be held to one: the parcel is reported unchecked, naming why.
        register = [dataclasses.replace(e, particella=' ') if e.oid == '990001' else e for e in REGISTER]
        run = landscape_results(self.s, AT, [A], [decision('d-1', on(sample(A), parcel('21', '301')))],
                                evaluated_at=CUTOFF, permitted_controlled_sources=GRANT, rows=self.rows,
                                register=register, zone=ROME, calendar=national_calendar())
        self.assertEqual((run['plants'][A]['records'], run['plants'][A]['reported']), (['d-1'], [dict(
            record='d-1', cause='parcel Monopoli fg 21 p.lla 301 not checked: entry 990001 prints no parcel it can be '
                                'held to')]))

    def test_a_record_naming_several_plants_attaches_each_group_on_its_own(self):
        run = self.run_caller([decision('d-3', [[sample(A)], [tag('0990202')], [sample(C)]])])
        for plant in (A, B, C):
            self.assertIs(run['plants'][plant]['facts'][RULE][GRANTED], True)
            self.assertEqual(run['plants'][plant]['records'], ['d-3'])
        self.assertEqual(run['unattached'], [])
        run = self.run_caller([decision('d-3', [[sample(A)], [tag('990505')], [sample('9199999')]])])
        self.assertIs(run['plants'][A]['facts'][RULE][GRANTED], True)
        self.assertEqual(self.causes(run), [('d-3', 2, 'identity undecided'), ('d-3', 3, 'no match')])
        self.assertNotIn(GRANTED, run['plants'][D]['facts'][RULE])
        # Two of a record's groups that are one plant in row 9 attach once, and the disagreement is reported.
        run = self.run_caller([decision('d-2', [[sample(A)], [tag('0990101')]])])
        self.assertEqual(run['plants'][A]['records'], ['d-2'])
        self.assertEqual(run['plants'][A]['reported'], [dict(record='d-2', cause='its groups 1 and 2 both attach to '
                                                                                  'this plant')])

    def test_records_attached_elsewhere_and_monitoring_references_asked_as_plants(self):
        supplied = [decision('d-g', on(sample('9100006'))), decision('d-e', on(sample('9100005')))]
        run = self.run_caller(supplied, plants=(A, '9100006', '9100005'))
        self.assertEqual(run['elsewhere'], [dict(record='d-g', kind='landscape-decision', occurred=DECIDED, plant=G)])
        self.assertEqual(self.causes(run), [('d-e', 1, 'several matches')])
        self.assertEqual(run['unattached'][0]['identifiers'][0]['plants'], [E1, E2])
        for asked, plants in (('9100006', [G]), ('9100005', [E1, E2])):
            item = run['plants'][asked]
            self.assertEqual(item['identity']['identity'], "not in PR #30's rows")
            self.assertEqual(item['reported'], [dict(plants=plants, cause=f"not a plant in PR #30's rows: a monitoring "
                                                                          f'reference of plants {plants}')])
        # Asked about, G gets the grant; nothing is listed elsewhere.
        run = self.run_caller(supplied, plants=(G,))
        self.assertIs(run['plants'][G]['facts'][RULE][GRANTED], True)
        self.assertEqual(run['elsewhere'], [])

    def test_art_146_5_and_146_8_move_with_the_proceeding_records(self):
        def rows(supplied):
            return self.run_caller(supplied)['plants'][A]['results']
        both = rows([lodging('l-1', on(sample(A))), route('r-1', on(sample(A)))])
        self.assertIs(both[DECISION].truth, True)
        self.assertEqual(self.run_caller([route('r-1', on(sample(A)))])['plants'][A]['opinion_route']['route'],
                         "parere della Soprintendenza ai sensi dell'art. 146, c. 8")
        self.assertEqual(both[DECISION].effect, self.s.version(DECISION, AT)['true_effect'])
        for complete in (None, False):
            with self.subTest(complete=complete):
                stated = self.run_caller([lodging('l-1', on(sample(A)), complete), route('r-1', on(sample(A)))])
                self.assertIsNone(stated['plants'][A]['results'][DECISION].truth)
                self.assertEqual(stated['plants'][A]['results'][DECISION].needs, {EDGE})
                self.assertEqual(stated['plants'][A]['due'], DUE)
                self.assertEqual(stated['plants'][A]['performances'], {})
        alone = rows([lodging('l-1', on(sample(A)))])
        self.assertEqual(alone[DECISION].needs, {ROUTE_NEED})
        unresolved = rows([lodging('l-1', on(sample(A))), route('r-1', on(sample(A)), resolved=False)])
        self.assertIs(unresolved[DECISION].truth, False)
        # The latest route stated decides; one day's records that differ supply nothing.
        later = rows([lodging('l-1', on(sample(A))), route('r-0', on(sample(A)), False, date(2025, 7, 20)),
                      route('r-1', on(sample(A)))])
        self.assertIs(later[DECISION].truth, True)
        split = self.run_caller([lodging('l-1', on(sample(A))), route('r-0', on(sample(A)), False),
                                 route('r-1', on(sample(A)))])['plants'][A]
        self.assertEqual(split['results'][DECISION].needs, {ROUTE_NEED})
        self.assertIn('the caller does not choose', split['reported'][0]['cause'])

    def test_art_146_8_moves_only_with_acts_received_stated_complete(self):
        def run(supplied):
            return self.run_caller(supplied)['plants'][A]
        self.assertEqual(run([])['results'][OPINION].needs, {RECEIPT_NEED})
        complete = run([received('a-1', on(sample(A)))])
        self.assertIs(complete['results'][OPINION].truth, True)
        self.assertEqual(complete['results'][OPINION].effect, self.s.version(OPINION, AT)['true_effect'])
        self.assertEqual(complete['receipts'], [dict(record='a-1', document='FIXTURE protocol a-1',
                                                     occurred=date(2025, 6, 24), recipient=SUPERINTENDENT,
                                                     complete=True)])
        for stated in (None, False):
            with self.subTest(complete=stated):
                item = run([received('a-1', on(sample(A)), stated)])
                self.assertEqual(item['results'][OPINION].needs, {RECEIPT_NEED})
                self.assertNotIn(RECEIVED, item['facts'][OPINION])
        # The latest day's receipts decide; one day's that disagree supply nothing.
        self.assertEqual(run([received('a-1', on(sample(A))), received('a-2', on(sample(A)), None,
                                                                         date(2025, 6, 30))])['results'][OPINION].needs,
                         {RECEIPT_NEED})
        later = run([received('a-1', on(sample(A)), False), received('a-2', on(sample(A)), True, date(2025, 6, 30))])
        self.assertIs(later['results'][OPINION].truth, True)
        split = run([received('a-1', on(sample(A))), received('a-2', on(sample(A)), None)])
        self.assertEqual(split['results'][OPINION].needs, {RECEIPT_NEED})
        self.assertEqual(split['reported'], [dict(records=['a-1', 'a-2'], cause='records of 2025-06-24 state different '
                                                                                'values; the caller does not choose')])

    def test_lodging_completeness_follows_the_latest_days_lodgings(self):
        def item(supplied):
            return self.run_caller(supplied + [route('r-1', on(sample(A)))])['plants'][A]
        earlier_complete = item([lodging('l-1', on(sample(A))), lodging('l-2', on(sample(A)), None, date(2025, 6, 20))])
        self.assertEqual(earlier_complete['results'][DECISION].needs, {EDGE})
        later_complete = item([lodging('l-1', on(sample(A)), None), lodging('l-2', on(sample(A)), True,
                                                                             date(2025, 6, 20))])
        self.assertIs(later_complete['results'][DECISION].truth, True)
        same_day = item([lodging('l-1', on(sample(A))), lodging('l-2', on(sample(A)), None)])
        self.assertEqual(same_day['results'][DECISION].needs, {EDGE})
        self.assertIn(dict(records=['l-1', 'l-2'], cause='records of 2025-06-17 state different values; the caller '
                                                         'does not choose'), same_day['reported'])
        self.assertEqual([(lg['record'], lg['recipient'], lg['complete']) for lg in same_day['lodgings']],
                         [('l-1', AUTHORITY, True), ('l-2', AUTHORITY, None)])

    def test_a_lodging_anchors_the_45_day_clock_and_its_lapse_grants_nothing(self):
        run = self.run_caller([lodging('l-1', on(sample(A)))], upstream={A: SETTLED})
        plant = run['plants'][A]
        self.assertEqual(plant['due'], DUE)
        self.assertGreater(AT, DUE.date())
        self.assertEqual(plant['results'][RULE].needs, {NEED['grant'], NEED['union']})
        self.assertIsNone(self.run_caller([])['plants'][A]['due'])
        # Lodgings at two moments: the caller anchors neither.
        two = self.run_caller([lodging('l-1', on(sample(A)), None),
                               lodging('l-2', on(sample(A)), True, date(2025, 6, 20))])
        self.assertIsNone(two['plants'][A]['due'])
        self.assertEqual(two['plants'][A]['reported'][0]['cause'],
                         'lodgings at different moments; the 45-day clock is not anchored')
        # A lodging dated after the evaluation date does not anchor it, nor stop the earlier one anchoring it.
        late = [lodging('l-9', on(sample(A)), True, AFTER)]
        self.assertIsNone(self.run_caller(late)['plants'][A]['due'])
        self.assertEqual(self.run_caller([lodging('l-1', on(sample(A)))] + late)['plants'][A]['due'], DUE)
        # A clock the held calendar cannot count is reported, never guessed: it ends on 24 February 2027, after
        # the national calendar's bound.
        late = self.run_caller([lodging('l-1', on(sample(A)), occurred=date(2027, 1, 10))], at=date(2027, 3, 1),
                               evaluated_at=datetime(2027, 3, 1, 12, tzinfo=ROME))
        self.assertIsNone(late['plants'][A]['due'])
        self.assertIn('the 45-day clock is not counted', late['plants'][A]['reported'][0]['cause'])

    def test_a_grant_changes_nothing_else_about_the_plant_or_any_other(self):
        base = [lodging('l-1', on(sample(A))), route('r-1', on(sample(A))), received('a-1', on(sample(A))),
                decision('d-c', on(sample(C)), 'denied')]
        without = self.run_caller(base, upstream={A: SETTLED})
        granted = self.run_caller(base + [decision('d-1', on(tag('0990101')))], upstream={A: SETTLED})
        for row in (DECISION, OPINION):
            self.assertEqual(granted['plants'][A]['results'][row], without['plants'][A]['results'][row])
        self.assertEqual(granted['plants'][A]['due'], without['plants'][A]['due'])
        for plant in (B, C, D):
            self.assertEqual(granted['plants'][plant], without['plants'][plant])
        self.assertEqual(without['plants'][A]['results'][RULE].needs, {NEED['grant'], NEED['union']})
        self.assertEqual(granted['plants'][A]['results'][RULE].needs, {NEED['union']})

    def test_records_dated_after_the_evaluation_date_are_reported_not_passed(self):
        empty = self.run_caller([], upstream={A: SETTLED})['plants'][A]
        for late in (decision('x-1', on(sample(A)), occurred=AFTER), route('x-1', on(sample(A)), occurred=AFTER),
                     received('x-1', on(sample(A)), occurred=AFTER), lodging('x-1', on(sample(A)), occurred=AFTER)):
            with self.subTest(kind=late['kind']):
                item = self.run_caller([late], upstream={A: SETTLED})['plants'][A]
                self.assertEqual(item['results'], empty['results'])
                self.assertEqual((item['due'], item['records']), (None, ['x-1']))
                self.assertEqual(item['reported'], [dict(record='x-1', cause='dated 2025-09-02, after the evaluation '
                                                                             'date; not passed to C')])

    def test_the_run_states_its_cutoff_and_grant(self):
        options = dict(rows=self.rows, register=REGISTER, zone=ROME, calendar=national_calendar())
        for missing in ('evaluated_at', 'permitted_controlled_sources'):
            stated = dict(evaluated_at=CUTOFF, permitted_controlled_sources=GRANT)
            stated.pop(missing)
            with self.subTest(missing=missing), self.assertRaises(TypeError):
                landscape_results(self.s, AT, [A], [], **stated, **options)
        with self.assertRaises(TypeError):
            self.run_caller([], grant={'f' * 64})
        # The landscape family is admitted by main's rule, and names no order.
        from cordon_d.case_prescriptions import admitted_records
        admit = dict(evaluated_at=CUTOFF, permitted_controlled_sources=GRANT, zone=ROME, family='landscape')
        self.assertEqual([r['record'] for r in admitted_records([lodging('l-1', on(sample(A)))], None, **admit)[0]],
                         ['l-1'])
        with self.assertRaisesRegex(ValueError, 'Landscape records name no order'):
            admitted_records([lodging('l-1', on(sample(A)))], 'REG-PUGLIA-U181-DIR-2025-00115', **admit)
        # A record dated after the cutoff was not held at it: the set is refused, granted or not.
        for late in (decision('d-late', on(sample(A)), occurred=date(2025, 10, 1)),
                     ungranted(lodging('l-late', on(sample('9199999')), occurred=date(2025, 10, 1)))):
            with self.subTest(record=late['record']), \
                    self.assertRaisesRegex(ValueError, f"Record {late['record']} .* states occurred 2025-10-01, later "
                                                       'than the evaluation'):
                self.run_caller([decision('d-1', on(sample(A))), late])

    def test_an_ungranted_record_withholds_what_it_could_change_and_shows_nothing_else(self):
        empty = self.run_caller([], upstream={A: SETTLED})['plants'][A]
        withheld = ungranted(decision('d-x', on(sample(A)), 'denied'))
        run = self.run_caller([decision('d-1', on(sample(A))), withheld], upstream={A: SETTLED})
        item = run['plants'][A]
        self.assertIsNone(item['results'][RULE].truth)
        self.assertEqual(item['results'][RULE].needs, {need(withheld)})
        self.assertEqual(item['withheld'], {RULE: [need(withheld)]})
        for row in (DECISION, OPINION):
            self.assertEqual(item['results'][row], empty['results'][row])
        self.assertEqual(item['records'], ['d-1'])
        self.assertEqual(run['ungranted'], [dict(record='d-x', kind='landscape-decision', need=need(withheld))])
        # With an empty grant, the granted decision is withheld too.
        run = self.run_caller([decision('d-1', on(sample(A)))], upstream={A: SETTLED}, grant=frozenset())
        self.assertEqual(run['plants'][A]['results'][RULE].needs,
                         {'authorized evidence for landscape-decision record d-1'})
        # An ungranted lodging withholds 146(5) and the clock; Art. 33(1) and 146(8) keep their answers.
        lodged = ungranted(lodging('l-x', on(sample(A))))
        item = self.run_caller([decision('d-1', on(sample(A))), received('a-1', on(sample(A))), lodged],
                               upstream={A: SETTLED})['plants'][A]
        self.assertEqual((item['results'][DECISION].needs, item['due']), ({need(lodged)}, None))
        self.assertEqual(item['withheld'], {DECISION: [need(lodged)], 'due': [need(lodged)]})
        self.assertEqual(item['results'][RULE].needs, {NEED['union']})
        self.assertIs(item['results'][OPINION].truth, True)
        # One dated after the evaluation date could change nothing at it, and withholds nothing.
        item = self.run_caller([decision('d-1', on(sample(A))), ungranted(decision('d-y', on(sample(A)), 'denied',
                                                                                   occurred=AFTER))],
                               upstream={A: SETTLED})['plants'][A]
        self.assertEqual((item['results'][RULE].needs, item['withheld']), ({NEED['union']}, {}))
        # An ungranted record that could change A's row 9 identity (its reference beside entry 990004's card, which
        # would make A's note-decided identity unknown) withholds every result for A: each record attaches through it.
        # A granted grant printing A's identity card still attaches, and decides nothing.
        doubt = ungranted(lodging('l-z', on(sample(A), tag('0990404'))))
        item = self.run_caller([decision('d-1', on(tag('0990101'))), doubt], upstream={A: SETTLED})['plants'][A]
        self.assertEqual(item['records'], ['d-1'])
        self.assertEqual({row: item['results'][row].needs for row in (RULE, DECISION, OPINION)},
                         {row: {need(doubt)} for row in (RULE, DECISION, OPINION)})
        self.assertIsNone(item['due'])
        # Nothing of an ungranted record is shown beyond its name, kind and need: not where it attaches, nor why
        # it does not.
        run = self.run_caller([ungranted(decision('d-g', on(sample('9100006')))),
                               ungranted(decision('d-u', on(tag('990505'))))])
        self.assertEqual((run['elsewhere'], run['unattached']), ([], []))
        self.assertEqual([u['record'] for u in run['ungranted']], ['d-g', 'd-u'])
        self.assertEqual(run['plants'][D]['withheld'], {})

    def test_refusals(self):
        clause = ("Di attivare la richiesta dell'autorizzazione paesaggistica di cui all'articolo 146 del decreto "
                  'legislativo 22 gennaio 2004, n. 42, esclusivamente per gli ulivi riconosciuti ufficialmente '
                  'monumentali e risultati non infetti alle analisi di laboratorio')
        # No requirement kind, either way, and the order's clause is not a record of any kind.
        for kind, fields in (('landscape-requirement', dict(required=True)),
                             ('landscape-requirement', dict(required=False)),
                             ('requirement', dict(required=True)),
                             ('order-clause', dict(text=clause, required=True)),
                             ('order-clause', dict(text=clause, required=False)),
                             ('pptr-designation', dict(designation='BP - Territori costieri')),
                             ('grove-constraint', dict(grove='uliveto monumentale, L.R. 14/2007 art. 6, c. 1')),
                             ('landscape-acts-sent', dict(complete=True, recipient=SUPERINTENDENT)),
                             ('personal-delivery', {}), ('posting', {})):
            with self.subTest(kind=kind, fields=fields), self.assertRaises(ValueError):
                self.run_caller([record('x-1', kind, on(sample(A)), LODGED, **fields)])
        # A record names its plants as groups of the identifiers it prints for each, in the forms PR #30's
        # identity reads.
        for plants in ([], [[]], [sample(A)], on(dict(oid='990001')), on(dict(card='0990101')), on(dict(sample=' ')),
                       [[sample(A)], []]):
            with self.subTest(plants=plants), self.assertRaises(ValueError):
                self.run_caller([lodging('l-1', plants)])
        # Nothing rides along on a record: no requirement, PPTR or grove value, no predicate.
        for extra in (dict(required=True), dict(required=False), dict(requires_authorization=True),
                      dict(designation='BP'), dict(grove=True), dict(granted=True), dict(complete_from='2025-06-17'),
                      dict(issuer=AUTHORITY)):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                self.run_caller([dict(lodging('l-1', on(sample(A))), **extra)])
        for missing in ('recipient', 'complete'):
            with self.subTest(missing=missing), self.assertRaises(ValueError):
                item = received('a-1', on(sample(A)))
                item.pop(missing)
                self.run_caller([item])
        # A decision states its outcome, intervention kind and conditions consistently.
        for bad in (dict(outcome='pending'), dict(outcome='silent-consent'), dict(intervention_kind='transplant'),
                    dict(outcome='granted-with-conditions', conditions=[]),
                    dict(outcome='granted', conditions=['una condizione']), dict(outcome='denied', conditions=['x']),
                    dict(issuer=' '), dict(issuer=1)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.run_caller([dict(decision('d-1', on(sample(A))), **bad)])
        for bad in (dict(complete='sì'), dict(complete=1), dict(recipient=''), dict(recipient=['a'])):
            for build in (lodging, received):
                with self.subTest(bad=bad, kind=build.__name__), self.assertRaises(ValueError):
                    self.run_caller([dict(build('l-1', on(sample(A))), **bad)])
        with self.assertRaises(ValueError):
            self.run_caller([dict(route('r-1', on(sample(A))), resolved=None)])
        with self.assertRaises(ValueError):
            self.run_caller([dict(lodging('l-1', on(sample(A))), occurred='2025-06-17T10:00:00')])
        # The caller sets no predicate a record does not state: not Union obligations, the grant, the route, the
        # receipt, nor either Art. 146(2) predicate (a PPTR designation or a grove constraint among them).
        for predicate in (UNION, GRANTED, ROUTE, RECEIVED, 'the property or area has legally protected landscape status',
                          'the proposed intervention requires landscape authorization', EDGE):
            with self.subTest(predicate=predicate), self.assertRaises(ValueError):
                self.run_caller([], upstream={A: {predicate: True}})
        with self.assertRaises(ValueError):
            self.run_caller([], plants=(A,), upstream={B: SETTLED})
        for option in ('facts', 'performances', 'designation', 'grove', 'required', 'granted'):
            with self.subTest(option=option), self.assertRaises(TypeError):
                self.run_caller([], **{option: True})
        # A landscape record is not a removal order's record.
        with self.assertRaises(ValueError):
            supplied_records([lodging('l-1', on(sample(A)))])

    def test_the_cli_caller_emits_Cs_results_as_C_returns_them(self):
        sys.path.insert(0, str(ROOT / 'scripts'))
        import read_landscape
        supplied = [lodging('l-1', on(sample(A))), received('a-1', on(sample(A))),
                    decision('d-1', on(tag('0990101')), 'granted-with-conditions',
                             conditions=['Reimpianto entro 90 giorni.']),
                    decision('d-cod', on(dict(cod=REPEATED))), decision('d-g', on(sample('9100006')))]
        run = dict(at=AT, known_through=CUTOFF, permitted_controlled_sources=GRANT)
        out = read_landscape.results(self.s, run, [A, C], supplied, self.rows, REGISTER)
        json.dumps(out)
        a = out['plants'][A]
        self.assertEqual(a['results'][RULE]['needs'], sorted(set(NEED.values()) - {NEED['grant']}))
        self.assertIsNone(a['results'][RULE]['truth'])
        self.assertEqual((a['decision']['occurred'], a['decision']['conditions'], a['decision']['issuer'], a['due']),
                         (DECIDED.isoformat(), ['Reimpianto entro 90 giorni.'], AUTHORITY, DUE.isoformat()))
        self.assertEqual((a['lodgings'][0]['recipient'], a['receipts'][0]['recipient']), (AUTHORITY, SUPERINTENDENT))
        self.assertEqual(out['plants'][C]['results'][RULE]['needs'], sorted(NEED.values()))
        self.assertEqual([(u['record'], u['cause']) for u in out['unattached']], [('d-cod', 'several matches')])
        self.assertEqual(out['elsewhere'], [dict(record='d-g', kind='landscape-decision', occurred=DECIDED.isoformat(),
                                                 plant=G)])
        self.assertEqual((out['evaluated_at'], out['permitted_controlled_sources']),
                         (CUTOFF.isoformat(), sorted(GRANT)))
        # The command requires the run's cutoff and grant, the grant stated even when empty; the arguments are
        # refused before the store is reached.
        stated = ['read_landscape.py', '--records', '/nonexistent.json', '--plants', A, '--at', AT.isoformat()]
        for argv, refused in ((stated + ['--known-through', CUTOFF.isoformat(), '--permitted-controlled-sources'],
                               False),
                              (stated + ['--permitted-controlled-sources'], True),
                              (stated + ['--known-through', CUTOFF.isoformat()], True),
                              (stated + ['--known-through', '2025-09-30T18:00:00', '--permitted-controlled-sources'],
                               True)):
            with self.subTest(argv=argv[7:]), mock.patch.object(sys, 'argv', argv), mock.patch('sys.stderr'), \
                    mock.patch.object(read_landscape, 'store_root', side_effect=LookupError('parsed')), \
                    self.assertRaises(SystemExit if refused else LookupError):
                read_landscape.main()

    def test_verify_holds_the_landscape_path_to_the_run_inputs(self):
        verify.verify()

        def cutoff_defaulted(snapshot, at, plants, supplied, *, permitted_controlled_sources, rows, register, zone,
                             calendar, upstream=None, evaluated_at=CUTOFF):
            raise AssertionError('not called')

        def grant_defaulted(snapshot, at, plants, supplied, *, evaluated_at, rows, register, zone, calendar,
                            upstream=None, permitted_controlled_sources=frozenset()):
            raise AssertionError('not called')
        for name, fake in (('evaluated_at', cutoff_defaulted), ('permitted_controlled_sources', grant_defaulted)):
            with self.subTest(name=name), mock.patch.object(landscape, 'landscape_results', fake), \
                    self.assertRaisesRegex(ValueError, f'{name} has a default on cordon_d.landscape.landscape_results'):
                verify.verify()


if __name__ == '__main__':
    unittest.main()
