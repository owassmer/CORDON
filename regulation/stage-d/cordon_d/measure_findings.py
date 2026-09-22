"""Attach prescribed source positions to existing, source-routed findings."""
from collections import defaultdict

from .findings import _coordinate_relation, _host_relation


def measure_findings(measure, *, report_population, findings, report_rows):
    """Consume a source-bound report population; never discover it from plant IDs.

    ``report_population`` maps report hashes to bindings established by the caller
    from this measure's source references. Bindings, findings and reverse rows stay
    attached unchanged. A match is an occurrence relationship, not confirmation,
    standing or proof that the report population or removal history is complete.
    """
    candidates_by_reference = defaultdict(list)
    for finding in findings:
        accepted = {tuple(m['key']) for m in finding['matches']}
        # Several publication routes can reach the same report occurrence.
        # Their complete evidence stays on finding, without inventing rivals.
        candidates = {tuple(m['key']): m for link in finding['links']
                      for m in link.get('candidates', ())}
        candidates.update((tuple(m['key']), m) for m in finding['matches'])
        for key, match in candidates.items():
            if key[0] in report_population:
                references = {finding['observation'].reference, *match['row'].identifiers} - {None, ''}
                for reference in references:
                    candidates_by_reference[reference].append((finding, key, match, key in accepted))
    reverse = defaultdict(list)
    for item in report_rows:
        if item['sha256'] in report_population:
            reverse[(item['sha256'], item['row'].locator)].append(item)

    outputs = []
    for target in measure.prescribed_targets():
        output = dict(measure=measure.identity, target=target,
                      report_population=report_population, candidates=[],
                      matches=[], status='unresolved', causes=[])
        outputs.append(output)
        field_issue = target.get('native_field_issue')
        if field_issue:
            output['causes'].append(field_issue)
        reference = target['reference']
        if not reference:
            output['causes'].append('the prescribed position has no plant identifier')
            continue
        for finding, key, match, accepted in candidates_by_reference[reference]:
            observation = finding['observation']
            association = {'fields': target['fields']}
            coordinates = (_coordinate_relation(match['row'], association)
                           if any(role in target['fields']
                                  for role in ('latitude', 'longitude'))
                           else 'not supplied by target')
            host = _host_relation(match['row'], association)
            causes = []
            binding = report_population[key[0]]
            if ('target_occurrences' in binding
                    and target['occurrence'] not in binding['target_occurrences']):
                causes.append('source report binding does not apply to this prescribed position')
            if binding.get('cause'):
                causes.append(binding['cause'])
            if field_issue:
                causes.append(field_issue)
            if not accepted:
                causes.append('ordinary finding has not resolved this report occurrence')
            if coordinates in {'conflicts', 'unresolved'}:
                causes.append('target/report coordinates ' + coordinates)
            if host in {'unresolved label equivalence', 'unresolved'}:
                causes.append('target/report host ' + host)
            reversed_rows = tuple(reverse.get(key, ()))
            if not reversed_rows:
                causes.append('reverse report occurrence is unavailable')
            elif any({tuple(identity) for identity in item['observations']}
                     != {observation.identity} for item in reversed_rows):
                causes.append('reverse report occurrence is not unique to this observation')
            output['candidates'].append(dict(
                finding=finding, match=match, report_binding=binding,
                reverse_rows=reversed_rows, coordinate_relation=coordinates,
                host_relation=host, causes=tuple(causes)))

        eligible = [c for c in output['candidates'] if not c['causes']]
        identities = {c['finding']['observation'].identity for c in eligible}
        if len(identities) > 1:
            output['causes'].append('the prescribed position has several eligible findings')
        elif eligible:
            output['matches'] = eligible
        elif output['candidates']:
            output['causes'].extend(dict.fromkeys(
                cause for c in output['candidates'] for cause in c['causes']))
        else:
            output['causes'].append('no finding occurrence in the source-bound report population')

    # Position indexes matter: repeated identifiers or occurrence strings must not
    # collapse two prescribed positions into one. Other acts are outside this scope.
    positions = defaultdict(set)
    for index, output in enumerate(outputs):
        for candidate in output['candidates']:
            if not candidate['causes']:
                positions[candidate['finding']['observation'].identity].add(index)
    for output in outputs:
        if any(len(positions[c['finding']['observation'].identity]) > 1
               for c in output['matches']):
            output['causes'].append('the finding has several prescribed positions in this act')
            output['matches'] = []
        if output['matches']:
            complete = all(c['finding'].get('status') == 'matched'
                           and c['match'].get('reading_complete') is True
                           for c in output['matches'])
            output['status'] = 'matched' if complete else 'provisional-match'
        for name in ('candidates', 'matches', 'causes'):
            output[name] = tuple(dict.fromkeys(output[name]) if name == 'causes'
                                 else output[name])
    return tuple(outputs)
