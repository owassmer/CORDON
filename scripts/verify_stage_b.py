#!/usr/bin/env python3
"""Stage B bounded mechanical checks (regression only — never acceptance). Schema stage-b-essence-v3."""
import hashlib, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
B = ROOT / 'regulation/stage-b/clocks-and-parameters.json'
KINDS = {'deadline', 'not_before', 'recurrence', 'minimum_duration', 'eligibility_threshold', 'lookback_window', 'ordering_constraint', 'promptness_standard', 'same_calendar_day'}
UNITS = {'hours', 'calendar_days', 'working_days', 'months', 'years', 'indefinite', None}
ANCHOR = {'legal_state': {'kind', 'producer_stable_provision_id', 'effect', 'object', 'medium', 'place'}, 'event': {'kind', 'event', 'record'},
          'biological': {'kind', 'term', 'place'}, 'recurrence': {'kind', 'scope', 'opening_state'},
          'resettable_period': {'kind', 'scope', 'start_event', 'reset_event', 'basis'}}
OWNERS = {'MEMBER_STATE_CONCERNED', 'MEMBER_STATES', 'COMPETENT_AUTHORITY', 'CENTRAL_PLANT_HEALTH_SERVICE', 'NATIONAL_PLANT_HEALTH_COMMITTEE', 'LANDSCAPE_AUTHORITY_REGION',
          'RESEARCH_LABORATORY', 'SELF_CONTROL_LABORATORY', 'OFFICIAL_LABORATORY', 'REGIONAL_PLANT_HEALTH_SERVICE', 'ARIF', 'OWNER_OR_HOLDER',
          'INNOVAPUGLIA'}
# the ruled silence narrowing: a stated post-silence period may run, but only against a recipient the act reached
EFFECTIVENESS = 'ACT_EFFECTIVE_AGAINST_RECIPIENT'
# corrected aperture (Owen 2026-09-02): an exclusion may never rest on the absence of a held instance
RETROSPECTIVE = re.compile(r'(?i)no (?:held )?(?:decision|case) consults|only held|has (?:not )?yet (?:occurred|happened)|no held instance')
PK = {'floor', 'exact', 'ceiling', 'threshold', 'design_target', 'open_term'}
PVALUE = ({'confidence', 'confidence_bound', 'design_prevalence', 'design_prevalence_bound'}, {'samples', 'tests'},
          {'from_month', 'to_month', 'wraps_year'}, {'open_term', 'reserved_to'})
PUNITS = {'m', 'km', 'percent', 'Cq', 'month', 'count', None}
DISP = {'clock', 'parameter', 'qualifies_clock', 'open_term', 'not_a_clock', 'implements_clock', 'restates_parameter', 'not_a_parameter'}
CF = ['clock_id', 'producer_provision_version_id', 'source_phrase', 'kind', 'anchor', 'magnitude', 'bound', 'unit', 'relation', 'window', 'applies_when',
      'legal_duty_owner', 'executor', 'consumer_decision', 'consequence_on_expiry', 'completion', 'effective_from', 'effective_to_exclusive', 'note']
PF = ['parameter_id', 'producer_provision_version_id', 'source_phrase', 'kind', 'value', 'unit', 'comparator', 'scope', 'consumer_decision', 'effective_from', 'effective_to_exclusive', 'note']
def norm(s): return re.sub(r'\s+', ' ', s or '').strip().lower()
def fail(m): print('FAIL:', m); sys.exit(1)
def toks(ast, acc):
    if isinstance(ast, dict):
        if isinstance(ast.get('effect'), str): acc.update(t.strip() for t in ast['effect'].split(';'))
        for x in ast.values(): toks(x, acc)
    elif isinstance(ast, list):
        for x in ast: toks(x, acc)
    return acc

def main():
    b = json.loads(B.read_text(encoding='utf-8'))
    if b.get('schema') != 'stage-b-essence-v3': fail('schema tag')
    if 'stage_a_inputs' in b: fail('canonical carries source paths/hashes; integrity metadata belongs in generation-status.json (essence-only boundary)')
    A = {}
    for p in ('regulation/stage-a/authoring-eu.json', 'regulation/jurisdiction/canonical/authoring.json'):
        for r in json.loads((ROOT / p).read_text(encoding='utf-8')): A[r['provision_version_id']] = r
    STABLE = {}
    for r in A.values(): STABLE.setdefault(r['stable_provision_id'], []).append(r)
    for v in STABLE.values(): v.sort(key=lambda r: r['effective_from'])
    TOK = {s: toks([r['condition_ast'] for r in rows], set()) for s, rows in STABLE.items()}
    ALL = set().union(*TOK.values())
    def interval(vid):
        r = A[vid]; rows = STABLE[r['stable_provision_id']]; i = rows.index(r); to = r['effective_to_exclusive'] or ''; j = i + 1
        while j < len(rows) and str(rows[j].get('semantic_change')).upper() == 'NO': to = rows[j]['effective_to_exclusive'] or ''; j += 1
        return r['effective_from'], to
    seen = set()
    for kind, rows, fields in (('clock', b['clocks'], CF), ('parameter', b['parameters'], PF)):
        for r in rows:
            rid = r.get('clock_id') or r.get('parameter_id')
            if list(r.keys()) != fields: fail(f'{rid}: field set/order')
            if rid in seen: fail(f'duplicate {rid}')
            seen.add(rid)
            p = A.get(r['producer_provision_version_id'])
            if not p: fail(f'{rid}: producer not in A')
            if norm(r['source_phrase']) not in norm(p['source_quote']): fail(f'{rid}: source_phrase not in producer quote')
            ef, et = interval(r['producer_provision_version_id'])
            if (r['effective_from'], r['effective_to_exclusive'] or '') != (ef, et): fail(f'{rid}: interval {r["effective_from"]}..{r["effective_to_exclusive"]} != {ef}..{et}')
            if r['consumer_decision'] not in STABLE: fail(f'{rid}: consumer_decision {r["consumer_decision"]} not a stable id')
            prose = norm(json.dumps({k: r.get(k) for k in ('anchor', 'note', 'scope', 'window')}, ensure_ascii=False))
            if 'specified pest (' in prose or 'xylella' in prose: fail(f'{rid}: definiens annotation (Art. 1(a))')
            for t in ('host plant', 'specified plant'):
                if t in prose and t not in norm(p['source_quote']): fail(f'{rid}: "{t}" not in producer quote')
            # note admissibility is a semantic question the conventions state and a human reread gates; a character
            # count enforces nothing and cannot tell an open term from rationale (review cycle 3, F4-06).
            if r['note'] is not None and not (isinstance(r['note'], str) and r['note'].strip()): fail(f'{rid}: note must be null or a non-empty string')
            if kind == 'clock':
                a = r['anchor']; ak = a.get('kind')
                if ak not in ANCHOR or set(a.keys()) != ANCHOR[ak]: fail(f'{rid}: anchor shape')
                if ak == 'legal_state':
                    if a['effect'] not in TOK.get(a['producer_stable_provision_id'], set()): fail(f'{rid}: anchor effect {a["effect"]} not emitted by {a["producer_stable_provision_id"]}')
                    if not a['object'] or not a['place']: fail(f'{rid}: legal_state anchor needs object and place')
                if ak == 'event' and a['record'] not in ('OPERATOR_RECORD', 'RECEIVED_RECORD'): fail(f'{rid}: record class')
                if ak == 'recurrence' and a['opening_state'] and a['opening_state']['effect'] not in TOK.get(a['opening_state']['producer_stable_provision_id'], set()): fail(f'{rid}: opening_state')
                if r['kind'] not in KINDS: fail(f'{rid}: kind')
                if r['unit'] not in UNITS: fail(f'{rid}: unit')
                if r['legal_duty_owner'] not in OWNERS: fail(f'{rid}: owner')
                m = r['magnitude']
                if m is not None and not re.fullmatch(r'\d+(\.\d+)?', m): fail(f'{rid}: magnitude not numeric')
                if (m is None) != (r['bound'] is None): fail(f'{rid}: bound must be set iff magnitude is set')
                if r['kind'] in ('deadline', 'not_before', 'minimum_duration', 'eligibility_threshold', 'lookback_window') and m is None: fail(f'{rid}: {r["kind"]} needs a magnitude')
                if r['kind'] in ('not_before', 'eligibility_threshold') and r['bound'] != 'floor': fail(f'{rid}: {r["kind"]} is a floor')
                if r['kind'] == 'eligibility_threshold' and r['completion']['kind'] == 'a_effect':
                    fail(f'{rid}: an eligibility threshold completes when its own period is satisfied, not on the downstream decision it enables')
                if r['kind'] == 'ordering_constraint' and not r['relation']: fail(f'{rid}: ordering needs relation')
                if r['kind'] == 'same_calendar_day' and (m is not None or r['unit'] is not None): fail(f'{rid}: same_calendar_day carries no magnitude')
                if r['kind'] == 'promptness_standard' and (m is not None or r['unit'] != 'indefinite'): fail(f'{rid}: promptness standard is open')
                for k in ('consequence_on_expiry', 'completion'):
                    e = r[k]
                    if e['kind'] == 'a_effect' and e['ref'] not in ALL: fail(f'{rid}: {k} token {e["ref"]} emitted nowhere in A')
                    if e['kind'] == 'a_version_performed' and e['ref'] not in A: fail(f'{rid}: {k} version')
                    if e['kind'] not in ('a_effect', 'a_version_performed', 'record', 'none'): fail(f'{rid}: {k} kind')
                if 'PRODUCER_' in json.dumps(r): fail(f'{rid}: sentinel survives')
                # Silence proves nothing by itself. The standing rule barred any clock on a silence route while seam 4 was
                # held; with seam 4 open the source's own post-silence window may be carried, but only from an anchor that
                # names evidenced non-response — never from a legal state, and never from the mere passage of publication.
                if 'silence' in r['producer_provision_version_id']:
                    a = r['anchor']
                    if a.get('kind') != 'event' or 'non-response' not in a.get('event', ''):
                        fail(f'{rid}: a silence route may only run from an anchor naming evidenced non-response')
                    if EFFECTIVENESS not in (r['applies_when'] or ''):
                        fail(f'{rid}: a silence route may only run where the act is effective against that recipient')
            else:
                if r['kind'] not in PK: fail(f'{rid}: kind')
                if r['unit'] not in PUNITS: fail(f'{rid}: parameter unit {r["unit"]}')
                v = r['value']
                # exhaustive union (review cycle 2, F3-C2-01): a value is a numeric string, or a dict whose key set
                # equals a declared member exactly. Lists, numbers, booleans and null are rejected here, not ignored.
                if isinstance(v, str):
                    if not re.fullmatch(r'\d+(\.\d+)?', v): fail(f'{rid}: scalar value must be a normalized numeric string')
                elif isinstance(v, dict):
                    if set(v) not in PVALUE: fail(f'{rid}: value shape {sorted(v)} is not a declared union member')
                else:
                    fail(f'{rid}: value must be a numeric string or a declared object, not {type(v).__name__}')
                # component types per member (review cycle 3, F3-C3-01): a boolean is not a number and a numeric
                # string is not a flag; each component is checked against its own declared type, not a union of both.
                if isinstance(v, dict) and 'open_term' not in v:
                    for k2, x in v.items():
                        if k2.endswith('_bound'):
                            if x not in ('exact', 'floor'): fail(f'{rid}: {k2} must be exact|floor')
                        elif k2 == 'wraps_year':
                            if not isinstance(x, bool): fail(f'{rid}: wraps_year must be a JSON boolean')

                        elif isinstance(x, bool) or not isinstance(x, str) or not re.fullmatch(r'\d+(\.\d+)?', x):
                            fail(f'{rid}: {k2} must be a normalized numeric string')
                if isinstance(v, dict) and set(v) == PVALUE[0] and r['unit'] != 'percent': fail(f'{rid}: a confidence/prevalence value is unit percent')
                if isinstance(v, dict) and set(v) == PVALUE[1] and r['unit'] != 'count': fail(f'{rid}: a samples/tests value is unit count')
                if isinstance(v, dict) and set(v) == PVALUE[2] and r['unit'] != 'month': fail(f'{rid}: a month-window value is unit month')
                if isinstance(v, dict) and set(v) == PVALUE[3]:
                    if r['kind'] != 'open_term': fail(f'{rid}: an open-term value requires kind open_term')
                    if not all(isinstance(x, str) and x for x in v.values()): fail(f'{rid}: open_term components must be non-empty strings')
                if r['kind'] in ('floor', 'ceiling', 'threshold') and not r['comparator']: fail(f'{rid}: comparator required')
                if set(r['scope']) != {'zone_type', 'purpose', 'branch', 'subspecies'}: fail(f'{rid}: scope keys')
    pop = {vid for s in json.loads((ROOT / 'regulation/stage-b/population.json').read_text(encoding='utf-8'))['seams'].values() for vid in s}
    covered = set()
    dseen = set()
    for d in b['dispositions']:
        if set(d) != {'provision_version_id', 'expression', 'disposition', 'ref', 'why'}: fail(f'disposition field set on {d.get("provision_version_id")}')
        k = json.dumps(d, ensure_ascii=False, sort_keys=True)
        # two identical entries are indistinguishable to any consumer, so one of them carries no fact (F4-07)
        if k in dseen: fail(f'duplicate disposition object on {d["provision_version_id"]}: {str(d["expression"])[:60]!r}')
        dseen.add(k)
        if d['provision_version_id'] not in A: fail('disposition unknown version')
        if d['disposition'] not in DISP: fail(f'disposition class {d["disposition"]}')
        # a class that claims a target must name it (review cycle 4, F3-C4-01): no relation asserted in prose alone
        if d['disposition'] in ('clock', 'parameter', 'qualifies_clock', 'implements_clock', 'restates_parameter'):
            if not d['ref']: fail(f'{d["provision_version_id"]}: {d["disposition"]} without a named target')
            if d['ref'] not in ({c['clock_id'] for c in b['clocks']} | {p['parameter_id'] for p in b['parameters']}):
                fail(f'{d["provision_version_id"]}: disposition ref {d["ref"]} is not a minted row')
        if d.get('why') and RETROSPECTIVE.search(d['why']):
            fail(f"{d['provision_version_id']}: exclusion rests on the absence of a held instance (retrospective aperture); state the vested-decision, closed-interval or not-holdable ground instead")
        covered.add(d['provision_version_id'])
    if pop - covered: fail(f'population rows without disposition: {sorted(pop - covered)[:5]}')
    # closure manifest (review cycle 2, F3-C2-04): an ACCEPTED seam must name the act and the reviewer. This checks that
    # an acceptance was RECORDED, never that it was sound — the act's semantic validity is Owen's, on a human reread.
    seams = json.loads((ROOT / 'regulation/stage-b/population.json').read_text(encoding='utf-8'))['seams']
    by_id = {c['clock_id']: c for c in b['clocks']} | {p['parameter_id']: p for p in b['parameters']}
    if [m['seam'] for m in b['closure_manifest']] != [1, 2, 3, 4]: fail('closure manifest must carry seams 1 to 4, each exactly once, in order')
    mc, mp = [], []
    for m in b['closure_manifest']:
        if set(m) != {'seam', 'title', 'status', 'clock_ids', 'parameter_ids', 'population_rows', 'reread',
                      'semantic_reviewer', 'acceptance_act', 'semantic_acceptance', 'accepted_content_sha256'}:
            fail(f'closure manifest seam {m.get("seam")}: field set')
        if m['semantic_acceptance'] not in ('ACCEPTED', 'NOT_ASSERTED'): fail(f'closure manifest seam {m["seam"]}: acceptance value')
        if m['semantic_acceptance'] == 'ACCEPTED' and not (m['acceptance_act'] and m['semantic_reviewer']):
            fail(f'closure manifest seam {m["seam"]}: ACCEPTED without a recorded acceptance act and reviewer')
        # C2: the acceptance is bound to the content it covered — the seam's clocks and parameters, the dispositions
        # that record what was read and excluded, AND the conventions block, because the conventions define what those
        # fields mean (F3-S5-02). Changing a convention reinterprets every accepted row, so it must break the binding
        # exactly as changing a row does. If any of it changes, ACCEPTED stops projecting until the owner accepts again.
        if m['semantic_acceptance'] == 'ACCEPTED':
            rows = [b['conventions']]
            rows += [by_id[i] for i in sorted(m['clock_ids'])] + [by_id[i] for i in sorted(m['parameter_ids'])]
            rows += sorted((d for d in b['dispositions'] if d['provision_version_id'] in set(seams.get(str(m['seam']), []))),
                           key=lambda d: json.dumps(d, ensure_ascii=False, sort_keys=True))
            fp = hashlib.sha256(json.dumps(rows, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            if m['accepted_content_sha256'] != fp:
                fail(f'closure manifest seam {m["seam"]}: ACCEPTED but its content no longer matches what was accepted')
        elif m['accepted_content_sha256'] is not None:
            fail(f'closure manifest seam {m["seam"]}: accepted content recorded without an acceptance')
        if m['status'] == 'HELD' and (m['clock_ids'] or m['parameter_ids'] or m['population_rows']):
            fail(f'closure manifest seam {m["seam"]}: a held seam carries no rows and no population')
        if m['population_rows'] != len(seams.get(str(m['seam']), [])): fail(f'closure manifest seam {m["seam"]}: population_rows disagrees with population.json')
        # each listed row must belong to the seam that claims it, by its producer's population membership
        # (review cycle 4, F3-C4-02: a global partition alone permits swapping a row between two seams)
        seam_of = {v: int(k) for k, vs in seams.items() for v in vs}
        for rid in m['clock_ids'] + m['parameter_ids']:
            prod = ({c['clock_id']: c for c in b['clocks']} | {p['parameter_id']: p for p in b['parameters']})[rid]['producer_provision_version_id']
            if seam_of.get(prod) != m['seam']:
                fail(f'closure manifest seam {m["seam"]}: {rid} produced by a row in seam {seam_of.get(prod)}')
        mc += m['clock_ids']; mp += m['parameter_ids']
    # the manifest must partition the canonical exactly: no row unmanifested, none claimed twice
    if sorted(mc) != sorted(c['clock_id'] for c in b['clocks']): fail('closure manifest clock_ids do not partition the canonical clocks')
    if sorted(mp) != sorted(p['parameter_id'] for p in b['parameters']): fail('closure manifest parameter_ids do not partition the canonical parameters')
    print('PASS Stage B bounded checks:', json.dumps({k: len(b[k]) for k in ('clocks', 'parameters', 'dispositions')}))

if __name__ == '__main__':
    main()
