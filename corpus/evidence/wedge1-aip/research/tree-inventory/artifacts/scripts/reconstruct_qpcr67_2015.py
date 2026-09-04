#!/usr/bin/env python3
"""Reconstruct a bounded 2015 olive-crown point inventory.

Inputs are the public QuantaLab qPCR table and a GeoTIFF exported from the
Regione Puglia 2015 colour-infrared ImageServer. The method intentionally uses
only stdlib plus numpy, scipy, Pillow and pyproj.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image
from pyproj import Transformer
from scipy import ndimage
from scipy.spatial import cKDTree


def wilson(k: int, n: int, z: float = 1.959963984540054) -> list[float]:
    p = k / n
    den = 1 + z * z / n
    ctr = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [ctr - half, ctr + half]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--controls", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    im = Image.open(args.image)
    arr = np.asarray(im).astype(float)
    tie = im.tag_v2[33922]
    scale = im.tag_v2[33550]
    x0, y0 = float(tie[3]), float(tie[4])
    sx, sy = float(scale[0]), float(scale[1])

    # The service renders CIR as NIR, red, green. Healthy vegetation is red.
    redness = (arr[:, :, 0] - arr[:, :, 1]) / (arr[:, :, 0] + arr[:, :, 1] + 1)
    mask = ndimage.binary_closing(redness > 0.10, iterations=2)
    mask = ndimage.binary_fill_holes(mask)
    labels, _ = ndimage.label(mask)

    candidates = []
    for label_id, sl in enumerate(ndimage.find_objects(labels), 1):
        if sl is None:
            continue
        pixel_count = int((labels[sl] == label_id).sum())
        area_m2 = pixel_count * sx * sy
        if not (2 <= area_m2 <= 250):
            continue
        row, col = ndimage.center_of_mass(mask, labels, label_id)
        candidates.append(
            {
                "label_id": label_id,
                "pixel_col": float(col),
                "pixel_row": float(row),
                "x_raw": x0 + float(col) * sx,
                "y_raw": y0 - float(row) * sy,
                "area_m2": area_m2,
            }
        )

    with open(args.controls, newline="", encoding="utf-8-sig") as fh:
        controls = list(csv.DictReader(fh))
    to_utm = Transformer.from_crs(4326, 32633, always_xy=True)
    qxy = np.asarray(
        [to_utm.transform(float(r["X"]), float(r["Y"])) for r in controls]
    )
    cxy = np.asarray([[r["x_raw"], r["y_raw"]] for r in candidates])
    raw_dist, raw_idx = cKDTree(cxy).query(qxy)

    # Register on alternating controls; the other half is a held-out location test.
    train = np.arange(len(qxy)) % 2 == 0
    residual = cxy[raw_idx] - qxy
    offset = np.median(residual[train & (raw_dist < 3)], axis=0)
    aligned = cxy - offset
    dist, idx = cKDTree(aligned).query(qxy)

    to_wgs = Transformer.from_crs(32633, 4326, always_xy=True)
    features = []
    for i, c in enumerate(candidates, 1):
        x, y = aligned[i - 1]
        lon, lat = to_wgs.transform(x, y)
        features.append(
            {
                "type": "Feature",
                "id": f"PUG2015-QPCR67-{i:04d}",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "inventory_id": f"PUG2015-QPCR67-{i:04d}",
                    "epoch": 2015,
                    "source": "Regione Puglia Ortofoto2015_IR",
                    "source_crs": "EPSG:32633",
                    "x_utm33": float(x),
                    "y_utm33": float(y),
                    "component_area_m2": float(c["area_m2"]),
                    "identity_status": "observation-derived crown candidate",
                    "official_identity": False,
                },
            }
        )
    (out / "reconstructed_2015_crown_points.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": features}, indent=2)
    )

    with open(out / "qpcr67_location_matches.csv", "w", newline="") as fh:
        fields = [
            "control_row",
            "split",
            "control_lon",
            "control_lat",
            "control_x_utm33",
            "control_y_utm33",
            "candidate_id",
            "distance_m",
        ]
        wr = csv.DictWriter(fh, fieldnames=fields)
        wr.writeheader()
        for j, r in enumerate(controls):
            wr.writerow(
                {
                    "control_row": j + 1,
                    "split": "registration" if train[j] else "held_out",
                    "control_lon": r["X"],
                    "control_lat": r["Y"],
                    "control_x_utm33": qxy[j, 0],
                    "control_y_utm33": qxy[j, 1],
                    "candidate_id": f"PUG2015-QPCR67-{idx[j] + 1:04d}",
                    "distance_m": dist[j],
                }
            )

    # Deterministic, conservative review of validation/precision_sample_100.png.
    # Ambiguous includes sparse, split/merge-looking or edge-clipped crowns.
    fp = {66}
    ambiguous = {6, 8, 10, 18, 20, 36, 39, 41, 43, 44, 48, 53, 55, 56, 63, 69, 78, 88, 91, 93, 100}
    tp = 100 - len(fp) - len(ambiguous)

    def subset_metrics(sel: np.ndarray) -> dict:
        ids = idx[sel]
        return {
            "n": int(sel.sum()),
            "median_location_error_m": float(np.median(dist[sel])),
            "p90_location_error_m": float(np.percentile(dist[sel], 90)),
            "within_1m": int((dist[sel] <= 1).sum()),
            "within_1m_rate": float(np.mean(dist[sel] <= 1)),
            "within_2m": int((dist[sel] <= 2).sum()),
            "within_2m_rate": float(np.mean(dist[sel] <= 2)),
            "within_3m": int((dist[sel] <= 3).sum()),
            "within_3m_rate": float(np.mean(dist[sel] <= 3)),
            "duplicate_control_assignments": int(len(ids) - len(set(ids.tolist()))),
        }

    summary = {
        "method_version": "cir-redness-v1",
        "image": str(Path(args.image).resolve()),
        "controls": str(Path(args.controls).resolve()),
        "image_crs": "EPSG:32633",
        "pixel_size_m": [sx, sy],
        "bbox_utm33": [x0, y0 - im.height * sy, x0 + im.width * sx, y0],
        "area_bbox_ha": im.width * sx * im.height * sy / 10000,
        "candidate_count": len(candidates),
        "candidate_density_per_bbox_ha": len(candidates)
        / (im.width * sx * im.height * sy / 10000),
        "segmentation": {
            "index": "(rendered_NIR-rendered_red)/(rendered_NIR+rendered_red+1)",
            "threshold": 0.10,
            "binary_closing_iterations": 2,
            "component_area_filter_m2": [2, 250],
        },
        "registration": {
            "registration_controls": int(train.sum()),
            "held_out_controls": int((~train).sum()),
            "candidate_minus_control_offset_m": offset.tolist(),
        },
        "registration_split": subset_metrics(train),
        "held_out_split": subset_metrics(~train),
        "all_controls": subset_metrics(np.ones(len(qxy), dtype=bool)),
        "manual_precision_sample": {
            "sampling_seed": 20260822,
            "sample_n": 100,
            "definite_true_positive": tp,
            "false_positive": len(fp),
            "ambiguous": len(ambiguous),
            "false_positive_ids": sorted(fp),
            "ambiguous_ids": sorted(ambiguous),
            "definite_precision": tp / 100,
            "definite_plus_ambiguous_upper_precision": (tp + len(ambiguous)) / 100,
            "definite_precision_wilson95": wilson(tp, 100),
            "review_scope": "image-only conservative review; no field adjudication",
        },
        "quality_boundary": [
            "Recall/location metrics apply only to the 67 published qPCR controls.",
            "The 100-image precision review is image interpretation, not field truth.",
            "Split/merge performance is not established for the whole bbox.",
            "Cross-epoch identity is not established by this run.",
            "Points are crown candidates, not official Plant identities.",
        ],
    }
    (out / "reconstruction_quality.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
