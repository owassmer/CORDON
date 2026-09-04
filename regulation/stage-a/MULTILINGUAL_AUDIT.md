# Articles 1–17 multilingual legal-linguistic audit

Status: **accepted Stage A verification input**
Date: 27 August 2026
Sources: current 24 November 2025 EUR-Lex consolidations in English, Italian,
French, German and Spanish; authentic amending Regulation (EU) 2024/2507.

## Method

The original 104-atom Articles 1–18 population was compared across five official
language versions. The current implemented aperture retains the 99 Article 1–17
atoms; the five Article 18 atoms remain deferred evidence.

- modifier scope;
- conjunction and disjunction precedence;
- parent/subparagraph structure;
- derogation target;
- pronoun and demonstrative referent;
- modality;
- temporal-window direction and anchor;
- spatial direction;
- singular/plural subject.

The current implemented inventory contains 99 rows and 99 unique provision IDs.

Material differences are retained only when another reading would change an
executable condition, duty, permission, clock, geometry, evidence requirement or
effect. For Puglia, Italian is the operating text, but all EU language versions
are equally authentic. A divergence is therefore retained as a legal-linguistic
conflict even where context and the Italian text support a compiled result.

## Findings and dispositions

| Provision | Risk | Disposition for Stage A |
|---|---|---|
| 3(1), final subparagraph | Annual plan update was parented under point (c). | **REPAIR.** It governs the contingency plan as a whole. Stable ID: `3(1)-final-subparagraph`. |
| 5(1)(a) | Spanish syntax can attach `immediately` only to removal; EN/IT/DE naturally cover sampling and removal. | **COMPILE BOTH IMMEDIATE; RETAIN CONFLICT.** Preserve separate sample and removal times. Failure of either blocks the derogation pending legal review. |
| 6(4) | EN/ES use initial identification/detection; IT/FR/DE use initial establishment. | **COMPILE INITIAL ESTABLISHMENT; RETAIN CONFLICT.** Art. 6(2), whose special route paragraph 4 reports, uses initial establishment in all versions. Preserve both dates. |
| 7(1)(e), third subparagraph | A taxon-wide history can replace evidence about the referenced plants/cohort. | **REPAIR EVIDENCE GRAIN.** Retain referenced plants/cohort, demarcated area, point-(e) results and Art. 10 surveys over the retrospective two-year window. Species history alone is insufficient. |
| 8(1), final sentence | ES `podrán incluir` is permissive; EN/IT/FR/DE are mandatory. | **COMPILE MANDATORY FOR PUGLIA; RETAIN CONFLICT.** Italian `comprendono` and the authentic amendment's EN text require inclusion. |
| 9(1) | `shortest distance from that location` can become an unanchored nearest-site test. | **REPAIR REFERENT.** The demonstrative refers to the designated nearby destruction location. Store designated and actual locations, route and net evidence. |
| 11(1) | Malformed English can make ISPM 14 optional or sever it. | **COMPILE CUMULATIVELY.** Open-ended eradication measures are constrained by ISPM 9 and the integrated approach under ISPM 14. |
| 14(2), final sentence | ES is permissive; EN/IT/FR/DE are mandatory. | **COMPILE MANDATORY FOR PUGLIA; RETAIN CONFLICT.** Italian `comprendono` requires inclusion. Keep Art. 14(1)'s separate before-removal/around-retained-plant duty. |
| 15(2), final subparagraph | Parented only under point (b). | **REPAIR.** Plural `those parts` in all versions covers both points (a) and (b). Stable ID: `15(2)-final-subparagraph`. |
| 15(2)(a) | German `um die Grenze` can suggest a two-sided boundary band. | **COMPILE INWARD BAND.** The Art. 15(2) stem limits it to a part of the infected zone; Art. 15(4) separately governs the buffer side. |
| 15(5) | English plural `specified pests` can mint a new subject. | **NORMALIZE TO THE DEFINED SINGULAR PEST.** IT/FR/DE/ES all use the singular definition from Art. 1(a). Preserve verbatim English as source evidence. |
| 18(b) | Scope of `preferably` and OR. | **DEFERRED EVIDENCE.** The finding remains available if a later planting/grafting aperture opens; it does not affect the Articles 1–17 implementation. |

## Corpus coverage

Implemented material findings occur in Articles 3, 5, 6, 7, 8, 9, 11, 14 and 15.
No additional executable-meaning discrepancy was found in Articles 1, 2, 4,
10, 12, 13, 16 or 17.

The accepted implementation effect covers Articles 1–17. It does not claim multilingual semantic coverage
of later transaction provisions, annex taxon/test contents, external standards,
national implementation or judicial interpretation. Those are indexed or owned
by their separate source families under the accepted aperture.

## Required Stage A changes

1. Re-parent 3(1) and 15(2) final subparagraphs.
2. Add a legal-linguistic-conflict field with source-language propositions.
3. Replace 6(4)'s identification anchor with initial establishment and preserve
   both dates in the evidence contract.
4. Split 5(1)(a)'s sample and removal timestamps while requiring immediacy for
   both.
5. Preserve referenced plant/cohort grain in 7(1)(e)'s retrospective evidence.
6. Add designated-location and actual-location referents to 9(1).
7. Preserve cumulative ISPM 9 + 14 constraints for 11(1).
8. Keep the Articles 8/14 Spanish modality divergence without weakening the
   Puglia rule.
9. Normalize 15(5) to the defined singular Taxon while retaining source text.
10. Keep Article 18(b)'s prior finding as deferred evidence only.

## Verification gates

- Mutation: parent 3(1) update under point (c) → fail.
- Mutation: parent 15(2) final text under point (b) → fail.
- Mutation: use detection as the sole 6(4) anchor → fail.
- Mutation: omit one 5(1)(a) timestamp → fail.
- Mutation: satisfy 7(1)(e) from species history alone → fail.
- Mutation: make ISPM 14 optional → fail.
- Mutation: construct 15(2)(a) as a two-sided buffer → fail.
- Mutation: hide a material authentic-language conflict → fail.
