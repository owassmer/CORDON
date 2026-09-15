#!/usr/bin/env python3
"""Read retained public scenes into observation-to-subject correspondence."""
import argparse
from datetime import date
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'regulation/stage-c'), str(ROOT/'regulation/stage-d')]
from cordon_d.hosts import HostNames
from cordon_d.subject_reading import scene_populations, read_scene, compile_scenes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start', type=date.fromisoformat, required=True, help='Operative inspection period start (inclusive)')
    parser.add_argument('--end', type=date.fromisoformat, required=True, help='Operative inspection period end (exclusive)')
    parser.add_argument('--frame', action='append', help='Retained image SHA256; includes all dated frames of its extent')
    parser.add_argument('--execute', action='store_true', help='Authorize uncached, tool-disabled Codex subscription source readings; no API-key fallback')
    args = parser.parse_args()
    if args.start >= args.end:
        parser.error('The inspection period must be nonempty')
    frames = [f for f in json.loads((ROOT/'corpus/sources/subject-imagery/records.json').read_text())
              if f['role'] == 'orthophoto-frame']
    if args.frame:
        unknown = set(args.frame) - {f['sha256'] for f in frames}
        if unknown:
            parser.error('Frame is not in the retained imagery population: '+', '.join(sorted(unknown)))
        extents = {tuple(f['extent']) for f in frames if f['sha256'] in args.frame}
        frames = [f for f in frames if tuple(f['extent']) in extents]
    names = HostNames.load(ROOT)
    scenes = []
    for (crs, extent), population in scene_populations(ROOT, frames):
        # All source families and outcomes enter. Period selection follows C;
        # missing dates remain visible and cannot silently count as inspections.
        population = tuple(o for o in population if o.day is None or args.start <= o.day < args.end)
        if not population:
            continue
        selected = [f for f in frames if f['crs'] == crs and tuple(f['extent']) == extent]
        print('Reading', extent, len(population), 'observations', file=sys.stderr, flush=True)
        response = read_scene(ROOT, selected, population, names,
                              period=(args.start, args.end), execute=args.execute)
        scenes.append((response, population))
        print(json.dumps(dict(request=response['request_sha256'], extent=extent,
                              observations=len(population))), flush=True)
    units = compile_scenes(scenes, names)
    print(json.dumps(dict(connected_observations=sum(unit is not None for unit, _ in units.values()),
                          inspection_units=len({unit for unit, _ in units.values() if unit is not None}))))


if __name__ == '__main__':
    main()
