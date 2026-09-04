# Consultant report adjudication — `consultant_universe_report.md`

Scope: everything in the report except the ST1/multiplex geography correction, which Connor verified himself and which is settled.

Method: the report's inline tokens (`citeturn25search6`, `fileciteturn4file0`) are not references. They are artifacts of the tool that produced the report. Every claim carrying only such a token starts UNVERIFIED. This file re-fetches the underlying sources.

Evidence classes are ordered as the brief requires: CLASS 3 first.

---

## CLASS 3 — ASSERTED FROM MODEL MEMORY, NO FETCHED SOURCE

These statements appear in this brief but rest on reasoning, on secondary reporting, or on the repo's own prior work rather than on a primary source I fetched in this session. Treat each as a verification task, not a finding.

1. **TAR Puglia sentenza n. 655/2026 (annulment of DGR 1073/2025 and DGR 1143/2025 on non-monumental olive felling authorisations).** I have three independent secondary reports (BariToday citing ANSA, salviamoilpaesaggio.it, ostuninews.it) and one law-reporter index entry (ambientediritto.it, "TAR PUGLIA, Bari – 29 maggio 2026"). I did not fetch the judgment text. The quoted holdings ("La sostituzione integrale dell'oliveto con altra coltura … NON migliora il fondo olivicolo, ma lo cancella") come from a campaign group's press release, not from the court.
2. **Consiglio di Stato cautelar order in the Monopoli monumental-olive matter (2024).** Reported by LecceCronaca.it only. No case number located. No primary fetched.
3. **Annual act counts for the Sezione Osservatorio Fitosanitario.** My per-year maxima (2019 ≥ 250, 2020 ≈ 184, 2021 ≈ 137, 2022 ≥ 127, 2023 ≥ 146, 2024 ≥ 158, 2025 ≥ 163, 2026 ≥ 120 by July) are read off act numbers I encountered incidentally in fetched documents and search results. They are lower bounds observed, not an enumeration. The corpus estimate in Claim 6 is built on them and inherits the uncertainty.
4. **Claim that nursery supply is not currently refusing cooperative orders.** I found no fetched evidence of a supply shortage and no fetched evidence of adequate supply. Absence of evidence, stated as such.
5. **Repo-internal facts I reuse without re-fetching**: the Art. 6 status at 30 Sep 2024 (€55M committed, 1,889 beneficiaries, 938,281 plants, 8,185.70 ha, €17M disbursed) from `references/verified-anchors.md`; the AGEA "phantom plantings" figures; TAR Puglia Bari sez. III 25/03/2026 n. 384. These were verified in earlier sessions, not in this one.

Everything below CLASS 1 was fetched in this session.

---

## CLASS 1 — QUOTED FROM A PRIMARY SOURCE I FETCHED

### C1-1 — The €222M figure, and its state

URL: `https://press.regione.puglia.it/-/piano-di-rigenerazione-olivicola-lo-stato-di-attuazione` (Regione Puglia press office, published 22 July 2024)

Verbatim, assessor Donato Pentassuglia:

> "In questo momento non ci sono domande di anticipazione o domande di saldo in istruttoria a valere sull'articolo 6 – Reimpianto ulivi zona infetta del Piano di Rigenerazione Olivicola – ha sottolineato l'assessore Pentassuglia – la misura che ha la seconda dotazione più importante del Piano e per la quale **servirebbero in totale 222 milioni di euro per coprire tutte le 9.186 richieste di contributo**."

Same page, verbatim:

> "Ad oggi la Regione Puglia ha impegnato 181 milioni di euro e erogato 137 milioni di euro. Questo significa che lo stato di attuazione del Piano di Rigenerazione olivicola è al 76% per gli impegni di spesa e al 58% per le erogazioni."

The conditional `servirebbero` ("would be needed") is decisive. The figure is required demand, not commitment.

The same page contains an unflagged typo that a naive scraper would ingest: "La dotazione finanziaria a disposizione della Regione Puglia è di **237.300,00 euro**". Trade press covering the same briefing reports the intended figure as €237 million (`https://olivoeolio.edagricole.it/attualita/xylella-piano-di-rigenerazione-olivicola-lo-stato-di-attuazione/`). The official primary source is wrong by three orders of magnitude on one number and right on the others.

### C1-2 — Art. 6 envelope is no longer €80M

URL: `https://www.masaf.gov.it/flex/cm/pages/ServeAttachment.php/L/IT/D/1%252F7%252F4%252FD.5c3365c21efe9140b306/P/BLOB%3AID%3D24121/E/pdf` (MASAF rimodulazione decree, signed after Comitato di sorveglianza opinions of 20 Nov and 22 Dec 2025)

Verbatim, Articolo Unico comma 2:

> "A seguito della rimodulazione di cui al comma 1, la dotazione finanziaria dell'articolo 6 del decreto interministeriale n. 2484 del 6 marzo 2020 è incrementata di euro 1.271.242,00, per uno stanziamento complessivo pari a **euro 81.271.242,00**."

### C1-3 — Corte dei conti registration is a real, separate money state, and the report omits it

Same MASAF decree, verbatim:

> "VISTO il decreto del Ministro dell'agricoltura, della sovranità alimentare e delle foreste 6 maggio 2022, n.203829, **registrato alla Corte dei Conti in data 19/08/2022 al n. 948**, recante 'Rimodulazione risorse finanziarie dall'articolo 4 all'articolo 6…'"

URL: `https://www.regione.puglia.it/documents/736605/1003703/Report++31.05.2023.pdf` (Regione Puglia, state-of-play report to 31 May 2023), verbatim:

> "Il decreto di che trattasi (D.M. n. 203829 del 06/05/2022) è stato approvato il 5 maggio del 2022 ed è stato ammesso alla dalla Corte dei Conti il 19/08/2022 per divenire efficace solo nel settembre 2022. Il Ministero ha trasferito alla Regione le risorse economiche, pari a 20 Meuro, sull'articolo 6 soltanto il 6 dicembre 2022."

URL: `https://www.masaf.gov.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/14966`, verbatim:

> "Decreto interministeriale n. 2484, del 6 marzo 2020, con cui è stato approvato il 'Piano straordinario per la rigenerazione olivicola della Puglia', **ammesso alla registrazione alla Corte dei Conti il 17/04/2020 n. 188**."

Seven months elapse between signature and effectiveness. Ten months elapse before cash moves. The report's fourteen-state vocabulary has no slot for either transition.

### C1-4 — Call budget is stated in the avviso, and differs from the appropriation

URL: `https://www.regione.puglia.it/documents/42866/687205/Bando+consolidato+Reimpianto+ulivi+in+zona+infetta_+Misura+art.+6+D.I.+n.+2484+06.03.2020.pdf`

Verbatim, §5:

> "La dotazione finanziaria prevista per l'intervento ammonta a € 39.600.000,00 … di cui € 13.860.000,00 a valere sull'annualità 2020 e 25.740.000,00 a valere sull'annualità 2021."

Same document, §4:

> "Gli aiuti sono concessi per operazioni ricadenti esclusivamente nella 'zona infetta' relativamente alla sottospecie Pauca ceppo ST53 di Xylella fastidiosa, con esclusione della zona soggetta a misure di contenimento … così come individuate dalla Determinazione del Dirigente dell'Osservatorio fitosanitario … n. 59 del 21/05/2019."

The call freezes a 2019 geography. Today's SIT layer is not the eligibility geography for this call. That is the report's "funding geography snapshot" point, confirmed against the call itself.

### C1-5 — Reg. (EU) 2020/1201 structure: the report names the wrong chapter for the binding constraint

URL: `https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02020R1201-20241017` (consolidated text, 17.10.2024)

Chapter headings, verbatim: `CHAPTER VI — PLANTING OF SPECIFIED PLANTS IN INFECTED ZONES` (Art. 18); `CHAPTER VII — MOVEMENT WITHIN THE UNION OF SPECIFIED PLANTS` (Arts. 19–26).

Art. 18, verbatim:

> "The planting of specified plants in infected zones may only be authorised by the Member State concerned in one of the following cases: (a) those specified plants are grown in insect-proof sites of production free from the specified pest and its vectors; (b) those specified plants are planted or grafted in the infected zones listed in Annex III, but outside the area referred to in Article 15(2), point (a), and preferably belong to varieties assessed as being resistant or tolerant to the specified pest…"

Art. 15(2)(a), as replaced by Reg. (EU) 2024/2507, verbatim:

> "within an area measuring at least 2 km from the border of the infected zone with the buffer zone"

Art. 24(1), verbatim:

> "The competent authority may only authorise a production site for the purposes of Articles 19 and 21 where it fulfils all of the following conditions: (a) it is registered in accordance with Article 65 of Regulation (EU) 2016/2031; (b) it is a site physically protected against the specified pest and its vectors; (c) it has been subjected annually to at least two inspections by the competent authority…"

Art. 24(3), verbatim:

> "Each Member State shall establish and update a list of all sites authorised in accordance with paragraph 1. It shall transmit that list to the Commission and the other Member States immediately after establishing or updating that list."

The report points at Chapter VII (movement). The constraint that actually binds a replanting grower is Chapter VI, Art. 18 — an authorisation for *planting*, not for moving.

### C1-6 — The Commission's authorised-production-site page is a stub

URL: `https://food.ec.europa.eu/plants/plant-health-and-biosecurity/plant-health-rules/control-measures/xylella-fastidiosa/pest-free-production-sites-authorised-eu-demarcated-areas_en`

The page's entire substantive content, verbatim:

> "Pest free production sites, fulfilling the specific requirements laid down under Art. 19 of the Regulation (EU) 2020/1201
> - Italy (Apulia) – Last update 12 June 2022 – Contact details available to EU NPPOs
> - Portugal – Last update 11 July 2024 – Contact details available to EU NPPOs
> - Spain (Balearic Islands) – Last update 20 October 2020 - Contact details available to EU NPPOs"

Three lines. No site names, no geography, no counts. The Apulia entry is four years stale. Contact details are restricted to national plant protection organisations.

A second Commission page in the same section still describes the containment strip using the pre-2024 width — "planted in the infected zones subject to containment measures, but outside the 5 km strip adjacent to the buffer zone" (`https://food.ec.europa.eu/plants/plant-health-and-biosecurity/plant-health-rules/control-measures/xylella-fastidiosa_en`). The consolidated regulation says 2 km. A Commission explanatory page contradicts the Commission's own regulation.

### C1-7 — Puglia has already issued a standing Art. 18 planting authorisation

URL: `https://burp.regione.puglia.it/documents/20135/2470544/DET_48_3_5_2024.pdf` — DDS Osservatorio Fitosanitario 3 maggio 2024, n. 48, "Disposizioni per l'applicazione degli artt. 18 e 23 del Reg. UE 2020/1201".

Verbatim, dispositivo:

> "Di autorizzare l'impianto, ai sensi della lettera b) dell'art. 18 del Reg. UE 2020/1201, nella zona infetta dell'area delimitata a Xylella fastidiosa pauca di cui alla DDS 18 del 14/03/2024, ad esclusione della zona in cui si applicano misure di contenimento, delle seguenti specie: Olivo - varietà Lecciana che presenta caratteri di resistenza … Olivo - varietà Leccio del Corno che presenta caratteri di tolleranza…"

Verbatim, on plant passports and operator authority:

> "…disponendo che devono essere utilizzate esclusivamente piante accompagnate da passaporti delle piante conformi all'art. 83 del Reg. (UE) 2016/2031 … rilasciati da Operatori Professionali autorizzati conformemente all'articolo 89 del Reg. (UE) 2016/2031"

Verbatim, on movement inside the demarcated area:

> "Nelle aree in cui si applicano misure di: - contenimento di cui agli articoli da 12 a 17 del Reg. UE 2020/1201, non potrà essere rilasciata alcuna autorizzazione ai sensi dell'art. 23"

Verbatim, and this is the artefact the report missed entirely:

> "Nel caso di produzione/commercializzazione di piante olivo delle varietà 'FS17' e 'Leccino' in zona infetta le informazioni relative al sito in cui le piante verranno impiantante (**dati catastali**) devono essere inserite sul portale web istituzionale http://www.emergenzaxylella.it/portal/portale_gestione_agricoltura/impianti."

A regional obligation exists to register the cadastral location of every FS17/Leccino planting in the infected zone. That is a parcel-level, product-relevant dataset. The report does not mention it.

### C1-8 — RUOP is published, not gated

URL: `https://burp.regione.puglia.it/documents/20135/2140091/DET_25_17_3_2023.pdf` — DDS 17 marzo 2023, n. 25, "Autorizzazione all'uso del passaporto delle piante per gli operatori professionali (O.P.) registrati al R.U.O.P. della Regione Puglia, risultati conformi ai controlli in loco eseguiti nel corso del 2022".

The act's Allegato A is a published table of RUOP codes authorised to issue plant passports (IT-16-0003 … IT-16-1601). The act states, verbatim:

> "sarà pubblicato sul portale R.U.O.P. e sul BURP, con valore di notifica per gli O.P."

URL: `http://cartografia.sit.puglia.it/doc/osservatorio_fitosanitario/181_DIR_2021_00045_ALLEGATO_1.pdf` (HTTP 200, 1,051,831 bytes) — "ELENCO OPERATORI PROFESSIONALI (O.P.) registrati al RUOP della Regione PUGLIA alla data del 25 maggio 2021", with operator names.

URL: `http://cartografia.sit.puglia.it/doc/osservatorio_fitosanitario/181_DIR_2021_000108_ALL.1.pdf`, verbatim:

> "alla data del 07/09/2021, il numero totale di Operatori Professionali registrati al portale informatizzato del RUOP aventi centri aziendali nella regione Puglia e che hanno richiesto l'autorizzazione all'uso del Passaporto è di 599 (cinquecentonovantanove)."

RUOP is not machine-queryable, but it is published in named and coded form across BURP and the SIT document store. "Scattered/gated" understates it.

### C1-9 — The ARIF free-plant scheme excludes farmers

URL: `https://burp.regione.puglia.it/documents/20135/2612276/DEL_184_2025.pdf` — DGR n. 184/2025.

Verbatim, dispositivo point 1:

> "di affidare all'Agenzia Regionale attività Irrigue e Forestali (ARIF) il compito di produrre e distribuire varietà di olivo resistenti/tolleranti a Xylella fastidiosa, a titolo gratuito, **a soggetti che non siano imprenditori agricoli**, alle associazioni e agli enti pubblici, come forma di risarcimento alle popolazioni locali per il disagio ambientale e paesaggistico causato da Xylella fastidiosa…"

Verbatim, Allegato A:

> "La concessione riguarderà l'assegnazione al massimo di n. 100 piante, per ogni intervento/progetto, di dimensioni inferiori ai 70 cm di altezza e allevate in contenitori/vasi."

Verbatim, eligibility (confirmed on `https://press.regione.puglia.it/-/xylella-regione-affida-all-arif-la-concessione-gratuita-di-piante-di-olivo-resistenti-al-batterio`):

> "Soggetti pubblici o privati, non operatori economici, che non abbiano usufruito né hanno in essere domande per contributo al reimpianto."

Non-economic operators only, 100 plants maximum, and explicitly incompatible with an Art. 6 replant application.

### C1-10 — BURP acts publish SHA256 hashes of their own annexes

URL: `https://burp.regione.puglia.it/documents/20135/2798636/DET_82_11_5_2026.pdf` (HTTP 200, 1,090,310 bytes, 9 pages) — DDS Osservatorio Fitosanitario 11 maggio 2026, n. 82, delimitation update.

Verbatim, tail of the act:

> "ALLEGATI INTEGRANTI
> Documento - Impronta (SHA256)
> ALLEGATO 1.pdf - 26004cfcc20096ec7764955c737a73d4191d3a4ea7c2c6a0c7f140e2df94782b
> ALLEGATO 1 BIS.pdf - a48efc90d7b343c69c7928ce8d59049d143a2f4c08862291bc66cd78bd0d6b7e
> ALLEGATO 2.pdf - b6541357ddffebdff0e6d7cbe06198f63ff3e182baf1681349c1d5ae631f7266"

Verbatim, on production and publication:

> "Il presente atto, redatto attraverso la piattaforma CIFRA2, firmato digitalmente e adottato in unico originale…"

Verbatim dispositivo, showing the imperative-infinitive form:

> "• Aggiornare l'area delimitata a Xylella fastidiosa sottospecie pauca ST53 ex Salento ai sensi del Reg. UE 2024/2507, costituita da: • zona infetta; • zona infetta in cui si applicano misure di contenimento che comprende un territorio di larghezza di 2 chilometri… • focolai puntiformi in agro di Mola di Bari e Noci in cui si applicano misure di eradicazione; • zona cuscinetto…
> • Rappresentare con gli Allegati 1 e 1 bis … i limiti geografici territoriali…
> • Riportare nell'Allegato 2 … i riferimenti catastali…
> • Stabilire che in tutta la zona infetta in cui si applicano misure di contenimento definita con il presente provvedimento, si applicano le misure di cui agli articoli da 13 a 17 del Reg.(UE) 2020/1201 e smi;
> • Stabilire che nei focolai di Mola di Bari e Noci si applicano misure di eradicazione di cui agli articoli da 7 a 9 del Reg.(UE) 2020/1201 e smi.;
> • Dichiarare il presente provvedimento immediatamente esecutivo…"

### C1-11 — The act template is not stable across sezioni or across time

URL: `https://regione.puglia.it/documents/736605/1030020/DDS+n.+348+del+19.05.2022.pdf` (HTTP 200, 192,523 bytes, 4 pages) — DDS Sezione Gestione Sostenibile e Tutela delle Risorse Forestali e Naturali 19 maggio 2022, n. 348, graduatoria rectification.

Different heading vocabulary (`VISTA` / `PREMESSO che` / `DETERMINA`, no `VISTI ALTRESI'`). Different issuing section. No `ALLEGATI INTEGRANTI` SHA256 block. Its operative content, verbatim:

> "di procedere alla correzione dell'errore materiale, limitatamente alla presa d'atto del decesso del…"

and, from the recital:

> "è stata approvata la rettifica della graduatoria delle domande di aiuto individuali di cui all'Allegato 'A' … ed è stata determinata la presa atto delle rinunce a n. 9 domande di aiuto individuali e dei decessi dei titolari di n. 7 domande di aiuto individuali"

### C1-12 — BURP full-text search does not index the corpus

URL: `https://burp.regione.puglia.it/search?q=xylella` → HTTP 200. Response body, verbatim:

> "Non è stato trovato alcun risultato con le parole chiave indicate: **xylella**."

The BURP portal serves the PDFs but its Liferay search does not index their contents.

### C1-13 — The judicial corpus is real, layered, and already cited inside the acts

Court of Justice, Joined Cases C-78/16 and C-79/16, *Pesce and Others*, 9 June 2016 (`https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX%3A62016CJ0078`). Subject, verbatim:

> "Obbligo di procedere alla rimozione immediata delle piante ospiti, indipendentemente dal loro stato di salute, in un raggio di 100 metri attorno alle piante infette – Validità … Diritto a un indennizzo"

Court of Justice, Case C-443/18, *Commission v Italy (Bacteria Xylella fastidiosa)*, 5 September 2019 (`https://curia.europa.eu/juris/liste.jsf?num=C-443/18`). Case description, verbatim:

> "Failure of a Member State to fulfil its obligations … Article 7(2)(c) — Containment measures — Obligation immediately to remove infected plants within a 20-kilometre strip in the infected zone — Article 7(7) — Obligation to monitor — Annual surveys — Article 6(2), (7) and (9) — Eradication measures — **Persistent and general failure** — Article 4(3) TEU — Obligation of sincere cooperation"

Corte costituzionale, sentenza n. 74/2021 (`https://www.cortecostituzionale.it/actionSchedaPronuncia.do?anno=2021&numero=74`). Verbatim dispositivo:

> "1) dichiara l'illegittimità costituzionale dell'art. 26 della legge della Regione Puglia 30 novembre 2019, n. 52"

Verbatim massima:

> "La norma regionale impugnata dal Governo, nel consentire nelle zone dichiarate infette dal batterio della xylella l'impianto di qualsiasi essenza arborea in deroga ai vincoli paesaggistico-colturali … ha introdotto un'ipotesi di esonero dall'autorizzazione paesaggistica diversa da quelle contemplate dall'art. 149 cod. beni culturali"

TAR Puglia Bari sez. III, sentenza 24 marzo 2023, n. 546 (`https://www.doctrine.it/decisions/ittar8q1aocbn0wnpy2`), on the monumental-tree derogation. Verbatim:

> "Sono fondate, dunque, le censure che la ricorrente ha articolato a proposito della omessa considerazione, da parte della regione Puglia, della tutela che la stessa legislazione regionale – con la legge 29 marzo 2017, n. 4 - ha approntato in favore degli olivi monumentali o con caratteristiche di monumentalità, così come ubicati nella piana degli olivi secolari."

TAR Puglia Bari sez. III, sentenza 12 dicembre 2019, n. 1640 (`https://www.ambientediritto.it/giurisprudenza/tar-puglia-bari-sez-3-12-dicembre-2019-n-1640/`), on notification by albo pretorio. Verbatim:

> "La mancata notifica dell'ordinanza di abbattimento degli ulivi dichiarati infetti da Xylella fastidiosa al conduttore del fondo non costituisce ex se un vizio di legittimità dell'atto…"

And, decisively for the report's claim that courts are a source family: the regional acts themselves cite judgments in their recitals. Four separate Osservatorio determinations — DET 38/2019, DET 199/2019, DET 149/2020, DET 184/2020, all on `burp.regione.puglia.it` — carry the identical recital, verbatim:

> "Viste le sentenze n° 11850 del 30/11/2017 del TAR Lazio e n. 573 del 09/04/2018 del TAR Lecce che confermano '… non sussisteva un obbligo di avviso dell'avvio del procedimento relativo all'abbattimento delle piante di ulivo, che in alcun modo avrebbe potuto influire sull'esito dello stesso, attesa la superiore finalità del contenimento della diffusione ed eradicazione del batterio, …'."

### C1-14 — The replant call's landscape-derogation chain

Same bando PDF as C1-4, verbatim, quoting the MiBACT/MIPAAF/Regione protocol:

> "Le operazioni di reimpianto nelle aree vincolate ricadenti in zone infette (con esclusione della zona di contenimento) … possono essere ricondotte a pratiche agricole non soggette ad autorizzazione paesaggistica, ai sensi dell'art. 149, co. 1, lett. b), del D. lgs. 42/2004, alle seguenti condizioni: a) … sono reimpiantate unicamente cultivar di olivo resistenti o tolleranti … b) nelle operazioni di reimpianto sono salvaguardati tutti i beni diffusi caratterizzanti il paesaggio rurale (muretti a secco, lamie, specchie, trulli, cisterne pozzi …)"

and, verbatim:

> "Laddove il reimpianto non rispetti le suddette condizioni, gli interventi sono sottoposti alla procedura ordinaria di cui all'art. 146 del D. lgs. 42/2004."

---

## CLASS 2 — INFERRED FROM CLASS 1

### Claim 1 — The money state machine

**The €222M figure and its state: CONFIRMED.** C1-1 gives the exact number, the exact denominator (9,186 requests), the exact date, and the conditional mood. It is required demand against an envelope that was €80M at the time and is €81,271,242 now (C1-2). The oversubscription ratio is ≈ 2.7×.

**The state's source is weaker than the report implies.** The only public statement of aggregate requested demand is a press-office quotation of a spoken remark at a stakeholder table. There is no decree, no register extract, no published aggregate. The report's proposed canonical source for `requested` — "Application register / official aggregate" — does not exist in public form for this measure. The correct provenance class is *authority statement, unreconciled*, which is neither "primary act" nor "secondary press."

**On the vocabulary itself.** Judged against C1-2, C1-3, C1-4, C1-11 and the Art. 6 pipeline:

States with a genuine canonical source in the Puglia/AGEA context:

| State | Canonical source, verified |
|---|---|
| `appropriated` | L. 44/2019 art. 8-quater → D.I. 2484/2020; envelope now fixed by MASAF rimodulazione decree (C1-2) |
| `programmed` / `reprogrammed` | MASAF rimodulazione decrees, each naming the source article and euro amount (C1-2) |
| `call_budget` | the avviso, §5 (C1-4) |
| `admitted` | graduatoria act and its Allegato A (C1-11) |
| `conceded` | "provvedimento di concessione" — DDS 92/2026, DDS 110/2026 |
| `committed_accounting` | the impegno di spesa in the act, plus the ragioneria check, which the Region describes as a distinct waiting state |
| `liquidated` | anticipazione and saldo determinations; C1-1 confirms these are separately tracked ("domande di anticipazione o domande di saldo in istruttoria") |
| `revoked` | revoca acts exist as a category; I did not fetch one |

States without a canonical source, or mis-sourced:

- **`requested`** — no public register. Authority statement only (above).
- **`paid`** — the report routes this to "AGEA/SIAN payment record." For Art. 6 that is wrong. SIAN is the *application* portal ("Le domande di aiuto si presentano mediante compilazione e rilascio sul Portale Sian nell'apposita sezione denominata 'Rigenerazione olivicola Puglia D.I. 2484/2020'", FAQ PDF, `regione.puglia.it/documents/42866/347990/`). Payment is executed regionally. Routing `paid` to AGEA transparency for this measure produces a permanent empty set.
- **`recovered`** — no fetched act. The AGEA/GdF material is oversight reporting, not a recovery act.
- **`under_audit`** and **`contested`** — these are not states of money. They are states of a *proceeding about* money. Modelling them as MoneyEvent states means a single euro amount can be in two states at once, which the report's own state-machine framing forbids.

States the report omits and the evidence demands:

1. **`registered_by_audit_court` / `effective`.** C1-3: signed 5 May 2022, registered 19 Aug 2022, effective Sept 2022. An appropriation that is signed but unregistered is legally inert. This is the single most consequential missing state.
2. **`transferred`.** C1-3: ministry-to-region cash transfer, 6 Dec 2022, four months after effectiveness.
3. **`economies`.** The rimodulazione decree exists because residues arose on Artt. 16, 19 and 22. Economies are the input to reprogramming.
4. **`renounced` / `beneficiary_deceased` / `ranking_rectified` / `scorrimento`.** C1-11 shows a single act taking note of 9 renunciations and 7 deaths and rectifying the ranking. These move money between applicants without any of the report's fourteen states firing.

**Verdict on the vocabulary: PARTLY CONFIRMED, and over-elaborated at one end while under-specified at the other.** Twelve of fourteen states are real. Two (`under_audit`, `contested`) are category errors. Four to six genuinely load-bearing Italian states are missing, and their absence is what actually causes the failure the report is trying to prevent — money that appears appropriated but cannot be spent for seven months.

### Claim 2/3 — The D-2 reformulation

**Verdict: materially better than "every material number traces to a primary act", but the report's own source table contains at least two errors, and it misses a third category.**

Is there a financial fact where a decree is genuinely not the right source? Yes, three:

1. **Aggregate requested demand.** No decree states it. Only C1-1 does. A decree cannot state it because no administrative act aggregates unfunded applications.
2. **Cumulative disbursement.** "impegnato 181 milioni … erogato 137 milioni" (C1-1) is an accounting position, not an act. No single decree contains it.
3. **Legal effectiveness of an appropriation.** The Corte dei conti registration is stamped *on* a decree and recorded *outside* it. To learn that D.M. 203829/2022 became effective you must read either a later decree's recital or the MASAF page (C1-3). The decree that creates the money cannot tell you whether the money is usable.

Where Connor's rule survives and the report's table is wrong:

- **Payment.** For Art. 6 the operative record is a regional liquidation determination — an act. The report routes it away from acts to AGEA/SIAN, which does not hold it.
- **Procurement.** The report routes "procurement commitment" to ANAC/BDNCP. The largest plant-supply intervention in the corpus, DGR 184/2025 (C1-9), is an in-house entrustment to ARIF that states it "non comporta oneri aggiuntivi per il bilancio della Regione Puglia." No CIG, no contract value, no ANAC record. The act is the only source.

So the reformulation is not a distinction without a difference — it correctly separates payment from law in principle. But applied literally to this product's flagship measure it would degrade accuracy in two places. The right form of the rule is narrower than either version:

> Every material financial claim names the record that establishes it, the administrative state that record proves, and whether that record is public, authority-stated, or absent.

The third category — **authority-stated, unreconciled** — is what the €222M actually is, and neither Connor's rule nor the report's has a slot for it.

### Claim 3 — Plant movement and nursery regime

**Verdict: PARTLY CONFIRMED. The omission is real. The framing of its importance is wrong.**

What the report gets right: the regime exists, it is legally distinct from removal, and Wedge 1 does not model it. Confirmed by C1-5 and C1-7.

What the report gets wrong:

1. **It names the wrong chapter.** Movement (Chapter VII) governs nurseries. Planting (Chapter VI, Art. 18) governs growers. For a cooperative replanting after felling, Art. 18 is the operative provision (C1-5).
2. **The Commission source it points at is empty.** Three lines, four-year-old Apulia entry, contacts restricted to NPPOs (C1-6). It cannot become a data dependency.
3. **The constraint is already discharged in Puglia and is static, not per-parcel.** DDS 48/2024 (C1-7) is a standing authorisation covering Leccino, FS-17, Lecciana and Leccio del Corno across the whole infected zone outside containment. There is no per-application authorisation step for the grower. The engine needs a table of four cultivars and one geographic exclusion, not an acquisition programme.
4. **In-kind supply does not reach the customer.** DGR 184/2025 (C1-9) excludes imprenditori agricoli, caps at 100 plants, and excludes anyone with a replant application. For the cooperative persona this scheme is legally unavailable. The report presents it as altering replant economics; for this customer it alters nothing.
5. **RUOP is more accessible than either the report or the repo says.** Coded and named lists are published on BURP and the SIT document store (C1-8). Not queryable, but scrapeable.

Where plant material *is* binding, and the report does not say so:

- Inside the 2 km containment strip, planting of resistant olives is not authorised at all (C1-7 excludes it; C1-5 Art. 18(b) excludes the Art. 15(2)(a) area). A parcel there gets a felling duty and no replant path. That is a legal answer the engine must give.
- The Art. 6 call requires replanting at least as many trees as were removed, capped at 300 trees/ha, with plants of authorised cultivars only (bando §§ 8–9). Cultivar legality is therefore an *eligibility criterion of the call*, not a separate movement problem.

On supply as an economic constraint: I found no fetched evidence either way. Coldiretti's "poco più di 3 milioni" replanted against "21 milioni di piante infette" (`quotidianodipuglia.it`, Apr 2025) is trade-association commentary quoted in press, not a supply measurement. See CLASS 3 item 4.

**The genuinely valuable finding in this area is one the report missed**: DDS 48/2024 mandates cadastral registration of every FS17/Leccino planting in the infected zone on `emergenzaxylella.it/…/impianti` (C1-7). That is a parcel-keyed regional dataset about actual replanting, and it is directly on the critical path.

### Claim 4 — Judicial and audit precedent

**Verdict: CONFIRMED, and the corpus is larger and more load-bearing than the report suggests.**

Layers found, with at least one decision each, all fetched or indexed in this session:

| Layer | Decisions located | Load-bearing for this engine? |
|---|---|---|
| CJEU | C-78/16 + C-79/16 *Pesce* (2016); C-443/18 *Commission v Italy* (2019) | Yes. *Pesce* validates the removal duty and holds no compensation regime is required by EU law — directly relevant to how the engine phrases Art. 7/13 duties. C-443/18 establishes persistent Italian non-compliance. |
| Corte costituzionale | sent. 74/2021 | **Yes, and it is not in the build.** It struck down LR Puglia 52/2019 art. 26, which had exempted replanting in infected zones from landscape authorisation. The Art. 6 bando's landscape-derogation chain (C1-14) rests on art. 149(1)(b) D.lgs. 42/2004 and a ministerial protocol, not on the struck-down regional article. An engine that tells a cooperative "no paesaggistica needed" must cite the protocol and the conditions, not a regional shortcut. |
| Consiglio di Stato | cautelar order, Monopoli monumental olives, 2024 | Probably. Not fetched (CLASS 3 item 2). |
| TAR Puglia (Bari) | 1640/2019; 546/2023; 1007/2023; 655/2026; 384/2026 (repo) | Yes. 546/2023 annuls a monumental-tree estirpazione for failure to consider LR 4/2017 art. 8(7-bis) alternatives. 1640/2019 settles that albo pretorio publication satisfies notification. 1007/2023 shows a challenge going *improcedibile* because a later delimitation act moved the parcel — a supersession effect the engine must model. |
| TAR Puglia (Lecce) | 573/2018; 458/2026; 497/2026 | Partly. 458/2026 is a damages action against the State, MIPAAF and Regione for the infection itself — outside the engine's scope. |
| TAR Lazio | 11850/2017 | Yes, procedurally: cited in the acts. |

Size: I count **at least a dozen** distinct decisions with visible relevance, spanning 2016–2026, across five fora. The true corpus is larger; TAR Puglia issued at least six cautelar orders on Ostuni monumental olives in a single day in May 2022 (ANSA, 9 May 2022), so interlocutory decisions alone run to dozens.

The strongest argument for the report's position is not the count. It is C1-13: **the Osservatorio's own determinations quote judgments verbatim in their recitals**, and have done so identically across at least four acts from 2019 to 2020. Judicial holdings are already inside the act corpus the build ingests. Not modelling them means the engine reads a recital it cannot represent.

**Corte dei conti: two distinct roles, and the report conflates them.**
- *Preventive control* (registration of decrees) is confirmed and load-bearing (C1-3). This is not "audit findings"; it is a validity gate.
- *Control on management* (relazioni di gestione) — the Puglia regional control section publishes these (e.g. delib. 163/GEST/2024 on PNRR/PNC implementation). I found **no** Corte dei conti *gestione* report specifically on Xylella spending. That is an unverified gap, not a negative finding.

### Claim 5 — The legal event ledger

**Verdict: PARTLY CONFIRMED. Extraction is more feasible than a sceptic expects, and less feasible than the report assumes.**

Arguments for feasibility, from C1-10:

- The dispositivo is a bulleted list of imperative infinitives: `Aggiornare`, `Rappresentare`, `Riportare`, `Stabilire`, `Dichiarare`, `Dare atto`, `Trasmettere`, `Pubblicare`. Verb-first, one clause per bullet. This is close to a controlled vocabulary.
- Acts are machine-generated by the CIFRA2 platform and digitally signed.
- **Acts publish SHA256 hashes of their own annexes.** The report proposes a `creating_act_sha256` field computed by the ingester. The stronger design is to read the authority's own published hash and treat a mismatch as a product state. The report did not notice this.
- The recital enumerates every prior act in force with its number and date — the AD→act attribution route the repo already uses.

Arguments against feasibility, from C1-10 and C1-11:

- **The template is not stable.** DDS 348/2022 (different sezione, three years earlier) uses `VISTA`/`PREMESSO che`/`DETERMINA`, has no `ALLEGATI INTEGRANTI` block and no hashes. A parser tuned on 2026 Osservatorio acts will not read 2022 funding acts. The corpus spans at least two templates and probably more across thirteen years.
- **The legally decisive content is not in the dispositivo.** DDS 82/2026's dispositivo says "Riportare nell'Allegato 2 … i riferimenti catastali". The parcel list lives in a separate PDF whose structure is a comune/foglio table with a `*` convention for partial fogli. Extracting it is table parsing, and the repo has already hit CID-font mojibake on DGR annexes.
- **The report's event vocabulary does not cover what these acts do.** DDS 82/2026's core operative sentence is "Stabilire che in tutta la zona infetta in cui si applicano misure di contenimento … si applicano le misure di cui agli articoli da 13 a 17". That attaches a *regime* to a *zone*. There is no `attaches_regime` event in the report's list. Likewise `Dichiarare … immediatamente esecutivo` (effectiveness), the publication-as-notification clause, and DDS 348/2022's rectification, renunciation and death events. Roughly a third of the operative sentences in the two acts I read have no matching event type.

**Recommendation.** Adopt `LegalAct` + `LegalActAttachment` with the *published* SHA256 — that part is free and strictly better than what the build has. Do not replace hand-authored `Zones`, `Measures` and `FundingWindows` with derived events in Wedge 1. The build holds 23 decrees and one persona. Full event-sourcing buys historical reconstruction, which Wedge 1 does not compute, at the cost of a parser that must survive two-plus templates and annex table extraction. That is D1 and D8: it grows the unit.

### Claim 6 — Scale of the act corpus

**Method.** Three independent estimates, all bounded below by acts I actually saw.

1. *Sezione Osservatorio Fitosanitario, by annual act number.* Determination numbers restart each year, so the highest number seen in a year is a lower bound on that year's output. Observed: 2019 ≥ 250 (DDS 250 del 23/12/2019); 2020 ≈ 184 (DET 184 del 21/12/2020); 2021 ≥ 137; 2022 ≥ 127; 2023 ≥ 146; 2024 ≥ 158; 2025 ≥ 163; 2026 ≥ 120 by 28 July. Take 130–250/year × 13 years (2013–2026) ≈ **1,700–3,000 acts**. Not all are Xylella — the section also handles other pests, RUOP, plant passports, phytosanitary products — but Xylella has driven the majority of its output since 2013.
2. *Giunta regionale (DGR).* Xylella-touching DGRs seen in this session alone: 1890/2018, 1178/2020, 343/2022, 770/2022, 1743/2022, 1866/2022, 570/2023, 591/2023, 994/2024, 1593/2024, 184/2025, 720/2025, 1073/2025, 1075/2025, 1143/2025. That is 15 encountered incidentally across eight years. A realistic rate is 5–15/year → **65–200 acts**.
3. *Funding-measure sezioni (Gestione Sostenibile, Competitività, Agricoltura).* The Piano has 14 measures, each with an avviso, graduatoria, rectifications, scorrimenti, concessions and liquidations. Art. 6 alone accounts for DDS 377/2020, 404/2020, 320/2022, 348/2022, 53/2026, 92/2026, 110/2026, 120/2026 and more. Estimate 20–50/year since 2019 → **150–400 acts**.

**Defensible answer: roughly 2,000–3,500 Regione Puglia acts touch Xylella since 2013.** Of those, the subset that is legally operative for what this engine computes — delimitation, prescription/felling, planting authorisation, vector obligation, funding window, ranking, concession, liquidation, monumental derogation — is plausibly **400–800**. The build holds 23. That is roughly 3–6% of the operative subset.

Caveat: estimate 1 is a lower bound built on eight incidentally-observed maxima (CLASS 3 item 3). It is the right order of magnitude, not a count.

**Enumerable by machine endpoint? No.** BURP full-text search returns zero results for "xylella" (C1-12). The document URLs embed a per-act folder id (2798636 for DDS 82/2026; 2735532 for DET 2 and 3 of 2026) that is not derivable from the act number. The SIT document store serves individual files but forbids directory listing (HTTP 403), and its filename scheme (`181_DIR_YYYY_NNNNN_*`) is not reconstructible from an act number — five guessed variants all returned 404.

**The realistic route is scraping the per-issue BURP sommari.** Each issue PDF carries a table of contents naming every determination by section, date and number. Enumerating issues by year and parsing their sommari yields a complete act index; the per-act PDF URL then has to be resolved from the issue page. This is a bounded scraping job, not an API.

### Claim 7 — What the report gets wrong or overstates

1. **Every non-geographic factual claim in the report is unverifiable as written.** The tokens are not citations. Of the claims I tested, the €222M and the Art. 6 oversubscription hold up exactly; the Commission production-site claim does not.
2. **"The Commission maintains specific information for authorised pest-free production sites in demarcated areas" is technically true and practically empty** (C1-6). Three lines, no data, Apulia four years stale, contacts NPPO-only. The report cites it twice as a foundation for an "acquisition program."
3. **The report cites Chapter VII for a grower-side constraint that lives in Chapter VI** (C1-5). Anyone implementing from the report will build the nursery movement model and miss Art. 18, which is the provision that actually determines whether a parcel can be replanted.
4. **The MoneyEvent vocabulary omits the Corte dei conti registration gate** (C1-3). A state machine designed to prevent conflating "appropriated" with "spendable" omits the exact transition that separates them in Italian public finance.
5. **`under_audit` and `contested` are not money states.** They describe proceedings, not the euro. Including them lets one amount occupy two states simultaneously.
6. **The D-2 source table mis-routes payment and procurement** for this product's two most important flows (Claim 2/3 above).
7. **"Regione/ARIF programs have included distribution of resistant/tolerant plants to eligible recipients, which affects the economics of replanting" overstates the effect for this customer.** DGR 184/2025 excludes farmers, caps at 100 plants, and disqualifies anyone with a replant application (C1-9).
8. **"Replace hand-authored Zones, Measures and FundingWindows with a LegalEvent ledger" would make Wedge 1 worse.** Two templates, annex table extraction, and an event vocabulary that misses a third of the operative sentences (Claim 5). The extractable win — the authority's own published annex SHA256 — is available without the rewrite.
9. **The report's own source registry proposal repeats the failure it diagnoses.** It lists `known_omissions` as a field but supplies no mechanism for discovering an omission. The mechanism that actually works in this domain is the one the repo already uses: read a recent act's recital, which enumerates every prior act in force.
10. **Where the report is right and should be adopted verbatim**: do not equate provisional monumental designation with an Art. 7(3)/13(2) derogation without a cited Puglia mapping; separate `heritage_status` from `xylella_derogation_status`; separate `legal_applicability` from `applicant_eligibility`; separate `source_reported_landholder` from `applicant`/`beneficiary`/`order_addressee`; treat funding geography as versioned as of the call (C1-4 proves this — the Art. 6 call freezes the 21/05/2019 delimitation); and stop claiming the engine performs no legal interpretation.
11. **One thing the report should have caught and did not**: the Regione's own press page states the regional allocation as "237.300,00 euro" where it means €237.3 million (C1-1). Any ingester that reads official press pages as structured figures will ingest that error. This is a concrete argument for the report's own "secondary context, never engine input" rule — applied to an *official* source.

---

## FETCH LOG — attempted and failed

| URL | Failure mode |
|---|---|
| `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02020R1201-20250101` | HTTP 200, page renders, body reads "The requested document does not exist." No consolidation exists at that date. Recovered via `02020R1201-20241017`. |
| `https://burp.regione.puglia.it/search?q=xylella` | HTTP 200, zero results: "Non è stato trovato alcun risultato con le parole chiave indicate: xylella." PDF contents are not indexed. |
| `http://cartografia.sit.puglia.it/doc/osservatorio_fitosanitario/` | HTTP 403, 218 bytes. Directory listing forbidden. Individual files under the same path return HTTP 200. |
| `http://cartografia.sit.puglia.it/doc/osservatorio_fitosanitario/181_DIR_2021_00045.pdf` and four sibling patterns (`181_DIR_2021_000045.pdf`, `181_DIR_2021_00108.pdf`, `181_DIR_2024_00158.pdf`, `181_DIR_2019_00199.pdf`) | HTTP 404 on all five. The filename scheme is not reconstructible from section code + year + act number; the working URLs carry an additional suffix (`_ALLEGATO_1`, `_ALL.1`). |
| `https://www.giustizia-amministrativa.it/ricerca-decisioni?p_p_id=GaSearch_INSTANCE_ricerca&query=xylella` | HTTP 404. No documented query surface found. |
| `https://www.giustizia-amministrativa.it/web/guest/dcsnprr` | HTTP 200, 148,510 bytes, but the landing page only. No programmatic search endpoint located; the corpus estimate in Claim 4 therefore rests on third-party indexes (doctrine.it, ambientediritto.it) and on judgments cited inside the acts. |
| `http://www.sit.puglia.it/portal/portale_gestione_agricoltura/Documenti` | HTTP 302, 0 bytes, redirect not followed to content even with `-L`. |
| `http://www.emergenzaxylella.it/` | HTTP 302, 0 bytes. The portal that hosts the mandated planting registry (C1-7) did not resolve for me this session. |
| `https://burp.regione.puglia.it/bollettini` | HTTP 200, 197,285 bytes, but no per-issue index parseable from the landing page. Enumeration would require walking the year/issue navigation. |
| `https://curia.europa.eu/juris/liste.jsf?num=C-443/18` | HTTP 200 but JS-rendered; only case metadata extractable, not judgment text. Metadata was sufficient. |
| Corte dei conti *gestione* report specific to Xylella spending | Not located. Searches returned the Puglia control section's PNRR/PNC reports (delib. 163/GEST/2024) and Corte dei conti *preventive* registrations of MASAF decrees. Recorded as an unverified gap, not a negative. |

---

## PER-CLAIM VERDICTS

| # | Claim | Verdict | Strongest single piece of evidence |
|---|---|---|---|
| 1a | Regione Puglia stated in July 2024 that ~€222M is needed for all 9,186 Art. 6 requests | **CONFIRMED** | `press.regione.puglia.it`, 22 Jul 2024: "servirebbero in totale 222 milioni di euro per coprire tutte le 9.186 richieste di contributo" |
| 1b | That figure is requested demand, not committed money | **CONFIRMED** | The conditional `servirebbero` in the same sentence, against the same page's separate "impegnato 181 milioni … erogato 137 milioni" |
| 1c | The 14-state MoneyEvent vocabulary describes real, distinguishable administrative states | **PARTLY CONFIRMED** | MASAF rimodulazione decree: "registrato alla Corte dei Conti in data 19/08/2022 al n. 948" — the decisive state the vocabulary omits, while `under_audit`/`contested` are not money states at all |
| 2 | The D-2 reformulation is materially better than "every number traces to a primary act" | **PARTLY CONFIRMED** | Regione state-of-play report: decree signed 5 May 2022, effective Sept 2022, cash transferred 6 Dec 2022 — three facts, three different records, none inside the decree. But the report mis-routes `paid` to AGEA/SIAN, which for Art. 6 holds only the application portal |
| 3a | The plant-movement / nursery regime is a real omission from the Wedge model | **CONFIRMED** | Reg. 2020/1201 Chapter VI Art. 18 and Chapter VII Arts. 19–26, consolidated text 17.10.2024 |
| 3b | The Commission maintains usable material on authorised production sites | **FALSE** | The Commission page's entire content: three bullet lines, "Italy (Apulia) – Last update 12 June 2022 – Contact details available to EU NPPOs" |
| 3c | Plant-material availability and movement authorisation is a binding constraint for a replanting cooperative in Puglia today | **UNSUBSTANTIATED** | DDS 48/2024 is a standing blanket authorisation for four cultivars across the infected zone outside containment; DGR 184/2025 excludes farmers from in-kind supply; no fetched evidence of nursery refusal |
| 3d | RUOP is scattered/gated and needs an acquisition programme | **PARTLY CONFIRMED** | DDS 25/2023 publishes the authorised-passport RUOP code list on BURP; `181_DIR_2021_00045_ALLEGATO_1.pdf` (HTTP 200) publishes named operators. Scrapeable, not queryable |
| 4a | Courts and audit bodies are a first-class source family | **CONFIRMED** | Four Osservatorio determinations (DET 38/2019, 199/2019, 149/2020, 184/2020) carry the identical recital "Viste le sentenze n° 11850 del 30/11/2017 del TAR Lazio e n. 573 del 09/04/2018 del TAR Lecce" — judgments are already inside the act corpus |
| 4b | Other decisions are load-bearing for the specific measures this engine computes | **CONFIRMED** | Corte cost. 74/2021: "dichiara l'illegittimità costituzionale dell'art. 26 della legge della Regione Puglia 30 novembre 2019, n. 52" — the struck-down article exempted infected-zone replanting from landscape authorisation, the exact question the Art. 6 bando answers |
| 4c | Corte dei conti has issued audit findings on Xylella spending | **UNSUBSTANTIATED** | No *gestione* report on Xylella located. What is confirmed is the different, preventive-control role (registration of MASAF decrees) |
| 5 | BURP acts are structured enough to derive a LegalEvent ledger reliably | **PARTLY CONFIRMED** | DDS 82/2026 publishes `ALLEGATI INTEGRANTI / Documento - Impronta (SHA256)` and a verb-first dispositivo; DDS 348/2022 from a different sezione has neither, and both acts contain operative sentences with no matching event type |
| 6 | The corpus is far larger than 23 decrees | **CONFIRMED** — estimate 2,000–3,500 acts since 2013, of which 400–800 are operative for this engine | Observed per-year Osservatorio act maxima (2019 ≥ 250, 2024 ≥ 158, 2026 ≥ 120 by July), extrapolated over 13 years |
| 6b | The corpus is enumerable via a machine endpoint | **FALSE** | `burp.regione.puglia.it/search?q=xylella` → "Non è stato trovato alcun risultato". SIT directory listing → HTTP 403. Filename guessing → 404 × 5. Scraping per-issue sommari is the only route |
