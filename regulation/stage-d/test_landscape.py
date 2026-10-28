"""Row 10: the landscape proceeding's record reaches C's Art. 33(1), 146(5) and 146(8) through the ordinary caller.

Every record, register entry and monitoring plant here is a FIXTURE (`fixture: true`, identifiers 99xxxxx and
91xxxxx): invented in the shape PR #30 shows for positive 1606667, entry 340453 (COD 107007_17_159_072030, card
0107007, MONOPOLI fg 17 p.lla 159) and the census tag 0107007 its note prints. None is a fact about a real plant
or proceeding. PR #30's identity is computed by PR #30's own functions (`protection.note_codes`,
`protection.candidates`) over the fixture register; the attachment reads only that identity.

Expected needs are the strings the probe of C's rows returned (PR #37's plan), written out here, not taken from the
code under test. The clock's end is counted by hand: 45 calendar days from Tuesday 17 June 2025 end on Friday
1 August 2025, so C's exclusive boundary is 2 August 00:00 in Rome.
"""
from datetime import date, datetime
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from zoneinfo import ZoneInfo

from cordon_c.core import Snapshot, evaluate
from cordon_d import protection
from cordon_d.calendar import national_calendar
from cordon_d.case_prescriptions import supplied_records
from cordon_d.landscape import (APPLICATION, DECISION, GRANTED, OPINION, RECEIVED, ROUTE, RULE, UNION, UPSTREAM,
                                landscape_results)

ROOT = Path(__file__).resolve().parents[2]
ROME = ZoneInfo('Europe/Rome')
AT = date(2025, 9, 1)
LODGED = date(2025, 6, 17)
DUE = datetime(2025, 8, 2, tzinfo=ROME)
DECIDED = date(2025, 8, 20)
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
# The plants. A is the 1606667 shape: a monitored olive whose note prints the census tag of the one entry it is, with
# another entry within d. B's entry shares its COD with an entry elsewhere. C is not a register tree.
A, B, C = '9100001', '9100002', '9100003'
REPEATED = '990202_22_310_072030'


def entry(oid, key, card, foglio, particella, x, y):
    return protection.Entry('listed', oid, key, card, 'DGR 357/2012', None, 'MONOPOLI', foglio, particella, x, y,
                            date(2012, 11, 13), 'e' * 64)


REGISTER = [entry('990001', '990101_21_300_072030', '0990101', '21', '300', 700000.0, 4500000.0),
            entry('990004', '990404_21_301_072030', '0990404', '21', '301', 700015.0, 4500000.0),
            entry('990002', REPEATED, '0990202', '22', '310', 700500.0, 4500000.0),
            entry('990003', REPEATED, '0990303', '22', '311', 705000.0, 4505000.0)]
PLANTS = {A: ('MONOPOLI', 700002.0, 4500000.0, ('sintomi assenti. pianta monumentale censita targhetta n. 0990101',)),
          B: ('MONOPOLI', 700501.0, 4500000.0, ('pianta monumentale targhetta n. 0990202',)),
          C: ('MONOPOLI', 720000.0, 4520000.0, ())}
ERROR_M, BOUND = 7.4, SimpleNamespace(error_m=23.15)


def pr30_rows():
    """PR #30's rows for the fixture plants, with the identity its own note-code rule and candidates give."""
    codes = protection.note_codes(PLANTS, REGISTER, lambda plant, e: ERROR_M + BOUND.error_m)
    rows = []
    for plant, (comune, x, y, notes) in PLANTS.items():
        named = [c for c in codes if c.plant == plant]
        cand = protection.candidates(plant, x, y, ERROR_M, REGISTER, lambda e: BOUND, named)
        rows.append(dict(plant=plant, kind='negative olive', order=None, coincides_with=[], comune=comune,
                         observations=[[plant, '2025-05-12']],
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


def decision(name, plants, outcome='granted', occurred=DECIDED, kind='removal', conditions=()):
    return record(name, 'landscape-decision', plants, occurred, outcome=outcome, intervention_kind=kind,
                  intervention="espianto dell'ulivo monumentale non infetto ai sensi dell'art. 33, c. 1",
                  procedure='procedimento ordinario, art. 146 D.lgs. 42/2004', conditions=list(conditions))


def lodging(name, plants, complete=True, occurred=LODGED):
    return record(name, 'landscape-lodging', plants, occurred, complete=complete)


def route(name, plants, resolved=True, occurred=date(2025, 7, 30)):
    return record(name, 'landscape-opinion-route', plants, occurred, resolved=resolved,
                  route='parere della Soprintendenza ai sensi dell\'art. 146, c. 8')


def received(name, plants, occurred=date(2025, 6, 24)):
    return record(name, 'landscape-acts-received', plants, occurred)


# The owning units' values for Art. 33(1)'s three upstream conjuncts (FIXTURES).
SETTLED = {UPSTREAM[0]: True, UPSTREAM[1]: True, UPSTREAM[2]: False}


class LandscapeRecords(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Snapshot.load(ROOT)
        cls.rows = pr30_rows()
        identities = {p['plant']: p['candidates']['identity'] for p in cls.rows['plants']}
        # PR #30's identity, from its own rules: A is entry 990001 only through its tag (990004 is also within d).
        assert identities == {A: '990001', B: '990002', C: 'not a register tree'}, identities
        assert {e['entry'] for p in cls.rows['plants'] if p['plant'] == A for e in p['candidates']['entries']} == \
            {'990001', '990004'}

    def run_caller(self, supplied, plants=(A, B, C), at=AT, upstream=None, **options):
        return landscape_results(self.s, at, list(plants), supplied, rows=self.rows, register=REGISTER, zone=ROME,
                                 calendar=national_calendar(), upstream=upstream, **options)

    def art33(self, supplied, plant=A, settled=True, at=AT):
        run = self.run_caller(supplied, at=at, upstream={plant: SETTLED} if settled else None)
        return run['plants'][plant]['results'][RULE], run

    def test_a_plant_with_no_record_gets_Cs_unknown_with_the_probed_needs(self):
        run = self.run_caller([])
        for plant in (A, B, C):
            result = run['plants'][plant]['results'][RULE]
            self.assertIsNone(result.truth)
            self.assertEqual(result.needs, set(NEED.values()))
        result, _ = self.art33([])
        self.assertIsNone(result.truth)
        self.assertEqual(result.needs, {NEED['grant'], NEED['union']})
        # An upstream conjunct not supplied adds its need as C lists it.
        partial = self.run_caller([], upstream={A: {UPSTREAM[0]: True, UPSTREAM[2]: False}})
        self.assertEqual(partial['plants'][A]['results'][RULE].needs, {NEED['grant'], NEED['union'], NEED['status']})
        self.assertEqual(run['unattached'], [])
        self.assertIn(UNION, run['not_supplied'])
        self.assertIn(APPLICATION, run['not_supplied'])
        # The caller evaluates exactly the three rows; Art. 146(2) is not among them.
        self.assertEqual(set(run['plants'][A]['results']), {RULE, DECISION, OPINION})

    def test_a_grant_fills_the_conjunct_from_the_decisions_date_with_its_procedure_and_conditions(self):
        for outcome, conditions in (('granted', ()), ('granted-with-conditions',
                                                       ('Il reimpianto di un ulivo della stessa cultivar entro 90 '
                                                        'giorni.', 'La conservazione del materiale legnoso.'))):
            with self.subTest(outcome=outcome):
                result, run = self.art33([decision('d-1', [sample(A)], outcome, conditions=conditions)])
                self.assertIsNone(result.truth)
                self.assertEqual(result.needs, {NEED['union']})
                plant = run['plants'][A]
                self.assertIs(plant['facts'][RULE][GRANTED], True)
                self.assertEqual(plant['decision']['occurred'], DECIDED)
                self.assertEqual(plant['decision']['procedure'], 'procedimento ordinario, art. 146 D.lgs. 42/2004')
                self.assertEqual(plant['decision']['conditions'], list(conditions))
                self.assertTrue(plant['fixture'])
                # From the decision's date: the day before, the grant is still C's need.
                before, _ = self.art33([decision('d-1', [sample(A)], outcome, conditions=conditions)],
                                       at=date(2025, 8, 19))
                self.assertEqual(before.needs, {NEED['grant'], NEED['union']})
                # What the caller passed, with the Union value no D reader supplies, opens C's route.
                facts = {(V33, p): v for p, v in plant['facts'][RULE].items()} | {(V33, UNION): True}
                self.assertEqual(evaluate(self.s, RULE, AT, facts).effect, self.s.versions[V33]['true_effect'])

    def test_a_denial_makes_it_false(self):
        for settled in (True, False):
            result, _ = self.art33([decision('d-1', [sample(A)], 'denied')], settled=settled)
            self.assertIs(result.truth, False)
            self.assertEqual(result.effect, self.s.versions[V33]['false_effect'])

    def test_nothing_but_a_decision_for_the_plant_and_its_removal_fills_the_grant(self):
        for name, supplied in (
                ('an opinion alone', [route('r-1', [sample(A)])]),
                ('a pending application', [lodging('l-1', [sample(A)]), received('a-1', [sample(A)])]),
                ('a replant-only consent', [decision('d-1', [sample(A)], kind='replanting-only')]),
                ('a grant for another project', [decision('d-1', [sample(A)], kind='other')]),
                ('a grant for another plant', [decision('d-1', [sample(C)])])):
            with self.subTest(name):
                result, run = self.art33(supplied)
                self.assertIsNone(result.truth)
                self.assertEqual(result.needs, {NEED['grant'], NEED['union']})
                self.assertNotIn(GRANTED, run['plants'][A]['facts'][RULE])
        _, run = self.art33([decision('d-1', [sample(A)], kind='replanting-only')])
        self.assertIn('not this removal; it fills nothing', run['plants'][A]['reported'][0]['cause'])
        # The grant for C fills C's grant, not A's.
        run = self.run_caller([decision('d-1', [sample(C)])])
        self.assertIs(run['plants'][C]['facts'][RULE][GRANTED], True)

    def test_a_decision_printing_the_card_or_tag_attaches_through_PR30s_identity(self):
        for printed in ([tag('0990101')], [tag('990101', 'MONOPOLI ')], [dict(cod='990101_21_300_072030')],
                        [tag('0990101'), dict(comune='Monopoli', foglio='21', particella='300')]):
            with self.subTest(printed=printed):
                result, run = self.art33([decision('d-tag', printed)])
                self.assertEqual(run['unattached'], [])
                self.assertEqual(run['plants'][A]['records'], ['d-tag'])
                self.assertEqual(result.needs, {NEED['union']})
        # The neighbouring entry's tag names its own entry, which is no plant's identity: no match.
        run = self.run_caller([decision('d-tag', [tag('0990404')])])
        self.assertEqual(run['unattached'][0]['cause'], 'no match')
        self.assertEqual(run['plants'][A]['results'][RULE].needs, set(NEED.values()))

    def test_a_repeated_cod_stays_unattached_and_fills_nothing(self):
        empty = self.run_caller([], upstream={B: SETTLED})
        run = self.run_caller([decision('d-cod', [dict(cod=REPEATED)])], upstream={B: SETTLED})
        self.assertEqual([(u['record'], u['cause']) for u in run['unattached']], [('d-cod', 'several matches')])
        self.assertEqual(run['unattached'][0]['identifiers'][0]['entries'], ['990002', '990003'])
        for plant in (A, B, C):
            self.assertEqual(run['plants'][plant]['results'], empty['plants'][plant]['results'])
            self.assertEqual(run['plants'][plant]['records'], [])
        # The same COD qualifies B's tag, since B's entry is one of the entries it names.
        run = self.run_caller([decision('d-cod', [dict(cod=REPEATED), tag('0990202')])], upstream={B: SETTLED})
        self.assertEqual(run['plants'][B]['records'], ['d-cod'])

    def test_unattached_causes(self):
        for printed, cause in (([sample('9199999')], 'no match'),
                               ([tag('0990101'), sample(C)], 'identifiers in conflict'),
                               ([tag('0990101'), dict(comune='Monopoli', foglio='22', particella='310')],
                                'identifiers in conflict'),
                               ([dict(comune='Monopoli', foglio='21', particella='300')], 'several matches'),
                               ([tag('0990101', 'Fasano')], 'no match')):
            with self.subTest(printed=printed):
                run = self.run_caller([decision('d-x', printed)])
                self.assertEqual([u['cause'] for u in run['unattached']], [cause])
                self.assertTrue(all(run['plants'][p]['records'] == [] for p in (A, B, C)))

    def test_art_146_5_and_146_8_move_with_the_proceeding_records(self):
        def rows(supplied):
            return self.run_caller(supplied)['plants'][A]['results']
        both = rows([lodging('l-1', [sample(A)]), route('r-1', [sample(A)])])
        self.assertIs(both[DECISION].truth, True)
        self.assertEqual(self.run_caller([route('r-1', [sample(A)])])['plants'][A]['opinion_route']['route'],
                         "parere della Soprintendenza ai sensi dell'art. 146, c. 8")
        self.assertEqual(both[DECISION].effect, self.s.version(DECISION, AT)['true_effect'])
        for complete in (None, False):
            with self.subTest(complete=complete):
                stated = self.run_caller([lodging('l-1', [sample(A)], complete), route('r-1', [sample(A)])])
                self.assertIsNone(stated['plants'][A]['results'][DECISION].truth)
                self.assertEqual(stated['plants'][A]['results'][DECISION].needs, {EDGE})
                self.assertEqual(stated['plants'][A]['due'], DUE)
                self.assertEqual(stated['plants'][A]['performances'], {})
        alone = rows([lodging('l-1', [sample(A)])])
        self.assertEqual(alone[DECISION].needs, {ROUTE_NEED})
        unresolved = rows([lodging('l-1', [sample(A)]), route('r-1', [sample(A)], resolved=False)])
        self.assertIs(unresolved[DECISION].truth, False)
        # The latest route stated decides; one day's records that differ supply nothing.
        later = rows([lodging('l-1', [sample(A)]), route('r-0', [sample(A)], False, date(2025, 7, 20)),
                      route('r-1', [sample(A)])])
        self.assertIs(later[DECISION].truth, True)
        split = self.run_caller([lodging('l-1', [sample(A)]), route('r-0', [sample(A)], False),
                                 route('r-1', [sample(A)])])['plants'][A]
        self.assertEqual(split['results'][DECISION].needs, {ROUTE_NEED})
        self.assertIn('the caller does not choose', split['reported'][0]['cause'])
        self.assertEqual(rows([])[OPINION].needs, {RECEIPT_NEED})
        self.assertIs(rows([received('a-1', [sample(A)])])[OPINION].truth, True)
        self.assertEqual(rows([received('a-1', [sample(A)])])[OPINION].effect,
                         self.s.version(OPINION, AT)['true_effect'])

    def test_a_lodging_anchors_the_45_day_clock_and_its_lapse_grants_nothing(self):
        run = self.run_caller([lodging('l-1', [sample(A)])], upstream={A: SETTLED})
        plant = run['plants'][A]
        self.assertEqual(plant['due'], DUE)
        self.assertGreater(AT, DUE.date())
        self.assertEqual(plant['results'][RULE].needs, {NEED['grant'], NEED['union']})
        self.assertIsNone(self.run_caller([])['plants'][A]['due'])
        # Lodgings at two moments: the caller anchors neither.
        two = self.run_caller([lodging('l-1', [sample(A)], None), lodging('l-2', [sample(A)], True, date(2025, 6, 20))])
        self.assertIsNone(two['plants'][A]['due'])
        self.assertEqual(two['plants'][A]['reported'][0]['cause'],
                         'lodgings at different moments; the 45-day clock is not anchored')
        self.assertIs(two['plants'][A]['results'][DECISION].needs >= {ROUTE_NEED}, True)
        self.assertNotIn(EDGE, two['plants'][A]['results'][DECISION].needs)
        # A clock the held calendar cannot count is reported, never guessed: it ends on 24 February 2027, after
        # the national calendar's bound.
        late = self.run_caller([lodging('l-1', [sample(A)], occurred=date(2027, 1, 10))], at=date(2027, 3, 1))
        self.assertIsNone(late['plants'][A]['due'])
        self.assertIn('the 45-day clock is not counted', late['plants'][A]['reported'][0]['cause'])

    def test_a_grant_changes_nothing_else_about_the_plant_or_any_other(self):
        base = [lodging('l-1', [sample(A)]), route('r-1', [sample(A)]), received('a-1', [sample(A)]),
                decision('d-c', [sample(C)], 'denied')]
        without = self.run_caller(base, upstream={A: SETTLED})
        granted = self.run_caller(base + [decision('d-1', [tag('0990101')])], upstream={A: SETTLED})
        for row in (DECISION, OPINION):
            self.assertEqual(granted['plants'][A]['results'][row], without['plants'][A]['results'][row])
        self.assertEqual(granted['plants'][A]['due'], without['plants'][A]['due'])
        for plant in (B, C):
            self.assertEqual(granted['plants'][plant], without['plants'][plant])
        self.assertEqual(without['plants'][A]['results'][RULE].needs, {NEED['grant'], NEED['union']})
        self.assertEqual(granted['plants'][A]['results'][RULE].needs, {NEED['union']})

    def test_a_record_dated_after_the_evaluation_date_is_not_passed(self):
        run = self.run_caller([decision('d-1', [sample(A)], occurred=date(2025, 9, 2))], upstream={A: SETTLED})
        self.assertEqual(run['plants'][A]['results'][RULE].needs, {NEED['grant'], NEED['union']})
        self.assertIn('after the evaluation date', run['plants'][A]['reported'][0]['cause'])

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
                             ('personal-delivery', {}), ('posting', {})):
            with self.subTest(kind=kind, fields=fields), self.assertRaises(ValueError):
                self.run_caller([record('x-1', kind, [sample(A)], LODGED, **fields)])
        # A record printing no plant identifier, or one in no form PR #30's identity reads.
        for plants in ([], [dict(oid='990001')], [dict(card='0990101')], [dict(sample=' ')]):
            with self.subTest(plants=plants), self.assertRaises(ValueError):
                self.run_caller([lodging('l-1', plants)])
        # Nothing rides along on a record: no requirement, PPTR or grove value, no predicate.
        for extra in (dict(required=True), dict(required=False), dict(requires_authorization=True),
                      dict(designation='BP'), dict(grove=True), dict(granted=True), dict(complete_from='2025-06-17')):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                self.run_caller([dict(lodging('l-1', [sample(A)]), **extra)])
        # A decision states its outcome, intervention kind and conditions consistently.
        for bad in (dict(outcome='pending'), dict(outcome='silent-consent'), dict(intervention_kind='transplant'),
                    dict(outcome='granted-with-conditions', conditions=[]),
                    dict(outcome='granted', conditions=['una condizione']), dict(outcome='denied', conditions=['x'])):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.run_caller([dict(decision('d-1', [sample(A)]), **bad)])
        for bad in (dict(complete='sì'), dict(complete=1)):
            with self.assertRaises(ValueError):
                self.run_caller([dict(lodging('l-1', [sample(A)]), **bad)])
        with self.assertRaises(ValueError):
            self.run_caller([dict(route('r-1', [sample(A)]), resolved=None)])
        with self.assertRaises(ValueError):
            self.run_caller([dict(lodging('l-1', [sample(A)]), occurred='2025-06-17T10:00:00')])
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
            supplied_records([lodging('l-1', [sample(A)])])

    def test_the_cli_caller_emits_Cs_results_as_C_returns_them(self):
        import json
        sys.path.insert(0, str(ROOT / 'scripts'))
        import read_landscape
        supplied = [lodging('l-1', [sample(A)]), decision('d-1', [tag('0990101')], 'granted-with-conditions',
                                                         conditions=['Reimpianto entro 90 giorni.']),
                    decision('d-cod', [dict(cod=REPEATED)])]
        out = read_landscape.results(self.s, AT, [A, C], supplied, self.rows, REGISTER)
        json.dumps(out)
        a = out['plants'][A]
        self.assertEqual(a['results'][RULE]['needs'], sorted(set(NEED.values()) - {NEED['grant']}))
        self.assertIsNone(a['results'][RULE]['truth'])
        self.assertEqual((a['decision']['occurred'], a['decision']['conditions'], a['due']),
                         (DECIDED.isoformat(), ['Reimpianto entro 90 giorni.'], DUE.isoformat()))
        self.assertEqual(out['plants'][C]['results'][RULE]['needs'], sorted(NEED.values()))
        self.assertEqual([(u['record'], u['cause']) for u in out['unattached']], [('d-cod', 'several matches')])


if __name__ == '__main__':
    unittest.main()
