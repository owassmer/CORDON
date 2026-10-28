"""Row 10: the landscape proceeding's record for D.lgs. 19/2021 Art. 33(1), as the Osservatorio's file holds it.

The Osservatorio supplies the lodging of its landscape-authorization request, the superintendent's receipt of the
acts, the superintendent-opinion route and the landscape authority's decision (`case_prescriptions.supplied_records`,
family 'landscape'), each naming one or more plants by the identifiers it prints for each. The run admits them under
its cutoff and grant (`case_prescriptions.admitted_records`). Each plant a record names attaches through the plant
identity PR #30's reader establishes (`protection`), or stays unattached with its cause. C then evaluates
Art. 33(1), Art. 146(5) and Art. 146(8) for each plant asked about, with what the records state and nothing else.

D supplies no "required / not required" fact: Art. 33(1)'s second paragraph names the one class that needs
authorization, its first derogates every other constraint, and A's row encodes the class. Neither Art. 146(2)
predicate is set and the row is not evaluated (`NOT_SUPPLIED`).
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime

from cordon_c.bindings import leaves
from cordon_c.core import Evaluation, MissingInput, evaluate
from .case_prescriptions import admitted_records

RULE = 'IT-DLGS-19-2021:Art.33(1):uninfected-protected-plant-removal'
DECISION = 'IT-DLGS42-A146:Art.146(5):regional-decision-owner'
OPINION = 'IT-DLGS42-A146:Art.146(8):superintendent-opinion'
APPLICATION = 'IT-DLGS42-A146:Art.146(2)'
CLOCK = 'B-CLK-IT-33(1)-landscape-authorization-45d'
GRANTED = 'the required landscape authorization has been granted'
ROUTE = 'the applicable superintendent-opinion route is resolved'
RECEIVED = 'the superintendent receives the complete acts for the landscape-authorization application'
# Art. 33(1)'s conjuncts their owning units supply (measure: row 6; legal status: row 9; infection: rows 1 and 2).
# The caller passes them as supplied; it sets no other predicate.
UPSTREAM = ('a valid measure requires plant removal in the exact demarcated area',
            'the plant has monumental or historic-interest legal status',
            'infection is currently established in the plant')
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


def _number(text):
    text = (text or '').strip()
    return int(text) if text.isdigit() else None


def _place(text):
    return ' '.join((text or '').split()).upper()


def _parcel(comune, foglio, particella):
    parts = (_place(comune), _number(foglio), _number(particella))
    return parts if parts[0] and None not in parts[1:] else None


def _printed(form):
    if set(form) == {'sample'}:
        return f"monitoring reference {form['sample']}"
    if set(form) == PARCEL:
        return f"parcel {form['comune']} fg {form['foglio']} p.lla {form['particella']}"
    return f"COD {form['cod']}" if set(form) == {'cod'} else f"card {form['card']} ({form['comune']})"


class Identities:
    """PR #30's identity of each plant in its rows (`protection.rows`): an entry, 'unknown' between the candidate
    entries within its d, or 'not a register tree' (no entry within d); and the register entries a printed key or
    card names (`protection.register_entries`, with any deleted entry the rows carry). Nothing here changes it."""

    def __init__(self, rows, register):
        self.plants, self.by_reference = {}, defaultdict(set)
        self.by_entry = defaultdict(set)       # an entry -> the plants whose row 9 identity it is
        self.candidate_of = defaultdict(set)   # an entry -> the 'unknown' plants it is a candidate of
        for p in rows['plants']:
            if p['plant'] in self.plants:
                raise ValueError(f"PR #30's rows name plant {p['plant']} twice")
            identity = p['candidates']['identity']
            candidates = [e['entry'] for e in p['candidates']['entries']] if identity == 'unknown' else []
            references = {o[0] for o in p['observations'] if o[0]} | set(p.get('coincides_with') or ())
            self.plants[p['plant']] = dict(identity=identity, references=sorted(references), candidates=candidates,
                                           point=p.get('point'))
            for reference in references:
                self.by_reference[reference].add(p['plant'])
            if identity not in NOT_A_REGISTER_IDENTITY:
                self.by_entry[identity].add(p['plant'])
            for entry in candidates:
                self.candidate_of[entry].add(p['plant'])
        self.entries = {e.oid: e for e in register}
        self.by_key, self.by_card = defaultdict(list), defaultdict(list)
        for e in register:
            if e.key and e.key.strip():
                self.by_key[e.key.strip()].append(e.oid)
            if _number(e.card) is not None and _place(e.comune):
                self.by_card[(_place(e.comune), _number(e.card))].append(e.oid)

    def output(self, plant):
        held = self.plants.get(plant)
        return dict(identity="not in PR #30's rows", references=[], candidates=[]) if held is None else \
            {k: v for k, v in held.items() if k != 'point'}

    def _entry_parcel(self, entry):
        e = self.entries.get(entry)
        return e and _parcel(e.comune, e.foglio, e.particella)

    def read(self, identifier):
        """What one printed identifier names: the plants, through row 9's identity, and for a key or card the
        register entries (None for a monitoring reference or a parcel, which name no one entry)."""
        form = dict(identifier)
        if set(form) == {'sample'}:
            return dict(identifier=form, kind='sample', plants=set(self.by_reference.get(form['sample'].strip(), ())),
                        entries=None)
        if set(form) == PARCEL:
            parcel = _parcel(form['comune'], form['foglio'], form['particella'])
            return dict(identifier=form, kind='parcel', entries=None,
                        plants={p for e, plants in self.by_entry.items() if parcel and self._entry_parcel(e) == parcel
                                for p in plants})
        if set(form) == {'cod'}:
            entries = list(self.by_key.get(form['cod'].strip(), ()))
        else:
            number = _number(form['card'])
            entries = list(self.by_card.get((_place(form['comune']), number), ())) if number is not None else []
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
        (a parcel, for a plant whose identity is not an entry: its own parcel is not held); ('noted', why) for a key
        or card that names no register entry at all, for a plant whose identity is not an entry: it names no tree
        that could compete, so it does not block and is reported beside the result; else why it does not agree.

        A key or card naming a register entry outside the plant's candidates names a monumental tree, whether or not
        PR #30's rows hold it as a plant, so it blocks: a grant for that tree must not reach this plant. Whether an
        Osservatorio record may decide that a plant is an entry row 9 left outside it is row 9's question."""
        form, held = named['identifier'], self.plants[plant]
        identity = held['identity']
        if named['kind'] == 'sample':
            return None if plant in named['plants'] else \
                f"{_printed(form)} names {sorted(named['plants']) or 'no plant'}, not plant {plant}"
        if named['kind'] == 'parcel':
            parcel = None if identity in NOT_A_REGISTER_IDENTITY else self._entry_parcel(identity)
            if parcel is None:
                return 'unchecked'
            return None if parcel == _parcel(form['comune'], form['foglio'], form['particella']) else \
                f"{_printed(form)} is not the parcel of entry {identity}, plant {plant}'s row 9 identity"
        entries = named['entries']
        if not entries:
            why = f'{_printed(form)} names no register entry'
            return ('noted', why) if identity in NOT_A_REGISTER_IDENTITY else why
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

    def attach(self, group):
        """One plant's group of printed identifiers: dict(plant, unchecked) where it attaches, else dict(cause,
        detail).

        It attaches to the one plant its deciding identifiers name where every other identifier it prints agrees
        with that plant's row 9 identity: a key or card naming the plant's identity entry, or one of the candidate
        entries of an 'unknown' plant; a parcel, only through the identity entry's own parcel, and otherwise left
        unchecked. Otherwise it is unattached: 'identifiers in conflict' where they name different plants or one
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
            detail = [reason for _, reason in checks if reason not in (None, 'unchecked') and not isinstance(reason, tuple)]
            if not detail:
                return dict(plant=plant, unchecked=[n['identifier'] for n, reason in checks if reason == 'unchecked'],
                            noted=[reason[1] for _, reason in checks if isinstance(reason, tuple)])
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
            outcome = identities.attach(group)
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
            notes[plant] += [dict(record=record['record'], cause=f'{_printed(form)} not checked: row 9 holds no '
                                                                 'parcel for a plant whose identity is not an entry')
                             for form in outcome['unchecked']]
            notes[plant] += [dict(record=record['record'], cause=f'attached by its deciding identifier; it disagrees '
                                                                 f"with row 9's reading, which it does not change: {why}")
                             for why in outcome['noted']]
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


def _upstream(snapshot, at, upstream, plants):
    """The owning units' values for Art. 33(1)'s measure, status and infection conjuncts; nothing else."""
    if set(upstream) - set(plants):
        raise ValueError(f'Upstream values for plants not asked about: {sorted(set(upstream) - set(plants))}')
    for plant, values in upstream.items():
        other = set(values) - set(UPSTREAM)
        if other:
            raise ValueError(f"The caller passes only Art. 33(1)'s measure, status and infection conjuncts as their "
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
    are PR #30's identity; `upstream` maps a plant to the values its owning units supply for Art. 33(1)'s measure,
    status and infection conjuncts.

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
        reported += [issue] if issue else []
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
        for row, row_needs in withheld.items():
            if row == 'due':
                due = None
            else:
                evaluations[row] = Evaluation(None, needs=frozenset(row_needs))
        results[plant] = dict(
            identity=identities.output(plant), records=[r['record'] for r in mine], results=evaluations,
            facts={sid: {p: v for (_, p), v in values.items()} for sid, values in facts.items()},
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
