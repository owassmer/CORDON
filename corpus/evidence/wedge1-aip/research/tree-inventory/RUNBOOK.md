# CSIC/JRC tree-inventory continuation runbook

Work only in:

`research/tree-inventory/`

Do not run Git. The procedures below use immutable HTTP archives and public APIs.

## 1. Verify retained artifacts

```bash
cd <wedge1-aip-repository-root>
python3 - <<'PY'
import hashlib, json
from pathlib import Path
m = json.loads(Path('research/tree-inventory/artifacts/manifests/SHA256_MANIFEST.json').read_text())
fail = []
for row in m['files']:
    p = Path(row['path'])
    if not p.exists():
        fail.append((str(p), 'missing'))
        continue
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    if h.hexdigest() != row['sha256']:
        fail.append((str(p), 'checksum'))
print('verified', len(m['files']) - len(fail), 'failed', fail)
raise SystemExit(bool(fail))
PY
```

The manifest intentionally covers `artifacts/`, not this runbook or the result report.

## 2. Re-acquire the current QuantaLab release

```bash
cd research/tree-inventory/artifacts/acquired
curl -L --fail --output Xf-NPlants-2018.zip \
  https://github.com/Quantalab/Xf-NPlants-2018/archive/refs/heads/master.zip
shasum -a 256 Xf-NPlants-2018.zip
```

Expected SHA-256 at this run: `44ee5727abd894edf6d677895813e00d06c573b20bea488d3bb243dd1082db5b`.

To audit the tables after extraction:

```bash
mkdir -p current
/usr/bin/ditto -x -k Xf-NPlants-2018.zip current
python3 ../scripts/audit_quantalab_tables.py \
  current/Xf-NPlants-2018-master/data/*.csv \
  > ../validation/quantalab_current_table_audit.json
```

## 3. Re-acquire the historical model snapshot

Commit `7b56fe69` is used because it contains both the 18 `.RData` model files and the MIT `LICENSE`.

```bash
cd research/tree-inventory/artifacts/acquired/history
curl -L --fail --output 7b56fe69.zip \
  https://codeload.github.com/Quantalab/Xf-NPlants-2018/zip/7b56fe69
shasum -a 256 7b56fe69.zip
```

Expected SHA-256: `94f47cc8d8f4cc59010cc54e1a98da478421dad27b0f7a90911e62277f31f2e3`.

Inventory the serialized objects without changing the archive:

```bash
TMP=$(mktemp -d)
/usr/bin/ditto -x -k 7b56fe69.zip "$TMP"
Rscript ../../scripts/inventory_recovered_rdata.R \
  "$TMP/Xf-NPlants-2018-7b56fe69" \
  ../../validation/recovered_rdata_inventory.csv
rm -rf "$TMP"
```

R may warn that `caret` is unavailable while deserializing trained objects. The inventory still succeeds because it reads object classes, dimensions and column names; it does not execute the models.

## 4. Re-acquire the 2015 CIR control chip

The exact export URL is preserved at:

`artifacts/sources/Ortofoto2015_IR_export_url.txt`

```bash
cd research/tree-inventory
curl -L --fail --output artifacts/acquired/Ortofoto2015_IR_qPCR67.tif \
  "$(tr -d '\n' < artifacts/sources/Ortofoto2015_IR_export_url.txt)"
shasum -a 256 artifacts/acquired/Ortofoto2015_IR_qPCR67.tif
```

Expected SHA-256: `bb5ebd2d619cc0115a2175c64ce07a58175db32c89b4f2c05147f1c5c2bbf117`.

The output request fixes the bbox, EPSG:32633, pixel dimensions and TIFF format. The source service may update its mosaic; a future checksum change must be investigated, not silently accepted.

## 5. Reproduce the 551-candidate inventory and quality outputs

Dependencies used successfully on 22 August 2026:

- Python 3;
- `numpy`;
- `scipy`;
- `Pillow`;
- `pyproj`.

```bash
cd <wedge1-aip-repository-root>
python3 research/tree-inventory/artifacts/scripts/reconstruct_qpcr67_2015.py \
  --image research/tree-inventory/artifacts/acquired/Ortofoto2015_IR_qPCR67.tif \
  --controls research/tree-inventory/artifacts/acquired/current/Xf-NPlants-2018-master/data/2-Data_Parcel_with_qPCR.csv \
  --outdir research/tree-inventory/artifacts/validation \
  > research/tree-inventory/artifacts/validation/reconstruction_run.log
```

Verify these facts in `reconstruction_quality.json`:

- `candidate_count = 551`;
- held-out `n = 33`;
- held-out median error approximately `0.3461365 m`;
- held-out `within_2m = 33`;
- held-out duplicate assignments `= 0`.

If they change, first check image checksum, QuantaLab CSV checksum, Python package versions and TIFF georeferencing tags.

## 6. Continue the original-data acquisition route

Do not send without owner approval. The exact draft is:

`artifacts/requests/CSIC_JRC_DATA_REQUEST_DRAFT.md`

Priority sequence:

1. Pieter Beck at JRC: `pieter.beck@ec.europa.eu`.
2. Laura Martinez-Sanchez through the current JRC staff directory.
3. Pablo Zarco-Tejada: `pablo.zarco@unimelb.edu.au`.
4. DIGITAL.CSIC Technical Office: `digital.csic@bib.csic.es`.
5. If the authors confirm JRC institutional custody, request deposition in the JRC Data Catalogue or a research-only data-use agreement.

Ask for derived vectors and metadata before imagery. Require:

- exact analysis mask and meaning of “region”;
- 2013 crown geometries/centroids and count;
- 2015/2018 change labels and correspondence key;
- source epoch, CRS and image product IDs;
- weights, code, annotations and validation split;
- precision, recall, omission, duplicate, split, merge and location-error records;
- rights statement for every artifact.

## 7. CORDIS deliverable retry

The relevant public document IDs are:

- POnTE D6.1: `080166e5c25685e6`;
- XF-ACTORS early indicators: `080166e5db99d20e`;
- XF-ACTORS damage metrics/datasets: `080166e5bfab3e35`;
- XF-ACTORS processing chain: `080166e5ca0eb2c1`.

The public CORDIS pages mint a temporary meta-refresh download URL. On this run, the second hop returned `HDS-010`. Preserved server responses are under `artifacts/sources/cordis_failed/`. Retry from the CORDIS results page. If `HDS-010` persists, report the Hermes ID shown in the response to the EC IT Helpdesk rather than claiming the deliverable is absent.

## 8. Acceptance gate for any newly obtained original inventory

Before operational use:

1. verify checksums and rights;
2. record CRS, epoch, coverage and count;
3. test precision/recall by orchard stratum;
4. measure duplicates, omissions, split and merge;
5. register epochs on stable non-tree controls;
6. measure cross-epoch continuation precision/recall;
7. preserve ambiguous continuation rather than forcing identity;
8. keep observed crown identity separate from official Plant identity and legal/diagnostic state.

A vector file's existence is not acceptance evidence.
