# Jurisdictional Stage A schema derivation authority

Status: **supporting schema evidence — no current-authority effect**

Current authority: `STAGE_A_AUTHORITY_SNAPSHOT.json`.
Date: 27 August 2026
Baseline: accepted EU Stage A schema in `regulation/stage-a/SCHEMA.md`

## Governing rule

The jurisdictional overlay uses the accepted EU Stage A schema as its baseline. National/Puglia fields are additive only where the authority chain introduces a real semantic distinction.

The overlay must not rename, collapse or remove accepted fields. A display or compiler adapter cannot cure a semantic schema mismatch.

## Why each accepted field exists

### Stable identity and hierarchy

| Field | Derivation reason | Failure prevented |
|---|---|---|
| `instrument_id` | A proposition belongs to one enduring legal instrument. | Treating a citation, portal row or later act as the instrument itself. |
| `stable_provision_id` | One legal atom survives text/status changes. | Latest-only law and duplicate identity per consolidation. |
| `parent_stable_provision_id` | Legal hierarchy differs from PDF placement. | Final subparagraphs attached to the last lettered point instead of all siblings. |
| `article` | Preserve the source legal locator. | Losing the path from rule to source structure. |
| `structural_kind` | Stem, paragraph, point and subparagraph behave differently. | Flattening composite conditions into one apparent rule. |
| `scope_status` | Implemented, dependency and deferred propositions coexist. | Deferred movement families disappearing or minting speculative transactions. |

### Temporal and source identity

| Field | Derivation reason | Failure prevented |
|---|---|---|
| `provision_version_id` | Versions are immutable legal states, not mutable latest rows. | Rewriting historical meaning. |
| `effective_from`, `effective_to_exclusive` | Applicability changes with legal effect, not search date. | Judging a historical act under current law. |
| `application_basis` | Publication, entry into force, delayed application and status-only boundaries differ. | Equating publication date, consolidation date and legal effect. |
| `source_uri` | The authoritative source route remains explicit. | Local copies becoming unidentified authority. |
| `source_snapshot_hashes`, `source_snapshot_dates` | Dated consolidations prove the exact comparison. | Treating one stale snapshot as current law. |
| `verbatim_text` | Semantic authoring remains checkable against exact text. | A summary silently replacing the operative clause. |
| `exact_change_kind` | Text change, status change and initial state are distinct. | Missing a delayed application because the text did not change. |
| `semantic_change` | Formatting-only snapshots do not create legal changes. | Amendment narrative and duplicate versions becoming the product. |

These fields were required after the amendment ruling proved that Annex II, Annex III and Annex IV changes reverse real answers. The accepted model records validity, not amendment narrative.

### Conditional legal meaning

| Field | Derivation reason | Failure prevented |
|---|---|---|
| `actor_role` | The bearer of a duty is not automatically the decision owner. | ARIF, Osservatorio, owner and Comune authority collapse. |
| `modality` | `shall`, `may` and `shall not` have different legal effects. | Eligibility being confused with authority election. |
| `trigger_expression` | The event/state activating the proposition must be explicit. | Geometry, wording or office identity used as a proxy for a trigger. |
| `conditions` | Preserve the complete structured legal condition expression. | Prose or family labels replacing legal conditions. |
| `conjunction` | Top-level AND/OR/route structure must remain visible. | Internal OR short-circuiting an outer AND. |
| `true_effect`, `false_effect` | Both legal routes are part of the decision. | Missing evidence or a failed condition becoming an invented negative. |
| `required_legal_effect` | Mandatory work remains visible even when calculation/evidence is incomplete. | Judgment-heavy duties disappearing as “not computable.” |
| `reserved_decision_owner` | A deterministic availability test does not exercise a `MAY` power. | Software taking a public decision. |
| `clock_rule` | Reserved Stage A field; always `-`. Complete source wording remains for Stage B derivation. | Clock extraction leaking backward into Stage A. |
| `numeric_parameters` | Reserved Stage A field; always `-`. Complete source wording remains for Stage B derivation. | Parameter extraction leaking backward into Stage A. |
| `evidence_contract` | Every predicate names what proves pass/fail/completion. | Public absence or proxy evidence becoming legal fact. |
| `external_dependencies` | Own the complete declared cross-proposition dependency set. | A locally complete row with an incomplete legal mechanism. |

### Five independent evaluation axes

The original `computable` field collapsed five different questions. The accepted schema separates them:

| Field | Question |
|---|---|
| `rule_determinacy` | Does the law define a rule, or reserve evidence/policy/judgment? |
| `calculation_support` | Does this proposition support logic, classification, a parameter or a later calculation? |
| `public_observability` | Can public evidence establish the fact? Stage D owns the answer. |
| `government_availability` | Does the authority hold controlled evidence? Stage D owns the answer. |
| `authority_judgment_required` | Must a competent actor interpret or exercise discretion? |

These fields prevent `not public`, `not calculated`, `not deterministic`, `not held` and `not legally required` from becoming one false state.

### Interpretation and conflict

| Field | Derivation reason |
|---|---|
| `authority_judgment_kind` | Names the exact open proposition without preselecting an ontology object. |
| `legal_linguistic_conflict` | Retains authentic-language differences that change executable meaning. |
| `semantic_note` | Carries a bounded interpretation without becoming an Action or source-system assumption. |

## Accepted jurisdictional additions

The selective reopening explicitly authorized the accepted field contract **plus** the fields below.

| Addition | Why jurisdictional law requires it |
|---|---|
| `jurisdiction` | EU, Italy and Puglia propositions have different rank and competence. |
| `legal_rank` | Conflict adjudication uses rank, competence, time and scope. |
| `structural_label` | National/regional instruments use heterogeneous article, point, annex and dispositive locators. |
| `decision_owner` | Regional processes distinguish duty bearer from the authority owning the decision. |
| `source_evidence_class` | Full primary text, current authentic provision, exact quote, metadata-only and unavailable evidence support different claim ceilings. |
| `territorial_scope` | Regional acts bind propositions to exact areas/components. |
| `subject_scope` | Operator, owner, plant, area and campaign populations differ. |
| `population_scope` | Removal, survey, planting and aid rules act on different populations. |
| `supersession_scope` | A successor can replace one deadline or annex without replacing the whole mechanism. |
| `higher_authority_dependencies` | Classify the authority-bearing subset of `external_dependencies`; external-only members are incorporated support. |
| `local_effect_kind` | Area adoption, notice, execution, indemnity and enforcement have distinct local effects. |
| `notice_rule` | Municipal posting, PEC, BURP and regional Albo publication are separate legal events. |
| `effectiveness_rule` | Notice and legal effectiveness are not interchangeable. |
| `exception_or_derogation` | Regional sources add or select operative exceptions. |
| `source_path`, `source_quote`, `source_hash` | Held local primary bodies provide reproducible exact support in addition to source URI/snapshot fields. |

These additions extend the accepted contract. They do not replace `reserved_decision_owner`, `clock_rule`, the five axes, temporal/source snapshot fields, or graph operators.

## Condition graph contract

The accepted graph row retains:

```text
stable_provision_id
operator
expression
true_effect
false_effect
```

Allowed nodes:

```text
predicate · all_of · any_of · not · provision_ref · route_table · otherwise
```

The jurisdictional graph must keep the same envelope and grammar. A pure AST is the source for the interactive node graph and downstream deterministic evaluation.

## Repair implication

The current jurisdictional artifact is not acceptance-eligible because it replaced rather than extended the accepted schema. The next compiler output must:

1. preserve every accepted field and graph key;
2. add only the authorized jurisdictional fields above;
3. populate each field from reviewed authoring or an explicit unresolved/deferred value;
4. expose missing semantic authoring as a gate failure rather than fabricate values;
5. regenerate the interactive graph from the schema-compatible artifacts;
6. rerun all affected Stage A review facets after the final change.
