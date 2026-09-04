# Planting rule (DDS 48/2024) and act-corpus corroboration

Read date: 2026-08-19. Retrieval by anonymous HTTP GET/POST. No authentication used anywhere.

Two questions. First, what DDS 48/2024 actually obliges, of whom, before any engine rule is
encoded. Second, whether the Regione Puglia act corpus can be counted by a route other than the
BURP sommario sweep.

Headline: the consultant attribution is wrong on three counts, and a second enumeration route
exists and disagrees with BURP by a factor of three.

---

## CLASS 3 — ASSERTED FROM MODEL MEMORY, NO FETCHED SOURCE

**none.**

Every act quotation below is from a PDF saved to
`data/extracts/acts-tier0/` and hashed. Every HTTP result below is a response this session
received. Where a fact is absent from what was fetched, it is stated as absent, not inferred.

---

## CLASS 1 — QUOTED FROM A SOURCE I ACTUALLY FETCHED

### 1.1 Frozen acts

| Act | URL fetched | Bytes | SHA-256 | Pages |
|---|---|---|---|---|
| DDS Osservatorio Fitosanitario 3 maggio 2024, n. 48 | `https://burp.regione.puglia.it/documents/20135/2470544/DET_48_3_5_2024.pdf` | 1,219,192 | `1bdb82ce5545285faefccb6209a2edb519df6b3ca0db67e35f464060ebad1ffe` | 10 |
| DDS Osservatorio Fitosanitario 3 agosto 2021, n. 75 | `https://www.regione.puglia.it/documents/42866/1877754/DDS+Osservatorio+Fitosanitario+n.+75+del+03.08.2021+_+BURP+n.+105+del+12.08.2021.pdf/1479adb9-47fb-fad6-fdab-0b5a359a4b21?t=1631610447116` | 198,860 | `bd02e992ca5d915f732990ecc2c502f3a564194e0750712ed11f0f7b23ab9a7e` | 5 |
| DDS Osservatorio Fitosanitario 18 novembre 2024, n. 158 | `https://burp.regione.puglia.it/documents/20135/2554373/DET_158_18_11_2024.pdf` | 2,604,981 | `3f8c274672be3b4a643f3bed4fa2928d362306d96231cd65c093b538c750918a` | 7 |
| DDS Osservatorio Fitosanitario 11 maggio 2026, n. 82 | `https://burp.regione.puglia.it/documents/20135/2798636/DET_82_11_5_2026.pdf` | 1,090,310 | `4ae654ecd49e41900b8ade099e53e8de9323573cdcceae285d1221014cd37e7b` | 9 |

Saved filenames: `DET_48_3_5_2024.pdf`, `DDS_75_3_8_2021.pdf`, `DDS_158_18_11_2024.pdf`,
`DDS_82_11_5_2026.pdf`, each with a `.txt` text extraction alongside.

DDS 48/2024 is published at BURP n. 38 del 9-5-2024. Its self-attestation, verbatim:

> "è composto da n. 8 (otto) facciate e dall'Allegato A costituito da n° 4 (quattro) facciate"

### 1.2 DDS 48/2024 — the DETERMINA, in full

The dispositivo has eight bullets. Reproduced verbatim, complete:

> "Di prendere atto di quanto espresso in narrativa, che costituisce parte integrante e
> sostanziale del presente atto e che qui si intende integralmente riportato.
>
> • Di confermare l'autorizzazione all'impianto, ai sensi della lettera b) dell'art. 18 del Reg.
> UE 2020/1201, nella zona infetta dell'area delimitata a Xylella fastidiosa pauca di cui alla
> DDS 18 del 14/03/2024, ad esclusione della zona in cui si applicano misure di contenimento, di
> piante specificate per Xylella fastidiosa sottospecie pauca risultate immuni,
> resistenti/tolleranti, di cui alla DDS 75/2021, in particolare:
> ○ olivo - varietà: Leccino e FS17 in quanto risultate resistenti/tolleranti a Xylella
> fastidiosa sottospecie pauca;
> ○ agrumi in quanto risultati immuni a Xylella fastidiosa sottospecie pauca;
> ○ pesco, susino e albicocco in quanto risultati immuni a Xylella fastidiosa sottospecie pauca;
> ○ mandorlo e ciliegio in quanto risultati a bassa suscettibilità a Xylella fastidiosa
> sottospecie pauca;
>
> • Di autorizzare l'impianto, ai sensi della lettera b) dell'art. 18 del Reg. UE 2020/1201,
> nella zona infetta dell'area delimitata a Xylella fastidiosa pauca di cui alla DDS 18 del
> 14/03/2024, ad esclusione della zona in cui si applicano misure di contenimento, delle seguenti
> specie:
> ○ Olivo - varietà Lecciana che presenta caratteri di resistenza a Xylella fastidiosa subspecie
> pauca
> ○ Olivo- varietà Leccio del Corno che presenta caratteri di tolleranza a Xylella fastidiosa
> subspecie pauca
> ○ Rosmarino (Salvia rosmarinus), Cisto (Cistus), Mirto (Myrtus communis), Alaterno (Rhamnus
> alaternus), Alloro (Laurus nobilis), Fillirea (Phillyrea latifolia), Geranio (Pelargonium), in
> quanto anche se risultate suscettibili presentano una bassa frequenza di infezione;
>
> • Di dare atto che l'Osservatorio, non avendo ancora a disposizione dati riferiti al lungo
> periodo, non esclude che nel tempo possano verificarsi problemi di tenuta della
> resistenza/tolleranza che influiscano sulla produttività;
>
> • Di dare atto che gli Operatori Professionali che producono le suddette specie in un sito
> ubicato in zona infetta e non autorizzato ai sensi dell'art. 19 del Reg. UE 2020/1201, possono
> produrre le specie innanzi indicate per il rimpianto rispettando le condizioni di cui agli art.
> 23 e 27 del suddetto Regolamento;
>
> • Di approvare l'allegato 'A' al presente provvedimento per formarne parte integrante e
> sostanziale che sostituisce l'allegato 1 della determina dirigenziale n. 16 del 02/03/2023 […]
>
> • Di trasmettere copia del presente atto:
> ○ al Comando Regionale Carabinieri Forestali – Puglia;
> ○ agli operatori professionali iscritti al RUOP;
>
> • Di dare atto che il presento provvedimento è immediatamente esecutivo;
>
> • Di pubblicare il presente provvedimento sul BUR Puglia."

**Machine check on the dispositivo.** A case-insensitive grep of the DETERMINA block for
`catast|emergenzaxylella|impianti|registra|comunica` returns **NO MATCH**. A grep of the whole
10-page document for `foglio` and `particella` returns **zero occurrences**. The string
`dati catastali` occurs exactly **once** in the whole act, at line 506 of the extraction, inside
Allegato A.

### 1.3 The one cadastral sentence, with its chapeau

Allegato A, section 5, verbatim and in full context. The chapeau that scopes the section:

> "**5. MOVIMENTAZIONE E TRACCIABILITÀ DELLE PRODUZIONI**
> Gli operatori professionali registrati al RUOP, autorizzati a rilasciare passaporti delle
> piante che, ispezionati, abbiano ricevuto la conformità e autorizzati ai sensi dell'art. 23 del
> Reg. UE 2020/1201, devono:
> - richiedere le analisi ufficiali preliminarmente alla commercializzazione comunicando la
> consistenza dei vegetali (piante specificate) presenti in azienda tramite PEC a:
> ruop.regione@pec.rupar.puglia.it […]
> - conservare per tre anni le informazioni per ogni lotto trasmesso o ricevuto dal produttore e
> dal destinatario sui sistemi di tracciabilità aziendali o dell'Osservatorio fitosanitario
> regionale utilizzando la procedura informatica "monitoraggio vivai" disponibile sul portale web
> istituzionale http://www.emergenzaxylella.it."

Immediately following, the sentence at issue:

> "Nel caso di produzione/commercializzazione di piante olivo delle varietà "FS17" e "Leccino" in
> zona infetta le informazioni relative al sito in cui le piante verranno impiantante (dati
> catastali) devono essere inserite sul portale web istituzionale
> http://www.emergenzaxylella.it/portal/portale_gestione_agricoltura/impianti."

Also in Allegato A, on the containment zone:

> "Nelle aree in cui si applicano misure di: - contenimento di cui agli articoli da 12 a 17 del
> Reg. UE 2020/1201, non potrà essere rilasciata alcuna autorizzazione ai sensi dell'art. 23"

And on the eradication zone:

> "ai sensi della lettera c) dell'art. 18 del Reg. UE Reg. (UE) 2020/1201, per come definito nel
> vigente Piano d'Azione, nella zona infetta in cui si applicano misure di eradicazione è
> autorizzato l'impianto di agrumi, pesco, albicocco, susino, in quanto risultate immuni a Xylella
> fastidiosa sub specie. Resta il divieto di impiantare e quindi movimentare, specie risultate
> tolleranti e le restanti specie specificate."

Sanction basis, Allegato A section 7:

> "L'Osservatorio Fitosanitario […] applica le sanzioni nei confronti dei soggetti risultati
> inadempienti a seguito dei controlli tecnici e/o documentali dei siti di autorizzati ai sensi
> dell'art. 23 a norma dell'art. 55 del D. Lgs 19 del 02/02/2021."

### 1.4 DDS 75/2021 — the operative text

The dispositivo, verbatim in relevant part:

> "- autorizzare, ai sensi della lettera b) dell'art. 18 del Reg. UE 2020/1201, l'impianto di
> piante specificate risultate immuni, resistenti, tolleranti o a bassa suscettibilità alla
> Xylella fastidiosa sottospecie pauca, nelle zone infette ad esclusione della zona di 5 km della
> zona infetta di cui alla DDS 69 del 27/07/2021 in cui si applicano le misure di contenimento, in
> particolare:
> olivo: varietà Leccino e FS17 in quanto risultate resistenti/tolleranti […]
> agrumi in quanto risultati immuni […]
> pesco, susino e albicocco in quanto risultati immuni […]
> mandorlo e ciliegio: in quanto risultati a bassa suscettibilità […]"

DDS 75/2021 carries one duty that DDS 48/2024 does **not** repeat:

> "- disporre che chiunque intende svellere gli oliveti per rimpianto deve chiedere
> l'autorizzazione ai Servizi Territoriali competenti per territorio, ai sensi della legge
> 14/02/1951 n° 144 che ha disciplinato l'abbattimento degli alberi di olivo."

DDS 75/2021 contains no cadastral registration duty and no reference to
`emergenzaxylella.it/…/impianti`. Its own publication clause names the trasparenza channel:

> "sarà pubblicizzato nella sezione "Amministrazione trasparente", sotto sezione "Provvedimenti
> dirigenti amministrativi" del sito www.regione.puglia.it."

### 1.5 Legal basis chain, as recited by the acts themselves

DDS 48/2024, PREMESSO CHE:

> "L'Osservatorio fitosanitario della Regione Puglia […] è l'Autorità fitosanitaria competente nel
> territorio regionale, ai sensi dell'art. 6 del Decreto legislativo 2 febbraio 2021, n. 19"

> "l'art. 18 del Reg. UE 2020/1201 dispone che l'impianto di piante specificate in zone infette
> può essere autorizzato dallo Stato membro interessato solo in uno dei casi seguenti: […] b. le
> piante specificate in questione appartengono di preferenza a varietà che si sono dimostrate
> resistenti o tolleranti all'organismo nocivo specificato e sono piantate nelle zone infette
> elencate nell'allegato III, ma al di fuori dell'area di cui all'articolo 15, paragrafo 2,
> lettera a)"

National concurrence, verbatim:

> "Il Comitato Fitosanitario Nazionale, nella seduta del 15 aprile 2024, ha valutato e ritenuto
> esaustiva la documentazione presentata dal Servizio fitosanitario della Regione Puglia […] ai
> sensi dell'articolo 18, paragrafo 1, lettera b) del Reg.(UE) 2020/1201"

> "Il Servizio Fitosanitario Nazionale con nota prot. n° 0179664 del 19/04/2024 ha condiviso
> l'autorizzazione alla piantagione delle due cultivar di olivo innanzi citate"

Also cited in the VISTI: Reg. (UE) 2016/2031, Reg. (UE) 2017/2313, Reg. di esecuzione (UE)
2023/1706, D.G.R. 1866 del 12/12/2022 and D.G.R. 570 del 26/04/2023 (Piano d'azione 2023-2025),
and DDS 18 del 14/03/2024 for the delimited area.

Regional law appears only in the delimitation acts, not in DDS 48/2024. From DDS 18/2024, quoted
in its own dispositivo:

> "Stabilire che nella zona di contenimento non è consentito applicare le misure alternative alla
> rimozione delle piante rinvenute infette di cui all'art.8, comma 7 bis, della legge regionale n.
> 4/2017, come modificato dalla legge regionale n. 45 del 30/11/2021 art.5, co. 1, lett. c)"

### 1.6 Supersession — searched, and what was found

No act adopted after 2024-05-03 amends, replaces or revokes DDS 48/2024's Art. 18 authorisation.
This was tested by enumerating **every** act of the Sezione Osservatorio Fitosanitario for
2021-2026 (939 acts) from the second route described in section 1.8, and filtering the `Oggetto`
field on `art. 18 | impianto | impianti | resistent | toller | Lecciana | Leccio del Corno | FS17
| Leccino`. 157 acts match across the whole period. Of the matches dated on or after 2024-05-03,
every one is either a funding act under art. 6 D.I. 2484/2020 ("Reimpianto olivi zona infetta"),
an art. 8 monumental-olive act, or an HR act. None touches Art. 18 authorisation.

What **does** move is the geographic operand DDS 48/2024 points at. Two later Osservatorio acts
redefine the delimited area that DDS 48/2024 incorporates by reference as "di cui alla DDS 18 del
14/03/2024":

| Act | Adopted | Oggetto (verbatim from the register) |
|---|---|---|
| DDS 158/2024 | 18-11-2024 | "Applicazione Reg. UE 2024/2507 di modifica del Reg. UE 2020/1201 - Aggiornamento dell'area delimitata a Xylella fastidiosa sottospecie Pauca ST53 - ai sensi dell'art. 4 del Reg. UE 2020/1201" |
| DDS 82/2026 | 11-05-2026 | "Aggiornamento dell'area delimitata a Xylella fastidiosa sottospecie pauca ST53 ex Salento - ai sensi dell'art. 4 del Reg. UE 2020/1201 e s.m.i." |

DDS 82/2026 dispositivo, verbatim:

> "Aggiornare l'area delimitata a Xylella fastidiosa sottospecie pauca ST53 ex Salento ai sensi
> del Reg. UE 2024/2507, costituita da:
> • zona infetta;
> • zona infetta in cui si applicano misure di contenimento che comprende un territorio di
> larghezza di 2 chilometri dalla zona infetta che si estende dallo Jonio all'Adriatico;
> • focolai puntiformi in agro di Mola di Bari e Noci in cui si applicano misure di eradicazione;
> • zona cuscinetto che comprende un territorio che si estende dallo Jonio all'Adriatico;"

The containment strip is 2 km as of 11-05-2026. DDS 75/2021 said 5 km. DDS 18/2024 said 5 km.

### 1.7 The BURP UUID-less path resolves — tested, 6 of 6

The brief asked whether `/documents/20135/{folderId}/{NAME}.pdf` resolves without the trailing
UUID. It does, when both the folder id and the short act filename are correct:

```
1964689/DET_95_6_9_2022.pdf     HTTP 200 bytes=2427117 application/pdf
2817336/DEL_916_2026.pdf        HTTP 200 bytes=1165246 application/pdf
2444921/DET_18_14_3_2024.pdf    HTTP 200 bytes=509383  application/pdf
2564917/DET_198_18_12_2024.pdf  HTTP 200 bytes=1103490 application/pdf
1989895/DET_127_17_11_2022.pdf  HTTP 200 bytes=1922321 application/pdf
2470544/DET_48_3_5_2024.pdf     HTTP 200 bytes=1219192 application/pdf
```

A guessed folder id fails: `20135/1719073/DET_75_3_8_2021.pdf` → HTTP 404, 664 bytes. The
folder id still has to come from the sommario. The UUID does not.

The `DET_{n}_{d}_{m}_{yyyy}.pdf` name is **not** unique. BURP 2024 sommari contain
`DET_48_3_5_2024.pdf`, `DET_48_13_9_2024.pdf`, `DET_48_18_7_2024.pdf`, `DET_48_22_2_2024.pdf` and
`DET_48_6_2_2024.pdf` — five different acts numbered 48, from different AOOs. Act number is
per-office and per-year, never a global key.

### 1.8 A second enumeration route exists, and it is open

The chain that found it, each step a fetched response.

`GET https://trasparenza.regione.puglia.it/v2/provvedimenti/provvedimenti-dirigenti-amministrativi`
→ HTTP 200, 799 bytes, an Angular shell naming six scripts. `main.js` (880,063 bytes) was
downloaded and read. It contains the CMS descriptor call:

```js
return this.http.post(`${this.baseUrl}/siep-cms/page/`, { slug: page, domain: hostname }, ...)
```

and the data-table call:

```js
getDataTable(endpoint, paginationRemote) {
  if (paginationRemote) {
    const queryString = `/paginated?page=${...}&size=${...}&sortBy=${...}&sortDirection=${...}`;
```

`POST https://sitra-cms.siep.regione.puglia.it/siep-cms/page/` with
`{"slug":"provvedimenti/provvedimenti-dirigenti-amministrativi","domain":"trasparenza.regione.puglia.it"}`
→ HTTP 200, 1,145 bytes. A leading slash on `slug` returns 404. The response names the content
endpoints:

```json
{"type":"AssetPublisher","props":{"endpoint":"/files","keyTitle":"fileName"},
 "endpoint":"/associable/files/OBBLIGHI","template":"file-list"}
```

`GET https://sitra-be.siep.regione.puglia.it/api/associable/files/OBBLIGHI/59` → HTTP 200,
**2 bytes**, body `[]`. Obbligo 59 is "Provvedimenti dirigenti amministrativi".

The endpoint is not broken. All 111 obligations in the menu tree were probed: 28 return non-empty
file lists, e.g. `(34, 'Contratti integrativi', 200, 52 files)`, `(33, 'Contrattazione
integrativa', 200, 25)`, `(6, 'Documenti di programmazione strategico-gestionale', 200, 19)`.
Obligations 55, 56, 57 and 59 — the entire *Provvedimenti* branch — all return 0.

`GET https://sitra-be.siep.regione.puglia.it/api/obblighi/59` → HTTP 200, 2,461 bytes. Its
`descrizione` field says where the acts really are, verbatim:

> "In questa sottosezione, in ottemperanza all'art. 23 del decreto legislativo 33/2013, sono
> pubblicati gli elenchi dei provvedimenti adottati dai dirigenti amministrativi della Regione
> Puglia.
> **Giunta Regionale** <a href="https://app.sistema.puglia.it/ords/f?p=130">Ricerca provvedimenti
> dei Dirigenti presso la Giunta Regionale</a>
> **Consiglio Regionale** <a href="https://alboonline.consiglio.puglia.it/archivio.html">Ricerca
> provvedimenti dei Dirigenti presso il Consiglio Regionale</a>"

`GET https://app.sistema.puglia.it/ords/f?p=130` → HTTP 200, 33,258 bytes, redirecting to
`f?p=130:4:12016215490434::NO:RP,4::`. An Oracle APEX interactive report. Page text, verbatim:

> "Trasparenza - Provvedimenti dei Dirigenti presso la Giunta Regionale. In questa sottosezione,
> in ottemperanza all'art.23 del Dlgs 33/2013, è pubblicato l'elenco dei provvedimenti adottati
> dai dirigenti amministrativi della Giunta Regionale negli ultimi cinque anni.
> […] 1 - 10 di 133.061"

Columns: `Anno; Numero; Ufficio; Tipo; Data Adozione; Oggetto; Documento; Allegati; Dipartimento;
Sezione; Servizio; Revoche/Rettifiche; Tipologia Dlgs. 33/2013`.

`GET https://app.sistema.puglia.it/ords/f?p=130:4:12016215490434:CSV` → HTTP 200, **77,929,758
bytes**, `text/csv`, 133,061 data rows. No login, no token, no referer needed. Year distribution
of the export:

```
2021  9,022    2022 24,930    2023 28,424
2024 26,371    2025 27,325    2026 16,989   (as at 2026-08-19)
```

### 1.9 The sample cross-check, and it disagrees

Unit chosen: acts of the **Sezione Osservatorio Fitosanitario**, calendar year **2024**. This is
the exact population Wedge 1 depends on.

*Route A — BURP sommario sweep.* The 2024 year listing returned 140 issues. All 140 sommari were
fetched, 0 errors. Regex `DETERMINAZIONE DEL DIRIGENTE SEZIONE OSSERVATORIO FITOSANITARIO
{date}, n. {N}` over the rendered text yields **64 distinct act numbers**, ranging 2 to 198.
DDS 48 is present, at issue n. 38 of 9 maggio 2024, burpId 9407.

*Route B — Sistema Puglia register.* Filtering the CSV on
`Sezione == "Sezione Osservatorio Fitosanitario"` and `Anno == 2024` yields 205 rows, **204
distinct act numbers**, contiguous 1 to 205.

*Result.*

| Measure | Count |
|---|---|
| Osservatorio 2024 acts in BURP | 64 |
| Osservatorio 2024 acts in Sistema Puglia | 204 |
| In BURP, absent from Sistema Puglia | **0** |
| In Sistema Puglia, absent from BURP | **140** |

BURP is a strict subset. It carries 31.4% of the Sezione's 2024 output. The missing 140 begin
`1, 4, 5, 6, 7, 9, 11, 14, 16, 17, 19, 20, 21, 22, 23, 24, 25, 26, 28, 32, 33, 35, 36, 37, 38, 39,
40, 41, 42, 44 …`.

The omission is verifiable independently of both routes. DDS 48/2024's own sibling acts of the
same date are among the missing:

| Act | Adopted | Oggetto (Sistema Puglia) | In BURP |
|---|---|---|---|
| DDS 49/2024 | 03-05-2024 | "decreto Interministeriale n. 2484 del 6/03/2020 'Piano straordinario per la rigenerazione olivicola della Puglia': conferimento in…" | no |
| DDS 50/2024 | 03-05-2024 | "Conferimento incarichi di Elevata Qualificazione presso la Sezione Osservatorio fitosanitario…" | no |

Both are cited by number and date inside acts that *are* in BURP. DDS 60 del 16/05/2024 recites
"la determinazione del Dirigente della Sezione Osservatorio Fitosanitario n. 49 del 03/05/2024 di
conferimento incarichi". DDS 71/2025 recites "conferiti con determinazione dirigenziale n. 50 del
03/05/2024". The acts exist. BURP does not carry them.

BURP states the reason in its own section headings, verbatim from the 2024 listing:

> "Determinazioni dirigenziali aventi contenuto di interesse generale"

### 1.10 emergenzaxylella.it — refuted as a public source, again

Every path tested returns the same gate:

```
http://www.emergenzaxylella.it/                                            HTTP 302
http://www.emergenzaxylella.it/portal/portale_gestione_agricoltura/impianti HTTP 302
http://www.emergenzaxylella.it/portal/emergenza_xylella/Documenti           HTTP 302
```

All three redirect to, verbatim from the `Location` header:

```
https://jossogateway.sit.puglia.it/josso/signon/login.do?josso_cmd=login_optional&josso_back_to=http://www.emergenzaxylella.it/josso_security_check
```

`https://emergenzaxylella.it/` fails at the TLS layer, HTTP 000, 0 bytes. No anonymous subpath
was found. The `/impianti` path named in DDS 48/2024 Allegato A is not anonymously readable.

### 1.11 Open data and feeds — measured

`GET https://dati.puglia.it/ckan/api/3/action/package_search?q=&rows=0` → HTTP 200,
`{"result":{"count":2012}}`. A query for `determinazione dirigenziale` returns count 2, both
irrelevant ("Elenco Comuni ad economia prevalentemente turistica", "Interventi di tutela e
valorizzazione delle chiese rupestri"). The catalogue holds 2,012 datasets and no act register.

`GET https://www.regione.puglia.it/robots.txt` → HTTP 200, 158 bytes:

```
User-Agent: *
Disallow: https://www.regione.puglia.it/web/salute-sport-e-buona-vita/osservatorio-covid-19/*
Sitemap: https://www.regione.puglia.it/sitemap.xml
```

`GET https://www.regione.puglia.it/sitemap.xml` → HTTP 200, 26,131 bytes, a `<sitemapindex>` of
Liferay layout sitemaps keyed on `p_l_id` and `layoutUuid`. It enumerates pages, not acts.

`GET https://trasparenza.regione.puglia.it/robots.txt` → HTTP 200, 1,655 bytes, a stock Drupal
robots file. No sitemap directive.

---

## CLASS 2 — INFERRED FROM CLASS 1

**C2-1. The consultant claim is wrong in three specific ways. Do not encode it.**

The claim was: *Regione Puglia requires cadastral registration of every resistant-cultivar
planting (Leccino, FS-17/Favolosa) via a dedicated service, attributed to DDS 48/2024.*

- **Wrong duty-holder.** The obligation sits under a chapeau addressed to "operatori professionali
  registrati al RUOP, autorizzati a rilasciare passaporti delle piante […] e autorizzati ai sensi
  dell'art. 23". That is the nurseryman. A grower planting trees on his own land is not the
  addressee of section 5 and is not registered at RUOP.
- **Wrong trigger.** The trigger is "produzione/commercializzazione di piante olivo" — producing
  or marketing nursery stock. It is not the act of planting. The registered datum is the
  *destination site* of plants the operator sells, declared by the seller.
- **Wrong cultivar set.** The clause names exactly two varieties, "FS17" and "Leccino". It does
  not name Lecciana or Leccio del Corno — the two cultivars DDS 48/2024 itself newly authorises.
  A rule keyed on "resistant cultivars" would over-fire on the two 2024 additions.

A fourth divergence, smaller but load-bearing for schema design: the act says "dati catastali",
not foglio and particella. Neither word appears anywhere in the 10 pages. The granularity of what
`/impianti` actually stores is not established by this act.

Correct statement of the rule: *when a RUOP-registered professional operator authorised under Art.
23 produces or markets FS17 or Leccino olive plants in the infected zone, the cadastral data of the
site where those plants will be planted must be entered on
`emergenzaxylella.it/portal/portale_gestione_agricoltura/impianti`.* Confidence: high — this is a
single sentence read in full context with its chapeau, and machine-verified as the only cadastral
sentence in the act.

**C2-2. There is no per-parcel planting authorisation for a grower, and never was.**

DDS 75/2021 and DDS 48/2024 are both standing, general authorisations. Neither creates an
application, an instance, a form, or a decision addressed to an individual planter. The engine
needs a lookup table — authorised species and varieties, one geographic exclusion — not an
authorisation workflow. Confidence: high.

**C2-3. The one grower-facing duty in this chain is the felling authorisation, and it is in the
2021 act, not the 2024 one.**

DDS 75/2021 disposes that "chiunque intende svellere gli oliveti per rimpianto deve chiedere
l'autorizzazione ai Servizi Territoriali […] ai sensi della legge 14/02/1951 n° 144". DDS 48/2024
does not repeat it. DDS 48/2024 also does not revoke it: its own dispositivo *confirms* the
DDS 75/2021 authorisation rather than replacing the act. Reading: the L. 144/1951 felling
authorisation remains live and is the real per-grower gate on the replant path. Confidence:
medium-high — the confirmation language is explicit, but no act was found that states DDS 75/2021
is wholly in force, and this should be put to Owen before it becomes an engine rule.

**C2-4. The authorisation is stable; its geographic operand is not.**

DDS 48/2024 incorporates the delimited area "di cui alla DDS 18 del 14/03/2024" by reference. That
delimitation has since been replaced at least twice, by DDS 158/2024 under Reg. UE 2024/2507 and
by DDS 82/2026. The containment strip that the authorisation excludes has narrowed from 5 km
(DDS 75/2021, DDS 18/2024) to 2 km (DDS 82/2026), and eradication now applies to point foci at
Mola di Bari and Noci that did not exist in 2024. An engine that resolves "is this parcel in the
zone excluded by DDS 48/2024" must resolve the *current* delimitation as of the evaluation date,
never the 2024 snapshot the act names. Confidence: high — the dispositivi are explicit and
fetched.

**C2-5. A second independent enumeration route exists. The corpus can be corroborated.**

Sistema Puglia APEX app 130 is anonymous, complete over 2021-2026, and exports the whole register
as one 78 MB CSV. It is genuinely independent of BURP: different host, different operator, a
different legal obligation (art. 23 D.lgs. 33/2013 rather than BURP publication), and it is the
channel the region's own transparency obligation points at. The prior finding "no second route
exists" is retired. Confidence: high — executed, and the export is on disk.

**C2-6. The routes disagree by 3.2×, and BURP is the one that omits.**

On the 2024 Osservatorio sample, BURP holds 64 of 204 acts. Nothing is in BURP that is missing
from Sistema Puglia. This is a systematic omission, not sampling noise, and BURP names its own
filter: it publishes determinazioni "aventi contenuto di interesse generale". Editorial selection,
applied by the publisher, invisible from inside BURP.

Consequences for the build, in order of severity:

1. **The 72,346 / 791 figures measure BURP, not the corpus.** They are correct as statements about
   what BURP contains. They are not statements about what the Regione Puglia adopted. Every
   external use must say which.
2. **The omission is not random with respect to Wedge 1.** Among the 140 missing 2024 acts are
   `conferimento incarichi`, delegation and responsibility acts — the kind that names who signs
   what. But the sample also shows the funding stream is heavily represented in the register and
   thinly in BURP: the `Reimpianto olivi zona infetta` payment, variance and graduatoria-scorrimento
   acts number in the dozens per year in Sistema Puglia. Those are exactly the acts that move money
   toward a grower. A BURP-only census will under-count the disbursement layer.
3. **The 2.9% coverage figure is against the wrong denominator.** Against 204 Osservatorio acts in
   2024 alone, and 939 across 2021-2026, current coverage is lower than reported.

Confidence: high on the counts, which are set arithmetic over two fetched enumerations.
Confidence: medium on the generalisation from one Sezione-year to the whole corpus — the sample is
one section and one year, deliberately chosen as the one that matters, and it should be repeated on
at least one more Sezione before the ratio is quoted as a corpus-wide figure.

**C2-7. Neither route alone is sufficient. They are complementary, and the union is the corpus.**

Sistema Puglia gives complete enumeration but reaches only five years back — the page states "negli
ultimi cinque anni" and the export confirms it, earliest year 2021. The Xylella corpus starts in
2013. BURP reaches back to 1999 but omits ~69% of a section's output. Neither is the corpus.

Recommended census method: enumerate 2021-2026 from Sistema Puglia as the spine, because it is
complete and costs one GET; enumerate 1999-2020 from the BURP sommario sweep, because nothing else
reaches there; reconcile the overlap 2021-2026 and treat any BURP act absent from Sistema Puglia as
a defect to investigate (there were none in the sample). Report pre-2021 coverage with an explicit
"BURP-only, editorially filtered" qualifier, because for those years the omission cannot be
measured at all.

**C2-8. Sistema Puglia enumerates but does not directly yield PDFs.**

The `Documento` column exports as the literal string `Scarica`. In the HTML the link is
`f?p=130:2:{session}::NO:RP,2:P2_ID_ATTO:{id}` — an APEX modal page keyed on an internal act id
that the CSV drops. Retrieving act text at scale from this route therefore needs the HTML report
paged, not the CSV, to capture `P2_ID_ATTO`. The CSV is the right tool for the census; it is the
wrong tool for acquisition. Confidence: high — both shapes were fetched and inspected.

**C2-9. Amministrazione Trasparente's *Provvedimenti* branch is legally populated and technically
empty.**

Obligations 55, 56, 57 and 59 all return `[]` while 28 sibling obligations return files. The
section discharges art. 23 D.lgs. 33/2013 by hyperlink to an external application rather than by
publishing a list. That is why every prior attempt to find a content endpoint failed: the endpoint
was always there and always empty. The failure was not in the guessing; it was in the assumption
that the section holds documents. Worth recording as a general lesson — an empty well-formed
response is a finding about the source, not a bug in the request.

**C2-10. `emergenzaxylella.it` is the single point of failure in the planting-registration chain,
and it is closed.**

The obligation in DDS 48/2024 Allegato A can only be discharged through a portal behind JOSSO SSO,
with sanctions under art. 55 D.lgs. 19/2021 for non-compliance. Wedge 1 cannot read the resulting
dataset, cannot verify that a given operator complied, and cannot show a grower his own record.
Any engine statement about planting registration must be framed as an obligation on a third party
that the engine cannot observe. Confidence: high.

**C2-11. Act filenames are not identifiers.**

Five distinct 2024 acts share the name pattern `DET_48_*_2024.pdf`. Any dataset keyed on act
number without the AOO/Sezione and adoption date will collide silently. The natural key is
`(anno, numero, ufficio)` — all three present in the Sistema Puglia export, and `Ufficio` 181 is
the Osservatorio. Confidence: high.

---

## FETCH LOG — every URL attempted that failed, and how

| URL | Result | Reading |
|---|---|---|
| `burp.../documents/20135/1719073/DET_75_3_8_2021.pdf` | HTTP 404, 664 B | Folder id was guessed. Confirms folder id must come from the sommario; only the UUID is optional |
| `burp.../bollettini?...SearchPortlet_datefilter=03%2F05%2F2024+-+03%2F05%2F2024` | HTTP 200, 100,254 B, **zero** `burpId` and zero `DET_` strings | The date-filter parameter name in the brief does not select on this endpoint. The year-listing plus sommario route works and was used instead |
| `burp.regione.puglia.it/rss-burp` | curl 28, timed out after 25 s, 0 bytes | Feed did not respond this session. Not retried — it is an incremental-detection aid, not an enumeration route |
| `https://emergenzaxylella.it/` | HTTP 000, 0 bytes | TLS failure before HTTP |
| `http://www.emergenzaxylella.it/` | HTTP 302 → `jossogateway.sit.puglia.it/josso/signon/login.do` | SSO gate |
| `http://www.emergenzaxylella.it/portal/portale_gestione_agricoltura/impianti` | HTTP 302 → same JOSSO URL | The path DDS 48/2024 names is gated |
| `http://www.emergenzaxylella.it/portal/emergenza_xylella/Documenti` | HTTP 302 → same | No public subpath found |
| `https://www.regione.puglia.it/web/agricoltura/osservatorio-fitosanitario` | HTTP 404, 126 B | No such page |
| `https://www.regione.puglia.it/web/agricoltura/-/xylella-fastidiosa` | HTTP 404, 126 B | No such page |
| `sitra-be.../v3/api-docs`, `/v2/api-docs`, `/swagger-ui/index.html`, `/swagger-resources`, `/actuator` | HTTP 404, 431 B each, `text/html` | No OpenAPI descriptor exposed |
| `sitra-be.../api/v3/api-docs` | HTTP 404, 104 B, `application/json` | Reaches the API, no descriptor |
| `sitra-cms.../siep-cms/page/` with slug `/provvedimenti/provvedimenti-dirigenti-amministrativi` | HTTP 404, 130 B, `"Pagina non trovata con slug: not-found"` | A leading slash breaks the lookup. Drop it |
| `sitra-cms.../siep-cms/page/` with domain `www.trasparenza.regione.puglia.it` | HTTP 404, 117 B, `"Client non trovato con dominio"` | Host must be the bare `trasparenza.regione.puglia.it` |
| `POST sitra-be.../api/associable/files/OBBLIGHI/paginated` body `{}` | HTTP 415 Unsupported Media Type | Wrong shape |
| `POST sitra-be.../api/files/paginated`, `/api/associable/files/OBBLIGHI/59/paginated` | HTTP 400 Bad Request | Payload contract not recovered; the unpaginated GET works and was used instead |
| `GET sitra-be.../api/associable/files/OBBLIGHI/59/paginated?page=0&size=5...` | HTTP 405 Method Not Allowed | `/paginated` is POST-only on this route |
| `http://cartografia.sit.puglia.it/doc/xylella/` | HTTP 403, 218 B | Directory listing disabled. Individual documents under it do resolve; the folder cannot be enumerated |
| `http://cartografia.sit.puglia.it/doc/osservatorio_fitosanitario/` | HTTP 403, 218 B | Same |
| `app.sistema.puglia.it/ords/f?p=130:4:{s}:::RIR:IREQ_ANNO,IRC_SEZIONE:2024,Osservatorio` | HTTP 200, 33,260 B, pager still reads "1 - 10 di 133.061" | Interactive-report column names are not `ANNO`/`SEZIONE`. Server-side filtering not achieved; the full CSV was exported and filtered locally instead |
| `app.sistema.puglia.it/ords/f?p=130:4:{s}:CSV` (first attempt, 90 s timeout) | curl 28 at 37,302,672 of 77,929,758 bytes | Timeout, not refusal. Succeeded at 900 s |

Not attempted, and why: `alboonline.consiglio.puglia.it/archivio.html` returned HTTP 200, 12,154
bytes and is the Consiglio Regionale register. It was not enumerated because Wedge 1's acts are
Giunta acts (AOO 181, Sezione Osservatorio Fitosanitario), and the Consiglio register is a
different population. It should be checked under its own task if any Wedge 1 obligation ever
traces to a Consiglio dirigenziale act.

---

## WHAT SHOULD CHANGE

1. **Do not encode a per-planting cadastral registration rule.** Encode the FS17/Leccino
   production-and-marketing obligation on RUOP operators, or encode nothing. C2-1.
2. **Encode the Art. 18 authorisation as a static table**, four olive varieties plus the immune
   and low-susceptibility species, with one geographic exclusion resolved against the *current*
   delimitation. C2-2, C2-4.
3. **Qualify the corpus figures.** 72,346 acts and 791 Xylella-relevant are BURP measurements. On
   the one sample tested, BURP holds 31% of a section's output. C2-6.
4. **Re-plan the census as a union of two routes**, Sistema Puglia for 2021-2026 and BURP for
   1999-2020. C2-7.
5. **Escalate the L. 144/1951 felling authorisation to Owen** before it becomes an engine rule.
   C2-3.
