# Migration exclusions

This is a disposition record, not current program authority. `MANIFEST.csv` records each tracked source path; this file explains the family-level decisions.

| Source family | Disposition | Reason | Recovery |
|---|---|---|---|
| Legacy root `AGENTS.md`, `CORDON.md`, master plans, build-state files, logs, and owner guides | Consolidated, not copied | They mix durable intent, stale operator/product state, and implementation ritual. Their surviving meaning is reauthored in the new constitution and current-state owner. | Source commits and working-tree hashes in `SOURCE_BASELINES.json` |
| Foundry RIDs, platform coordinates, proposals, branch rituals, and historical B1–B11 build artifacts | Excluded | Development-stage and platform specific; they do not govern the A–G regional derivation. | `wedge1-aip` Git history |
| Cooperative Land/Funding/Applications/Field Work/Payments product plans and ontology artifacts | Historical evidence only where part of retained research; otherwise excluded | The cooperative product route is superseded and cannot authorize current work. | Both legacy repositories |
| Reviews outside the current Stage B review corpus | Excluded | Dated implementation evidence with no surviving current-state role. | `wedge1-aip` Git history |
| One-time Stage B transform and repair scripts | Excluded | They reconstruct superseded shapes or depend on historical Git/tmp state. Canonical authored artifacts now own the result. | `wedge1-aip` Git history |
| `data-tmp`, extracted GIS bulk, acquisition caches, generated media, and reproducible binary dumps | Excluded from the lean repository | Large derived or regenerable material. Relevant source existence and acquisition knowledge remains in the retained inventories. | Legacy working trees and source URLs recorded in evidence |
| Unreferenced jurisdictional bulk PDFs | Inventoried, bytes not copied | The admitted Stage A canon directly references a 104-file, approximately 8.5 MB evidence closure. Copying the full 1.5 GB archive would obscure that closure. | Per-file source path and hash in `MANIFEST.csv`; `wedge1-aip` Git history |
| `olive-xylella/interface`, pitch material, and presentation surfaces | Excluded | Product-stage artifacts that do not own current research, evidence, or regulatory meaning. | `olive-xylella` Git history |
| Hermes profile state, prompts, and full transcripts | Referenced, not copied | They are migration provenance and reasoning context, not program authority. | Session IDs in `SOURCE_BASELINES.json` and the Hermes state database |
| `corpus/evidence/olive-xylella` and `corpus/evidence/wedge1-aip` (369 admitted files) | Retired from the live tree on 2026-09-10 | Research, superseded interpretations, notional cooperative data and platform capability notes that no current owner reads; one retained table stated a notice rule accepted Stage A rejects. | `MANIFEST.csv` rows marked `RETIRED_FROM_LIVE_TREE`; tag `archive/legacy-evidence-2026-09-10` at `b94c18c`; the legacy repositories |
