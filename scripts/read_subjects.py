#!/usr/bin/env python3
"""Reconcile the whole established stream through observed-subject consumers."""
from collections import Counter
from datetime import date, datetime, timezone
import argparse
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'regulation/stage-c'),str(ROOT/'regulation/stage-d')]
from cordon_d.hosts import HostNames
from cordon_d.monitoring import distinct_observations
from cordon_d.subjects import (Municipalities, inspection_units, observed_subjects, finding_host,
                               cadastral_memberships, subject_with_finding)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report-reading-version', help='Explicit retained report revision; never launches extraction')
    parser.add_argument('--area-date', type=date.fromisoformat, help='Evaluate published locations against this area date; defaults to observation date')
    parser.add_argument('--subject-reading', action='append', default=[], help='Exact retained subject-reading request SHA256; replay only')
    args = parser.parse_args()
    names = HostNames.load(ROOT)
    municipalities = Municipalities.load(ROOT)
    factory = lambda: distinct_observations(ROOT/'corpus/sources/monitoring')
    units = inspection_units(())
    if args.subject_reading:
        from cordon_d.subject_reading import retained_scene, compile_scenes
        units = compile_scenes([retained_scene(ROOT, request, names) for request in args.subject_reading], names)
    count, results, hosts, records = Counter(),Counter(),Counter(),Counter()
    if args.report_reading_version:
        from cordon_d.findings import findings
        from cordon_d.store import store_root
        stream = findings(factory(), ROOT/'corpus/sources/reports', store_root(ROOT),
                          extraction_version=args.report_reading_version, known_through=datetime.now(timezone.utc))
    else:
        stream = ({'observation': group} for group in factory())
    from cordon_d.areas import versions
    areas = versions(ROOT)
    for joined in stream:
        subject = next(observed_subjects([joined['observation']],names,municipalities,units))
        subject = subject_with_finding(subject,joined,names)
        group = subject.observation
        count['observations'] += 1
        count['source_occurrences'] += len(group.members)
        results[group.result or 'other/unresolved'] += 1
        hosts['species' if subject.host.species(names) else 'rank/conflict/unresolved'] += 1
        count['reference_candidates'] += len(subject.references)
        count['cadastral_occurrences'] += len(subject.parcels)
        count['with_cadastral_reference'] += bool(subject.parcels)
        at = args.area_date or group.day
        if subject.parcels and at:
            memberships = cadastral_memberships(subject,areas,ROOT,at)
            count['cadastral_intersections'] += bool(memberships)
            count['published_location_inside'] += any(m.subject_inside.truth is True for m in memberships)
        if joined.get('matches'):
            count['joined_report_observations'] += 1
            count['resolved_finding_species'] += finding_host(joined,names).species(names) is not None
        if subject.inspection_unit:
            records[subject.inspection_unit] += 1
        if count['observations'] % 500000 == 0:
            print('Read',count['observations'],'observations',file=sys.stderr,flush=True)
    count['connected_observations'] = sum(records.values())
    count['inspection_units'] = len(records)
    count['repeated_units'] = sum(n>1 for n in records.values())
    print(json.dumps(dict(counts=count,results=results,host_identity=hosts,
                         repeated_units=[dict(unit=k,observations=n) for k,n in records.items() if n>1]),indent=2))


if __name__ == '__main__':main()
