"""Correspond declared administrative references; do not compose operative work."""
from datetime import date

from cordon_c.core import MissingInput
from .removal_events import act_id


def _source(reading):
    sources = reading.response.get('request', {}).get('sources', ())
    return sources[0] if sources else None


def _identity(act):
    """Use typed components only; leave the declaration and its unknowns untouched."""
    if act.get('authority') == 'other':
        return None, None, 'cited act belongs to another authority outside this removal-measure resolver'
    missing = [] if act.get('number') else ['number']
    if act.get('authority') != 'puglia-osservatorio':
        missing.append('resolved Osservatorio issuing authority')
    number = act.get('number')
    if number and (not number.isascii() or not number.isdecimal()):
        return None, None, 'cited act number is not an unambiguous numeric act number'
    adopted = None
    if act.get('adopted') is not None:
        try:
            adopted = date.fromisoformat(act['adopted'])
        except (TypeError, ValueError):
            return None, None, 'cited adoption date is not an exact ISO calendar day'
    year = act.get('year')
    if year is not None:
        if not isinstance(year, str) or len(year) != 4 or not year.isascii() or not year.isdecimal():
            return None, adopted, 'cited act year is not an explicit four-digit year'
        if adopted and int(year) != adopted.year:
            return None, adopted, 'cited act year conflicts with its explicit adoption date'
    elif adopted:
        year = str(adopted.year)
    else:
        missing.append('year or exact adoption date')
    if not act.get('support'):
        missing.append('source support')
    if missing:
        return None, adopted, 'cited act lacks ' + ', '.join(missing)
    return act_id(number, year), adopted, None


def _reading_identity(reading):
    try:
        return reading.identity, reading.adopted, None
    except (MissingInput, ValueError, TypeError) as error:
        return None, None, str(error)


def _result(reference, *, act=None, selection=None, candidates=(), reading=None,
            cause=None, conflicts=()):
    return dict(reference=reference, act=act, selection=selection,
                candidates=tuple(candidates), reading=reading, cause=cause,
                conflicts=tuple(conflicts))


def referenced_measures(measure, readings):
    """Return independent source claims and their existing, original reading objects.

    An act identity can resolve without supplying the predecessor to extraction.
    A selected document resolves by its principal source hash, never a context hash.
    Neither correspondence applies a correction, selects a current version, or
    imports any target. Repeated references retain their own affected payloads.
    """
    readings = tuple(readings)
    identities = [(reading, *_reading_identity(reading)) for reading in readings]
    results = []
    for reference in measure.values['references']:
        acts = reference.get('acts', [])
        declarations = [(act, *_identity(act)) for act in acts]
        for act, identity, adopted, cause in declarations:
            candidates, matches, conflicts = [], [], []
            if identity is not None:
                for reading, candidate_id, candidate_date, _ in identities:
                    if candidate_id != identity:
                        continue
                    candidates.append(reading)
                    if adopted is not None and candidate_date != adopted:
                        conflicts.append(dict(reading=reading,
                            cause='cited adoption date conflicts with the retained measure adoption date'))
                    else:
                        matches.append(reading)
                if len(matches) > 1:
                    cause = 'cited act is ambiguous among supplied measure readings'
                elif not matches:
                    cause = ('cited adoption date conflicts with every supplied reading of this act'
                             if conflicts else 'no supplied measure reading identifies the cited act')
            results.append(_result(reference, act=act, candidates=candidates,
                reading=matches[0] if len(matches) == 1 else None, cause=cause, conflicts=conflicts))

        for selection in reference.get('documents', []):
            candidates = [reading for reading in readings if _source(reading) == selection['source']]
            # A laboratory or governing-law document is not a missing removal act.
            if not candidates and not acts and reference['relationship'] in {'laboratory-evidence', 'governing-law'}:
                continue
            conflicts = []
            if not candidates:
                cause = 'selected document has no supplied principal measure reading'
            elif len(candidates) > 1:
                cause = 'selected document has multiple supplied measure readings'
            else:
                identity, adopted, problem = _reading_identity(candidates[0])
                cause = 'selected measure identity is unresolved: ' + problem if problem else None
                # Explicit component contradictions cannot be bypassed by a hash
                # selection from the same compound reference.
                if cause is None and declarations:
                    matches_declaration = any(identity == d[1] and (d[2] is None or adopted == d[2])
                                              for d in declarations)
                    contradictory_year = any(
                        d[0].get('year') and d[2] is not None and
                        d[0]['year'] != str(d[2].year) for d in declarations)
                    if not matches_declaration and (contradictory_year or all(d[1] is not None for d in declarations)):
                        cause = 'selected measure conflicts with every declared act identity in this reference'
                        conflicts.append(dict(reading=candidates[0], cause=cause))
            results.append(_result(reference, selection=selection, candidates=candidates,
                reading=candidates[0] if cause is None else None, cause=cause, conflicts=conflicts))

        if (not acts and not reference.get('documents') and
                reference['relationship'] not in {'laboratory-evidence', 'governing-law'}):
            results.append(_result(reference,
                cause='reference has no structured act identity or selected document'))
    return tuple(results)
