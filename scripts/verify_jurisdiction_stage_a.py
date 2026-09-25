#!/usr/bin/env python3
"""Verify the canonical jurisdictional Stage A decision map.

This gate checks serialization and named semantic invariants. It supports, but
never replaces, source reading and legal adjudication.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

from verify_stage_a import ast_nodes, verify_result_references

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUTHORING = ROOT / "regulation/jurisdiction/canonical/authoring.json"
EU_STABLE = ROOT / "regulation/stage-a/stable-provisions.csv"
GENERATED = ROOT / "regulation/jurisdiction/generated"
AUTHORITY = ROOT / "state/CURRENT.json"


def fail(message: str) -> None:
    raise AssertionError(message)


def refs(value: Any) -> list[str]:
    out: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "provision_ref" and isinstance(child, str):
                out.append(child)
            else:
                out.extend(refs(child))
    elif isinstance(value, list):
        for child in value:
            out.extend(refs(child))
    return list(dict.fromkeys(out))


def nested_otherwise(value: Any, path: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    out: list[tuple[Any, ...]] = []
    if isinstance(value, dict):
        if "otherwise" in value and path:
            out.append(path)
        for key, child in value.items():
            out.extend(nested_otherwise(child, path + (key,)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            out.extend(nested_otherwise(child, path + (index,)))
    return out


def effect_set(row: dict[str, Any]) -> set[str]:
    return {route["effect"] for route in row["condition_ast"].get("route_table", [])}


def get(by: dict[str, list[dict[str, Any]]], sid: str, latest: bool = True) -> dict[str, Any]:
    candidates = by.get(sid, [])
    if latest:
        candidates = [row for row in candidates if row.get("temporal_status") != "SUPERSEDED"]
    if len(candidates) != 1:
        fail(f"{sid}: expected one {'latest ' if latest else ''}row, got {len(candidates)}")
    return candidates[0]


def verify(authoring: Path, check_projection: bool, check_authority: bool) -> dict[str, int]:
    rows = json.loads(authoring.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        fail("canonical authoring must be a non-empty array")
    eu_rows = json.loads((ROOT / "regulation/stage-a/authoring-eu.json").read_text(encoding="utf-8"))
    verify_result_references(rows, eu_rows + rows)
    removed_fields = {
        "verbatim_text", "semantic_equivalence_key", "scope_status",
        "public_observability", "government_availability", "clock_rule",
        "numeric_parameters", "conjunction", "conditions", "trigger_expression",
        "calculation_support", "required_legal_effect", "is_latest",
    }
    for row in rows:
        present = removed_fields.intersection(row)
        if present:
            fail(f"{row['provision_version_id']}: removed schema field reintroduced: {sorted(present)[0]}")
    # A correction or supplement names the instruments it corrects; its own quote cites each one.
    act_id = re.compile(r"(.+)-(\d{4})-(\d{5})")
    for row in rows:
        if "corrects_instrument_ids" not in row:
            continue
        corrected, own = row["corrects_instrument_ids"], act_id.fullmatch(row["instrument_id"])
        if not own or not isinstance(corrected, list) or not corrected or len(set(corrected)) != len(corrected):
            fail(f"{row['provision_version_id']}: corrects_instrument_ids is a non-empty list of distinct instruments")
        for instrument in corrected:
            match = act_id.fullmatch(instrument) if isinstance(instrument, str) else None
            if not match or match[1] != own[1] or instrument == row["instrument_id"]:
                fail(f"{row['provision_version_id']}: {instrument} is not another act of the same series")
            if not re.search(rf"\b0*{int(match[3])}\b[^\n]{{0,30}}?{match[2]}", row["source_quote"]):
                fail(f"{row['provision_version_id']}: source quote does not cite corrected instrument {instrument}")
    for row in rows:
        higher = set(row.get("higher_authority_dependencies", []))
        external = set(row.get("external_dependencies", []))
        if not higher.issubset(external):
            missing = sorted(higher - external)[0]
            fail(f"{row['provision_version_id']}: higher authority missing from external dependency inventory: {missing}")
    by: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by[row["stable_provision_id"]].append(row)

    version_ids = [row["provision_version_id"] for row in rows]
    if len(version_ids) != len(set(version_ids)):
        fail("duplicate provision version ID")
    for row in rows:
        if hashlib.sha256(row["source_quote"].encode()).hexdigest() != row["source_quote_sha256"]:
            fail(f"{row['provision_version_id']}: source quote hash mismatch")
        bad_paths = nested_otherwise(row["condition_ast"])
        if bad_paths:
            fail(f"{row['provision_version_id']}: nested otherwise at {bad_paths[0]}")

    normalize = lambda text: re.sub(r"\s+", " ", text).strip()
    source_anchors = {
        "IT-DM-2022-XYLELLA-PLAN:§6.7:containment-surveillance-band-5km": ["monitoraggio e' effettuato almeno nell'area di 5 km"],
        "IT-DM-348260-2026-XYLELLA-PLAN:§9.3:containment-surveillance-band-2km": ["area di almeno 2 km", "0,7%"],
        "IT-DM-348260-2026-XYLELLA-PLAN:§9.2:containment-vector-treatment-coverage": ["tempistica di esecuzione", "effettiva efficacia", "area di almeno 2 km"],
        "IT-DM-348260-2026-XYLELLA-PLAN:§8.2:action-plan-15-day-unit-conflict": ["nei successivi 15 giorni", "CFN approva il PA"],
        "PUG-DGR1593-2024:Art7(3)-policy": ["olivi monumentali ufficialmente riconosciuti", "comma 3 dell’art. 7"],
        "PUG-DGR1593-2024:notice-owner-election": ["entro massimo 3 giorni"],
        "PUG-DGR1593-2024:notice-silence-substitute-execution": ["decorsi 3 giorni", "10 giorni successivi"],
        "PUG-DGR1593-2024:notice-refusal-forced-removal": ["rimozione forzosa"],
        "PUG-DGR538-2021:notice-owner-election": ["entro massimo 7 giorni"],
        "PUG-DGR538-2021:notice-silence-substitute-execution": ["decorsi 7 gg"],
        "REG-PUGLIA-U181-DIR-2022-00006:case-delta:seasonal-no-treatment-judgment": ["non deve essere eseguito", "non necessario in questo periodo"],
        "REG-PUGLIA-U181-DIR-2021-00135:case-delta:seasonal-no-treatment-judgment": ["non effettuare", "non necessario in questo periodo"],
        "REG-PUGLIA-U181-DIR-2025-00045:sample-custody-transfer": ["stessa giornata", "due Assistenti fitosanitari", "personale autorizzato al trasporto"],
        "REG-PUGLIA-U181-DIR-2025-00045:cq-analytical-result-classification": ["Cq< 32", "Cq>32 e < 35", "Cq> 35"],
    }
    for sid, anchors in source_anchors.items():
        for row in by[sid]:
            quote = normalize(row["source_quote"])
            for anchor in anchors:
                if normalize(anchor) not in quote:
                    fail(f"{row['provision_version_id']}: source anchor missing: {anchor}")

    for sid, versions in by.items():
        ordered = sorted(versions, key=lambda row: row["effective_from"] or "0000-00-00")
        if sum(row.get("temporal_status") != "SUPERSEDED" for row in ordered) > 1:
            fail(f"{sid}: multiple latest versions")
        for left, right in zip(ordered, ordered[1:]):
            if (left["effective_to_exclusive"] or "9999-12-31") > (right["effective_from"] or "0000-00-00"):
                fail(f"{sid}: temporal overlap")

    # Classification order is explicit and contiguous.
    is_regional = lambda row: row["instrument_id"].startswith("PUG-") or row["instrument_id"].startswith("REG-PUGLIA-")
    first_regional = next(index for index, row in enumerate(rows) if is_regional(row))
    if any(not is_regional(row) for row in rows[first_regional:]):
        fail("national/reached-dependency row occurs after regional block")

    with EU_STABLE.open(newline="", encoding="utf-8-sig") as handle:
        eu = {row["stable_provision_id"].removeprefix("EU-2020-1201:") for row in csv.DictReader(handle)}
    canonical = set(by)
    for row in rows:
        for ref in refs(row["condition_ast"]):
            if ref not in canonical and ref.removeprefix("EU-2020-1201:") not in eu:
                fail(f"{row['provision_version_id']}: unresolved AST reference {ref}")

    # Master containment partition is disjoint by named state and preserves invalid area.
    master = get(by, "PUG-LR4-2017:Art.6(1)")
    required_master = {
        "VALID_AREA_REQUIRED; PRESERVE_ANY_OUTSTANDING_EU_ARTICLE_4_DUTY",
        "LEGAL_CONFLICT_OR_AUTHORITY_ADJUDICATION_REQUIRED",
        "CONTAINMENT_SUBSTITUTES_FOR_ERADICATION",
        "ERADICATION_CONTROLS",
        "CONTAINMENT_VALIDITY_ADJUDICATION_REQUIRED",
    }
    if not required_master <= effect_set(master):
        fail("master containment partition incomplete")
    ast_text = json.dumps(master["condition_ast"], ensure_ascii=False)
    if ast_text.count("mutually incompatible operative eradication and containment selections") < 3:
        fail("master containment routes are not explicitly disjoint: conclusive routes must exclude the incompatibility conflict")
    if "CONTAINMENT_AUTHORITY_OR_SELECTION_EVIDENCE_REQUIRED" not in ast_text:
        fail("master containment missing-evidence result absent")

    containment_children = {
        "IT-DM-2022-XYLELLA-PLAN:§6.6.2:containment-vector-treatment-band-5km",
        "IT-DM-2022-XYLELLA-PLAN:§6.7:containment-surveillance-band-5km",
        "IT-DM-348260-2026-XYLELLA-PLAN:§9.3:containment-surveillance-band-2km",
        "IT-DM-348260-2026-XYLELLA-PLAN:§9.2:containment-vector-treatment-coverage",
        "PUG-LR4-2017:Art.6(2)",
        "PUG-LR4-2017:Art.6(3)",
        "REG-PUGLIA-U181-DIR-2025-00045:containment-treatment-removal-sequence",
        "REG-PUGLIA-U181-DIR-2025-00045:containment-root-wood-completion",
        "REG-PUGLIA-U181-DIR-2025-00045:containment-execution-evidence",
        "REG-PUGLIA-U181-DIR-2024-00158:containment-selection",
    }
    propagated = {
        "CONTAINMENT_CHILD_NOT_APPLICABLE; ERADICATION_CONTROLS",
        "LEGAL_CONFLICT_OR_AUTHORITY_ADJUDICATION_REQUIRED",
        "CONTAINMENT_VALIDITY_ADJUDICATION_REQUIRED",
        "VALID_AREA_REQUIRED; PRESERVE_ANY_OUTSTANDING_EU_ARTICLE_4_DUTY",
        "CONTAINMENT_AUTHORITY_OR_SELECTION_EVIDENCE_REQUIRED",
    }
    for sid in containment_children:
        for child in by[sid]:
            child_effects = effect_set(child)
            if not propagated <= child_effects:
                fail(f"{child['provision_version_id']}: master result not fully propagated")
            for route in child["condition_ast"]["route_table"]:
                if route["effect"] in propagated:
                    continue
                if "CONTAINMENT_SUBSTITUTES_FOR_ERADICATION" not in json.dumps(route["when"], ensure_ascii=False):
                    fail(f"{child['provision_version_id']}: child-specific route can swallow parent result")

    eradication = get(by, "IT-DLGS-19-2021:Art.31(3):eradication-regime")
    eradication_text = json.dumps(eradication["condition_ast"], ensure_ascii=False)
    if '"not"' in eradication_text or "ERADICATION_CONTROLS" not in eradication_text:
        fail("eradication regime uses unsafe negation or omits resolved parent result")

    # EU duty and national procedure remain independent.
    area_duty = get(by, "IT-DLGS-19-2021:Art.31(3):establish-demarcated-area")
    if "EU_ARTICLE_4_DEMARCATION_DUTY_OUTSTANDING" not in effect_set(area_duty):
        fail("Article 4 duty is not independently preserved")
    if "committee opinion" in json.dumps(area_duty["condition_ast"], ensure_ascii=False).lower():
        fail("Article 4 duty improperly depends on national committee opinion")
    opinion = get(by, "IT-DLGS-19-2021:Art.6(3)(g)")
    if "PRIOR_COMMITTEE_OPINION_DUTY_BREACHED" not in json.dumps(opinion["condition_ast"]) or "REGIONAL_AREA_DECISION_AUTHORITY_ESTABLISHED" not in json.dumps(opinion["condition_ast"]):
        fail("national opinion duty and area authority not separately represented")
    area_validity = get(by, "PUG-LR4-2017:Art.3(2)")
    validity_text = json.dumps(area_validity["condition_ast"], ensure_ascii=False)
    if "SOURCE_STATED_GEOGRAPHY_HELD" not in validity_text or "OPERATIVE_LEGAL_AREA_STATE_ESTABLISHED" not in validity_text:
        fail("source geography and operative area validity are collapsed")

    # Puglia consumes the EU population and post-exception result, not a second provenance rule.
    article13 = get(by, "PUG-LR4-2017:Art.6(2)")
    activation = next((route["when"] for route in article13["condition_ast"].get("route_table", [])
                       if route["effect"] == "ARTICLE_13_REMOVAL_ACTIVATED"), None)
    if activation is None:
        fail("shared Puglia Article 13 removal activation is missing")
    for sid, effect in (("EU-2020-1201:13(1)", "ARTICLE_13_BASELINE_REMOVAL_POPULATION"),
                        ("EU-2020-1201:13(2)", "ARTICLE_13_REMOVAL_STANDS")):
        required = {"result_ref": {"producer_stable_provision_id": sid, "allowed_effect": effect}}
        if required not in list(ast_nodes(activation)):
            fail("shared Puglia Article 13 route lacks the controlling population or exception result")
    population13 = next(row for row in eu_rows if row["stable_provision_id"] == "EU-2020-1201:13(1)")
    if "the finding arose from the Article 15(2) monitoring" not in json.dumps(population13["condition_ast"]):
        fail("EU Article 13 population lacks Article 15(2) provenance")

    # Retained wood never reaches full-destruction results.
    for sid, full_effect, retained_effect in (
        ("REG-PUGLIA-U181-DIR-2025-00045:root-wood-completion", "ARTICLE_9_1_FULL_DESTRUCTION_COMPLETE", "ARTICLE_9_2_LIMITED_DESTRUCTION_COMPLETE"),
        ("REG-PUGLIA-U181-DIR-2025-00045:containment-root-wood-completion", "ARTICLE_16_1_FULL_DESTRUCTION_COMPLETE", "ARTICLE_16_2_LIMITED_DESTRUCTION_COMPLETE"),
    ):
        row = get(by, sid)
        routes = {route["effect"]: json.dumps(route["when"], ensure_ascii=False) for route in row["condition_ast"]["route_table"]}
        if "no wood retained" not in routes.get(full_effect, ""):
            fail(f"{sid}: full destruction does not exclude retained wood")
        if "wood retained" not in routes.get(retained_effect, ""):
            fail(f"{sid}: retained-wood route missing")

    # Article 31(1) substance and 31(2) notification are separate.
    art31 = get(by, "EU-2016-2031:Art.31:more-stringent-national-measures")
    if "notification" in json.dumps(art31["condition_ast"], ensure_ascii=False).lower():
        fail("Article 31(1) substantive route depends on notification")
    art31n = get(by, "EU-2016-2031:Art.31(2):more-stringent-measure-notification")
    if "NOTIFICATION_BREACH" not in json.dumps(art31n["condition_ast"]):
        fail("Article 31(2) notification breach state missing")

    # Unsupported regional Article 13(2) policy is absent.
    if "PUG-DGR343-2022:Art13(2)-scientific-retention-policy" in canonical:
        fail("unsupported DGR 343 Article 13(2) proposition survives")

    # Concurrent clocks remain separate.
    plan_clock = get(by, "IT-DM-348260-2026-XYLELLA-PLAN:§8.2:action-plan-15-day-unit-conflict")
    if "15-working-day" in json.dumps(plan_clock["condition_ast"]):
        fail("plan clock competes with statutory clock in one route table")

    # Analytical classification and doubtful sequence.
    cq = get(by, "REG-PUGLIA-U181-DIR-2025-00045:cq-analytical-result-classification")
    boundary = next(route for route in cq["condition_ast"]["route_table"] if "BOUNDARY" in route["effect"])
    if "valid analytical evidence" not in json.dumps(boundary["when"]):
        fail("Cq boundary route lacks analytical-validity guard")
    doubtful = get(by, "REG-PUGLIA-U181-DIR-2025-00045:doubtful-result-route")
    required_steps = {"REPEAT_EXTRACTION_AND_HARPER_TEST_REQUIRED", "TEST_INDIVIDUAL_POOL_CONSTITUENTS", "SEND_INDIVIDUAL_TO_CNR_IPSP_ALIQUOT_REVIEW", "NOTIFY_REGIONAL_SERVICE; RECORD_DOUBTFUL_RESULT; RESAMPLE_PLANT"}
    if not required_steps <= effect_set(doubtful):
        fail("doubtful analytical workflow is flattened")

    # Treatment wait failure and proof separation.
    for sid in ("REG-PUGLIA-U181-DIR-2025-00045:treatment-removal-sequence", "REG-PUGLIA-U181-DIR-2025-00045:containment-treatment-removal-sequence"):
        text = json.dumps(get(by, sid)["condition_ast"], ensure_ascii=False)
        if "WAIT_EVIDENCE_REQUIRED" not in text or "SEQUENCE_NONCOMPLIANT" not in text:
            fail(f"{sid}: 48-hour wait outcomes incomplete")
    for sid in ("REG-PUGLIA-U181-DIR-2025-00045:execution-evidence", "REG-PUGLIA-U181-DIR-2025-00045:containment-execution-evidence"):
        text = json.dumps(get(by, sid)["condition_ast"], ensure_ascii=False)
        if "unresolved signature state" in text or "NONEXECUTION_NOT_PROVEN" not in text:
            fail(f"{sid}: unresolved proof satisfies completion or missing proof implies nonexecution")
    executor = get(by, "REG-PUGLIA-U181-DIR-2025-00045:executor-selection")
    if "effective prescription" not in json.dumps(executor["condition_ast"]):
        fail("executor selection lacks effective prescription")

    custody = get(by, "REG-PUGLIA-U181-DIR-2025-00045:sample-custody-transfer")
    custody_text = json.dumps(custody["condition_ast"], ensure_ascii=False)
    if "laboratory receipt digital signature" in custody_text or "transporter digitally countersigns" not in custody_text:
        fail("sample-custody signature actor does not match source")

    # Partial commencement/programme states survive.
    for sid in ("IT-DM-0677268-2021:Art.1(1):CREA-DC-Firenze-designation", "IT-DM-0677268-2021:Art.1(1):CREA-DC-Roma-designation"):
        if "LATER_EVENT_DESIGNATION_STATUS_ESTABLISHED_WITHOUT_RETROACTIVE_START_CONCLUSION" not in effect_set(get(by, sid)):
            fail(f"{sid}: later operative status cannot coexist with unknown original start")

    # Owen's 2026-09-24 rulings: the act's own ground and a surviving annulment test decide mass publicity; the Art. 21-ter
    # notice is A's Art. 21-bis result; a tree is listed only through its own definitively republished, undeleted entry.
    mass = get(by, "IT-L241-A21BIS:Art.21-bis(1):mass-publicity-route")
    if [route["when"] for route in mass["condition_ast"]["route_table"]] != [{"all_of": [
            {"predicate": "the act states its own ground for reaching its recipients by public posting"},
            {"predicate": "the publicity form the act states has been completed"},
            {"not": {"predicate": "a court has annulled the act on its stated ground for public posting"}}]}]:
        fail("Art. 21-bis mass publicity must rest on the act's own ground, completed publicity and no annulment on that ground")
    # The personal branch reads whether communication was effected, not the individual row's effect, so a reasoned
    # immediate-effect clause cannot defeat notice.
    notice = {"any_of": [{"predicate": "the communication to that recipient has been effected, including in the forms "
                                       "prescribed for notification to the unreachable in the cases provided by the code of civil procedure"},
                         {"provision_ref": "IT-L241-A21BIS:Art.21-bis(1):mass-publicity-route"}]}
    if notice not in list(ast_nodes(get(by, "IT-L241-A21TER:Art.21-ter(1):stated-term-coercive-direction")["condition_ast"])):
        fail("Art. 21-ter notice is not the Art. 21-bis communication predicate or mass-publicity result")
    for sid in ("PUG-DGR343-2022:Art7(3)-policy", "PUG-DGR1866-2022:Art7(3)-policy"):
        if not by.get(sid) or any({"provision_ref": "PUG-LR14-2007:Art.5(3):definitive-listing"} not in list(ast_nodes(row["condition_ast"]))
                                  for row in by[sid]):
            fail(f"{sid}: official recognition within the reach is L.R. 14/2007 Art. 5(3) listing")
    listing = get(by, "PUG-LR14-2007:Art.5(3):definitive-listing")
    if [route["when"] for route in listing["condition_ast"]["route_table"]] != [{"all_of": [
            {"predicate": "the tree has its own entry in an Article 5 list"},
            {"predicate": "the Giunta approved that entry definitively and the list containing it was republished on BURP on or before the event date"},
            {"not": {"predicate": "the entry was deleted from the list on or before the event date"}}]}]:
        fail("L.R. 14/2007 listing must rest only on the tree's own definitively republished, undeleted entry")
    if check_projection:
        with (GENERATED / "dependency-manifest.csv").open(newline="", encoding="utf-8-sig") as handle:
            dependencies = list(csv.DictReader(handle))
        represented = {(row["source_provision_version_id"], row["target_ref"]) for row in dependencies}
        for row in rows:
            expected = set(row.get("higher_authority_dependencies", [])) | set(row.get("external_dependencies", [])) | set(refs(row["condition_ast"]))
            missing = {(row["provision_version_id"], ref) for ref in expected} - represented
            if missing:
                fail(f"dependency manifest omits {sorted(missing)[0]}")
        if any(row["status"] == "UNRESOLVED_EXPLICIT" for row in dependencies):
            fail("unresolved dependency manifest edge")

    if check_authority:
        authority = json.loads(AUTHORITY.read_text(encoding="utf-8"))
        stage_a = authority["stages"]["A"]["canonical_artifacts"]["italy_and_puglia"]
        expected_hash = hashlib.sha256(authoring.read_bytes()).hexdigest()
        if stage_a["sha256"] != expected_hash:
            fail("authority canonical hash mismatch")
        if stage_a["provision_versions"] != len(rows):
            fail("authority canonical row count mismatch")
        if stage_a["national_prefix_rows"] != first_regional:
            fail("authority national prefix count mismatch")
        prefix = json.dumps(rows[:first_regional], ensure_ascii=False, indent=2) + "\n"
        if stage_a["national_prefix_sha256"] != hashlib.sha256(prefix.encode()).hexdigest():
            fail("authority national prefix hash mismatch")

    return {"versions": len(rows), "stable": len(by), "national": first_regional, "regional": len(rows) - first_regional}


def run_mutations(authoring: Path) -> None:
    original = json.loads(authoring.read_text(encoding="utf-8"))
    mutations = []

    def drop_effect(rows: list[dict[str, Any]], sid: str, effect: str) -> None:
        row = next(row for row in rows if row["stable_provision_id"] == sid and row.get("temporal_status") != "SUPERSEDED")
        row["condition_ast"]["route_table"] = [route for route in row["condition_ast"]["route_table"] if route["effect"] != effect]

    mutations.append(("drop containment conflict", lambda rows: drop_effect(rows, "PUG-LR4-2017:Art.6(1)", "LEGAL_CONFLICT_OR_AUTHORITY_ADJUDICATION_REQUIRED")))
    def allow_retained_wood(rows):
        row = get({r['stable_provision_id']: [r] for r in rows}, "REG-PUGLIA-U181-DIR-2025-00045:root-wood-completion")
        for node in ast_nodes(row['condition_ast']['route_table'][0]['when']):
            if node.get('predicate') == 'no wood retained':
                node['predicate'] = 'wood retained'
                return
        fail('retained-wood mutation has no target')

    mutations.append(("allow retained wood as full destruction", allow_retained_wood))
    mutations.append(("remove Article 13 provenance", lambda rows: setattr_proxy(next(row for row in rows if row["stable_provision_id"] == "PUG-LR4-2017:Art.6(2)" and row.get("temporal_status") != "SUPERSEDED"), "condition_ast", {"predicate": "official infected-plant finding"})))
    mutations.append(("correction names an instrument its quote does not cite", lambda rows: setattr_proxy(next(row for row in rows if row["stable_provision_id"] == "REG-PUGLIA-U181-DIR-2024-00165:case-delta:annex-only-municipality-correction"), "corrects_instrument_ids", ["REG-PUGLIA-U181-DIR-2024-00146"])))
    def latest(rows, sid):
        return next(row for row in rows if row["stable_provision_id"] == sid and row.get("temporal_status") != "SUPERSEDED")

    def listing_when(rows):
        return latest(rows, "PUG-LR14-2007:Art.5(3):definitive-listing")["condition_ast"]["route_table"][0]["when"]["all_of"]

    mutations.append(("list a tree from its first publication", lambda rows: listing_when(rows).__setitem__(1, {
        "predicate": "the tree has its own entry in a list approved provisionally and published on BURP under Article 5(2) on or before the event date"})))
    mutations.append(("a listed grove lists a tree without its own entry", lambda rows: listing_when(rows).__setitem__(0, {"any_of": [
        {"predicate": "the tree has its own entry in an Article 5 list"}, {"predicate": "the tree stands in a listed monumental grove"}]})))
    mutations.append(("drop the annulment negation", lambda rows: latest(rows, "IT-L241-A21BIS:Art.21-bis(1):mass-publicity-route")[
        "condition_ast"]["route_table"][0]["when"]["all_of"].pop()))
    def personal_notice_reads_effect(rows):
        row = latest(rows, "IT-L241-A21TER:Art.21-ter(1):stated-term-coercive-direction")
        for node in ast_nodes(row["condition_ast"]):
            if "any_of" in node:
                node["any_of"][0] = {"provision_ref": "IT-L241-A21BIS:Art.21-bis(1):individual-communication-effect"}
                return
        fail("personal-notice mutation has no target")

    mutations.append(("personal notice reads the individual row's effect", personal_notice_reads_effect))
    mutations.append(("restore unsupported DGR343 policy", lambda rows: rows.append({**rows[-1], "stable_provision_id": "PUG-DGR343-2022:Art13(2)-scientific-retention-policy", "provision_version_id": "mutant:dgr343"})))

    for label, mutate in mutations:
        mutant = json.loads(json.dumps(original))
        mutate(mutant)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "authoring.json"
            path.write_text(json.dumps(mutant, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            result = subprocess.run([sys.executable, __file__, "--authoring", str(path), "--skip-projections", "--skip-authority"], capture_output=True, text=True)
            if result.returncode == 0:
                fail(f"mutation was not caught: {label}")
            print(f"PASS MUTATION: {label}")


def setattr_proxy(row: dict[str, Any], key: str, value: Any) -> None:
    row[key] = value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authoring", type=Path, default=DEFAULT_AUTHORING)
    parser.add_argument("--skip-projections", action="store_true")
    parser.add_argument("--skip-authority", action="store_true")
    parser.add_argument("--mutation-test", action="store_true")
    args = parser.parse_args()
    counts = verify(args.authoring, not args.skip_projections, not args.skip_authority)
    print("PASS jurisdiction Stage A:", json.dumps(counts, sort_keys=True))
    if args.mutation_test:
        run_mutations(args.authoring)
        print("PASS: all jurisdiction mutations were caught")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
