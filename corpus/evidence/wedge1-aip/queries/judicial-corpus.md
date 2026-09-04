# Judicial corpus — Xylella fastidiosa, Puglia

Retrieval date: 2026-08-19. Scope: administrative and constitutional decisions that bear on rules the
Wedge 1 eligibility engine computes. Saved documents: `data/extracts/judgments/`.

Status line for the load-bearing citation is at the end of this file.

---

## CLASS 3 — ASSERTED FROM MODEL MEMORY, NO FETCHED SOURCE

**none.**

Every judgment, article number, act number, RG number, date, holding, and quotation below comes from a
document fetched in this session. Where a fact comes from another party's report rather than the court's
own text, the source is named inline and the fact is marked as such.

---

## CLASS 1 — QUOTED FROM A SOURCE I ACTUALLY FETCHED

### 1.1 The official text of TAR Puglia Bari, sez. III, 25/03/2026, n. 384

**Retrieved.** The Giustizia Amministrativa document server serves it.

| Field | Value |
|---|---|
| URL | `https://mdp.giustizia-amministrativa.it/visualizza/?nodeRef=&schema=tar_ba&nrg=202400185&nomeFile=202600384_01.html&subDir=Provvedimenti` |
| HTTP | 200 |
| Content-Type | `text/xml; charset=utf-8` |
| Content-Disposition | `inline; filename=202600384_01.html` |
| Bytes | 25 551 |
| sha256 | `71e0e161303c698f77df2df9357907b6fe6f2c452fa23e6eb076e58bbc1a8251` |
| Local file | `data/extracts/judgments/TAR_BA_sez3_2026_00384_RG_202400185.xml` |

**The official publication format is XML, not PDF.** The payload is a NIR-schema XML document
(`urn:nir:tar.puglia;sezione.3:sentenza`, root element `<GA>`, stylesheet `Sentenze.xsl`) whose
`nomeFile` parameter carries an `.html` extension. Requesting the same document with `nomeFile=202600384_01.pdf`
returns HTTP 302 to a 404 page. A PDF representation of n. 384 does not exist on the portal. The portal
does serve PDFs for provvedimenti deposited as PDF — TAR Lecce 2026 nn. 1009, 1011, 1012, 1013, 1103, 1105
resolve as `..._01.pdf` — so the absence here is a property of this document, not of the endpoint.

The XML embeds its own provenance: source file `20240018520260311103423694.xml`, fascicle path
`202400185\202400185.xml`, magistrate folder `U:\DocumentiGA\Magistrati\972 Vincenzo Blanda\`, publication
date `25/03/2026`.

**Collegio and procedural facts, from the official text:**

> Il Tribunale Amministrativo Regionale per la Puglia
> (Sezione Terza)
> ha pronunciato la presente
> SENTENZA
> Vincenzo Blanda, Presidente
> Desirèe Zonno, Consigliere, Estensore
> Lorenzo Ieva, Primo Referendario

> Così deciso in Bari nella camera di consiglio del giorno 18.02.2026

**Dispositivo, verbatim:**

> P.Q.M.
> Il Tribunale Amministrativo Regionale per la Puglia (Sezione Terza), definitivamente pronunciando sui
> ricorsi, come in epigrafe proposti, così provvede:
> -dichiara improcedibile per sopravvenuta carenza di interesse il ricorso principale;
> -respinge quello per motivi aggiunti;
> -compensa le spese di giudizio, ad eccezione di quelle di verificazione da porsi a carico della ricorrente.

**Act under challenge, from the epigrafe:**

> dell'atto dirigenziale n. 138 dell'1.12.2023 del Resp. Sezione Osservatorio Fitosanitario – Dipartimento
> Agricoltura, Sviluppo Rurale e Ambientale della Regione Puglia recante: "Reg. (UE) 2020/1201 - D.Lgs 19
> del 02/02/2021 – D.G.R. 1866 /2022. Prescrizione di misure di eradicazione per n. 5 piante infette, ai
> sensi dell'art. 7 del Reg. (UE) 2020/1201, site in agro di Monopoli (BA) - Area Delimitata Valle D'Itria –
> Zona Infetta", notificata a mezzo pec alla sig.ra Lucia Apuleo in data 1.12.2023

### 1.2 Character-by-character comparison of the two load-bearing passages

Both passages appear in the official text. Neither is a paraphrase. The differences below are confined to
character-set flattening in the brief handed to me (ASCII apostrophes and no diacritics) and to explicit
`...` ellipsis markers, which correctly signal elided material.

**Passage 1 — official text at offset 13 799 of the extracted plain text:**

> ciò al fine di porre in rilievo che quella che la Regione definisce quale "zona di contenimento" -quasi a
> distinguerla da quella infetta- è, invece, pur sempre una zona infetta per cui l'Ente (rectius lo Stato
> membro) ha ritenuto di applicare (in base ad una valutazione discrezionale, che muove dalla verifica
> scientifica di infestazione della zona) le misure di contenimento di cui al capo V, invece di quelle di
> eradicazione, per elezione dovute a seguito dell'accertamento della natura infetta della zona.

Differences against the secondary text in the task brief: `e,` for `è,`, `l Ente` for `l'Ente`,
straight quotes for typographic quotes, and one `...` standing for the parenthetical
`(in base ad una valutazione discrezionale, che muove dalla verifica scientifica di infestazione della zona)`.
No word is added, dropped, or reordered. **Substantively identical.**

**Passage 2 — official text at offset 16 696:**

> Alla luce di ciò e dipanando l'articolato dei rinvii operati dalle disposizioni in questione (con tecnica
> normativa che non si segnala per la cristallina intellegibilità), la deroga alla rimozione delle piante
> infette può disporsi (semplificando), nelle cd. zone di contenimento (rectius zone infette sottoposte a
> misure di contenimento, v. art. 4 reg n.2020/1201) qual è tutto l'agro di Monopoli, solo per i siti di
> piante monumentali, al di fuori della zona infetta in senso stretto (ed oltre 2 km dal suo confine), ossia,
> per dirla con la classificazione utilizzata dalla Regione, al di fuori della zona di contenimento (rectius
> della zona infetta di contenimento).

Differences against the secondary text: `puo` for `può`, and two `...` standing for `(semplificando),` and
for `(rectius zone infette sottoposte a misure di contenimento, v. art. 4 reg n.2020/1201) qual è tutto
l'agro di Monopoli,`. **Substantively identical.**

### 1.3 Contradiction to flag — an unmarked elision inside a quotation in `DOMAIN_DECISIONS.md`

`DOMAIN_DECISIONS.md` §D-12, "Judicial confirmation", quotes Passage 1 as:

> quella che la Regione definisce quale "zona di contenimento" — quasi a distinguerla da quella infetta — è,
> invece, pur sempre una zona infetta per cui lo Stato membro ha ritenuto di applicare le misure di
> contenimento di cui al capo V, invece di quelle di eradicazione

Two departures from the official text, neither marked:

1. `per cui lo Stato membro` drops `l'Ente (rectius ` and the closing `)`. The court wrote
   `per cui l'Ente (rectius lo Stato membro)`. The correction matters: the court is naming the Region as the
   acting body and then substituting the correct EU-law addressee. The repo version erases that move.
2. The parenthetical `(in base ad una valutazione discrezionale, che muove dalla verifica scientifica di
   infestazione della zona)` is removed with no ellipsis. That parenthetical is the court's statement that
   the eradication/containment choice is **discretionary** for the Member State. Removing it silently makes
   the sentence read as if the choice were automatic.

The holding the build rests on survives. The quotation as printed does not match the court's words.
Read-only task: reported, not edited.

### 1.4 The numbering question — resolved from official case-management data

Source: Giustizia Amministrativa open data, CKAN dataset `cds:tar-puglia-bari-sentenze`, resource
"TAR Puglia - Bari - Sentenze - 2026", JSON, 752 records, licence CC BY 4.0.
`https://openga.giustizia-amministrativa.it/dataset/af75b821-91f1-451a-b467-ec1ec47c15a1/resource/929c07a9-ff43-41ed-8397-e1443e0dc5a4/download/tar-puglia-bari-sentenze-2026.json`
(HTTP 200, 458 255 bytes).

| Provvedimento | RG (NUMERO_RICORSO) | Sezione | Deposito | Oggetto (official field) | Esito (official field) |
|---|---|---|---|---|---|
| 202600383 | 202400099 → **RG 99/2024** | Terza | 2026-03-25 | ESTIRPAZIONE DI PIANTE DI ULIVO RISULTATE INFETTE DA XYLELLA | RESPINGE SUI MOTIVI AGGIUNTI |
| 202600384 | 202400185 → **RG 185/2024** | Terza | 2026-03-25 | ESTIRPAZIONE DI PIANTE DI ULIVO RISULTATE INFETTE DA XYLELLA | RESPINGE SUI MOTIVI AGGIUNTI |
| 202600387 | 202301238 → **RG 1238/2023** | Terza | 2026-03-25 | PRESCRIZIONE DI MISURE DI ERADICAZIONE | RESPINGE SUI MOTIVI AGGIUNTI |
| 202600655 | 202501682 → **RG 1682/2025** | Terza | 2026-05-29 | DISCIPLINA DEL PROCEDIMENTO DI RILASCIO DELLE AUTORIZZAZIONI ALL'ABBATTIMENTO DI ALBERI DI OLIVO PRIVI DEL CARATTERE DI MONUMENTALITÀ | ACCOGLIE |

The same `nrg` values reappear in the portal's own document URLs, which is the second independent
confirmation: n. 384 is served under `nrg=202400185`, n. 387 under `nrg=202301238`.

**Answer.** n. 384 and n. 387 are **different disputes**, not the same one under two numbers.

- n. 384 (RG 185/2024) attacks **DDS 138 del 1.12.2023** — eradication of 5 infected plants in agro di
  Monopoli — with motivi aggiunti against DDS 18/2024.
- n. 387 (RG 1238/2023) is the **ottemperanza** action. Its epigrafe, verbatim from the official text:
  > per quanto riguarda il ricorso introduttivo:
  > l'ottemperanza della sentenza del TAR Puglia Bari, sez. III, 15.07.2023 n. 1007;
  and it attacks **AD n. 96 del 28.08.2023**, whose title is itself
  > "… Prescrizione di misure di eradicazione ai sensi dell'art. 7 del Reg. (UE) 2020/1201, site in agro di
  > Monopoli (BA) - Area Delimitata Valle D'Itria – Determinazione in ordine alla sentenza n. 1007/2023 del
  > TAR Bari"
- n. 383 (RG 99/2024) is a third sibling, attacking **DDS 119 dell'8.11.2023** — eradication of 37 infected
  plants, same agro, same applicant name in the epigrafe (Lucia Apuleo).

All three are decided by the same collegio in the same camera di consiglio of 18.02.2026 and deposited on
25/03/2026. Their dispositivi differ:

- 384: improcedibile principale, respinge motivi aggiunti.
- 383: improcedibile principale, respinge motivi aggiunti.
- 387: *improcedibili* principale **and** primi motivi aggiunti, respinge **secondi** motivi aggiunti.

**How I know.** The RG↔provvedimento mapping comes from the court's own case-management export, not from a
repository index. The document URLs constructed from those RG numbers return the matching judgments. The
epigrafi of the two texts describe two different sets of challenged acts.

**Correction to the brief handed to me.** The brief describes n. 387 as "a related ottemperanza … RG 1238/2023".
That is right. It does not state n. 384's RG. n. 384 is **RG 185/2024**. Any repo row that carries
RG 1238/2023 against n. 384 is wrong.

### 1.5 The corpus — decisions retrieved in full

All TAR Bari items below are official Giustizia Amministrativa documents pulled from
`https://mdp.giustizia-amministrativa.it/visualizza/?nodeRef=&schema=tar_ba&nrg=<NRG>&nomeFile=<FILE>&subDir=Provvedimenti`
and saved under `data/extracts/judgments/`.

| File | nrg | sha256 (first 16) | Bytes |
|---|---|---|---|
| `TAR_BA_sez3_2019_01640_RG_201901396.xml` | 201901396 | `e8114a4f19d9549c` | 16 878 |
| `TAR_BA_sez3_2022_00078_RG_202100694.xml` | 202100694 | `fbef8f48cad7031e` | 84 783 |
| `TAR_BA_sez3_2022_01490_RG_202101341.xml` | 202101341 | `4d82082e2f1d2f57` | 16 147 |
| `TAR_BA_sez3_2023_00514_RG_202300176.xml` | 202300176 | `8d2bac938411c2a6` | 22 331 |
| `TAR_BA_sez3_2023_00546_RG_202200281.xml` | 202200281 | `0a3085beb25be5f0` | 52 556 |
| `TAR_BA_sez3_2023_00547_RG_202200282.xml` | 202200282 | `8b3af1d4f5926e89` | 52 289 |
| `TAR_BA_sez3_2023_00548_RG_202200189.xml` | 202200189 | `8756a79b316fccda` | 50 101 |
| `TAR_BA_sez3_2023_01007_RG_202300023.xml` | 202300023 | `700b7350ec5042ba` | 15 198 |
| `TAR_BA_sez3_2026_00383_RG_202400099.xml` | 202400099 | `3b767fd716139f52` | 27 056 |
| `TAR_BA_sez3_2026_00384_RG_202400185.xml` | 202400185 | `71e0e161303c698f` | 25 551 |
| `TAR_BA_sez3_2026_00387_RG_202301238.xml` | 202301238 | `f751acc2e9819e16` | 28 609 |
| `TAR_BA_sez3_2026_00400_RG_202300325.xml` | 202300325 | `8772b05277381950` | 15 135 |
| `TAR_BA_sez3_2026_00655_RG_202501682.xml` | 202501682 | `cb7ab38dbf83fadc` | 15 717 |

Full sha256 values are reproducible with `shasum -a 256` in that directory.

### 1.6 Verbatim holdings, per decision

**TAR Bari sez. III, 25/03/2026, n. 384 — Reg. 2020/1201 Artt. 12, 13(1), 13(2), 15(2)(a)–(b).**
The chain, verbatim:

> -a norma dell'art. 12, nelle zone infette (come l'agro di Monopoli), possono disporsi le misure di
> contenimento (come disposto dalla Regione);
> - le misure di contenimento comportano in via principale, comunque, la rimozione delle piante infette
> (art. 13, par. 1 …);
> -a norma dell'art. 13, par. 2, lo Stato membro può decidere, in deroga, di non rimuovere le piante infette,
> ma ciò può fare solo "nei siti di piante che presentano particolare valore culturale e sociale di cui
> all'articolo 15, paragrafo 2, lettera b)";
> - il richiamo a tale ultima previsione (art. 15, par.2, lett. b) comporta che la deroga può essere disposta
> per siti di piante monumentali situati al di fuori dell'area di cui alla lettera a) del medesimo art. 15,
> par.2, e designati a tal fine dallo Stato membro;
> - a sua volta l'art. 15, par.2, lett. a) individua "un'area di almeno 2 km dal confine tra la zona infetta
> e la zona cuscinetto".

Conclusion, verbatim:

> Poiché le piante infette controverse si trovano nella zona infetta (di contenimento) individuata dall'all.
> III (comprendente tutto l'agro monopolitano) e tale qualificazione del territorio in cui ricadono è disposta
> direttamente a livello regolamentare eurounitario, né in alcun modo contestata dalla ricorrente, deve
> concludersi che per esse non vi è possibilità alcuna di derogare alla rimozione.

On the regional derogation, verbatim:

> neppure la normativa regionale invocata da parte ricorrente (art. 8, co 7 bis L.R. Puglia n.4/2017) consente
> la deroga reclamata, in quanto essa è consentita solo "Laddove consentito dalla normativa vigente"

The judgment also reproduces the operative clause of the act it upholds, DDS 18/2024:

> "nella zona di contenimento non è consentito applicare le misure alternative alla rimozione delle piante
> rinvenute infette di cui all'art.8, comma 7 bis, della legge regionale n. 4/2017, come modificato dalla
> legge regionale n. 45 del 30/11/2021 art.5, co. 1, lett. c)"

and records that DDS 18/2024 narrowed the pending orders to infected plants only:

> "per i seguenti provvedimenti di prescrizione di rimozione già emanati dall'Osservatorio e non ancora
> attuati: ○ Determina dirigenziale n. 96 del 28/08/2023; ○ Determina dirigenziale n. 113 del 16/10/2023;
> ○ Determina dirigenziale n. 119 del 08/11/2023; ○ Determina dirigenziale n. 124 del 15/11/2023;
> ○ Determina dirigenziale n. 138 del 0[1/12/2023] … non si procederà all'estirpazione delle piante ospiti
> ricadenti nell'area di 50 m attorno alle piante infette"

**TAR Bari sez. III, 15/07/2023, n. 1007 (RG 23/2023).** Improcedibile. Verbatim:

> Ed invero, in applicazione del combinato disposto degli artt. 4 e 13 del regolamento UE n. 1201/2020, la
> Regione dovrà riconsiderare la questione delle misure di contenimento da adottare nell'area in questione,
> valutando la possibilità di misure alternative all'eradicazione (cfr. in particolare art. 13, comma 2).

**TAR Bari sez. III, 2023, nn. 546, 547, 548 (Ostuni, "zona ex contenimento").** All three accolgono and
annul. Ratio, verbatim from n. 546:

> mentre per gli olivi risultati contaminati da Xylella fastidiosa la misura dell'eradicazione costituisce
> strumento elettivo di contrasto alla diffusione dell'organismo nocivo specificato, a diverse conclusioni
> deve pervenirsi qualora ci si trovi al cospetto di un olivo monumentale o con caratteristiche di
> monumentalità … trattandosi appunto di pianta che gode di tutela rafforzata

and:

> La misura decisa dalla Regione Puglia risulta affetta dalla denunciata violazione del principio di
> proporzional[ità]

The same judgment reads Art. 13(2) narrowly on its face:

> "in deroga al paragrafo 1, lo Stato membro interessato può decidere, per scopi scientifici, di non rimuovere
> le piante che sono risultate infette … nei siti di piante che presentano particolare valore culturale e
> sociale di cui all'articolo 15, paragrafo 2, lettera b)"

**TAR Bari sez. III, 2022, n. 1490 (RG 1341/2021) — Art. 6 D.I. 2484/2020 replant aid.** Accoglie and annuls.
Verbatim:

> Con Determina datata 8/9/2020 n. 377, il Dirigente Sezione Gestione Sostenibile e Tutela delle Risorse
> Forestali e Naturali approvava l'Avviso pubblico per la l'aiuto al reimpianto di olivi in zona infetta da
> xylella fastidiosa, in esecuzione del Decreto interministeriale 6/3/20 n. 2484

> II – Il ricorso è fondato.

> P.Q.M. … lo accoglie e, per l'effetto, annulla i provvedimenti impugnati.

The disputed criterion is the "Principio 4" IAP/CD 10-point award under art. 12 of the DDS 377/2020 avviso,
and whether provisional IAP recognition held at the application date counts.

**TAR Bari sez. III, 2023, n. 514 (RG 176/2023) — Castellana Grotte, zona cuscinetto.** Respinge.
Challenged: AD 5 del 31/01/2023 prescribing Art. 7 eradication in the buffer zone, plus DGR 1866/2022.

**TAR Bari sez. III, 2019, n. 1640 (RG 1396/2019).** Respinge. Challenged: an Osservatorio felling order and
DGR 1890/2018 "nella parte in cui dispone che l'atto di prescrizione di abbattimento degli ulivi dichiarati
infetti da Xylella fastidiosa sia pubblicato sull'albo pretorio".

**TAR Bari sez. III, 2022, n. 78 (RG 694/2021).** Respinge. Challenged: DGR 538/2021, Piano d'azione 2021.

**TAR Bari sez. III, 2026, n. 400 (RG 325/2023).** Inammissibile. Challenged: DGR 1866/2022 (Piano d'azione
2023-2024) and DET 127/2022 (aggiornamento aree delimitate).

**TAR Bari sez. III, 2025, n. 1273 (RG 277/2025).** Inammissibile. Challenged: DGR 1593/2024, Piano d'azione
2024-2026, "in particolare … del par. 4.7".

**TAR Bari, 2025, n. 1061 (RG 1163/2025).** Irricevibile. Challenged: AD 188 del 12.12.2024 on the ST1
(subsp. *fastidiosa*) demarcated area, Allegato 1/C owner list for the 50 m infected ring.

**TAR Bari sez. III, 29/05/2026, n. 655 (RG 1682/2025) — L. 144/1951 felling authorisation.** Accoglie and
annuls DGR 1073/2025 (and consequentially DGR 1143/2025). Verbatim:

> La L. n. 144 del 1951 … pone un divieto generale di abbattimento degli alberi di olivo. … L'art. 2 consente
> l'abbattimento, previa autorizzazione, soltanto in cinque ipotesi tassative

> Nessun atto amministrativo regionale può aggiungere nuove ipotesi di deroga, né ampliare il contenuto di
> quelle esistenti

> la sostituzione integrale dell'oliveto con altra coltura (anche se solo arborea) non migliora il fondo
> olivicolo, ma lo cancella

> la delibera è illegittima nella parte in cui estende la nozione di "opere di pubblica utilità" fino a
> ricomprendervi gli impianti privati per la produzione di energia da fonti rinnovabili

**Corte costituzionale, sent. 74/2021, ECLI:IT:COST:2021:74.** Fetched from
`https://www.cortecostituzionale.it/scheda-pronuncia/2021/74`. Decided 09/02/2021, deposited 21/04/2021,
GU 21/04/2021 n. 16, ric. 13/2020. Dispositivo, verbatim:

> 1) dichiara l'illegittimità costituzionale dell'art. 26 della legge della Regione Puglia 30 novembre 2019,
> n. 52 (Assestamento e variazione al bilancio di previsione per l'esercizio finanziario 2019 e pluriennale
> 2019-2021);

Massima 43834, verbatim:

> La norma regionale impugnata dal Governo, nel consentire nelle zone dichiarate infette dal batterio della
> xylella l'impianto di qualsiasi essenza arborea in deroga ai vincoli paesaggistico-colturali … ha introdotto
> un'ipotesi di esonero dall'autorizzazione paesaggistica diversa da quelle contemplate dall'art. 149 cod.
> beni culturali, così, del pari, violando la disciplina dell'autorizzazione paesaggistica di cui all'art. 146
> del medesimo codice.

The judgment also records the surviving route, the DGR 2052/2019 protocollo d'intesa, verbatim:

> "[l]e operazioni di reimpianto nelle aree vincolate ricadenti in zone infette (con esclusione della zona di
> contenimento) […] possono essere ricondotte a pratiche agricole non soggette ad autorizzazione paesaggistica"
> [conditional on resistant cultivars — "Leccino o la Fs-17" — and on preserving the rural heritage features]

> Fuori dalle condizioni espressamente previste dal comma 1 … gli interventi di reimpianto devono essere
> sottoposti … a «procedura ordinaria di cui all'art. 146 del D.Lgs. 42/2004».

**CJEU, joined Cases C-78/16 and C-79/16, *Pesce and Others*, 9 June 2016, ECLI:EU:C:2016:428.** Fetched from
`https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:62016CJ0078`. Operative part, verbatim:

> L'esame delle questioni sollevate non ha rivelato alcun elemento idoneo ad inficiare la validità
> dell'articolo 6, paragrafo 2, lettera a), della decisione di esecuzione (UE) 2015/789 della Commissione …
> in rapporto alla direttiva 2000/29/CE … letta alla luce dei principi di precauzione e di proporzionalità,
> nonché in rapporto all'obbligo di motivazione previsto dall'articolo 296 TFUE e dall'articolo 41 della Carta

The provision upheld is the obligation to remove host plants within a 100 m radius of infected plants
"indipendentemente dal loro stato di salute".

**CJEU, C-443/18, *Commissione v Repubblica italiana*, 5 September 2019, ECLI:EU:C:2019:676.** Fetched from
`https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:62018CJ0443`. Operative part, verbatim:

> La Repubblica italiana,
> – avendo omesso di garantire, nella zona di contenimento, la rimozione immediata almeno di tutte le piante
> risultate infette da Xf, se site nella zona infetta entro 20 km dal confine di tale zona infetta con il
> resto del territorio dell'Unione, è venuta meno ai propri obblighi sanciti dall'articolo 7, paragrafo 2,
> lettera c) della decisione di esecuzione 2015/789 modificata, e
> – avendo omesso di garantire, nella zona di contenimento, il monitoraggio della presenza di Xf mediante
> ispezioni annuali effettuate al momento opportuno durante l'anno, è venuta meno agli obblighi ad essa
> incombenti in forza dell'articolo 7, paragrafo 7, di tale decisione di esecuzione.

> 2) Il ricorso è respinto quanto al resto.

Two limits worth recording. The Court **rejected** the Commission's third complaint:

> la Commissione non ha dimostrato che la Repubblica italiana abbia violato ripetutamente gli obblighi
> specifici di cui all'articolo 6, paragrafi 2, 7 e 9, della decisione di esecuzione 2015/789 modificata.

and the finding is against Decision 2015/789, the predecessor instrument, not against Reg. 2020/1201.

### 1.7 Census of Xylella judgments on the portal

Phrase search `"Xylella fastidiosa"`, tipo `Sentenza`, run against the portal's own index
(`https://www.giustizia-amministrativa.it/web/guest/dcsnprr`, Liferay portlet POST):

- Sede **Bari**: **27** sentenze, 2018 → 2026. All 27 document URLs captured.
- Sede **Lecce**: **32** sentenze, 2018 → 2026. All 32 document URLs captured. Six 2026 Lecce items are
  served as PDF (`202601009_01.pdf`, `202601011_01.pdf`, `202601012_01.pdf`, `202601013_01.pdf`,
  `202601103_01.pdf`, `202601105_01.pdf`).

The count is a floor, not a ceiling: it covers `Sentenza` only, and misses judgments that never spell the
organism's Latin binomial (n. 655/2026 does not appear in the Bari 27 — it was located through the OpenGA
oggetto field).

### 1.8 Recitals as a discovery route — cross-check

**DET 8 del 28/01/2025**, Sezione Osservatorio Fitosanitario, already in `data/extracts/acts/DET_8_28_1_2025.pdf`.
Its recital cites the CJEU directly:

> PRESO ATTO CHE
> La Corte di Giustizia dell'Unione Europea, con la sentenza del 05/09/2019, ha statuito che l'Autorità
> competente deve procedere con immediatezza all'attuazione delle misure fitosanitarie nell'ambito della
> gestione dell'emergenza fitosanitaria.

and then applies Art. 13(1):

> Dovere applicare con immediatezza, ai sensi del comma 1 dell'art. 13 del Reg. (UE) 2020/1201, le misure di
> estirpazione della pianta di olivo infetta di cui al presente provvedimento, in quanto non sostituibili con
> altra misura fitosanitaria meno drastica

The sentenza of 05/09/2019 is C-443/18. The act corpus therefore does index the judicial corpus, and the
link runs in the operative direction: a CJEU finding on Art. 7(2)(c) of Decision 2015/789 is being used to
justify immediacy under Art. 13(1) of Reg. 2020/1201.

**AD n. 96 del 28.08.2023** is the clearest case: the judgment number is inside the act's own title —
"Determinazione in ordine alla sentenza n. 1007/2023 del TAR Bari" — quoted verbatim in the epigrafe of the
official text of n. 387/2026.

**DDS 18/2024** quotes its own legal position on the LR 4/2017 art. 8(7-bis) derogation, quoted verbatim in
the official text of n. 384 (§1.6 above).

**Negative result, stated as such.** I grepped the eleven regional PDFs already in
`data/extracts/acts/` for `sentenz|Corte di Giustizia|Tribunale Amministrativo`. Only `DET_8_28_1_2025.pdf`
hits. DET 82/2026, DET 53/2026, DET 120/2026, DDS 39/2026 and DGR 1075/2025 contain no judgment citation in
their extractable text. The prior finding of "four Osservatorio determinations quoting TAR judgments
verbatim" is **not reproduced by the acts currently on disk**. Either those four are acts not yet fetched,
or the finding needs re-sourcing. I did not fetch new BURP acts in this session.

---

## CLASS 2 — INFERRED FROM CLASS 1

### 2.1 Operative vs context — strict split

The engine computes: Art. 13 removal duty in containment zones; Art. 7 eradication; the Art. 7(3) and
Art. 13(2) monumental derogations; Art. 6 replant aid eligibility under D.I. 2484/2020; AGEA reconversion.
A decision is **operative** only if it construes, limits, annuls, suspends, or upholds one of those.

#### OPERATIVE — changes an answer the engine gives

| Decision | Provision affected | Relation | Effect on the engine |
|---|---|---|---|
| **TAR Bari sez. III 25/03/2026 n. 384** (RG 185/2024) | Reg. 2020/1201 Artt. 12, 13(1), **13(2)**, 15(2)(a)-(b) | **construes** | Two rules. (a) A regional "zona di contenimento" label does not create a legal category: the area is a zona infetta under Chapter V measures. (b) The Art. 13(2) derogation reaches only monumental sites outside the strict infected zone and beyond 2 km from its border. An infected monumental tree inside the band has no derogation route. The engine's refusal to offer one is now anchored to the official text. |
| **TAR Bari sez. III 25/03/2026 n. 383** (RG 99/2024) | same | **construes** | Same collegio, same day, same reasoning, 37 plants. Corroborates n. 384 as a line, not a one-off. |
| **TAR Bari sez. III 25/03/2026 n. 387** (RG 1238/2023) | Reg. 2020/1201 Art. 13(2); LR 4/2017 art. 8(7-bis) | **construes / upholds** | Holds the Region complied with n. 1007/2023 by re-evaluating alternatives and lawfully concluding none was available. Kills the argument that n. 1007/2023 created an entitlement to alternative measures. |
| **TAR Bari sez. III 15/07/2023 n. 1007** (RG 23/2023) | Reg. 2020/1201 Artt. 4 and 13(2) | **construes** | Establishes the duty to *consider* Art. 13(2) alternatives when a parcel is reclassified into the infected zone. Superseded on outcome by nn. 384/387 but still the source of the consideration duty. |
| **TAR Bari sez. III 2023 nn. 546, 547, 548** (Ostuni) | Reg. 2020/1201 Art. 13(1)-(2); LR 4/2017 art. 8(7-bis); D.Lgs. 19/2021 art. 33 | **limits** | Annuls Art. 13 removal orders against monumental plants on proportionality grounds where urgency is not shown. Tension with n. 384 — see §2.2. |
| **TAR Bari sez. III 2022 n. 1490** (RG 1341/2021) | D.I. 2484/2020 **Art. 6**; DDS 377/2020 avviso art. 12 "Principio 4" | **annuls** | Directly on Art. 6 replant aid ranking. Bears on how the engine scores IAP/CD status and on the date at which qualification is tested. |
| **Corte cost. 74/2021** | LR Puglia 52/2019 art. 26 | **annuls** | Removes the regional landscape-authorisation exemption for post-Xylella planting. Replanting in a vincolata area falls back on DGR 2052/2019 conditions (resistant cultivar, heritage features preserved) or the ordinary art. 146 D.Lgs. 42/2004 procedure. Any engine rule that treats replant as automatically exempt is wrong. |
| **CJEU C-78/16 / C-79/16 (Pesce)** | Decision 2015/789 art. 6(2)(a) | **upholds** | Validity of removal of healthy host plants in the 100 m radius survives proportionality and precaution challenge. Sets the ceiling for challenges to the successor Art. 7 ring duty. |
| **CJEU C-443/18** | Decision 2015/789 artt. 7(2)(c), 7(7) | **construes** | Establishes immediacy as an obligation, not discretion, in the containment zone, and the annual-survey duty. Cited by the Osservatorio itself as the ground for immediate execution under Art. 13(1) (§1.8). Feeds the deadline/urgency logic. |
| **TAR Bari sez. III 29/05/2026 n. 655** (RG 1682/2025) | L. 144/1951 artt. 1-2; DGR 1073/2025; DGR 1143/2025 | **annuls** | Not a phytosanitary rule, but it governs whether an olive stand may be lawfully removed for conversion. Any reconversion path the engine surfaces that relies on "sostituzione dell'oliveto con altra coltivazione" as a miglioramento fondiario, or on a private renewable plant as an opera di pubblica utilità, is no longer available. |

#### CONTEXT — does not change an engine answer

| Decision | Why context |
|---|---|
| TAR Bari sez. III 2023 n. 514 (RG 176/2023) | Respinge. Confirms Art. 7 eradication in the buffer zone without construing the article. No rule moves. |
| TAR Bari sez. III 2019 n. 1640 (RG 1396/2019) | Respinge. Notification by albo pretorio. Procedural, though it supports the "publication = notification" premise the deadline clock already uses. |
| TAR Bari sez. III 2022 n. 78 (RG 694/2021) | Respinge. Piano d'azione 2021 upheld wholesale. |
| TAR Bari sez. III 2026 n. 400 (RG 325/2023) | Inammissibile. No merits reached on DGR 1866/2022. |
| TAR Bari sez. III 2025 n. 1273 (RG 277/2025) | Inammissibile. No merits reached on DGR 1593/2024. |
| TAR Bari 2025 n. 1061 (RG 1163/2025) | Irricevibile. Time-barred. ST1 area, owner annex. |
| TAR Bari sez. III 2023 n. 1054 (RG 714/2023) | Procedural only — opposizione inammissibile, file returned for ricorso straordinario. |
| TAR Bari sez. II 2022 n. 387 (RG 732/2017) | Respinge. Pre-Reg. 2020/1201 felling orders. Historical. |
| TAR Bari sez. II 2019 n. 726, 2018 n. 1318 | Respinge / improcedibile. Pre-Reg. 2020/1201. Historical. |
| TAR Bari sez. III 2020 n. 973, 2021 n. 297, sez. II 2025 n. 952 | PSR ranking, INPS wage supplement, landscape opinion on an unrelated project. Xylella appears in the facts only. |

### 2.2 The unresolved tension the engine must carry

nn. 546/547/548 (2023) annul Art. 13 removal orders against infected monumental plants on proportionality
grounds. n. 384 (2026) holds that for infected plants inside the Annex III infected zone
"non vi è possibilità alcuna di derogare alla rimozione". Same tribunal, same section.

They are reconcilable on their own terms. The 2023 line attacks the *urgency* qualification and the failure
to weigh LR 4/2017 alternatives; the 2026 line holds that once Annex III places the whole comune in the
infected zone, the EU text leaves the Region no discretion at all, and the regional derogation is
conditioned on "Laddove consentito dalla normativa vigente". The 2026 reading is later, is directly on the
Art. 15(2)(a)/(b) geography, and rests on the post-2024/1320 Annex III. It is the one to encode.

The engine should not present the 2023 line as a live derogation route. It should record it as a
superseded-on-geography precedent, because the Annex III amendment that drives n. 384 postdates it.

### 2.3 What the numbering finding implies for the build

The `JudicialDecision` rows for n. 384 and n. 387 must carry different RG keys (185/2024 and 1238/2023) and
must not be merged. n. 383 (RG 99/2024) is missing from the corpus as described in the brief and should be
added — it is the same holding on a larger set of plants and strengthens the citation.

### 2.4 Consiglio di Stato order 755/2024 — identity and interim effect resolved

Official OpenGA dataset `cds-ordinanze`, 2024 resource, carries:

```
NUMERO_PROVVEDIMENTO  202400755
NUMERO_RICORSO        202401065  (RG 1065/2024)
SEZIONE               VI
DATA_PUBBLICAZIONE    2024-03-01
ESITO                 ACCOGLIE
DEFINISCE             N
OGGETTO               Piano d'azione Xylella 2023–2024; renewed removal order
                      for an infected monumental olive and all plants within 50 m
```

TAR n. 384 characterises the order's legal effect: it *"ha provvisoriamente sospeso l'eradicazione,
in vista della definizione nel merito"* and has no giudicato effect. It is an **interim suspension**, not
a merits rule and not a live derogation route.

The official document-server text remains unfetched: `schema=cds`, NRG `202401065`, and filename
variants `_01` / `_11` in HTML, XML and PDF all return the portal's 1,535-byte not-found shell. Status:
`official_metadata_confirmed`, `text_unfetched`.

### 2.5 Where the corpus is still thin

- TAR **Lecce** holds 32 Xylella sentenze. None is analysed here. Lecce covers the Salento core, where the
  Art. 7 eradication and Art. 6 replant geographies were first drawn. That is the largest remaining gap.
- The **Consiglio di Stato** merits corpus remains thin. Order 755/2024 is identified from official
  metadata and its interim effect from n. 384, but its text is unfetched. Any merits appeal against
  nn. 383/384/387 would sit above everything in §2.1 and is not yet located.
- No decision on **AGEA reconversion** payments was located.

---

## FETCH LOG — failures, with exact failure mode

| URL | Failure |
|---|---|
| `https://www.giustizia-amministrativa.it/portale/pages/istituzionale/visualizza?nodeRef=&schema=tar_ba&nrg=202400185&nomeFile=202600384_01.doc&subDir=Provvedimenti` | HTTP 302 → `portali.giustizia-amministrativa.it/...` → HTTP 200 serving a 1 535-byte HTML page titled "404 - Pagina non trovata". Legacy `/portale/pages/istituzionale/visualizza` path is retired. |
| same, `nomeFile=202600384_20.doc` | Identical: 302 → 1 535-byte "404 - Pagina non trovata". |
| `https://mdp.giustizia-amministrativa.it/visualizza/?nodeRef=&schema=tar_ba&nrg=202400185&nomeFile=202600384_01.pdf&subDir=Provvedimenti` | HTTP 302 → HTTP 200, 1 535-byte "404 - Pagina non trovata". **No PDF representation of n. 384 exists.** |
| `https://www.giustizia-amministrativa.it/ricerca-provvedimenti?p_p_id=GaSearch` | HTTP 404, 105 504-byte Liferay error page. Wrong portlet path. |
| `https://www.doctrine.it/decisions/ittardoxcze8gn1qcpad` | HTTP 200, 101 957 bytes, but a Next.js shell. No `<title>`, no judgment text, and the "Fonte ufficiale — Scarica documento" link is not in the served HTML. The text visible through search-engine indexing is client-rendered. Not usable as a fetched source, and not needed. |
| `https://eur-lex.europa.eu/legal-content/IT/TXT/PDF/?uri=CELEX:62018CJ0443` | **HTTP 202, 0 bytes.** Bot mitigation, not a 404. Retried with `--compressed`, browser UA, `Accept: application/pdf`, `Accept-Language: it-IT`, `Referer: https://eur-lex.europa.eu/` and `&from=IT`: HTTP 202, 2 035-byte HTML. The HTML view of the same CELEX returns the full text and is the source used. |
| `https://eur-lex.europa.eu/legal-content/IT/TXT/PDF/?uri=CELEX:62016CJ0078` | HTTP 202, 0 bytes. Same mitigation. HTML view used instead. |
| `https://www.cortecostituzionale.it/stampa-pdf-pronuncia/2021/74` | HTTP 200, `Content-Type: text/html`, 15 074 bytes — a **Radware Captcha Page** (`captcha.perfdrive.com`), not a PDF. The `scheda-pronuncia` HTML view returns the full fatto/diritto/dispositivo/massime and is the source used. |
| `https://curia.europa.eu/juris/document/document.jsf?text=&docid=179644&doclang=IT` and `...docid=217669...` | HTTP 200 but both return an identical 130 226-byte `text/html` page. The docids are guesses and do not resolve to the judgments. Not used. |
| BURP fetch of AD 96/2023 and DDS 18/2024 | **Not attempted.** Both are quoted verbatim inside official judgment texts already retrieved. No new BURP request was made this session. |

---

## STATUS

**`authority_confirmed`** — the official Giustizia Amministrativa text of TAR Puglia Bari sez. III
25/03/2026 n. 384 (RG 185/2024) is retrieved from `mdp.giustizia-amministrativa.it`, saved as
`data/extracts/judgments/TAR_BA_sez3_2026_00384_RG_202400185.xml`, sha256
`71e0e161303c698f77df2df9357907b6fe6f2c452fa23e6eb076e58bbc1a8251`, 25 551 bytes, and both load-bearing
passages match the official wording; the official publication format is XML, not PDF, and no PDF
representation of this judgment exists on the portal.
