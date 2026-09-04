# Resistance-and-target brief — challenge to CORDON locks

**Artifact:** CORDON Resistance Decoder challenge (not the finished decoder table)
**Date:** 15 August 2026
**Mode:** computational / literature only. **Do not synthesize** any peptide, phage stock, or editing reagent.
**Question:** Are Leccino / FS-17 the resistance ceiling, and do AMP / phage stay paper-only?

**Verdict.** No *named commercial cultivar* in the papers we hold beats Leccino or FS-17 on both titer and canopy. What *does* beat parental Leccino, inside La Notte 2024, are two unregistered Leccino × Cipressino seedlings: **S105** (field HR; quiet transcriptome; zero desiccation at 24 mpvi) and **S215** (zero desiccation *and* colonization that fails to progress). That kills “Leccino is a finished genotype ceiling.” It does not kill “Leccino is the best-documented parental source and the legal replant core.” Pavan 2021 already names **Frantoio** and **Nocellara Messinese** as partial resistance below Leccino. BeXyl greenhouse **Gordal** is press (Jan 2026), not a paper. AMP / phage are no longer concept-only: Sabri 2024 MATE 2 lyses *Xfp* A0PT1 *in vitro*; Sabri itself names commercial **XylPhi-PD** and Ahern / Das as the Pierce’s-disease analogue (grape, not olive). None of that is an olive-field product, and none of it authorizes CORDON to synthesize anything. The computational-only and do-not-synthesize locks survive as *team* rules. The claim that the literature itself is paper-only does not.

**Extraction honesty.** Local files only: Giampetruzzi 2016, La Notte 2024, Surano 2022, Pavan 2021, Sabri 2024 extract, CORDON.md, `data/decoder/v0-genes.md`, `queries/assumption-reopen-live.md`. **Giampetruzzi Additional file 3 is missing** (the full Leccino DEG matrix with olive contig IDs). La Notte Suppl. Tables S4–S11 are not on disk; SOBIR1 / R1A-10 / RGA3 / RPM1-like are *named* in the main text, their `OE9A*` IDs are not. Montilon 2022, Sabella 2019, Ahern 2014, Clavijo-Coppens 2021, Moll 2021, and a De Donno CDS table are **not** on disk. No gene name below is invented.

---

## 1. Ranked olive pathways / genes

Rank is “what a CNR postdoc should take to lab meeting,” not a p-value leaderboard. Two ID systems — do not mix them:

- **Giampetruzzi 2016** (*BMC Genomics*): de novo xylem transcriptome, no Farga genome. IDs are Arabidopsis orthologues plus contig names (`OG_xylem_*`, `LCxylem_*`). 39.58% of Leccino DEGs unassigned. Olive locus IDs live in **Additional file 3 — not extracted, not on disk**.
- **La Notte 2024** (*Front. Plant Sci.* 15:1457831): RNA-seq mapped to **cv. Farga genome v9**. IDs are `OE9A*`. Contrast is S105 (HR) vs S215 (R) vs S234 (R), not Leccino vs Ogliarola.

DEG counts that matter:

| Contrast | Filter | Count | Source |
|---|---|---|---|
| Leccino infected vs healthy | paper DE | **659** (586 down, 73 up) | Giampetruzzi 2016 |
| Ogliarola infected vs healthy | same | **447** | Giampetruzzi 2016 |
| Infected Leccino vs infected Ogliarola | same | **512** | Giampetruzzi 2016 |
| S234 Xf_DDpos vs Xf_neg | p < 0.001 / FDR < 0.05 | **17,227 / 13,080** | La Notte 2024 |
| S215 Xf_DDpos vs Xf_neg | same | **13,030 / 9,956** | La Notte 2024 |
| S105 Xf_DDpos vs Xf_neg | same | **4,513 / 2,897** | La Notte 2024 |

S105 is the quiet transcriptome. Decode that phenotype, not generic Leccino.

Parentage (La Notte): **S105** and **S215** = Leccino × Cipressino (HR and R); **S234** = Leccino × Ogliarola salentina (R). A fourth inoculated seedling, **S218**, is Leccino × Cellina di Nardò.

### Rank 1 — Receptor / PTI signaling (Leccino-up; S105-specific)

**Why first.** The only large class that is *up* in resistant Leccino, *down* in susceptible Ogliarola, and again present in the HR seedling S105. Giampetruzzi analogizes EFR / rice Xa21. La Notte notes RLK/RLP members sit in grapevine *PdR1b*.

**Giampetruzzi 2016, Leccino up (up to 4-fold); a selected LRR-RLK is RT-qPCR confirmed:**

| Class | Arabidopsis orthologue | Olive contig |
|---|---|---|
| LRR-RLK | `at5g49290`, `at1g74190`, `at1g74180`, `at3g23120`, `at5g27060` | full olive IDs in Additional file 3 — **missing** |
| LRR-RLP | `at1g07390`, `at1g74170`, `at3g53240` | same |
| LRR-RLK, inter-cultivar exclusive | *Sesamum indicum* hit | `OG_xylem_325091` |

Ogliarola does the opposite: LRR-RLK / LRR-RLP **down**. CRK8/10 (`at4g23180.1`) and CRK6 (`at4g23140.1`) move in *both* cultivars (RT-qPCR confirmed); they are not a resistance discriminator.

**La Notte 2024, S105-enriched (GO:0004674 / GO:0004672 / GO:0043531; Suppl. Table S4 not on disk):**

| Gene / class | Farga v9 ID | Where it lights up |
|---|---|---|
| LRR-RLK At3g47580 (LRR XII) | `OE9A013998T1`, `OE9A100116T1` | Highly expressed in S105; also present S215/S234 (Suppl. Fig. S6) |
| SOBIR1 (LRR-RLK, RLP co-receptor) | **OE9A not in main text** | Named among S105 GO:0004674 transcripts |
| WAK2-like | **OE9A not in main text** | Same GO set |
| Late blight homolog R1A-10 | **OE9A not in main text** | S105; highest fold among disease-resistance proteins |
| Disease resistance RGA3 | **OE9A not in main text** | S105 |
| RPM1-like | **OE9A not in main text** | S105 |
| WAK-like, DUF26, S-Domain1/2/3, RLCK-VII | BIN, not a single ID | More up in S215 and S234 than S105 |
| PBS1-like RLCK | BIN | More up in S215/S234 |

La Notte also names “probable LRR receptor-like serine threonine-kinase **At3g47570**” in the same GO paragraph as SOBIR1. That is a different AGI from the `At3g47580` pair above. Do not collapse them. Do not invent the missing OE9A IDs.

### Rank 2 — Cell-wall integrity, pectin, pit-membrane seam

**Why.** 82 cell-wall DEGs **down** 2- to 8-fold in infected Leccino (Giampetruzzi). Mercator: cell wall 11.39% of destabilized classes (then stress 7.78%, signaling 7.08%). The same axis (PMEI, expansin, PGIP) is *loud* in S215/S234 and *quiet* in S105. Montilon 2022 (PDF not on disk; cited by CORDON and La Notte) is the anatomical claim: Cellina pit membranes degrade, Leccino’s do not to the same degree. We have not re-read that PDF.

**Giampetruzzi 2016, Leccino down (Arabidopsis orthologues):**

| Function | IDs |
|---|---|
| FLA11 / FLA12 (cellulose deposition, adhesion) | `at5g03170`, `at5g60490` — RT-qPCR FLA confirmed |
| PME | `at5g53370` |
| PMEI | `at3g49220`, `at5g09760` |
| Pectin lyases | `at5g19730`, `at1g60590`, `at1g48100`, `at1g10640`, `at5g48900`, `at3g61490` |
| Polygalacturonase | `at1g70370` |
| Laccases (up to 7-fold down; LAC12, LAC17 RT-qPCR) | `at2g40370`, `at2g3021` (paper’s own truncation), `at2g38080`, `at5g01190`, `at5g60020` |
| Expansins (Ogliarola-up; same family) | `at4g17030`, `at4g30380`; contigs `OG_xylem_175154`, `OG_xylem_146321` (Expansin-like B1) |

A PME 3-like orthologue was **down only in infected Ogliarola** (Additional files 8b / 9) and was RT-qPCR validated. Susceptibility-side pectin gene, not a Leccino marker.

**La Notte 2024, S215 / S234 up (cell wall / secondary metabolism BIN):**

| Gene | Farga v9 ID |
|---|---|
| PMEI family | `OE9A103328`, `OE9A018498` |
| Expansin A-1 | `OE9A055620` |
| Expansin-like B1 | `OE9A100033` |
| Polygalacturonase inhibitor-like | `OE9A070676T1`, `OE9A036088T1` (highest “pathogen” fold in S234/S215) |

**La Notte PC1 top-loading, down in Xf_DDpos** (the drought/collapse axis S105 mostly avoids): expansin-like B1 `OE9A106136T1`, `OE9A061049T1`, `OE9A016298T1`.

Giampetruzzi 2016 also notes the CoDiRO polygalacturonase has a **premature stop codon**, offered as a reason for slow movement / low titer. We do not have the De Donno locus tag. Do not invent one.

### Rank 3 — Hormone / susceptibility genes (DMR6, JOX1)

**Why.** La Notte names these as susceptibility genes with published knock-outs in grape, tomato, potato, banana. They are **up in S215/S234**, not the S105 signature. This is the biotech door *they* wrote down.

| Gene | Farga v9 ID | Note |
|---|---|---|
| DMR6-like (SA hydroxylase) | `OE9A054976T1`, `OE9A079697T1` | Similar to VvDMR6.2 / VvDMR6.1 |
| 2-OG-dependent dioxygenase / JOX1 (At3g11180; JA hydroxylase) | `OE9A092418T1,2,3` | PC1 bottom-loading, up in Xf_DDpos S215/S234 |
| GA 2-beta-dioxygenase 1-like | `OE9A116007T1,2,3` | PC1 bottom-loading |
| ACBP60 / SARD1-like | `OE9A093289T1`, `OE9A068952` | Up with PGIP in S234/S215 “pathogen” BIN |
| ABI5 | `OE9A075379T1,2,3,4` | PC1 top-loading **down** in Xf_DDpos |

### Rank 4 — Hydraulics / drought-like physiology

**Why.** Infected physiology looks like drought. Resistant trees manage that drought. Surano 2022 is the numbers. Sabella 2019 (PDF not on disk): Leccino constitutively less prone to cavitation, faster refill.

**Surano 2022** (vector-inoculated; Cq means Cellina 20.24, Leccino 22.04, FS17 20.56; Cq not statistically different among infected plants):

- Stomatal conductance *gs*: Cellina infected always << healthy. Leccino infected differs only at the first two dates. **FS17 infected never differs from healthy.**
- Δ*gs* (healthy − infected): Cellina 0.06–0.20 mol m⁻² s⁻¹; Leccino 0.012–0.066; FS17 −0.001–0.050. Leccino and FS17 not different from each other; both different from Cellina.
- Stem water potential: infected Cellina more negative than Leccino and FS17. Infected Leccino still drops vs its own healthy plants. **Infected FS17 does not.** ΔΨstem near 0 in FS17.

FS17 is hydraulically *at least as good as* Leccino in this trial, with a point estimate of higher bacterial load (lower Cq). Split phenotype, not a commercial beat. *gs* and Ψstem are a **phenotyping tool**, not just a mechanism.

**Giampetruzzi Ogliarola-up drought transcripts (RT-qPCR: ELIP, FAR, ABA2):**

| Gene | Contig |
|---|---|
| ELIP | `LCxylem_81506`, `OG_xylem_197731` |
| Dehydrin | `OG_xylem_111461` |
| LEA | `OG_xylem_45532` |
| FAR-RED impaired response 1 | `at4g15090` |
| ABA2 | RT-qPCR set; contig in Additional file 8/9 |

**La Notte PC1 down in Xf_DDpos (photosynthetic / sugar collapse S215/S234):**

| Gene | Farga v9 ID |
|---|---|
| Rubisco activase | `OE9A079773T1,2` |
| Beta-amylase 3 chloroplastic | `OE9A045257T1`, `OE9A107186T1` |
| Galactinol synthase | `OE9A047763T1,2` |
| PSII chlorophyll a–b binding (FC < −5) | `OE9A075888T1`, `OE9A096707T1` |
| Sugar transport protein 13 (up) | `OE9A030382T1`, `OE9A049120T1` |
| Beta-glucosidase-like (up) | `OE9A093988T1`, `OE9A054617T1`, `OE9A117672T1`, `OE9A051211T1` |

S105 stress DEGs: abiotic 39 / biotic 33. S215: 113 / 98. S234: 144 / 105. All “pathogen” DEGs up in S234 and S215.

### Rank 5 — Tylose / ethylene TFs (S215/S234, not S105)

La Notte: ERF071-like is the grapevine tylose TF (Zaini 2018; Ingel 2021). Loud in the *resistant-but-perturbed* seedlings, quiet in S105.

| TF | Farga v9 ID | Pattern |
|---|---|---|
| ERF071-like | `OE9A032259T1,2` | PC1 bottom-loading; up S215/S234 |
| ABR1-like | `OE9A066785T2` | Up S215/S234 |
| ERF096-like | `OE9A102306` | GO TF set S215/S234 |
| WRKY30 | `OE9A105450T1`, `OE9A042006T1` | FC > +5 S215/S234 |
| WRKY53 / WRKY40 | `OE9A042006`, `OE9A054922` | S215/S234 GO |
| NAC domain 2-like | `OE9A057226T1`, `OE9A102768T1` | FC > +5 S215/S234 |
| Cationic peroxidase 1-like (PR-9) | `OE9A024386` | Enriched S234 |

S105 downregulated histone H2B / nucleosome (GO:0000786) — La Notte reads this as SA-linked epigenetic control. No single histone OE9A in the main text.

### Rank 6 — Breeding-side SSR, not a gene

La Notte: SSRs do **not** predict Xfp phenotype well. Two exceptions with positive fixation index **only in susceptible genotypes**: **GAPU103a** and **UDO99-043**. POP analysis: Leccino + Ogliarola + Frantoio + Pendolino share a cluster that holds many HR/R/T spontaneous trees; another cluster holds FS17 + Cellina + Nociara.

### What we will not rank

- Any olive contig from Additional file 3 (file missing).
- Any OE9A ID that does not appear in the extracted La Notte main text.
- Olive AOX, endophyte taxa, CRISPR olives.

---

## 2. Does any 2021–2026 genotype beat Leccino / FS-17?

**Named commercial cultivar, in papers we hold: no.**

| Source | What was screened | Versus Leccino / FS-17 |
|---|---|---|
| Pavan et al. 2021 *Front. Plant Sci.* 12:723879 (PDF on disk) | Grower PRPs in Lecce; 23 PRPs in SSR cluster **K1** with Leccino and FS-17; field test of Frantoio, Nocellara Messinese, Pendolino, Bella di Spagna vs Ogliarola, Cellina, Leccino (Wilcoxon) | **Leccino still lowest symptoms and lowest colonization.** **Partial resistance in Frantoio and Nocellara Messinese** vs susceptible controls. Not a beat. Official reconversion at the time: only Leccino and FS-17. Intermediate resistance also cited from prior screens (Frantoio, Toscanina, Termite di Bitetto, Maiatica, Dolce di Cassano, Oliastro, Nociara, Nocellara Etnea). |
| La Notte / Saponari / Giampetruzzi / Saldarelli 2024 (PDF on disk) | 171 symptom-poor spontaneous genotypes; 139 unique SSR; 61 Leccino progeny field-scored; four open-pollinated seedlings inoculated (S105, S215, S218, S234) vs Leccino and Cellina | Field: **67% of Leccino offspring HR/R/T** vs Cellina 32% and Ogliarola 49%. Inoculation at 24 mpvi: **S105 and S215 (Leccino × Cipressino) showed no desiccation**; Leccino, S218, S234 showed mild shoot dieback; Cellina collapsed. **S215**: only 2 replicates qPCR-positive at 24 mpvi. **S105 had the highest bacterial population of the four seedlings** and was the exception vs Cellina at 16 mpvi. |
| Surano 2022 (PDF on disk) | Leccino vs FS17 vs Cellina, hydraulics | FS17 matches or beats Leccino on *gs* and ΔΨstem; Leccino has the better (higher) Cq. Split, not a commercial beat. |
| BeXyl greenhouse, Olive Oil Times 5 Jan 2026 | Leccino, Frantoio, **Gordal** vs Arbequina / Arbosana under *pauca* | **PRESS, not a paper.** Those three grouped as lower load/symptoms than the SHD Spanish pair. That is “with Leccino,” not “beats Leccino.” Gordal remains a greenhouse claim until the BeXyl paper. |

**The real challenge to the ceiling is not Frantoio.** Pavan is partial resistance *below* Leccino. The challenge is:

1. **S105** — Leccino × Cipressino, field HR, fewest DEGs (2,897 vs 9,956 / 13,080), zero desiccation, **but not lower titer than Leccino**. Quiet host, not a sterilizer.
2. **S215** — same cross; paper: part of a grafted tree (rootstock), carries olive leaf yellowing associated virus and olive latent virus 1 (S105 and S234 are virus-clean / seed-origin). Zero desiccation **and** colonization that fails to progress (2 positives at 24 mpvi). Closest thing in the corpus to “better than Leccino” on both axes — with a virus / graft confound.
3. **Cipressino as the other parent** — Saponari personal communication in La Notte: “not as susceptible as Cellina / Ogliarola.” Crosses to the two local susceptibles (S218 = Leccino × Cellina; S234 = Leccino × Ogliarola) only matched parental Leccino.
4. CORDON’s legal replant set already names Lecciana and Leccio del Corno beside Leccino / FS-17. Authorization ≠ superiority. No head-to-head titer paper on disk that puts them above Leccino.

S105 / S215 are **not released cultivars**. Treating them as a replant option is a category error. Treating Leccino as the last word on olive genetics is also a category error. `entities/leccino.md` (“No screened cultivar has beaten Leccino / FS-17”) is true for *cultivars* and false if “cultivar” is allowed to mean “genotype.”

---

## 3. ST53 / Xfp surface and xylem-exposed proteins (phage / AMP targets)

No ST53 proteome PDF and no De Donno CDS table are on disk. The olive-infecting reference genome is *X. fastidiosa* subsp. *pauca* strain **De Donno** (ST53 / CoDiRO; Giampetruzzi et al. 2017 *Genome Announc.*, cited). The phage host we actually hold a paper for is **A0PT1** (*Xfp*, olive, Italy — Sabri 2024). Sabri does **not** print “ST53” in the extract we have. Do not invent A0PT1 = ST53 without an MLST table. Treat A0PT1 as the local olive *pauca* isolate used for phage work; treat De Donno as the published ST53 reference.

Xylem-exposed / surface families with a published phage or AMP analogue. Family-level only — **no `B9J09_*` or other De Donno locus tags invented**:

| Target class | Why it is xylem-exposed | Published analogue (what we actually hold) | Caveat |
|---|---|---|---|
| **Type IV pili** (PilA / PilY1 / PilQ / twitching) | Surface nanofilaments; motility, aggregation, biofilm, vector acquisition | Sabri 2024 cites **Ahern et al. 2014** and **Das et al. 2015** (four-phage PD cocktail) and names commercial **XylPhi-PD** as a PD bactericide. Sabri’s genome comparison table includes *Xylella* phage **Sano** and **Salvo**. Ahern PDF is **not** on disk; receptor sentence (T4P-dependent) is therefore secondary. **XylPhi-PD is grape / subsp. *fastidiosa*, not olive.** | Receptor demonstrated on *Xf* in the Ahern lineage, not mapped on De Donno / A0PT1 in papers we hold. Pilus-minus escape is the classic path. |
| **LPS / outer membrane** | Gram-negative OM; first surface a tailed phage hits if not pilus | Sabri 2024: MATE 2 is polyvalent on *Xanthomonadaceae*; paper states polyvalent phages typically use **OMP or LPS** via the same tail fiber. Receptor of MATE 2 is **not experimentally identified**. | “OMP or LPS” is a literature class, not a measured A0PT1 receptor. |
| **Peptidoglycan (endolysin substrate)** | Exposed after OM disruption, or via phage lysis cassette | MATE 2 encodes an **endolysin** (Sabri Fig. 2). | Gram-negative OM blocks naked endolysin unless delivered. Paper-only. **Do not synthesize.** |
| **EPS / biofilm matrix** | Occludes vessels; the clinical object | No AMP assay PDF on disk. CORDON.md parks AMP generators in phase-2 paper-candidates. | Do not invent peptide names. |
| **pglA polygalacturonase** | Secreted CWDE; pit-membrane punch | Not a phage receptor. Host-side counter is PGIP (`OE9A070676T1`, `OE9A036088T1`). CoDiRO allele is truncated (Giampetruzzi 2016). | Truncation may already limit ST53 movement. Not an AMP plan. |
| **XadA / FimA / MopB** | Afimbrial adhesins, type I fimbriae, major OMP — standard *Xf* surface families | No phage whose receptor *is* XadA in files we hold. | Family-level only. Do not invent locus tags. Do not claim they are MATE 2 receptors. |

**Phage objects that actually exist against *Xfp* / *Xf* (from files we hold):**

| Phage | Year | Host in the paper we hold | Form | Field? |
|---|---|---|---|---|
| **MATE 2** | Sabri et al. 2024 *Front. Microbiol.* 15:1412650 | *Xfp* A0PT1 (olive, Italy); also *X. albilineans*, *X. campestris*. No lysis of *Paenibacillus rigui*, *B. subtilis*, *B. pumilus*, *Pantoea agglomerans*. | Sewage, Bari. 63,695 nt, 95 ORFs, G+C 52.1%, tentative *Carpasinavirus*, no lysogeny / virulence / AR / toxin genes. Adsorption 10 min. 77% lysis at 24 h; culture cleared 48 h; no regrowth 7 days. Capsid 60±5 nm, contractile tail 120±7.5 nm. GenBank **PP816325**. Corresponding: Elbeaino, CIHEAM Bari. | **In vitro only.** Authors: efficacy on *Xf*-infected olive trees in the field “has yet to be determined.” |
| Sano, Salvo (and the Das 2015 four-phage set) | Ahern 2014 / Das 2015 | Named by Sabri; PDFs **not** on disk | Isolated, characterized (secondary) | Das 2015 grape cocktail; **XylPhi-PD** commercial (US grape). Not olive. |
| Clavijo-Coppens 2021 Mediterranean set | CORDON.md names it | PDF **not** on disk | Isolated, sequenced (secondary) | No olive field product. |

**AMP.** No AMP assay PDF is on disk (Moll 2021, El Handi 2022, etc. were not extracted here). CORDON.md already forbids de novo AMPGAN sequences and forbids synthesis. AMP stays a **paper class** in this brief, not a named peptide list.

---

## 4. At most ten candidate interventions

Every row is a **paper hypothesis**. Flag on every row: **do not synthesize.** CORDON does not make peptides, phage lysates, or guide RNAs. A named containment lab does, after they ask.

### 1. Breeding marker — S105 receptor cassette
- **Target:** LRR-RLK At3g47580 `OE9A013998T1` / `OE9A100116T1`, plus the unnamed SOBIR1 / R1A-10 / RGA3 / RPM1-like set in La Notte Suppl. Table S4.
- **Why:** Only S105-enriched immune set that is also the Leccino-up class from 2016. Quiet host, HR canopy.
- **Closest analogue:** Grapevine *PdR1b* RLK/RLP cluster (cited by La Notte). Not a single olive locus.
- **Why it might fail:** Polygenic. SSR already failed as a phenotype predictor. S105 titer is *not* low. Marker could select pretty canopies that still feed vectors. Suppl. S4 IDs are not in hand.
- **Next lab step:** Pull Suppl. Table S4; design KASP/ampliseq on the 61 Leccino progeny; score vs existing field HR/R/T. No new inoculation required for v0.

### 2. Breeding marker — S215 colonization control
- **Target:** The S215 “infection does not progress” phenotype (2 positives at 24 mpvi), not a single gene.
- **Why:** Closest genotype in the corpus to beating Leccino on **both** symptoms and titer trajectory.
- **Closest analogue:** Same La Notte inoculation panel. Cipressino as donor.
- **Why it might fail:** S215 is a grafted rootstock piece, virus-positive (OLYaV, OLV-1). Phenotype may be scion/rootstock or virus confound. Not seed-clean like S105/S234.
- **Next lab step:** Re-inoculate virus-indexed S215 ramets. If the colonization block holds, map it. If it vanishes, discard.

### 3. Susceptibility-gene screen — DMR6-like / JOX1
- **Target:** `OE9A054976T1`, `OE9A079697T1` (DMR6-like); `OE9A092418T1,2,3` (JOX1 / At3g11180).
- **Why:** La Notte explicitly calls them susceptibility genes; knock-outs work in grape, tomato, potato, banana.
- **Closest analogue:** The DMR6/JOX1 editing papers La Notte cites. S105 does **not** need DMR6 knocked out to be HR.
- **Why it might fail:** Perennial woody editing; chimeras; SA/JA trade-off. EU GMO/NGT politics.
- **Next lab step:** qPCR the two DMR6 IDs across the 61 progeny. Test whether high DMR6 tracks S215/S234-like noisy resistance. Editing is their decision. **Do not synthesize guides.**

### 4. Negative marker — GAPU103a / UDO99-043
- **Target:** The two SSRs fixed in susceptible genotypes (La Notte).
- **Why:** Cheap discard rule for a seedling pile. Not a resistance gene.
- **Closest analogue:** The same paper’s POP analysis.
- **Why it might fail:** Authors already say SSRs are underpowered. Fixation in susceptibles ≠ causative. Will throw away useful recombinants.
- **Next lab step:** Score the existing 139 unique profiles; report PPV/NPV against field HR/R/T. Keep only if NPV for “susceptible” is high.

### 5. Seedling ranking rule, not a molecule
- **Target:** Prioritize Leccino × Cipressino over Leccino × Cellina / Leccino × Ogliarola for the next inoculation queue.
- **Why:** La Notte’s own split: Cipressino crosses symptomless; local-susceptible crosses = parental Leccino. 67% R/T rate in Leccino offspring.
- **Closest analogue:** Livestock genomic-selection analogy in CORDON.md §3.
- **Why it might fail:** n = 4 inoculated genotypes. Cipressino “not as susceptible” is a personal communication. Oil chemistry / vigor of Cipressino hybrids unknown.
- **Next lab step:** Ask CNR for the unpublished inoculation panel and score this ranking against it. That is the Artifact B ask in CORDON.md.

### 6. Hydraulics screen — *gs* / Ψstem
- **Target:** Not a gene. The Surano 2022 discriminant (Cellina vs Leccino/FS-17).
- **Why:** Cheap, non-destructive, already shown to separate the legal pair from Cellina. Complements qPCR (FS17 can look hydraulically fine with a worse Cq).
- **Closest analogue:** Surano porometer + pressure-chamber protocol (LI-600; Scholander).
- **Why it might fail:** Drought, load, and age confound. One-date *gs* is not a genotype. S105 was not in this trial.
- **Next lab step:** Put a porometer on the next seedling panel next to qPCR. Score S105/S215 against Leccino, not just Cellina.

### 7. Phage — type IV pilus class (Ahern / Das / XylPhi-PD)
- **Target:** *Xf* T4P (PilA/PilY1 surface). Family-level; no De Donno tag in hand.
- **Why:** Only *Xf* phage receptor class with a published experimental weight (Ahern 2014, cited by Sabri). XylPhi-PD proves the class can leave the fridge — in grape.
- **Closest analogue:** XylPhi-PD / Das 2015 four-phage PD cocktail. AgriPhage™ is the *Xanthomonas* commercial cousin, not *Xf*.
- **Why it might fail:** Pilus-minus escape; xylem delivery; olive biofilm ≠ grape; EU quarantine release of a replicating virus; Ahern PDF not re-read here.
- **Next lab step:** **They** (CIHEAM Bari / CNR, already on MATE 2) do A0PT1 pilus-mutant receptor work and a contained plant assay. We do not. **Do not synthesize.**

### 8. Phage — MATE 2 on A0PT1
- **Target:** Unknown A0PT1 surface receptor (OMP or LPS class). Secondary: MATE 2 endolysin.
- **Why:** Fastest published kill curve on *Xfp* we hold (clear at 48 h, no regrowth 7 days). Isolated in the same geography as the epidemic. Polyvalent on *Xanthomonadaceae*, quiet on the beneficials they tested. No lysogeny/toxin genes.
- **Closest analogue:** Itself (Sabri 2024). Isolation pipeline is already at CIHEAM Bari.
- **Why it might fail:** No field olive data (authors say so). Receptor unknown → resistance unpredicted. Xylem persistence unknown. Polyvalence cuts both ways.
- **Next lab step:** Receptor ID (pull-down / escape mutants). Contained olive plantlet assay. **Do not synthesize. Do not isolate phage in this apartment.**

### 9. AMP class — paper-only, no named peptide from files we hold
- **Target:** *Xf* membrane / biofilm, if and only if a named containment lab wants an AMP lane.
- **Why:** CORDON.md already reserved AMP generators as phase-2 paper candidates. We hold **no AMP assay PDF**. Inventing 1036 / RIJK2 / Ascaphin sequences here would violate the “do not invent” rule.
- **Closest analogue:** Whatever a partner already has under BSL/quarantine (not us).
- **Why it might fail:** No ST53 / A0PT1 AMP data on disk. Sap proteolysis. Phytotoxicity. Xylem PK. EFSA 2016 still binds on clearance.
- **Next lab step:** If a partner asks, they test *published* peptides on A0PT1 / De Donno. We do not design sequences. **Do not synthesize.**

### 10. Endophyte / symptom-tool scoring, not a seventh biopesticide
- **Target:** Not a bacterial protein. Host xylem community (CORDON: Leccino microbiota more stable under OQDS) or BIOVEXO-class symptom products.
- **Why:** Only intervention class with olive-field symptom data in Europe. CORDON must not compete with BIOVEXO; we can score it against CAMP PCR if locations exist.
- **Closest analogue:** BIOVEXO six-candidate set; Dentamet endotherapy (Girelli 2022, cited in `assumption-reopen-live.md`). EFSA 2016: not a cure.
- **Why it might fail:** Symptom ≠ titer. Vector acquisition tracks load. Product-not-yet as of 2025 press.
- **Next lab step:** Computationally join any released trial blocks to CAMP. We do not brew endophytes.

**Not in the ten, on purpose.** RNAi against ERF071 (`OE9A032259`) — tylose is a double-edged host response; silencing it could worsen hydraulics. De novo AMPGAN peptides — CORDON.md already forbids generating sequences to synthesize. CRISPR olives — locked out in CORDON.md §4.2.

---

## 5. Which CORDON locks survive

| Lock | Status after this brief | Why |
|---|---|---|
| **Computational-only (we do not touch a live bacterium)** | **Survives.** Safety lock, not an evidence lock. Quarantine pest. MATE 2 being a real wet-lab object does not put it in this apartment. | CORDON.md §4.4, §7. `assumption-reopen-live.md` already said this. |
| **Do-not-synthesize (AMP / phage / peptides)** | **Survives as a team rule.** The *literature* is past paper-only (see below). We still do not make the molecules. | Same. Every row in §4 is flagged. |
| **AMP / phage stay paper-only** *(as a claim about the world)* | **Does not survive for phage. Survives for AMP in the files we hold.** | XylPhi-PD is a commercial grape product (Sabri 2024 names it). Ahern 2014 + Das 2015 left the page a decade ago. MATE 2 (2024) lyses *Xfp* A0PT1 in a Bari-adjacent lab. What *is* still paper-only: an olive-grove phage product, any AMP assay we can cite from disk, and any CORDON-origin sequence. |
| **Leccino / FS-17 are the ceiling** | **Survives for named commercial cultivars. Dies for genotypes.** | No paper we hold puts a released cultivar above Leccino on titer *and* symptoms. S105/S215 beat parental Leccino on canopy; S215 also on colonization trajectory. Frantoio is partial, below Leccino (Pavan 2021). Gordal is a greenhouse cluster-with-Leccino **press** claim, not a beat. `entities/leccino.md` should say “no *cultivar*,” not “no genotype.” |
| **Do not email Bari until Artifact A or B exists** | **Survives.** | This file is a challenge brief, not the decoder table a postdoc can take to lab meeting without us. Send after Additional file 3 + Suppl. S4 IDs land in `data/decoder/`. |
| **Do not compete with BIOVEXO / Planetek / Zarco-Tejada** | **Survives.** | Their field objects are detection or symptom tools. Our decoder should mark seedlings and score their blocks, not invent a seventh biopesticide. |

---

## 6. Nulls, gaps, what we did not do

- **Did not invent gene names.** Every `OE9A*` and every Arabidopsis ID above is in the extracted main text of Giampetruzzi 2016 or La Notte 2024. SOBIR1 / RGA3 / RPM1 / R1A-10 / WAK2-like are *named* in La Notte and ID-less here because they live in Suppl. Table S4, which is **not on disk**.
- **Additional file 3 of Giampetruzzi is missing.** That is the full Leccino DEG matrix with olive contig IDs. A real decoder v0 should parse it. Until then, most of the 659 / 447 DEGs have no olive locus tag in this brief.
- **Did not re-download Montilon 2022 or Sabella 2019.** Pit-membrane and cavitation claims are cited, not re-read.
- **Did not obtain the De Donno CDS table.** Surface proteins are families, not locus tags. A partner with the De Donno accession can map PilA / XadA / MopB in an afternoon.
- **Did not claim A0PT1 = ST53.** Sabri extract does not print the MLST type.
- **Did not claim Frantoio or Gordal beat Leccino.** Pavan 2021 is explicit that Leccino remains lowest. BeXyl / Olive Oil Times Jan 2026 groups Frantoio and Gordal *with* Leccino against Arbequina/Arbosana — **press, not paper**.
- **Did not treat S105 as a cultivar.** It is a seedling. Its titer is the *highest* of the four inoculated Leccino offspring.
- **Did not treat S215’s colonization block as clean.** Virus-positive rootstock origin.
- **Did not extract Ahern, Clavijo-Coppens, or any AMP PDF.** Phage names Sano/Salvo and XylPhi-PD are from Sabri’s own text and references. Receptor mechanism for Ahern is secondary.
- **No peptide sequences are reproduced here.** No AMP names are listed as if we hold the assays.
- **No one was emailed. Nothing was synthesized.**

**What would falsify this brief.** (1) A 2021–2026 paper with a named cultivar, qPCR, and symptom scores that beat Leccino on both. (2) Suppl. Table S4 IDs that show the S105 “receptor” story is a GO dump, not a coherent cassette. (3) An A0PT1 / De Donno plant assay where MATE 2 fails to move titer. (4) Additional file 3 showing the Leccino LRR-RLK up-list is a single noisy contig. (5) A BeXyl paper that actually puts Gordal above Leccino — the press piece does not.

**Handoff.** This file is `queries/`, not `data/decoder/`. The decoder v0 table still needs: parsed Additional file 3, La Notte Suppl. S4 IDs, and De Donno locus tags. Until those three exist, do not send Bari.
