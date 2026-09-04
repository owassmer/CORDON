# TAR Puglia — Lecce: Xylella judicial corpus

Retrieval date: 2026-08-19. Scope: every TAR Puglia, Lecce, **sentenza** returned by the official Giustizia Amministrativa decision index for the phrase `Xylella fastidiosa`, plus the OpenGA subject-field cross-check. The official index returns 32 decisions. The 2023–2026 annual OpenGA JSON resources add no subject-bearing decision outside those 32.[1][2]

Official full text was retrieved for all 32 decisions. Twenty-six documents are NIR-style XML and six are court-deposited PDFs. The files and hashes are listed below. A 1,535-byte portal 404 shell is not counted as a document.

---

## CLASS 3 — ASSERTED FROM MODEL MEMORY, NO FETCHED SOURCE

**none.**

Dates, RG numbers, holdings, challenged acts, quotations, appeal status, URLs, byte counts, and hashes below come from fetched official metadata or official court documents. The four pre-OpenGA dates marked `date cross-check` were checked against indexed secondary citation pages; the official XML supplies the court, section, number, RG, deliberation date, and complete text but does not print a publication-date line.

---

## CLASS 1 — QUOTED FROM SOURCES ACTUALLY FETCHED

### 1. Census and method

The official Giustizia Amministrativa decision search, filtered to `Sentenza`, sede `Lecce`, phrase `Xylella fastidiosa`, returned **32 results**: 16 in 2026, four in 2025, one in 2024, seven in 2023, two in 2021, and two in 2018.[2] The OpenGA TAR Lecce dataset supplies court-generated subject, RG, section, date, and outcome fields for 2023–2026.[1]

The subject-field cross-check catches the operative case descriptions directly. Examples are:

- n. 723/2023: `MISURE FITOSANITARIE PER IL CONTENIMENTO DELLA DIFFUSIONE DELLA XYLELLA FASTIDIOSA - ESTIRPAZIONE PIANTE INFETTE -`;
- n. 552/2023: `INDENNIZZO DANNO XYLELLA FASTIDIOSA`;
- n. 1122/2024: `EROGAZIONE INDENNIZZO XYLELLA FASTIDIOSA`;
- n. 1439/2025: `RISARCIMENTO DANNI DA XYLELLA FASTIDIOSA - RIASSUNZIONE DAL TRIBUNALE DI LECCE`.

### 2. The only Lecce merits decision that directly construes a plant-removal rule

**TAR Puglia, Lecce, sez. III, 9 April 2018, n. 573, RG 693/2017.** The challenged acts are Regional determinations 68/2017 and 109/2017. They order, at the owner’s expense, removal of 13 and 72 infected olive trees in Oria, plus the SELGE/CNR test reports. The court applies Decision 2015/789, Arts. 7(2)(c) and 4(2), and LR Puglia 4/2017.[6]

The court states:

> La suddetta “rimozione immediata”, a carattere - con ogni evidenza - imperativo, è da intendersi come rimozione totale, comprensiva anche delle radici.

It then holds:

> In definitiva, le disposte misure di rimozione totale degli alberi infetti risulta adeguata e proporzionata, in ragione del bilanciamento dei contrapposti interessi e in applicazione del principio di precauzione.

On participation, it states:

> non sussisteva un obbligo di avviso dell’avvio del procedimento relativo all’abbattimento delle piante di ulivo, che in alcun modo avrebbe potuto influire sull’esito dello stesso, attesa la superiore finalità del contenimento della diffusione ed eradicazione del batterio

The dispositif declares the indemnity claim outside administrative jurisdiction; declares the annulment claim partly moot after voluntary execution; rejects the remaining annulment and damages grounds. The decision therefore **upholds and construes** the predecessor containment-removal rule. It does not annul an eradication act.

### 3. The damages-liability line

**TAR Lecce, sez. III, 30 October 2025, n. 1439, RG 52/2024**, followed by fourteen 2026 judgments, rejects claims that Italy, MASAF, and the Region caused private orchard losses by failing to act quickly enough.[7]

The lead judgment states:

> il Tribunale ritiene infondate e insussistenti le allegate illegittimità delle condotte e dei poteri discrezionali delle PP.AA. resistenti in subiecta materia, per la denunciata mancata, ritardata o inadeguata attivazione della funzione pubblica in tema di misure di protezione e contenimento della Xylella fastidiosa

It also states that the historical response involved:

> una serie di ostacoli giuridici e fattuali riguardanti, lo studio e il monitoraggio del fenomeno, l’identificazione e la ricerca dei proprietari delle piante infette e la predisposizione degli atti ingiuntivi di abbattimento: operazioni del tutto laboriose, complesse e notoriamente ostacolate o comunque non eseguite dagli stessi proprietari.

The line relies on Directive 2000/29 Art. 16, Decision 2015/789 Arts. 6(2), 6(7), 6(9), and 7(2)(c), and CJEU C-443/18. It rejects private damages liability. It does **not** create a current Reg. 2020/1201 parcel duty.

### 4. Art. 6 replant aid: controlling Consiglio di Stato merits decision

The official CDS metadata search located **Consiglio di Stato, sez. VI, 28 August 2023, n. 7994, RG 2498/2023**, which affirms TAR Bari n. 20/2023, not a TAR Lecce judgment.[3][8]

The court reproduces D.I. 2484/2020 Art. 6 and the DDS 377/2020 notice. It holds that a legal representative’s personal `coltivatore diretto` status does not automatically become the applicant cooperative’s status for the Art. 12 `Principio 4` premium. It also treats possession and proof at the application date as controlling. The dispositif states:

> Il Consiglio di Stato in sede giurisdizionale (Sezione Sesta), definitivamente pronunciando sull’appello (n. R.g. 2498/2023), come indicato in epigrafe, lo respinge.

This is a final merits authority on the **Art. 6 aid-scoring rule**. It corroborates the Bari line and is the most important new higher-court item found during the Lecce gap search.

### 5. Appeals against Lecce decisions and Bari nn. 383/384/387

The official `Verifica appello` endpoint was queried for all 32 Lecce judgments and for TAR Bari nn. 383, 384, and 387/2026. The result is:

| First-instance decision | Official appeal result as of retrieval | Merits status |
|---|---|---|
| TAR Bari nn. 383/2026 (RG 99/2024), 384/2026 (RG 185/2024), 387/2026 (RG 1238/2023) | No appeal record for any of the three | **No later CdS merits decision located** |
| TAR Lecce n. 552/2023 (RG 1296/2021) | CdS RG 8982/2023; CdS sez. VI decree 16/09/2025 n. 552 declares perenzione | **No merits**; appeal ended procedurally.[5][9] |
| TAR Lecce n. 1275/2025 (RG 1340/2024) | CdS RG 7751/2025 and 8575/2025; interim order 3944/2025; CdS sez. VI 13/07/2026 n. 5612 joins and rejects both appeals | Final merits, but the case concerns an antenna. Xylella appears only in a landscaping condition; no Wedge rule changes.[3][4][10] |
| TAR Lecce n. 1439/2025 (RG 52/2024) | CdS RG 3662/2026; no published decision in OpenGA sentenze/ordinanze/decreti through the 28 July 2026 resources | Pending/no merits located |
| TAR Lecce n. 641/2026 (RG 1144/2022) | CdS RG 4939/2026; no published decision in OpenGA sentenze/ordinanze/decreti through the 28 July 2026 resources | Pending/no merits located |
| Remaining 28 Lecce judgments | Official endpoint reports no appeal | No later merits located |

CdS order 755/2024 remains the separate interim appeal already identified in the Bari corpus. OpenGA confirms sez. VI, RG 1065/2024, non-final (`FLG_DEFINISCE=N`), with temporary suspension of the monumental-tree removal dispute.[4] No later merits sentenza for RG 1065/2024 appears in the 2024–2026 CDS sentenze resources.[3]

### 6. Decision-by-decision corpus

`Rule effect` uses only the requested Wedge rules: Art. 7 eradication; Art. 13 containment removal; monumental derogations; D.I. 2484/2020 Art. 6 aid; AGEA reconversion; vector duties.

| Court / date / decision / RG | Challenged act or claim | Holding and exact provision affected | Relation | Operative or context; Wedge rule effect |
|---|---|---|---|---|
| Lecce III, 09/04/2018, n. 573, RG 693/2017 | Regional DDS 68/2017 and 109/2017; CNR/SELGE tests; 85 infected olives in Oria | Partly no jurisdiction, partly moot, remainder rejected. Decision 2015/789 Arts. 7(2)(c), 4(2); LR 4/2017. `Rimozione immediata` means total removal including roots; no pre-removal participation required where outcome is fixed. | **construes / upholds** | **Operative historical predecessor.** Directly supports infected-tree removal and owner execution/cost. It does not change current Arts. 7 or 13 geography. No monumental, Art. 6, AGEA, or current vector-rule change. |
| Lecce I, 09/05/2018, n. 767, RG 1445/2017 | Nardò GM 345/2017 approving the Sarparea subdivision plan and VAS synthesis | Rejects challenge. Monumental-olive survey and protection may be enforced at the execution/permit stage. LR 14/2007 and planning/VAS rules; Xylella appears in the planning record. | **upholds** | **Context.** Concerns planning-stage monumental-olive survey, not Reg. 2020/1201 monumental derogations. No Wedge rule changes. |
| Lecce III, 13/07/2021, n. 1128, RG 1526/2020 | Exclusion from PSR 2014–2020 Operation 4.1.C under DDS 37/2019 for incomplete title documentation uploaded by the deadline | Rejects. Applicant bears proof of platform malfunction; no soccorso istruttorio for a late/incomplete required title. DDS 37/2019 §17.2 and deadline rules. | **upholds** | **Context.** Xylella-targeted PSR investment aid, but not D.I. 2484/2020 Art. 6. No listed Wedge rule changes. |
| Lecce I, 14/10/2021, n. 1522, RG 1/2021 | Porto Cesareo denial of a PUE and regional landscape opinion | Partly annuls a 40 m safeguard prescription and otherwise rejects. PPTR/planning provisions. | **limits** | **Context.** Xylella appears only in landscape-restoration conditions. No Wedge rule changes. |
| Lecce II, 06/03/2023, n. 318, RG 1748/2021 | Brindisi Province PAUR denial for agrivoltaic plant and negative opinions | Annuls denial and opinions. The proposed FS17 olive planting is a project fact. Energy/PAUR rules, not phytosanitary law. | **annuls** | **Context.** No Wedge rule changes. |
| Lecce III, 27/03/2023, n. 403, RG 552/2022 | Questore foglio di via issued after protest at Xylella felling site | Annuls foglio di via. D.Lgs. 159/2011 Arts. 1–2. | **annuls** | **Context.** The felling event is factual background only. No Wedge rule changes. |
| Lecce III, 31/03/2023, n. 423, RG 551/2022 | Same protest; separate foglio di via | Annuls foglio di via. D.Lgs. 159/2011 Arts. 1–2. | **annuls** | **Context.** No Wedge rule changes. |
| Lecce III, 27/04/2023, n. 552, RG 1296/2021 | CLE note 20/05/2021 refusing to reopen EIP submission for 2018 Xylella indemnity | Annuls note and requires reconsideration/reopening because the record supported a platform interruption. D.Lgs. 102/2004 indemnity procedure and notice deadline. | **annuls** | **Operative only for the separate D.Lgs. 102/2004 compensation workflow.** No Art. 6, AGEA, eradication, removal, monumental, or vector-rule change. Later appeal ended by perenzione, not merits. |
| Lecce I, 05/05/2023, n. 581, RG 1735/2021 | Landscape opinions for rural-building renovation in Salve | Annuls only the Union’s note; other opinion challenges inadmissible. D.Lgs. 42/2004 Art. 146 and PPTR. | **annuls / limits** | **Context.** Xylella-resistant planting is a compensatory condition. No Wedge rule changes. |
| Lecce III, 05/06/2023, n. 723, RG 536/2020 | DDS 30–37 and 39/2020 ordering infected-tree removal in Carovigno, `zona ex contenimento` | Declares case moot after execution. Decision 2015/789 is recited, but no merits holding reaches the removal rule. | **moot; no merits** | **Context.** No current Art. 13 or Art. 7 rule changes. |
| Lecce III, 19/10/2023, n. 1164, RG 553/2022 | Third foglio di via from the same felling protest | Annuls Questore order. D.Lgs. 159/2011 Arts. 1–2. | **annuls** | **Context.** No Wedge rule changes. |
| Lecce III, 28/10/2024, n. 1122, RG 182/2024 | ARIF note treating 2018 indemnity application as not receivable because it was never completed in EIP | Rejects challenge. Application record, not alleged later paper material, controls completion. D.Lgs. 102/2004; 14/12/2020 notice. | **upholds** | **Operative only for D.Lgs. 102/2004 income support.** No listed Wedge rule changes. |
| Lecce III, 15/04/2025, n. 634, RG 998/2024 | Final PSR 4.1.C review requiring partial repayment of advance/acconto | Rejects. Final review may disallow non-eligible post-planting and other costs under DDS 37/2019 and later implementation acts. | **upholds** | **Context for a separate PSR measure.** Not Art. 6 D.I. 2484/2020; no listed rule changes. |
| Lecce II, 29/07/2025, n. 1275, RG 1340/2024 | Martina Franca mobile-radio installation authorisation and municipal antenna regulation | Partly accepts main challenge; rejects conditional cross-claim. A hedge of species resistant to Xylella is merely an installation condition. | **annuls / limits** | **Context.** No Wedge rule changes. CdS n. 5612/2026 rejects both appeals. |
| Lecce III, 30/10/2025, n. 1439, RG 52/2024 | Damages claim for alleged late/inadequate public Xylella response | Rejects. Directive 2000/29 Art. 16; Decision 2015/789 Arts. 6(2), 6(7), 6(9), 7(2)(c); CJEU C-443/18. No unlawful public omission or proven causal chain. | **upholds historical response / rejects liability** | **Context for Wedge.** It does not alter current parcel rules. It does not create a vector duty. CdS RG 3662/2026 pending/no decision located. |
| Lecce I, 03/11/2025, n. 1447, RG 1156/2023 | Region’s refusal to rectify PPTR mapping | Annuls for formal/decisional defects and remands. D.Lgs. 42/2004 and PPTR rectification rules. Xylella-related drying is factual context. | **annuls / remands** | **Context.** No Wedge rule changes. |
| Lecce III, 20/03/2026, n. 458, RG 638/2023 | Damages claim after civil-to-administrative transfer | Rejects on n. 1439 line. Same historical EU provisions. | **rejects liability** | **Context; no listed Wedge rule changes.** |
| Lecce III, 20/03/2026, n. 459, RG 786/2023 | Same class of damages claim | Rejects on n. 1439 line. | **rejects liability** | **Context; no listed Wedge rule changes.** |
| Lecce III, 20/03/2026, n. 460, RG 727/2023 | Same class of damages claim | Rejects on n. 1439 line. | **rejects liability** | **Context; no listed Wedge rule changes.** |
| Lecce III, 20/03/2026, n. 461, RG 710/2023 | Same class of damages claim | Rejects on n. 1439 line. | **rejects liability** | **Context; no listed Wedge rule changes.** |
| Lecce III, 31/03/2026, n. 496, RG 775/2023 | Same class of damages claim | Rejects on n. 1439 line. | **rejects liability** | **Context; no listed Wedge rule changes.** |
| Lecce III, 31/03/2026, n. 497, RG 784/2023 | Same class of damages claim | Rejects on n. 1439 line. | **rejects liability** | **Context; no listed Wedge rule changes.** |
| Lecce III, 31/03/2026, n. 500, RG 749/2023 | Same class of damages claim | Rejects on n. 1439 line. | **rejects liability** | **Context; no listed Wedge rule changes.** |
| Lecce III, 31/03/2026, n. 501, RG 468/2024 | Same class of damages claim | Rejects on n. 1439 line. | **rejects liability** | **Context; no listed Wedge rule changes.** |
| Lecce III, 27/04/2026, n. 641, RG 1144/2022 | Nardò revocation and recovery of a €125,743.90 D.Lgs. 102/2004 Xylella 2016/17 indemnity | Rejects. DGR 494/2018 and incorporated materials limit eligible production; `ALTRI VIVAI` was not covered. The municipality could correct and recover the award. | **upholds revocation** | **Operative only for D.Lgs. 102/2004 compensation.** No listed Wedge rule changes. CdS RG 4939/2026 pending/no decision located. |
| Lecce III, 08/07/2026, n. 1009, RG 822/2023 | Damages claim alleging breach of 2014/2015 EU Xylella decisions | Rejects on n. 1439 line. | **rejects liability** | **Context; no listed Wedge rule changes.** |
| Lecce III, 08/07/2026, n. 1011, RG 870/2023 | Same class of damages claim | Rejects on n. 1439 line. | **rejects liability** | **Context; no listed Wedge rule changes.** |
| Lecce III, 08/07/2026, n. 1012, RG 872/2023 | Same class of damages claim | Rejects on n. 1439 line. | **rejects liability** | **Context; no listed Wedge rule changes.** |
| Lecce III, 08/07/2026, n. 1013, RG 874/2023 | Same class of damages claim | Rejects on n. 1439 line. | **rejects liability** | **Context; no listed Wedge rule changes.** |
| Lecce I, 14/07/2026, n. 1057, RG 1302/2025 | Silent refusal of access to records for an accepted 2018 Xylella-damage claim | Annuls silent refusal, recognises access right, orders disclosure within 30 days. L. 241/1990 Arts. 22–25; c.p.a. Art. 116. | **annuls / orders disclosure** | **Context.** Access only; no eligibility or plant-duty rule changes. |
| Lecce III, 23/07/2026, n. 1103, RG 1349/2024 | Damages claim alleging breach of 2014/2015 EU Xylella decisions | Rejects on n. 1439 line. | **rejects liability** | **Context; no listed Wedge rule changes.** |
| Lecce III, 23/07/2026, n. 1105, RG 869/2023 | Same class of damages claim | Rejects on n. 1439 line. | **rejects liability** | **Context; no listed Wedge rule changes.** |

### 7. Retrieved official files and sha256

All paths are under `data/extracts/judgments/`.

| File | Bytes | sha256 |
|---|---:|---|
| `TAR_LE_sez3_2018_00573_RG_201700693.xml` | 40,587 | `76c7850ac89ed1565beecff5db882760c3b4ed7d3c86683614e23638441e8711` |
| `TAR_LE_sez1_2018_00767_RG_201701445.xml` | 29,833 | `5e996668f856520b7541074a4065754337b4a64e1d6c79b5f7512172b6d6641e` |
| `TAR_LE_sez3_2021_01128_RG_202001526.xml` | 34,136 | `48f7149ec68c4216aac7ef2abf7e33e9bd347e7caf8fbe87cfcc6ca6346c63c6` |
| `TAR_LE_sez1_2021_01522_RG_202100001.xml` | 42,495 | `fc9684573bd53d7a679202e6fcc0bf482eda37bb17066a114ed1d25ff2d5c5db` |
| `TAR_LE_sez2_2023_00318_RG_202101748.xml` | 64,044 | `ac3a39a968b7c253c8acb299663c1c8b4ec0b6535df397cf433c28c1786f578e` |
| `TAR_LE_sez3_2023_00403_RG_202200552.xml` | 18,478 | `bfde56666c0cfdf98c8da2037287efb7a974ad0a0c2937e65894f1b3155833b1` |
| `TAR_LE_sez3_2023_00423_RG_202200551.xml` | 18,043 | `9692a0343b283484bc067da8804448ac5d95d3c8b8145a45e8ee30f41fa0ea74` |
| `TAR_LE_sez3_2023_00552_RG_202101296.xml` | 20,753 | `bb150aaf089bb3532a670c7973e14ca6e12cb52333a78fe35dc296c12dd02713` |
| `TAR_LE_sez1_2023_00581_RG_202101735.xml` | 29,752 | `c2195f235152756c2b67a4b3ec015f406f7d13ba35aacea331dd1c03f96e0f23` |
| `TAR_LE_sez3_2023_00723_RG_202000536.xml` | 15,521 | `cd6f574a0f0cbf26a667b1d2d54eeb41475ea053ebc40029819da0e817dec44d` |
| `TAR_LE_sez3_2023_01164_RG_202200553.xml` | 25,173 | `11272bd94e06c81cf3b2432db0e6ec8edeb820418164259e652891b5cfd39e3d` |
| `TAR_LE_sez3_2024_01122_RG_202400182.xml` | 26,936 | `e7b01480560cb9a3de245c6757515698aaf4aab0f1b95fcb742a6baf7a44a61d` |
| `TAR_LE_sez3_2025_00634_RG_202400998.xml` | 35,767 | `5c9a76fe273657dca0602f875ce6f482c4b0623420caeb7208286d35b14a5c8e` |
| `TAR_LE_sez2_2025_01275_RG_202401340.xml` | 61,550 | `3adc9b73ec459c2917c53b846cf54e02742365db5e0606b894a73518ae38d0f3` |
| `TAR_LE_sez3_2025_01439_RG_202400052.xml` | 50,756 | `4da29d1a7cdc77fac92594df7663b718fb108f74aecb49ec0aa068e4d77cfdfd` |
| `TAR_LE_sez1_2025_01447_RG_202301156.xml` | 17,211 | `8f65be89eee30ddea36bb47bae2fb52764979922483cab09b5e5dd03fad521a3` |
| `TAR_LE_sez3_2026_00458_RG_202300638.xml` | 53,633 | `8372f4c8012e5eeccbc3a707aa05c55f0e08cad545b23ba46f86eca8686ae402` |
| `TAR_LE_sez3_2026_00459_RG_202300786.xml` | 51,079 | `1be3c57444935ba31483d6c97dcf2c6db83ecb0189c6fb71b45dc2c36e5cb140` |
| `TAR_LE_sez3_2026_00460_RG_202300727.xml` | 50,204 | `ac9b39f34161eb5820db082534546811e68d400082e1d0d8eb66c57c3fb1c756` |
| `TAR_LE_sez3_2026_00461_RG_202300710.xml` | 50,843 | `8f4529e7d8fb9cde65e897a13046cac858d49185d9bb4d6f4d0e45c25e4b82d5` |
| `TAR_LE_sez3_2026_00496_RG_202300775.xml` | 42,329 | `55d9e971aa6d30bfc28daf098ba9b471012cbe00db5e11364a039edba7885e0c` |
| `TAR_LE_sez3_2026_00497_RG_202300784.xml` | 46,485 | `50f17bbd749a47bf2f1ea54b99b12cf1f3ba2dcea01a625c8d0b13b14dab23bb` |
| `TAR_LE_sez3_2026_00500_RG_202300749.xml` | 44,614 | `95ee3089acf8cb774b7419ec91a647065d3749120e99f5d51fe2ae8f90241ef7` |
| `TAR_LE_sez3_2026_00501_RG_202400468.xml` | 47,337 | `f9e38e1007b57ef3de6e56bff97bb0b951932ab8fd5f3341dc18c403938e3888` |
| `TAR_LE_sez3_2026_00641_RG_202201144.xml` | 31,550 | `fc29cfa8be04b1bf7b995ef4a3d128d03e8f8b87b2a0423a574e25980af384a3` |
| `TAR_LE_sez3_2026_01009_RG_202300822.pdf` | 177,940 | `25bfa5a6a6bddfa73710a43b234c429f3af4c1a3452039c5acfa517649a6e77b` |
| `TAR_LE_sez3_2026_01011_RG_202300870.pdf` | 177,630 | `a8d16658c5e54dffacd291d65b1e0f8c9dda202aff951ff78ce50e66f1342345` |
| `TAR_LE_sez3_2026_01012_RG_202300872.pdf` | 175,133 | `0519d41d7f6e8b8b8e434a67bbae59a60b00ce86f6ea26546ed9d7522bc0f81b` |
| `TAR_LE_sez3_2026_01013_RG_202300874.pdf` | 175,429 | `e247fc7b787d1ab587e06a005e387f3a2c2a333b93006d2ebb5148b13702df19` |
| `TAR_LE_sez1_2026_01057_RG_202501302.xml` | 7,473 | `a0d9c71fe9e440f3c4c596039ab8b7514d857d76b9a706217a8d273724295297` |
| `TAR_LE_sez3_2026_01103_RG_202401349.pdf` | 175,549 | `90369e1732b0e753b6215d0215ab6734d96d1a91c545affba44da39582ab617e` |
| `TAR_LE_sez3_2026_01105_RG_202300869.pdf` | 178,951 | `9d7acb1e95eba340f869f3afe149f0f0365102ac368f1973e8a6f6cb13aebdf7` |
| `CDS_sez6_2023_07994_RG_202302498.xml` | 46,134 | `71925260782e13320df52825263dc351f984502475dacd58d7df1a530875c869` |
| `CDS_sez6_2025_00552_RG_202308982.xml` | 4,286 | `95d537fd262dda04a413c1a8e09a5dbe858b79ba98b8e7a030f354df4405e992` |
| `CDS_sez6_2026_05612_RG_202508575.xml` | 70,074 | `e5ea96088e0ffa86ee791c70dd13317ca8ed2add3186860ab556967eedec12d1` |

---

## CLASS 2 — INFERRED FROM CLASS 1

### 1. Operative versus context

Only **n. 573/2018** directly construes a plant-removal obligation. It is historical because it applies Decision 2015/789, not Reg. 2020/1201. Its direct effect is narrow: an infected olive inside the then 20 km containment band had to be removed fully, roots included, and the owner could not defeat an inevitable order through a participation objection.

The second-order effect is useful but limited. It supports the product’s treatment of a mandatory infected-tree removal as an execution duty rather than a discretionary option. It does **not** answer whether a current parcel falls under Art. 7 or Art. 13. Current legal geography still comes from Reg. 2020/1201, Annex III, and the live regional acts.

The 2025–2026 damages line is context. It rejects liability for the historical epidemic response. It does not validate every later act, redraw a zone, create a vector-treatment deadline, or eliminate a statutory derogation.

### 2. Wedge rule ledger

| Wedge rule | Lecce effect | Higher-court effect found in this search |
|---|---|---|
| Reg. 2020/1201 Art. 7 eradication | **No change.** n. 573/2018 is a predecessor-rule analogue only. n. 723/2023 is moot without merits. | No later CdS merits appeal against Bari nn. 383/384/387 located. |
| Art. 13 containment removal | **No current-rule change.** n. 573 supports immediacy/completeness under the predecessor regime. | CdS order 755/2024 remains interim and non-final. |
| Monumental derogations | **No change.** n. 767/2018 is planning context, not an EU phytosanitary derogation. | No new merits decision. |
| D.I. 2484/2020 Art. 6 aid | **No Lecce change.** Lecce aid cases concern D.Lgs. 102/2004 or PSR 4.1.C. | **CdS n. 7994/2023 changes/clarifies the rule set:** the applicant entity itself must hold and prove the IAP/CD status used for `Principio 4` at the application date; a representative’s personal status is not imputed automatically. |
| AGEA reconversion | **No decision located.** | No CdS merits decision located. |
| Vector duties | **No new parcel duty.** The damages cases describe vectors and historical owner obstruction but do not formulate a current operational vector-control rule. | No new merits decision located. |

### 3. Direct and second-order effects

- **Direct:** the corpus closes the Lecce gap with 32/32 official texts and exact RG mappings.
- **Direct:** n. 573/2018 supplies official language for complete infected-tree removal, including roots, under the predecessor containment regime.
- **Direct:** n. 7994/2023 is a final CdS merits authority for Art. 6 aid scoring and applicant identity.
- **Second-order:** D.Lgs. 102/2004 indemnity and PSR 4.1.C cases must not be merged into the Art. 6 aid rule. They are different programs with different notices, criteria, and procedural clocks.
- **Second-order:** the 2025–2026 damages cases should not be converted into positive proof that every public Xylella measure was lawful. They decide causation and liability on the records before the court.
- **Second-order:** pending CdS RG 3662/2026 and RG 4939/2026 should be monitored. They concern the damages line and the D.Lgs. 102/2004 revocation, not the core Art. 7/13 rule fork.

---

## FETCH LOG

| Source or request | Result |
|---|---|
| OpenGA CKAN `package_show?id=tar-puglia-lecce-sentenze` | HTTP 200. Annual JSON resources for 2023, 2024, 2025, 2026 fetched and searched by subject.[1] |
| Official Decisioni e pareri search: `Xylella fastidiosa`, `Sentenza`, `Lecce` | 32 results. All official document URLs extracted.[2] |
| 26 `schema=tar_le`, `_01.html` document requests | HTTP 200, XML payloads. Saved and hashed. |
| Six 2026 `schema=tar_le`, `_01.pdf` requests: nn. 1009, 1011, 1012, 1013, 1103, 1105 | HTTP 200, genuine PDF payloads. Saved and hashed. |
| Official appeal-verification endpoint for all 32 Lecce judgments and Bari nn. 383/384/387 | HTTP 200 for each query. Four Lecce decisions have appeal records; all three Bari decisions return zero. |
| OpenGA `cds-sentenze`, `cds-ordinanze`, `cds-decreti` annual JSON | Fetched through the 28 July 2026 resources. Located CdS n. 7994/2023, decree n. 552/2025, order n. 755/2024, and n. 5612/2026.[3][4][5] |
| CdS n. 7994/2023, `_11.html` | HTTP 200, 46,134-byte XML. Saved and hashed.[8] |
| CdS decree n. 552/2025 | `_01` through `_16` and `_18` through `_20` were 1,535-byte 404 shells; `_17.html` returned the 4,286-byte official XML. Saved and hashed.[9] |
| CdS n. 5612/2026, `_11.html` | HTTP 200, 70,074-byte XML. Saved and hashed.[10] |
| CdS order n. 755/2024 filename variants | Existing corpus result remains `official_metadata_confirmed`, `text_unfetched`; no new official full text located. |
| Secondary date cross-checks | Used only for the four pre-OpenGA publication dates. No secondary text supplies a holding used in the rule analysis. |

---

## Findings

1. The TAR Lecce sentence corpus is complete at 32 official full texts.
2. Only n. 573/2018 directly construes a Xylella plant-removal rule, and it applies the predecessor Decision 2015/789 regime.
3. The fifteen-decision damages line is context for Wedge 1. It rejects liability but does not alter current parcel duties.
4. No Lecce decision changes current Art. 7, Art. 13, monumental-derogation, AGEA reconversion, or vector-duty logic.
5. CdS n. 7994/2023 is the load-bearing new merits authority: applicant-entity identity and application-date proof control the Art. 6 `Principio 4` IAP/CD premium.

## Immediate next 5 steps

1. Add CdS n. 7994/2023 to the Art. 6 rule evidence because it is final and controls applicant identity.
2. Keep D.Lgs. 102/2004 indemnity, PSR 4.1.C investment aid, and D.I. 2484/2020 Art. 6 in separate measure families because the courts apply different notices and criteria.
3. Monitor CdS RG 3662/2026 and RG 4939/2026 because they are the only unresolved appeals against materially Xylella-specific Lecce judgments.
4. Preserve n. 573/2018 as historical support, not as the source of current Art. 7/13 geography.
5. Do not encode the damages line as a positive compliance rule because it decides liability and causation, not parcel eligibility.

## Telos

**Reduce the projected Xylella loss — €1.86–5.17B unreplanted against €0.59–1.57B with replant.** This corpus strengthens source-cited parcel legal state and aid scoring while preventing compensation, PSR, and phytosanitary rules from being merged into wrong advice.

## Sources

[1] https://openga.giustizia-amministrativa.it/dataset/tar-puglia-lecce-sentenze — OpenGA — TAR Puglia Lecce Sentenze
[2] https://www.giustizia-amministrativa.it/web/guest/dcsnprr — Giustizia Amministrativa — Decisioni e pareri
[3] https://openga.giustizia-amministrativa.it/dataset/cds-sentenze — OpenGA — Consiglio di Stato Sentenze
[4] https://openga.giustizia-amministrativa.it/dataset/cds-ordinanze — OpenGA — Consiglio di Stato Ordinanze
[5] https://openga.giustizia-amministrativa.it/dataset/cds-decreti — OpenGA — Consiglio di Stato Decreti
[6] https://mdp.giustizia-amministrativa.it/visualizza/?nodeRef=&schema=tar_le&nrg=201700693&nomeFile=201800573_01.html&subDir=Provvedimenti — TAR Lecce sez. III n. 573/2018
[7] https://mdp.giustizia-amministrativa.it/visualizza/?nodeRef=&schema=tar_le&nrg=202400052&nomeFile=202501439_01.html&subDir=Provvedimenti — TAR Lecce sez. III n. 1439/2025
[8] https://mdp.giustizia-amministrativa.it/visualizza/?nodeRef=&schema=cds&nrg=202302498&nomeFile=202307994_11.html&subDir=Provvedimenti — Consiglio di Stato sez. VI n. 7994/2023
[9] https://mdp.giustizia-amministrativa.it/visualizza/?nodeRef=&schema=cds&nrg=202308982&nomeFile=202500552_17.html&subDir=Provvedimenti — Consiglio di Stato sez. VI decreto n. 552/2025
[10] https://mdp.giustizia-amministrativa.it/visualizza/?nodeRef=&schema=cds&nrg=202508575&nomeFile=202605612_11.html&subDir=Provvedimenti — Consiglio di Stato sez. VI n. 5612/2026
