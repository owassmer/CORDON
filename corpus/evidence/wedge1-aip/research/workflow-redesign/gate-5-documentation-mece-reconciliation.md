# Gate 5 documentation and MECE reconciliation

Status: **ACCEPTED — Gate 4 selectively corrected to nine families and 16 atomic predicates**
Date: 22 August 2026

## Inputs reconciled

- `palantir-ontology-current-grounding.md` — 164 current official documentation pages traversed.
- `gate-5-mece-self-audit.md` — Connor independent audit; 39 connected-model propositions.
- `gate-5-mece-coverage-audit.md` — exhaustive coverage audit; 52 propositions.
- `gate-5-mece-exclusivity-audit.md` — adversarial placement audit; 34 atomic fact patterns.
- `connected-operating-model.md` — accepted operator decisions.
- `gate-3-noun-candidates.md` — accepted nouns.
- `gate-4-relationship-candidates.md` — accepted relationship authority under review.

## Documentation verdict

Current official Palantir guidance strongly validates the sequence already used:

- model reality before source schemas;
- separate identity from observations/events when they have different real grains;
- keep one focused type per distinct real entity or event;
- use semantically named links;
- use direct links only when the relation owns no facts;
- use an object-backed link when the relationship owns dates, role, allocation, quantity, status or comparable metadata;
- store each fact once;
- use cohesive Actions for real operations;
- introduce Interfaces only for a proven shared polymorphic contract;
- avoid System Silos, Kitchen Sink, Department Silos, God Object, Golden Hammer, Action Sprawl, Time Machine and Misnomer anti-patterns.

Sources and complete ledger: `palantir-ontology-current-grounding.md`.

Current docs also correct several historical assumptions:

- object types may represent real entities **or specific events**;
- separating identity from observation is a diagnostic, not an automatic rule creating an Observation type;
- relationship metadata does not automatically include provenance/source/confidence;
- Action Logs are optional platform audit objects, not mandatory domain decision objects;
- Interfaces remain optional and unevenly supported across applications;
- one-to-one cardinality is intent metadata, not uniqueness enforcement;
- current state, real domain amendments, time series, edit history and Action logs are different history mechanisms.

## MECE verdict

### Nouns

**PASS.**

All 13 nouns survive deletion. No fourteenth noun is required. No accepted noun is redundant.

The Governing Instrument boundary requires one clarification during Gate 5:

- the independently identifiable operative act/agreement is the noun;
- issuance, signature, release or decision is an event/outcome;
- normative consequence is a relationship fact;
- a resulting durable member right is a separate relationship fact;
- a PDF/source artifact is evidence only.

This is a boundary clarification, not a noun addition.

### Relationships

**FAIL AS WRITTEN.**

The current seven-family prose is collectively incomplete and semantically overlapping. It would require Ontology implementation choices to settle unresolved domain ownership. That is prohibited.

The fatal defects are:

1. F1 and F3 both claim authority, mandate and delegation.
2. F1 and F7 can both claim beneficiary/creditor identity.
3. F2’s broad name invites Parcel–Official Area applicability.
4. F3 and F7 duplicate member-specific right facts.
5. F5 and F6 both claim Lot reservation.
6. F5’s “actual” and “accepted” wording promotes observations/outcomes into relationships.
7. Public Proceeding subject/scope has no complete semantic home.
8. Plant Trade Unit/Lot custody outside Intervention use has no complete semantic home.
9. Compound anti-collapse grains combine facts that belong to different families.
10. F4 can become overbroad unless restricted to biological pathogen/host-response predicates.

## Why stretching seven families is rejected

The coverage audit proposed:

- putting formal Proceeding scope into F3;
- putting actor–Lot custody into F1.

That repairs count coverage but weakens mutual exclusivity:

- formal Proceeding scope can change independently without being a Governing Instrument effect;
- custody of a traceable Lot is not the same semantic kind as membership, office, representation or decision authority;
- F1 and F3 are already the broadest and most collision-prone families;
- expanding them creates precisely the generic Assignment/Effect pattern that current Palantir guidance warns against.

Minimum type count is not the objective. Minimum semantic duplication and one fact owner are.

## Recommended relationship inventory

Use **nine semantic relationship families**.

These remain review families, not nine generic implementation types. Every Ontology relationship still requires an exact domain predicate and grain.

### F1. Actor Assignment and Authority

A Natural Person or Organization holds a real scoped membership, office, representation, delegation, decision authority or operational responsibility relative to an Organization, Agricultural Holding, Public Proceeding or Intervention.

Owns the instantiated assignment: actor, context, role/predicate, powers, duties, scope and effective period.

Does not own:

- the Instrument effect creating/limiting it → F3;
- actor–Parcel tenure/access → F2;
- creditor/right-holder identity → F7;
- Lot custody → F9.

### F2. Holding–Parcel Operation and Actor–Parcel Tenure/Access

Owns only:

- Agricultural Holding ↔ Cadastral Parcel declaration/conduction/operation;
- Person/Organization ↔ Cadastral Parcel title, lease, usufruct, occupation, management, access or consent.

Excludes Official Area applicability, Plant location, Intervention scope and actor–Holding assignment.

### F3. Scoped Governing Instrument Effect and Applicability

Owns what a Governing Instrument normatively creates, limits, suspends, amends, supersedes, stays, construes or terminates, including authority/date/rule-grounded Parcel–Official Area applicability.

Owns the normative effect, not the instantiated assignment or right resulting from it.

Excludes:

- actor assignment → F1;
- member-specific surviving right → F7;
- formal Proceeding subject/scope → F8;
- raw polygon overlap → derived result.

### F4. Biological Pathogen–Host Response

Owns directed, evidence-qualified biological predicates between pathogen/lineage and host Taxon or Cultivar:

- host-of;
- susceptible-to;
- resistant-to;
- tolerant-to.

Preserves direction, biological grain and evidence/authority class.

Excludes individual infection observations, legal host/applicability classification, programme/cultivar authorization, Intervention target/use and vector/transmission ecology.

### F5. Intervention Physical and Material Scope

Owns independently preserved:

- intended scope;
- authorized scope;
- as-built physical/material inclusion or use.

Endpoints can include Parcel, supported Individual Plant, Cultivar, organism target and Plant Trade Unit/Lot.

Excludes:

- Lot reservation → F6;
- Lot custody → F9;
- observations and observed footprint;
- execution, delivery, installation, substitution, acceptance and replacement occurrences;
- acceptance outcome.

Events/outcomes may create, evidence or change F5. They are not F5 predicates.

### F6. Scarce Capacity Reservation or Commitment

Owns quantified/time-bounded operational or financial capacity actually earmarked or committed to an Intervention, including a specific Lot when stock is reserved.

Preserves owner, quantity/slot, period, firmness, prerequisites, expiry, release and reallocation consequences.

Excludes requirement, availability estimate, actor responsibility, material use and reservation/release events.

### F7. Member-Specific Entitlement or Creditor Right

Owns the instantiated durable right/exposure after creation:

- holder/creditor/assignee/recovery obligor;
- awarded scope and amount/ceiling;
- permitted claim stages;
- conditions and period;
- assignment;
- guarantee/recovery exposure;
- remaining right.

F3 owns the Instrument’s creating/limiting/discharging effect. F7 owns the right thereafter. Claims, liquidation, payment, audit, revocation and recovery are events/outcomes acting on it.

### F8. Formal Proceeding Subject and Scope

A Public Proceeding formally concerns a Person, Organization, Holding, Parcel, Official Area, Individual Plant, Lot, Programme, Governing Instrument or Intervention with independently changing recognized facts.

Owns exact proceeding-specific subject/scope such as:

- claimed/requested scope;
- reviewed scope;
- admitted/excluded scope;
- decided/permitted scope;
- appealed/audited/enforced/recovery scope;
- version, quantity, amount, basis and effective history when the real proceeding preserves them.

Excludes:

- actor participation/decision authority → F1;
- bare subject pointer with no independent facts → contextual direct link;
- normative Instrument effect → F3;
- durable entitlement → F7;
- physical Intervention scope → F5;
- submission/decision occurrence → event/outcome.

### F9. Plant Material Allocation and Custody

A Natural Person or Organization has an independently preserved allocation, possession/custody, dispatch-control, receipt-control, movement-control, warranty or return responsibility for a Plant Trade Unit/Lot.

Owns:

- accountable actor;
- Lot or quantity/share;
- allocation/custody basis;
- effective period;
- duties;
- transfer/handoff condition;
- traceability responsibility.

Excludes:

- Intervention material use → F5;
- reserved/committed stock → F6;
- dispatch, movement, receipt and return occurrences → events/outcomes;
- origin/producer/cultivar classification with no independent relationship facts → contextual direct link.

## Required atomic anti-collapse predicates

Replace the 11 compound grains with **16 atomic tests**:

1. Cooperative membership — F1
2. Holding stewardship/representation — F1
3. Actor–Parcel tenure/access/consent — F2
4. Holding–Parcel declaration/conduction — F2
5. Authority-grounded Parcel–Official Area applicability — F3
6. Governing Instrument effect/lineage — F3
7. Biological pathogen–host response — F4
8. Public Proceeding actor participation/authority — F1
9. Public Proceeding subject/scope — F8
10. Intervention Parcel/Plant physical scope — F5
11. Intervention–Cultivar/material specification — F5
12. Intervention actor responsibility/authority — F1
13. Intervention scarce-capacity commitment — F6
14. Member-specific entitlement/creditor right — F7
15. Lot inclusion/use in Intervention — F5
16. Lot actor allocation/custody — F9

The earlier 11 remain historical review groupings. Gate 5 uses these 16 atomic predicates as the anti-collapse contract.

## Global placement precedence

Apply in order:

1. Atomize compound statements.
2. Resolve endpoint identity/co-reference.
3. Classify event/outcome.
4. Classify observation.
5. Classify derived overlay/computation.
6. Classify endpoint value or contextual direct link.
7. Place the independently surviving relationship in exactly one of F1–F9.
8. Keep separate propositions that legitimately coexist, such as:
   - F3 creating effect + F1 instantiated assignment;
   - F3 creating effect + F7 instantiated right;
   - F1 responsibility + F6 capacity commitment;
   - F5 material use + F6 prior reservation;
   - F5 material use + F9 custody.
9. Unknown private facts remain unknown.

## Event and observation implication from current docs

Palantir supports object types for real events. The accepted rejection of a generic Event noun remains correct. Gate 5 must now test each consequential occurrence independently:

- Does it have its own externally recognized identity?
- Must operators refer to the same occurrence after correction/reopening?
- Does it own facts that cannot live on surviving nouns/relationships or platform Action/edit history?
- Is it a domain event rather than an Action Log, source record or technical observation?

Only a concrete event passing those tests can become an event object type. Platform support alone does not admit one.

## Gate disposition

Accepted sequence:

1. Reopen Gate 4 selectively.
2. Accept the nine-family partition and 16 atomic anti-collapse predicates.
3. Propagate the corrected ownership and precedence rules to Gate 4, Gate 5 reground and core-Ontology contract.
4. Re-run the MECE verifier.
5. Resume Ontology representation derivation only after it passes.

No noun changes are recommended. No object, direct link, object-backed link, property, cardinality, Action, Function or Interface is selected in this reconciliation.
