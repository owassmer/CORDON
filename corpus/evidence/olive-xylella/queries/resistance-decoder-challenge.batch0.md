# Resistance-and-target brief — challenge to CORDON locks

**Artifact:** CORDON Resistance Decoder challenge (not the finished decoder table)
**Date:** 15 August 2026
**Mode:** computational / literature only. **Do not synthesize** any peptide, phage stock, or editing reagent.
**Question:** Are Leccino / FS-17 the resistance ceiling, and do AMP / phage stay paper-only?

**Verdict in one paragraph.** No *named commercial cultivar* published in 2024–2026 beats Leccino or FS-17 on both titer and canopy dieback. What *does* beat parental Leccino, inside papers we hold, are two unregistered Leccino × Cipressino seedlings (S105, S215): zero desiccation at 24 months post vector inoculation while Leccino showed mild shoot dieback (La Notte et al. 2024). That kills “Leccino is a finished ceiling.” It does not kill “Leccino is the best documented parental source and the legal replant core.” AMP / phage are no longer concept-only: Ahern 2014 + Das 2015 + commercial XylPhi-PD exist for Pierce’s disease; MATE 2 (2024) and Phi1 / Phi3 (2026) lyse *Xfp* ST53 *in vitro*. None of that is an olive-field product, and none of it authorizes CORDON to synthesize anything. The computational-only and do-not-synthesize locks survive as *team* constraints. The claim that the literature itself is paper-only does not.

**Extraction honesty.** Local PDFs read with pymupdf 1.26.5: Giampetruzzi 2016, La Notte 2024, Surano 2022, Pavan 2021, Sabri 2024. Giampetruzzi Additional file 3 (the full DEG matrix) was **not** parsed; olive contig IDs for most of the 659 / 447 DEGs live there. La Notte Supplementary Tables S4–S11 hold OE9A IDs for SOBIR1, R1A-10, RGA3, RPM1-like; those names are in the main text, the locus IDs are not. Montilon 2022, Sabella 2019, Ahern 2014, Clavijo-Coppens 2021, and a dedicated ST53 proteome paper are **not** on disk. De Donno / ST53 surface proteins below are family-level from published Xf literature, not invented locus tags.

---

## 1. Ranked olive pathways / genes

Rank is “how much a CNR postdoc should care for a seedling screen or a marker panel,” not a p-value leaderboard. Two ID systems, do not mix them:

- Giampetruzzi 2016: de novo xylem transcriptome, **no Farga genome**. IDs are Arabidopsis orthologues plus contig names (`OG_xylem_*`, `LCxylem_*`). 39.58% of Leccino DEGs unassigned.
- La Notte 2024: RNA-seq mapped to **cv. Farga genome v9**. IDs are `OE9A*`. Contrast is S105 (HR) vs S215 (R) vs S234 (R), not Leccino vs Ogliarola.

DEG counts that matter:

| Contrast | Filter | Count | Source |
|---|---|---|---|
| Leccino infected vs healthy | DESeq2 ∩ SeqMonk | 659 total (586 down, 73 up) | Giampetruzzi 2016 |
| Ogliarola infected vs healthy | same | 447 | Giampetruzzi 2016 |
| Infected Leccino vs infected Ogliarola | same | 512 | Giampetruzzi 2016 |
| S234 Xf_DDpos vs Xf_neg | FDR < 0.05 | 13,080 | La Notte 2024 |
| S215 Xf_DDpos vs Xf_neg | FDR < 0.05 | 9,956 | La Notte 2024 |
| S105 Xf_DDpos vs Xf_neg | FDR < 0.05 | 2,897 | La Notte 2024 |

S105 is the quiet transcriptome. That is the phenotype to decode, not a slogan.

### Rank 1 — Receptor / PTI signaling (Leccino-up; S105-specific)

**Why first.** The only pathway that is *up* in resistant Leccino, *down* in susceptible Ogliarola, and *again* up in the HR seedling S105. Paper analogizes EFR and rice Xa21 (Giampetruzzi 2016). La Notte notes RLK/RLP members sit in grapevine *PdR1b*.

**Giampetruzzi 2016, Leccino up (up to 4-fold), RT-qPCR confirmed for a selected LRR-RLK:**

| Class | Arabidopsis orthologue | Olive contig if named |
|---|---|---|
| LRR-RLK | `at5g49290`, `at1g74190`, `at1g74180`, `at3g23120`, `at5g27060` | full olive IDs in Additional file 3, not extracted |
| LRR-RLP | `at1g07390`, `at1g74170`, `at3g53240` | same |
| LRR-RLK, inter-cultivar exclusive | — | `OG_xylem_325091` (*Sesamum indicum* hit) |

Ogliarola does the opposite: LRR-RLK / LRR-RLP **down**. CRK8/10 (`at4g23180.1`) and CRK6 are differentially expressed in *both* cultivars (RT-qPCR confirmed); they are not a resistance discriminator.

**La Notte 2024, S105-enriched (GO:0004674 / GO:0004672 / GO:0043531):**

| Gene / class | Farga v9 ID | Where it lights up |
|---|---|---|
| LRR-RLK At3g47580 (LRR XII) | `OE9A013998T1`, `OE9A100116T1` | Highly expressed in S105; also present S215/S234 (Suppl. Fig. S6) |
| SOBIR1 (LRR-RLK, RLP co-receptor) | **OE9A not in main text** (Suppl. Table S4) | Upregulated in S105 |
| WAK2-like | Suppl. Table S4 | S105 GO set |
| Late blight homolog R1A-10 | Suppl. Table S4 | S105, highest fold among disease-resistance proteins |
| Disease resistance RGA3 | Suppl. Table S4 | S105 |
| RPM1-like | Suppl. Table S4 | S105 |
| WAK-like, DUF26, S-Domain1/2/3, RLCK-VII | BIN, not a single ID | More up in S215 and S234 than S105 |
| PBS1-like RLCK | BIN | More up in S215/S234 |

**Null.** We do not have the SOBIR1 / RGA3 / RPM1 OE9A IDs. Do not invent them. Next lab step is to pull Suppl. Table S4, not to guess.

### Rank 2 — Cell-wall integrity, pectin, pit-membrane seam

**Why.** 82 cell-wall DEGs **down** 2- to 8-fold in infected Leccino (Giampetruzzi). Mercator: cell wall 11.39% of destabilized classes. The same axis (PMEI, expansin, PGIP) separates S215/S234 (loud remodeling) from S105 (quiet). Montilon 2022 (PDF not on disk; cited by CORDON and by La Notte) is the anatomical claim: Cellina pit membranes degrade, Leccino’s do not to the same degree. We have not re-read that PDF.

**Giampetruzzi 2016, Leccino down (Arabidopsis orthologues):**

| Function | IDs |
|---|---|
| FLA11 / FLA12 (cellulose deposition, adhesion) | `at5g03170`, `at5g60490` — RT-qPCR FLA confirmed |
| PME | `at5g53370` |
| PMEI | `at3g49220`, `at5g09760` |
| Pectin lyases | `at5g19730`, `at1g60590`, `at1g48100`, `at1g10640`, `at5g48900`, `at3g61490` |
| Polygalacturonase | `at1g70370` |
| Laccases (up to 7-fold down; LAC12, LAC17 RT-qPCR) | `at2g40370`, `at2g3021`, `at2g38080`, `at5g01190`, `at5g60020` |

A PME 3-like orthologue was **down only in infected Ogliarola** (Additional file 8b / 9) and was RT-qPCR validated. That is a susceptibility-side pectin gene, not a Leccino marker.

**La Notte 2024, S215 / S234 up (cell wall / secondary metabolism BIN):**

| Gene | Farga v9 ID |
|---|---|
| PMEI family | `OE9A103328`, `OE9A018498` |
| Expansin A-1 | `OE9A055620` |
| Expansin-like B1 | `OE9A100033` |
| Polygalacturonase inhibitor-like | `OE9A070676T1`, `OE9A036088T1` (highest “pathogen” fold in S234/S215) |

**La Notte PC1 top-loading, down in Xf_DDpos (the drought/collapse axis S105 mostly avoids):**

| Gene | Farga v9 ID |
|---|---|
| Expansin-like B1 | `OE9A106136T1`, `OE9A061049T1`, `OE9A016298T1` |

**Giampetruzzi Ogliarola-up expansins (same family, different ID system):** `OG_xylem_175154`, `OG_xylem_146321` (Expansin-like B1). RT-qPCR EXP confirmed up in Ogliarola.

### Rank 3 — Hormone / susceptibility genes (DMR6, JOX1)

**Why.** La Notte names these as “susceptibility genes” with published knock-outs in grape, tomato, potato, banana. They are **up in S215/S234**, not the S105 signature. This is the biotech door they wrote down, not one we invented.

| Gene | Farga v9 ID | Note |
|---|---|---|
| DMR6-like (SA hydroxylase) | `OE9A054976T1`, `OE9A079697T1` | Similar to VvDMR6.2 / VvDMR6.1 |
| 2-OG-dependent dioxygenase / JOX1 (At3g11180; JA hydroxylase) | `OE9A092418T1,2,3` | PC1 bottom-loading, up in Xf_DDpos S215/S234 |
| GA 2-beta-dioxygenase 1-like | `OE9A116007T1,2,3` | PC1 bottom-loading |
| ACBP60 / SARD1-like | `OE9A093289T1`, `OE9A068952` | Up with PGIP in S234/S215 “pathogen” BIN |
| ABI5 | `OE9A075379T1,2,3,4` | PC1 top-loading **down** in Xf_DDpos |

### Rank 4 — Hydraulics / drought-like physiology

**Why.** Infected physiology looks like drought. Resistant trees manage that drought. Surano 2022 is the numbers, not the slogan. Sabella 2019 (PDF not on disk): Leccino constitutively less prone to cavitation, faster refill.

**Surano 2022 (vector-inoculated; Cq means Cellina 20.24, Leccino 22.04, FS17 20.56; Cq not statistically different among infected plants):**

- Stomatal conductance *gs*: Cellina infected always << healthy. Leccino infected differs only at the first two dates. **FS17 infected never differs from healthy.**
- Δ*gs* (healthy − infected): Cellina 0.06–0.20 mol m⁻² s⁻¹; Leccino 0.012–0.066; FS17 −0.001–0.050. Leccino and FS17 not different from each other; both different from Cellina.
- Stem water potential: infected Cellina more negative than Leccino and FS17. Infected Leccino still drops vs its own healthy plants. **Infected FS17 does not.** ΔΨstem near 0 in FS17.

FS17 is hydraulically *at least as good as* Leccino in this trial, with a point estimate of higher bacterial load (lower Cq). That is a split phenotype, not a beat.

**Giampetruzzi Ogliarola-up drought transcripts (RT-qPCR: ELIP, FAR, ABA2):**

| Gene | Contig |
|---|---|
| ELIP | `LCxylem_81506`, `OG_xylem_197731` |
| Dehydrin (*Rhododendron catawbiense*) | `OG_xylem_111461` |
| LEA | `OG_xylem_45532` |
| Mis-called LEA / hydrophilins (Ogliarola **down**) | `LCxylem_268715`, `LCxylem_237449`, `LCxylem_206556` |
| ABA2 | RT-qPCR set; contig in Additional file 8/9 |

**La Notte PC1 down in Xf_DDpos (photosynthetic / sugar collapse S215/S234):**

| Gene | Farga v9 ID |
|---|---|
| Rubisco activase | `OE9A079773T1,2` |
| Beta-amylase 3 chloroplastic | `OE9A045257T1`, `OE9A107186T1` |
| Galactinol synthase | `OE9A047763T1,2` |
| PSII proteins (FC < −5 in S234/S215) | `OE9A075888T1`, `OE9A096707T1` |
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

La Notte: SSRs do **not** predict Xfp phenotype well. Two exceptions with positive fixation index **only in susceptible genotypes**: **GAPU103a** and **UDO99-043**. POP4 (Leccino + Ogliarola + Frantoio + Pendolino) holds 52% of HR/R/T spontaneous trees. POP8 holds FS17 + Cellina + Nociara. Spanish and Greek cultivars showed no genetic similarity to the surviving seedlings.

### What we will not rank

- Olive AOX (Arnholdt-Schmitt; cited by Fanelli 2026 review). Not in the two required papers.
- Endophyte taxa from Vergine 2019. Real, not a gene list.
- Any OE9A ID that does not appear in the extracted La Notte main text.

---

## 2. Does anything beat Leccino / FS-17?

**Named commercial cultivar, 2024–2026: no.**

What was actually screened, and what it showed:

| Source | What was screened | Versus Leccino / FS-17 |
|---|---|---|
| Pavan et al. 2021 *Front. Plant Sci.* (PDF on disk) | Grower PRPs in Lecce, 2019–2020; 23 PRPs in SSR cluster K1 with Leccino and FS-17; controlled test of Frantoio, Nocellara Messinese, Pendolino, Bella di Spagna vs Ogliarola, Cellina, Leccino (8 biological replicates, Wilcoxon) | **Leccino still lowest symptoms and lowest colonization.** Frantoio and Nocellara Messinese < susceptible controls (partial resistance). Not a beat. Official reconversion at the time: only Leccino and FS-17. |
| Prior Italian screens cited by Pavan (Baù 2017; Boscia 2017) | Italian cultivars | None comparable to Leccino/FS-17. Intermediate: Frantoio, Toscanina, Termite di Bitetto, Maiatica, Dolce di Cassano, Oliastro, Nociara, Nocellara Etnea. |
| La Notte / Saponari / Giampetruzzi / Saldarelli 2024 (PDF on disk) | 171 symptom-poor spontaneous genotypes in the high-inoculum zone; 139 unique SSR profiles; 61 Leccino progeny field-scored; four open-pollinated seedlings artificially inoculated (S105, S215, S218, S234) vs Leccino and Cellina | Field: 67% of Leccino offspring HR/R/T vs 32% Cellina and 49% Ogliarola. Inoculation: **S105 and S215 (Leccino × Cipressino) showed no desiccation at 24 mpvi; Leccino, S218, S234 showed mild shoot dieback; Cellina collapsed.** S215: only 2 replicates qPCR-positive at 24 mpvi. **S105 had the highest bacterial population of the four seedlings** and was the exception vs Cellina at 16 mpvi. |
| Agromillora / Agrimeca Nov 2025 (local extract) | Legal replant set | Four authorized cultivars: **Leccino, FS-17, Lecciana, Leccio del Corno**. Authorization ≠ superiority. No titer table. |
| Olive Oil Times 5 Jan 2026 (BeXyl greenhouse report, not the paper) | Leccino, Frantoio, Gordal vs Arbequina / Arbosana under *pauca* | Those three had **lower** load/symptoms than the SHD Spanish pair. That is “with Leccino,” not “beats Leccino.” Gordal remains a greenhouse claim until the BeXyl paper. |
| Abou Kubaa / Giampetruzzi / Saldarelli 2025 *Physiol. Mol. Plant Pathol.* (abstracts only; PDF not on disk) | Clones of cultivar Leccino | Intra-cultivar HR / R / T split. Variation *inside* Leccino, not a replacement cultivar. |
| Fanelli et al. 2026 *BMC Plant Biol.* (abstract) | Cultivar transcriptomes | Treats Leccino as the resistant reference. Does not claim a beat. |
| Surano 2022 (PDF on disk) | Leccino vs FS17 vs Cellina, hydraulics | FS17 matches or beats Leccino on *gs* and ΔΨstem; Leccino has the better (higher) Cq. Split, not a commercial beat. |

**The real challenge to the ceiling is not Frantoio.** Pavan is partial resistance below Leccino. The challenge is:

1. **S105** — Leccino × Cipressino, field HR, fewest DEGs (2,897 vs 9,956 / 13,080), zero desiccation, **but not lower titer than Leccino**. Quiet host, not a sterilizer.
2. **S215** — same cross (paper: originates from a rootstock; carries olive leaf yellowing associated virus and olive latent virus 1). Zero desiccation **and** colonization that fails to progress (2/n positive at 24 mpvi). This is the closest thing in the corpus to “better than Leccino” on both axes.
3. **Cipressino as the other parent** — Saponari personal communication in La Notte: “not as susceptible as Cellina / Ogliarola.” Crosses to the two local susceptibles (S218 = Leccino × Cellina; S234 = Leccino × Ogliarola) only matched parental Leccino.
4. **Legal set is already four cultivars**, not two. Lecciana and Leccio del Corno are in the ground in Salento. We have no head-to-head titer paper that puts them above Leccino.

S105 / S215 are **not released cultivars**. Treating them as a replant option would be a category error. Treating Leccino as the last word on olive genetics is also a category error. CORDON’s own `entities/leccino.md` line “No screened cultivar has beaten Leccino / FS-17” is true for *cultivars* and false if “cultivar” is allowed to mean “genotype.”

---

## 3. ST53 / Xfp surface and xylem-exposed proteins (phage / AMP targets)

No ST53 proteome PDF is on disk. The olive-infecting reference genome is *X. fastidiosa* subsp. *pauca* strain **De Donno** (ST53 / CoDiRO), complete genome Giampetruzzi et al. 2017 *Genome Announc.* Strain used for phage work below is **A0PT1** (ST53, olive, Apulia) — Sabri 2024 and Cara / Sabri et al. 2026. Giampetruzzi 2016 notes the CoDiRO polygalacturonase has a **premature stop codon**, offered as a reason for slow movement / low titer. We do not have the De Donno locus tag for that ORF in local files. Do not invent one.

Xylem-exposed / surface families with a published phage or AMP analogue:

| Target class | Why it is xylem-exposed | Published analogue | ST53-specific caveat |
|---|---|---|---|
| **Type IV pili** (PilA / PilY1 / PilQ / twitching apparatus) | Surface nanofilaments; motility, aggregation, biofilm, vector acquisition | Ahern et al. 2014: phages **Sano, Salvo** (siphophage) and **Prado, Paz** (podophage) are **type IV pilus–dependent** on both *X. fastidiosa* and *Xanthomonas*. Das et al. 2015: four-phage cocktail reduced Pierce’s disease in grape. Commercial **XylPhi-PD** (Ahern / Texas A&M lineage) is the field analogue — grape, not olive. Cara 2026: Phi3 is 96.70% identical to *Xylella* phage Salvo (genus *Salvovirus*). | Receptor demonstrated on *Xf*, not yet mapped on De Donno / A0PT1 in papers we hold. Pilus-minus escape is the classic resistance path. |
| **LPS / outer membrane** | Gram-negative OM; first surface a tailed phage hits if not pilus | Sabri 2024: MATE 2 is polyvalent on *Xanthomonadaceae*; paper states polyvalent phages typically use **OMP or LPS** via the same tail fiber. Receptor of MATE 2 is **not experimentally identified**. | “OMP or LPS” is a literature class, not a measured A0PT1 receptor. |
| **XadA family trimeric autotransporter adhesins** (XadA / XadA1 / XadA2 / XadA3) | Afimbrial adhesins; biofilm; Caserta 2010; Feitosa-Junior 2022; Scala / XadA2 2025 (Temecula1, not ST53) | No published phage whose receptor *is* XadA. AMP / antibiofilm peptides (Moll 2021; El Handi 2022) hit the biofilm that XadA helps build. | Do not claim XadA is a phage receptor. It is a biofilm / adhesion target. |
| **Type I fimbriae (FimA)** | Attachment / biofilm | Same as XadA: biofilm-axis, not a named phage receptor. | — |
| **MopB** (major OMP) | Dominant OM protein in *Xf* surface profiles (Igo / PD proceedings) | Candidate OMP receptor class for polyvalent *Xanthomonadaceae* phages. Not demonstrated for MATE 2 or Phi1. | Family-level only. |
| **EPS / biofilm matrix** (gum, DNA, protein) | Occludes vessels; the clinical object | Moll 2021: peptides **1036** and **RIJK2**, dual bactericidal–antibiofilm on Mediterranean *Xf* (selected strain IVIA 5387.2). El Handi 2022: **Ascaphin-8 (GF19)** and **IL14**, 40–50% biofilm reduction at 50 μM. Phi1/Phi3 2026: *in silico* depolymerases (DePP >90%) and endolysins. MATE 2 encodes an endolysin (Sabri Fig. 2). | Peptides were not tested on ST53 A0PT1 / De Donno in the papers we read. IVIA 5387.2 is a Mediterranean strain panel pick, not ST53-olive by default. |
| **Peptidoglycan (endolysin substrate)** | Exposed after OM disruption, or via phage lysis cassette | MATE 2 endolysin; Phi1/Phi3 predicted endolysins (Cara 2026). | Gram-negative OM blocks naked endolysin unless delivered or engineered. Paper-only. |
| **pglA polygalacturonase** | Secreted CWDE; pit-membrane punch | Not a phage receptor. Host-side counter is PGIP (`OE9A070676T1`, `OE9A036088T1`). CoDiRO allele is truncated (Giampetruzzi 2016). | Truncation may already limit ST53 movement. Knocking it further is not an AMP plan. |

**Phage objects that actually exist against *Xfp* / *Xf*:**

| Phage | Year | Host in the paper | Form | Field? |
|---|---|---|---|---|
| Sano, Salvo, Prado, Paz | Ahern 2014 | *X. fastidiosa* + *Xanthomonas*; T4P-dependent | Isolated, characterized | Das 2015 grape cocktail; later XylPhi-PD commercial (US grape) |
| Usme, Cota, Bacata (and *Xanthomonas* phages Sopo, Tabio, Tenjo) | Clavijo-Coppens 2021 | Mediterranean *Xf* isolates + *X. albilineans* | Isolated, sequenced | No olive field product. PDFs not on disk; names from PMC/secondary. |
| **MATE 2** | Sabri et al. 2024 *Front. Microbiol.* 15:1412650 | *Xfp* A0PT1 (ST53); also *X. albilineans*, *X. campestris* | Sewage, southern Italy. 63,695 nt, 95 ORFs, *Carpasinavirus*, no lysogeny/virulence/AR/toxin. Adsorption 10 min. 77% lysis at 24 h; culture cleared 48 h; no regrowth 7 days. Capsid 60±5 nm, contractile tail 120±7.5 nm. Stable 4–60 °C, pH 4–10. GenBank **PP816325**. Corresponding: Elbeaino, CIHEAM Bari. | **In vitro only.** Authors: “efficacy on Xf-infected olive trees in the field has yet [to be shown].” |
| **Phi1, Phi3** | Cara, Sabri et al. 2026 *Sci. Rep.* 16:11969 | *Xfp* A0PT1 ST53. Isolated Bari sewage Oct 2024. Propagated on *Xcc* CFBP 1710 surrogate. | Phi1: podovirus, 44,345 bp, 92.52% ANI vs *Xanthomonas* phage phi Xc10, genus *Pradovirus*, novel species. Phi3: siphovirus, 55,413 bp, 96.70% identity vs *Xylella* phage Salvo, genus *Salvovirus* (likely same species as Salvo). Strictly lytic *in silico*; no temperate markers, virulence, AMR. No lysis of 14 olive-tree bacteria or 10 beneficials. TEM: replication on *Xfp* cells. | **In vitro + genomics.** “Efficacy under field conditions remains to be evaluated.” |

**BIOVEXO** (H2020 887281, 2020–2025): six candidates — two bacterial strains, one microbial metabolite, two plant extracts, one entomopathogenic. Not phage. Public-facing 2025 press: three biopesticides “may soon be available,” symptom mitigation. Project deliverable language (biovexo.eu public deliverables snippet): **X-biopesticides do not reduce *Xylella* population sizes** even when disease reduction occurs. That is EFSA 2016 in a new bottle: symptom ≠ clearance.

---

## 4. At most ten candidate interventions

Every row is a **paper hypothesis**. Flag on every row: **do not synthesize.** CORDON does not make peptides, phage lysates, or guide RNAs. A named containment lab does, after they ask.

### 1. Breeding marker — S105 receptor cassette
- **Target:** LRR-RLK At3g47580 `OE9A013998T1` / `OE9A100116T1`, plus SOBIR1 / R1A-10 / RGA3 / RPM1-like from La Notte Suppl. Table S4.
- **Why:** Only S105-enriched immune set that is also the Leccino-up class from 2016. Quiet host, HR canopy.
- **Closest analogue:** Grapevine *PdR1b* RLK/RLP cluster (Agüero 2022, cited by La Notte). Not a single olive locus.
- **Why it might fail:** Polygenic. SSR already failed as a phenotype predictor. S105 titer is *not* low. Marker could select pretty canopies that still feed vectors.
- **What a lab does next:** Extract Suppl. Table S4 IDs; design KASP/ampliseq on the 61 Leccino progeny; score vs the existing field HR/R/T calls. No new inoculation required for v0.

### 2. Breeding marker — S215 colonization control
- **Target:** The S215 “infection does not progress” phenotype (2 positives at 24 mpvi), not a single gene. Transcriptomic noise is high; viruses present (OLYaV, OLV-1).
- **Why:** Closest genotype in the corpus to beating Leccino on **both** symptoms and titer trajectory.
- **Closest analogue:** Same La Notte inoculation panel. Cipressino as donor.
- **Why it might fail:** S215 is a grafted rootstock piece, virus-positive. Phenotype may be scion/rootstock or virus confound. Not seed-clean like S105/S234.
- **What a lab does next:** Re-inoculate virus-indexed S215 ramets. If the colonization block holds, map it. If it vanishes, discard.

### 3. Susceptibility-gene screen — DMR6-like / JOX1
- **Target:** `OE9A054976T1`, `OE9A079697T1` (DMR6-like); `OE9A092418T1,2,3` (JOX1 / At3g11180).
- **Why:** La Notte explicitly calls them susceptibility genes; knock-outs work in grape, tomato, potato, banana.
- **Closest analogue:** de Toledo Thomazella 2021; Kieu 2021; Giacomelli 2022; Pirrello 2022 (as cited by La Notte).
- **Why it might fail:** Perennial woody editing; chimeras; SA/JA trade-off that S105 already balances without a knock-out. EU GMO/NGT politics. S105 does **not** need DMR6 knocked out to be HR.
- **What a lab does next:** qPCR the two DMR6 IDs across the 61 progeny. Test whether high DMR6 tracks S215/S234-like noisy resistance. Editing is their decision, not ours. **Do not synthesize guides.**

### 4. Negative marker — GAPU103a / UDO99-043
- **Target:** The two SSRs fixed in susceptible genotypes (La Notte).
- **Why:** Cheap discard rule for a seedling pile. Not a resistance gene.
- **Closest analogue:** The same paper’s POP analysis.
- **Why it might fail:** Authors already say SSRs are underpowered. Fixation in susceptibles ≠ causative. Will throw away useful recombinants.
- **What a lab does next:** Score the existing 139 unique profiles; report PPV/NPV against field HR/R/T. If NPV for “susceptible” is high, keep as a junk filter.

### 5. Seedling ranking rule, not a molecule
- **Target:** Prioritize Leccino × Cipressino over Leccino × Cellina / Leccino × Ogliarola for the next inoculation queue.
- **Why:** La Notte’s own split: Cipressino crosses symptomless; local-susceptible crosses = parental Leccino.
- **Closest analogue:** The 67% R/T rate in Leccino offspring (La Notte). Livestock genomic selection analogy in CORDON.md §3.
- **Why it might fail:** n = 4 inoculated genotypes. Cipressino “not as susceptible” is a personal communication. Oil chemistry / vigor of Cipressino hybrids unknown.
- **What a lab does next:** Ask CNR for the unpublished inoculation panel and score our ranking against it. That is the Artifact B ask in CORDON.md §5.

### 6. Phage — type IV pilus (Sano/Salvo/Prado/Paz → Phi3)
- **Target:** ST53 T4P (PilA/PilY1 surface).
- **Why:** Only *Xf* phage receptor with experimental weight (Ahern 2014). Phi3 (2026) is essentially Salvo on an ST53 host. XylPhi-PD proves the class can leave the fridge — in grape.
- **Closest analogue:** XylPhi-PD / Das 2015 four-phage PD cocktail. AgriPhage™ is the *Xanthomonas* commercial cousin, not *Xf*.
- **Why it might fail:** Pilus-minus escape; xylem delivery; olive biofilm ≠ grape; EU quarantine release of a replicating virus; Phi3 host-range on olive endophytes is a 24-isolate lab panel, not a grove.
- **What a lab does next:** **They** (CIHEAM Bari / CNR, already on MATE 2 and Phi1/Phi3) do A0PT1 pilus-mutant receptor confirmation and a contained plant assay. We do not. **Do not synthesize.**

### 7. Phage — MATE 2 on A0PT1
- **Target:** Unknown A0PT1 surface receptor (OMP or LPS class). Secondary: MATE 2 endolysin.
- **Why:** Fastest published kill curve on *Xfp* (clear at 48 h, no regrowth 7 days). Isolated in the same geography as ST53. Polyvalent on *Xanthomonadaceae*, quiet on the beneficials they tested.
- **Closest analogue:** Itself (Sabri 2024). Isolation pipeline reused for Phi1/Phi3.
- **Why it might fail:** No field olive data. Receptor unknown → resistance unpredicted. Xylem persistence unknown. Polyvalence cuts both ways (non-target *Xanthomonas* on the tree).
- **What a lab does next:** Receptor ID (pull-down / escape mutants). Contained olive plantlet assay. Cocktail with Phi1/Phi3 to slow escape. **Do not synthesize. Do not isolate phage in this apartment.**

### 8. AMP — 1036 and RIJK2
- **Target:** *Xf* membrane + biofilm (dual activity).
- **Why:** Moll et al. 2021 *Front. Microbiol.* 12:753874. Selected after a six-strain Mediterranean panel. Dual bactericidal–antibiofilm, moderate hemolysis / tobacco phytotoxicity. Authors’ own “best candidates.”
- **Closest analogue:** Same group’s BP171 / BP178 (Baró 2020a,b), ~3.6 log kill at 12.5 μM. Older: indolicidin, magainin 2 (MIC 8–64 μM; Li & Gray 2003; Kuzina 2006).
- **Why it might fail:** Strain was IVIA 5387.2, not De Donno/A0PT1. No olive xylem PK. Proteolysis in sap. Phytotoxicity at working dose. Resistance still possible if the mode is not purely lytic.
- **What a lab does next:** MIC / biofilm on A0PT1 and De Donno. Sap stability. Then stop unless a containment partner exists. **Do not synthesize.**

### 9. AMP — Ascaphin-8 (GF19) / IL14
- **Target:** Biofilm (40–50% reduction at 50 μM); GF19 and IL14 highest bactericidal + antibiofilm in El Handi et al. 2022.
- **Why:** Independent peptide set, *in planta* claim in the title. Different chemotype from 1036/RIJK2.
- **Closest analogue:** El Handi 2022 *Biology* 11:1685 (MDPI HTML 404 on our fetch; used PubMed/PMC snippets).
- **Why it might fail:** 50 μM is a lot of peptide to put in a xylem. *In planta* species in that paper is not a bearing olive grove. We did not extract the full methods (Firecrawl rate-limit / MDPI 404).
- **What a lab does next:** Read the full PDF, repeat on ST53, drop if the plant system is tobacco/arabidopsis only. **Do not synthesize.**

### 10. Endophyte / BIOVEXO-class symptom tool
- **Target:** Not a bacterial protein. Host xylem community (Vergine 2019: Leccino microbiota stable under OQDS; Cellina labile) or BIOVEXO bacterial-strain / metabolite products.
- **Why:** Only intervention class with **olive-field** symptom data in Europe. CORDON should not compete with it; we should score it.
- **Closest analogue:** BIOVEXO six-candidate set; *Paraburkholderia phytofirmans* in grape (Baccari 2019). Deliverable caveat: **no effect on *Xylella* population size**.
- **Why it might fail:** EFSA 2016 still binds on clearance. Symptom-only tools do not cut vector acquisition if titer stays high. Product-not-yet as of 2025 press.
- **What a lab does next:** We computationally score BIOVEXO trial blocks against CAMP PCR if they release locations. We do not brew endophytes.

**Not in the ten, on purpose.** RNAi against ERF071 (`OE9A032259`) — tylose is a double-edged host response; silencing it could worsen hydraulics. De novo AMPGAN peptides — CORDON.md already forbids us generating sequences to synthesize. CRISPR olives — locked out in §4.2.

---

## 5. Which CORDON locks survive

| Lock | Status after this brief | Why |
|---|---|---|
| **Computational-only (we do not touch a live bacterium)** | **Survives.** Safety lock, not an evidence lock. Quarantine pest. MATE 2 and Phi1/Phi3 being real wet-lab objects does not put them in this apartment. | CORDON.md §4.4, §7. `assumption-reopen-live.md` already said this. |
| **Do-not-synthesize (AMP / phage / peptides)** | **Survives as a team rule.** The *literature* is past paper-only (see below). We still do not make the molecules. | Same. Every row in §4 is flagged. |
| **AMP / phage stay paper-only** *(as a claim about the world)* | **Does not survive.** | XylPhi-PD is a commercial grape product. Ahern 2014 + Das 2015 left the page a decade ago. MATE 2 (2024) and Phi1/Phi3 (2026) lyse ST53 A0PT1 in Bari-adjacent labs. Moll 2021 and El Handi 2022 are wet AMP assays, not generators. What *is* still paper-only: an olive-grove phage or AMP product, and any CORDON-origin sequence. |
| **Leccino / FS-17 are the ceiling** | **Survives for named commercial cultivars. Dies for genotypes.** | No 2024–2026 paper puts a released cultivar above Leccino on titer *and* symptoms. S105/S215 beat parental Leccino on canopy; S215 also on colonization trajectory. Legal set already expanded to Lecciana + Leccio del Corno without a published superiority trial. `entities/leccino.md` should say “no *cultivar*,” not “no genotype.” Frantoio is partial, below Leccino (Pavan 2021). Gordal is a greenhouse cluster-with-Leccino claim, not a beat. |
| **Do not email Bari until Artifact A or B exists** | **Survives.** | This file is a challenge brief, not the decoder table a postdoc can take to lab meeting without us. The ranked OE9A list + the ten rows are close. Send after a one-page table lands in `data/decoder/`, not this query note. |
| **Do not compete with BIOVEXO** | **Survives, and is now sharper.** | Their field objects are symptom tools that do not move titer. Our decoder should mark seedlings and score their blocks, not invent a seventh biopesticide. |
| **Replant-with-Leccino is already happening; we do not talk as if farmers wait for us** | **Survives.** | Agromillora 2025: hundreds of hectares already going back in as Leccino / FS-17 / Lecciana / Leccio del Corno. |

---

## 6. Nulls, gaps, what we did not do

- **Did not invent gene names.** Every OE9A and every Arabidopsis ID above is in the extracted main text of Giampetruzzi 2016 or La Notte 2024. SOBIR1 / RGA3 / RPM1 / R1A-10 / WAK2-like are *named* in La Notte and ID-less here because they live in Suppl. Table S4.
- **Did not parse Additional file 3** (Giampetruzzi DEG matrix). A real decoder v0 should. That is the next computational hour, not a new paper.
- **Did not re-download Montilon 2022 or Sabella 2019.** Pit-membrane and cavitation claims are cited, not re-read.
- **Did not obtain the De Donno CDS table.** Surface proteins are families, not `B9J09_*` locus tags. A partner with GenBank CP020870 (or the current De Donno accession) can map PilA / XadA / MopB in an afternoon.
- **Did not claim Frantoio or Gordal beat Leccino.** Pavan 2021 is explicit that Leccino remains lowest. The 5 Jan 2026 Olive Oil Times piece groups Frantoio and Gordal *with* Leccino against Arbequina/Arbosana.
- **Did not treat S105 as a cultivar.** It is a seedling. Its titer is the *highest* of the four inoculated Leccino offspring.
- **Did not treat S215’s colonization block as clean.** Virus-positive rootstock origin.
- **Did not extract Clavijo-Coppens or Ahern PDFs.** Phage names and the T4P-receptor claim are from PubMed/PMC/secondary. Receptor sentence for Ahern is widely restated (including Cara 2026); still, the primary PDF is not on disk.
- **El Handi 2022 full text** failed (MDPI 404 + Firecrawl rate limit). Peptide names GF19 / IL14 / Ascaphin-8 are from PubMed/PMC snippets.
- **No peptide sequences are reproduced here on purpose.**
- **No one was emailed. Nothing was synthesized.**

**What would falsify this brief.** (1) A 2024–2026 paper with a named cultivar, qPCR, and symptom scores that beat Leccino on both. (2) Suppl. Table S4 IDs that show the S105 “receptor” story is a GO dump, not a coherent cassette. (3) An ST53 plant assay where MATE 2 or Phi1/Phi3 fail to move titer. (4) Additional file 3 showing the Leccino LRR-RLK up-list is a single noisy contig.

**Handoff.** This file is `queries/`, not `data/decoder/`. The decoder v0 table still needs: parsed Additional file 3, La Notte Suppl. S4 IDs, and De Donno locus tags. Until those three exist, do not send Bari.
