# Resistance Decoder v1 — cited target table for CNR

**Artifact:** CORDON Resistance Decoder v1 (Artifact B).
**Date:** 15 August 2026.
**Mode:** computational and literature only. **Do not synthesize** any peptide, phage stock, or editing reagent. Every AMP/phage row below carries an explicit DO NOT SYNTHESIZE flag.
**Pathogen:** *Xylella fastidiosa* subsp. *pauca* ST53, strain De Donno (XfDD) / CoDiRO; phage-work strain A0PT1.
**Scope:** why some olive genotypes stay functional under infection, and what a partner with a greenhouse and a containment lab should test first.

This version closes the v0 gap: the resistance genes that were named-only in v0 now carry real locus IDs, extracted from supplementary files that are now on disk. Two ID systems are used and never mixed:

- **La Notte et al. 2024** maps RNA-seq to *O. europaea* cv. Farga genome v9. IDs are `OE9A*`. Contrast is genotype S105 (highly resistant, quiet transcriptome, 2,897 DEGs at FDR < 0.05) vs S215 (resistant, 9,956) vs S234 (resistant, 13,080), all Xf_DDpos vs Xf_neg.
- **Giampetruzzi et al. 2016** has no olive genome. IDs are de novo xylem contig names (`lc_xylem_*` for Leccino, `og_xylem_*` for Ogliarola) plus Arabidopsis orthologues (`atNgNNNNN`). DEG counts: Leccino 659 (73 up, 586 down); Ogliarola 447.

Every ID, count, and fold change traces to a file listed in `SOURCES.md`. Nothing here is invented. Where a value could not be sourced, it is marked **GAP**.

---

## Part I — Olive resistance pathways with real locus IDs

Ranked by how much a postdoc should care for a seedling screen or a marker panel, not by p-value.

### Rank 1 — Receptor / PTI signaling (S105-enriched immune cassette)

The one immune axis that is up in resistant Leccino (Giampetruzzi 2016), up in the highly resistant seedling S105, and enriched under GO categories "protein serine/threonine kinase activity" (GO:0004674) and "ADP binding" (GO:0043531) in the S105 upregulated set (La Notte 2024). S105 is the phenotype to decode: fewest DEGs, no canopy desiccation at 24 months post vector inoculation.

**Resolved from La Notte 2024 Supplementary Table S4** (upregulated DEGs, S105 Xf_DDpos vs Xf_neg; file `Table4.xlsx`, sheet "Suppl.Table 4"). Columns reported: shrunk log2 fold change (shrunkFC) and FDR.

| Gene (Description in Table S4) | Farga v9 locus ID(s) | shrunkFC | FDR | v0 status |
|---|---|---|---|---|
| LRR receptor-like Ser/Thr kinase At3g47570 | `OE9A013998T1`, `OE9A100116T1`, `OE9A033576T1`, `OE9A024481T1`, `OE9A095595T1` | 3.55, 3.59, 3.44, 3.05, 2.95 | 1.8e-11, 9.8e-11, 7.5e-8, 5.9e-8, 7.5e-8 | had (as At3g47580) |
| SOBIR1 (LRR-RLK, RLP co-receptor) | `OE9A095575T1`, `OE9A014277T1` | 2.80, 2.74 | 5.5e-6, 2.2e-6 | **RESOLVED** |
| Wall-associated receptor kinase 2-like (WAK2) | `OE9A078886T1` | 3.00 | (padj in S4) | **RESOLVED** |
| Disease resistance RPM1-like | `OE9A109149T1` | 2.60 | 9.6e-6 | **RESOLVED** |
| Late blight resistance homolog R1A-10 | `OE9A108835T1`, `OE9A046916T1/T3`, `OE9A057321T1/T2`, `OE9A098446T1`, `OE9A025621T1/T2` | 2.71, 2.83, 2.13, 2.33, 2.79 | 1.3e-10, 3.7e-12, ~, ~, ~ | **RESOLVED** |
| Disease resistance RGA3 | `OE9A041094T1`, `OE9A102868T1` | 2.84, 2.24 | 2.7e-11, ~ | **RESOLVED** |
| Late blight resistance homolog R1B-19 | `OE9A088549T1` | 3.82 | 1.1e-11 | new (highest R-gene shrunkFC) |
| L-type lectin-domain receptor kinase-like | `OE9A010050T1` | 2.77 | ~ | new |

Note on annotation: La Notte main text calls the LRR-RLK "At3g47580"; the Supplementary Table S4 `Description` field labels the same contigs "At3g47570". Both point to the same LRR XII cluster; the ID is what the frozen table records.

Note on direction: the main text (line ~1030) mentions R1A-10 / RGA3 / RPM1-like near a clause about "highest decreased fold change," but these genes appear in the **upregulated** Table S4 with positive log2FC and are described later (line ~1332) as "overexpressed in genotype S105." The primary data (Table S4) is upregulation; that is what is reported here.

**Giampetruzzi 2016 Leccino-up receptor-like proteins (Additional file 3 / `MOESM3`, sheet "up"), strongest contigs:**

| Class (Arabidopsis orthologue) | Olive contig | log2FC | padj |
|---|---|---|---|
| RLP56 (at5g49290) | `lc_xylem_86506` | +3.53 | 5.0e-6 |
| RLP15 (at1g74190) | `lc_xylem_18210` | +3.45 | 8.5e-6 |
| RLP14 (at1g74180) | `lc_xylem_84661`, `lc_xylem_142738` | +3.32, +3.32 | 2.6e-5, 2.7e-5 |
| RLP1 / RLP13 / RLP38 / RLP45 / RLP53 | `lc_xylem_136196`, `lc_xylem_87076`, `lc_xylem_130148`, `lc_xylem_25871`, `lc_xylem_84723` | +2.8 to +3.0 | ~1e-4 |

RT-qPCR-validated LRR-LRK with a real olive TSA accession (Additional file 9 / `MOESM9`): `OG_xylem_247707` → At1g35710.1 → *O. europaea* TSA `GBKW01101615`.

### Rank 2 — Cell wall, pectin, pit-membrane seam

Anatomy plus transcriptome. Montilon 2022 (now on disk) is the mechanism: in susceptible Cellina di Nardò, XfDD degrades pit membranes (uneven, fragmented middle lamella) and spreads systemically; in Leccino, pit membranes stay compact and undegraded and vessels fill with callose-like granules that entrap the bacterium. Montilon attributes pit-membrane loss to bacterial cell-wall-degrading enzymes (CWDEs), citing Roper 2007 (Xylella requires polygalacturonase for colonization). Giampetruzzi 2016 shows 82 cell-wall DEGs down 2–8 fold in infected Leccino; the strongest single DEG in the whole Leccino set is a fasciclin-like arabinogalactan protein.

**Resolved from Giampetruzzi 2016 Additional file 3 (`MOESM3`, sheet "down"), strongest contig per gene:**

| Function (Arabidopsis orthologue) | Olive contig | log2FC | padj |
|---|---|---|---|
| FLA11 (at5g03170) — strongest Leccino DEG | `lc_xylem_247803` | −8.11 | 3.0e-68 |
| FLA (at5g03170, add'l copies) | `lc_xylem_268555`, `lc_xylem_273783`, `lc_xylem_277531` | −7.14, −5.52, −5.48 | 6e-59, 4e-23, 6e-23 |
| FLA12 (at5g60490) | `lc_xylem_236640` | −6.04 | 1.8e-33 |
| Laccase LAC17 (at5g60020) | `lc_xylem_172242` | −6.93 | 3.4e-33 |
| Laccase (at2g40370) | `lc_xylem_274416` | −6.17 | 2.8e-39 |
| Polygalacturonase PG2 (at1g70370) | `lc_xylem_186043`, `lc_xylem_221315` | −4.98, −4.07 | 2.0e-34, 9.6e-10 |
| PMEI (at5g09760) | `lc_xylem_192195` | −3.41 | 7.2e-42 |
| PMEI / PME (at3g49220 / at5g53370) | `lc_xylem_179601`, `lc_xylem_277495`, `lc_xylem_279404` | −3.27, −3.07, −3.25 | 5e-16, 3e-16, 5e-7 |

RT-qPCR-validated with olive TSA accessions (Additional file 9 / `MOESM9`): FLA `LCxylem_247803` → At5g03170 → TSA `GBKW01116148`; LAC17 `LCxylem_172242` → At5g60020 → TSA `GBKW01023045`; PME `LC_xylem_72497` → At3g14300 → TSA `GBKW01045281`.

**Ogliarola side (Additional file 4 / `MOESM4`, `og_xylem_*`):** the same axis moves in the susceptible cultivar but with expansins **up**, e.g. Expansin-like B1 `og_xylem_146321` (log2FC +5.45, padj 1.4e-13) and `og_xylem_126598` (+5.72). RT-qPCR-validated expansin `OG_xylem_175154` → At4g17030 → TSA `GABQ01072002`. Ogliarola matrix has 92 up and 354 down contigs in the file (the paper's 447 total counts a different filter intersection; the file is the DEG source, the 447 is the paper's SeqMonk∩DESeq2 number).

### Rank 3 — Lignin / phenylpropanoid reinforcement (Leccino-specific)

Sabella 2018 (J. Plant Physiol.) and Sabella 2019 (Sci Rep, on disk) are the mechanism: infected Leccino raises total stem lignin and upregulates Cinnamoyl-CoA Reductase (CCR); susceptible Cellina downregulates C4H and 4CL. This is a cultivar-level qPCR panel (β-Actin-normalized), not a Farga-mapped locus set, so IDs are GenBank mRNA accessions from Sabella's primer table, not `OE9A*`.

| Enzyme | GenBank accession (Sabella primer table) | Leccino response |
|---|---|---|
| CCR (cinnamoyl-CoA reductase) | `ACD13265.1` | up (lignin branch) |
| C4H (cinnamate-4-hydroxylase) | `JQ711532.1` | down in Cellina, not Leccino |
| 4CL (4-coumarate:CoA ligase) | `JX266203.1` | down in Cellina |
| PAL | `JX266201.1` | genotype-dependent |
| PPO (polyphenol oxidase) | `JX266193.1` | down in Leccino (FC −1.83) |

### Rank 4 — Hydraulics: cavitation resistance and refilling (Leccino-specific)

Sabella 2019 (on disk): Leccino is constitutively less cavitation-prone and refills vessels faster via starch hydrolysis. Montilon 2022 links Leccino's callose/starch granule occlusions to this refilling. qPCR IDs are olive gene names from Sabella 2019, not Farga loci.

| Gene | Leccino fold change (Sabella 2019) | Role |
|---|---|---|
| OeTIP1.1 (aquaporin) | +15.92 | embolism sensing / water flux |
| OePIP2.1 (aquaporin) | +2.04 | membrane water transport |
| OeAMY / OeAMY2 (α-amylase) | +10.20 / +9.51 | starch→sugar, osmotic refilling |
| OeSUT1 / OeMST2 (sugar transporters) | +2.74 / +5.79 | refilling osmoticum |
| OeGBSSI (starch synthase) | −62.61 | block of sucrose→starch (defence signal) |

La Notte 2024 Farga-mapped counterpart (PC1 collapse axis, down in Xf_DDpos S215/S234, from main text / Suppl. tables): Rubisco activase `OE9A079773T1`, β-amylase 3 `OE9A045257T1`, galactinol synthase `OE9A047763T1`.

### Rank 5 — Susceptibility genes (biotech door, S215/S234, NOT the S105 signature)

La Notte 2024 names these explicitly as "susceptibility genes" with published knock-outs in grape, tomato, potato, banana. They are up in the loud seedlings, not in quiet S105 — a knock-out target, not a resistance marker.

| Gene | Farga v9 ID (La Notte main text) | Note |
|---|---|---|
| DMR6-like (SA hydroxylase) | `OE9A054976T1`, `OE9A079697T1` | like VvDMR6; knock-out = resistance in model hosts |
| JOX1 / 2-OG dioxygenase (At3g11180) | `OE9A092418T1` | JA hydroxylase; up in Xf_DDpos |

### Rank 6 — Breeding-side markers (SSR, not a gene)

La Notte 2024: SSRs poorly predict Xfp phenotype. Two SSRs (**GAPU103a**, **UDO99-043**) show a positive fixation index only in susceptible genotypes — usable as a cheap discard filter, not a resistance call. POP4 (Leccino + Ogliarola + Frantoio + Pendolino) holds 52% of the HR/R/T spontaneous trees.

---

## Part II — Ten candidate interventions

Every row is a **paper hypothesis**, computational-only on our side. Format: target | why | closest published analogue | why it might fail | next lab step (for a partner with a greenhouse + containment lab). Phage/AMP rows are flagged **DO NOT SYNTHESIZE**.

Ordered by how much a postdoc should care.

### 1. Breeding marker — S105 receptor cassette (olive-side)
- **Target:** the S105 immune set now with real IDs — LRR-RLK `OE9A013998T1`/`OE9A100116T1`, SOBIR1 `OE9A095575T1`, WAK2 `OE9A078886T1`, RPM1-like `OE9A109149T1`, RGA3 `OE9A041094T1`, R1A-10 `OE9A108835T1`.
- **Why:** the only immune cassette that is up in resistant Leccino (2016) and enriched in the quiet HR seedling S105 (La Notte 2024, Table S4).
- **Closest analogue:** grapevine *PdR1b* RLK/RLP cluster (cited by La Notte).
- **Why it might fail:** polygenic; SSRs already failed as predictors; S105 titer is not low, so a marker could select functional canopies that still feed vectors.
- **Next lab step:** design KASP/ampliseq assays on these OE9A loci; genotype the 61 Leccino progeny; score against existing field HR/R/T calls. No new inoculation needed.

### 2. Breeding marker — S215 colonization-block phenotype (olive-side)
- **Target:** the S215 "infection does not progress" trait (2/n qPCR-positive at 24 mpvi), not a single gene.
- **Why:** closest genotype in the corpus to beating parental Leccino on both symptoms and titer trajectory.
- **Closest analogue:** La Notte inoculation panel; Cipressino as donor parent.
- **Why it might fail:** S215 is a virus-positive (OLYaV, OLV-1) rootstock piece; phenotype may be scion/rootstock or virus confound.
- **Next lab step:** re-inoculate virus-indexed S215 ramets; if the block holds, map it; if it vanishes, discard.

### 3. Pit-membrane / cell-wall reinforcement screen (olive-side)
- **Target:** FLA11/FLA12 `lc_xylem_247803`/`lc_xylem_236640`, PG2 `lc_xylem_186043`, PMEI `lc_xylem_192195`, plus Leccino callose/lignin (CCR `ACD13265.1`).
- **Why:** Montilon 2022 shows Leccino pit membranes resist CWDE degradation and vessels fill with callose; Giampetruzzi shows the wall DEGs; Sabella shows the lignin rise.
- **Closest analogue:** grapevine pit-membrane composition studies (Ingel 2019; Sun 2011, cited by Montilon).
- **Why it might fail:** wall-down signature is correlative; direct CWDE involvement was not proven in olive (Montilon states this).
- **Next lab step:** TEM pit-membrane comparison S105 vs Cellina under XfDD; qPCR the contigs above across the progeny.

### 4. Susceptibility-gene knock-out candidates — DMR6-like / JOX1 (olive-side)
- **Target:** DMR6-like `OE9A054976T1`/`OE9A079697T1`; JOX1 `OE9A092418T1`.
- **Why:** La Notte names them susceptibility genes; knock-outs confer resistance in grape/tomato/potato/banana.
- **Closest analogue:** de Toledo Thomazella 2021; Kieu 2021; Giacomelli 2022; Pirrello 2022 (cited by La Notte).
- **Why it might fail:** perennial woody editing, chimeras, SA/JA trade-off; S105 is HR without a DMR6 knock-out; EU NGT politics.
- **Next lab step:** qPCR both DMR6 IDs across the 61 progeny; test whether high DMR6 tracks noisy S215/S234-type resistance. Editing is the partner's decision. **Do not synthesize guides.**

### 5. Hydraulic phenotyping screen (olive-side)
- **Target:** cavitation vulnerability index + refilling markers OeTIP1.1, OeAMY, OeGBSSI (Sabella 2019).
- **Why:** cheap, non-destructive proxy that separates Leccino from Cellina; infected physiology looks like drought.
- **Closest analogue:** Surano 2022 (gs, Ψstem; on disk); Sabella 2019.
- **Why it might fail:** FS17 is hydraulically as good as Leccino but carries higher titer — hydraulics ≠ low load.
- **Next lab step:** porometer + laser-scanning cavitation index on seedlings; correlate to qPCR titer.

### 6. Phage — type IV pilus (PilA) target [DO NOT SYNTHESIZE]
- **Target:** ST53 type IV pilus, major subunit PilA.
- **Why:** the only experimentally demonstrated *X. fastidiosa* phage receptor — Ahern 2014 showed ΔpilA Temecula1 is resistant to Sano/Salvo/Prado/Paz, restored by complementation. Cara 2026 Phi3 is 96.7% identical to Salvo on an ST53 host.
- **Closest analogue:** Das 2015 four-phage grape cocktail; commercial XylPhi-PD (grape, not olive).
- **Why it might fail:** pilus-minus escape; xylem delivery; olive biofilm ≠ grape; EU quarantine release of a replicating virus.
- **Next lab step:** the partner (CIHEAM Bari / CNR) confirms the A0PT1 pilus receptor with escape mutants and runs a contained plantlet assay. **Do not synthesize. Do not isolate phage.**

### 7. Phage — MATE 2 on A0PT1 [DO NOT SYNTHESIZE]
- **Target:** unknown A0PT1 surface receptor (OMP or LPS class); secondary, its endolysin.
- **Why:** fastest published kill curve on *Xfp* (culture cleared 48 h, no regrowth 7 days), isolated in the same geography as ST53; no lysogeny/virulence/AMR genes (Sabri 2024, GenBank PP816325).
- **Closest analogue:** itself; isolation pipeline reused for Phi1/Phi3.
- **Why it might fail:** no field olive data; receptor unknown → resistance unpredicted; polyvalence risks non-target *Xanthomonas*.
- **Next lab step:** receptor ID by pull-down / escape mutants; contained olive-plantlet assay; cocktail with Phi1/Phi3. **Do not synthesize.**

### 8. AMP — 1036 / RIJK2 [DO NOT SYNTHESIZE]
- **Target:** *Xf* membrane + biofilm (dual activity).
- **Why:** Moll 2021 selected these after a six-strain Mediterranean panel; dual bactericidal–antibiofilm.
- **Closest analogue:** same group's BP178 (Baró 2020).
- **Why it might fail:** tested on strain IVIA 5387.2, not De Donno/A0PT1; no olive xylem PK; sap proteolysis; phytotoxicity at dose.
- **Next lab step:** MIC/biofilm on A0PT1 and De Donno; sap stability; then stop unless a containment partner exists. **Do not synthesize.**

### 9. AMP — Ascaphin-8 (GF19) / IL14 [DO NOT SYNTHESIZE]
- **Target:** biofilm (40–50% reduction at 50 µM; El Handi 2022).
- **Why:** independent peptide set, different chemotype from 1036/RIJK2, with an in planta claim.
- **Closest analogue:** El Handi 2022 (Biology 11:1685).
- **Why it might fail:** 50 µM is a lot of peptide for xylem; the in planta host is not a bearing olive; full methods not extracted (MDPI 404 on our fetch — flagged in SOURCES).
- **Next lab step:** obtain full PDF, repeat on ST53, drop if the plant system is herbaceous only. **Do not synthesize.**

### 10. Endophyte / BIOVEXO-class symptom tool (score, do not build)
- **Target:** host xylem community or BIOVEXO bacterial-strain / metabolite products — not a bacterial protein.
- **Why:** only intervention class with olive-field symptom data in Europe. CORDON should score it, not compete.
- **Closest analogue:** BIOVEXO six-candidate set; *Paraburkholderia phytofirmans* in grape (Baccari 2019).
- **Why it might fail:** BIOVEXO's own deliverable language says X-biopesticides do not reduce *Xylella* population size; EFSA 2016 still binds on clearance.
- **Next lab step:** score BIOVEXO trial blocks against CAMP qPCR if locations are released. We do not brew endophytes.

---

## Gaps and honesty

- **RESOLVED (were name-only in v0):** SOBIR1, WAK2, RPM1-like, RGA3, R1A-10 now carry real `OE9A*` IDs from La Notte Supplementary Table S4 (`Table4.xlsx`, sheet "Suppl.Table 4", now on disk). The 659 Leccino DEGs (`lc_xylem_*`) and 447 Ogliarola DEGs (`og_xylem_*`) are in Additional files 3 and 4 (`MOESM3`, `MOESM4`, on disk).
- **Direction caveat:** La Notte main text has an ambiguous "highest decreased fold change" clause near the R-gene list; the primary Table S4 records these as upregulated (positive log2FC). Table S4 is treated as authoritative. A partner should confirm sign before acting.
- **Annotation caveat:** At3g47580 (main text) vs At3g47570 (Table S4 Description) for the LRR-RLK — same cluster, ID as recorded.
- **GAP — De Donno locus tags:** PilA / XadA / MopB surface proteins remain family-level; the De Donno CDS table (GenBank) was not parsed. A partner can map PilA from Temecula1 `NP_780105.1` to the De Donno orthologue.
- **GAP — El Handi 2022 full methods:** MDPI HTML 404 on our fetch; peptide names from PubMed/PMC. Not frozen to disk.
- **GAP — Clavijo-Coppens 2021, Das 2015 primary PDFs:** not on disk; phage facts from Ahern 2014 (on disk) and secondary sources.
- **No peptide or phage sequences are reproduced here. Nothing was synthesized. No one was emailed.**
