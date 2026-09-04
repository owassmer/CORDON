# Plant Trade Unit / Lot reopening gate

Status: OPEN SEMANTIC DECISION — no Ontology change authorized
Date: 2026-08-24
Trigger: independent operator/data fan-out after Q5/Q6 closure

## Verified primary-source basis

Regione Puglia DET 48/2024 requires:

- compliant plant passports;
- three-year traceability for every transmitted/received lot, producer and recipient;
- cadastral destination registration for FS17 and Leccino planted in the infected zone.

Source and quotations are preserved in `operator-reality.md` S16.

## Why this may reopen Gate 5

A commercial plant lot may change independently of supplier and Intervention and may be split across several Interventions. The operational facts potentially owned by the lot are:

- supplier/RUOP/passport authority;
- cultivar/specification/certification;
- quantity reserved, dispatched, received, rejected, planted, returned and replaced;
- production site and recipient;
- allocation across Interventions/Parcels;
- substitution, recall, quarantine, warranty and replacement lineage.

The current conditional exclusion said to add a Lot only when a real operator allocation, dispatch, substitution, warranty or return decision cannot be preserved in Intervention material history. Primary law establishes the lot identity and traceability requirement; it does not yet prove PugliaOlive's internal decision workflow.

## Direct-evidence gate

Acquire one actual redacted nursery cycle:

quote → availability promise → reservation/deposit → order → lot/passport/test → delivery note → allocation by Intervention/Parcel → rejection/substitution/return/warranty/replacement.

Then test whether the accepted Intervention history can support all of these without:

- duplicating one lot across Interventions;
- losing remaining quantity or custody;
- making substitution/warranty a generic edit;
- preventing query of one lot's complete allocation and outcome history.

## Decision branches

### Keep excluded

Use Intervention material history + evidence references if the lot never needs independent selection, allocation, mutation or cross-Intervention lifecycle.

### Admit `PlantTradeUnit`

Admit one visible or backstage object only if the evidence proves independent identity/lifecycle. Reuse existing Party, Intervention, Parcel, Plant and histories; do not add separate Order, Delivery, Inventory, Warranty or Batch objects unless deletion tests independently pass.

### Exact Action consequence

If PugliaOlive authoritatively allocates or substitutes regulated lots across Interventions, the four-Action ceiling may need one bounded `Allocate or Substitute Plant Material` Action. Do not overload the capacity Action if it would make a recommendation/commitment silently become custody/allocation truth. This is an Owen decision because it changes the accepted Action count.

## Anti-complexity bar

The lot earns admission only if it replaces duplicated material-state facts and enables a real allocation/substitution/warranty decision. Traceability alone can remain backstage evidence; legal importance does not automatically imply a visible object or fifth Action.
