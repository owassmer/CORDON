# CORDON stages A–G verification and acceptance protocol

Status: **supporting process reference — no current-state authority**

Current authority: `jurisdiction/STAGE_A_AUTHORITY_SNAPSHOT.json`.
Owner: Owen closes stage decisions; Connor plans, derives, adjudicates and verifies
Date: 27 August 2026

## Current Stage A exception

The current Stage A regional serialization is Connor-only. Do not delegate
semantic reading, authoring, adjudication, review or closure. Prior independent
reviews repeatedly became source-completeness engines because their isolated
briefs could not carry the whole cross-session forest. Their findings and PASS
states are historical evidence only.

Stage A now runs:

```text
accepted EU + accepted national core + Steps 4–5 semantic authority
→ whole-forest Step 6 serialization by Connor
→ bounded deterministic/mechanical checks
→ Connor top-down and bottom-up whole-forest semantic verification
→ coherent presentation
→ one-question-at-a-time Owen grill
→ Owen accepts / deletes / reopens / blocks
→ freeze accepted authority
```

The 417-version Puglia file is candidate material. A local PASS, prior review,
row count or current-source checkpoint cannot promote it to authority.

## Governing sequence for later stages

Stages B–G retain the sequence below unless Owen closes a stage-specific
verification plan differently during its pre-stage grill.

```text
accepted prior stage
→ exhaustive attack plan
→ coherent prior-stage result + proposed next-stage plan presentation
→ one-question-at-a-time pre-stage grill
→ Owen closes all plan decisions
→ execute the stage
→ internal deterministic/mechanical verification
→ independent multi-faceted review
→ row-by-row finding adjudication
→ repair accepted defects
→ fresh multi-faceted re-review of the repaired artifact
→ all required facets PASS
→ coherent post-stage presentation
→ one-question-at-a-time post-stage grill
→ Owen accepts / deletes / reopens / blocks
→ freeze accepted authority
→ open the next stage only
```

No later stage starts from provisional decisions. A failed review keeps the current stage open. A local green gate does not open the post-stage grill by itself.

## Before execution

### 1. Exhaustive attack plan

Connor authors the plan. It states:

- exact purpose and end state;
- exact scope and negative scope;
- controlling authority and recursive dependencies;
- output schemas and consumers;
- mechanical completeness checks;
- semantic, practitioner and adversarial checks;
- decisions Owen must close;
- what would falsify the approach;
- which earlier stage can reopen and under what evidence;
- review facets required after execution.

### 2. Coherent presentation

Before the first grill question, present:

- what the prior stage accepted;
- what remains authoritative;
- what the next stage proposes;
- why the stage exists;
- outputs, exclusions and downstream consumers;
- failure modes and verification design;
- the complete decision tree the grill must close.

### 3. Pre-stage grill

Ask one decision at a time. Provide a recommendation and consequences. Retrieve facts rather than asking Owen. Execution begins only after every load-bearing decision is closed.

## Execute and verify

### 4. Execution

Build the declared stage artifact only. Do not pull downstream design into the stage. Preserve stable IDs, temporal versions, source evidence and accepted upstream boundaries.

### 5. Internal verification

Internal checks prove the artifact is mechanically reproducible and that its declared invariants discriminate. Depending on the stage, this includes:

- deterministic regeneration;
- schema and reference closure;
- exact source-span checks;
- population conservation;
- point-in-time interval checks;
- real-population sweeps;
- property, boundary and negative controls;
- mutation testing of the actual gate;
- independent calculations where numeric claims exist.

Tests are evidence. They are not a review facet and do not certify purpose, domain correctness or architecture.

### 6. Independent multi-faceted review

Reviewers work in independent contexts. Each receives the current authority, artifact, scope, negative scope, prior failed classes, evidence paths and explicit instruction to verify rather than trust the brief.

The standing facets are:

1. **Canon, operator and telos alignment**  
   Does the stage serve the Osservatorio’s accepted decisions and the loss-reduction objective? Does it preserve scope and avoid over-provenance, N=1 design and downstream creep?

2. **Domain, authority and practitioner correctness**  
   Is the artifact correct under the relevant law, science, operational practice and authority hierarchy? This facet splits into separate expertise lanes when jurisdictions or disciplines are independently load-bearing.

3. **Semantic and technical architecture**  
   Are identity, grain, versions, ASTs, formulas, data contracts, Actions, relationships or ontology mechanisms structurally correct for this stage? Does the artifact support its declared downstream consumer without importing the consumer prematurely?

4. **Source, population, lineage and coverage**  
   Is the denominator correct? Are conflicts, gaps, source roles, joins, annexes, identities, effective intervals and excluded populations explicit? Can the completeness claim survive an independent reconstruction?

5. **Adversarial verification and generalization**  
   Attack the strongest claim, reproduce defects, test materially different cases and populations, and verify the gate can fail. Do not manufacture unrelated edge cases or expand the declared slice.

A single reviewer may not self-certify multiple independently load-bearing facets merely by mentioning them. Combine facets only when they share the same expertise and evidence substrate; keep the verdicts separate.

### 7. Adjudication and re-review

Connor reads every report in full. Every finding receives:

```text
finding_id
facet
severity
assertion
exact evidence
current-authority check
factual disposition
implementation disposition
repair or rejection reason
dependent surfaces
verification check
status
```

A correct diagnosis does not automatically accept the reviewer’s cure. Repair accepted defects. Then dispatch fresh independent review against the repaired artifact. Previous PASS results become stale after a load-bearing change.

The stage reaches review closure only when every required facet returns PASS with no unresolved Critical/High finding and all lower findings have explicit dispositions consistent with the stage acceptance bar.

## Post-stage gate

### 8. Coherent post-stage presentation

Present the complete stage result, not only counts or findings:

- purpose and operator decision changed;
- accepted outputs and authority surfaces;
- exact scope and negative scope;
- review facets and verdicts;
- repaired and rejected findings;
- bounded gaps and authority judgments;
- what stays backstage;
- downstream contract;
- proposed status of the next stage.

### 9. Post-stage grill

One question at a time. The grill determines:

- what should be retained;
- what should be deleted;
- what became first-class;
- what remains backstage;
- whether an earlier stage was falsified;
- whether the current stage is accepted;
- whether the next stage opens.

Only Owen accepts the stage. After acceptance, update the current authority and task ledger. Downstream work consumes only accepted authority surfaces.

## Stage-specific outputs and review facets

### Stage A — provision decision map

**Output**

- stable provisions and immutable versions;
- actor, owner, modality, trigger, pure condition AST, branch and effect;
- exception, scope, evidence, notice, effectiveness and source span;
- recursive dependency/citation closure;
- authority judgments and bounded gaps;
- jurisdictional/case-family mappings.

**Connor whole-forest verification passes**

1. EU/Italian national legal authority and temporal hierarchy.
2. Puglia/Osservatorio legal-practitioner correctness.
3. Source population, UOR identity, annex, citation and lineage closure.
4. Atomic semantics, parents, condition ASTs, branches and dependency closure.
5. Downstream clock/parameter/math readiness without Stage B/C leakage.
6. Canon/telos/aperture discipline and adversarial generalization.

These are perspectives inside one Connor-owned whole-forest verification, not
delegated facets or source-specific review rounds. Stage A passes only after the
complete forest resolves coherently in both directions and Owen explicitly
freezes it.

### Stage B — clocks and parameters

**Output**

- clock definitions;
- parameter definitions;
- timing interpretations;
- clock/parameter dependency graph;
- validation and bounded unresolved inputs.

**Required review facets**

1. Legal clock wording, anchor, actor, consequence and point-in-time version.
2. Scientific/statistical parameter authority, uncertainty and legal-effect ceiling.
3. Temporal mechanics: windows, recurrence, lookbacks, pause/stay, reset and branch interaction.
4. Osservatorio operational usefulness and authority-stack propagation.
5. Source completeness and parameter lineage.
6. Adversarial boundary review: no geometry/math/data/Action leakage from C–E.

### Stage C — deterministic math and geometry

**Output**

- formulas and predicate evaluators;
- statutory-minimum candidates;
- adopted-geometry and open-term interfaces;
- survey adequacy and achieved-assurance calculations;
- deterministic decision envelopes.

**Required review facets**

1. Legal-to-math fidelity.
2. Geospatial/CRS/topology correctness.
3. Statistical survey and diagnostic math correctness.
4. Algorithm/DSA, numerical stability and boundary behavior.
5. Reproducibility, independent recomputation and mutation/property tests.
6. Operator/telos and generalization across materially different cases.

### Stage D — data and evidence contracts

**Output**

- one contract per required predicate/formula input;
- source class, owner, locator, grain, keys, version, cadence and completeness;
- conflict, missingness, correction and access behavior;
- public versus controlled evidence boundaries.

**Required review facets**

1. Source authority and domain meaning.
2. Population, identity, joins, grain and lineage.
3. Data engineering, refresh, correction and reproducibility.
4. Privacy, security, permissions and protected evidence.
5. Predicate/formula coverage and honest unavailable states.
6. Adversarial absence/generalization review and operator usefulness.

### Stage E — generalized Actions and external events

**Output**

- generalized action families;
- authority, actor, parameters, preconditions, refusal criteria and atomic effects;
- external-event ingestion/reconciliation;
- idempotency, concurrency and evidence-of-completion contracts.

**Required review facets**

1. Legal authority, permissions and reserved decisions.
2. Osservatorio practitioner workflow.
3. Action atomicity, refusal, idempotency and successor-state semantics.
4. Security, privacy and auditability.
5. Platform/transaction architecture and failure recovery.
6. Canon/telos, minimal action catalogue and adversarial execution tests.

### Stage F — minimum nouns and fact-bearing relationships

**Output**

- real-world noun set;
- fact owners;
- relationships, direction, cardinality, metadata and lifecycle;
- admission/rejection rationale;
- coverage of every accepted decision and Action.

**Required review facets**

1. Domain/practitioner reality.
2. Semantic identity, lifecycle and one-fact-one-owner.
3. Relationship grain, direction, cardinality and temporal metadata.
4. Decision/Action coverage.
5. Minimality, type-budget trajectory and anti-governance-product discipline.
6. Adversarial population/generalization and canon/telos review.

### Stage G — Foundry Ontology derivation

**Output**

- Objects and Properties;
- Links and relationship objects with cardinalities;
- Interfaces;
- Actions and Functions;
- permissions, writeback and audit types;
- migration/build order;
- live type-budget arithmetic and headroom.

**Required review facets**

1. Canon/product/operator alignment.
2. Foundry Ontology and platform architecture/DSA.
3. Domain-semantic fidelity to Stage F and Stage A decisions.
4. Actions/Functions authority, transaction and AIP boundaries.
5. Security, permissions, privacy and audit.
6. Type budget, migration overlap and deployability.
7. Adversarial end-to-end acceptance and N>1 generalization.

Stage G acceptance opens platform-build planning only. It does not itself authorize a Foundry write. Platform work follows its own reviewed build plan, implementation cycles, three-lane implementation review and read-back verification.

## Current Stage A posture

Accepted EU outputs, the accepted national core, completed Step 4
readings and Step 5 joint adjudication are the Step 6 authority. The current
Puglia suffix remains candidate material despite local regeneration, validation
or historical review results.

Reconciliation proceeds by missing bidirectional forest relationship. Connor
then performs bounded mechanical checks and one whole-forest verification using
the six Stage A perspectives above. No delegated or source-specific review is
required or permitted before Owen's post-stage grill.
