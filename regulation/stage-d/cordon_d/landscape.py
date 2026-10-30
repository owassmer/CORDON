"""Row 10: the landscape proceeding's record for D.lgs. 19/2021 Art. 33(1), as the Osservatorio's file holds it.

The Osservatorio supplies the lodging of its landscape-authorization request, the superintendent's receipt of the
acts, the superintendent-opinion route and the landscape authority's decision (`case_prescriptions.supplied_records`,
family 'landscape'), each naming one or more plants by the identifiers it prints for each. The run admits them under
its cutoff and grant (`case_prescriptions.admitted_records`). Each plant a record names attaches through row 9's
identity, or stays unattached with its cause: PR #30's rows with the identities the same records, under the same
cutoff and grant, decide (`protection.named_rows`). Row 10 decides no identity. C then evaluates
Art. 33(1), Art. 146(5) and Art. 146(8) for each plant asked about, with what the records state, the plant's legal
status as row 9's rows carry it, and nothing else.

D supplies no "required / not required" fact: Art. 33(1)'s second paragraph names the one class that needs
authorization, its first derogates every other constraint, and A's row encodes the class. Neither Art. 146(2)
predicate is set and the row is not evaluated (`NOT_SUPPLIED`).
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime

from cordon_c.bindings import authorization_efficacy_facts, bind, leaves, listing_facts
from cordon_c.core import Evaluation, MissingInput, evaluate
from .case_prescriptions import admitted_records
from .instruments import DECLARATION, NATIONAL, PROPOSAL
from .protection import WITHIN, Register, named_rows, parcel_agrees, parcel_unread, printed as _printed

RULE = 'IT-DLGS-19-2021:Art.33(1):uninfected-protected-plant-removal'
DECISION = 'IT-DLGS42-A146:Art.146(5):regional-decision-owner'
OPINION = 'IT-DLGS42-A146:Art.146(8):superintendent-opinion'
APPLICATION = 'IT-DLGS42-A146:Art.146(2)'
CLOCK = 'B-CLK-IT-33(1)-landscape-authorization-45d'
GRANTED = 'the required landscape authorization has been granted'
ROUTE = 'the applicable superintendent-opinion route is resolved'
RECEIVED = 'the superintendent receives the complete acts for the landscape-authorization application'
# Art. 33(1)'s conjuncts their owning units supply (measure: row 6; infection: rows 1 and 2). The caller passes them
# as supplied; it sets no other predicate. The plant's legal status is read from row 9's rows, the rows this caller
# already takes: the register entry's act chain for L.R. 14/2007 Art. 5(3), and row 9's fact for each other instrument.
UPSTREAM = ('a valid measure requires plant removal in the exact demarcated area',
            'infection is currently established in the plant')
REGISTER_ROW = 'PUG-LR14-2007:Art.5(3):definitive-listing'
STATUS_ROWS = {NATIONAL: 'IT-L10-2013:Art.7(2):monumental-tree-status',
               DECLARATION: 'IT-DLGS42-A136:Art.136(1):declared-tree',
               PROPOSAL: 'IT-DLGS42-A139:Art.139-141:proposal-effect'}
EFFICACY = 'IT-DLGS42-A146:Art.146(4):authorization-efficacy'
EFFICACY_NEED = 'the day the landscape authorization for the removal took effect (its decision record)'
# The proposal row's conjunct naming the tree; the others (its start, its conclusion, its lapse) follow from its dates.
NAMES_THE_TREE = ('a proposal of declaration of notable public interest names the tree in its object or motivation, '
                  'alone or in a row or group, and not only as a feature of the area it proposes')
UNION = 'removal complies with applicable Union obligations'
# What this caller never supplies, and why; emitted once beside the results.
NOT_SUPPLIED = {
    UNION: "Art. 33(1)'s fifth conjunct, bound to operative-act and operative-assessment; outside row 10, and no "
           'D reader supplies it',
    APPLICATION: "not evaluated, unlike Art. 146(5) and 146(8), whose predicates are events the Osservatorio's file "
                 'records: its predicate "the proposed intervention requires landscape authorization" is the '
                 "statute's own meaning (D.lgs. 19/2021 Art. 33(1) names the plants whose removal needs it), which D "
                 'does not supply; its predicate "the property or area has legally protected landscape status" would '
                 'need the PPTR reads that ruling makes unneeded; and Art. 146(5) reaches it only through the '
                 'performance edge "complete landscape application submitted", which a lodging stated complete fills',
}
NOT_A_REGISTER_IDENTITY = ('unknown', 'not a register tree')
PARCEL = {'comune', 'foglio', 'particella'}
# The results a record of each kind could change; an ungranted one withholds them for the plant it names.
WITHHOLDS = {'landscape-lodging': (DECISION, 'due'), 'landscape-acts-received': (OPINION,),
             'landscape-opinion-route': (DECISION,), 'landscape-decision': (RULE,)}


def undecided(rows):
    """(record, group) -> [(plant, entry, row 9's rule)]: each group row 9 reads as naming a candidate entry for a
    plant whose identity it does not decide to be that entry."""
    found = defaultdict(list)
    for p in rows['plants']:
        for n in p['candidates'].get('named', ()):
            if n['cause'] == WITHIN and n['entries'] != [p['candidates']['identity']]:
                found[(n['record'], n['group'])].append((p['plant'], n['entries'][0], p['candidates']['rule']))
    return found


class Identities:
    """Row 9's identity of each plant in its rows (`protection.rows`, with the identities the run's records decide,
    `protection.named_rows`): an entry, 'unknown' between the candidate entries within its d, or 'not a register
    tree' (no entry within d); and the register entries a printed key or card names (`protection.Register`, over
    `protection.register_entries` with any deleted entry the rows carry). Nothing here changes it. A candidate marked
    `named_for` another plant stays this plant's candidate. A record's group that row 9 reads as naming a candidate
    entry for a plant, and does not decide, is held against that plant (`undecided`)."""

    def __init__(self, rows, register):
        self.plants, self.by_reference = {}, defaultdict(set)
        self.needs = {}  # a plant -> the needs of records outside the grant that could change its row 9 identity
        self.by_entry = defaultdict(set)       # an entry -> the plants whose row 9 identity it is
        self.candidate_of = defaultdict(set)   # an entry -> the 'unknown' plants it is a candidate of
        self.undecided = undecided(rows)
        for p in rows['plants']:
            if p['plant'] in self.plants:
                raise ValueError(f"PR #30's rows name plant {p['plant']} twice")
            identity = p['candidates']['identity']
            candidates = [e['entry'] for e in p['candidates']['entries']] if identity == 'unknown' else []
            references = {o[0] for o in p['observations'] if o[0]} | set(p.get('coincides_with') or ())
            self.plants[p['plant']] = dict(identity=identity, references=sorted(references), candidates=candidates,
                                           point=p.get('point'))
            if p['candidates'].get('needs'):
                self.needs[p['plant']] = list(p['candidates']['needs'])
            for reference in references:
                self.by_reference[reference].add(p['plant'])
            if identity not in NOT_A_REGISTER_IDENTITY:
                self.by_entry[identity].add(p['plant'])
            for entry in candidates:
                self.candidate_of[entry].add(p['plant'])
        self.register = register if isinstance(register, Register) else Register(register)
        self.entries = self.register.entries

    def output(self, plant):
        held = self.plants.get(plant)
        return dict(identity="not in PR #30's rows", references=[], candidates=[]) if held is None else \
            {k: v for k, v in held.items() if k != 'point'}

    def _parcel_agrees(self, form, entry):
        """`protection.parcel_agrees` for an entry held here; None where it is not held or prints no parcel."""
        e = self.entries.get(entry)
        return None if e is None else parcel_agrees(form, e)

    def read(self, identifier):
        """What one printed identifier names: the plants, through row 9's identity, and for a key or card the
        register entries (None for a monitoring reference or a parcel, which name no one entry)."""
        form = dict(identifier)
        if set(form) == {'sample'}:
            return dict(identifier=form, kind='sample', plants=set(self.by_reference.get(form['sample'].strip(), ())),
                        entries=None)
        if set(form) == PARCEL:
            return dict(identifier=form, kind='parcel', entries=None,
                        plants={p for e, plants in self.by_entry.items() if self._parcel_agrees(form, e) for p in plants})
        entries = [e.oid for e in self.register.names(form)]
        return dict(identifier=form, kind='register', entries=entries,
                    plants=set().union(*(self.by_entry.get(e, set()) for e in entries)))

    @staticmethod
    def decides(named):
        """A monitoring reference naming one plant, or a key or card naming one entry that is one plant's row 9
        identity. A parcel never decides."""
        return named['kind'] != 'parcel' and len(named['plants']) == 1 and \
            (named['entries'] is None or len(named['entries']) == 1)

    def _distance(self, plant, entry):
        point, e = self.plants[plant]['point'], self.entries.get(entry)
        if not point or e is None or e.x is None or e.y is None:
            return None
        return round(((e.x - point['x']) ** 2 + (e.y - point['y']) ** 2) ** 0.5, 2)

    def check(self, named, plant):
        """None where the identifier agrees with the plant's row 9 identity; 'unchecked' where it cannot be computed
        (a parcel, for a plant whose identity is not an entry, or is one that prints no parcel
        `protection.parcel_agrees` reads: its own parcel is not held); else why it does not
        agree. A key or card that names no register entry blocks for every plant: the index finding none is not
        evidence that no tree carries it, so the record stays unattached and named, never attached.

        A key or card naming a register entry outside the plant's candidates names a monumental tree, whether or not
        PR #30's rows hold it as a plant, so it blocks: a grant for that tree must not reach this plant. Row 9 never
        decides an entry outside the candidates: a record naming one within 50 m makes the identity unknown, and
        one beyond 50 m leaves it unchanged (`protection.identity`)."""
        form, held = named['identifier'], self.plants[plant]
        identity = held['identity']
        if named['kind'] == 'sample':
            return None if plant in named['plants'] else \
                f"{_printed(form)} names {sorted(named['plants']) or 'no plant'}, not plant {plant}"
        if named['kind'] == 'parcel':
            agrees = None if identity in NOT_A_REGISTER_IDENTITY else self._parcel_agrees(form, identity)
            if agrees is None:
                return 'unchecked'
            unread = parcel_unread(form, self.entries[identity])
            return None if agrees else f"{_printed(form)} cannot be held to entry {identity}, plant {plant}'s row 9 " \
                f"identity: {unread}" if unread else \
                f"{_printed(form)} is not the parcel of entry {identity}, plant {plant}'s row 9 identity"
        entries = named['entries']
        if not entries:
            return f'{_printed(form)} names no register entry held here'
        if identity in entries or set(entries) & set(held['candidates']):
            return None
        reasons = []
        for entry in entries:
            if identity not in NOT_A_REGISTER_IDENTITY:
                reasons.append(f"{_printed(form)} names entry {entry}; plant {plant}'s row 9 identity is entry "
                               f'{identity}')
                continue
            distance = self._distance(plant, entry)
            where = f'{distance} m from plant {plant}' if distance is not None else \
                f'at a distance from plant {plant} not held here'
            reasons.append(f"{_printed(form)} names entry {entry}, {where}; row 9 found no entry within d of it"
                           if identity == 'not a register tree' else
                           f"{_printed(form)} names entry {entry}, {where}, not within d; row 9's candidates are "
                           f"{held['candidates']}")
        return '; '.join(reasons)

    def attach(self, group, at=None):
        """One plant's group of printed identifiers, group `at` = (record, number): dict(plant, unchecked) where it
        attaches, else dict(cause, detail).

        It attaches to the one plant its deciding identifiers name where every other identifier it prints agrees
        with that plant's row 9 identity: a key or card naming the plant's identity entry, or one of the candidate
        entries of an 'unknown' plant; a parcel, only through the identity entry's own parcel, and otherwise left
        unchecked. A group row 9 reads as naming a candidate entry for the plant and does not decide (records or a
        note disagree, or the entry is named for several plants) never agrees: a grant it carries could be another
        tree's. Otherwise it is unattached: 'identifiers in conflict' where they name different plants or one
        disagrees with row 9 (each disagreement named); 'identity undecided' where its keys and cards name only
        entries that are no plant's identity, among them candidates of 'unknown' plants, and nothing else decides;
        'several matches' where an identifier names several plants or entries, or a parcel names plants; 'no
        match' where none names a plant.
        """
        named = [self.read(identifier) for identifier in group]
        deciding = {next(iter(n['plants'])): n for n in named if self.decides(n)}
        detail = []
        if len(deciding) == 1:
            plant = next(iter(deciding))
            checks = [(n, self.check(n, plant)) for n in named]
            detail = [reason for _, reason in checks if reason not in (None, 'unchecked')]
            detail += [f'row 9 reads this group as naming entry {entry} for plant {plant} and does not decide it: '
                       f'{rule}' for named_plant, entry, rule in self.undecided.get(at, ()) if named_plant == plant]
            if not detail:
                return dict(plant=plant, unchecked=[n['identifier'] for n, reason in checks if reason == 'unchecked'])
            cause = 'identifiers in conflict'
        elif deciding:
            cause = 'identifiers in conflict'
            detail = [f"{_printed(n['identifier'])} names plant {plant}" for plant, n in sorted(deciding.items())]
        else:
            registered = [e for n in named if n['kind'] == 'register' for e in n['entries']]
            undecided = {e: sorted(self.candidate_of[e]) for e in registered if self.candidate_of.get(e)}
            if undecided and not any(self.by_entry.get(e) for e in registered):
                cause = 'identity undecided'
                detail = [f'entry {e} is no plant\'s row 9 identity; it is a candidate of the "unknown" plants '
                          f'{plants}' for e, plants in undecided.items()]
            elif any(len(n['plants']) > 1 or len(n['entries'] or ()) > 1 or (n['kind'] == 'parcel' and n['plants'])
                     for n in named):
                cause = 'several matches'
            else:
                cause = 'no match'
        return dict(cause=cause, detail=detail, identifiers=[
            dict(identifier=n['identifier'], plants=sorted(n['plants']), entries=n['entries']) for n in named])


def attach(records, identities):
    """Each plant a record names, attached through row 9's identity or reported unattached with its cause.

    Returns (attached: plant -> its records, unattached: one item per group that attaches to no plant, notes:
    plant -> what the attachment leaves for that plant to report). Each group is the record's printed identifiers
    for one plant, numbered from 1 as the record lists them.
    """
    attached, unattached, notes = defaultdict(list), [], defaultdict(list)
    for record in records:
        seen = {}
        for number, group in enumerate(record['identifiers'], 1):
            outcome = identities.attach(group, (record['record'], number))
            plant = outcome.get('plant')
            if plant is None:
                unattached.append(dict(record=record['record'], kind=record['kind'], group=number,
                                       cause=outcome['cause'], detail=outcome['detail'],
                                       identifiers=outcome['identifiers'], fixture=record['fixture']))
                continue
            if plant in seen:
                notes[plant].append(dict(record=record['record'], cause=f'its groups {seen[plant]} and {number} '
                                                                        'both attach to this plant'))
                continue
            seen[plant] = number
            attached[plant].append(record)
            identity = identities.plants[plant]['identity']
            notes[plant] += [dict(record=record['record'], cause=f'{_printed(form)} not checked: ' + (
                'row 9 holds no parcel for a plant whose identity is not an entry' if identity in NOT_A_REGISTER_IDENTITY
                else parcel_unread(form, identities.entries[identity]))) for form in outcome['unchecked']]
    return attached, unattached, notes


def _day(moment, zone):
    return moment.astimezone(zone).date() if isinstance(moment, datetime) else moment


def _latest(records, value, zone):
    """The record of the latest day, where every record of that day states the same value; else None and the
    report of the records that differ."""
    if not records:
        return None, None
    last = max(_day(r['event'].occurred, zone) for r in records)
    final = [r for r in records if _day(r['event'].occurred, zone) == last]
    if len({value(r) for r in final}) > 1:
        return None, dict(records=sorted(r['record'] for r in final),
                          cause=f'records of {last.isoformat()} state different values; the caller does not choose')
    return final[0], None


def _fact(value, cause):
    return value if value is not None else Evaluation(None, needs=frozenset({cause}))


def status_facts(snapshot, at, rows, identities, plant):
    """The facts of Art. 33(1)'s legal-status rows for one plant, from row 9's rows. The register: the identity row 9
    decides (`identities`) and that entry's act chain as the rows carry it (`zone_entries[].acts`), through C's
    `listing_facts`; 'not a register tree' has no entry, 'unknown' may have one. Each other instrument: row 9's fact,
    which row 9 computes at its own decision date, so it is used only where that date is `at`; otherwise its predicates
    stay unset, naming that. A proposal fact true names a proposal whose effect C would date; row 9 holds none."""
    out = {}
    held = identities.plants.get(plant)
    identity = held['identity'] if held else None
    if identity is not None:
        entry = {e['entry']: e for e in rows.get('zone_entries') or ()}.get(identity) if identity not in \
            NOT_A_REGISTER_IDENTITY else None
        acts = (entry or {}).get('acts') or {}
        day = lambda act: act and act.get('published') and date.fromisoformat(act['published'])  # noqa: E731
        out |= listing_facts(snapshot, at, own_entry={'not a register tree': False, 'unknown': None}.get(identity, True),
                             first_publication=day(acts.get('provisional')),
                             definitive_decision=(day(acts['definitive']), True) if day(acts.get('definitive')) else None,
                             deletion=day(acts.get('deletion')), entry_history_complete=bool(acts.get('history_complete')))
    row = next((p for p in rows['plants'] if p['plant'] == plant), None)
    status = (row or {}).get('status') or {}
    read_at = (rows.get('instruments') or {}).get('at')
    for kind, stable in STATUS_ROWS.items():
        fact = status.get(kind)
        version = snapshot.version(stable, at)
        if fact is None or read_at != at.isoformat():
            continue
        cause = f"row 9's {kind} fact: {fact.get('cause')}"
        if kind == PROPOSAL:
            if fact['value'] is True:
                continue   # its start, conclusion and lapse are dated from the proposal's own dates
            out |= bind(version, {NAMES_THE_TREE: _fact(fact['value'], cause)})
        else:
            out |= bind(version, {text: _fact(fact['value'], cause) for text in leaves(version['condition_ast'])})
    return out


def _upstream(snapshot, at, upstream, plants):
    """The owning units' values for Art. 33(1)'s measure and infection conjuncts; nothing else."""
    if set(upstream) - set(plants):
        raise ValueError(f'Upstream values for plants not asked about: {sorted(set(upstream) - set(plants))}')
    for plant, values in upstream.items():
        other = set(values) - set(UPSTREAM)
        if other:
            raise ValueError(f"The caller passes only Art. 33(1)'s measure and infection conjuncts as their "
                             f'owning units supply them; not {sorted(other)} (plant {plant})')
    row = snapshot.version(RULE, at)
    if set(UPSTREAM) | {GRANTED, UNION} != set(leaves(row['condition_ast'])):
        raise ValueError(f"A's Art. 33(1) conjuncts changed: {row['provision_version_id']}")


def _event(record):
    return dict(record=record['record'], document=record['document'], occurred=record['event'].occurred)


def landscape_results(snapshot, at: date, plants, supplied, *, evaluated_at, permitted_controlled_sources, rows,
                      register, zone, calendar, upstream=None):
    """C's Art. 33(1), 146(5) and 146(8) results for each plant asked about, at the evaluation date `at`.

    `supplied` is the Osservatorio's landscape records, admitted as the run states (`admitted_records`): a record
    dated after `evaluated_at` (the knowledge cutoff) refuses the set; a record outside
    `permitted_controlled_sources` reaches no result, and the results it could change for a plant it names, dated
    on or before `at`, are withheld with the need 'authorized evidence for …' (`WITHHOLDS`). `rows` and `register`
    are PR #30's rows and the register, with which row 9 decides each identity from the same admitted records
    (`protection.named_rows`), and whose status facts give each plant's legal status (`status_facts`); `upstream`
    maps a plant to the values its owning units supply for Art. 33(1)'s measure and infection conjuncts.

    A granted record dated after `at` is reported, not passed. A predicate is true or false only where an attached
    record states it, and among several records of a kind the latest day's decide (one day's that disagree supply
    nothing and are reported): acts received stated complete fill 146(8); the opinion route fills 146(5)'s route
    predicate, false only where stated unresolved; a lodging stated complete fills 146(5)'s performance edge; the
    decision for the plant's removal fills Art. 33(1)'s grant, false only for a denial. A decision for another
    intervention fills nothing. A lodging anchors B's 45-day clock, whose end is reported as `due`; elapsed time
    fills nothing. Who acted (the lodging's and receipt's recipient, the decision's issuer) is reported as printed.
    """
    from cordon_c.quantities import clock_boundary
    upstream = upstream or {}
    _upstream(snapshot, at, upstream, plants)
    granted, ungranted = admitted_records(supplied, None, evaluated_at=evaluated_at, zone=zone, family='landscape',
                                          permitted_controlled_sources=permitted_controlled_sources)
    register = register if isinstance(register, Register) else Register(register)
    # Row 9 decides each plant's identity from the same records, under the same cutoff and grant; row 10 attaches.
    rows = named_rows(rows, register, supplied, evaluated_at=evaluated_at, zone=zone,
                      permitted_controlled_sources=permitted_controlled_sources)
    identities = Identities(rows, register)
    attached, unattached, notes = attach(granted, identities)
    needs = {r['record']: need for r, need in ungranted}
    withholding, _, _ = attach([r for r, _ in ungranted], identities)
    asked = list(dict.fromkeys(plants))
    versions = {sid: snapshot.version(sid, at)['provision_version_id'] for sid in (RULE, DECISION, OPINION)}
    results = {}
    for plant in asked:
        mine = attached.get(plant, [])
        held = [r for r in mine if _day(r['event'].occurred, zone) <= at]
        reported = list(notes.get(plant, ()))
        reported += [dict(record=r['record'], cause=f"dated {_day(r['event'].occurred, zone).isoformat()}, after the "
                                                    'evaluation date; not passed to C')
                     for r in mine if r not in held]
        if plant not in identities.plants and identities.by_reference.get(plant):
            named = sorted(identities.by_reference[plant])
            reported.append(dict(plants=named, cause=f"not a plant in PR #30's rows: a monitoring reference of "
                                                     f'plants {named}'))
        kinds = defaultdict(list)
        for r in held:
            kinds[r['kind']].append(r)
        facts = {RULE: {(versions[RULE], p): v for p, v in upstream.get(plant, {}).items()}, DECISION: {}, OPINION: {}}
        receipt, issue = _latest(kinds['landscape-acts-received'], lambda r: r['complete'], zone)
        if receipt is not None and receipt['complete'] is True:
            facts[OPINION][(versions[OPINION], RECEIVED)] = True
        reported += [issue] if issue else []
        route, issue = _latest(kinds['landscape-opinion-route'], lambda r: r['resolved'], zone)
        if route is not None:
            facts[DECISION][(versions[DECISION], ROUTE)] = route['resolved']
        reported += [issue] if issue else []
        lodging, issue = _latest(kinds['landscape-lodging'], lambda r: r['complete'], zone)
        performances = {(DECISION, APPLICATION): True} if lodging is not None and lodging['complete'] is True else {}
        reported += [issue] if issue else []
        removal = []
        for r in kinds['landscape-decision']:
            if r['intervention_kind'] == 'removal':
                removal.append(r)
            else:
                reported.append(dict(record=r['record'], cause=f"a decision for {r['intervention_kind']} "
                                                               f"({r['intervention']}), not this removal; it fills nothing"))
        decision, issue = _latest(removal, lambda r: (r['outcome'], r['procedure'], tuple(r['conditions']),
                                                      r['issuer']), zone)
        if decision is not None:
            facts[RULE][(versions[RULE], GRANTED)] = decision['outcome'] != 'denied'
            if decision['outcome'] != 'denied':
                # Art. 146(4): the grant counts while in effect; a phytosanitary removal needs no building title, so
                # its five years run from the decision's own day. No commencement record reaches row 10.
                facts[RULE] |= authorization_efficacy_facts(
                    snapshot, at, effective=_day(decision['event'].occurred, zone), works_began=None,
                    works_history_complete=False, zone=zone, calendar=calendar)
        if (versions[RULE], GRANTED) not in facts[RULE]:
            # Art. 146(4) dates the grant from the day it took effect, which only the decision supplies: one need.
            efficacy = snapshot.version(EFFICACY, at)
            facts[RULE] |= {(efficacy['provision_version_id'], text): Evaluation(None, needs=frozenset({EFFICACY_NEED}))
                            for text in leaves(efficacy['condition_ast'])}
        reported += [issue] if issue else []
        facts[RULE] |= status_facts(snapshot, at, rows, identities, plant)
        moments = {r['event'].occurred for r in kinds['landscape-lodging']}
        due = None
        if len(moments) == 1:
            try:
                due = clock_boundary(snapshot, CLOCK, at, next(iter(moments)), zone=zone, calendar=calendar)
            except MissingInput as error:
                reported.append(dict(records=sorted(r['record'] for r in kinds['landscape-lodging']),
                                     cause=f'the 45-day clock is not counted: {error}'))
        elif moments:
            reported.append(dict(records=sorted(r['record'] for r in kinds['landscape-lodging']),
                                 cause='lodgings at different moments; the 45-day clock is not anchored'))
        evaluations = {RULE: evaluate(snapshot, RULE, at, facts[RULE]),
                       DECISION: evaluate(snapshot, DECISION, at, facts[DECISION], performances=performances),
                       OPINION: evaluate(snapshot, OPINION, at, facts[OPINION])}
        # An ungranted record that could change a result for this plant leaves it without a definite answer.
        withheld = defaultdict(set)
        for r in withholding.get(plant, ()):
            if _day(r['event'].occurred, zone) <= at:
                for row in WITHHOLDS[r['kind']]:
                    withheld[row].add(needs[r['record']])
        # A record outside the grant that could change this plant's row 9 identity (`protection.named_rows`, `needs`)
        # withholds every result: each record attaches through that identity.
        for need in identities.needs.get(plant, ()):
            for row in (RULE, DECISION, OPINION, 'due'):
                withheld[row].add(need)
        for row, row_needs in withheld.items():
            if row == 'due':
                due = None
            else:
                evaluations[row] = Evaluation(None, needs=frozenset(row_needs))
        results[plant] = dict(
            identity=identities.output(plant), records=[r['record'] for r in mine], results=evaluations,
            facts={sid: {p: v for (vid, p), v in values.items() if vid == versions[sid]} for sid, values in facts.items()},
            # The facts of the rows Art. 33(1) refers to: legal status from row 9's rows, Art. 146(4) from the decision.
            referenced_facts={vid: {p: v for (v_, p), v in facts[RULE].items() if v_ == vid}
                              for vid in sorted({vid for vid, _ in facts[RULE]} - {versions[RULE]})},
            performances={f'{c} -> {r}': v for (c, r), v in performances.items()},
            decision=None if decision is None else dict(
                _event(decision), outcome=decision['outcome'], issuer=decision['issuer'],
                procedure=decision['procedure'], intervention=decision['intervention'],
                conditions=list(decision['conditions'])),
            lodgings=[dict(_event(r), recipient=r['recipient'], complete=r['complete'])
                      for r in kinds['landscape-lodging']],
            receipts=[dict(_event(r), recipient=r['recipient'], complete=r['complete'])
                      for r in kinds['landscape-acts-received']],
            opinion_route=None if route is None else dict(_event(route), route=route['route'],
                                                          resolved=route['resolved']),
            due=due, withheld={row: sorted(v) for row, v in withheld.items()}, reported=reported,
            fixture=any(r['fixture'] for r in mine))
    elsewhere = [dict(record=r['record'], kind=r['kind'], occurred=r['event'].occurred, plant=plant)
                 for plant, records in sorted(attached.items()) if plant not in asked for r in records]
    return dict(at=at, evaluated_at=evaluated_at, permitted_controlled_sources=sorted(permitted_controlled_sources),
                plants=results, unattached=unattached, elsewhere=elsewhere,
                ungranted=[dict(record=r['record'], kind=r['kind'], need=need) for r, need in ungranted],
                not_supplied=NOT_SUPPLIED)
