"""Row 10: the landscape proceeding's record for D.lgs. 19/2021 Art. 33(1), as the Osservatorio's file holds it.

The Osservatorio supplies, per plant, the lodging of its landscape-authorization request, the superintendent's
receipt of the complete acts, the superintendent-opinion route and the landscape authority's decision
(`case_prescriptions.supplied_records`, family 'landscape'). Each record attaches to one plant through the plant
identity PR #30's reader establishes (`protection`), or stays unattached with its cause. C then evaluates
Art. 33(1), Art. 146(5) and Art. 146(8) for each plant asked about, with what the records state and nothing else.

D supplies no "required / not required" fact: Art. 33(1)'s second paragraph names the one class that needs
authorization, its first derogates every other constraint, and A's row encodes the class. Neither Art. 146(2)
predicate is set and the row is not evaluated: it is the landscape authority's procedural row, and 146(5) reaches
it only through the performance edge a lodging stated complete fills.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime

from cordon_c.bindings import leaves
from cordon_c.core import MissingInput, evaluate
from .case_prescriptions import supplied_records

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
    APPLICATION: "the landscape authority's procedural row; neither of its predicates is supplied and the row is "
                 'not evaluated, because no Osservatorio decision reads it; Art. 146(5) reaches it only through the '
                 'performance edge "complete landscape application submitted", which a lodging stated complete fills',
}
NOT_A_REGISTER_IDENTITY = ('unknown', 'not a register tree')


def _number(text):
    text = (text or '').strip()
    return int(text) if text.isdigit() else None


def _place(text):
    return ' '.join((text or '').split()).upper()


def _parcel(comune, foglio, particella):
    parts = (_place(comune), _number(foglio), _number(particella))
    return parts if parts[0] and None not in parts[1:] else None


class Identities:
    """PR #30's identity of each plant in its rows (`protection.rows`), and the register entries a printed key or
    card names (`protection.register_entries`, with any deleted entry the rows carry)."""

    def __init__(self, rows, register):
        self.plants, self.by_reference, self.by_entry = {}, defaultdict(set), defaultdict(set)
        for p in rows['plants']:
            if p['plant'] in self.plants:
                raise ValueError(f"PR #30's rows name plant {p['plant']} twice")
            identity = p['candidates']['identity']
            references = {o[0] for o in p['observations'] if o[0]} | set(p.get('coincides_with') or ())
            self.plants[p['plant']] = dict(identity=identity, references=sorted(references))
            for reference in references:
                self.by_reference[reference].add(p['plant'])
            if identity not in NOT_A_REGISTER_IDENTITY:
                self.by_entry[identity].add(p['plant'])
        self.entries = {e.oid: e for e in register}
        self.by_key, self.by_card = defaultdict(list), defaultdict(list)
        for e in register:
            if e.key and e.key.strip():
                self.by_key[e.key.strip()].append(e.oid)
            if _number(e.card) is not None and _place(e.comune):
                self.by_card[(_place(e.comune), _number(e.card))].append(e.oid)

    def names(self, identifier):
        """The plants one printed identifier names through PR #30's identity, and the register entries it names
        (None for a monitoring reference or a parcel, which name no entry by themselves)."""
        form = dict(identifier)
        if set(form) == {'sample'}:
            return set(self.by_reference.get(form['sample'].strip(), ())), None
        if set(form) == {'comune', 'foglio', 'particella'}:
            parcel = _parcel(form['comune'], form['foglio'], form['particella'])
            return {plant for entry, plants in self.by_entry.items() if entry in self.entries and parcel and
                    _parcel(self.entries[entry].comune, self.entries[entry].foglio,
                            self.entries[entry].particella) == parcel for plant in plants}, None
        if set(form) == {'cod'}:
            entries = list(self.by_key.get(form['cod'].strip(), ()))
        else:
            number = _number(form['card'])
            entries = list(self.by_card.get((_place(form['comune']), number), ())) if number is not None else []
        return set().union(*(self.by_entry.get(e, set()) for e in entries)), entries


def attach(records, identities):
    """Each record attached to one plant, or reported unattached with its cause.

    An identifier decides a plant only where it names exactly one plant, and, for a key or card, exactly one
    register entry: a monitoring reference, a COD that does not repeat, or a card in its comune. A parcel never
    decides; it qualifies. A record attaches to the plant its deciding identifiers name when every identifier it
    prints names that plant. Otherwise it is unattached: 'identifiers in conflict' where they name different plants
    or one fails the plant another names, 'several matches' where they name several plants or entries and none
    decides, 'no match' where they name none.
    """
    attached, unattached = defaultdict(list), []
    for record in records:
        named = []
        for identifier in record['identifiers']:
            plants, entries = identities.names(identifier)
            parcel = set(dict(identifier)) == {'comune', 'foglio', 'particella'}
            named.append((dict(identifier), plants, entries, parcel))
        deciding = {next(iter(plants)) for _, plants, entries, parcel in named
                    if not parcel and len(plants) == 1 and (entries is None or len(entries) == 1)}
        if len(deciding) == 1 and all(next(iter(deciding)) in plants for _, plants, _, _ in named):
            attached[next(iter(deciding))].append(record)
            continue
        if deciding:
            cause = 'identifiers in conflict'
        elif any(len(plants) > 1 or (entries and len(entries) > 1) or (parcel and plants)
                 for _, plants, entries, parcel in named):
            cause = 'several matches'
        else:
            cause = 'no match'
        unattached.append(dict(record=record['record'], kind=record['kind'], cause=cause, fixture=record['fixture'],
                               identifiers=[dict(identifier=i, plants=sorted(p), entries=e)
                                            for i, p, e, _ in named]))
    return attached, unattached


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


def landscape_results(snapshot, at: date, plants, supplied, *, rows, register, zone, calendar, upstream=None):
    """C's Art. 33(1), 146(5) and 146(8) results for each plant asked about, at the evaluation date `at`.

    `supplied` is the Osservatorio's landscape records; `rows` and `register` are PR #30's identity; `upstream`
    maps a plant to the values its owning units supply for Art. 33(1)'s measure, status and infection conjuncts.
    A record dated after `at` is not passed. A predicate is true or false only where an attached record states it:
    the acts received fill 146(8); the latest opinion route fills 146(5)'s route predicate, false only where it is
    stated unresolved; a lodging stated complete fills 146(5)'s performance edge; the latest decision for the
    plant's removal fills Art. 33(1)'s grant, false only for a denial. A decision for another intervention fills
    nothing. A lodging anchors B's 45-day clock, whose end is reported as `due`; elapsed time fills nothing.
    """
    from cordon_c.quantities import clock_boundary
    upstream = upstream or {}
    _upstream(snapshot, at, upstream, plants)
    identities = Identities(rows, register)
    attached, unattached = attach(supplied_records(supplied, family='landscape'), identities)
    versions = {sid: snapshot.version(sid, at)['provision_version_id'] for sid in (RULE, DECISION, OPINION)}
    results = {}
    for plant in dict.fromkeys(plants):
        mine = attached.get(plant, [])
        held = [r for r in mine if _day(r['event'].occurred, zone) <= at]
        reported = [dict(record=r['record'], cause=f"dated {_day(r['event'].occurred, zone).isoformat()}, after the "
                                                   'evaluation date; not passed to C')
                    for r in mine if r not in held]
        kinds = defaultdict(list)
        for r in held:
            kinds[r['kind']].append(r)
        facts = {RULE: {(versions[RULE], p): v for p, v in upstream.get(plant, {}).items()}, DECISION: {}, OPINION: {}}
        if kinds['landscape-acts-received']:
            facts[OPINION][(versions[OPINION], RECEIVED)] = True
        route, issue = _latest(kinds['landscape-opinion-route'], lambda r: r['resolved'], zone)
        if route is not None:
            facts[DECISION][(versions[DECISION], ROUTE)] = route['resolved']
        reported += [issue] if issue else []
        performances = ({(DECISION, APPLICATION): True}
                        if any(r['complete'] is True for r in kinds['landscape-lodging']) else {})
        removal = []
        for r in kinds['landscape-decision']:
            if r['intervention_kind'] == 'removal':
                removal.append(r)
            else:
                reported.append(dict(record=r['record'], cause=f"a decision for {r['intervention_kind']} "
                                                               f"({r['intervention']}), not this removal; it fills nothing"))
        decision, issue = _latest(removal, lambda r: (r['outcome'], r['procedure'], tuple(r['conditions'])), zone)
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
        results[plant] = dict(
            identity=identities.plants.get(plant, dict(identity="not in PR #30's rows", references=[])),
            records=[r['record'] for r in mine],
            results={RULE: evaluate(snapshot, RULE, at, facts[RULE]),
                     DECISION: evaluate(snapshot, DECISION, at, facts[DECISION], performances=performances),
                     OPINION: evaluate(snapshot, OPINION, at, facts[OPINION])},
            facts={sid: {p: v for (_, p), v in values.items()} for sid, values in facts.items()},
            performances={f'{c} -> {r}': v for (c, r), v in performances.items()},
            decision=None if decision is None else dict(
                record=decision['record'], document=decision['document'], occurred=decision['event'].occurred,
                outcome=decision['outcome'], procedure=decision['procedure'], intervention=decision['intervention'],
                conditions=list(decision['conditions'])),
            lodgings=[dict(record=r['record'], document=r['document'], occurred=r['event'].occurred,
                           complete=r['complete']) for r in kinds['landscape-lodging']],
            opinion_route=None if route is None else dict(
                record=route['record'], document=route['document'], occurred=route['event'].occurred,
                route=route['route'], resolved=route['resolved']),
            due=due, reported=reported, fixture=any(r['fixture'] for r in mine))
    return dict(at=at, plants=results, unattached=unattached, not_supplied=NOT_SUPPLIED)
