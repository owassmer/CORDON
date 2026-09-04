# ST1 delimitation currency — regional act register

Read date: 2026-08-19.

## Claim

No act later than DDS 236/2025 was located in the Regione Puglia administrative-act register that
institutes or updates the delimited area for *Xylella fastidiosa* subspecies *fastidiosa* ST1.

This is a registry-scoped negative with a reproducible predicate. It is not a claim that no authority
could ever publish an act elsewhere.

## Source

Anonymous Sistema Puglia / Regione act-register CSV export:

```
rows     133,061
bytes    77,929,758
sha256   ec0aa21dfc2e4ac383c346ff689f0f7e68d5feb7587fbe78d9ef48376df2f695
source   https://app.sistema.puglia.it/ords/f?p=130
```

The register's natural key is `(Anno, Numero, Ufficio)`. Office `181` is Sezione Osservatorio
Fitosanitario.

## Filter

```python
office == '181'
adoption_date > 2025-12-18
upper(subject) contains 'SOTTOSPECIE FASTIDIOSA'
upper(subject) contains 'ST1'
upper(subject) contains 'AREA DELIMITATA'
upper(subject) contains one of {'AGGIORNAMENTO', 'ISTITUZIONE'}
```

Intermediate counts:

```
all register rows                  133,061
office 181 rows                        938
office 181 after 2025-12-18             132
exact ST1 delimitation hits                0
```

The broader review also enumerated the post-cutoff ST1 eradication/removal orders and other-subspecific
area updates. They do not update the ST1 area. DDS 112/2026, for example, updates the *pauca* Modugno
area, not *fastidiosa* ST1.

## Result

The complete BURP general-interest series and the wider regional register independently return no
later ST1 delimitation update through the export date. `DDS-236-2025` is therefore the current acquired
ST1 geometry-version act as of 2026-08-19, with source coverage stated rather than implied.
