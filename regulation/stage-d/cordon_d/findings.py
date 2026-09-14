"""Attach literal report rows to the accepted distinct-observation stream."""
from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .reports import Report, report


def document_name(route):
    parts = urlsplit(route)
    return parse_qs(parts.query).get('nomeFile', [parts.path])[0].rsplit('/', 1)[-1]


def _captures(root, known_through):
    if known_through.tzinfo is None or known_through.utcoffset() is None:
        raise ValueError('A knowledge cutoff must be timezone-aware')
    by_route = defaultdict(list)
    for capture in json.loads((root / 'records.json').read_text()):
        at = datetime.fromisoformat(capture['captured_at'])
        if at.tzinfo is None:
            raise ValueError('Capture has no timezone')
        if at <= known_through:
            by_route[capture['url']].append(capture)
    return by_route


def _comparable(member, results):
    """Per-column cross-check only. No overall positive/negative verdict is inferred."""
    labels = {'published-positive': True, 'published-positive-and-removal-label': True,
              'published-negative': False}
    expected = labels.get(member.result)
    comparisons = []
    for value in results:
        target = ' '.join((value.analyte or '').casefold().split())
        # These are explicit equivalences of stated labels, not inference from view names.
        species = target in {'xylella fastidiosa', 'x. fastidiosa'}
        subspecies = bool(member.subspecies and target in {
            f'xylella fastidiosa subsp. {member.subspecies.casefold()}',
            f'x. fastidiosa subsp. {member.subspecies.casefold()}'})
        positive = value.kind in {'positive', 'detected'}
        negative = value.kind in {'negative', 'not-detected'}
        reason = None
        if expected is None:
            reason = 'the published label is not a binary analytical result this reader compares'
        elif not value.analyte:
            reason = 'no analyte recovered for this reported result'
        elif not (species or subspecies):
            reason = 'the recovered analyte does not supply the compared species/subspecies level'
        elif not (positive or negative):
            reason = 'the reported literal is not classified as detected or not detected by this reader'
        verdict = 'not comparable' if reason else 'agree' if expected == positive else 'disagree'
        comparisons.append({'result_locator': value.locator, 'verdict': verdict, 'cause': reason,
                            'level': 'subspecies' if subspecies else 'species' if species else None,
                            'published_label': member.result, 'reported_literal': value.text})
    return comparisons


def _repeated_representations(candidates):
    """Relate source-supported repetitions; keep every row and result occurrence."""
    rows = [c['row'] for c in candidates.values()]
    if len({r.page for r in rows}) != 1:
        return False
    tables = {r.locator.split('/')[1] for r in rows}
    if len(tables) != len(rows):
        return False  # Repeated rows within one table are not a second representation.
    common = set.intersection(*[{f['id'] for f in row.facts
        if f['role'] == 'repeated_representation' and tables <= set(f['applies_to'])}
        for row in rows])
    if not common:
        return False
    def values(row):
        if any(c['text'] is None and c.get('cause') != 'not_stated' for c in row.cells):
            return None
        cells = sorted((tuple(c['heading']), c['role'], ' '.join((c['text'] or '').split())) for c in row.cells)
        facts = sorted(json.dumps({k: f.get(k) for k in ('role', 'text', 'value', 'section')}, sort_keys=True)
                       for f in row.facts if f['role'] != 'repeated_representation')
        results = [(r.assay, r.analyte, r.text) for r in row.results]
        return cells, facts, results
    first = values(rows[0])
    return first is not None and all(values(r) == first for r in rows[1:])


def findings(groups, reports_root: Path, store: Path, *, extraction_version, known_through):
    """One output per accepted observation identity; unresolved candidates never disappear.

    Index only routed observations. The caller supplies the full accepted stream.
    This function performs no acquisition, model calls or observation regrouping.
    """
    captures = _captures(reports_root, known_through)
    by_name, readings = defaultdict(set), {}
    for route, versions in captures.items():
        for capture in versions:
            if digest := capture.get('sha256'):
                by_name[document_name(route)].add(digest)
                if digest not in readings:
                    readings[digest] = report(digest, store, extraction_version=extraction_version)
    row_index = {}
    for digest, reading in readings.items():
        if isinstance(reading, Report):
            index = defaultdict(list)
            for row in reading.rows:
                if row.candidate_reference is not None:
                    index[row.candidate_reference].append(row)
            row_index[digest] = index
    routed, reverse = [], defaultdict(set)
    for group in groups:
        output = {'observation': group, 'links': [], 'limitations': [], 'matches': []}
        if not group.report_routes:
            output['limitations'].append('no report route recovered in the observation reading')
            yield output
            continue
        eligible = {}
        for member in group.members:
            for route_field, route in member.report_routes:
                versions = captures.get(route, [])
                digests = {v['sha256'] for v in versions if 'sha256' in v}
                if not digests:
                    output['links'].append({'route': route, 'route_field': route_field, 'member': member,
                        'status': 'source route not acquired at knowledge cutoff',
                        'alternative_candidates': sorted(by_name.get(document_name(route), set()))})
                    continue
                for digest in sorted(digests):
                    reading = readings[digest]
                    link = {'route': route, 'route_field': route_field, 'member': member, 'sha256': digest, 'candidates': [],
                            'rendition_ambiguity': len(digests) > 1}
                    output['links'].append(link)
                    if not isinstance(reading, Report):
                        link['status'] = reading.cause
                        continue
                    link['reading_issues'] = reading.issues
                    if not group.correlatable:
                        link['status'] = group.uncorrelated_because or 'observation identity unresolved'
                        continue
                    rows = row_index[digest].get(group.reference, [])
                    link['status'] = 'candidates recovered' if rows else 'publisher reference not recovered in reading'
                    for row in rows:
                        key = digest, row.locator
                        dated = row.sampling_date
                        temporal = ('agrees' if dated == group.day else 'conflicts') if dated else 'unresolved'
                        candidate = {'row': row, 'key': key, 'temporal': temporal,
                                     'date_cause': row.date_cause,
                                     'identity_cause': ('publisher identifier reading remains unresolved'
                                                        if row.reference is None else None),
                                     'reading_issues': reading.issues,
                                     'reading_complete': len(reading.complete_pages) == reading.pages,
                                     'comparisons': _comparable(member, row.results)}
                        link['candidates'].append(candidate)
                        if candidate['identity_cause']:
                            output['limitations'].append({'sha256': digest, 'row': row.locator,
                                                         'cause': candidate['identity_cause']})
                        if row.reference is not None and temporal != 'conflicts' and len(digests) == 1:
                            eligible[key] = candidate
                            reverse[key].add(group.identity)
        routed.append((output, eligible))
    for output, eligible in routed:
        identity = output['observation'].identity
        by_document = defaultdict(dict)
        for key, candidate in eligible.items():
            by_document[key[0]][key] = candidate
        output['ambiguities'] = []
        for digest, candidates in by_document.items():
            repeated = len(candidates) > 1 and _repeated_representations(candidates)
            if len(candidates) != 1 and not repeated:
                output['ambiguities'].append({'sha256': digest,
                    'cause': 'observation has several eligible source-row occurrences'})
                continue
            if any(reverse[key] != {identity} for key in candidates):
                output['ambiguities'].append({'sha256': digest,
                    'cause': 'report row has several eligible observation identities'})
                continue
            for candidate in candidates.values():
                if repeated:
                    candidate['relationship_basis'] = 'model-proposed repeated representation; all recovered fields and qualifications agree'
                output['matches'].append(candidate)
        if output['matches']:
            output['status'] = ('matched' if all(c['reading_complete'] and c['temporal'] == 'agrees' for c in output['matches'])
                                else 'provisional-match')
        elif output['ambiguities']:
            output['status'] = '; '.join(a['cause'] for a in output['ambiguities'])
        else:
            output['status'] = 'no eligible source-row relationship established'
        yield output


def report_rows(readings, joined):
    """Reverse view: retain every source-row occurrence, including unmatched negatives."""
    matched = defaultdict(set)
    for finding in joined:
        for item in finding['matches']:
            matched[item['key']].add(finding['observation'].identity)
    for reading in readings:
        if isinstance(reading, Report):
            for row in reading.rows:
                yield {'sha256': reading.sha256, 'row': row,
                       'reading_issues': reading.issues,
                       'observations': sorted(matched[(reading.sha256, row.locator)], key=str)}


def confirmation_inputs(joined, *, result_pair, qualification):
    """Project explicitly selected source results to C; never infer legal qualifications.

    qualification supplies already source-supported C inputs. Unavailable inputs
    stay unknown. This is a consumer adapter, not a second evidence-adjudication owner.
    """
    from cordon_c.core import Evaluation, conjunction
    if joined.get('status') not in {'matched', 'provisional-match'}:
        raise ValueError('An unambiguous source relationship is required')
    if len(result_pair) != 2 or result_pair[0] == result_pair[1]:
        raise ValueError('Select two distinct (source hash, result locator) occurrences')
    eligible = []
    for match in joined['matches']:
        results = {(match['key'][0], r.locator): r for r in match['row'].results}
        if all(tuple(key) in results for key in result_pair):
            eligible.append((match, results))
    if len(eligible) != 1:
        raise ValueError('Selected results must belong to one unambiguous joined source row')
    candidate, results = eligible[0]
    first, second = (results[tuple(key)] for key in result_pair)
    def missing(name):
        return Evaluation(None, needs=frozenset({name}))
    def positive(value):
        if value.kind in {'positive', 'detected'}:
            return Evaluation(True)
        if value.kind in {'negative', 'not-detected'}:
            return Evaluation(False)
        return missing('classifiable reported result: ' + value.locator)
    output = {}
    for prefix, result in [('first', first), ('second', second)]:
        polarity = (positive(result) if candidate['reading_complete'] else
                    missing('unread report scope may qualify selected result: ' + result.locator))
        output[prefix + '_positive_annex_iv'] = conjunction([
            polarity,
            qualification.get(prefix + '_annex_iv', missing('Annex IV qualification: ' + result.locator))])
        # Displayed headings remain on Result; canonical identities need their own support.
        output[prefix + '_test'] = qualification.get(prefix + '_test')
        output[prefix + '_sample'] = qualification.get(prefix + '_sample')
        output[prefix + '_extract'] = qualification.get(prefix + '_extract')
        output[prefix + '_genome_target'] = qualification.get(prefix + '_genome_target')
    output['same_extract_route_appropriate'] = qualification.get(
        'same_extract_route_appropriate', missing('appropriateness of shared-extract route'))
    output['inside_demarcated_area'] = qualification.get(
        'inside_demarcated_area', missing('event-time demarcated-area relationship'))
    return output
