# CORDON Reference Library — INDEX

Purpose: retrieval index for AI FDE during the CORDON Wedge 1 build. Read this file first in every session. Then retrieve exactly the files the active prompt names. Every file here is a governing authority. Authorities are read-only context. Never edit them on the platform.

This repository is a Python Transforms code repository used as a document store. Ignore the template scaffolding (`build.gradle`, `gradle*`, `ci.yml`, `templateConfig.json`, `transforms-python/`, lock files); only `INDEX.md`, `authorities/` and `semantic-pack/` are governing content.

## Bundles

| Bundle | Meaning | Files (repo path) |
|---|---|---|
| G0 | Governing authorities | `authorities/REDESIGN_SEQUENCE.md`; `authorities/gate-5-reconciled-operator-graph.md`; `authorities/gate-6-capability-reconciliation.md`; `authorities/gate-6-data-mechanism-purpose-ledger.md`; `authorities/gate-6-aip-mechanism-purpose-ledger.md`; `authorities/gate-5-minimum-operator-properties.md` |
| S0 | Accepted surface architecture | `authorities/gate-7-operator-surface-architecture-comparison.md` |
| D0 | Real-data mapping ledger | `authorities/gate-7-real-data-to-ontology-mapping-ledger.md` |
| P | Prompt set / operating contract | `authorities/gate-7-ai-fde-ontology-handoff-prompts.md` |
| O0 | Owen-approved semantic pack | `semantic-pack/` — see status below |

Reading precedence: `REDESIGN_SEQUENCE.md` → `gate-5-reconciled-operator-graph.md` → `gate-6-capability-reconciliation.md` → the two Gate 6 mechanism-purpose ledgers → `gate-5-minimum-operator-properties.md` (subordinate where reconciliation changed history representation or type count). S0 fixes the surface. D0 fixes source admission. P fixes the operating contract.

## Per-prompt retrieval

| Prompt | Retrieve |
|---|---|
| 00 | P; G0; S0 |
| 01 | P; G0; D0 |
| 02 | P; G0 |
| 03 | P; G0; D0 |
| 04 | P; G0; D0; O0 `now-view-projection-contract.md` |
| 05 | P; G0; D0 |
| 06 | P; G0; D0; O0 kernel sheets (all four) — REQUIRED |
| 07 | P; G0; O0 kernel sheets (all four) — REQUIRED |
| 08 | P; G0; O0 `kernel-commit-or-rebalance-intervention-capacity.md` |
| 09 | P; G0; D0 |
| 10 | P; G0; S0; O0 `chatbot-tool-schema.md` — REQUIRED |
| 11 | P; G0; O0 kernel sheets; O0 `chatbot-tool-schema.md` |
| 12 | P; G0 |
| 13 | P; G0; S0 |
| 14 | P; G0; S0 |

## O0 semantic pack status

| Sheet | File | Status |
|---|---|---|
| Kernel — Accept Cooperative Execution Mandate | `semantic-pack/kernel-accept-cooperative-execution-mandate.md` | APPROVED (Owen, 2026-08-23) |
| Kernel — Decide Cooperative Pursuit | `semantic-pack/kernel-decide-cooperative-pursuit.md` | APPROVED (Owen, 2026-08-23) |
| Kernel — Commit or Rebalance Intervention Capacity | `semantic-pack/kernel-commit-or-rebalance-intervention-capacity.md` | APPROVED (Owen, 2026-08-23) |
| Kernel — Dispatch Intervention | `semantic-pack/kernel-dispatch-intervention.md` | APPROVED (Owen, 2026-08-23) |
| Now-view projection contract | `semantic-pack/now-view-projection-contract.md` | APPROVED (Owen, 2026-08-23) |
| Chatbot tool schema | `semantic-pack/chatbot-tool-schema.md` | APPROVED (Owen, 2026-08-23) |

All six sheets are APPROVED and present, including `semantic-pack/README.md` (shared kernel conventions and the closed decision log D1–D5). If a sheet does not answer an implementation question, the question routes to Owen. No agent invents a predicate, tool, status field, or data binding.

## Hard boundaries

- The historical `CORDON-Wedge-1` project is read-only evidence. Never open a write path to it.
- The build occurs only in the `CORDON` project on the approved Global Branch, per prompt P02.
- This repository's default branch holds authorities only. No build code lands here.
