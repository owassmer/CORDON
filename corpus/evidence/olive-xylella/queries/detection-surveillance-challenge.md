---
title: Detection and surveillance challenge
created: 2026-08-15
updated: 2026-08-15
type: query
tags: [detection, method, controversy, open-question]
sources:
  - nowcast/SCENE_JOIN.md
  - concepts/previsual-detection.md
  - data/DAY1.md
  - raw/papers/zarco-tejada-2018-natureplants.pdf
  - raw/papers/zarco-tejada-2021-natcomm.pdf
confidence: medium
contested: true
---

# Detection and surveillance challenge

Question this file answers: *what would falsify the one-scene NDMI result, and is CORDON's assumption that 10 m NDVI is dead and airborne hyperspectral is out of reach still allowed to stand?*

Not: a nowcast. Not: a literature victory lap.

CORDON's current claim, written before this pass (`nowcast/SCENE_JOIN.md`, 15 Aug 2026):

- Scene `S2A_34TBL_20210812_0_L2A`, cloud 0.014%, tile covers Bari / Brindisi / north Taranto, **not Lecce**.
- 50 official CAMP PCR positives + 50 negatives, summer 2021, SCL 4/5/7 prefilter.
- Pre-registered move rule: |Cliff’s δ| ≥ 0.15 **and** two-sided permutation p < 0.05; predicted direction: positives drier.
- **NDMI moved** (mean pos −0.060 vs neg −0.015; δ −0.312; p = 0.008).
- **NDVI did not** (δ −0.124; p = 0.29).
- **NDRE direction-only** (δ −0.218; p = 0.072).
- No drought control. Labels are northern-front CAMP PCR. Olive positives collapse after 2021 (2,861 → 235 → 123).

Two load-bearing assumptions sit under that table: (1) 10 m NDVI is the wrong object, so a moisture index is the next honest feature; (2) airborne hyperspectral is proven physics we will not fly, so Sentinel-2 + official PCR is the only computational path. Both can be wrong in ways that kill Artifact A.

**Bottom line, before the citations.** The NDVI miss is *expected* from Zarco-Tejada 2018 and is not a CORDON discovery. The NDMI hit is still a drought-shaped residual until it is residualized. Airborne hyperspectral is not out of reach in Puglia — REDoX flew CASI + thermal in 2022 and published toward-operational SVM numbers in 2025 — but it is also **not** an operational Regione nowcast. CORDON is not yet redundant. It is also not yet a detection result.

[[previsual-detection]] · [[front-nowcast]] · [[puglia-monitoring]] · [[camp-csv]]

---

## 1. Zarco-Tejada 2018 and 2021 — exact traits, exact accuracies

Local PDFs: `raw/papers/zarco-tejada-2018-natureplants.pdf` (Owen-fetched preprint; line numbers below from `pdftotext -layout`) and `raw/papers/zarco-tejada-2021-natcomm.pdf`. Publisher records: *Nature Plants* 4:432–439, doi:10.1038/s41477-018-0189-7; *Nature Communications* 12:6088, doi:10.1038/s41467-021-26335-3.

### 1.1 2018 — what actually moved

Instrument: airborne imaging spectroscopy (260 narrow bands) + thermal, June 2016 and July 2017, 15 Puglia orchards, mostly old Ogliarola Salentina / Cellina di Nardò, one Leccino block. Visual DS 0–4 on 3,328 trees (2016) and 3,987 trees (2017). Oracle: qPCR (Harper et al. assay).

Traits that carried the detection, ranked by ROC on the training set (n = 5,852 trees):

| Rank / role | Trait | What it is | Why it is not 10 m NDVI |
|---|---|---|---|
| 1–2 (asymp vs sympt) | **NPQI** | Chlorophyll-degradation / phaeophytinization index from **415 and 435 nm** | Sentinel-2 B2 is 490 nm. No NPQI. |
| 1–2 | **CWSI** | Crop Water Stress Index from crown temperature | S2 has no thermal. Landsat TIR is ~100 m. |
| next | **Anth**, **Cx+c** | Anthocyanins, carotenoids (photoprotection / pigment degradation) | Need narrow visible bands + RT inversion. |
| next | **SIF / Fi** | Solar-induced fluorescence and fluorescence efficiency via FluorFLIGHT 3-D | Not a Sentinel-2 product at tree scale. |
| failed | **NDVI** | Standard red–NIR greenness | “NDVI did not differ significantly between asymptomatic and symptomatic trees … and was therefore unable to detect non-visual symptoms.” |

Model ladder on the held-out visual set (test n = 1,463 of 7,315):

| Input set | OA | κ |
|---|---:|---:|
| SVI — NDVI + blue/green/red ratios (the satellite-like bandset) | **65.4%** | **0.29** |
| PS — pigment + structure traits, no SIF, no temperature | intermediate | intermediate |
| **PSFT** — pigment + structure + fluorescence + temperature (SVM) | **80.9%** | **0.61** |

Against qPCR, not against the human eye:

- One orchard, n = 67 qPCR trees: RS OA **94.03%**, κ **0.88**. Visual vs qPCR: OA 77.62%, κ 0.55.
- Eight orchards, n = 100 qPCR-visible trees: RS OA **96%**, κ **0.92**. Visual stays ~77% / 0.54.
- Of qPCR-positive, visually asymptomatic trees: RS caught **92.9%**.
- In the intensively tested orchard: 11 of 40 visual-asymptomatic trees were qPCR-positive; RS called them infected at **91%**.

Temporal revisit (the actual previsual claim): trees the 2016 PSFT model called affected but pathologists called clear (SVM FP n = 178) developed visible symptoms at **61%** by month 4, versus **39%** of the true-negatives (n = 818; two-sided t-test p < 0.001). That gap held through 12 months. This is the sentence CORDON keeps quoting. It is real. It is not a 10 m result.

Operational aside the 2018 paper itself already wrote: an aircraft payload of **<10 narrow VNIR bands (≤10 nm) plus a broadband thermal** would still exceed **70%** OA. That is the cheaper airborne floor, not Sentinel-2.

### 1.2 2021 — drought is the hard problem, and they measured it

Instrument: same physics, now >1 million olive and almond crowns, Xf and *Verticillium dahliae*, pathogen-free water-stress flights over ~380,000 trees across two summers. Feature-weighted ML, then a second-stage clustering on traits that diverge between biotic and abiotic pathways.

Before uncoupling (biotic traits only):

| Pathosystem | n trees | OA | κ |
|---|---:|---:|---:|
| Xf almond | 4,048 | 84% | 0.68 |
| Xf olive | 7,296 | 77% | 0.43 |
| Vd olive | 1,852 | 75% | 0.49 |

After uncoupling (host- and pathogen-specific divergent pathways; high-uncertainty trees re-scored):

| Pathosystem | OA | κ | oracle |
|---|---:|---:|---|
| Xf almond | **94%** (was 83%) | **0.87** (was 0.65) | qPCR n = 265 |
| Xf olive | **92%** (was 62%) | **0.83** (was 0.25) | qPCR n = 77 |
| Vd olive | **93%** (was 75%) | **0.87** (was 0.49) | visual n = 1,852 |

Misclassified fraction after the abiotic uncouple: **6.5% olive, 6.6% almond** — the “uncertainty below 6%” line. High-uncertainty share *before* the uncouple: 38% of olive, 17% of almond.

Abiotic ranking, pathogen-free groves, CWSI-clustered C0–C4: **CWSI first**, then xanthophyll-cycle **PRIn**. As water stress rose, transpiration traits lost relative importance and pigment/structure gained. In olive, **NPQI was insensitive to abiotic stress** (Anth only weakly sensitive). That is the 2021 reason NPQI is a biotic marker and CWSI is not: the same water-stress direction can be drought or Xf, and only the *rest of the trait vector* splits them.

Irrigated almond vs rainfed: NPQI marked Xf in almond **only under non-water-limited conditions**. Olive stem Ψ in the scanned groves ran −2.0 to −2.9 MPa; almond −1.7 to −1.9 MPa. Any 10 m moisture index that cannot condition on irrigation status is repeating the 2021 failure mode.

### 1.3 Is 10 m NDVI failing expected?

**Yes. Expected, and already published in 2018.** Zarco-Tejada’s own single-date NDVI boxplots do not separate asymptomatic from symptomatic crowns. The SVI (satellite-like) model is their *worst* model, 15 points of OA below PSFT. CORDON’s NDVI δ −0.124 / p = 0.29 is a replication of that negative, at coarser grain, on official PCR instead of visual+qPCR. It does not license the stronger claim “greenness is dead.”

Hornero et al. 2020 (below) then showed that **multi-date** Sentinel-2 *soil-adjusted* greenness (ARVI, OSAVI) **does** track orchard-level disease incidence once understory is modelled — r² > 0.7. So the honest statement is narrower:

- Single-date 10 m NDVI is a weak previsual feature. Zarco already knew.
- Multi-date soil-adjusted greenness can still carry **incidence**, not incubation.
- NDRE failing to clear p < 0.05 on n = 100 is not a death certificate for red-edge. It is an underpowered one-scene test.

What 10 m NDVI *cannot* do, and will not start doing: retrieve NPQI (wrong blue bands), SIF, or CWSI. That is a sensor limitation, not a sample-size limitation.

---

## 2. Later remote-sensing / UAV / satellite Xylella papers, 2018–2026

Sweep run 15 Aug 2026. Papers listed only if a primary or near-primary text was opened this session, or a numbered result was read from a publisher/PMC/author-PDF page. “Galván” as a named Xylella RS paper was **not located** (see §8).

### 2.1 Airborne / UAV — Puglia and near-Puglia

| Year | Paper | Platform | What they actually classified | Headline number | Bearing on CORDON |
|---|---|---|---|---|---|
| 2020 | Di Nisio, Adamo, Acciani, Attivissimo, *Sensors* 20:4915. doi:10.3390/s20174915 | UAV RGB + multispectral, Poliba, south Italy | **Visible OQDS symptoms**, LDA after a new crown-segmentation | Segmentation Sørensen–Dice ~70%; **98% sensitivity, 93% precision** on affected trees | Fast visual scouting, not previsual, not PCR. Does not compete with NDMI. |
| 2020 / 2021 | Castrignanò et al., *Remote Sens.* 13:14. doi:10.3390/rs13010014 | UAV multispectral, 3 Apulian groves, 4 flights 2017–2019 | Xfp **severity class**, geostats + discriminant | Non-parametric CV: **OA 0.69**, error 0.31; early-detection class **acc 0.77 / misclass 0.23** | Honest early-class number is far below Zarco PSFT. UAV MS is not a substitute for fluorescence+thermal. |
| 2021 | Castrignanò et al., *Sci. Total Environ.* (geostatistical fusion) | UAV + proximal geophysics + visual + diagnostics, Oria (BR) | Probabilistic **infection-risk map** | Qualitative: entry points and high-risk patches | Fusion is the move; we have not reproduced it. |
| 2020 | Poblete, Camino, Beck, Hornero et al., *ISPRS JPRS* 162:27–40 | Airborne MS + thermal; bandset reduction from hyperspectral | Xf symptoms | Band-reduction study (cited by D’Addabbo 2025 as the operational-bandset paper) | The cheap-airborne path Zarco 2018 already sketched. |
| 2021 | Poblete et al., *ISPRS JPRS* (JRC124921). Discriminating Xf from *V. dahliae* | Airborne thermal + hyperspectral plant traits, 27 flights | Xf vs Vd vs healthy | Three-stage ML: **FPR 9%, OA 98%, κ 0.7** on Vd identification | Directly relevant confounder. Puglia olives get Verticillium. CORDON has no Vd layer. |
| 2021 | Camino et al., *Remote Sens. Environ.* (JRC122399) | Airborne traits + epidemic-spread model, **almond** (Alicante) | Xf infection | RS-only weaker; **RS+spread OA 80%, κ 0.48**; qPCR subset n = 318: **OA 71%, κ 0.33** vs RS-only 64–65% / 0.26–0.31 | Spatial prior beats spectra alone. CORDON should steal this, not just indices. |
| 2022 | Camino et al., *Remote Sens. Environ.* 282:113281 | Airborne HS, SCOPE / PROSAIL-PRO, Vcmax + biochemistry | Xf in almond | Validation **AUC 0.96** | Still airborne, still not 10 m. |
| 2023 | Belmonte et al., *Remote Sens.* 15:656 | UAV, multi-scale geostats | Spatial modelling of infection risk | Method paper | Same Bari/CNR-IREA cluster as Castrignanò / D’Addabbo. |
| 2024 | Hadjichristodoulou et al., SPIE 13212:1321210 | Review | “How RS can be used for Xf” | Review, not a new accuracy | Useful bibliography; not a result. |
| 2025 | D’Addabbo & Matarrese, *Remote Sens.* 17:1372. doi:10.3390/rs17081372 | Airborne CASI 1500 (up to 288 bands, 350–1050 nm) + MICRO TABI 640 thermal, **50 cm**, Sep 2022, Gorgognolo + Polignano | Infected vs not, SVM on crown segments (Mean-Shift on NDVI-mask + IR) | Best Gorgognolo classifiers reach **OA 86.1%** at 85% train; mean OA on a joint set **68.3%**. Polignano is 8.5% infected and **does not support a robust classifier**. | **REDoX-funded.** Closest thing to “operational airborne” in Puglia. Explicitly *toward* a system, not a shipped service. Cross-grove transfer is the unsolved problem. |

Di Nisio’s 98/93 is the number most likely to be waved at CORDON as “UAV already solved this.” Read the abstract: they classified **affected** trees — OQDS you can see. Incubation 6–18 months is named as the reason PCR is still required. Do not let that paper retire previsual.

### 2.2 Satellite — what Sentinel-2 has actually been shown to do

| Year | Paper | What S2 was asked to do | Result | Bearing |
|---|---|---|---|---|
| 2018 | Hornero et al., IGARSS / Quantalab PDF “Using Sentinel-2 Imagery to Track Changes Produced by Xylella Fastidiosa in Olive Trees” | Track **symptom** change | Exploratory | Not previsual. |
| 2020 | Hornero, Hernández-Clemente, North, Beck, Boscia, Navas-Cortés, Zarco-Tejada, *Remote Sens. Environ.* 236:111480 | Orchard **incidence and severity** from 2-year S2A time series, 3D-RTM for seasonal understory, validated on >3,000 trees / 16 orchards + coincident airborne HS | ARVI and OSAVI temporal variation: **r² > 0.7** (p < 0.001) for DS and DI. Modelling seasonal understory **cut DI prediction error 3-fold**. | The important S2 paper. They write, in the introduction, that **tree-level early/non-visible alterations “cannot be detected directly by current satellite sensors due to their limited spectral and spatial resolutions.”** Intermediate-to-advanced symptoms are the object. |
| 2023 | Blonda et al., *Sci. Rep.* 13:5695 | Multi-resolution satellite on bio-fertilizer **restoration** in Xfp groves | Restoration monitoring, not detection | Downstream of the epidemic, not a nowcast. |
| 2025 | D’Addabbo 2025 (above) mentions S2 (13 bands, 5-day) only as context | Not their classifier | — | They still flew a plane. |

Hornero 2020 is the paper that can kill CORDON’s “weaker version of the same idea at 10 m” sentence. The Zarco group themselves scoped Sentinel-2 to **incidence of visible damage**, and they needed a 3-D canopy+soil RTM to stop the understory from eating the signal. A one-date NDMI on 10 m pixels in August — peak dry grass between crowns — is the setting Hornero spent a paper warning about.

### 2.3 What this list does *not* contain

- A published, validated, **previsual** Sentinel-2 tree-level detector against qPCR.
- A 2024–2026 paper that makes 10 m NDVI suddenly work for incubation.
- A “Galván” Xylella RS paper (name was in the task list; this sweep did not find a distinct match — do not invent one).
- An operational Regione product that already consumes CAMP + S2 and ships a suspicion map.

---

## 3. Has anyone operationalized previsual detection in Puglia?

### 3.1 Planetek REDoX — project, not a public nowcast

- Project: **REDoX — Remote Early Detection of Xylella**, MIMIT / MiSE grant **F/200139/01-03/X45**. Coordinator: Distretto Tecnologico Aerospaziale (DTA). Planetek Italia: service design + processing. Operational base named as Grottaglie airport.
- Stated goal (Vincenzo Barbieri, Planetek CMO, Olive Oil Times 17 Dec 2021): “a methodology applicable to large areas to identify olive trees that are infected with Xylella but do not yet show evident symptoms.” Thermal + hyperspectral on long-endurance UAV; first trials Monopoli (BA); further flights discussed for Apr and Aug 2022 inside the national action plan.
- Scientific output that actually exists: D’Addabbo & Matarrese 2025, explicitly “funded by … the REDoX project.” They flew a **manned aircraft** with CASI + TIR at 50 cm over Gorgognolo and Polignano in September 2022. Conclusion, quoted from the paper: an operational system *could* support current sampling, **but** training data must come from multiple groves and geographies or cultivar/management shift kills the SVM. Polignano’s 8.5% positive rate already broke it.
- That is a research pipeline with one published classifier study. It is not Regione Puglia’s monitoring system. It is not a Sentinel-2 product. It is not something a grower or a CNR postdoc can query.

### 3.2 Planetek FIXYLL — farm service, 2024–2025

FIXYLL (“FIght XYLeLla fastidiosa”), Planetek + DTA, ~18 months, kickoff Jan 2024, stated end Jul 2025. Satellites **and** drones, framed as innovative services **to farms**, not as a replacement for official PCR. Complementary to REDoX, not evidence that the Osservatorio already runs a nowcast.

### 3.3 Regione / Osservatorio

Official surveillance is still ground crews + laboratory PCR/qPCR (EPPO protocols), mapped at emergenzaxylella.it (SSO-blocked from this host on 2026-08-15; see `data/DAY1.md`). Open slice: CKAN `dati-monitoraggio-xylella-fastidiosa`. CORDON already holds the tree-level CAMP file. Nothing in the 2022 Piano d’azione snippets, the 2024–2026 piano PDF listing, or the CKAN dataset description says the Region scores Sentinel-2 and then samples the score.

### 3.4 Is CORDON redundant?

**No, not yet.** Redundancy would require a shipped, public or partner-only, drought-controlled suspicion layer that (a) already beats NDVI-only and drought-only on a held-out official year, and (b) is what CNR-IPSP / Osservatorio actually use to place the next PCR. REDoX/FIXYLL are airborne/UAV service prototypes. Zarco’s flights were campaign science. Hornero’s S2 work is incidence, not incubation.

**Yes, it can become redundant** the moment Planetek or the Osservatorio publish a validated S2 (or Planet/Skysat) layer over the buffer. CORDON.md already says do not compete with Planetek REDoX. The non-competitive slot that still exists:

1. **Cheap spatial prior for official sampling** on the northern CAMP grain Hornero never used as a tree-level PCR oracle.
2. **Open, reproducible drought ablation** on the public COG + public CAMP join — which REDoX has not released.
3. **A written negative** if that ablation kills NDMI. That negative is still a CORDON deliverable.

If a partner meeting reveals that Osservatorio already ranks parcels with S2 NDMI/ARVI internally, stop building Artifact A and write the partner brief around decoder work instead.

---

## 4. Non-spectral surveillance — dogs, vectors, metabolites, IoT, citizens

These are the oracles and priors a nowcast should lose to, or fuse with. None of them make 10 m NDMI true.

### 4.1 Sniffer dogs

- Puglia 2021 task force (Olive Oil Times, 17 Dec 2021): six dogs (2 Jack Russell, Belgian Shepherd, bloodhound, Labrador, springer spaniel), later “eight units,” trained by Serena Donnini on hundreds of plant-odour samples. Deployment named: **nurseries, ports, airports** — import gate, not the 100 km front.
- BeXyl 2024: Ellis and Paco, FAO video. Goal: early-stage / asymptomatic detection. Still a squad, not a landscape sample.
- Agroportal, 29 Jan 2026 (secondary): tests showed high sensitivity/accuracy; soil where an infected plant had stood was also detectable. **Not independently extracted from a methods paper this session.**
- Niche is real. Landscape scale is not. Dogs do not falsify NDMI; they are a different sampling channel for cryptic trees the nowcast might rank.

### 4.2 Vector PCR in the buffer — this one already found ST1

Cornara et al. 2025, *Eur. J. Plant Pathol.*, doi:10.1007/s10658-024-02945-7 (page text opened via Springer HTML):

- Late summer **2022**: one Xf-positive *Philaenus spumarius* male in an olive orchard, Triggiano (BA), ~20 km NW of the Xfp-ST53 demarcated area, i.e. in the then-free zone. Follow-up inside 500 m: 2 / 79 (2.53%).
- Autumn **2023**: 13 / 474 (2.65%) positive *P. spumarius* in a ~600 m radius, ~1 km from the 2022 orchard, semi-natural + olive.
- Plant campaign followed in early 2024. By end of April 2024, in the Xff-ST1 demarcated area: **289 infected host plants** — 197 almond, 86 grape (wine + table), 4 cherry, 1 apricot, 1 *Polygala myrtifolia*.

Agromillora synthesis (20 Nov 2025; CORDON.md already cites the same outbreak): ~50,000 tests in the restricted area; ST1 on almond 214, grape 127, cherry 7, *Polygala* 1; ~30 ha of vineyard removed. Vector infectivity in the buffer was the leading indicator; plant PCR came second.

CORDON.md already named this as the ctDNA analogue. A nowcast that ignores insect PCR is scoring the wrong compartment for the live 2024–26 emergency.

### 4.3 Azelaic acid

Nicolì, Negro, Nutricati, Vergine, Aprile, Sabella, Damiano, De Bellis, Luvisi, 2019, *Phytopathology* 109:318–325, doi:10.1094/PHYTO-07-18-0236-FI. PubMed 30566025 (abstract retrieved; APS full text not opened).

Claim: azelaic acid (AzA) is a mobile dicarboxylic-acid defence signal that **accumulates in Xf-infected olive**; because it moves, it could reduce the sampling error caused by the bacterium’s erratic within-tree distribution. Framed as a low-cost health-screening metabolite, not as a field kit that Regione runs.

Status: research marker. Not operational. Useful as a *lab* adjunct if CORDON ever ranks trees for a partner to sample; useless as a landscape layer.

### 4.4 IoT stomatal / sap sensors — Cagnarini 2025

Cagnarini et al., 2025, *Plants* 14:1380, doi:10.3390/plants14091380. PDF abstract + HTML body retrieved.

- 40 Cellina di Nardò trees, two Salento groves (Mesagne, Avetrana), TreeTalker on every trunk: sap-flux density (thermal dissipation), under-canopy T, transmitted-band tNDVI (810 / 650 nm), plus nearby ARIF meteo and TTsoil water potential.
- 3% thymol, ± cellulose-nanoparticle carrier, foliar, ~1.5 years. **Neither treatment halted disease or significantly cut bacterial load.** Preventive trial: load reduction increased over time but stayed non-significant. Curative: no effect.
- Symptomatic trees showed **increased** sap-flux density; thymol mitigated that in the curative trial. tNDVI stayed lower on infected trees; the greenness response **lagged** symptom severity.
- Stomatal conductance / transpiration on non-symptomatic leaves of infected trees did **not** collapse — “functioning stomatal control.” That is a warning for any remote CWSI/NDMI story that assumes Xf = stomatal shutdown = dry pixel.

This is proximal physiology on 40 trees in the **infected zone**, not a buffer nowcast. It does two useful things for CORDON: (1) it shows NDVI-like greenness is a late, blunt instrument even at the trunk; (2) it shows the hydraulic signature is not a simple “drier = sicker” monotone. If NDMI is just “drier,” Cagnarini is a reason to be nervous.

### 4.5 Citizen science

- BRIGIT / John Innes Centre (UK): public reporting of suspect plants to the plant-health authority. Preparedness, not Puglia operations.
- Olive Oil Times, 29 Mar 2021: volunteers in Puglia and Andalusia tracking spittlebug activity with mobile apps (BeXyl / related). Useful phenology, not a PCR substitute.
- Pavan et al. 2021 / La Notte et al. 2024 already used grower-reported paucisymptomatic trees in Salento as a **germplasm** screen, not as a surveillance network.

No evidence that citizen reports are an official layer on emergenzaxylella.it. Do not build Artifact A as a citizen app.

---

## 5. How to drought-control NDMI — and what would falsify the one-scene result

NDMI = (NIR − SWIR1) / (NIR + SWIR1) = Sentinel-2 `(B8 − B11) / (B8 + B11)`. It is a canopy-water / SWIR contrast. It moves with Xf-like hydraulic failure **and** with irrigation, August senescence of the grass understory, soil brightness, LAI, recent rain, and SCL-adjacent mixed pixels. Zarco 2021 is the existence proof that this family of signals is the main false-positive engine.

### 5.1 Controls that would make the test honest

Do these **before** calling NDMI a nowcast feature. Write the decision rule first, as `nowcast/SCENE_JOIN.md` already did for the uncontrolled test.

1. **Residualize the index, do not just add covariates.**
   - Fit NDMI ~ f(NDVI or OSAVI, LAI-proxy, fraction bare/soil) on the *negatives*, apply to all, test the residual.
   - Hornero 2020: ARVI and OSAVI beat raw NDVI once soil is in the model; a 3-D RTM cut DI error 3×. Minimum viable CORDON version: OSAVI + NDMI residual, not NDMI raw.
2. **Weather, same week as the scene.**
   - 12 Aug 2021 is high-summer. Pull ERA5 / ARIF station P, T, VPD, and a 30- and 90-day SPEI or SPI for each point (or for the comune).
   - If the pos−neg NDMI gap vanishes inside SPEI strata, it was drought geography, not infection.
3. **Irrigated vs rainfed.**
   - Split the 100 points (and then the full SCL-clean 260/841) on an irrigation layer: SIGRIA / Regione irrigable cadastre if it exists, or a summer NDVI-amplitude proxy (irrigated olives hold greenness).
   - Zarco 2021: NPQI marked Xf in almond only when water was not limiting. An NDMI gap that is just “rainfed positives vs irrigated negatives” is dead.
4. **SCL and mixed pixels, again.**
   - Keep 4/5/7. Also drop pixels whose 10 m footprint is < some olive-fraction threshold (even a crude summer NDVI cut, or a 3×3 purity rule).
   - August understory in Brindisi is dry grass. A 10 m pixel on a traditional wide-spaced grove is mostly soil+grass. That is Hornero’s understory term. If positives sit in more open groves than negatives, NDMI is spacing.
5. **Soil.**
   - Copernicus SSM or SMAP at the scene date; soil-texture class if a Puglia soil map is open.
   - Test NDMI residual after SSM. If the Cliff δ dies, it was soil moisture.
6. **Design, not just features.**
   - Pair each positive to its nearest negative **inside the same comune and same irrigation class** (or 1 km). Recompute δ on the pairs.
   - Spatial-block permutation (shuffle labels inside 2–5 km blocks, or inside comuni), not iid label shuffles. Brindisi-heavy positives (4,018 of 5,195 olive positives in CAMP) will manufacture a climate/soil main effect.
7. **Time.**
   - Repeat the identical 50/50 (or the full 260/841) on a **2020** August scene and a **2021 June** scene. Previsual that is real should exist before peak visual, and should not be unique to one dry Thursday.
   - Hornero-style two-year anomaly: does 2021 NDMI deviate from that pixel’s own 2017–2020 August climatology more for positives than for negatives?

### 5.2 Pre-registered falsifiers

Any one of these, written now, kills the SCENE_JOIN NDMI sentence as a *detection* claim. The join path (CAMP lat/lon → COG → index) can still be true.

| ID | Falsifier | Why it is fatal |
|---|---|---|
| F1 | After residualizing NDMI on SPEI + irrigation class + SSM (or on NDVI/OSAVI + SSM), \|δ\| < 0.15 or perm p ≥ 0.05 | Uncontrolled moisture, not Xf. |
| F2 | Paired-within-comune test loses the gap | Spatial confounding (Brindisi climate/soil). |
| F3 | Spatial-block permutation p ≥ 0.05 | Same, more formally. |
| F4 | 2020 August or 2021 June replication fails the move rule | One-date weather. |
| F5 | Pixel-purity / understory filter removes the gap | Mixed-pixel grass, not canopy water. |
| F6 | Same NDMI gap appears when labels are shuffled onto 2018–19 “would-be” coordinates, or onto non-olive CAMP rows | Index marks a place, not a PCR. |
| F7 | Restricted to CAMP rows with `SINTOMO = Assente`, NDMI does not move | We detected symptomatic dryness, i.e. Hornero incidence, not Zarco previsual. **This is the one that decides whether Artifact A is allowed to use the word previsual.** |
| F8 | A drought-only model (SPEI + irrigation + SSM, no spectrum) matches or beats NDMI on a held-out year | The mandatory ablation in `concepts/front-nowcast.md`. |

F7 is not optional. CAMP has a symptom field. SCENE_JOIN did not stratify on it.

---

## 6. The 2022–23 positive collapse — epidemic drop or monitoring-design change?

### 6.1 What CORDON measured

From `data/DAY1.md`, CAMP_2020_2022.csv (full file, through 30 Jun 2023):

- Olive positives: **2020 = 1,976 · 2021 = 2,861 · 2022 = 235 · 2023 (to 30 Jun) = 123**.
- Lecce **absent**. Provinces present: Bari, Brindisi, Taranto, BAT, Foggia. Brindisi holds 4,018 of 5,195 olive positives.
- This is official monitoring of the **buffer / northern front**, not a census of dead Salento.

A 2022–23 temporal hold-out is therefore honest in time and **starved by construction**. `concepts/front-nowcast.md` already requires a 2020–21 spatial fold alongside it. That requirement stands.

### 6.2 Ciervo & Scortichini 2024

Ciervo, M. & Scortichini, M. (2024). *J. Phytopathology*, e13272. doi:10.1111/jph.13272.

**Full Wiley PDF was not retrieved this session** (publisher HTML abstract only). Numbers below are from the FoodTimes 25 Feb 2024 write-up of that paper, which reproduces the authors’ figures and is marked **secondary**. Treat as provisional until the PDF is on disk.

What the secondary account says they found:

- Incidence in the last two campaigns **≤ 0.23%** in all monitored (demarcated) areas.
- 2014–15: **69.56% of symptomatic olive trees** tested Xfp-positive — early-campaign symptomatics were mostly Xf.
- From 2021, plants **removed far exceed** PCR-positives (they quote +1050% and almost +1300% in the last two campaigns) because the 50/100 m asymptomatic radius still comes down.
- They argue the bacterium’s incidence in demarcated areas is “surprisingly low” and that drastic felling of monumentals should be revisited.

**Contested.** Scortichini has a public record of arguing Xf is not the main cause of Apulian olive death (Olive Oil Times, 25 Mar 2024, “Scientists Defend Study…”). Do not let Ciervo’s low incidence become CORDON’s epidemiology. Do use it as a **description of the official time series in the demarcated (mostly buffer/containment) zone**, which is the same zone CAMP covers.

### 6.3 Official methods — what changed, and what did not

Retrieved this session as snippets, not as a complete SOPs corpus:

- **DGR 343 / 14 Mar 2022**, *Piano d’azione per contrastare la diffusione di Xylella fastidiosa* (BURP 36, 28 Mar 2022). Three official investigation levels: (i) **zona indenne** — confirm absence, intercept new foci; (ii) **zona infetta / contenimento** — show the bacterium is confined; (iii) **zone cuscinetto** — intercept new infections originating from the outbreak/containment zone.
- Risk strata: **alto / medio / basso**. High-risk example named in the operational annex: the **400 m ring** (50–450 m) around the 50 m buffer of each plant that tested positive in the previous campaign.
- Sampling density in the 2022 piano and the 2023–2024 follow-on (Fitogest, 11 Jan 2023): **14 samples/ha or 7 samples/ha** by risk, “in line with 2021.” EU 2020/1201 BESS+ confidence/prevalence targets; the Region says it sometimes goes stricter.
- Ciervo’s own maps (FoodTimes Figs. 1–2): containment and buffer **polygons walk north** from 2013–14 through 2022–23. The sampled universe is a moving window, not a fixed panel of groves.

What we could **not** get this session: the full 2022 operational annex PDF (`cartografia.sit.puglia.it/.../All_A_181_DIR_2022_00031.pdf` was only partially extracted), the 2024–2026 piano as clean text, and emergenzaxylella.it methodology notes (JOSSO). Those belong on disk before anyone writes “the protocol changed in year Y.”

### 6.4 How to read the collapse

Two stories, both partly true; neither is licensed as *the* story yet.

**A. Real epidemiological drop on the northern front.** Vector control, 50 m felling, and a slower ST53 front are the official narrative (CORDON.md §1.3: northernmost late-March 2025 finds are seven Bari-outskirt olives, treated as hitchhiking). Boscia’s “fewer superinfections” remark is about old Salento, not about CAMP counts. A real drop in *new* northern infections is compatible with a still-devastated south that CAMP does not see.

**B. Monitoring-design change / frame shift.** CAMP never contained Lecce. As the buffer is redrawn north into lower-prevalence olive land, the same 7–14 samples/ha will return fewer positives even if nothing about ST53 biology changed. 2023 in our file is truncated at 30 June. From 2024 the Osservatorio’s attention and test budget visibly move to **ST1 / grape** (45,000 plants in one restricted oval — Cornara / Uva da Tavola). A hold-out that overlaps a target shift is not a clean temporal fold.

**What would decide.** Need, on disk: (i) samples tested **and** positives **per year × zona (cuscinetto / contenimento / indenne) × provincia**, not just CAMP olive-positive counts; (ii) hectares monitored per year (Ciervo claims this evolved); (iii) whether 2022–23 used the same host list and the same “olive” denominator; (iv) the 2023 full-year file, not 30 June. Until then, treat the collapse as **label starvation of unknown mixture**, and do not interpret a 2022–23 PR number as “the epidemic ended.”

Ciervo’s ≤0.23% is consistent with story B even if story A is also true: official effort is concentrated where expected prevalence is designed to be low.

---

## 7. ST1 near grapes — should detection pivot?

### 7.1 What is actually there

- Feb 2024, Triggiano (BA): Osservatorio announces Xf subsp. **fastidiosa ST1** (Pierce’s disease genotype) on almond, then grape, a few kilometres from the Noicattaro / Rutigliano table-grape district (Uva da Tavola, 19 May 2025; Cornara 2025; Agromillora 20 Nov 2025).
- Same season: subsp. **multiplex ST26** on the Murge. Different host set, different politics.
- Vector PCR preceded plant PCR (§4.2). California sharpshooters are absent; *P. spumarius* is treated as a secondary Pierce’s vector and still sufficed.
- Eradication is the official posture (not containment): tens of thousands of tests, ~30 ha of vineyard removed. The infected oval is small enough that eradication is still the honest word.

Olive ST53 and grape ST1 share a genus and a xylem and almost nothing else that a 10 m index can see. Tendone table grape is irrigated, dense, and spectrally a different canopy. Zarco’s almond work is the closer spectral cousin, and even that needed airborne HS + thermal + an epidemic-spread prior (Camino 2021).

### 7.2 Pivot, split, or stay?

| Option | Verdict | Why |
|---|---|---|
| Abandon the olive nowcast and retarget ST1 grape | **No.** | CAMP olive labels, SCENE_JOIN, and the northern ST53 front are a real, still-open computational object. ST1 has no open tree-level grape PCR file we hold. |
| Pretend NDMI-on-olive transfers to grape | **No.** | Different subspecies, host, canopy, irrigation, and symptomology. That would be a new one-scene join, with new falsifiers. |
| Ignore ST1 in the partner brief | **No.** | It is the live phytosanitary emergency next to Europe’s most important table-grape district. A Bari meeting that only talks olive NDMI will sound dated. |
| Split the detection stack | **Yes.** | Artifact A stays olive-ST53 / CAMP / S2, with the drought ablation and F7 symptom split. A **separate** one-pager: vector-PCR-first for ST1, no claim that CORDON can see Pierce’s from Sentinel-2 unless a grape label file appears. If CNR-IPSP says they need help ranking the Triggiano oval, that is a new Day-1, not a reuse of `scene_join_100.csv`. |

Vector PCR already did the “hidden signal” job for ST1. The nowcast’s comparative advantage is the **olive buffer**, where insect infectivity is lower and the official plant grid is coarse. Do not pivot off a dataset we have onto a dataset we do not.

---

## 8. Nulls, access failures, what is still allowed

### 8.1 Retrieval failures (this session)

| URL / object | What happened | Consequence |
|---|---|---|
| Wiley Ciervo & Scortichini 2024 full PDF | Abstract / FoodTimes secondary only | Incidence ≤0.23% and the 69.56% / felling-ratio figures are **provisional**. |
| emergenzaxylella.it | Regional JOSSO / SSO, already ACCESS_BLOCKED in DAY1 | Official polygon layer and the Osservatorio’s own “how to read the database” note unread. |
| Planetek REDoX project page | Firecrawl rate-limit | Operational status inferred from Olive Oil Times 2021 + D’Addabbo 2025 funding line + DTA listings, not from Planetek’s current product page. |
| D’Addabbo 2025 PDF (second fetch) | Rate-limit; HTML body was retrieved | OA 86.1% / 68.3% / Polignano failure from HTML, not from a local PDF. |
| `All_A_181_DIR_2022_00031.pdf` (Regione operational annex) | Partial extract | 7 vs 14/ha and the 400 m high-risk ring are cited from snippets, not from a complete SOP. |
| APS Nicolì 2019 full text | Abstract only | AzA mechanism beyond “mobile metabolite / screening” not re-read. |
| “Galván” Xylella RS paper | **Not found** as a distinct 2018–2026 hit | Do not cite. If someone has a DOI, add it. |
| Poblete 2021 and Camino 2021 full Elsevier PDFs | JRC / abstract / secondary numbers | OA 98% / κ 0.7 and OA 80% / 71% are from JRC and citing reviews, consistent across sources, but not from a local PDF. |

### 8.2 What this challenge does *not* retract

- The join path is real. CAMP lat/lon → public COG → index is closed.
- NDVI as a **single-date previsual** feature is a bad bet. Zarco 2018 already ran that funeral.
- A drought ablation on NDMI (and NDRE) is still the correct next build step. This file is the list of ways that step can fail.
- Airborne HS+thermal remains the gold-standard *physics*. CORDON should not pretend to fly a plane. It also should not pretend nobody else is flying one.

### 8.3 What this challenge does retract, or put on probation

- “NDVI is dead” as a blanket. Multi-date ARVI/OSAVI incidence monitoring is live science (Hornero 2020). Kill single-date NDVI; keep a time-series greenness ablation.
- “Airborne hyperspectral is out of reach.” REDoX reached it in 2022 over two named Apulian sites and published in 2025. Out of reach **for us without a partner** is the accurate sentence. That partner path is already in CORDON.md.
- “NDMI moved, therefore previsual at 10 m.” Not until F1–F8, especially **F7** (asymptomatic-only).
- “2022–23 is a clean hold-out of a dying epidemic.” It is a starved, design-shifted, Lecce-free, mid-year-truncated label set. Keep the spatial 2020–21 fold.
- “Stay on olive and ignore ST1.” Stay on olive for Artifact A; do not walk into CNR talking only about August 2021 NDMI.

### 8.4 Next empirical move (not another literature pass)

1. Re-open `nowcast/cache/scene_join_100.csv`, attach CAMP `SINTOMO`, irrigation proxy, and a 2021 August SPEI/SSM. Run F1, F2, F7.
2. Same 100 IDs on a 2020 August COG (F4).
3. If F7 dies, Artifact A is an **incidence** model in Hornero’s sense. Say so, and stop using the word previsual.
4. If F7 lives, *then* spend compute on the full 260/841 and the drought-only ablation.
5. Put Ciervo’s PDF and the 2022 annex on disk before anyone quotes 0.23% to a Bari postdoc.
