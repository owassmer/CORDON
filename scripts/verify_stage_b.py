#!/usr/bin/env python3
"""Stage B bounded mechanical checks (regression only — never acceptance). Schema stage-b-essence-v6."""
import argparse, copy, hashlib, json, re, subprocess, sys, tempfile
from calendar import monthrange
from decimal import Decimal
from pathlib import Path
from verify_stage_a import verify_result_references
ROOT = Path(__file__).resolve().parents[1]
B = ROOT / 'regulation/stage-b/clocks-and-parameters.json'
POPULATION = ROOT / 'regulation/stage-b/population.json'
SOURCE_PARITY = ROOT / 'corpus/evidence/stage-b-regional-plan-source-parity-2026-09-08-stage-c.json'
STAGE_A_LOGICAL = ('regulation/stage-a/authoring-eu.json', 'regulation/jurisdiction/canonical/authoring.json')
KINDS = {'deadline', 'not_before', 'recurrence', 'minimum_duration', 'eligibility_threshold', 'lookback_window', 'ordering_constraint', 'promptness_standard', 'same_calendar_day'}
UNITS = {'hours', 'calendar_days', 'working_days', 'months', 'years', 'indefinite', None}
ANCHOR = {'legal_state': {'kind', 'producer_stable_provision_id', 'effect', 'object', 'medium', 'place'}, 'event': {'kind', 'event', 'record'},
          'biological': {'kind', 'term', 'place'}, 'recurrence': {'kind', 'scope', 'opening_state'},
          'resettable_period': {'kind', 'scope', 'start_event', 'reset_event', 'basis'}}
OWNERS = {'MEMBER_STATE_CONCERNED', 'MEMBER_STATES', 'COMPETENT_AUTHORITY', 'CENTRAL_PLANT_HEALTH_SERVICE', 'NATIONAL_PLANT_HEALTH_COMMITTEE', 'LANDSCAPE_AUTHORITY_REGION',
          'RESEARCH_LABORATORY', 'SELF_CONTROL_LABORATORY', 'OFFICIAL_LABORATORY', 'REGIONAL_PLANT_HEALTH_SERVICE', 'ARIF', 'OWNER_OR_HOLDER',
          'INNOVAPUGLIA', 'OFFICIAL_SAMPLE_CUSTODIAN'}
# the ruled silence narrowing: a stated post-silence period may run, but only against a recipient the act reached
EFFECTIVENESS = 'ACT_EFFECTIVE_AGAINST_RECIPIENT'
# corrected aperture (Owen 2026-09-02): an exclusion may never rest on the absence of a held instance
RETROSPECTIVE = re.compile(r'(?i)no (?:held )?(?:decision|case) consults|only held|has (?:not )?yet (?:occurred|happened)|no held instance')
PK = {'floor', 'exact', 'ceiling', 'threshold', 'design_target', 'open_term'}
PVALUE = ({'confidence', 'confidence_bound', 'design_prevalence', 'design_prevalence_bound'}, {'samples', 'tests'},
          {'from_month', 'to_month', 'wraps_year'}, {'open_term', 'reserved_to'})
PUNITS = {'m', 'km', 'percent', 'Cq', 'month', 'count', None}
DISP = {'clock', 'parameter', 'qualifies_clock', 'open_term', 'not_a_clock', 'implements_clock', 'restates_parameter', 'not_a_parameter'}
CF = ['clock_id', 'producer_provision_version_id', 'source_phrase', 'kind', 'anchor', 'magnitude', 'bound', 'unit', 'recurrence', 'relation', 'window', 'applies_when',
      'legal_duty_owner', 'executor', 'consumer_decision', 'consequence_on_expiry', 'completion', 'effective_from', 'effective_to_exclusive', 'note']
PF = ['parameter_id', 'producer_provision_version_id', 'source_phrase', 'kind', 'value', 'unit', 'comparator', 'legal_effect', 'applies_when', 'dependencies',
      'scope', 'consumer_decision', 'effective_from', 'effective_to_exclusive', 'note']
APERTURE = {'IN_APERTURE', 'EXTERNAL_ANCHOR', 'DEFERRED'}
LEGAL_EFFECT = {'OPERATIVE', 'CONDITIONAL', 'CONFLICT_RETAINED'}
def norm(s): return re.sub(r'\s+', ' ', s or '').strip().lower()
def fail(m): print('FAIL:', m); sys.exit(1)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
NUMBER = r'\d+(?:[.,]\d+)?'
MONTHS = ('january gennaio', 'february febbraio', 'march marzo', 'april aprile', 'may maggio', 'june giugno',
          'july luglio', 'august agosto', 'september settembre', 'october ottobre', 'november novembre', 'december dicembre')
NUMBER_WORDS = {'one': '1', 'first': '1', 'two': '2', 'four': '4', 'five': '5', 'un': '1', 'uno': '1',
                'due': '2', 'tre': '3', 'cinque': '5', 'quindici': '15', 'quarantacinque': '45'}
def decimal(text): return Decimal(text.replace(',', '.'))
def labelled_value(text, pattern, value, scale=1):
    found = re.search(pattern, text)
    return bool(found and decimal(found.group(1)) * scale == Decimal(value))
def scalar_value_matches(parameter):
    """Check the admitted distance/Cq phrase forms, not arbitrary legal language."""
    text, value = norm(parameter['source_phrase']), Decimal(parameter['value'])
    if parameter['kind'] == 'design_target' and parameter['unit'] == 'count' and parameter['comparator'] is None:
        return labelled_value(text, rf'({NUMBER})\s+plants to sample\b', value)
    if parameter['kind'] == 'exact' and parameter['unit'] is None and parameter['comparator'] is None:
        return labelled_value(text, rf'relative risk\s+({NUMBER})\b', value)
    cq = re.fullmatch(rf'cq\s*(<=|>=|<|>|=)\s*({NUMBER})', text)
    if cq:
        return (parameter['unit'] == 'Cq' and parameter['kind'] == 'threshold'
                and parameter['comparator'] == cq.group(1) and value == decimal(cq.group(2)))
    for match in re.finditer(rf'\b({NUMBER})\s*(km|m|metri)\b', text):
        if value != decimal(match.group(1)): continue
        unit = 'm' if match.group(2) == 'metri' else match.group(2)
        prefix = text[:match.start()]
        if re.search(r"(?:at least|no less than|almeno(?: nell'area di)?)\s*$", prefix):
            kind, comparator = 'floor', '>='
        elif re.search(r'(?:entro i|entro la distanza di|up to|no more than)\s*$', prefix):
            kind, comparator = 'ceiling', '<='
        elif re.search(r'more than\s*$', prefix):
            kind, comparator = 'threshold', '>'
        elif re.search(r'less than\s*$', prefix):
            kind, comparator = 'threshold', '<'
        else:
            kind, comparator = 'exact', None
        if (parameter['unit'], parameter['kind'], parameter['comparator']) == (unit, kind, comparator):
            return True
    return False

def source_value_matches(parameter):
    value, text = parameter['value'], norm(parameter['source_phrase'])
    if isinstance(value, str): return scalar_value_matches(parameter)
    if 'open_term' in value: return True
    if 'from_month' in value:
        found = [(m.start(), i) for i, names in enumerate(MONTHS, 1) for name in names.split()
                 for m in re.finditer(r'\b' + name + r'\b', text)]
        months = [i for _, i in sorted(found)]
        start, end = int(value['from_month']), int(value['to_month'])
        return months == [start, end] and value['wraps_year'] == (end < start)
    if 'samples' in value:
        return all(labelled_value(text, rf'({NUMBER})\s+{label}\b', value[label]) for label in ('samples', 'tests'))
    if 'confidence' in value:
        # Legal percent phrases and labelled workbook proportions have different units.
        if re.search(r'\bconfidence\s+' + NUMBER, text):
            return (labelled_value(text, rf'confidence\s+({NUMBER})', value['confidence'], 100)
                    and labelled_value(text, rf'(?:design )?prevalence\s+({NUMBER})', value['design_prevalence'], 100)
                    and value['confidence_bound'] == value['design_prevalence_bound'] == 'exact')
        patterns = {
            'confidence': rf'(?P<floor>at least\s+)?(?P<number>{NUMBER})\s*%\s*(?:of\s+)?confidence',
            'design_prevalence': rf'level of presence(?: of infected plants)?(?: of)?\s+(?P<floor>at least\s+)?(?P<number>{NUMBER})\s*%',
        }
        for field, pattern in patterns.items():
            match = re.search(pattern, text)
            if not match or decimal(match['number']) != Decimal(value[field]): return False
            if value[field + '_bound'] != ('floor' if match['floor'] else 'exact'): return False
        return True
    return False

def clock_value_matches(clock):
    """Bounded lexical checks of stated quantities, not a legal or calendar-arithmetic engine."""
    text = norm(clock['source_phrase'])
    words = '|'.join(NUMBER_WORDS)
    units = {'hours': r'ore|hours?', 'calendar_days': r'gg|giorni(?! lavorativi)|days?(?! working)',
             'working_days': r'(?:giorni|gg) lavorativi|working days?', 'months': r'mesi|months?', 'years': r'anni|years?'}
    if isinstance(clock['magnitude'], str):
        if clock['unit'] not in units: return False
        matches = [m for m in re.finditer(rf'\b({NUMBER}|{words})\s+(?:{units[clock["unit"]]})\b', text)
                   if decimal(NUMBER_WORDS.get(m[1], m[1])) == Decimal(clock['magnitude'])]
        if not matches: return False
        if clock['kind'] in ('not_before', 'eligibility_threshold'):
            if clock['bound'] != 'floor': return False
        elif clock['kind'] == 'minimum_duration':
            if not any(clock['bound'] == ('floor' if re.search(r'(?:at least|almeno)\s*$', text[:m.start()]) else 'exact')
                       for m in matches): return False
        elif clock['bound'] != 'exact':
            return False
    rec = clock['recurrence']
    if rec:
        # Recognized source requirements cannot disappear into a permitted null component.
        annual_required = bool(re.search(r'\b(?:annual(?:ly|e|i|mente)?|each year|ogni anno|course of the year)\b|l[’\x27]anno\b', text))
        monthly_required = bool(re.search(r'\b(?:mensilmente|monthly)\b', text))
        occurrence_required = bool(re.search(r'\b(?:once|twice|una volta|due volte)\b', text))
        date_required = any(re.search(rf'\b\d{{1,2}}\s+(?:{"|".join(names.split())})\b', text) for names in MONTHS)
        if (annual_required or monthly_required) and rec['period'] is None: return False
        if occurrence_required and rec['occurrences_per_period'] is None: return False
        if date_required and rec['calendar_deadline'] is None: return False
        period = rec['period']
        if period:
            annual = bool(re.search(r'\b(?:annual(?:ly|e|i|mente)?|year|anno)\b', text))
            monthly = 'mensilmente' in text or 'monthly' in text
            if period['magnitude'] != '1' or period['bound'] != 'exact' or not ((period['unit'] == 'years' and annual) or (period['unit'] == 'months' and monthly)):
                return False
        occurrence = rec['occurrences_per_period']
        if occurrence:
            stated = '2' if re.search(r'\b(?:twice|due volte)\b', text) else '1' if re.search(r'\b(?:once|una volta)\b', text) else None
            if stated != occurrence['count']: return False
            bound = 'floor' if re.search(r'\b(?:at least\s+(?:once|twice)|almeno\s+(?:una volta|due volte))\b', text) else 'exact'
            if occurrence['bound'] != bound: return False
        due = rec['calendar_deadline']
        if due:
            month, day = int(due['month']), int(due['day'])
            if not (1 <= month <= 12 and 1 <= day <= monthrange(2000, month)[1]): return False
            if not any(re.search(rf'\b{day}\s+{name}\b', text) for name in MONTHS[month - 1].split()): return False
    return True
def toks(ast, acc):
    if isinstance(ast, dict):
        if isinstance(ast.get('effect'), str): acc.update(t.strip() for t in ast['effect'].split(';'))
        for x in ast.values(): toks(x, acc)
    elif isinstance(ast, list):
        for x in ast: toks(x, acc)
    return acc

def acceptance_fingerprint(b, manifest, seams, stage_a_paths, population_path):
    population = set(seams.get(str(manifest['seam']), []))
    rows = [{
        'stage_a_inputs': {logical: sha(path) for logical, path in zip(STAGE_A_LOGICAL, stage_a_paths)},
        'population_sha256': sha(population_path),
    }, b['conventions']]
    for kind, key in (('clocks', 'clock_id'), ('parameters', 'parameter_id')):
        rows += sorted(({k: v for k, v in r.items() if k not in ('effective_from', 'effective_to_exclusive')}
                        for r in b[kind] if r['producer_provision_version_id'] in population), key=lambda r: r[key])
    rows += sorted((d for d in b['dispositions'] if d['provision_version_id'] in population),
                   key=lambda d: json.dumps(d, ensure_ascii=False, sort_keys=True))
    return hashlib.sha256(json.dumps(rows, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

def main(ledger_path=B, stage_a_paths=None, population_path=POPULATION):
    stage_a_paths = stage_a_paths or tuple(ROOT / p for p in STAGE_A_LOGICAL)
    b = json.loads(ledger_path.read_text(encoding='utf-8'))
    if b.get('schema') != 'stage-b-essence-v6': fail('schema tag')
    if 'stage_a_inputs' in b: fail('canonical carries source paths/hashes; integrity metadata belongs in generation-status.json (essence-only boundary)')
    A = {}
    for p in stage_a_paths:
        for r in json.loads(p.read_text(encoding='utf-8')): A[r['provision_version_id']] = r
    try:
        verify_result_references(list(A.values()), list(A.values()))
    except AssertionError as error:
        fail(str(error))
    STABLE = {}
    for r in A.values(): STABLE.setdefault(r['stable_provision_id'], []).append(r)
    for v in STABLE.values(): v.sort(key=lambda r: r['effective_from'])
    TOK = {s: toks([r['condition_ast'] for r in rows], set()) for s, rows in STABLE.items()}
    ALL = set().union(*TOK.values())
    deferred = {d['provision_version_id'].rsplit(':v', 1)[0] for d in b['dispositions'] if d.get('aperture') == 'DEFERRED'}
    # Dispositions scope expressions, not entire mixed-purpose legal owners.
    deferred -= {d['provision_version_id'].rsplit(':v', 1)[0] for d in b['dispositions'] if d.get('aperture') != 'DEFERRED'}
    def interval(vid):
        r = A[vid]; rows = STABLE[r['stable_provision_id']]; i = rows.index(r); to = r['effective_to_exclusive'] or ''; j = i + 1
        while j < len(rows) and str(rows[j].get('semantic_change')).upper() == 'NO': to = rows[j]['effective_to_exclusive'] or ''; j += 1
        return r['effective_from'], to
    seen = set()
    parameter_intervals = {}
    for kind, rows, fields in (('clock', b['clocks'], CF), ('parameter', b['parameters'], PF)):
        for i, r in enumerate(rows):
            rid = r.get('clock_id') or r.get('parameter_id')
            authored_fields = [k for k in fields if k not in ('effective_from', 'effective_to_exclusive')]
            if list(r.keys()) != authored_fields: fail(f'{rid}: field set/order; effective dates belong to the derived consumer view')
            if rid in seen: fail(f'duplicate {rid}')
            seen.add(rid)
            p = A.get(r['producer_provision_version_id'])
            if not p: fail(f'{rid}: producer not in A')
            if norm(r['source_phrase']) not in norm(p['source_quote']): fail(f'{rid}: source_phrase not in producer quote')
            ef, et = interval(r['producer_provision_version_id'])
            values = r | {'effective_from': ef, 'effective_to_exclusive': et}
            r = rows[i] = {k: values[k] for k in fields}
            if r['consumer_decision'] not in STABLE: fail(f'{rid}: consumer_decision {r["consumer_decision"]} not a stable id')
            if r['consumer_decision'] in deferred: fail(f'{rid}: consumer_decision crosses into an explicitly deferred route')
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
                rec = r['recurrence']
                if r['kind'] == 'recurrence':
                    if set(rec or {}) != {'period', 'occurrences_per_period', 'calendar_deadline'}:
                        fail(f'{rid}: recurrence shape')
                    if any(r[k] is not None for k in ('magnitude', 'bound', 'unit')):
                        fail(f'{rid}: recurrence cannot overload magnitude/bound/unit')
                    period = rec['period']
                    if period is not None:
                        if set(period) != {'magnitude', 'unit', 'bound'} or period['unit'] not in ('months', 'years') \
                                or period['bound'] not in ('exact', 'floor') or not re.fullmatch(r'\d+(\.\d+)?', period['magnitude']):
                            fail(f'{rid}: recurrence period shape')
                    occurrences = rec['occurrences_per_period']
                    if occurrences is not None:
                        if set(occurrences) != {'count', 'bound'} or occurrences['bound'] not in ('exact', 'floor') \
                                or not re.fullmatch(r'\d+', occurrences['count']):
                            fail(f'{rid}: recurrence occurrence-count shape')
                    due = rec['calendar_deadline']
                    if due is not None and (set(due) != {'month', 'day'} or
                            not all(isinstance(x, str) and re.fullmatch(r'\d+', x) for x in due.values()) or
                            not (1 <= int(due['month']) <= 12) or not (1 <= int(due['day']) <= 31)):
                        fail(f'{rid}: recurrence calendar deadline shape')
                elif rec is not None:
                    fail(f'{rid}: non-recurrence clock carries recurrence semantics')
                m = r['magnitude']
                if isinstance(m, dict):
                    # A term the named instrument states: B holds no number, unit or bound, and no default.
                    if set(m) != PVALUE[3] or not all(isinstance(x, str) and x for x in m.values()) or r['kind'] != 'deadline' \
                            or r['unit'] is not None or r['bound'] is not None \
                            or re.search(rf'\b(?:{NUMBER}|{"|".join(NUMBER_WORDS)})\b', norm(r['source_phrase'])):
                        fail(f'{rid}: a reserved term is a deadline whose phrase, unit and bound carry no quantity')
                    m = None
                elif m is not None and not re.fullmatch(r'\d+(\.\d+)?', m): fail(f'{rid}: magnitude not numeric')
                if r['bound'] not in (None, 'exact', 'floor'): fail(f'{rid}: bound vocabulary')
                if (m is None) != (r['bound'] is None): fail(f'{rid}: bound must be set iff magnitude is set')
                if r['kind'] in ('deadline', 'not_before', 'minimum_duration', 'eligibility_threshold', 'lookback_window') and m is None and not isinstance(r['magnitude'], dict): fail(f'{rid}: {r["kind"]} needs a magnitude')
                if r['kind'] in ('not_before', 'eligibility_threshold') and r['bound'] != 'floor': fail(f'{rid}: {r["kind"]} is a floor')
                if r['kind'] in ('eligibility_threshold', 'lookback_window') and r['completion']['kind'] == 'a_effect':
                    fail(f'{rid}: a threshold or lookback completes on its own evidenced condition, not the downstream decision')
                if not clock_value_matches(r): fail(f'{rid}: clock quantity or calendar date is not evidenced by source_phrase')
                if r['kind'] == 'ordering_constraint' and not r['relation']: fail(f'{rid}: ordering needs relation')
                if r['kind'] == 'same_calendar_day' and (m is not None or r['unit'] is not None): fail(f'{rid}: same_calendar_day carries no magnitude')
                if r['kind'] == 'promptness_standard' and (m is not None or r['unit'] != 'indefinite'): fail(f'{rid}: promptness standard is open')
                for k in ('consequence_on_expiry', 'completion'):
                    e = r[k]
                    if e['kind'] == 'a_effect' and e['ref'] not in ALL: fail(f'{rid}: {k} token {e["ref"]} emitted nowhere in A')
                    if e['kind'] == 'a_version_performed' and e['ref'] not in A: fail(f'{rid}: {k} version')
                    if e['kind'] not in ('a_effect', 'a_version_performed', 'record', 'none'): fail(f'{rid}: {k} kind')
                if r['completion']['kind'] == 'none': fail(f'{rid}: a minted clock must name its own completion fact')
                expiry_ref = r['consequence_on_expiry'].get('ref')
                if expiry_ref and expiry_ref.rsplit(':v', 1)[0] in deferred:
                    fail(f'{rid}: consequence_on_expiry crosses into an explicitly deferred route')
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
                if r['comparator'] not in (None, '<', '<=', '>', '>=', '='): fail(f'{rid}: comparator vocabulary')
                expected_comparator = {'floor': '>=', 'ceiling': '<='}.get(r['kind'])
                if expected_comparator and r['comparator'] != expected_comparator: fail(f'{rid}: comparator disagrees with kind')
                if r['kind'] in ('exact', 'design_target', 'open_term') and r['comparator'] is not None:
                    fail(f'{rid}: this kind carries no comparator')
                if r['legal_effect'] not in LEGAL_EFFECT: fail(f'{rid}: legal effect')
                if r['legal_effect'] != 'OPERATIVE' and not r['applies_when']:
                    fail(f'{rid}: conditional or conflict-retained parameter needs applies_when')
                if not isinstance(r['dependencies'], list) or any(x not in STABLE for x in r['dependencies']):
                    fail(f'{rid}: parameter dependency is not a stable Stage A proposition')
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
                if not source_value_matches(r): fail(f'{rid}: normalized value is not evidenced by source_phrase')
                if r['kind'] in ('floor', 'ceiling', 'threshold') and not r['comparator']: fail(f'{rid}: comparator required')
                if set(r['scope']) != {'zone_type', 'purpose', 'branch', 'subspecies'}: fail(f'{rid}: scope keys')
                identity = {k: v for k, v in r.items() if k not in
                            ('parameter_id', 'producer_provision_version_id', 'effective_from', 'effective_to_exclusive')}
                key = (p['stable_provision_id'], json.dumps(identity, sort_keys=True, ensure_ascii=False))
                for prior in parameter_intervals.setdefault(key, []):
                    if max(r['effective_from'], prior['effective_from']) < min(r['effective_to_exclusive'] or '9999', prior['effective_to_exclusive'] or '9999'):
                        fail(f'{rid}: duplicate parameter overlaps {prior["parameter_id"]}')
                parameter_intervals[key].append(r)
    population = json.loads(population_path.read_text(encoding='utf-8'))
    if set(population) != {'seams'}: fail('population.json may own only the seam partition')
    if set(population['seams']) != {'1', '2', '3', '4'}: fail('population must partition seams 1 to 4')
    flat_population = [vid for s in population['seams'].values() for vid in s]
    pop = set(flat_population)
    if len(pop) != len(flat_population): fail('a Stage A version occurs more than once across the seam partition')
    if pop != set(A):
        fail(f'population is not exactly Stage A: missing={sorted(set(A)-pop)[:5]} extra={sorted(pop-set(A))[:5]}')
    covered = set()
    dseen = set()
    expressions = set()
    by_id = {c['clock_id']: c for c in b['clocks']} | {p['parameter_id']: p for p in b['parameters']}
    owned_expressions = set()
    for d in b['dispositions']:
        minted = d.get('disposition') in ('clock', 'parameter')
        fields = {'provision_version_id', 'disposition', 'ref', 'why', 'aperture'}
        if not minted: fields.add('expression')
        if set(d) != fields: fail(f'disposition field set on {d.get("provision_version_id")}')
        k = json.dumps(d, ensure_ascii=False, sort_keys=True)
        # two identical entries are indistinguishable to any consumer, so one of them carries no fact (F4-07)
        if k in dseen: fail(f'duplicate disposition object on {d["provision_version_id"]}')
        dseen.add(k)
        if d['provision_version_id'] not in A: fail('disposition unknown version')
        if d['disposition'] not in DISP: fail(f'disposition class {d["disposition"]}')
        if d['aperture'] not in APERTURE: fail(f'{d["provision_version_id"]}: aperture class')
        if d['aperture'] == 'DEFERRED' and d['ref'] is not None: fail(f'{d["provision_version_id"]}: deferred expression targets an in-scope row')
        if d['aperture'] == 'EXTERNAL_ANCHOR' and d['disposition'] != 'qualifies_clock':
            fail(f'{d["provision_version_id"]}: external anchor must qualify an included clock')
        expression = d.get('expression')
        if minted:
            if not isinstance(d['ref'], str) or d['ref'] not in by_id:
                fail(f'{d["provision_version_id"]}: minted disposition must name one existing target')
            expected = 'parameter_id' if d['disposition'] == 'parameter' else 'clock_id'
            if expected not in by_id[d['ref']]:
                fail(f'{d["provision_version_id"]}: disposition target kind disagrees')
            if by_id[d['ref']]['producer_provision_version_id'] != d['provision_version_id']:
                fail(f'{d["provision_version_id"]}: minted disposition producer differs from its target')
            expression = by_id[d['ref']]['source_phrase']
        if d['disposition'] == 'open_term' and not expression:
            fail(f'{d["provision_version_id"]}: an open term must retain its exact source expression')
        if expression is not None:
            if norm(expression) not in norm(A[d['provision_version_id']]['source_quote']):
                fail(f'{d["provision_version_id"]}: disposition expression not in producer quote')
            expression_key = (d['provision_version_id'], norm(expression))
            if expression_key in expressions:
                fail(f'{d["provision_version_id"]}: one expression has more than one disposition')
            expressions.add(expression_key)
        # a class that claims a target must name it (review cycle 4, F3-C4-01): no relation asserted in prose alone
        if d['disposition'] in ('clock', 'parameter', 'qualifies_clock', 'implements_clock', 'restates_parameter'):
            if not d['ref']: fail(f'{d["provision_version_id"]}: {d["disposition"]} without a named target')
            refs = d['ref'] if isinstance(d['ref'], list) else [d['ref']]
            if not all(isinstance(ref, str) and ref in by_id for ref in refs):
                fail(f'{d["provision_version_id"]}: disposition ref {d["ref"]} is not a minted row')
            targets = [by_id[ref] for ref in refs]
            expected = 'parameter_id' if d['disposition'] in ('parameter', 'restates_parameter') else 'clock_id'
            if any(expected not in target for target in targets): fail(f'{d["provision_version_id"]}: disposition target kind disagrees')
            if isinstance(d['ref'], list):
                if d['disposition'] in ('clock', 'parameter') or len(refs) < 2 or len(set(refs)) != len(refs):
                    fail(f'{d["provision_version_id"]}: temporal target list shape')
                if len({A[t['producer_provision_version_id']]['stable_provision_id'] for t in targets}) != 1:
                    fail(f'{d["provision_version_id"]}: temporal targets are not versions of one proposition')
                if any(left['effective_to_exclusive'] != right['effective_from'] for left, right in zip(targets, targets[1:])):
                    fail(f'{d["provision_version_id"]}: temporal targets have a gap, overlap or wrong order')
            producer = A[d['provision_version_id']]
            if d['aperture'] != 'EXTERNAL_ANCHOR':
                if (targets[0]['effective_from'] > producer['effective_from'] or
                        (targets[-1]['effective_to_exclusive'] or '9999') < (producer['effective_to_exclusive'] or '9999')):
                    fail(f'{d["provision_version_id"]}: disposition target does not cover the producer interval')
            if d['disposition'] in ('clock', 'parameter'):
                owned_expressions.add(d['ref'])
        if d.get('why') and RETROSPECTIVE.search(d['why']):
            fail(f"{d['provision_version_id']}: exclusion rests on the absence of a held instance; justify it by the expression's effect on the chosen decision chain, not current evidence availability")
        covered.add(d['provision_version_id'])
    if pop != covered: fail(f'disposition coverage differs from population: missing={sorted(pop-covered)[:5]} extra={sorted(covered-pop)[:5]}')
    if owned_expressions != set(by_id): fail(f'minted items without their own expression disposition: {sorted(set(by_id)-owned_expressions)}')
    # closure manifest (review cycle 2, F3-C2-04): an ACCEPTED seam must name the act and the reviewer. This checks that
    # an acceptance was RECORDED, never that it was sound — the act's semantic validity is Owen's, on a human reread.
    seams = population['seams']
    if [m['seam'] for m in b['closure_manifest']] != [1, 2, 3, 4]: fail('closure manifest must carry seams 1 to 4, each exactly once, in order')
    for m in b['closure_manifest']:
        if set(m) != {'seam', 'title', 'status', 'reread',
                      'semantic_reviewer', 'acceptance_act', 'acceptance_evidence', 'semantic_acceptance', 'accepted_content_sha256'}:
            fail(f'closure manifest seam {m.get("seam")}: field set')
        if m['semantic_acceptance'] not in ('ACCEPTED', 'NOT_ASSERTED'): fail(f'closure manifest seam {m["seam"]}: acceptance value')
        if m['semantic_acceptance'] == 'ACCEPTED':
            if not (m['acceptance_act'] and m['semantic_reviewer'] and isinstance(m['acceptance_evidence'], dict)):
                fail(f'closure manifest seam {m["seam"]}: ACCEPTED without a recorded acceptance act, reviewer and evidence record')
            evidence = m['acceptance_evidence']
            if set(evidence) != {'record_path', 'record_sha256'}:
                fail(f'closure manifest seam {m["seam"]}: acceptance evidence shape')
            evidence_path = ROOT / evidence['record_path']
            if not evidence_path.is_file() or sha(evidence_path) != evidence['record_sha256']:
                fail(f'closure manifest seam {m["seam"]}: acceptance evidence missing or changed')
            try:
                record = json.loads(evidence_path.read_text(encoding='utf-8'))
            except (ValueError, UnicodeError):
                fail(f'closure manifest seam {m["seam"]}: evidence is not an acceptance record')
            expected_record = {'schema': 'cordon-stage-b-acceptance-v1', 'seam': m['seam'],
                               'reviewer': m['semantic_reviewer'], 'act': m['acceptance_act'],
                               'accepted_content_sha256': m['accepted_content_sha256']}
            if not isinstance(record, dict) or any(record.get(k) != value for k, value in expected_record.items()):
                fail(f'closure manifest seam {m["seam"]}: evidence does not record this content, reviewer and act')
        # C2: the acceptance is bound to the content it covered — the seam's clocks and parameters, the dispositions
        # that record what was read and excluded, AND the conventions block, because the conventions define what those
        # fields mean (F3-S5-02). Changing a convention reinterprets every accepted row, so it must break the binding
        # exactly as changing a row does. If any of it changes, ACCEPTED stops projecting until the owner accepts again.
        if m['semantic_acceptance'] == 'ACCEPTED':
            fp = acceptance_fingerprint(b, m, seams, stage_a_paths, population_path)
            if m['accepted_content_sha256'] != fp:
                fail(f'closure manifest seam {m["seam"]}: ACCEPTED but its content no longer matches what was accepted')
        elif m['accepted_content_sha256'] is not None or m['acceptance_evidence'] is not None:
            fail(f'closure manifest seam {m["seam"]}: acceptance content or evidence recorded without an acceptance')
        if m['status'] == 'HELD' and seams[str(m['seam'])]:
            fail(f'closure manifest seam {m["seam"]}: a held seam carries no rows and no population')
    if ledger_path.resolve() == B.resolve():
        verify_source_parity(b)
    print('PASS Stage B bounded checks:', json.dumps({k: len(b[k]) for k in ('clocks', 'parameters', 'dispositions')}))
    return b

def verify_source_parity(b):
    parity = json.loads(SOURCE_PARITY.read_text(encoding='utf-8'))
    if parity.get('schema') != 'cordon-source-parity-v1': fail('regional-plan source parity schema')
    for item in parity['instruments']:
        extract = ROOT / item['extract_path']
        if not extract.is_file() or sha(extract) != item['extract_sha256']:
            fail(f"{item['instrument_id']}: admitted source extract missing or changed")
        text = norm(extract.read_text(encoding='utf-8'))
        rows = [r for r in b['clocks'] + b['parameters']
                if r['producer_provision_version_id'].startswith(item['instrument_id'] + ':')]
        transcribed = {}
        if 'reviewed_transcriptions' in item:
            evidence = item['reviewed_transcriptions']
            path = ROOT / evidence['path']
            if not path.is_file() or sha(path) != evidence['sha256']:
                fail('reviewed regional transcription snapshot missing or changed')
            amendment = json.loads(path.read_text(encoding='utf-8'))
            transcribed = {r['parameter_id']: r for r in amendment['stage_b_additions']['parameters']
                           if r['producer_provision_version_id'].startswith(item['instrument_id'] + ':')}
            actual = {r['parameter_id']: {k: v for k, v in r.items()
                                          if k not in {'effective_from', 'effective_to_exclusive'}}
                      for r in rows if r.get('parameter_id') in transcribed}
            if actual != transcribed or len(actual) != item['reviewed_transcription_matches']:
                fail('regional transcriptions differ from the exact reviewed content')
        literal = [r for r in rows if r.get('parameter_id') not in transcribed]
        matched = sum(norm(r['source_phrase']) in text for r in literal)
        if len(rows) != item['stage_b_phrases'] or matched != item['normalized_exact_matches'] or matched + len(transcribed) != len(rows):
            fail(f"{item['instrument_id']}: Stage B phrases no longer match the parity record")


def mutation_tests(stage_a_paths, population_path):
    base = json.loads(B.read_text(encoding='utf-8'))
    def rejected(name, mutant, extra_args=None):
        with tempfile.NamedTemporaryFile('w', suffix='.json', encoding='utf-8') as f:
            json.dump(mutant, f, ensure_ascii=False); f.flush()
            cmd = [sys.executable, str(Path(__file__).resolve()), '--ledger', f.name] + (extra_args or [])
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0: fail(f'mutation survived: {name}')
        print(f'PASS MUTATION: {name}')

    m = copy.deepcopy(base)
    c = next(x for x in m['clocks'] if x['clock_id'] == 'B-CLK-DM169819-14(3)-research-lab-24h')
    c['consumer_decision'] = 'IT-DLGS-19-2021:Art.55(9):notification-violation'
    rejected('route an in-scope notification clock into the deferred sanction chain', m)

    m = copy.deepcopy(base)
    next(x for x in m['dispositions'] if x['disposition'] == 'open_term')['expression'] = None
    rejected('erase the exact phrase of a genuine open term', m)

    m = copy.deepcopy(base)
    ds = [x for x in m['dispositions'] if x['provision_version_id'] == 'IT-PNI-2026:Xylella:Puglia-plant-survey-design:v1' and x['ref'] in
          ('B-PAR-PNI2026-prunus-citrus-design', 'B-PAR-PNI2026-vitis-design')]
    ds[1]['ref'] = ds[0]['ref']
    rejected('assign one referenced expression to two parameter dispositions', m)

    m = copy.deepcopy(base)
    c = next(x for x in m['clocks'] if x['clock_id'] == 'B-CLK-EU-8(2)-v1-vector-control-timing')
    c['completion'] = {'kind': 'none', 'ref': None}
    rejected('mint a clock without its own completion fact', m)

    m = copy.deepcopy(base)
    next(x for x in m['parameters'] if x['parameter_id'] == 'B-PAR-EU-2(4)-v2-C80-p1')['value']['design_prevalence'] = '999'
    rejected('change a normalized parameter value without changing its source phrase', m)

    m = copy.deepcopy(base)
    recurrence = next(x for x in m['clocks'] if x['clock_id'] == 'B-CLK-EU-5(1)(d)-vector-tests-twice-in-flight-season')
    recurrence['magnitude'], recurrence['bound'], recurrence['unit'] = '2', 'exact', 'years'
    rejected('collapse recurrence occurrence count back into cadence fields', m)

    population = json.loads(population_path.read_text(encoding='utf-8'))
    with tempfile.NamedTemporaryFile('w', suffix='.json', encoding='utf-8') as changed_population:
        duplicate = copy.deepcopy(population)
        duplicate['seams']['2'].append(duplicate['seams']['1'][0])
        json.dump(duplicate, changed_population, ensure_ascii=False); changed_population.flush()
        rejected('duplicate one Stage A version across two seams', base, ['--population', changed_population.name])

    with tempfile.NamedTemporaryFile('w', suffix='.json', encoding='utf-8') as changed_population:
        shortened = copy.deepcopy(population)
        producers = {x['producer_provision_version_id'] for x in base['clocks'] + base['parameters']}
        victim = next(v for values in shortened['seams'].values() for v in values if v not in producers)
        for values in shortened['seams'].values():
            if victim in values: values.remove(victim)
        mutant = copy.deepcopy(base)
        mutant['dispositions'] = [x for x in mutant['dispositions'] if x['provision_version_id'] != victim]
        json.dump(shortened, changed_population, ensure_ascii=False); changed_population.flush()
        rejected('remove a no-mint Stage A producer, its disposition and its population membership together', mutant,
                 ['--population', changed_population.name])

    manifest = base['closure_manifest'][0]
    seams = population['seams']
    original_fp = acceptance_fingerprint(base, manifest, seams, stage_a_paths, population_path)
    with tempfile.NamedTemporaryFile('wb', suffix='.json') as changed_a:
        changed_a.write(stage_a_paths[0].read_bytes() + b'\n'); changed_a.flush()
        changed_fp = acceptance_fingerprint(base, manifest, seams, (Path(changed_a.name), stage_a_paths[1]), population_path)
        if changed_fp == original_fp: fail('acceptance fingerprint survived an upstream Stage A byte change')
        print('PASS MUTATION: acceptance fingerprint changes with upstream Stage A bytes')
    with tempfile.NamedTemporaryFile('wb', suffix='.json') as changed_population:
        changed_population.write(population_path.read_bytes() + b'\n'); changed_population.flush()
        changed_fp = acceptance_fingerprint(base, manifest, seams, stage_a_paths, Path(changed_population.name))
        if changed_fp == original_fp: fail('acceptance fingerprint survived a population byte change')
        print('PASS MUTATION: acceptance fingerprint changes with population bytes')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mutation-test', action='store_true')
    parser.add_argument('--ledger', type=Path, default=B)
    parser.add_argument('--stage-a-eu', type=Path, default=ROOT / STAGE_A_LOGICAL[0])
    parser.add_argument('--stage-a-jurisdiction', type=Path, default=ROOT / STAGE_A_LOGICAL[1])
    parser.add_argument('--population', type=Path, default=POPULATION)
    args = parser.parse_args()
    stage_a_paths = (args.stage_a_eu, args.stage_a_jurisdiction)
    main(args.ledger, stage_a_paths, args.population)
    if args.mutation_test:
        mutation_tests(stage_a_paths, args.population)
