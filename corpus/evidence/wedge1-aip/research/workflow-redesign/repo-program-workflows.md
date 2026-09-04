# Repository evidence for CORDON program workflows

**Lane:** independent repository lane A.  
**Evidence boundary:** tracked files in `/Users/owenwassmer/Desktop/Connor/olive-xylella` only. No web, session history, `wedge1-aip` content, or outside source was used to fill a gap. A citation such as `path:10-12` refers to the tracked file and exact line range in that repository. Dated research records are evidence of what the repository had concluded at that time; they are not silently promoted to current legal authority.

## 1. Inventory and coverage ledger

### Method and coverage result

- `git ls-files` returned **186 tracked files**. All 186 existed on disk. The working tree also contained untracked `grill.md`; it was excluded because this lane is limited to tracked corpus.
- **126 text-like files** were read in full as text, totaling **37,379 lines**. This includes every tracked program document, query, producer artifact, data-universe file, schema, script, manifest, brief, analysis, interface artifact, source extract, and source note.
- **42 office/PDF/archive files** were structurally inspected. OOXML/ZIP files were enumerated by container members and worksheet/slide parts. PDFs were signature/page-object inspected and represented by their adjacent tracked text extracts or `raw/papers/MANIFEST.md` where available.
- **18 image files** were represented by path, byte size, signature/hash, and their role as paired article figures. No image is treated as independent workflow evidence.
- Therefore **files read or represented = 186/186**. This is repository-file coverage, not proof that the repository contains every external act, form, award rule, or user workflow.
- Classification vocabulary: **primary evidence** = frozen source or source extract; **verified fact** = repo record explicitly reporting a primary-source or live-probe check; **derived analysis** = computation or synthesis; **hypothesis** = proposed interpretation/test; **decision** = program/product direction; **historical record** = dated plan, review, log, or superseded state; **superseded assumption** = claim explicitly overturned elsewhere in the tracked corpus. The program itself says research records are evidence rather than authority (`AGENTS.md:7-21`) and that legacy Wedge 1 artifacts are historical, not redesign authority (`CORDON.md:25-28`).

### Directory summary

| Tracked area | Count | Treatment | Workflow relevance |
|---|---:|---|---|
| Root + `.hermes` | 11 | Full text read | Program authority, schema, plans, history |
| `briefs/` | 5 | Full text read | Surveillance and proposal outputs; limited direct application workflow |
| `checks/` | 2 | Full source read | Verification utilities |
| `concepts/` | 7 | Full text read | Scientific/domain terminology |
| `data/` | 16 | Full text/source read | Data universe, workbook inventory, decoder, provenance |
| `entities/` | 4 | Full text read | Domain actors/organisms/cultivars |
| `interface/` | 10 | Full text/source/data read | Derived campaign display artifacts |
| `nowcast/` | 27 | Full text/source read | Derived field/scientific analyses |
| `producers/` | 4 | Full text/source read | User, channel, playbook, exposure workflow |
| `queries/` | 17 | Full text read | Reviews, decisions, hypotheses, contradictions |
| `raw/` | 84 | 42 text files read; 42 binary/archive/image files structurally represented | Primary evidence and source captures |
| **Total** | **186** | **186 read or represented** | Complete tracked-file coverage |

### Artifact-by-artifact ledger

The following ledger is exhaustive. “Workflow-keyword lines indexed” is a mechanical coverage aid, not a relevance score.

### `[root]/`
- `.gitignore` — **decision** — read text L1–25; 1 workflow-keyword lines indexed.

### `.hermes/plans/`
- `.hermes/plans/2026-08-15_143215-f7-imagery.md` — **historical record; decision** — read text L1–179; 17 workflow-keyword lines indexed.
- `.hermes/plans/2026-08-15_145047-experiment1-vhr.md` — **historical record; decision** — read text L1–171; 14 workflow-keyword lines indexed.
- `.hermes/plans/2026-08-16_ferro-profile-design.md` — **historical record; decision** — read text L1–263; 63 workflow-keyword lines indexed.

### `[root]/`
- `AGENTIC_DEVELOPMENT_FIRST_PRINCIPLES.md` — **historical record; decision** — read text L1–1217; 136 workflow-keyword lines indexed.
- `AGENTS.md` — **decision; verified fact** — read text L1–104; 21 workflow-keyword lines indexed.
- `CORDON.md` — **decision; verified fact** — read text L1–81; 24 workflow-keyword lines indexed.
- `SCHEMA.md` — **decision** — read text L1–69; 0 workflow-keyword lines indexed.

### `briefs/`
- `briefs/build_landscape_iso.py` — **derived analysis; historical record** — read text L1–274; 15 workflow-keyword lines indexed.
- `briefs/cordon-landscape-isometric.html` — **derived analysis; historical record** — read text L1–145; 8 workflow-keyword lines indexed.
- `briefs/it-onepager-skeleton.md` — **derived analysis; historical record** — read text L1–27; 2 workflow-keyword lines indexed.
- `briefs/murge-surveillance-gap.md` — **derived analysis; historical record** — read text L1–74; 7 workflow-keyword lines indexed.
- `briefs/wv3-esa-tpm-proposal.md` — **derived analysis; historical record** — read text L1–43; 9 workflow-keyword lines indexed.

### `checks/`
- `checks/verify_day1.py` — **derived analysis** — read text L1–18; 0 workflow-keyword lines indexed.
- `checks/verify_scene_join.py` — **derived analysis** — read text L1–25; 0 workflow-keyword lines indexed.

### `concepts/`
- `concepts/camp-csv.md` — **derived analysis; hypothesis** — read text L1–32; 1 workflow-keyword lines indexed.
- `concepts/front-nowcast.md` — **derived analysis; hypothesis** — read text L1–26; 1 workflow-keyword lines indexed.
- `concepts/oqds.md` — **derived analysis; hypothesis** — read text L1–31; 3 workflow-keyword lines indexed.
- `concepts/previsual-detection.md` — **derived analysis; hypothesis** — read text L1–28; 1 workflow-keyword lines indexed.
- `concepts/puglia-monitoring.md` — **derived analysis; hypothesis** — read text L1–22; 3 workflow-keyword lines indexed.
- `concepts/resistance-decoder.md` — **derived analysis; hypothesis** — read text L1–24; 0 workflow-keyword lines indexed.
- `concepts/resistance-not-immunity.md` — **derived analysis; hypothesis** — read text L1–33; 0 workflow-keyword lines indexed.

### `data/`
- `data/CAMP_XLSX.md` — **derived analysis; verified fact** — read text L1–66; 3 workflow-keyword lines indexed.
- `data/CRECCO.md` — **derived analysis; verified fact** — read text L1–21; 0 workflow-keyword lines indexed.
- `data/DATA_UNIVERSE_CIVIC.md` — **verified fact; derived analysis; historical record** — read text L1–110; 48 workflow-keyword lines indexed.
- `data/DATA_UNIVERSE_FLIPS.md` — **verified fact; derived analysis; historical record** — read text L1–56; 21 workflow-keyword lines indexed.
- `data/DATA_UNIVERSE_GEO.md` — **verified fact; derived analysis; historical record** — read text L1–101; 51 workflow-keyword lines indexed.
- `data/DAY1.md` — **derived analysis; verified fact** — read text L1–45; 3 workflow-keyword lines indexed.
- `data/ORTOFOTO.md` — **derived analysis; verified fact** — read text L1–25; 0 workflow-keyword lines indexed.
- `data/PRISMA.md` — **derived analysis; verified fact** — read text L1–9; 0 workflow-keyword lines indexed.
- `data/README.md` — **derived analysis; verified fact** — read text L1–30; 1 workflow-keyword lines indexed.
- `data/_camp_xlsx_inventory.json` — **derived analysis; verified fact** — read text L1–1100; 1 workflow-keyword lines indexed.
- `data/_inventory_camp_2020_2022.json` — **derived analysis; verified fact** — read text L1–139; 0 workflow-keyword lines indexed.
- `data/_stats_partial.json` — **derived analysis; verified fact** — read text L1–164; 0 workflow-keyword lines indexed.
- `data/analyze_camp_xlsx.py` — **derived analysis** — read text L1–242; 4 workflow-keyword lines indexed.

### `data/decoder/`
- `data/decoder/SOURCES.md` — **historical record; primary-evidence index** — read text L1–44; 2 workflow-keyword lines indexed.
- `data/decoder/v0-genes.md` — **derived analysis; hypothesis** — read text L1–57; 6 workflow-keyword lines indexed.
- `data/decoder/v1-targets.md` — **derived analysis; hypothesis** — read text L1–202; 7 workflow-keyword lines indexed.

### `entities/`
- `entities/cnr-ipsp.md` — **derived analysis; hypothesis** — read text L1–29; 0 workflow-keyword lines indexed.
- `entities/leccino.md` — **derived analysis; hypothesis** — read text L1–30; 1 workflow-keyword lines indexed.
- `entities/philaenus-spumarius.md` — **derived analysis; hypothesis** — read text L1–24; 1 workflow-keyword lines indexed.
- `entities/xylella-fastidiosa.md` — **derived analysis; hypothesis** — read text L1–35; 0 workflow-keyword lines indexed.

### `[root]/`
- `index.md` — **historical record; derived analysis** — read text L1–35; 1 workflow-keyword lines indexed.

### `interface/`
- `interface/README.md` — **derived analysis** — read text L1–33; 3 workflow-keyword lines indexed.
- `interface/build_display_data.py` — **derived analysis** — read text L1–174; 3 workflow-keyword lines indexed.

### `interface/data/`
- `interface/data/campaigns.json` — **derived analysis** — read text L1–254; 0 workflow-keyword lines indexed.
- `interface/data/comune_campaign.json` — **derived analysis** — read text L1–1; 0 workflow-keyword lines indexed.
- `interface/data/comune_year.json` — **derived analysis** — read text L1–1; 0 workflow-keyword lines indexed.
- `interface/data/cordon_data.js` — **derived analysis** — read text L1–1; 1 workflow-keyword lines indexed.
- `interface/data/meta.json` — **derived analysis** — read text L1–21; 1 workflow-keyword lines indexed.
- `interface/data/ndmi100.json` — **derived analysis** — read text L1–1; 0 workflow-keyword lines indexed.
- `interface/data/years.json` — **derived analysis** — read text L1–171; 0 workflow-keyword lines indexed.

### `interface/`
- `interface/index.html` — **derived analysis** — read text L1–230; 9 workflow-keyword lines indexed.

### `[root]/`
- `log.md` — **historical record** — read text L1–73; 5 workflow-keyword lines indexed.

### `nowcast/`
- `nowcast/ARTIFACT_A.md` — **derived analysis; verified fact** — read text L1–27; 3 workflow-keyword lines indexed.
- `nowcast/CROWN_DILUTION.md` — **derived analysis; verified fact** — read text L1–184; 3 workflow-keyword lines indexed.
- `nowcast/CULTIVAR_FIELD.md` — **derived analysis; verified fact** — read text L1–73; 8 workflow-keyword lines indexed.
- `nowcast/EXPERIMENT1.md` — **derived analysis; verified fact** — read text L1–37; 0 workflow-keyword lines indexed.
- `nowcast/F7.md` — **derived analysis; verified fact** — read text L1–36; 1 workflow-keyword lines indexed.
- `nowcast/FRONT_RATE.md` — **derived analysis; verified fact** — read text L1–224; 13 workflow-keyword lines indexed.
- `nowcast/NEGATIVE.md` — **derived analysis; verified fact** — read text L1–14; 0 workflow-keyword lines indexed.
- `nowcast/README.md` — **derived analysis; verified fact** — read text L1–6; 0 workflow-keyword lines indexed.
- `nowcast/SCENE_JOIN.md` — **derived analysis; verified fact** — read text L1–47; 0 workflow-keyword lines indexed.
- `nowcast/SR.md` — **derived analysis; verified fact** — read text L1–46; 0 workflow-keyword lines indexed.
- `nowcast/TEMPORAL.md` — **derived analysis; verified fact** — read text L1–100; 7 workflow-keyword lines indexed.
- `nowcast/VALIDATION.md` — **derived analysis; verified fact** — read text L1–26; 0 workflow-keyword lines indexed.
- `nowcast/camp_crecco_overlap.py` — **derived analysis** — read text L1–65; 0 workflow-keyword lines indexed.
- `nowcast/crown_fraction_2021.py` — **derived analysis** — read text L1–152; 0 workflow-keyword lines indexed.
- `nowcast/crown_stratified_paired.py` — **derived analysis** — read text L1–153; 0 workflow-keyword lines indexed.
- `nowcast/cultivar_conversion.py` — **derived analysis** — read text L1–231; 4 workflow-keyword lines indexed.
- `nowcast/experiment1_extract.py` — **derived analysis** — read text L1–149; 1 workflow-keyword lines indexed.
- `nowcast/experiment1_match.py` — **derived analysis** — read text L1–129; 0 workflow-keyword lines indexed.
- `nowcast/experiment1_paired.py` — **derived analysis** — read text L1–166; 1 workflow-keyword lines indexed.
- `nowcast/experiment1_sr.py` — **derived analysis** — read text L1–658; 21 workflow-keyword lines indexed.
- `nowcast/experiment1_temporal.py` — **derived analysis** — read text L1–336; 7 workflow-keyword lines indexed.
- `nowcast/f7_count.py` — **derived analysis** — read text L1–72; 0 workflow-keyword lines indexed.
- `nowcast/f7_join.py` — **derived analysis** — read text L1–188; 1 workflow-keyword lines indexed.
- `nowcast/front_rate.py` — **derived analysis** — read text L1–377; 7 workflow-keyword lines indexed.
- `nowcast/join_one_scene.py` — **derived analysis** — read text L1–285; 2 workflow-keyword lines indexed.
- `nowcast/probe_repeat_visits.py` — **derived analysis** — read text L1–49; 0 workflow-keyword lines indexed.
- `nowcast/resample_aug22.py` — **derived analysis** — read text L1–40; 0 workflow-keyword lines indexed.

### `producers/`
- `producers/STRATEGY.md` — **decision; derived analysis; historical record** — read text L1–43; 13 workflow-keyword lines indexed.
- `producers/amalberga-profile.md` — **decision; derived analysis; historical record** — read text L1–44; 7 workflow-keyword lines indexed.
- `producers/front_exposure.py` — **derived analysis** — read text L1–218; 2 workflow-keyword lines indexed.
- `producers/playbook-2026.md` — **decision; derived analysis; historical record** — read text L1–274; 82 workflow-keyword lines indexed.

### `queries/`
- `queries/assumption-reopen-live.md` — **superseded assumption; hypothesis; historical record** — read text L1–66; 13 workflow-keyword lines indexed.
- `queries/detection-surveillance-challenge.md` — **derived analysis; hypothesis; historical record** — read text L1–403; 43 workflow-keyword lines indexed.
- `queries/foundry-platform-atlas-draft.md` — **derived analysis; hypothesis; historical record** — read text L1–277; 82 workflow-keyword lines indexed.
- `queries/intervention-landscape-challenge.md` — **derived analysis; hypothesis; historical record** — read text L1–304; 83 workflow-keyword lines indexed.
- `queries/resistance-decoder-challenge.batch0.md` — **derived analysis; hypothesis; historical record** — read text L1–338; 22 workflow-keyword lines indexed.
- `queries/resistance-decoder-challenge.md` — **derived analysis; hypothesis; historical record** — read text L1–338; 22 workflow-keyword lines indexed.
- `queries/resistance-decoder-challenge.relaunch.md` — **derived analysis; hypothesis; historical record** — read text L1–327; 21 workflow-keyword lines indexed.
- `queries/telos-pivot-resilience-os.md` — **decision; derived analysis; historical record** — read text L1–68; 26 workflow-keyword lines indexed.
- `queries/telos-pivot-verification.md` — **decision; derived analysis; historical record** — read text L1–27; 16 workflow-keyword lines indexed.
- `queries/telos-review-S0-self.md` — **derived analysis; hypothesis; historical record** — read text L1–44; 8 workflow-keyword lines indexed.
- `queries/telos-review-S1-spread.md` — **derived analysis; hypothesis; historical record** — read text L1–65; 31 workflow-keyword lines indexed.
- `queries/telos-review-S2-severity-replant.md` — **derived analysis; hypothesis; historical record** — read text L1–85; 18 workflow-keyword lines indexed.
- `queries/telos-review-S4-tailrisk.md` — **derived analysis; hypothesis; historical record** — read text L1–56; 13 workflow-keyword lines indexed.
- `queries/telos-review-S7-producer-market.md` — **derived analysis; hypothesis; historical record** — read text L1–66; 24 workflow-keyword lines indexed.
- `queries/telos-review-S8-product-feasibility.md` — **derived analysis; hypothesis; historical record** — read text L1–71; 24 workflow-keyword lines indexed.
- `queries/telos-review-S9-producer-playbook.md` — **derived analysis; hypothesis; historical record** — read text L1–52; 24 workflow-keyword lines indexed.
- `queries/telos-synthesis.md` — **decision; derived analysis; historical record** — read text L1–44; 19 workflow-keyword lines indexed.

### `raw/articles/`
- `raw/articles/.gitkeep` — **historical record** — read text L1–0; 0 workflow-keyword lines indexed.
- `raw/articles/agromillora-2025-xylella-picture.extract.md` — **primary evidence** — read text L1–371; 34 workflow-keyword lines indexed.
- `raw/articles/ahern-2014.pdf.txt` — **primary evidence** — read text L1–945; 19 workflow-keyword lines indexed.
- `raw/articles/efsa-2016.pdf.txt` — **primary evidence** — read text L1–707; 121 workflow-keyword lines indexed.
- `raw/articles/giampetruzzi-2016.pdf.txt` — **primary evidence** — read text L1–1634; 55 workflow-keyword lines indexed.
- `raw/articles/la-notte-2024.pdf.txt` — **primary evidence** — read text L1–2150; 52 workflow-keyword lines indexed.
- `raw/articles/montilon-2022.pdf.txt` — **primary evidence** — read text L1–593; 27 workflow-keyword lines indexed.
- `raw/articles/pavan-2021.pdf.txt` — **primary evidence** — read text L1–989; 27 workflow-keyword lines indexed.
- `raw/articles/sabella-2019.pdf.txt` — **primary evidence** — read text L1–674; 22 workflow-keyword lines indexed.
- `raw/articles/sabri-2024-mate2.extract.md` — **primary evidence** — read text L1–1208; 32 workflow-keyword lines indexed.
- `raw/articles/schneider-2020-pnas.extract.md` — **primary evidence** — read text L1–1532; 64 workflow-keyword lines indexed.
- `raw/articles/surano-2022.pdf.txt` — **primary evidence** — read text L1–866; 22 workflow-keyword lines indexed.
- `raw/articles/zarco-2018.pdf.txt` — **primary evidence** — read text L1–1426; 58 workflow-keyword lines indexed.

### `raw/data/`
- `raw/data/.gitkeep` — **historical record** — read text L1–0; 0 workflow-keyword lines indexed.

### `raw/extracts/`
- `raw/extracts/giampetruzzi-2016-bmc-genomics.txt` — **primary evidence** — read text L1–1670; 55 workflow-keyword lines indexed.
- `raw/extracts/la-notte-2024-frontiers.txt` — **primary evidence** — read text L1–2192; 52 workflow-keyword lines indexed.
- `raw/extracts/pavan-2021-frontiers.txt` — **primary evidence** — read text L1–1007; 27 workflow-keyword lines indexed.
- `raw/extracts/sabri-2024-frontiers-mate2.txt` — **primary evidence** — read text L1–862; 32 workflow-keyword lines indexed.
- `raw/extracts/surano-2022-frontiers.txt` — **primary evidence** — read text L1–882; 22 workflow-keyword lines indexed.

### `raw/papers/`
- `raw/papers/MANIFEST.md` — **primary evidence** — read text L1–22; 2 workflow-keyword lines indexed.
- `raw/papers/efsa-2016-treatments.pdf` — **primary evidence** — structurally inspected PDF; ~12 page objects; represented by adjacent extract/manifest where available.
- `raw/papers/giampetruzzi-2016-bmc-genomics.pdf` — **primary evidence** — structurally inspected PDF; ~18 page objects; represented by adjacent extract/manifest where available.
- `raw/papers/la-notte-2024-frontiers.pdf` — **primary evidence** — structurally inspected PDF; ~21 page objects; represented by adjacent extract/manifest where available.
- `raw/papers/pavan-2021-frontiers.pdf` — **primary evidence** — structurally inspected PDF; ~0 page objects; represented by adjacent extract/manifest where available.
- `raw/papers/sabri-2024-frontiers-mate2.pdf` — **primary evidence** — structurally inspected PDF; ~11 page objects; represented by adjacent extract/manifest where available.
- `raw/papers/surano-2022-frontiers.pdf` — **primary evidence** — structurally inspected PDF; ~8 page objects; represented by adjacent extract/manifest where available.
- `raw/papers/zarco-tejada-2018-natureplants.pdf` — **primary evidence** — structurally inspected PDF; ~18 page objects; represented by adjacent extract/manifest where available.
- `raw/papers/zarco-tejada-2021-natcomm.pdf` — **primary evidence** — structurally inspected PDF; ~11 page objects; represented by adjacent extract/manifest where available.

### `raw/supp/`
- `raw/supp/ahern-2014.xml` — **primary evidence** — read text L1–0; 0 workflow-keyword lines indexed.
- `raw/supp/epmc-supp.zip` — **primary evidence** — structurally inspected OOXML/ZIP; 34 members.
- `raw/supp/giam-article.html` — **primary evidence** — read text L1–88; 0 workflow-keyword lines indexed.
- `raw/supp/giampetruzzi-2016-MOESM3.xlsx` — **primary evidence** — structurally inspected OOXML/ZIP; 11 members; 2 worksheet XML parts.
- `raw/supp/giampetruzzi-2016-MOESM4.xlsx` — **primary evidence** — structurally inspected OOXML/ZIP; 11 members; 2 worksheet XML parts.
- `raw/supp/giampetruzzi-2016-MOESM9.xlsx` — **primary evidence** — structurally inspected OOXML/ZIP; 10 members; 1 worksheet XML parts.
- `raw/supp/lanotte-2024-DataSheet1.docx` — **primary evidence** — structurally inspected; mislabeled HTML capture, not valid OOXML.
- `raw/supp/lanotte-DataSheet1.docx` — **primary evidence** — structurally inspected; mislabeled HTML capture, not valid OOXML.
- `raw/supp/lanotte-Table1.docx` — **primary evidence** — structurally inspected; mislabeled HTML capture, not valid OOXML.
- `raw/supp/lanotte-Table2.docx` — **primary evidence** — structurally inspected; mislabeled HTML capture, not valid OOXML.
- `raw/supp/lanotte-Table3.xlsx` — **primary evidence** — structurally inspected; mislabeled HTML capture, not valid OOXML.
- `raw/supp/lanotte-Table4.xlsx` — **primary evidence** — structurally inspected; mislabeled HTML capture, not valid OOXML.
- `raw/supp/lanotte-Table5.xlsx` — **primary evidence** — structurally inspected; mislabeled HTML capture, not valid OOXML.
- `raw/supp/lanotte-Table6.docx` — **primary evidence** — structurally inspected; mislabeled HTML capture, not valid OOXML.
- `raw/supp/lanotte-article.html` — **primary evidence** — read text L1–119; 6 workflow-keyword lines indexed.

### `raw/supp/lanotte-epmc/`
- `raw/supp/lanotte-epmc/DataSheet1.docx` — **primary evidence** — structurally inspected OOXML/ZIP; 37 members.
- `raw/supp/lanotte-epmc/Presentation1.pptx` — **primary evidence** — structurally inspected OOXML/ZIP; 47 members; 1 slide XML parts.
- `raw/supp/lanotte-epmc/Presentation2.pdf` — **primary evidence** — structurally inspected PDF; ~1 page objects; represented by adjacent extract/manifest where available.
- `raw/supp/lanotte-epmc/Presentation3.pptx` — **primary evidence** — structurally inspected OOXML/ZIP; 45 members; 1 slide XML parts.
- `raw/supp/lanotte-epmc/Presentation4.pptx` — **primary evidence** — structurally inspected OOXML/ZIP; 46 members; 1 slide XML parts.
- `raw/supp/lanotte-epmc/Presentation5.pptx` — **primary evidence** — structurally inspected OOXML/ZIP; 45 members; 1 slide XML parts.
- `raw/supp/lanotte-epmc/Presentation6.pptx` — **primary evidence** — structurally inspected OOXML/ZIP; 46 members; 1 slide XML parts.
- `raw/supp/lanotte-epmc/Presentation7.pptx` — **primary evidence** — structurally inspected OOXML/ZIP; 47 members; 1 slide XML parts.
- `raw/supp/lanotte-epmc/Presentation8.pptx` — **primary evidence** — structurally inspected OOXML/ZIP; 50 members; 1 slide XML parts.
- `raw/supp/lanotte-epmc/Presentation9.pdf` — **primary evidence** — structurally inspected PDF; ~1 page objects; represented by adjacent extract/manifest where available.
- `raw/supp/lanotte-epmc/Table1.docx` — **primary evidence** — structurally inspected OOXML/ZIP; 11 members.
- `raw/supp/lanotte-epmc/Table2.docx` — **primary evidence** — structurally inspected OOXML/ZIP; 11 members.
- `raw/supp/lanotte-epmc/Table3.xlsx` — **primary evidence** — structurally inspected OOXML/ZIP; 22 members; 1 worksheet XML parts.
- `raw/supp/lanotte-epmc/Table4.xlsx` — **primary evidence** — structurally inspected OOXML/ZIP; 28 members; 6 worksheet XML parts.
- `raw/supp/lanotte-epmc/Table5.xlsx` — **primary evidence** — structurally inspected OOXML/ZIP; 29 members; 6 worksheet XML parts.
- `raw/supp/lanotte-epmc/Table6.docx` — **primary evidence** — structurally inspected OOXML/ZIP; 16 members.
- `raw/supp/lanotte-epmc/fpls-15-1457831-g001.gif` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (9596 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g001.jpg` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (199945 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g002.gif` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (9740 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g002.jpg` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (73534 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g003.gif` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (9298 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g003.jpg` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (78551 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g004.gif` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (19378 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g004.jpg` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (131547 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g005.gif` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (9885 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g005.jpg` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (98466 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g006.gif` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (13914 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g006.jpg` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (185699 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g007.gif` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (9746 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g007.jpg` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (78271 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g008.gif` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (16944 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g008.jpg` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (294769 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g009.gif` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (12355 B).
- `raw/supp/lanotte-epmc/fpls-15-1457831-g009.jpg` — **primary evidence** — binary image represented by signature/hash; paired article figure asset (158364 B).

### `raw/supp/`
- `raw/supp/montilon-2022.pdf` — **primary evidence** — structurally inspected PDF; ~10 page objects; represented by adjacent extract/manifest where available.
- `raw/supp/pmc.html` — **primary evidence** — read text L1–3927; 75 workflow-keyword lines indexed.
- `raw/supp/sabella-2019.pdf` — **primary evidence** — structurally inspected PDF; ~11 page objects; represented by adjacent extract/manifest where available.
- `raw/supp/try_DataSheet1.docx` — **primary evidence** — structurally inspected; empty placeholder (0 B).
- `raw/supp/try_DataSheet_1.docx` — **primary evidence** — structurally inspected; empty placeholder (0 B).
- `raw/supp/try_Data_Sheet_1.docx` — **primary evidence** — structurally inspected; empty placeholder (0 B).
- `raw/supp/try_Table_1.docx` — **primary evidence** — structurally inspected; empty placeholder (0 B).

## 2. Terminology

| Term | Repository-grounded meaning and workflow consequence |
|---|---|
| **Parcel / particella / foglio** | The decision grain for legal status and applications. Official order annexes can contain foglio, particella, owner, sample, coordinates, and zone (`data/DATA_UNIVERSE_CIVIC.md:40-45`). Public cadastral geometry supports coordinate→parcel and foglio/particella validation (`data/DATA_UNIVERSE_GEO.md:27-31,53-57`). |
| **CUAA / fascicolo aziendale / schedario oleicolo** | Grower/business identity and current holding/crop record. The current link is not open; SIAN is gated and the coop/CAA is expected to bring fascicolo extracts (`data/DATA_UNIVERSE_GEO.md:67-70`). This is a handoff, not a land-geometry blocker. |
| **Official status** | Status determined by the Osservatorio, not by CORDON. Product output is private, source-cited reproduction of official requirements, never diagnosis or certification (`CORDON.md:48-55,68-71`; `producers/playbook-2026.md:11-20`). |
| **Area delimitata (AD)** | A demarcated area established by an act. Separate eradication ADs use a 50 m infected zone plus buffer; the ex-Salento area follows containment rules (`producers/playbook-2026.md:69-85`). |
| **Zona infetta** | Ambiguous without regime. In an eradication AD it is the 50 m removal zone. In the ex-Salento containment area it is the broad infected territory. The repository repeatedly warns that Salento rules do not transfer to northern eradication foci (`producers/playbook-2026.md:24-52,132-156`). |
| **Zona di contenimento** | The 2 km northern strip where containment measures and special bans apply. It is distinct from the broader ex-Salento infected zone (`data/DATA_UNIVERSE_GEO.md:11-18`; `producers/playbook-2026.md:38-43`). |
| **Zona cuscinetto** | Surveillance/buffer belt around infected areas; heightened sampling and movement/planting restrictions apply (`producers/playbook-2026.md:44-49`). |
| **Duty / prescrizione** | Source-backed legal obligation tied to land, zone, host, and time: tillage, treatment, access, reporting, movement, removal, or planting constraints. A removal order is notified by publication and must be read by regime, parcel annex, measures, exclusions, and deadline (`producers/playbook-2026.md:87-93`). |
| **Measure / funding window** | Public intervention with geography, beneficiary, cost, timing, and documentation rules. The tracked corpus names Art. 6, SRD01.01B, SRD01.01A, SRD06.01, grafting, indemnity, and the not-yet-open €30M AGEA line (`producers/playbook-2026.md:203-230`). It does not contain a complete normalized ruleset for them. |
| **Domanda / dossier** | Application package. The product decision is to prefill a dossier skeleton from parcel and official rules, not to provide regulated CAP consultancy (`CORDON.md:11-21,30-36`). The repository does not enumerate a complete field-level form schema. |
| **Graduatoria / scorrimento** | Ranked queue and later movement of applicants into processing. DDS 53/2026 moved 403 positions, then triggered a 30-day delegation upload (`producers/playbook-2026.md:205-215`). |
| **Delega** | Portal-uploaded authorization required after a ranking movement; failure triggered archival, while DDS 120/2026 reopened for ten days and then exposed applicants to forfeiture (`producers/playbook-2026.md:211-215`). |
| **Concessione** | Individual aid-concession act after entry into processing. The repo notes continuing concession acts but does not document their complete rule or acceptance workflow (`producers/playbook-2026.md:211-213`). |
| **Commitment vs cash** | Award/commitment is not payment. €55M committed versus €17M disbursed is the repository's core warning; advances and balances arrive late (`producers/playbook-2026.md:209-215`; `queries/telos-review-S2-severity-replant.md:31-36`). |
| **Field execution** | Human/contractor work after or alongside legal/funding decisions: tillage, adult treatment, felling, replanting, grafting, inspection access, evidence capture. The corpus specifies many duties but only fragments of scheduling, assignment, completion, and verification. |
| **Verified field action** | Program target for closing the administrative loop, stated in `AGENTS.md:29-33`, but not yet backed by an end-to-end tracked operational schema in this repository. |
| **Source state** | Current, superseded, not located as of date, or conflicting. The product must not fabricate provenance or state (`CORDON.md:48-55`) and dates/acts must be rechecked before action (`producers/playbook-2026.md:19-20`). |

## 3. Actor map

### Product and governance actors

| Actor | Role, decision rights, handoff |
|---|---|
| **Owen** | Decides direction, external sends, spend, true ambiguity, and load-bearing domain/product interpretations. Receives escalations from Connor (`AGENTS.md:35-39`). |
| **Connor** | Specifies, synthesizes primary evidence, reviews, orchestrates, and resolves escalations. Read-only on Foundry. Handoff is Ferro → Connor → Owen (`AGENTS.md:35-39`). |
| **Ferro** | Sole Foundry writer/implementer; integrates and merges only after review PASS (`AGENTS.md:35-39`). This is product governance, not a domain workflow actor. |
| **CORDON product** | Computes and reproduces source-cited official requirements; does not certify status, prescribe treatment, give litigation strategy, or practice application consultancy (`CORDON.md:68-71`; `producers/playbook-2026.md:13-20`). |

### Users, intermediaries, and applicants

| Actor | Decisions and work |
|---|---|
| **Owner / proprietor** | Checks whether parcel is named, receives legal effect through publication, grants access, performs or arranges duties, and may apply for aid. Owners do not necessarily receive certified letters (`producers/playbook-2026.md:87-93`). |
| **Conduttore / farm manager** | Shares region-wide tillage obligations and operational responsibility for agricultural land (`producers/playbook-2026.md:97-114`). |
| **Public/private land manager** | Responsible for uncultivated surfaces, public green, roadsides, canals, and demanio; public bodies may delegate execution to farmers (`producers/playbook-2026.md:108-112`). |
| **Producer / farmer / estate** | Makes discrete test, graft, replant, comply, diversify, and recordkeeping decisions. The repository says these are 2–4 decisions per decade, not a weekly SaaS need (`queries/telos-review-S7-producer-market.md:19-24,40-49`). |
| **Cooperative / OP / DOP consortium / AMO / GAL** | Paying/channel user and batch coordinator. It gathers member parcel/CUAA data, monitors calls/deadlines, and is the intended licensee of dossier tooling (`CORDON.md:13-21,30-36`; `queries/telos-review-S7-producer-market.md:7-17`). |
| **CAA** | Holds/mediates live fascicolo and application records; expected source for CUAA/parcel data unavailable publicly. It is also an intended product licensee (`data/DATA_UNIVERSE_GEO.md:67-70`; `CORDON.md:13-17`). |
| **Agronomist / DPI-licensed advisor** | Owns product/dose/spray choice and individualized agronomy; CORDON only reports the official obligation and source (`producers/playbook-2026.md:19,116-122`; `queries/telos-review-S9-producer-playbook.md:43-47`). |
| **Lawyer / TAR** | Owns individual challenge or appeal strategy; product may explain the generic notification mechanism only (`producers/playbook-2026.md:91-93`; `queries/telos-review-S9-producer-playbook.md:43-47`). |
| **Commercialista / finance advisor** | Owns business plans and credit files; the corpus does not define a finance-authorization role for payment preparation (`producers/playbook-2026.md:19`; `queries/telos-review-S9-producer-playbook.md:45-47`). |
| **Nursery / Agromillora / polo antixylella** | Supplies passported authorized cultivars; capacity and proprietary stock constrain field conversion (`queries/telos-review-S2-severity-replant.md:38-44`; `producers/playbook-2026.md:175-199`). |

### Authorities and operational bodies

| Actor | Decisions, outputs, and handoffs |
|---|---|
| **Regione Puglia / Dipartimento Agricoltura / AdG** | Publishes maps, calls, rankings, concession acts, action plans, deadlines, and CSR rules. Web publication can have full notification effect (`producers/playbook-2026.md:203-230`). |
| **Osservatorio Fitosanitario** | Sole authority for phytosanitary status/demarcation; receives suspect reports; issues or supports monitoring/prescriptions. CORDON must not impersonate it (`producers/playbook-2026.md:13-20,124-128`). |
| **ARIF** | Operational monitoring/felling capacity and potential compliance-verification buyer. Crew throughput is not captured by contracts alone and remains an accesso-civico target (`data/DATA_UNIVERSE_CIVIC.md:31-36,102-106`). |
| **Comune / albo pretorio** | Publishes orders for the legally effective seven-day notice period and may receive support/delegate field work (`producers/playbook-2026.md:87-93,108-112`). |
| **Carabinieri Forestali** | Checks compliance with juvenile vector-control soil works (`producers/playbook-2026.md:108-114`). |
| **CNR-IPSP / UniBari DiSSPA / official labs** | Produce official diagnostic results and are named in lab-service awards; monitoring points can carry protocol/document confirmation (`data/DATA_UNIVERSE_CIVIC.md:31-36`; `data/DATA_UNIVERSE_GEO.md:21-25`). |
| **AGEA** | Payer/transparency source for relevant schemes, but not every Art. 6 flow; administers the €30M national line when opened and performs controls (`data/DATA_UNIVERSE_CIVIC.md:12-19`; `queries/telos-pivot-verification.md:14-15`). |
| **SIAN** | Portal/record system for current fascicolo and two-year rolling beneficiary transparency. Requires annual harvesting to avoid history loss (`data/DATA_UNIVERSE_CIVIC.md:14-19`; `data/DATA_UNIVERSE_GEO.md:67-70`). |
| **MASAF / MEF** | National measure and funding-rule actors, including the €30M replant/conversion criteria and transfer to AGEA (`queries/telos-pivot-verification.md:12,15`). |
| **InnovaPuglia** | Holds parcel↔coordinate resolution outputs used in DDS and is an administrative/data handoff point (`data/DATA_UNIVERSE_CIVIC.md:102-107`). |
| **Guardia di Finanza** | Post-scandal control partner; tighter audit/document expectations are an inferred consequence, not a fully modeled workflow (`producers/playbook-2026.md:217-220`). |
| **TAR / courts** | Appeal adjudication. Repository probes report pro-administration outcomes and uphold notice by publication (`data/DATA_UNIVERSE_CIVIC.md:50-53`). |
| **Field crews / contractors** | Execute sampling, tillage, felling, grafting, planting, or treatment. Their contracts may be discoverable via ANAC/EmPULIA/BURP, but assignment, availability, scheduling, and completion records are absent (`data/DATA_UNIVERSE_CIVIC.md:31-36`). |
| **Finance authorizer** | **Not identified in the tracked corpus.** No named role, segregation rule, approval threshold, or payment-release interface supports the fifth starting assertion.

## 4. Workflow evidence by function

### 4.1 Land

**Core decision.** Establish the parcel and current official legal geography before deriving duties or funding applicability. The current program contract states the prototype input as parcel coordinates with optional CUAA/particella from the coop and outputs zone status, measures, conditions, calendar, and dossier skeleton (`CORDON.md:30-36`). Public data can now do more than that legacy input statement implies: SIT Puglia supports point→parcel on a 2021 cadastral snapshot, AdE WFS supports current parcel geometry, and official Xylella zone polygons are queryable (`data/DATA_UNIVERSE_GEO.md:11-19,27-31,53-57`).

**Inputs.** Coordinate; comune/foglio/particella; optional CUAA/fascicolo from coop/CAA; official zone layers; decree-versioned historical zones; DOP/PPTR/land-use constraints; monumental registry; host/species and monitoring records (`data/DATA_UNIVERSE_GEO.md:34-44,88-99`).

**State transitions.** `unresolved parcel → validated parcel geometry → official zone/regime as-of act → applicable duty/measure set`. A parcel can move from zona indenne to a new eradication AD overnight, so cached status must carry an as-of date and source act (`producers/playbook-2026.md:24-52`). Historical status is separately recoverable from decree-versioned layers and BURP annexes (`data/DATA_UNIVERSE_CIVIC.md:55-66`).

**Outputs.** Cited parcel identifier, geometry provenance, current and historical regime, intersecting constraints, monumental status, applicable duties/measures, and unresolved data gaps. Owner identity must be masked in public demos even when published in an act (`AGENTS.md:98-104`; `CORDON.md:68-71`).

**Exceptions and pain points.** Current CUAA↔parcel/crop link remains gated; live data comes through the CAA/customer (`data/DATA_UNIVERSE_GEO.md:67-70`). SIT cadastral geometry is stale to September 2021; AdE WFS is current but must be used instead of the WMS image layer (`data/DATA_UNIVERSE_GEO.md:27-31,53-57`). A parcel can intersect more than one legal layer. Monumental status changes removal derogation and funding relevance (`data/DATA_UNIVERSE_GEO.md:34-38`). The repo does not define conflict resolution for source disagreement or partial intersection beyond general “do not choose quietly” doctrine (`AGENTS.md:73-81`).

**Tools.** SIT Puglia ArcGIS `DatiPubbliciFasceXF`, `Background/Catasto`, `UliviMonumentali`, historical PSR zone layers; AdE INSPIRE WFS; BURP; emergenzaxylella viewer; CAMP workbooks and derived inventory (`data/DATA_UNIVERSE_GEO.md:7-44`; `data/CAMP_XLSX.md:1-7`).

### 4.2 Funding

**Core decision.** Funding is a versioned portfolio and queue, not one eligibility question. Candidate lines include Art. 6, SRD01.01B, related CSR lines, grafting, indemnity, ST1 compensation, and a €30M national line that was real but not open as of the repository date (`producers/playbook-2026.md:203-230`; `queries/telos-pivot-verification.md:14-15`).

**Inputs.** Parcel/regime; beneficiary and fascicolo; crop/cultivar; monumental status; call act and amendments; funding window state; eligible-cost rules; budget; ranking position; prior application/concession/payment; required evidence. The corpus only has fragments of the last three input families.

**Decisions.** `potentially applicable?`, `window open/current?`, `beneficiary/geography/cost eligible?`, `application already in queue?`, `ranking moved?`, `delegation or other response due?`, `concession issued?`, `pursue now / monitor / reject / escalate exception?`. The repo's strongest finding is that administration and capital, not biological knowledge, bind replant (`queries/telos-review-S2-severity-replant.md:23-44`).

**Triggers and state transitions.** Publication of an avviso opens a window; closure freezes intake; scorrimento moves ranked applications into processing; web publication starts a 30-day delegation deadline; failure causes `archiviazione d'ufficio`; DDS 120/2026 reopens for ten days; failure then causes `decadenza`; concession acts follow; commitment and payment are later distinct states (`producers/playbook-2026.md:205-215`). For the €30M line, “announced/imminent” remained `not open`, showing why a monitor must not invent an actionable state (`queries/telos-pivot-verification.md:14-15,23-25`).

**Outputs.** Comparable measure assessment with rule citations; open/closed/not-located status; next trigger/date; disqualifier/exception list; evidence required; queue/concession/payment state where known; do-not-promise warning. The program decision is to expose measures and a deadline calendar, not forecast ranking outcomes (`CORDON.md:30-36`; `queries/telos-review-S9-producer-playbook.md:43-52`).

**Pain points and feedback loops.** Demand is roughly 2.8× Art. 6 allocation and cash lags commitments (`queries/telos-review-S2-severity-replant.md:31-36`). Silent portal deadlines kill applications (`producers/playbook-2026.md:211-215`). Fraud/audit findings create a feedback loop: weak verification → phantom plantings → GdF/AGEA scrutiny → tighter documentation burden for honest applicants (`producers/playbook-2026.md:217-220`). Nursery capacity constrains what a funded plan can execute (`queries/telos-review-S2-severity-replant.md:38-44`).

**Challenge to sequentiality.** The starting assertion “complete Funding evaluation then pursue” is too linear. Funding windows, rankings, land status, and applicant records change independently. The repository supports a continuously versioned assessment and deadline watch, with pursuit only after critical eligibility and source-state exceptions are resolved. It does not support waiting for a globally complete portfolio evaluation before monitoring or preparing time-sensitive actions.

### 4.3 Applications

**Core product decision.** The repository repeatedly proposes `parcel in → zone status → measures → eligibility conditions → deadline calendar → pre-filled dossier skeleton`, licensed to coops/OPs/CAAs so CORDON tools dossier work without practicing consultancy (`CORDON.md:13-21,30-36`; `queries/telos-pivot-resilience-os.md:46-55`).

**Known actors and handoffs.** Member/producer supplies or confirms parcel and holding data → coop/OP/CAA supplies CUAA/fascicolo and selects the measure → engine prepares source-cited fields and unresolved exceptions → human intermediary resolves exceptions and submits on the official portal → Regione/AdG ranks and later issues concession acts → applicant uploads triggered delegation or later evidence. The first half is a product decision; only the scorrimento/delega/concession fragment is evidenced operationally in this repository (`producers/playbook-2026.md:205-215`).

**Known inputs.** Parcel geometry/status, CUAA/fascicolo, measure/call/version, authorized cultivars, legal/land constraints, applicant/holding data, deadlines, and source citations. **Missing inputs:** the complete official application forms, field-level schemas, attachment checklist, signature/delegation rules, co-applicant/collective-application rules, validation codes, amendment/variant rules, duplicate/conflict checks, and portal response/error model.

**Known outputs.** A dossier **skeleton**, not a submission-ready claim. It must state private analysis, retain provenance, cite every field, and never predict award (`CORDON.md:48-55,68-71`; `queries/telos-review-S9-producer-playbook.md:37-50`).

**Exceptions.** Missing or conflicting cadastral identity; missing live fascicolo; ambiguous zone intersection; monumental status; source act superseded or not located; window not open; applicant already queued; portal trigger active; field evidence absent; cultivar supply mismatch; legal/advisory boundary. The repo says gaps must remain explicit and source state cannot be fabricated (`CORDON.md:48-55`; `producers/playbook-2026.md:263-274`).

**Pain points.** Rules are fragmented across acts and change mid-season; new foci create users with the wrong inherited mental model; publication itself starts deadlines; trust is low after payment-control failures (`queries/telos-review-S9-producer-playbook.md:37-41`; `queries/telos-pivot-resilience-os.md:5-16,24-28`).

**Evidence limit.** No tracked artifact demonstrates a real application automatically prepared, exception-resolved, submitted, accepted, or amended. “Auto-prepared Applications with exception resolution” is a design hypothesis/decision, not a verified workflow outcome.

### 4.4 Field Work

**Duty derivation and execution must remain separate.** Land/regime answers what must or may happen. Field work answers who performs it, when, with what materials, under which exception, and what proves completion. The product may reproduce official duties but may not invent agronomy (`CORDON.md:68-71`).

**Duty triggers.** Region-wide juvenile-vector dates trigger tillage/ground work; annual adult-treatment determina triggers treatment by comune/crop and authorized actives; positive/suspect/same-species proximity triggers different removal rules by regime; planting zone triggers cultivar and movement restrictions; suspect symptoms trigger reporting; order publication triggers inspection/removal clocks (`producers/playbook-2026.md:97-128,132-199`).

**Execution methods and exceptions.** Soil work can be ploughing, milling, harrowing, or mowing with sward ≤10 cm; inaccessible slopes/roadsides allow fire/steam and herbicide only where physical means are impossible; crop parcels may require under-canopy work; protected areas/woods/pines/private gardens have stated exceptions (`producers/playbook-2026.md:97-114`). Eradication removes infected, suspect, same-species, and certain untested specified plants; tested other species and plants not infected in the prior two years may receive relief; non-susceptible species and tested historic trees can be excluded (`producers/playbook-2026.md:136-150`). Containment removes infected plants only, with additional strip bans (`producers/playbook-2026.md:152-156`).

**Human roles.** Owner/manager or delegated farmer executes tillage; licensed advisor chooses plant-protection product/dose; nursery provides passported stock; field crew removes/plants/grafts; inspector/lab establishes official result; Carabinieri checks tillage; Osservatorio/ARIF manages official control. The repository does not identify a dispatcher/scheduler, crew assignment rule, SLA, availability calendar, or acceptance authority.

**Inputs.** Parcel/status/duty; act and deadline; host/cultivar; exceptions; field accessibility; crew/equipment/material; nursery stock/passport; order annex; inspection/lab result; funding/concession constraints. Only the legal and biological inputs are substantially documented.

**Outputs.** Expected operational outputs include scheduled work order, completion evidence, georeferenced photos, invoices/delivery notes/passports, inspector confirmation, exception/escalation, and updated parcel/action state. The repo explicitly advises keeping invoices, delivery notes, passports, and georeferenced photos under tighter audit conditions (`producers/playbook-2026.md:217-220`) but does not define their schemas or review gates.

**Scheduling and feedback.** Deadlines move annually and can be extended mid-season (`producers/playbook-2026.md:97-121`). Positive result → removal → panel attrition creates survivorship bias in monitoring (`CORDON.md:52-55`; `queries/telos-review-S8-product-feasibility.md:31-37`). Detection → order → felling delay → neighborhood conversion is proposed as a measurable feedback loop, but the operational felling-date dataset is not built (`queries/telos-review-S1-spread.md:49-52`). Field completion → payment/control should be another loop, but it is not modeled.

**Evidence limit.** “Auto-prepared source-supported Field Work with human scheduling” is partly supported at the work-definition level. Source support is strong; auto-preparation is a reasonable design; human scheduling is necessary. The repository contains no verified scheduling or dispatch workflow and has a critical 2026 adult-treatment source gap (`producers/playbook-2026.md:116-122,263-269`).

### 4.5 Payments

**Observed states.** The corpus distinguishes application, entry into processing, concession/commitment, advance, balance, and actual disbursement. It warns that commitments are not cash and payments arrive years later (`producers/playbook-2026.md:205-215`; `queries/telos-review-S2-severity-replant.md:31-36`).

**Observed controls and evidence.** AGEA/SIAN can expose recent per-beneficiary payments; Art. 6 flows may require regional cross-check; OpenCoesione and FarmSubsidy could extend project/history; audit findings compare payments with plant-count change (`data/DATA_UNIVERSE_CIVIC.md:12-29`; `producers/playbook-2026.md:217-220`). The applicant is advised to retain invoices, delivery notes, passports, and georeferenced photos (`producers/playbook-2026.md:217-220`).

**Inferred state chain, not a verified full workflow.** `concession/award → authorized field plan → work performed → evidence/expense dossier → claim/advance/balance request → administrative/technical control → finance authorization → AGEA/region payment → transparency/audit reconciliation`. Only scattered nodes are evidenced. The repository does not track award-letter clauses, eligible-cost calculation, procurement requirements, variant approvals, expenditure dates, invoice matching, claim forms, inspection acceptance, payment calculation, recoveries, or authorization segregation.

**Actors missing.** No “finance authorizer” is named. It is unclear whether approval sits with Regione/AdG, AGEA, another paying agency, or a cooperative internal finance role for each measure. No consequence-based approval matrix exists in the tracked corpus.

**Assertion verdict.** “Award-rule-driven Payment preparation with finance authorization” is **not confirmed**. The repository supports the need for source-cited award rules, evidence packs, and separate authorization, but does not contain the rules or operating workflow necessary to implement or verify them.

## 5. Connected workflow evidence

### Repository-supported spine

1. **Capture/validate parcel.** Coordinate and/or foglio/particella; obtain CUAA/fascicolo from coop/CAA where needed (`data/DATA_UNIVERSE_GEO.md:27-31,53-70`).
2. **Resolve official legal state.** Overlay official current zones and cite the establishing/updating act; preserve historical state (`data/DATA_UNIVERSE_GEO.md:11-19,88-99`).
3. **Derive duties and constraints.** Removal regime, vector control, replant/movement, monumental and landscape exceptions (`producers/playbook-2026.md:24-199`).
4. **Evaluate funding portfolio continuously.** Match geography/beneficiary/cost/window, distinguish not-open from open, monitor scorrimenti and amendments (`producers/playbook-2026.md:203-230`).
5. **Prepare application skeleton.** Populate source-backed fields; expose unresolved exceptions; hand to coop/OP/CAA and human adviser (`CORDON.md:13-21,30-36`).
6. **Submit and react to administrative triggers.** Official portal submission is outside the documented repository flow; one evidenced post-ranking trigger is delegation upload within 30/10 days (`producers/playbook-2026.md:211-215`).
7. **Receive concession/award.** Individual concession acts exist, but rule extraction and award-condition state are not documented (`producers/playbook-2026.md:211-213`).
8. **Translate award + legal duties into field work.** Produce source-cited work definition; licensed/human actors schedule and execute. This is an intended handoff, not a demonstrated automation (`CORDON.md:50-51,68-71`).
9. **Capture completion and cost evidence.** Photos, invoices, delivery notes, passports are named but not schematized (`producers/playbook-2026.md:217-220`).
10. **Prepare and authorize payment claim.** Repository gap.
11. **Disburse and reconcile.** Transparency and audit sources can show cash and anomalies; no case-level end-to-end trace exists (`data/DATA_UNIVERSE_CIVIC.md:12-29`).
12. **Feed outcomes back.** Official monitoring changes land state; field completion changes evidence/payment state; audit findings tighten documentation; nursery capacity changes feasible scheduling; post-positive removal distorts monitoring panels. Only the monitoring and audit loops are documented.

### State model implied by evidence

`PARCEL_UNRESOLVED → PARCEL_VALIDATED → OFFICIAL_STATE_AS_OF_ACT → DUTIES_DERIVED`  
`→ FUNDING_CANDIDATE → {NOT_OPEN | INELIGIBLE | ELIGIBLE_OPEN | EXCEPTION}`  
`→ DOSSIER_DRAFT → HUMAN_RESOLUTION → SUBMITTED → RANKED_WAITING → CALLED_BY_SCORRIMENTO`  
`→ DELEGA_DUE → {ARCHIVED | REOPENED_10D → FORFEITED | IN_PROCESSING}`  
`→ CONCESSION/COMMITMENT → FIELD_PLAN → SCHEDULED → EXECUTED → EVIDENCE_READY`  
`→ PAYMENT_CLAIM → TECHNICAL_CONTROL → FINANCE_AUTHORIZED → {ADVANCE | BALANCE | HOLD | RECOVERY}`.

The first two lines have substantial repository evidence. From `DOSSIER_DRAFT` onward, evidence becomes progressively fragmentary. The final payment line is a proposed model required by the starting assertions, not a repository-proven workflow.

### Handoffs and failure modes

- **Authority → engine:** acts, polygons, calls, rankings, deadlines. Failure: superseded/missing act or incorrect zone semantics.
- **Member → coop/CAA:** parcel/CUAA/fascicolo and intent. Failure: incomplete or conflicting identity/holding record.
- **Engine → intermediary:** cited draft + exceptions. Failure: false “ready” state when forms/rules are missing.
- **Intermediary → portal:** submission/delegation. Failure: silent publication clock and portal deadline.
- **Authority → applicant:** ranking/concession. Failure: commitment mistaken for cash.
- **Award/legal state → field scheduler:** authorized work and constraints. Failure: supply/crew/deadline mismatch or unauthorized agronomy.
- **Field → evidence/payment:** proof of planting/removal/work. Failure: weak evidence, phantom planting, rejected/held claim.
- **Control → program:** audit findings and new acts. Failure: stale rules remain on dependent surfaces.

## 6. Product and user findings

1. **The user is an intermediary operations team, not a mass farmer SaaS user.** Buying power and adoption concentrate in coops/OPs/consortia, while direct farm software willingness to pay is low and Xylella decisions are episodic (`queries/telos-review-S7-producer-market.md:7-17,40-49`).
2. **The job is translation and coordination.** Users need one place connecting parcel status, duties, measures, deadlines, and evidence. The repo says the current legal matrix is scattered across acts and changes mid-season (`queries/telos-review-S9-producer-playbook.md:37-41`).
3. **Auditability is a product requirement, not decoration.** Every output field needs decree/article provenance because post-scandal intermediaries absorb fraud and reputational risk (`queries/telos-pivot-resilience-os.md:24-28`).
4. **Freshness is recurring value.** Farmer decisions are infrequent, but calls scroll, decrees change, campaigns refresh, and portal clocks start silently. The pivot converts static briefs into a recurring per-body service (`queries/telos-pivot-resilience-os.md:59-61`).
5. **The sharpest pain is administrative latency and opacity.** Oversubscription, years-long queue movement, commitment/cash divergence, and short notification windows dominate (`queries/telos-review-S2-severity-replant.md:31-44`; `producers/playbook-2026.md:205-215`).
6. **Land status is high consequence.** Applying containment logic to an eradication parcel can cost healthy same-species trees; the reverse can wrongly imply removal (`producers/playbook-2026.md:132-156`).
7. **The product must abstain on missing source state.** The €30M line was real but not open; the 2026 adult-treatment act was not located; no invented deadline or treatment is acceptable (`queries/telos-pivot-verification.md:14-15`; `producers/playbook-2026.md:116-122`).
8. **Existing official tools are inputs, not competitors.** Official parcel lookup exists, but it does not assemble history, measure fit, deadlines, dossier fields, or evidence state. Rebuilding a plain zone lookup is explicitly killed (`queries/telos-review-S9-producer-playbook.md:37-50`).
9. **Human professional boundaries matter.** CAA/application specialists, agronomists, lawyers, commercialisti, inspectors, and finance approvers retain regulated or consequence-bearing decisions (`producers/playbook-2026.md:19`; `queries/telos-review-S9-producer-playbook.md:43-50`).
10. **No tracked user research validates exception-resolution or scheduling UX.** Named channels and an exemplar exist, but no interview notes, observed dossier walkthrough, task timing, error log, or acceptance study is tracked.

## 7. Starting assertions: confirmed or challenged

| Starting assertion | Verdict | Repository evidence and correction |
|---|---|---|
| **Land status/duties vs Field execution** | **Confirmed and sharpened.** | Status and duty derivation are authoritative/legal; execution is human/operational. Same land can change regime, and execution methods/exceptions differ. Product must produce a cited duty without pretending the work occurred (`CORDON.md:68-71`; `producers/playbook-2026.md:24-52,97-199`). Add explicit states for `duty derived`, `scheduled`, `executed`, and `verified`. |
| **Complete Funding evaluation then pursue** | **Challenged.** | The portfolio is dynamic; some measures are closed, queued, amended, or not open. Waiting for global completeness conflicts with short publication clocks. Correct pattern: continuously versioned funding assessment, pursue only after critical eligibility exceptions clear, and monitor triggers in parallel (`producers/playbook-2026.md:203-230`; `queries/telos-pivot-verification.md:14-15`). |
| **Auto-prepared Applications with exception resolution** | **Partially confirmed as a decision; unverified as a workflow.** | Parcel→cited dossier skeleton is the accepted product route (`CORDON.md:13-21,30-36`). No complete form schema, exception taxonomy/state machine, portal integration, or real accepted application exists in this corpus. Human CAA/coop resolution must remain explicit. |
| **Auto-prepared source-supported Field Work with human scheduling** | **Partially confirmed; scheduling unproven.** | Duties, methods, exceptions, and source acts are rich enough to generate a work definition. The repository lacks scheduler, crew/resource calendar, dispatch, acceptance, and completion schemas; one annual treatment act is missing/stale (`producers/playbook-2026.md:97-199,263-269`). |
| **Award-rule-driven Payment preparation with finance authorization** | **Challenged / unsupported.** | The corpus distinguishes commitments, advances, balances, and cash and names evidence to retain, but it has no award-rule parser, claim schema, eligible-cost calculation, technical-control workflow, finance role, authorization matrix, or payment case trace (`producers/playbook-2026.md:205-220`; `data/DATA_UNIVERSE_CIVIC.md:12-29`). Treat this as a discovery hypothesis, not repository fact. |

## 8. Contradictions and staleness

1. **Monumental registry blocked vs unblocked.** `queries/telos-synthesis.md:14-20,22-30` and `producers/STRATEGY.md:20-29` call grafting triage blocked. `data/DATA_UNIVERSE_GEO.md:34-38` and `data/DATA_UNIVERSE_FLIPS.md:14-16,43-47` prove a 341,428-record layer. `CORDON.md:21-24` adopts the unblocked state. Older claims are superseded assumptions.
2. **Action plan version.** The playbook still grounds duties in DGR 1593/2024, Piano 2024–2026 (`producers/playbook-2026.md:69,116-122,251-255`). The flip audit says DGR 1075/2025, Piano 2025–2027, supersedes it (`data/DATA_UNIVERSE_FLIPS.md:14,41,47`). `CORDON.md:36-38` acknowledges the pending update. The playbook is stale for shipment.
3. **ArcGIS output format.** `data/DATA_UNIVERSE_FLIPS.md:9-16` instructs `f=geojson`. The more detailed `data/DATA_UNIVERSE_GEO.md:7-10` says `f=geojson` is unsupported and to use Esri `f=json`. The implementation instruction in FLIPS is stale/wrong.
4. **Parcel geometry wording.** `data/DATA_UNIVERSE_FLIPS.md:12` describes AdE WMS/GML as solving geometry. `data/DATA_UNIVERSE_GEO.md:53-57` clarifies WMS is image-only and WFS is the live geometry route. The latter is more precise.
5. **Seven-day order availability.** The playbook emphasizes seven-day albo publication and no certified letter (`producers/playbook-2026.md:87-93`). The civic audit shows regional DDS persist in BURP and other archives (`data/DATA_UNIVERSE_CIVIC.md:40-48`). Both can be true: seven days is the legal-notification clock, not the data-retention limit. Product workflow must monitor the clock but can recover history permanently.
6. **Static brief vs recurring product.** S7 says Xylella creates 2–4 decisions per decade and rejects farmer subscription (`queries/telos-review-S7-producer-market.md:19-24,40-49`). The pivot adopts recurring per-body subscription because campaigns, calls, and decrees have recurring cadence (`queries/telos-pivot-resilience-os.md:59-61`). This is a channel/cadence correction, not proof of farmer recurring demand.
7. **Funding counts.** Art. 6 appears as 9,186 requests versus another 9,136 figure and 1,341 paid (`producers/playbook-2026.md:205-213`). The repo flags source variation but does not reconcile applicant vs request vs paid definitions.
8. **Live monitoring count.** The same ArcGIS probe returned 210 then 340 2026 pauca positives depending on query (`data/DATA_UNIVERSE_GEO.md:21-25`). It is unsafe to treat a single live count as stable without query/capture metadata.
9. **Raw paper manifest stale.** `raw/papers/MANIFEST.md:16-22` lists Montilon, Sabella, and Ahern as NOT YET while tracked text/PDF artifacts now exist under `raw/articles/` or `raw/supp/`. The manifest no longer accurately inventories the frozen source library.
10. **Raw immutability/schema drift.** `SCHEMA.md:21-31,47-48` requires raw-source URL/ingest/hash metadata and treats raw as immutable. Many tracked raw extracts are plain `.txt`/HTML captures without the declared frontmatter, and multiple `.docx`/`.xlsx` files are actually HTML captures or empty placeholders. Provenance quality is uneven.
11. **Binary supplemental corruption/mislabeling.** `raw/supp/lanotte-2024-DataSheet1.docx`, `lanotte-DataSheet1.docx`, `lanotte-Table{1,2,6}.docx`, and `lanotte-Table{3,4,5}.xlsx` are HTML rather than OOXML; four `try_*` files are empty. Valid replacements exist under `raw/supp/lanotte-epmc/`, but the duplicates make source selection error-prone.
12. **Legacy authority boundary.** `CORDON.md:25-28` says legacy Wedge 1 artifacts are historical records. `AGENTS.md:15-19` points current product/architecture/legal authority outside this repository. This lane therefore proves repository program evidence, not current wedge implementation authority.

## 9. Repository blind spots

### End-to-end product evidence

- No complete call/measure register with normalized legal version, window, geography, beneficiary, eligible costs, exclusions, evidence, award conditions, and payment rules.
- No tracked official application forms, portal schema, validation responses, attachment checklist, signature/delegation rules, or collective-application agreement.
- No real dossier instance traced from parcel intake through submission, ranking, concession, field execution, and payment.
- No exception ontology with owner, evidence needed, SLA, escalation, waiver, resolution, and audit trail.
- No user-research corpus from coop operations managers, CAA operators, applicants, field coordinators, or finance teams.

### Land and legal state

- Current CUAA↔parcel/crop linkage is not public and no customer-supplied sample is tracked (`data/DATA_UNIVERSE_GEO.md:67-70`).
- No repository rule settles partial intersections, competing acts, geometry vintage mismatch, or source disagreement at product level.
- Current legal owner documents live outside the repository according to `AGENTS.md:15-19`; this lane cannot verify them.
- The tracked repository contains notes about official acts, not a complete frozen, hashed legal-act corpus.

### Funding and applications

- Measure eligibility beyond headline geography/cultivar/budget is mostly absent.
- Ranking, concession, variant, withdrawal, appeal, and reopening states are not normalized.
- “Dossier skeleton” is not defined field-by-field and has no readiness/abstention criteria.
- No actual portal/API integration or manual-submission handoff is documented.

### Field work

- No crew roster, contractor qualification, equipment, nursery inventory, scheduling calendar, task duration, route, weather constraint, field-access consent, or dependency model.
- No completion/acceptance schema for tillage, treatment, felling, grafting, or planting.
- No authoritative 2026 adult-treatment act; no public compliance-inspection outcome dataset (`data/DATA_UNIVERSE_FLIPS.md:14,24-25`).
- Procurement records can reveal contract values/winners, but not actual crew availability or daily throughput (`data/DATA_UNIVERSE_CIVIC.md:31-36,102-106`).

### Payments

- No award-letter rule extraction or award-condition model.
- No eligible-cost ledger, procurement rule, invoice/delivery-note/passport matching, advance/balance calculation, inspection acceptance, hold/recovery, or bank/payment-release workflow.
- No identified finance authorizer or segregation-of-duties model.
- SIAN history is rolling two years; no tracked harvest proves case-level payment history (`data/DATA_UNIVERSE_CIVIC.md:14-23`).
- Audit numbers are aggregate/secondary in the playbook; the repository lacks a beneficiary-level ground-truth reconciliation.

### Corpus/provenance

- No tracked `references/` directory exists in the 186-file git inventory, despite the broader program convention referring to reference fact banks elsewhere. This report does not treat absent/untracked references as read.
- Raw campaign workbooks are gitignored and represented by inventory/analysis, not tracked primary files (`data/CAMP_XLSX.md:1-7`).
- Several source binaries are corrupt, mislabeled, duplicates, or placeholders; `raw/papers/MANIFEST.md` is stale.
- Historical reviews restate facts across many files, producing the contradictions the one-owner doctrine warns against (`AGENTS.md:73-81`).

## 10. Unresolved questions

1. Which exact official measures are in first-release scope, and where are their current acts, forms, amendments, eligible-cost rules, and award/payment conditions frozen?
2. What is the authoritative interpretation and precedence rule when parcel geometry, zone layers, and current acts disagree or only partially intersect?
3. What minimum coop/CAA-supplied fields are required to link parcel, CUAA, fascicolo, existing application, and beneficiary without exposing owner identity in public demos?
4. What makes a funding assessment “complete enough to pursue” for one measure, and which unknowns force abstention versus human exception resolution?
5. What are the actual application form fields, attachments, signatures, delegations, collective-applicant agreements, and portal validations for Art. 6 and SRD01.01B?
6. Who owns each application exception: member, coop operations manager, CAA operator, agronomist, lawyer, Regione help desk, or CORDON reviewer?
7. What event proves `submitted`, `received`, `admissible`, `ranked`, `called`, `conceded`, `varied`, `withdrawn`, `archived`, or `forfeited`?
8. Does the 2026 adult-treatment determina exist; if so, what are its exact comuni, crops, deadline, substances, and supersession chain?
9. Who schedules tillage, treatment, felling, grafting, and planting for a collective dossier, and what capacity/stock/weather/access constraints govern the sequence?
10. What completion evidence is legally sufficient for each work type, who verifies it, and how is rejected evidence remediated?
11. Which award terms authorize work before concession, require pre-approval for variants, or condition advances/balances on milestones?
12. What is the precise payment-claim flow for each measure: claim form, expense eligibility, procurement rules, inspection, calculation, hold, recovery, and appeal?
13. Who is the finance authorizer for Regione/AGEA and for the cooperative, and what segregation/threshold rules must the product enforce?
14. Can a real historical application be reconstructed end-to-end from public records and a willing coop/CAA to validate every state and handoff?
15. How will the product distinguish legal notification time, data availability time, effective date, supersession date, and observed portal publication time?
16. Which source families must be monitored at what cadence so that “current” status is defensible and silent deadlines cannot be missed?
17. How will aggregate payment/audit records be reconciled with applicant-level evidence while respecting purpose limitation and privacy?
18. What user-research evidence shows coop/CAA staff want auto-preparation and exception queues rather than a cited research brief or existing consultancy workflow?
19. Which raw-source duplicates/corrupt files are authoritative, and what manifest/hash repair is needed before they can support automated extraction?
20. What acceptance test proves the connected workflow reaches **verified field action and authorized disbursement**, rather than stopping at an attractive eligibility verdict?
