"""Attach literal report rows to the accepted distinct-observation stream."""
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .reports import Report, report, record_rows
from .monitoring import day as observation_day
from .report_relations import correspondences, related, replacements, current_limitation, norm, dated


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
    # A failed transport can have a source-reconciled copy at another retained
    # route. Keep the failed request intact and carry the recovery evidence.
    recovered = []
    for route, captures in by_route.items():
        for capture in captures:
            recovery = capture.get('document_recovery')
            if not recovery:
                continue
            established = datetime.fromisoformat(recovery['established_at'])
            if established.tzinfo is None:
                raise ValueError('Document recovery has no timezone')
            if established > known_through:
                continue
            if not recovery.get('identity') or not recovery.get('support'):
                raise ValueError('Document recovery requires source identity and located support')
            alternatives = by_route.get(recovery['url'], [])
            if not any(c.get('sha256') == recovery['sha256'] for c in alternatives):
                raise ValueError('Recovered document is not acquired at the knowledge cutoff')
            recovered.append((route, {'sha256': recovery['sha256'],
                                     'document_recovery': recovery}))
    for route, capture in recovered:
        by_route[route].append(capture)
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
    """Derive equal report displays; keep every row and result occurrence."""
    rows = [c['row'] for c in candidates.values()]
    if not rows or not rows[0].identifiers or len({row.identifiers for row in rows}) != 1:
        return False
    tables = {r.locator.split('/')[1] for r in rows}
    if len(tables) != len(rows):
        return False  # Repeated rows within one table are not a second representation.
    def values(row):
        if any(c['text'] is None and c.get('cause') != 'not_stated' for c in row.cells):
            return None
        cells = sorted((tuple(c['heading']), c['role'], c.get('section') or '', ' '.join((c['text'] or '').split()))
                       for c in row.cells if c['text'] and c['text'].strip())
        results = [(r.assay, r.analyte, r.text) for r in row.results]
        return cells, results, row.sampling_date, row.date_cause
    sections = {frozenset(f['section'].split('/', 1)[-1] for f in row.facts if f.get('section'))
                for row in rows}
    if len(sections - {frozenset()}) > 1:
        return False
    first = values(rows[0])
    return first is not None and all(values(r) == first for r in rows[1:])


def _coordinate_relation(row, association):
    """Compare literal pairs at the referring source's published precision.

    This is derived occurrence evidence inside an explicitly named report, never
    a free spatial join or a declaration that two identifier strings are aliases.
    """
    for role in ('latitude', 'longitude'):
        cells = [c for c in row.cells if c['role'] == role]
        if any(c.get('role_cause') or c.get('reading_issues') for c in cells):
            return 'unresolved'
        values = [c['text'] for c in cells if c.get('text') is not None]
        printed = association['fields'].get(role, {}).get('text')
        if len(values) != 1 or not printed:
            return 'unresolved'
        try:
            expected = Decimal(''.join(printed.split()).replace(',', '.'))
            actual = Decimal(''.join(values[0].split()).replace(',', '.'))
            if not expected.is_finite() or not actual.is_finite():
                return 'unresolved'
            # A reported integer coordinate is insufficient precision for this relation.
            if expected.as_tuple().exponent >= 0:
                return 'unresolved'
            if abs(actual - expected) > Decimal(5).scaleb(expected.as_tuple().exponent - 1):
                return 'conflicts'
        except InvalidOperation:
            return 'unresolved'
    return 'agrees at published decimal precision'


def _associations(reading, records):
    if not reading.relations:
        return []
    identity = reading.relations['identity']
    number, day = identity.get('number'), dated(identity.get('date'))
    if not number or not day:
        return []
    labels = [label['value'] for label in identity.get('issuer_labels', [])]
    primary_tokens = re.findall(r'(?<!\w)[A-ZÀ-ÖØ-Þ]{2,}(?!\w)', identity.get('issuer') or '')
    labels.extend(primary_tokens)
    result = []
    for record in records:
        fields = record['fields']
        reference = fields.get('report_reference', {}).get('text', '')
        literal_issuer = any(re.search(r'(?<!\w)' + re.escape(norm(label)) + r'(?!\w)', norm(reference))
                             for label in labels if norm(label))
        if (literal_issuer
                and re.search(r'(?<![\w/])' + re.escape(norm(number)) + r'(?![\w/])', norm(reference))
                and dated(''.join(fields.get('report_date', {}).get('text', '').split())) == day):
            result.append(record)
    return result


def _monitoring_associations(group, route):
    """Use an accepted observation's explicit report reference and native degrees.

    No transformed coordinate acquires invented decimal precision. Source members
    remain linked through the observation reader's existing identity, not proximity.
    """
    positions = [m for m in group.members if m.coordinates and m.crs == 'EPSG:4326']
    result = []
    for member in group.members:
        if route not in {url for _, url in member.report_routes}:
            continue
        carried = dict(member.carried)
        references = {norm(carried[key]): carried[key] for key in ('PROT_SELGE', 'PROTOCOLLO')
                      if carried.get(key)}
        date_text = carried.get('DATA_PROT_SELGE')
        if len(references) != 1 or not date_text:
            continue
        reference = next(iter(references.values()))
        try:
            raw_date = int(date_text) if member.locator.startswith('feature:') and date_text.isdecimal() else date_text
            date = observation_day(raw_date, arcgis=member.locator.startswith('feature:'))
        except (ValueError, OverflowError, OSError):
            continue
        if date is None:
            continue
        for position in positions:
            # A float's synthetic .0 must not turn integer degrees into decimal evidence.
            if any(value.is_integer() for value in position.coordinates):
                continue
            fields = {'plant_id': group.reference, 'report_reference': reference,
                      'report_date': date.isoformat(), 'longitude': str(position.coordinates[0]),
                      'latitude': str(position.coordinates[1])}
            if position.species:
                fields['host'] = position.species
            result.append({'fields': {key: {'text': value} for key, value in fields.items()},
                'source_kind': 'monitoring publication',
                'support': [{'sha256': m.sha256, 'locator': m.locator, 'release': m.release}
                            for m in (member, position)],
                'report_date_literal': date_text, 'issues': list(member.issues + position.issues)})
    return result


def _host_relation(row, association):
    printed = association['fields'].get('host', {}).get('text')
    if not printed:
        return 'not supplied by source association'
    cells = [cell for cell in row.cells if cell['role'] == 'host']
    if any(cell.get('role_cause') or cell.get('reading_issues') for cell in cells):
        return 'unresolved'
    values = [cell['text'] for cell in cells if cell.get('text') is not None]
    if len(values) != 1:
        return 'unresolved'
    def labels(value):
        result = {norm(value), norm(re.sub(r'\s*\([^)]*\)\s*$', '', value))}
        # A printed binomial beside a common name is an explicit second label.
        match = re.search(r'\(([A-Z][a-z]+ [a-z]+)\)\s*$', value)
        if match:
            result.add(norm(match[1]))
        return result
    return 'agrees on printed host' if labels(values[0]) & labels(printed) else 'conflicts'


def findings(groups, reports_root: Path, store: Path, *, extraction_version, known_through, association_readings=()):
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
    edges = correspondences(readings)
    association_index = defaultdict(list)
    for source in association_readings:
        for association in source.rows:
            reference = ''.join(association['fields'].get('plant_id', {}).get('text', '').split())
            if reference:
                association_index[reference].append(dict(association,
                    reading_issues=source.issues, reading_scope=source.scope))
    row_index, records_by_document = {}, {}
    for digest, reading in readings.items():
        if isinstance(reading, Report):
            index = defaultdict(list)
            records_by_document[digest] = record_rows(reading)
            for row in records_by_document[digest]:
                for identifier in row.identifiers:
                    index[identifier].append(row)
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
                superseded = {e['predecessor'] for e in edges
                              if e['effect'] == 'replaces' and e['status'] == 'resolved'}
                destinations = {}
                for routed_digest in sorted(digests):
                    for destination, chain in replacements(edges, routed_digest).items():
                        destinations.setdefault(destination, chain)
                rendition_ambiguity = len(set(destinations) - superseded) > 1
                for digest, chain in sorted(destinations.items()):
                    reading = readings[digest]
                    link = {'route': route, 'route_field': route_field, 'member': member, 'sha256': digest, 'candidates': [],
                            'rendition_ambiguity': rendition_ambiguity}
                    link['route_recoveries'] = [v['document_recovery'] for v in versions
                        if v.get('sha256') in digests and v.get('document_recovery')]
                    output['links'].append(link)
                    link['document_relationships'] = related(edges, digest)
                    link['replacement_chain'] = chain
                    link['document_cause'] = current_limitation(edges, digest)
                    if not isinstance(reading, Report):
                        link['status'] = reading.cause
                        continue
                    link['reading_issues'] = reading.issues
                    link['relationship_reading'] = reading.relations
                    if reading.relations is None:
                        link['document_cause'] = 'current relationship inventory unread'
                    elif reading.relations.get('reading_complete') is not True:
                        link['document_cause'] = 'current relationship inventory incomplete'
                    if not group.correlatable:
                        link['status'] = group.uncorrelated_because or 'observation identity unresolved'
                        continue
                    source_links = _associations(reading, [*association_index.get(group.reference, []),
                                                          *_monitoring_associations(group, route)])
                    link['source_associations'] = source_links
                    coordinate_links = {row.locator: [_coordinate_relation(row, a) for a in source_links]
                                        for row in records_by_document[digest]} if source_links else {}
                    host_links = {row.locator: [_host_relation(row, a) for a in source_links]
                                  for row in records_by_document[digest]} if source_links else {}
                    link['association_comparisons'] = coordinate_links
                    derived = {row.locator for row in records_by_document[digest] if source_links
                        and len(reading.complete_pages) == reading.pages
                        and all(value == 'agrees at published decimal precision' for value in coordinate_links[row.locator])
                        and all(value in {'agrees on printed host', 'not supplied by source association'}
                                for value in host_links[row.locator])
                        and not any(a.get('issues') for a in source_links)}
                    # Every compatible row competes. Result polarity cannot select identity.
                    rows = [row for row in records_by_document[digest] if row in row_index[digest].get(group.reference, [])
                            or row.locator in derived]

                    link['status'] = 'candidates recovered' if rows else 'publisher reference not recovered in reading'
                    for row in rows:
                        key = digest, row.locator
                        dated = row.sampling_date
                        temporal = ('agrees' if dated == group.day else 'conflicts') if dated else 'unresolved'
                        association_cause = None
                        if 'conflicts' in coordinate_links.get(row.locator, []):
                            association_cause = 'source plant-to-report association conflicts with report-row coordinates'
                        elif 'conflicts' in host_links.get(row.locator, []):
                            association_cause = 'source plant-to-report association conflicts with report-row host'
                        elif 'unresolved' in host_links.get(row.locator, []):
                            association_cause = 'report-row host needed by the source association remains unresolved'
                        derived_identity = row.locator in derived
                        exact_identity = group.reference in row.identifiers
                        candidate = {'row': row, 'key': key, 'temporal': temporal,
                                     'result_cause': None if row.results else 'no analytical result recovered for this occurrence',
                                     'date_cause': row.date_cause,
                                     'identity_cause': ('no literal report-row identifier or source association establishes this observation'
                                                        if not exact_identity and not derived_identity else None),
                                     'association_cause': association_cause,
                                     'source_associations': source_links,
                                     'association_comparisons': coordinate_links.get(row.locator, []),
                                     'host_comparisons': host_links.get(row.locator, []),
                                     'identity_basis': ('derived occurrence correspondence: observation route, source report identity/date, host and unique coordinates at published precision; client identifiers remain distinct'
                                                        if derived_identity else 'literal identifier equality within the observation’s explicit report route'),
                                     'reading_issues': reading.issues,
                                     'document_cause': link['document_cause'],
                                     'reading_complete': (len(reading.complete_pages) == reading.pages
                                         and reading.relations is not None
                                         and reading.relations.get('reading_complete') is True),
                                     'comparisons': _comparable(member, row.results)}
                        link['candidates'].append(candidate)
                        if candidate['identity_cause']:
                            output['limitations'].append({'sha256': digest, 'row': row.locator,
                                                         'cause': candidate['identity_cause']})
                        if row.results and (exact_identity or derived_identity) and not association_cause and not link['document_cause'] and temporal != 'conflicts' and not rendition_ambiguity:
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
                    candidate['relationship_basis'] = 'derived repeated display: populated fields and analytical results agree; each occurrence retains its own qualifications'
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
    readings = list(readings)
    edges = correspondences({r.sha256: r for r in readings})
    matched = defaultdict(set)
    for finding in joined:
        for item in finding['matches']:
            matched[item['key']].add(finding['observation'].identity)
            for part in (item['row'].projection or {}).get('parts', ()):
                matched[(item['key'][0], part)].add(finding['observation'].identity)
    for reading in readings:
        if isinstance(reading, Report):
            for row in reading.rows:
                yield {'sha256': reading.sha256, 'row': row,
                       'reading_issues': reading.issues,
                       'document_relationships': related(edges, reading.sha256),
                       'relationship_reading': reading.relations,
                       'document_cause': current_limitation(edges, reading.sha256),
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
