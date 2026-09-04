# CSIC/JRC tree-inventory acquisition result

Date: 22 August 2026  
Status: **partial positive artifact recovery; original regional inventory not acquired**

## Final verdict

The reported 2013 regional crown baseline and 2015/2018 crown-loss products were not retrieved from any public record, repository, project portal, JRC catalogue result or code host inspected in this run.

Relevant CORDIS deliverables exist, but their public download service returned server-side `HDS-010` errors, so their contents remain unresolved rather than proved empty.[6][7]

The public 2019 record asserts that the team delineated each olive tree from 2013 photography and checked 2015/2018 photography, but exposes only conference PDFs.[1][2]

The downloadable presentation contains the orchard-level MODIS analysis, not a crown inventory, regional tree count, Mask R-CNN weights, annotations, crown vectors, change table, or crown-validation record.[2]

This run nevertheless produced two real positives:

1. **Recovered airborne model artifacts:** a licensed historical GitHub snapshot contains 18 `.RData` files deleted from the current QuantaLab branch. They preserve trained LDA, SVM, kNN and neural-network objects plus analysis train/test frames for the 2016–2017 airborne study. The snapshot does not contain full crown coordinates or polygons. Its public repository license is MIT.[3]
2. **Reproducible bounded crown candidate inventory:** a 4.91 ha 2015 CIR chip, covered by IODL 2.0 metadata, yielded 551 observation-derived crown candidate points. Against 33 held-out published qPCR tree coordinates, median location error is 0.346 m; 31/33 are within 1 m and 33/33 within 2 m after a registration shift derived only from the other 34 controls. This is a bounded falsifiable reconstruction, not a Puglia census or official Plant identity.[8][9]

The current strongest usable historical inventory for broad operator work therefore remains the independently published 76,637-point Crecco population described in the parent evidence note. For the CSIC/JRC line specifically, the recovered model snapshot and 551-candidate reconstruction are the strongest artifacts now on disk, while direct author/JRC custody is the only credible path to the original regional outputs.

## What was acquired or recovered

### A. Historical QuantaLab airborne-model snapshot

Artifact:

`research/tree-inventory/artifacts/acquired/history/7b56fe69.zip`

- SHA-256: `94f47cc8d8f4cc59010cc54e1a98da478421dad27b0f7a90911e62277f31f2e3`
- Size: 172,907,534 bytes.
- Source: public GitHub commit `7b56fe69` in QuantaLab `Xf-NPlants-2018`.[3]
- Rights: repository `LICENSE` is MIT in this snapshot.
- Contents: three public CSVs, code, and 18 model-state `.RData` files for Tables 4 and 5.
- Verified inventory: 404 serialized objects across 18 files. Each model artifact preserves analysis datasets and trained objects. Observed frame sizes include 6,659 training rows plus 656 test rows and 2,969 training rows plus 297 test rows, depending on table/model.
- Important limit: none of the serialized datasets has `TREE`, X/Y, crown geometry, imagery, or a full-population source key. They are classifier-state artifacts, not the 200,000-crown inventory.

Object inventory:

`research/tree-inventory/artifacts/validation/recovered_rdata_inventory.csv`

Current public release mirror:

`research/tree-inventory/artifacts/acquired/Xf-NPlants-2018.zip`

- SHA-256: `44ee5727abd894edf6d677895813e00d06c573b20bea488d3bb243dd1082db5b`
- Current table audit confirms 7,296 analytical rows, 4,033 distinct `TREE` values, no global X/Y fields, a 67-row coordinate-bearing Parcel set and a 100-row coordinate-bearing Orchard set.
- The 67 coordinates are all distinct. They form one compact orchard control covering about 254 m × 127 m.
- The XF-ACTORS DROP entry links only to this reproduction collection and declares no license itself; the GitHub repository supplies the MIT license.[3][4]

### B. Bounded 2015 crown reconstruction

Source image:

`research/tree-inventory/artifacts/acquired/Ortofoto2015_IR_qPCR67.tif`

- SHA-256: `bb5ebd2d619cc0115a2175c64ce07a58175db32c89b4f2c05147f1c5c2bbf117`
- Epoch: 2015 flight, May–November.
- Native delivered pixel size: 0.149995 m.
- CRS: EPSG:32633.
- Bounds: 763413.75–763707.29 E, 4478537.25–4478704.65 N.
- Rights: the official metadata names Regione Puglia as owner and states IODL 2.0, 15 cm spatial resolution, 0.5 m positional accuracy, and Brindisi/Lecce/Taranto coverage.[8]
- Acquisition: public `Ortofoto2015_IR` ArcGIS ImageServer export.[9]

Derived inventory:

`research/tree-inventory/artifacts/validation/reconstructed_2015_crown_points.geojson`

- SHA-256: `739ab81f343f95edaff3d72ef894ac1eee804187b9f391898d171522e68c680e`
- Population: 551 candidate points in a 4.91 ha bounding box, 112.2 candidates/ha.
- Identity: stable IDs `PUG2015-QPCR67-0001` onward are artifact-local observation IDs only.
- Method: CIR redness threshold, binary closing, connected components, 2–250 m² area filter, then centroid extraction.
- Registration: median detected-minus-control shift from 34 alternating controls is −1.932 m east and −0.364 m north. The shift is applied to candidate points before held-out evaluation.

Measured quality:

`research/tree-inventory/artifacts/validation/reconstruction_quality.json`

- Held-out controls: 33.
- Held-out median / p90 location error: 0.346 m / 0.782 m.
- Held-out within 1 m: 31/33 (93.9%).
- Held-out within 2 m and 3 m: 33/33.
- Duplicate candidate assignments among held-out controls: 0.
- Omission among held-out controls at 2 m: 0/33.
- Deterministic image-only precision sample: 78 definite crowns, 1 definite false positive and 21 ambiguous/sparse/split-merge-looking cases among 100 candidates. The conservative definite precision is 0.78; counting ambiguous cases as real crowns gives an upper bound of 0.99. This is not field-adjudicated precision.
- Full-area split, merge and duplicate rates are **not established**. Cross-epoch identity stability is **not established**. The reconstruction therefore does not pass the parent note's proposed production thresholds.

The exact script is:

`research/tree-inventory/artifacts/scripts/reconstruct_qpcr67_2015.py`

## Original regional crown route: exhaustion record

### Public repositories and catalogues

- DIGITAL.CSIC item 10261/215092 exposes the presentation and abstract booklet only.[1]
- The EFSA-hosted presentation is downloadable and contains no crown vectors, model package, tree count, validation table or change output.[2]
- OpenAIRE mirrors the same metadata, not data.
- JRC Data Catalogue searches found no Xylella/Apulia crown dataset.
- POnTE CORDIS identifies public D6.1, “Remote sensing system for detection and monitoring of Xf,” but no tree inventory dataset is catalogued.[6]
- XF-ACTORS CORDIS lists remote-sensing indicator, processing-chain, and damage-metric deliverables, but no crown-vector dataset. Its OpenAIRE data search currently returns no results.[7]
- The CORDIS document server minted download URLs for the relevant deliverables but returned server-side `HDS-010` technical errors. The captured responses are preserved under `artifacts/sources/cordis_failed/`.
- The XF-ACTORS DROP has not been maintained since December 2020. Its relevant “Data and codes” object resolves to the QuantaLab repository already audited.[4]
- Zenodo 1087231 contains only the 2017 conference PDF, not crowns or imagery.[5]

### Code-host archaeology

- QuantaLab has one public repository. Current and historical trees were enumerated without Git.
- A historical snapshot recovered the 18 deleted `.RData` model files described above.
- No historical commit inspected contains full crown coordinates, crown polygons, imagery footprints, a crown-population key, or the reported 200,000-tree vector.
- Laura Martinez-Sanchez's public `Mask_RCNN` repository is an unmodified 2018 fork of Matterport's generic implementation. It contains no Xylella training data, configuration, weights or outputs.[11]
- Her public `DeadTrees` and CanHeMon repositories predate the Xylella crown claim and target pine-canopy decline. Pieter Beck's CanHeMonR remains useful generic crown-processing code but is not the claimed olive Mask R-CNN.[10]

### Scope contradiction to resolve

The abstract says the team delineated “each olive tree in the region.”[1] The presentation's actual regional analysis uses 27,188 olive-orchard polygons covering 2,261 km² and then focuses on 3,135 orchards larger than 12.5 ha for MODIS damage mapping.[2] No released artifact states whether the crown run covered all Puglia, the August-2018 infected/buffer geography, all 27,188 polygons, or a smaller mask. The 2019 claim therefore proves an inventory-producing analysis existed, but does not establish a complete regional inventory's scope or accuracy.

## Rights and custody

- QuantaLab code/data/model snapshot: MIT via repository license.[3]
- 2015 Puglia orthophoto chip: IODL 2.0 according to official dataset metadata.[8]
- 2013 AGEA orthophoto and 2016/2018 imagery: technical service access was confirmed, but no matching derivative-vector reuse basis was established in this run. Those image chips were not retained.
- CSIC/JRC regional derived vectors and model artifacts: rights unknown because the artifacts were not obtained.
- Airborne source imagery: not public and not copied. Custody likely spans JRC/CSIC campaign leads and project partners; written clearance or a data-use agreement is required.

## Exact recommendation

1. Send the prepared request to Pieter Beck, with Laura Martinez-Sanchez and Pablo Zarco-Tejada copied. Ask first for derived vectors, cross-epoch correspondence, weights, annotations, validation, processing masks and rights—not restricted pixels. JRC led XF-ACTORS remote sensing, and Pieter remains the named contact.[12]
2. If author custody fails, ask DIGITAL.CSIC to route a private research-copy request and preservation query; its documented fallback contact is `digital.csic@bib.csic.es`.[14]
3. Treat any acquired 2013 vectors as a historical observation baseline. Require explicit 2015/2018 continuation, disappearance, split, merge and ambiguity fields before creating persistent cross-epoch identity.
4. Continue bounded reconstruction only on imagery with explicit derivative rights. Use the 67-tree chip as a registration/control fixture and Crecco as the larger falsification environment. Do not scale the current simple threshold model region-wide.
5. Do not admit these candidate points as official Plant identities, infection findings, removals, plantings, survival, legal status or fraud findings.

Prepared request:

`research/tree-inventory/artifacts/requests/CSIC_JRC_DATA_REQUEST_DRAFT.md`

## Mainline correction

No new noun or relationship family is justified. This work supports the proposed selective boundary: an Individual Plant can be observation-derived only after a validated reproducible inventory. The present 551-candidate artifact remains below that bar because full precision, split/merge and cross-epoch identity are unresolved.

## Artifact manifest

All retained files, byte sizes and SHA-256 checksums:

`research/tree-inventory/artifacts/manifests/SHA256_MANIFEST.json`

## Sources

[1] https://digital.csic.es/handle/10261/215092
[2] https://www.efsa.europa.eu/sites/default/files/event/191029-xylella/S6.P1_BECK.pdf
[3] https://github.com/Quantalab/Xf-NPlants-2018
[4] https://xfactors.eppo.int/data/f57f942e-7eb9-4142-b223-8cd9a8c853d1
[5] https://doi.org/10.5281/zenodo.1087231
[6] https://cordis.europa.eu/project/id/635646/results
[7] https://cordis.europa.eu/project/id/727987/results
[8] https://geodati.gov.it/resource/id/r_puglia:1de1e983-7933-4e2e-8865-b6128ac05e08
[9] https://webapps.sit.puglia.it/arcgis/rest/services/BaseMaps/Ortofoto2015_IR/ImageServer
[10] https://github.com/pieterbeck/CanHeMonR
[11] https://github.com/MartinezLaura/Mask_RCNN
[12] https://www.xfactorsproject.eu/partner/jrc
[14] https://www.cid.csic.es/biblioteca/sites/default/files/documents/peticion_copia_nueva_funcionalidad_DC.pdf
