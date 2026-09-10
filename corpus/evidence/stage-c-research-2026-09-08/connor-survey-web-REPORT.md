# Branch 1 — survey, diagnostic and biological-timing operative methods (in actu)

Status: CHECKPOINT FINAL, 2026-09-08. Written by the Connor subagent (branch 1). Assertion set for the primary to verify; nothing here binds CORDON.

Directory layout: `REPORT.md` (this file), `sources.json` (url, sha256, retrieved_at, title, issuer, date, status for every source relied on, including pre-captured files referenced by path), `raw/` (files fetched by this branch, PDF + pdftotext `.txt`). Pre-captured files are referenced by absolute path and were not re-fetched (`/Users/owenwassmer/dev/CORDON/corpus/workbench/stage-c-research/survey-web/`, `/Users/owenwassmer/dev/CORDON/regulation/jurisdiction/{regional,national}/`).

Status vocabulary used below: BINDING ACT / INCORPORATED STANDARD (a method a binding act or adopted plan expressly adopts) / ADOPTED PLAN (DGR-approved piano d'azione or MASAF plan) / OFFICIAL GUIDANCE (EFSA, EPPO, IPPC, MASAF technical documents) / DOCUMENTED PRACTICE (what the operator demonstrably did, e.g. campaign workbooks, published counts) / SCIENTIFIC METHOD (papers, worked examples) / RECONSTRUCTION (this branch's independent recomputation).

Summary of verdicts

| Q | Topic | Verdict |
|---|---|---|
| 1 | Population model, one- vs two-stage, epidemiological unit | ESTABLISHED (by plan text + exact numerical reproduction) |
| 2 | Software/version, defaults, rounding, clipping, PNI 2026 derivation | PARTIALLY ESTABLISHED (method and every input reproduced exactly; tool version and manuals not retrievable) |
| 3 | Method sensitivity values and sources | ESTABLISHED for the value actually used (0.55 = 0.70×0.78, EFSA reference value); NOT FOUND for any Puglia-measured or pooled-sample sensitivity |
| 4 | Risk stratification and conversion of EU targets | ESTABLISHED (relative risks, bands, per-stratum allocation reproduced) |
| 5 | Rounding rule, fractional infected count, two-stage composition | PARTIALLY ESTABLISHED (no act states a rule; reproduction fixes ceil(n), D=round-half-up(p·N), within-unit confidence as second-stage sensitivity, clip-and-reallocate) |
| 6 | Cq classification, boundary values, assay, confirmation, subspecies | PARTIALLY ESTABLISHED (procedure fully documented); NOT FOUND for Cq exactly 32 / exactly 35 |
| 7 | Sampling protocol facts that change populations | ESTABLISHED |
| 8 | Flight season, "periodi opportuni", treatment windows, Nov–Mar, 48 h | PARTIALLY ESTABLISHED (operational dates by act per year; no act defines "stagione di volo" by date; DGR 1866 states adult presence "da maggio a novembre") |
| 9 | Annual survey scheduling, campaign calendars 2021–2026 | ESTABLISHED as documented practice (workbook date spans), PARTIALLY as plan text |

---

## Q1. Population model, one-stage vs two-stage, epidemiological unit

Verdict: ESTABLISHED.

### Evidence

**(a) Piano d'azione 2021 — DGR 538/2021 (ADOPTED PLAN; BURP n. 55 del 20-4-2021).** Held text `regulation/jurisdiction/regional/DGR-538-2021-plan.tesseract.txt` (tesseract OCR); also captured as `raw/piano_azione_2021_approvato.pdf` (confagricolturabari mirror, 108 466 chars pdftotext).

Area indenne, first sub-zone (lines 445–470 of the held OCR; raw txt "Tab. 3"):
> "Il piano di indagine è stato ottenuto utilizzando il tool statistico RiBESS+ con un'applicazione a due step. Il primo step è stato finalizzato ad individuare il numero di piante da campionare nell'Unità Epidemiologica identificata (macromaglia da 100 ettari) e il secondo teso a definire il numero di macromaglie da monitorare."
> Tab. 3: "Livello di confidenza 0,80 / Prevalenza 0,01 / Densità di impianto (piante/ettaro) 150 / Numero di piante specificate 73.579.800 / Unità Epidemiologiche: Maglia da 100 ettari / Numero di Unità Epidemiologiche 4.905 / Numero di piante per U.E. 735.750 / Livello di confidenza a livello di U.E. 0,50 / U.E. da campionare 126 / Piante da campionare per U.E. 317 / Totale Piante da campionare 39.942 / Piante da campionare per ettaro 7 / Numero ettari per U.E. 45".

Delimited areas (Tab. 10–11, raw txt PDF pages 20–21): unit = "Ettaro", "Piante per ettaro 150", "Livello di confidenza a livello di U.E. 0,05", "Piante da campionare per ettaro 14 (alto rischio) / 7 (rischio base)". Tab. 1: "Sensibilità del metodo 0,55"; "Campioni singoli o pool costituiti da max 7 piante/campione".

**(b) Piano d'azione 2022 — DGR 343/2022 (ADOPTED PLAN; BURP n. 36 del 28-3-2022).** Held text `DGR-343-2022-plan.txt` lines 620–700:
> "È stata utilizzata una metodologia a doppio step con la quale si è definito, con il primo step, il numero di piante da campionare in un ettaro (maglia) e con il secondo il numero di ettari (maglie) da monitorare. Il primo step si basa sull'ipotesi di avere mediamente la presenza di 150 piante per ettaro …"
> Tabella 1 (within-hectare): Cuscinetto p 0,01 / conf 0,1 / Sens 0,55 / 200 piante/ha → 19 campioni; 150 → 14; conf 0,05: 200 → 10; 150 → 7. Contenimento p 0,007 / conf 0,1: 200 → 37; 150 → 28; conf 0,05: 200 → 19; 150 → 14.
> Tab. 2 (Zona Cuscinetto, Olivi): "Livello di confidenza 0,9 / Prevalenza 0,01 / Numero di piante specificate 1.203.563 / Area a Rischio Alto 102.635 / Base 1.100.928 / Incidenza 0,0853 / 0,9147 / Unità epidemiologica Ettaro / Numero di ettari 8.023,75 (AR 684,23; RB 7.339,52) / Piante per ettaro 150 / Livello di confidenza a livello di U.E. 0,05 / Piante da campionare 29.218 (AR 4.788; RB 24.430) / Piante da campionare per ettaro 7 / Ettari da campionare 4.174 (AR 684; RB 3.490)".

**(c) Piano d'azione 2023-2024 — DGR 1866/2022 (ADOPTED PLAN; BURP n. 139 del 27-12-2022).** Held `DGR-1866-2022-plan.txt` lines 689–698:
> "si applica il RIBESS+ con i valori di prevalenza e di confidenza previsti dal Reg. (UE) 2020/1201 o se del caso più stringenti … L'applicazione del Ribess + prevede una metodologia a doppio step con la quale si definisce, con il primo step, il numero di piante da campionare in un ettaro (maglia) e con il secondo step il numero di ettari (maglie) da monitorare. Nel programma di sorveglianza 2023 e 2024, in linea con la metodologia utilizzata nel 2022, si procede al prelievo di 7/14 campioni per ettaro a seconda dei valori di rischio applicati nelle diverse zone delimitate."

**(d) Piano d'azione 2024-2026 — DGR 1593/2024 (ADOPTED PLAN).** Captured `raw/DGR_1593_2024_piano_2024-2026.pdf` (agrometeopuglia mirror). Line 1104 of the pdftotext: "L'applicazione del Ribess + prevede una metodologia ad uno step con la quale si definisce il numero di piante da campionare"; line 1180: "Si prelevano campioni pool costituiti da 7 piante/ettaro per olivo e da 4 piante/ettaro per tutte le altre specie." Tables carry "Piante per ettaro 300 / 1500 / 625 / 300" (olivi / vigneti / fruttiferi / altre). The switch from two-step to one-step therefore dates to DGR 1593/2024, not DGR 1075/2025.

**(e) Piano d'azione 2025-2027 — DGR 1075/2025 (ADOPTED PLAN; BURP n. 68 del 25-8-2025).** Held `DGR-1075-2025-plan.vision-ocr.txt` page 23–25:
> "La dimensione del campione all'interno delle aree da sottoporre a sorveglianza è determinata applicando 2 livelli di rischio: Alto (valore 2) e Base (valore 1). … L'applicazione del Ribess+ prevede una metodologia ad uno step con la quale si definisce il numero di piante da campionare nell'area interessata."
> Tabella 2 (Area indenne): "Livello di confidenza 0,95 / 0,95 / 0,95 / 0,9 / 0,99999; Prevalenza 0,0005 / 0,0009 / 0,0009 / 0,007 / 0,0001; Numero di piante specificate 59.362.059 / 109.955.160 / 17.607.769 / 48.315.879 / 235.240.867; Area a Rischio Alto 990.804 / 2.109.000 / 568.331 / 641.688; Area a Rischio Base 58.371.255 / 107.846.160 / 17.039.438 / 47.674.191; Incidenza sul totale AR 0,016690863 / 0,019180546 / 0,032277301 / 0,0132811; Unità epidemiologica Ettaro; Numero di ettari 197.873,53 / 73.303,44 / 28.172,43 / 161.052,93; Piante per ettaro 300 / 1500 / 625 / 300; Piante da campionare 8.302 / 4.625 / 4.683 / 454 (AR 2.765 / 1.541 / 1.560 / 151; RB 5.537 / 3.084 / 3.123 / 303)."
> Tabella 3 (zona infetta contenimento): conf 0,95 / prevalence 0,0003 (olivi), 0,005 (vigneti), 0,0007 (fruttiferi), 0,005 (altre). Tabella 4 (zona cuscinetto): same prevalence set.

**(f) PNI 2026 workbook (national programme; ADOPTED PLAN, CFN opinion 13-11-2025 per Piemonte attestation).** Held `regulation/jurisdiction/national/PNI-2026/xylella-ripest.xlsx` rows 138–146 (extracted text `xylella-ripest.txt`): G138=197873.53 ha, H138=59362059 plants, U138=0.98330913690173727, U139=0.016690863098262815, T=1/2, O=0.7, P=0.78, AC=0.95, AD=0.0005, X=5537/2765, AA=791/395; comment AF138: "Il disegno di indagine è stato sviluppato applicando lo strumento RiPEST, e come fattore di rischio è stata considerata la distanza di 1 km intorno alle aree delimitate, utilizzando un design prevalence differente nelle diverse unità epidemiologiche. Il livello di confidenza totale ottenuto nel territorio è lo 0.99." Row 146 (authorized sites): "Popolazione infinita … Per l'unità epidemiologica 'luoghi di produzione', l'unità di misura è il numero di vivai/serre investigati (Operatore Professionale iscritto al RUOP), che contano una popolazione di piante infinita", C=0.8, p=0.01, 292 samples / 60 tests.

The PNI 2026 Puglia rows are numerically identical to DGR 1075/2025 Tabella 2 (populations, stratum proportions to 9 decimals, counts). The workbook's own comment names RiPEST; DGR 1075 names RiBESS+.

**(g) EFSA general guidelines EN-9788 (2025) (OFFICIAL GUIDANCE; pre-captured `survey-web/efsa9788.pdf`).** §5.8 (p. 37): "the estimated sample size for an unknown (statistically infinite – binomial distribution) target population size compares to a known target population size (finite population – hypergeometric distribution) … both curves converge around 15,000 host plants on approximately 370 samples … when information about the size of the target population is lacking, the sample size can be estimated using the binomial distribution." Line 2128–2129: in a two-step design "This confidence level at field level is considered as the method sensitivity of the [next level]". EN-1873 (2020) Appendix C (`raw/efsa_EN-1873_2020_xylella_guidelines.txt` from line 3552) is the Xylella-specific two-step worked example: "an extreme case would be to consider each hectare that contains at least one host plant of X. fastidiosa as an independent epidemiological unit"; C.2.2 "95% confidence level with a design prevalence of 0.4% … In an orchard with 300 host trees"; C.2.3 "0.55 has been used as the reference value".

### Reconstruction (RECONSTRUCTION; scripts run in this session, code reproduced in `sources.json` notes)

One-stage (DGR 1075 Tabella 2 = PNI 2026), per stratum i with N_i plants, RR_i ∈ {1,2}, q_i = N_i/N, p_i = p·RR_i/Σ_j q_j RR_j, sensitivity s, target per stratum C_i = 1−(1−C)^(1/2), hypergeometric detection with D_i = round-half-up(p_i·N_i), n_i = least integer meeting C_i:

| row | published base/high | binomial s=0.546 | hyper s=0.546 (round) | binomial s=0.55 | hyper s=0.55 D=floor | **hyper s=0.55 D=round** | hyper s=0.55 D=ceil |
|---|---|---|---|---|---|---|---|
| Olea 0.95/0.0005 | 5537/2765 | 5578/2789 | 5578/2785 | 5537/2769 | 5537/2768 | **5537/2765** | 5537/2765 |
| Vitis 0.95/0.0009 | 3084/1541 | 3106/1553 | 3106/1553 | 3084/1542 | 3084/1542 | **3084/1541** | 3084/1541 |
| Prunus/Citrus 0.95/0.0009 | 3123/1560 | 3146/1573 | 3146/1572 | 3123/1562 | 3123/1560 | **3123/1560** | 3123/1559 |
| Altre 0.90/0.007 | 303/151 | 305/153 | 305/153 | 303/151 | 303/151 | **303/151** | 303/151 |
| Authorized sites (infinite, 0.8/0.01) | 292 | 294 | — | **292** | — | — | — |

All eight stratum counts and the infinite-population count are reproduced only by: s = 0.55 (not 0.7×0.78 = 0.546), finite hypergeometric per stratum, D = round-half-up(p_i·N_i), equal per-stratum target confidence, ceiling to the least sufficient integer. The achieved per-stratum confidence is ≈0.776 each; global 1−Π(1−C_i) ≈ 0.95; the workbook's "0.99" total is not reproduced by this composition (see Q5 gaps).

Two-stage within-hectare (DGR 343/2022 Tabella 1, s = 0.55): hypergeometric with N ∈ {200,150}, D = round-half-up(p·N) reproduces all eight cells (19, 14, 10, 7; 37, 28, 19, 14). floor fails at p·N = 1.5 (gives 28 and 14 instead of 14 and 7); ceil fails at p·N = 1.4 and 1.05 (gives 19/14/10/7 instead of 37/28/19/14). Round-half-up is therefore the only convention consistent with the published table.

Two-stage second step (DGR 343/2022 Tab. 2, Olivi, cuscinetto): unit = hectare, N_h = 684, N_b = 7 339/7 340, sensitivity of a hectare = within-unit confidence 0.05, p = 0.01, RR 2/1, target 0.9. The high stratum cannot reach its equal-allocation target even when every hectare is sampled (max confidence 0.4867); the published allocation samples all 684 ha and puts 3 490 ha in the base stratum; the residual-confidence recomputation (1−0.1/(1−0.4867) = 0.8052 in the base stratum) gives 3 489 ha. This is the observable clipping behaviour: the tool caps a stratum at its population and moves the residual confidence to the other stratum; it does not declare the capped stratum's target met.

### Implication for the computation

- Operative unit for the one-stage design is the plant, with the hectare used only as the allocation grid ("Unità epidemiologica: Ettaro", pools per hectare). Under DGR 538/343/1866 the hectare (or 100-ha macromaglia in 2021 area indenne) is the epidemiological unit of a genuine two-stage design whose first stage has confidence 0.05/0.10/0.50 and whose second stage treats that confidence as the unit sensitivity.
- Finite hypergeometric is the operative kernel at both stages (populations of 10^2 within a hectare, 10^5–10^8 at territory level); binomial gives the same territory-level counts only to within ~0.5 %, which is enough to flip the published integer.
- The switch to one-step is dated DGR 1593/2024 (Piano 2024-2026), maintained by DGR 1075/2025.

### Gaps / boundary

- No act states the kernel explicitly; the kernel is established by reproduction and by EFSA's description of the tool. RiBESS+/RiPEST manuals could not be retrieved (Zenodo 403/504 from this network; see Q2).
- DGR 1075 Tabella 3 and 4 numbers are partially lost to OCR (mojibake); only parameter rows were readable. Not re-derived.
- Searched: BURP (DGR 538/343/1866/1593/1075 texts held), emergenzaxylella.it (portal is a Liferay SPA; documents reached through mirrors), protezionedellepiante.it (PNI 2026), EFSA Knowledge Junction (Zenodo — blocked), EFSA journal (Wiley — 403), JKI mirror (EN-1873 obtained).

---

## Q2. Software and version; defaults; rounding; clipping; PNI 2026 derivation

Verdict: PARTIALLY ESTABLISHED.

### Evidence

- RiBESS+ named by every Puglia plan 2021–2025 (Q1 quotes); glossary DGR 1866 (u) and DGR 1075 (w): "RiBESS +: strumento statistico che calcola la dimensione del campione basato sull'analisi del rischio".
- RiPEST named by the PNI 2026 workbook comment (Q1(f)) and by DM 348260/2026 §5.1 (ADOPTED NATIONAL PLAN, held `national/DM-348260-2026-Xylella-plan.txt` lines 857–868): "l'EFSA predispone e aggiorna modelli statistici (attualmente rappresentati dal software statistico RiPEST) per il calcolo della dimensione del campione … Sensibilità del metodo: … Combina l'efficacia del campionamento e i valori di sensibilità diagnostica. … Fattori di rischio: … quantificati per mezzo del loro rischio relativo e della proporzione della popolazione target a cui si applicano." Lines 909–912: "Poiché gli attuali modelli statistici dell'EFSA non forniscono indicazioni sulla distribuzione del campione, ai fini di una distribuzione omogenea dello stesso, le Unità Epidemiologiche andranno ulteriormente suddivise, utilizzando ad esempio una griglia di adeguate dimensioni."
- EFSA EN-9411 (2025, RiPEST Webinar 2, 2 Dec 2024; OFFICIAL GUIDANCE; search snippet, DOI page 403 to curl/Crawl4AI): "RiPEST 2.0 tool … Yes, RiPEST is a standalone application and it can be used separately from RiBESS. The underlying formulas for calculating the sample size are exactly the same in both applications."
- RiPEST releases (Zenodo metadata via search only): 10.5281/zenodo.8335473 published 2023-09-11 (Bemelmans, Cortiñas Abrahantes, Kaluski, Verbeke); 10.5281/zenodo.17701334 published 2025-11-18 (adds Junius); concept DOI 10.5281/zenodo.8335472 latest 2026-03-06. RiBESS+: 10.5281/zenodo.2541541 / 664465 (2016-11-17), "extends the features of the risk based estimate of system sensitivity tool (EFSA, 2012)". EFSA WG minutes (pre-captured `survey-web/efsa-wg-minutes.txt` line 1992): "The RiPEST tool pre-filled values are now synchronised with the database: Diagnostic sensitivity, sampling time, and relative risk."
- Formula family (OFFICIAL GUIDANCE / SCIENTIFIC METHOD): EN-9788 §5.8 (binomial vs hypergeometric, Q1(g)); Table 7 example (C 95 %, p 1 %, N 1 000 000, s 80 % → 373); §on risk factors: "RiPEST and RiBESS+ will aim to ensure the same confidence across all risk categories. Fewer samples are needed to reach this confidence in the high-risk area." Adjusted-risk formula AR_i = RR_i/Σ(RR·PPr), EPI = P*·AR: `raw/epitools_formulae.pdf` (Ausvet; the RiBESS lineage is Martin, Cameron & Greiner 2007).

### Reconstruction of the PNI 2026 Puglia rows

Inputs actually used (established by identity with DGR 1075 Tabella 2 and by exact reproduction, Q1): population = plants per hectare × hectares from AGEA land use (300 olive, 1 500 vine, 625 fruit, 300 other); one risk factor, two levels, RR 2 for "1 km di area libera attorno alle aree delimitate" (PNI) = DGR 1075 "zona esterna, larga 1 km, a partire dal confine di ogni zona cuscinetto" (+ 1 km on the Basilicata border, Canosa ex-focolaio, per DGR 1866 §4.2.4), RR 1 elsewhere; proportion of population in the high level = N_high/N (0.016690863 etc.); confidence 0.95 (olive, vine, fruit), 0.90 (spontaneous), 0.80 (authorized sites); design prevalence 0.0005 (olive), 0.0009 (vine, Prunus/Citrus), 0.007 (spontaneous), 0.01 (authorized sites); method sensitivity entered as 0.7 and 0.78 in the workbook but the counts correspond to 0.55 (Q3); pooling ratio: tests = ceil(samples/7) for olive (5537/7 → 791; 2765/7 → 395), ceil(samples/4) for all other species (3123/4 → 781; 1560/4 → 390; 3084/4 → 771; 1541/4 → 386; 303/4 → 76; 151/4 → 38); authorized sites 292/60 (ratio 4.87, not explained by either rule — NOT FOUND).

Defaults observed: equal-target allocation across risk levels (not convenience sampling); ceiling to integer; D = round-half-up(p_i·N_i); finite branch used whenever N is entered; infinite branch used for authorized sites ("Popolazione infinita").

Clipping: DGR 343/2022 Tab. 2 shows a stratum capped at its whole population (684 of 684.23 ha) with the residual confidence loaded on the other stratum (Q1 reconstruction: 3 489 vs published 3 490). No stratum is reported as "achieved" when capped.

### Gaps / boundary

- Which RiPEST/RiBESS+ build produced the numbers is NOT FOUND (no version string in DGR 1075 or the PNI workbook; file name suffix `20251002` is the workbook date). Manuals (RiBESS+ manual, RiPEST manual Bemelmans et al. 2023) NOT RETRIEVED: `zenodo.org` returned HTTP 403 to curl (all UAs) and 504 to Crawl4AI; the browser tool had no CDP endpoint. EFSA r4eu app is a login SPA ("Loading…", pre-captured `ripest-live.html`). The Wiley EFSA journal returns 403.
- Whether the product 0.546 is rounded to 0.55 by the tool or 0.55 was entered directly is not determinable from public sources (Q3).
- The workbook's "confidenza totale 0.99" is not reproduced (Q5).

---

## Q3. Method sensitivity values actually used; pooled-sample sensitivity; sources

Verdict: ESTABLISHED for the value used (0.55); NOT FOUND for any Puglia-measured value or any pooling adjustment.

### Evidence

- EFSA EN-1873 (2020) §2.3 (OFFICIAL GUIDANCE; `raw/efsa_EN-1873_2020_xylella_guidelines.txt` lines 796–807): "For the case studies in this document an average sampling effectiveness of 0.70 has been applied. … For example, when using a specific PCR method on olive samples this value is estimated at 0.67, while for Polygala samples it is set at 0.90 when using the same PCR method. For the case studies in this document a diagnostic sensitivity of 0.78 has been applied to reflect a hypothetical host that would be in between these matrices. … Method sensitivity = sampling effectiveness × diagnostic sensitivity = 0.70 × 0.78 = 0.55, thus 0.55 can be considered as a reference value." Table 1 and Appendix C use 0.55; Figure 2 screenshot "method sensitivity of 55%".
- Puglia plans (ADOPTED PLANS): DGR 538/2021 Tab. 1 "Sensibilità del metodo 0,55"; DGR 343/2022 Tabella 1 "Sensibilità del metodo 0,55" for every row. DGR 1866/2022, 1593/2024, 1075/2025: no sensitivity row in the readable text; PNI 2026 columns O = 0.7, P = 0.78 for every Puglia row.
- Reproduction (Q1): the 2025/2026 counts correspond to s = 0.55, not 0.546.
- EFSA Pest Survey Card (2019 EN-1667 PDF `raw/efsa_pest_survey_card_xylella_2019.pdf` §2.3.3; and the current storymap JSON pre-captured `survey-web/efsa-card-extracted.txt` lines 427–441): "Method sensitivity = sampling effectiveness × diagnostic sensitivity"; "a diagnostic sensitivity of 100% is obtained … when four leaf petioles of infected olive leaves are pooled with 20 g (= 800-900 pieces) of leaf petioles from healthy trees, followed by the CTAB method for DNA extraction and the real-time PCR method of Harper et al. (2010, erratum 2013) … sampling four leaf petioles from 200 trees, one infected tree would still give a positive test result"; "using the QuickPick Plant DNA kit and the KingFisher … on spiked olive petioles and the same real-time PCR method of Harper … resulted in a diagnostic sensitivity of 67%. When the same method was applied to petioles of Vitis vinifera the diagnostic sensitivity was 94%."
- EPPO PM 7/24 (4) 2023 (OFFICIAL GUIDANCE; pre-captured `survey-web/eppo-pm7-revised.txt` lines 2170–2190, test-performance-study table): "Diagnostic sensitivity % 60.42 / 95.54 / 56.25 / 79.17 … Accuracy % (restricted series) 78.33 / 97.44 / 66.67 / 86.11". No EPPO table gives 0.78 as a diagnostic sensitivity for Harper on olive.
- Belgium FPS report (DOCUMENTED PRACTICE of another MS; `raw/belgium_fps_xylella_survey_design.html`): "an average sampling effectiveness of 70 % was chosen, and an average diagnostic sensitivity of 78 % was assumed. The overall method sensitivity … was thus estimated at 55 % (70 % x 78 %)"; "it is possible to confidently detect 1 infected plant when pooled with up to 49 healthy plants."
- EN-10065 (2026) (pre-captured `survey-web/efsa10065.clean.txt` lines 784–786): "For some pests such as … Xylella fastidiosa, method sensitivity is assessed through the sampling of asymptomatic plant materials". The document announces an EKE-based Pest Survey Report for X. fastidiosa; no numbers for Xylella in the captured text.
- DDS 45/2025 (BINDING ACT, procedure; held `181_DIR_2025_00045.txt` lines 1398–1405) gives the rationale for tissue choice, not a number: "si evince la necessità di prelevare i tessuti da saggiare da almeno 4 rametti lignificati, e di utilizzare porzioni di ramo piuttosto che tessuti fogliari, che permettono di ottenere (soprattutto per le cultivar resistenti) valori di sensibilità diagnostica più elevati."

### Implication

- The operative method sensitivity in Puglia since 2021 is the EFSA reference value 0.55, a hypothetical-host illustration adopted as a plan input, with no Puglia validation and no pooled-sample discount. The PNI 2026's 0.7/0.78 are the same value split into its EFSA components.
- No source applies a pooling correction: the pool of 7 (olive) or 4 (others) plants is treated as 7 (4) independently inspected plants with sensitivity 0.55 each; the EFSA card's 100 % detection at 1:200 petiole dilution (CTAB + Harper) is the only evidence that pooling at 1:7 does not lower diagnostic sensitivity.

### Gaps / boundary

- No published Puglia-lab diagnostic-sensitivity value; the October 2024 ring test cited by DDS 45 ("tenendo conto del risultato del ring test effettuato a ottobre 2024") is not published. EURL Hodgetts specificity/sensitivity report is pre-captured (`survey-web/eurl-hodgetts.txt`) but concerns the Hodgetts subspecies assay.
- Searched: EFSA card (both versions), EN-1873, EN-9788, EN-10065, EFSA WG minutes (grep "0.78", "Xylella … sensitivity": no hit), EPPO PM 7/24 (4), Belgium FPS, Zenodo poster 10.5281/zenodo.4682148 (abstract only).

---

## Q4. Risk stratification actually applied; conversion of Article 2/5/6/10/15 targets

Verdict: ESTABLISHED.

### Evidence (ADOPTED PLANS)

- 2021 (DGR 538): "il piano di monitoraggio attribuisce un fattore di rischio doppio rispetto a quello base, alle porzioni di territorio localizzate entro i 400 metri dalla zona infetta"; delimited-area tables give "Piante da campionare per ettaro (alto rischio) 14 / (rischio base) 7" and "% ettari da campionare (alto rischio) 99–100 %".
- 2022 (DGR 343 §4.1.1): "AR – valore di rischio 2 nell'area larga 400 m al confine con la zona contenimento dallo Jonio all'Adriatico; RB – restante area"; 684.23 ha = 8.5 % of the olive area.
- 2023-2024 (DGR 1866 §4.2, lines 632–634, 710–748): "La dimensione del campione … viene determinata applicando 3 livelli di rischio: Alto (valore 2), medio (valore 1,5) e basso (valore 1)"; containment zone: "Alto Rischio – valore di rischio 2 nell'area larga 400 m (da 50 a 450 m) intorno al buffer di 50 m di ciascuna pianta risultata infetta nel monitoraggio 2022; Medio Rischio – valore di rischio 1,5 nell'area larga 400 m (da 450m a 850m) …; Basso Rischio – valore di rischio 1 nella restante zona"; Valle d'Itria infected zone: "Alto Rischio – valore di rischio 2 nell'area larga 400 m al confine con la zona contenimento … valore 2 nelle aree di 100 m lungo le strade di grande percorrenza … Medio 1,5 nella restante area"; area indenne: "Alto Rischio – valore 2 nell'area di 1 km dei comuni limitrofi alla regione Basilicata; Medio 1,5 nell'area di 1 km attorno all'ex focolaio di Canosa; Basso 1 nella restante area".
- 2025-2027 (DGR 1075 §4.1.1–4.1.4): two levels 2/1; "L'ampiezza delle aree potenzialmente infette è determinata considerando un'area larga 400 m intorno al buffer di 50 m di raggio di ciascuna pianta risultata infetta nella campagna di monitoraggio dell'anno precedente (da 50 a 450 m). Tale area larga 400 metri è considerata ad alto rischio"; area indenne: "Alto Rischio – valore di rischio 2 nella zona esterna, larga 1 km, a partire dal confine di ogni zona cuscinetto; Rischio base – valore di rischio 1 nella restante zona indenne"; cuscinetto: "valore di rischio 2 nell'area larga 400 m dal confine della zona cuscinetto dallo Jonio all'Adriatico; … 400 m attorno ad eventuali piante infette rilevate nell'anno precedente".
- Confidence/prevalence actually set versus EU floors (DGR 1075 Tabelle 2–4): area indenne olive 0.95/0.0005, vine and fruit 0.95/0.0009, spontaneous 0.90/0.007, authorized sites 0.80/0.01 (EU Art. 2(4): 80 %/1 %); containment infected zone olive 0.95/0.0003, vine 0.95/0.005, fruit 0.95/0.0007, other 0.90/0.005 (EU Art. 15(2): 90 %/0.7 %); cuscinetto same prevalence set (EU Art. 15(4)/10: 90 %/1 %). DGR 1866: "con i valori di prevalenza e di confidenza previsti dal Reg. (UE) 2020/1201 o se del caso più stringenti". DM 348260/2026 §9.3 restates the EU floors verbatim in Italian: "rilevare un tasso di presenza di piante infette dello 0,5% con un livello di confidenza almeno del 90% … dell'1% … considerando che i primi 400 m attorno alle zone infette presentano un livello di rischio più elevato … dello 0,7% …".
- Post-finding enhanced surveillance (not statistical): DGR 1866 §4.3: "in una terza area di larghezza pari a 400 m attorno alla seconda area, tutti gli ettari con specie specificate … sono sottoposti a sorveglianza rafforzata, prelevando 14 campioni/ettaro"; DGR 1075 §4.2.1: "nell'area di larghezza pari a 400 m attorno all'area infetta, tutti gli ettari con specie specificate alla sottospecie rinvenuta, sono sottoposti a sorveglianza. … Per ritrovamenti in area indenne, successivamente alla sorveglianza nei 400 m, … si procede andando a sottoporre a sorveglianza tutti gli ettari … partendo dai confini della zona cuscinetto verso la zona infetta. In caso di individuazione di nuovi positivi il processo viene ripetuto in maniera ricorsiva … Una volta definiti i confini dell'area delimitata, nella successiva campagna di monitoraggio vengono stabiliti i livelli di rischio e si procede con il campionamento su base statistica."

### Conversion actually performed (reconstruction, Q1)

Per stratum: p_i = p·RR_i/(q_base + 2·q_high [+1.5·q_medium]); C_i = 1−(1−C)^(1/k); n_i = least integer with hypergeometric detection ≥ C_i. Effect of RR 2: the 400 m / 1 km band receives ≈ half the base count for ≈ 1.7–3.2 % of the population, i.e. ≈ 30-fold higher sampling density (DGR 1075 Tabella 2: 2 765 of 8 302 olive samples on 990 804 of 59 362 059 plants).

### Implication

- The EU "first 400 m has a higher risk" is operationalised as RR = 2 (never a different number), applied to a 400 m band measured from the 50 m infected-zone buffer around each previous-campaign infected plant (50–450 m); in 2023–2024 a second 400 m band (450–850 m) carried RR 1.5.
- EU targets are floors: the plan's own stricter values, not the EU numbers, are the inputs to the count.

### Gaps

- The area-indenne "1 km" band (PNI/DGR 1075) has no EU anchor; it is a regional risk choice.
- The multi-level (1.5) scheme is historical (2023–2024 only).

---

## Q5. Rounding rule, fractional implied infected count, composition of two-stage confidence

Verdict: PARTIALLY ESTABLISHED (by reproduction, not by text).

- No Puglia act, national plan or EFSA document found states a rounding rule ("arrotond", "rounded", "integer" — no hit in DGR 538/343/1866/1075, DM 348260, EN-1873, EN-9788).
- Reproduction (Q1): sample count = least integer meeting the target (ceiling of the real root); infected count in the finite branch D = round-half-up(p·N) — uniquely determined by DGR 343/2022 Tabella 1 (1.5 → 2; 1.4 → 1; 1.05 → 1) and consistent with all 2025 strata (974.54 → 975 needed for 2765; 991.0 → 991).
- Two-stage composition: DGR 538/343 tables label the first stage "Livello di confidenza a livello di U.E." (0.05, 0.10, 0.50) and the second stage uses that value as the hectare's sensitivity (EN-9788: "This confidence level at field level is considered as the method sensitivity"); numbers of hectares then follow from the hypergeometric on hectares (Q1: 3 489 vs 3 490). Multiplying plants × hectares gives workload only (29 218 plants = 4 174 ha × 7).
- Global confidence across strata: 1−Π(1−C_i) ≈ 0.95 with equal targets. The PNI comment "confidenza totale … 0.99" and the "TOTALE" column of DGR 1075 Tabella 2 (0.99999 / 0.0001) are not reproduced by this composition; they may be the tool's report of a territory-level statement at a different design prevalence (0.0001 over 235 240 867 plants). NOT FOUND.
- Clipping: capped stratum → residual confidence reallocated (Q1). The kernel never reports the capped stratum as achieving its target.

Implication for C: the recorded method decision on prevalence-to-integer can be bound to "round-half-up(p·N)" as the operative Puglia convention (documented practice reproduced across 2022 and 2025), while the EU floor test should use the exact real-valued kernel; a fractional D is never used by the tool.

---

## Q6. Cq classification (DDS 31/2022, DDS 45/2025), boundary handling, assay, confirmation, subspecies, CNR-IPSP

Verdict: PARTIALLY ESTABLISHED; NOT FOUND for Cq exactly 32 and exactly 35.

### Evidence

**DDS 31/2022 (BINDING ACT; held `All_A_181_DIR_2022_00031.txt` lines 1036–1075):**
> "In Puglia, per uniformare i risultati dei diversi laboratori e tenendo conto dei ring test effettuati a ottobre 2020, i laboratori effettueranno le analisi molecolari applicando: PCR in tempo reale sulla base di Harper et al., 2010 (e erratum 2013). Al fine di armonizzare l'interpretazione dei risultati, qui di seguito si forniscono dei criteri generali di riferimento per l'interpretazione dei valori ottenuti dalle reazioni di real time PCR: Cq< 32: 'Positivo'; Cq>32: 'Dubbio' da sottoporre ad ulteriori verifiche; Cq=nessun valore, 'Negativo'. È importante sottolineare che tali indicazioni sono generiche e vanno adattate alle risultanze ottenute per ogni singolo saggio real time PCR, es. considerando i valori ottenuti e generati nei controlli (negativo, positivo, senza DNA target) inseriti in ogni saggio real time PCR. In caso di risultato dubbio, il laboratorio procede dapprima a sottoporre lo stesso estratto ad un ulteriore verifica in real time PCR utilizzando nuovamente il saggio di Harper et al. (2010) oppure il saggio di Ouyang et al. (2013) … Qualora da questa ripetizione in tutte le repliche (pozzetti della piastra real time) del saggio real time PCR, il campione generi valori di 'Cq' compresi fra 32 e 35, si procede dapprima ad una nuova estrazione del campione come 'campione pool', e successivamente ove il risultato sia ancora dubbio si procede al saggio dei singoli campioni del pool."
> Positive pool: "ZONA CONTENIMENTO - il laboratorio procede ad analizzare singolarmente i campioni …; ZONA INDENNE O CUSCINETTO - il campione pool, comprensivo delle 7 buste dei campioni singoli, è consegnato prima possibile al CNR-IPSP, che procede all'analisi dei singoli campioni … e all'identificazione della sottospecie"; CNR reports "entro massimo 5" working days.

**DDS 45/2025 (BINDING ACT; held `181_DIR_2025_00045.txt` lines 1494–1581):**
> "In Puglia, per uniformare i risultati dei diversi laboratori e tenendo conto del risultato del ring test effettuato a ottobre 2024, i laboratori effettuano le analisi molecolari applicando: PCR in tempo reale sulla base di Harper et al., 2010 (e erratum 2013). … Cq< 32: 'Positivo'; Cq>32 e < 35: 'Dubbio' da sottoporre ad ulteriori verifiche; Cq> 35: nessun valore, 'Negativo'. In caso di risultato dubbio, il laboratorio procede dapprima a sottoporre lo stesso campione vegetale ad un ulteriore estrazione e verifica in real time PCR utilizzando nuovamente il saggio di Harper et al. (2010). Qualora da questa ripetizione del saggio real time PCR per i campioni pool si ottiene nuovamente esito dubbio, si procede al saggio dei singoli campioni del pool. Nel caso in cui anche il campione singolo generi un risultato dubbio, i laboratori del saggio di primo livello … inviano il campione vegetale al laboratorio del CNR-IPSP che procede a saggiare il singolo campione in aliquote (o subcampioni). Se una o più delle aliquote processate generi ancora un risultato dubbio in real time PCR, ne viene data comunicazione al SFR e l'esito caricato sul database. In tal caso la pianta dovrà essere ricampionata."
> Positive pool: "ZONA CONTENIMENTO e CUSCINETTO - il laboratorio procede ad analizzare singolarmente i campioni delle 7/4 buste per individuare la pianta o le piante infette. Tutti i campioni singoli positivi sono consegnati al CNR-IPSP per l'identificazione della sottospecie, utilizzando il protocollo qPCR descritto da Dupas et al. (2019) come previsto nel Reg. (UE) 2024/2507 …; ZONA INDENNE - … consegnati al CNR-IPSP che procede all'identificazione della sottospecie dapprima con il protocollo qPCR descritto da Dupas et al. (2019) e successivamente mediante analisi MLST … Yuan et al. (2010)". New host species: MLST. Deadlines: "7 giorni lavorativi dal ricevimento dei campioni, per i campioni risultati positivi; 10 gg lavorativi … negativi"; "I campioni positivi devono essere inviati con sollecitudine al CNR -IPSP che effettua l'analisi e comunica il risultato entro massimo tre giorni lavorativi"; "I rapporti di prova dei campioni risultati positivi del IPSP - CNR sono pubblicati sul sito emergenzaxylella.it."

**Reg. (EU) 2020/1201 Art. 2(6) (BINDING ACT; held consolidation):** "In case of positive results detected in areas other than the demarcated areas, the presence of the specified pest shall be confirmed by one more positive molecular test listed in that Annex, targeting different parts of the genome. Those tests shall be performed on the same plant sample or, if appropriate for the molecular confirmatory test used, on the same plant extract."

**DTU 39 rev.1 (OFFICIAL GUIDANCE, national survey sheet; held `national/DTU-39-Xylella-rev1.txt` lines 745–770):** "Per campioni provenienti da aree delimitate non è richiesto alcun saggio di conferma. Indipendentemente dalla zona di provenienza del campione, il metodo di prova può produrre risultati inconclusivi o dubbi; in tali casi è necessario procedere alla ripetizione dell'analisi utilizzando lo stesso metodo di prova. Qualora il risultato della seconda analisi sia: positivo, l'analisi deve essere confermata applicando un metodo di prova diretto a parti diverse del genoma; negativo, il campione viene assegnato con 'X. fastidiosa non rilevata/assente'; inconclusivo, si procede ove possibile ad un nuovo campionamento, oppure ad una nuova analisi sullo stesso campione vegetale o … sullo stesso estratto vegetale … Qualora il risultato delle analisi producesse nuovamente un risultato inconclusivo il campione sarà considerato come 'X. fastidiosa non rilevata/assente'." Test list: "Real Time PCR EPPO PM 7/24 Appendice 5 (sulla base di Harper et al., 2010, erratum 2013) e Appendice 7 (Ouyang et al., 2013)"; subspecies: MLST App. 16, Pooler & Hartung App. 18, Hernandez-Martinez App. 19, Dupas App. 10, Hodgetts App. 11.

**EPPO PM 7/24 (4) 2023 Appendix 5 (Harper) (OFFICIAL GUIDANCE; pre-captured `survey-web/eppo-pm7-revised.txt` lines 1920–1936):** "A test will be considered positive if it produces an exponential amplification curve. A test will be considered negative if it does not produce an amplification curve or if it produces a curve which is not exponential. Tests should be repeated if any contradictory or unclear results are obtained. Comment: some laboratories have noted the occurrence of late Ct values (above 38) with this test. Such cases should be considered as inconclusive. Retesting and/or re-sampling are recommended." No numeric Cq cut-off is set by the standard.

**DTU 8 rev.2 (held `national/DTU-8-rev2-2025-01-07.txt`)**: no Cq or threshold rule (grep "Cq|soglia|threshold": no hit). DM 169819/2022 (laboratories): no Cq rule.

### What happens at exactly 32 and exactly 35

NOT FOUND. Both regional procedures use strict inequalities on both sides ("Cq< 32", "Cq>32 e < 35", "Cq> 35"), so Cq = 32.00 and Cq = 35.00 belong to no class in the text; the escalation clause of DDS 31 uses the inclusive phrase "compresi fra 32 e 35". DDS 31 itself says the criteria are "generiche e vanno adattate alle risultanze ottenute per ogni singolo saggio", which delegates the boundary to the laboratory's controls. EPPO gives no cut-off. No lab SOP (Accredia-accredited method descriptions of CNR-IPSP, Agritest, Loewe/other regional labs) is public. The repeat route de facto absorbs the boundary: any value that is not "< 32" is re-tested (new extraction + Harper), and a persistent doubtful result ends in resampling (DDS 45) or "non rilevata" (DTU 39, after two inconclusives).

### Implication

- C's Cq classifier must keep 32 and 35 unresolved as B records; the procedure supplies a deterministic *route* for any non-positive value (repeat → singles → CNR aliquots → resample) whose end state is decided by later tests, not by the boundary value.
- The confirmation-on-a-second-genome-region duty (Art. 2(6), DTU 39) is satisfied in Puglia through the CNR-IPSP subspecies qPCR (Dupas 2019) on every positive from pest-free/buffer zones; DDS 45 does not name Art. 2(6) but its flow performs it. In demarcated areas no confirmation is required (DTU 39).
- DDS 45's ">35 negativo" is stricter than EPPO's ">38 inconclusive"; DDS 31 had no upper bound (">32 dubbio").

### Gaps / boundary

- Searched: DDS 31/2022, DDS 45/2025 full text; DTU 39 rev.1; DTU 8 rev.2; DM 169819/2022; EPPO PM 7/24 (4) (pre-captured revised text); IPPC DP 25 (pre-captured; not re-read for Cq); Harper 2010 + 2013 erratum (citation only; the erratum corrects the reverse primer sequence — not fetched; SCIENTIFIC METHOD); no public CNR-IPSP/Agritest SOP found (query "Accredia metodo Xylella Cq 32 35 laboratorio"; not run to exhaustion — reported as boundary).

---

## Q7. Sampling protocol facts that change populations

Verdict: ESTABLISHED.

- Pool size: DDS 45/2025 (lines 1380–1430, 1460–1475): "Bustone (CODICE CAMPIONE POOL) (max 7 buste con i campioni della stessa specie e raccolti nella stessa maglia)"; "Campione vegetale pool (pool di 4/7 campioni)"; "il laboratorio procede ad analizzare singolarmente i campioni delle 7/4 buste". DGR 1075 (page 25): "Si prelevano campioni pool costituiti da 7 piante/ettaro per olivo e da 4 piante/ettaro per tutte le altre specie. In caso di presenza di piante sintomatiche si prelevano campioni singoli; in caso di impianti consociati si prelevano campioni pool dalla specie prevalente." DGR 1866 §4.2 and DDS 31 (lines 637–651): "campionamento di 7 oppure 14 piante che costituiscono i/il campione/i pool. Le piante devono essere scelte casualmente …; In una maglia in cui sono prelevati 14 campioni, si costituiscono 2 campioni pool distinti."; "In caso di oliveti in cui sono presenti numerosi ulivi sintomatici, si prelevano campioni singoli da 7 olivi sintomatici".
- Symptomatic vs asymptomatic (DDS 45 lines 1160–1200): "Per le piante con sintomatologia lieve o conclamata bisogna campionare nei settori della chioma che mostrano sintomi …; Per le piante asintomatiche bisogna campionare esclusivamente con l'uso dello svettatoio dalla parte alta della chioma prelevando almeno 4 rametti lungo l'intera circonferenza in corrispondenza dei quattro punti cardinali"; single sample: "sulle piante sintomatiche … Si rammenta che in tal caso il campione singolo non sarà utilizzato per costituire un campione pool. In caso di necessità di campionare un olivo asintomatico, … almeno 8 rametti"; excluded: recently hard-pruned plants, suckers.
- Laboratory pooling (not field pooling): the 7 bags stay sealed; the lab cuts 4 portions per twig → "28 porzioni di ramo (ca. 1,2-2 grammi)"; "Il restante materiale vegetale presente nelle 7 buste deve essere conservato sino al risultato analitico del campione pool" (enables single-plant retest without revisiting the field; matches EFSA card's "pooling in the laboratory").
- Sample-to-test ratio in the plans: tests = ceil(samples/7) olive, ceil(samples/4) other species (Q2). 2021 plan: "216.757 piante specificate da campionare per 30.943 analisi" (≈ 7.0).
- Sampling period (DDS 45 lines 1125–1150; DM 348260 §5.2 identical wording): "i campioni possono essere prelevati durante l'intero arco dell'anno. Per le specie ospiti a foglia caduca, in particolare vite, ciliegio e mandorlo, … il batterio è rilevabile nei tessuti fogliari soltanto in estate inoltrata/fine estate e sino alla caduta delle foglie. Pertanto, per vite, mandorlo e ciliegio è da evitarsi il campionamento e il saggio su foglie nei periodi primaverili - inizio estate. … il campionamento ed il saggio possono essere effettuati sul tessuto legnoso prelevato da rametti ben lignificati in fase di dormienza."
- Post-finding populations (DDS 45 lines 1980–1995, 2050–2065; DGR 1075 §4.2): 50 m zone = all specified plants (except non-susceptible citrus/peach/apricot/plum for ST53); 400 m band = every hectare with specified species sampled (historically 14 samples/ha, now "sottoposti a sorveglianza").
- Vectors (DDS 45 lines 1740–1815): "analisi molecolari singolarmente o in gruppi di max 5 individui"; molecular analyses "sugli individui raccolti a metà giugno, luglio, settembre e ottobre"; CNR-IPSP reports within 5 working days.

Implication: an inspection unit is a plant; a test is a pool; a positive pool yields 7 (4) single tests; a doubtful pool yields a re-extraction of the pool and then 7 (4) singles. Population counts for "plants sampled" must not be inferred from test counts by a constant ratio in mixed-species hectares (authorized-site row 292/60 shows a non-integer ratio).

---

## Q8. Biological timing terms as used in Puglia acts and plans

Verdict: PARTIALLY ESTABLISHED.

### "Stagione di volo del vettore" / adult period

- No Puglia act defines the flight season by calendar dates. The nearest regional statement is DGR 1866/2022 §4.8 (ADOPTED PLAN, line 940): "qualora … si fosse nel periodo di presenza dello stadio adulto dei vettori (da maggio a novembre), … devono procedere obbligatoriamente … ad isolare la pianta infetta con protezioni meccaniche". DGR 343/2022 §4.8 uses the same clause without dates.
- DDS 45/2025 vector-monitoring section (BINDING ACT, lines 1682–1695): "Il monitoraggio dei vettori deve essere svolto da marzo a novembre con cadenza settimanale/quindicinale …; STADI GIOVANILI … nel periodo marzo-maggio, con ispezioni settimanali …; ADULTI … a partire dalla comparsa della IV età giovanile (ninfa di II età) sino a novembre, seguendo il protocollo EFSA. Le ispezioni saranno effettuate con una cadenza di 10-15 giorni"; vineyards: "32 trappole cromotropiche … durante il periodo metà giugno-fine settembre".
- EFSA Pest Survey Card (OFFICIAL GUIDANCE, storymap text line 149): "In Apulia (southern Italy), the emergence of P. spumarius adults usually around the end of April and beginning of May, with a high population abundance in late spring to early summer and movement from herbaceous plants to olive trees is observed. Although adult vectors could be collected from May onwards, surveillance of adult vectors in Apulia (Italy) should take place later during the summer period"; line 139: "Adults generally appear from the dried-up spittle in spring and live until autumn"; line 407: "Sampling for vectors should preferably be done from late spring to early autumn".
- Springer 2024 paper (SCIENTIFIC METHOD / DOCUMENTED PRACTICE; pre-captured `survey-web/apulia2024.html`): "Insect vectors surveillance is yearly carried out from the beginning of March to the end of October in 90 olive orchards (at approx. 10 days interval) across the Apulia Region."

### "Before the next flight season" and the November–March window

- DGR 1075 §4.3.3 (ADOPTED PLAN, page 33): "Tale rimozione è effettuata immediatamente dopo l'identificazione ufficiale della presenza dell'organismo nocivo o, se l'organismo nocivo è rilevato al di fuori della stagione di volo del vettore, prima della stagione di volo successiva. Prima delle estirpazioni si effettuano trattamenti chimici contro il vettore nell'area interessata, per evitare la diffusione dell'organismo nocivo specificato. I trattamenti non si effettuano nel periodo novembre - marzo in quanto non necessari, salvo dall'attività di monitoraggio dei vettori dovesse risultare ancora la presenza di adulti sulle piante arboree." §4.8.3: "i trattamenti insetticidi contro i vettori devono essere eseguiti anche sulle piante soggette ad estirpazione, di cui agli articoli 7 -13 del Reg. (UE) 2020/1201, ad eccezione del periodo novembre - marzo in quanto non necessari."
- DDS 45/2025 (BINDING ACT, lines 1982–1990 and 2055–2061): "I FASE - Trattamento fitosanitario. Preventivamente alle operazioni di estirpazione delle piante, nella zona infetta viene effettuato un trattamento fitosanitario contro i vettori della Xylella con prodotti autorizzati. Tale trattamento non si applica nel periodo novembre - marzo in quanto non necessario. II FASE – Estirpazione. … Dopo 48 ore dall'esecuzione del trattamento fitosanitario, si procede all'estirpazione"; containment: "Dopo 48 ore dal trattamento si procede all'estirpazione delle piante infette." DDS 31/2022 carries the same two clauses (the B ledger's CONFLICT_RETAINED rows).
- DM 348260/2026 §9 (ADOPTED NATIONAL PLAN, line 1377): "In applicazione dell'art. 8, prima della rimozione delle piante e nel corso di tale rimozione, durante la stagione di volo dei vettori, devono essere effettuati adeguati trattamenti fitosanitari contro gli insetti vettori". The national plan, like the EU text after 2024/2507, confines the pre-removal treatment duty to the flight season; the regional Nov–Mar exemption is therefore the Region's operationalisation of "outside the flight season", with DGR 1075 adding a monitoring-based override. Tension: DGR 1866 states adults present "da maggio a novembre"; DDS 45 monitors adults "sino a novembre"; the exemption starts in November.
- The 48 h wait has no EU or national counterpart found; it is a regional procedural rule (DDS 31/45) with no stated biological source.

### Vector-control timing actually fixed by act (BINDING ACTS; per year)

| Year | Juvenile mechanical control (lavorazioni) | Adult insecticide treatment |
|---|---|---|
| 2021 | plan: vector monitoring "da aprile e giugno" (DGR 538 §8); tillage act not captured | not captured |
| 2022 | DGR 644/2022 (ARIF/CC convention, BURP n. 71 del 27-6-2022, search snippet): controls "a partire dall'11 maggio fino al 30 giugno" | not captured |
| 2023 | not captured | Circolare n. 5 del 23/06/2023 (`raw/circolare_5_2023_adulti.pdf`): "è obbligatoria l'esecuzione del II° trattamento insetticida e tale intervento … deve essere eseguito prima possibile e comunque entro il 10 luglio" (19 comuni + Triggiano) |
| 2024 | Circolare n. 2 del 15/04/2024 (referenced by fruitjournal; not captured) | Circolare n. 4 del 24/05/2024 (`raw/circolare_4_2024_adulti.pdf`): "L'intervento insetticida deve essere eseguito entro e non oltre il 10 giugno 2024" |
| 2025 | DDS 47 del 26/03/2025 (<200 m: "entro il 15 aprile", ground kept clean "sino al 30 aprile 2025"), DDS 61/2025 proroga to 23/04/2025, DDS 66 del 18/04/2025 (>200 m: "entro il 12 maggio 2025") — Monopoli/Noci/AIPP sources (`raw/monopoli_avviso_2025_lavorazioni.html`, `raw/aipp_palmisano_2025.pdf`) | DDS 105 del 16/06/2025 (`raw/DDS_105_2025_adulti.pdf`): "Il trattamento dovrà essere eseguito entro e non oltre il 30 giugno 2025" (14 comuni; olive+almond, +vine in Bari, Noicattaro, Triggiano, Valenzano); DDS 121 del 30/06/2025 (`raw/DET_121_30_6_2025.pdf`): "prorogare sino al 10 luglio 2025" |
| 2026 | DDS 39 del 11/03/2026 (`raw/DDS_39_2026_lavorazioni.pdf`): "<200 m … dal 25 marzo al 30 aprile 2026; >200 m … dal 10 aprile al 15 maggio 2026", whole region; DDS 79 del 28/04/2026 (`raw/DDS_79_2026_proroga_lavorazioni.pdf`): "entro il 15 maggio 2026 / entro il 30 maggio 2026"; ANCI 27/05/2026 (`raw/anci_no_proroga_2026.html`): no further extension "effettuare i trattamenti oltre le date già prorogate risulterebbe inutile ai fini del contrasto allo stadio giovanile" | NOT FOUND as of 2026-09-08 (queries: "trattamenti obbligatori adulti … 2026 determina"; consistent with the skill's standing GAP) |

DGR 1075 §4.8.2–4.8.3 delegates both windows to acts: "Occorre intervenire prima che l'insetto raggiunga il picco del IV stadio giovanile … Le indicazioni del periodo di esecuzione del/dei trattamenti obbligatori per aree omogenee sono emanate dall'Osservatorio attraverso atti dirigenziali/circolari pubblicati sul sito istituzionale www.emergenzaxylella.it"; "I trattamenti non vanno eseguiti: su piante … completamente secche; in aree verdi; in aree urbane; in boschi e pinete."

### "Periodi opportuni" / "most appropriate time" for plant surveys

- EFSA card (line 121): "The time frame for the survey activity is not addressed here as it will vary across the EU depending on the climate conditions"; line 383: "The current EU guidelines require sampling of young branches of leaves during the summer time … The sample should include mature leaves and sampling young growing shoots briefly after emergence should be avoided".
- DDS 45 / DM 348260 / DTU 39: all-year sampling with the deciduous-host caveat (Q7). DM 348260 §5.1: "Le indagini sono effettuate nel periodo dell'anno più idoneo alla rilevazione della batteriosi, tenendo conto della biologia dell'organismo nocivo e dei suoi vettori, della presenza e della biologia delle piante ospiti nonché delle informazioni … del Documento Tecnico Ufficiale n. 39 e dell'EFSA (EFSA pest survey card)."
- Authorized sites (DGR 1075 §4.10.1): "sottoposto ogni anno ad almeno due ispezioni da parte dell'autorità competente, nel periodo più adatto".

### Implication

- C should carry "flight season" as an open biological term with two regional operative surrogates: (i) the Nov–Mar no-treatment window (DDS 31/45, DGR 1075, with the DGR 1075 monitoring override); (ii) the DGR 1866 adult-presence statement May–November. They disagree in November; the monitoring data (bollettini on emergenzaxylella.it) are the fact the override turns on.
- Juvenile-control windows are altitude-stratified since 2025 (< / > 200 m ISTAT mean altitude) and set per year by determina, with prorogations; adult-treatment deadlines have fallen between 10 June and 10 July (2023–2025).

### Gaps / boundary

- Not captured: 2021–2022 adult circulars, 2023–2024 juvenile circulars (circolare n. 2/2024 exists per fruitjournal), 2026 adult act (none found). `cartografia.sit.puglia.it/doc/xylella/vettori/` folders deny listing; only `circolari2023/circolare_5_2023.pdf` is confirmed. emergenzaxylella.it news feed not enumerable without a browser (SPA).

---

## Q9. "Annual survey", "twice during the flight season", campaign scheduling 2021–2026

Verdict: ESTABLISHED as documented practice; PARTIALLY as plan text.

### Plan calendars (ADOPTED PLANS)

- DGR 538/2021 §7.6 "Calendarizzazione della sorveglianza": "L'attività di sorveglianza sul territorio regionale viene effettuata da maggio a ottobre 2021 con le seguenti priorità: 1. aree delimitate in eradicazione e seconda sottozona … 2. zona cuscinetto, con priorità per la zona di 400 m ad alto rischio … 3. zona contenimento … 4. area indenne. L'ulteriore azione di sorveglianza … sarà svolta da novembre a dicembre 2021." Calendar table: Monopoli-Polignano-Canosa May–June; cuscinetto and contenimento June–August; area indenne between Monopoli and Polignano May; area indenne September–October; further surveillance November–December. §8: vector monitoring for control strategy "da aprile e giugno"; vector testing under Arts 10/15 "da giugno ad ottobre".
- DGR 343/2022, 1866/2022, 1593/2024, 1075/2025 §7 "Cronoprogramma": month-grid tables (Mar–Dec; Gen–Dic) whose cell marks did not survive OCR/pdftotext; not readable in the held texts. DGR 644/2022 convention: ARIF must complete the 2022 surveillance "entro il 31 dicembre 2022".
- PNI 2026 column E for every Puglia row: "Gennaio; Febbraio; …; Dicembre" (all twelve months).

### Actual sampling dates (DOCUMENTED PRACTICE; recomputed this session from the Osservatorio's published campaign workbooks held at `/Users/owenwassmer/Desktop/Connor/olive-xylella/raw/data/camp_xlsx/`, column DATA_RILEVAMENTO)

| Book | rows | first | 5th pct | median | 95th pct | last |
|---|---|---|---|---|---|---|
| CAMP_2019_2020 | 50 967 | 2019-08-01 | 2019-09-09 | 2020-01-23 | 2020-03-05 | 2020-04-30 |
| CAMP_2020 | 172 005 | 2020-04-30 | 2020-06-26 | 2020-09-08 | 2021-02-18 | 2021-03-05 |
| CAMP_2021 | 219 120 | 2021-05-26 | 2021-06-25 | 2021-09-14 | 2022-01-13 | 2022-02-03 |
| CAMP_2022 | 266 352 | 2022-06-09 | 2022-06-17 | 2022-09-15 | 2023-06-08 | 2023-06-30 |
| CAMP_2023 | 62 876 | 2023-07-18 | 2023-08-24 | 2024-01-11 | 2024-03-05 | 2024-03-11 |
| CAMP_2024 | 119 729 | 2024-01-23 | 2024-03-21 | 2024-08-26 | 2024-12-09 | 2024-12-20 |
| CAMP_2025 | 121 860 | 2025-01-07 | 2025-01-21 | 2025-06-30 | 2025-11-26 | 2025-12-19 |

Monthly counts are in `sources.json` notes. Reading: 2020–2022 campaigns straddled years (start May/June, peaks July–October, tail into winter, the 2022 book running to June 2023); from 2024 the campaign is a calendar year with sampling in every month (2025: 5 305–14 021 samples per month). The Rivista di Agraria article (`raw/rivistadiagraria_decennio_monitoraggio.html`, built from FOIA'd Osservatorio data) states the same spans: "225.014 da maggio 2021 a febbraio 2022, e 266.366 da giugno 2022 a giugno 2023". AIPP/Palmisano slides (27-11-2025): "Nelle campagne di monitoraggio attuate dal 2023, sono state campionate e analizzate complessivamente 1.389.928 piante."

### "Twice during the flight season" (vector tests, Art. 5(1)(d))

- DDS 45/2025 §7: "Le analisi molecolari devono essere effettuate dal laboratorio IPS-CNR sugli individui raccolti a metà giugno, luglio, settembre e ottobre" — four occasions per season, exceeding the EU "twice"; adult monitoring every 10–15 days from the IV instar to November; Springer 2024: March–October, ~10-day intervals, 90 orchards.

### Implication

- "Annual survey" is performed as one continuous campaign per year (calendar-year since 2024) that touches all twelve months; a recurrence test cannot use a fixed start date; the plan's per-area priorities and the workbook dates are the only operative evidence of "when".
- The 2023 book is anomalous (62 876 rows, gap Oct–Dec 2023) — a caveat for any negative-survey support based on that year.

### Gaps / boundary

- Campaign books after 2025 not yet published; open-data CKAN dataset (dati.puglia.it "dati-monitoraggio-xylella-fastidiosa", last update 2025-12-23) covers 2020–2022 only per its description.
- The cronoprogramma cell marks of the 2022–2025 plans require the BURP PDFs (not the OCR'd texts); not re-fetched.

---

## Search boundary (whole branch)

Catalogs enumerated or attempted: BURP document store (DET/DEL PDFs reached by known URL patterns; three fetched); municipiumapp S3 mirrors (DDS 39/2026, 79/2026, 105/2025, 121/2025, circolare 4/2024); cartografia.sit.puglia.it/doc/xylella/vettori (listing denied; one file confirmed); protezionedellepiante.it (PNI 2026 workbook pre-captured; EFSA card 2019 mirror; DM 2026 plan pre-captured); JKI mirror (EN-1873); EFSA Knowledge Junction/Zenodo (blocked: 403 curl, 504 Crawl4AI; browser unavailable); EFSA journal on Wiley (403); EFSA site PDF (RiPEST 2023 poster); pestrisk.org (RiPEST slides); epitools (formulae); dati.puglia.it CKAN (description only); Belgium FPS; Springer (pre-captured); Rivista di Agraria; AIPP.

Inaccessible after retry: RiBESS+ manual (zenodo 2541541), RiPEST manuals (zenodo 8335473, 17701334, 8335472), EFSA EN-366 (2012 RiBESS framework), EFSA EN-9411 full text (DOI 403), press.regione.puglia.it (connection failure), comune.guagnano.le.it (403), emergenzaxylella.it (SPA, no static index).

Not run: exhaustive enumeration of the UOR-181 determinazioni register for every 2021–2024 vector circular; Accredia SOP search for the Puglia laboratories.
