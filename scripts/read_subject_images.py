#!/usr/bin/env python3
"""Read retained subject imagery locally; no subscription/API extraction or training."""
from pathlib import Path
import argparse
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'regulation/stage-d'))
from cordon_d.subject_images import CrownReader,reading_path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--force',action='store_true',help='Recompute readings of unchanged images')
    args=parser.parse_args()
    frames=[f for f in json.loads((ROOT/'corpus/sources/subject-imagery/records.json').read_text())
            if f['role']=='orthophoto-frame']
    reader=None
    for frame in frames:
        if reading_path(ROOT,frame).exists() and not args.force:
            continue
        if reader is None:reader=CrownReader(ROOT)
        result=reader.read(frame)
        print(frame['sha256'],len(result['boxes']),'crown candidates',flush=True)


if __name__=='__main__':main()
