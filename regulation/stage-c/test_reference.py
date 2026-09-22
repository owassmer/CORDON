"""Independent boundary and composition examples for the C reference.

Run with PYTHONPATH=regulation/stage-c .venv/bin/python -m unittest discover
-s regulation/stage-c -p test_reference.py. Synthetic observations exercise real
accepted provisions; they are not asserted to be actual official case records.
"""

import copy
import json
from pathlib import Path
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from fractions import Fraction
from itertools import product
from math import comb
import unittest
from zoneinfo import ZoneInfo

from hypothesis import given, settings, strategies as st
from pyproj import CRS
from shapely.geometry import Point, Polygon, MultiPolygon, box, LineString

from cordon_c import Evaluation, MissingInput, Snapshot, evaluate
from cordon_c.core import conjunction, disjunction
from cordon_c.bindings import assay_facts, leaves, merge_facts, wait_facts
from cordon_c.diagnostic import AssayResult
from cordon_c.quantities import metres, clock_boundary, PeriodRule, planned_workload_difference
from cordon_c.temporal import add_months, deadline, elapsed_hours, month_window, WorkingCalendar, no_detection_anchor, recurrence_coverage
from cordon_c.spatial import MetricGeometry, adopted_membership, band_membership, partial_parcel, population_coverage, distance_test, ground_distance, distance_envelope
from cordon_c.populations import post_finding_inner, containment_outer, pest_free_hectare, inward_band
from cordon_c.survey import binomial_confidence, binomial_sample_size, risk_prevalences, independent_system_confidence, equal_group_target, proportional_allocation, method_sensitivity
from cordon_c.survey import finite_confidence, finite_sample_size, finite_meets, BinomialStratum, binomial_design_adequacy, negative_survey_support

AT = date(2026, 9, 8)
ROME = ZoneInfo("Europe/Rome")
CRS_M = CRS.from_epsg(32633)


def shape(geometry, error=0):
    return MetricGeometry(geometry, CRS_M, error)


def simple_snapshot(ast, extra=()):
    row = dict(provision_version_id="test:v1", stable_provision_id="test", effective_from="2020-01-01",
               effective_to_exclusive="", semantic_change="YES", condition_ast=ast,
               true_effect="TRUE", false_effect="FALSE")
    return Snapshot([row, *extra], dict(clocks=[], parameters=[], dispositions=[]))


class LegalComposition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = Snapshot.load()

    def test_truth_tables_and_irrelevant_unknowns(self):
        for a, b in product([True, False, None], repeat=2):
            va, vb = Evaluation(a, needs=frozenset({"a"}) if a is None else frozenset()), Evaluation(b, needs=frozenset({"b"}) if b is None else frozenset())
            expected_and = False if False in [a, b] else None if None in [a, b] else True
            expected_or = True if True in [a, b] else None if None in [a, b] else False
            self.assertIs(conjunction([va, vb]).truth, expected_and)
            self.assertIs(disjunction([va, vb]).truth, expected_or)
        self.assertFalse(conjunction([Evaluation(False), Evaluation(None, needs=frozenset({"unused"}))]).needs)
        self.assertFalse(disjunction([Evaluation(True), Evaluation(None, needs=frozenset({"unused"}))]).needs)
        with self.assertRaises(TypeError):
            bool(Evaluation(None))

    def test_unknown_does_not_select_otherwise(self):
        s = simple_snapshot({"route_table": [{"when": {"predicate": "known"}, "effect": "YES"}], "otherwise": {"effect": "NO"}})
        self.assertIsNone(evaluate(s, "test", AT).effect)
        self.assertEqual(evaluate(s, "test", AT, {("test:v1", "known"): False}).effect, "NO")

    def test_route_order_has_no_priority(self):
        branches = [{"when": {"predicate": p}, "effect": p} for p in ("a", "b")]
        facts = {("test:v1", "a"): False, ("test:v1", "b"): True}
        for order in (branches, branches[::-1]):
            s = simple_snapshot({"route_table": order, "otherwise": {"effect": "NONE"}})
            self.assertEqual(evaluate(s, "test", AT, facts).effect, "b")
            with self.assertRaises(ValueError):
                evaluate(s, "test", AT, {k: True for k in facts})

    def test_compound_effect_is_not_prefix_matched(self):
        parent = simple_snapshot({"predicate": "no additional condition"}).versions["test:v1"]
        parent = parent | {"stable_provision_id": "parent", "provision_version_id": "parent:v1", "true_effect": "DONE; CONDITION"}
        s = simple_snapshot({"result_ref": {"producer_stable_provision_id": "parent", "allowed_effect": "DONE"}}, [parent])
        self.assertFalse(evaluate(s, "test", AT).truth)

    def test_national_notification_requires_completed_entry(self):
        s = self.snapshot
        identity = "IT-DLGS-19-2021:Art.29(2)"
        row = s.version(identity, AT)
        facts = {(row["provision_version_id"], p): True for p in leaves(row["condition_ast"])}
        result = evaluate(s, identity, AT, facts)
        self.assertIsNone(result.truth)
        self.assertIn("regional electronic entry completed", result.needs)
        edge = identity, "IT-DLGS-19-2021:Art.29(1)"
        self.assertTrue(evaluate(s, identity, AT, facts, performances={edge: True}).truth)
        self.assertFalse(evaluate(s, identity, AT, facts, performances={edge: False}).truth)

    def test_computed_facts_and_performances_compose_with_remaining_semantic_reader(self):
        s = simple_snapshot({"all_of": [{"predicate": "calculated"}, {"predicate": "official fact"}]})
        read = []
        def reader(row, text):
            read.append(text)
            return True
        result = evaluate(s, "test", AT, {("test:v1", "calculated"): False}, reader=reader)
        self.assertFalse(result.truth)
        self.assertEqual(read, ["official fact"])
        identity = "IT-DLGS-19-2021:Art.29(2)"
        edge = identity, "IT-DLGS-19-2021:Art.29(1)"
        complete = population_coverage({"official-entry": Evaluation(True)}, frozenset({"official-entry"}),
            required_population_complete=True, completion_records_complete=False)
        self.assertTrue(evaluate(self.snapshot, identity, AT, reader=reader, performances={edge: complete}).truth)
        incomplete = Evaluation(None, needs=frozenset({"entry receipt"}))
        unresolved = evaluate(self.snapshot, identity, AT, reader=reader, performances={edge: incomplete})
        self.assertIsNone(unresolved.truth)
        self.assertIn("entry receipt", unresolved.needs)

    def test_input_evaluations_cannot_replace_the_consuming_legal_effect(self):
        s = self.snapshot
        identity = "EU-2020-1201:2(2)"
        row = s.version(identity,AT)
        for truth in (True,None):
            supplied = Evaluation(truth,effect="UNRELATED_EFFECT",needs=frozenset({"source evidence"}),
                                  provisions=frozenset({"upstream-evidence"}))
            result = evaluate(s,identity,AT,{(row["provision_version_id"],"a survey is conducted"):supplied})
            self.assertEqual(result.effect,row["true_effect"] if truth else None)
            self.assertIn("upstream-evidence",result.provisions)
            consumer = "IT-DLGS-19-2021:Art.14(3):cross-region-use"
            edge = consumer,"IT-DLGS-19-2021:Art.14(3):cross-region-designation"
            result = evaluate(s,consumer,AT,performances={edge:supplied})
            self.assertEqual(result.effect,s.version(consumer,AT)["true_effect"] if truth else None)
            self.assertIn("source evidence",result.needs)

    def test_cost_consequences_require_their_own_lawful_basis_and_determination(self):
        s = self.snapshot
        edges = [
            ("IT-DLGS-19-2021:Art.32(3):determine-completion-costs","IT-DLGS-19-2021:Art.32(3):substitute-execution"),
            ("IT-DLGS-19-2021:Art.32(3):recovery-right","IT-DLGS-19-2021:Art.32(3):determine-completion-costs"),
            ("IT-DLGS-19-2021:Art.55(13):coercive-removal-costs","IT-DLGS-19-2021:Art.55(13):coercive-removal"),
        ]
        # The fixture establishes the proper obligor/offender, not performance
        # of substitute work or determination of any amount merely from omission.
        for edge in edges:
            absent = evaluate(s,edge[0],AT,reader=lambda row,text:True)
            self.assertIsNone(absent.truth)
            self.assertTrue(absent.needs)
            self.assertFalse(evaluate(s,edge[0],AT,reader=lambda row,text:True,performances={edge:False}).truth)
            proven = evaluate(s,edge[0],AT,reader=lambda row,text:True,performances={edge:True})
            self.assertTrue(proven.truth)
            self.assertEqual(proven.effect,s.version(edge[0],AT)["true_effect"])

    def test_early_lifting_preserves_a_pre_amendment_reduction_result(self):
        s = self.snapshot
        reduced_on, lifted_on = date(2022,12,15),date(2023,3,1)
        reduced = evaluate(s,"EU-2020-1201:5(1)",reduced_on,reader=lambda row,text:True)
        self.assertEqual(reduced.effect,"BUFFER_ZONE_REDUCED")
        self.assertIn("EU-2020-1201:5(1)(c):v1",reduced.provisions)
        def lifting_facts(row,text):
            # This would defeat the later reduction requirement. It cannot
            # retroactively change the completed earlier reduction.
            return not (row["provision_version_id"] == "EU-2020-1201:5(1)(c):v2" and "90 %" in text)
        edge = "EU-2020-1201:6(2)","EU-2020-1201:5(1)"
        result = evaluate(s,edge[0],lifted_on,reader=lifting_facts,historical_results={edge:(reduced_on,reduced)})
        self.assertEqual(result.effect,"DEMARCATED_AREA_LIFTED")
        self.assertNotIn("EU-2020-1201:5(1)(c):v2",result.provisions)
        self.assertIsNone(evaluate(s,edge[0],lifted_on,reader=lifting_facts).effect)
        later = evaluate(s,edge[1],lifted_on,reader=lifting_facts)
        self.assertEqual(later.effect,"BUFFER_ZONE_NOT_REDUCED")
        self.assertEqual(evaluate(s,edge[0],lifted_on,reader=lifting_facts,
            historical_results={edge:(lifted_on,later)}).effect,"AREA_REMAINS_DEMARCATED")
        with self.assertRaises(ValueError):
            evaluate(s,edge[0],lifted_on,reader=lifting_facts,
                historical_results={edge:(date(2023,3,2),later)})
        with self.assertRaises(ValueError):
            evaluate(s,edge[0],lifted_on,reader=lifting_facts,
                historical_results={edge:(reduced_on,Evaluation(True,effect="BUFFER_ZONE_REDUCED"))})

    def test_version_seam_and_parameter_continuity(self):
        s = self.snapshot
        rows = s.stable["EU-2020-1201:15(2)(a)"]
        seam = date.fromisoformat(rows[1]["effective_from"])
        self.assertEqual(s.version("EU-2020-1201:15(2)(a)", seam)["provision_version_id"], rows[1]["provision_version_id"])
        self.assertEqual(metres(s, "B-PAR-EU-15(2)(a)-v1-inward-band-5km", seam - timedelta(days=1)), 5000)
        with self.assertRaises(MissingInput):
            metres(s, "B-PAR-EU-15(2)(a)-v1-inward-band-5km", seam)
        self.assertEqual(metres(s, "B-PAR-EU-15(2)(a)-v2-inward-band-2km", seam), 2000)

    def test_removal_population_and_retention_are_separate(self):
        s = self.snapshot
        # A symptomatic plant falls in point (b), whether or not retention is
        # exercised downstream. This population computation cannot remove it.
        r = s.version("EU-2020-1201:7(1)(b)", AT)
        f = {(r["provision_version_id"], "plants showing symptoms indicating possible infection, or suspected of infection"): True}
        self.assertTrue(evaluate(s, r["stable_provision_id"], AT, f).truth)
        self.assertIsNone(evaluate(s, "EU-2020-1201:7(1)", AT, f).truth)

    def test_full_removal_and_retention_conclusions(self):
        s = self.snapshot
        def fact(identity, text, value):
            return {(s.version(identity, AT)["provision_version_id"], text): value}
        f = merge_facts(
            fact("EU-2020-1201:12", "the infected zone is listed in Annex III", False),
            fact("EU-2020-1201:7(1)", "an infected zone established for the purpose of eradication exists", True),
            fact("EU-2020-1201:7(1)(a)", "plants known to be infected", False),
            fact("EU-2020-1201:7(1)(b)", "plants showing symptoms indicating possible infection, or suspected of infection", True),
            fact("EU-2020-1201:7(1)(e)", "specified plants other than points (c) and (d)", False),
            fact("EU-2020-1201:7(3)", "individual specified plant", True),
            fact("EU-2020-1201:7(3)", "plant officially designated as a plant with historic value", True),
            fact("EU-2020-1201:7(3)(a)", "annual inspection, sampling and testing by an Annex IV test confirming the plant is not infected", True),
            fact("EU-2020-1201:7(3)(b)", "appropriate phytosanitary treatment against the vector population in all stages, on the plants or the area", True),
            fact("EU-2020-1201:7(3)", "the Member State decides that the individual plant need not be removed", True))
        self.assertEqual(evaluate(s, "EU-2020-1201:7(3)", AT, f).effect, "RETENTION_DEROGATION_EXERCISED")
        self.assertEqual(evaluate(s, "EU-2020-1201:7(1)", AT, f).effect, "NO_ARTICLE_7_1_REMOVAL_DUTY")
        f.update(fact("EU-2020-1201:7(3)", "the Member State decides that the individual plant need not be removed", False))
        self.assertEqual(evaluate(s, "EU-2020-1201:7(1)", AT, f).effect, "IMMEDIATE_REMOVAL_REQUIRED")

    def test_containment_sampling_survives_scientific_retention(self):
        s = self.snapshot
        facts = {}
        for identity, text in [("EU-2020-1201:12", "the infected zone is listed in Annex III"),
                               ("EU-2020-1201:12", "the competent authority decides to apply the containment measures of Articles 13 to 17 instead of eradication"),
                               ("EU-2020-1201:15(1)", "an infected zone listed in Annex III under containment measures exists"),
                               ("EU-2020-1201:15(1)", "plants found infected")]:
            facts[(s.version(identity, AT)["provision_version_id"], text)] = True
        # Sampling is independently decidable without a removal/retention input.
        self.assertEqual(evaluate(s, "EU-2020-1201:15(1)", AT, facts).effect, "IMMEDIATE_50M_SAMPLING_AND_TESTING_REQUIRED")

    def test_doubtful_route_uses_doubtful_class_not_any_matched_route(self):
        s = self.snapshot
        identity = "REG-PUGLIA-U181-DIR-2025-00045:doubtful-result-route"
        row = s.version(identity, AT)
        facts = {(row["provision_version_id"], text): text in {"initial analytical class = doubtful", "repeat extraction and Harper test not yet completed"}
                 for text in leaves(row["condition_ast"])}
        classification = "REG-PUGLIA-U181-DIR-2025-00045:cq-analytical-result-classification"
        for cq, expected in [("33", "REPEAT_EXTRACTION_AND_HARPER_TEST_REQUIRED"), ("30", "DOUBTFUL_WORKFLOW_STAGE_OR_ANALYTICAL_EVIDENCE_REQUIRED")]:
            computed = assay_facts(s, classification, AT, AssayResult(True, True, Decimal(cq), False))
            self.assertEqual(evaluate(s, identity, AT, merge_facts(facts, computed)).effect, expected)

    def test_all_shapes_load_without_claiming_evidence(self):
        for r in self.snapshot.versions.values():
            at = date.fromisoformat(r["effective_from"] or "2026-09-08")
            value = evaluate(self.snapshot, r["provision_version_id"], at)
            self.assertIsInstance(value, Evaluation)

    def test_conflicting_facts_are_not_overwritten(self):
        with self.assertRaises(ValueError):
            merge_facts({("a", "b"): True}, {("a", "b"): False})

    def test_contextual_reference_bindings_resolve_to_actual_edges_and_effects(self):
        bindings = json.loads((Path(__file__).parent / "reference-bindings.json").read_text())
        keys = [(r["consumer"], r["reference"]) for r in bindings]
        self.assertEqual(len(keys), len(set(keys)))
        def references(ast):
            if isinstance(ast, dict):
                if "provision_ref" in ast:
                    yield ast["provision_ref"]
                if "result_ref" in ast:
                    yield ast["result_ref"]["producer_stable_provision_id"]
                for value in ast.values():
                    yield from references(value)
            elif isinstance(ast, list):
                for value in ast:
                    yield from references(value)
        for binding in bindings:
            consumers = self.snapshot.stable[binding["consumer"]]
            self.assertTrue(any(binding["reference"] in references(r["condition_ast"]) for r in consumers))
            if "outcomes" not in binding:
                continue
            for consumer in consumers:
                if binding["reference"] not in references(consumer["condition_ast"]):
                    continue
                for producer in self.snapshot.stable[binding["reference"]]:
                    if max(consumer["effective_from"], producer["effective_from"]) >= min(consumer["effective_to_exclusive"] or "9999", producer["effective_to_exclusive"] or "9999"):
                        continue
                    ast = producer["condition_ast"]
                    effects = {b["effect"] for b in ast["route_table"]} | {ast["otherwise"]["effect"]}
                    self.assertLessEqual(effects, binding["outcomes"].keys())


class DiagnosticBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = Snapshot.load()

    def classification(self, source, at, value=None, explicit_no_cq=False, valid=True, selected=True):
        identity = f"REG-PUGLIA-U181-DIR-{source}:cq-analytical-result-classification"
        facts = assay_facts(self.snapshot, identity, at, AssayResult(valid, selected, Decimal(value) if value is not None else None, explicit_no_cq))
        return evaluate(self.snapshot, identity, at, facts).effect

    def test_exact_boundaries_and_no_cq(self):
        expected = {"31.999": "POSITIVE_ANALYTICAL_RESULT", "32": "AUTHORITY_INTERPRETATION_REQUIRED_FOR_BOUNDARY_VALUE",
                    "32.001": "DOUBTFUL_ANALYTICAL_RESULT", "34.999": "DOUBTFUL_ANALYTICAL_RESULT",
                    "35": "AUTHORITY_INTERPRETATION_REQUIRED_FOR_BOUNDARY_VALUE", "35.001": "NEGATIVE_ANALYTICAL_RESULT"}
        for value, effect in expected.items():
            self.assertEqual(self.classification("2025-00045", AT, value), effect)
        self.assertEqual(self.classification("2025-00045", AT, explicit_no_cq=True), "NEGATIVE_ANALYTICAL_RESULT")
        with self.assertRaises(MissingInput):
            self.classification("2025-00045", AT)
        self.assertEqual(self.classification("2025-00045", AT, valid=False), "ANALYTICAL_EVIDENCE_REQUIRED")
        self.assertEqual(self.classification("2025-00045", AT, "30", selected=False), "ANALYTICAL_CLASSIFICATION_UNRESOLVED")

    def test_predecessor_does_not_borrow_later_threshold(self):
        self.assertEqual(self.classification("2022-00031", date(2024, 1, 1), "36"), "DOUBTFUL_ANALYTICAL_RESULT")

    def test_confirmation_uses_distinct_tests_same_origin_and_target_identity(self):
        from cordon_c.bindings import confirmation_facts
        args = dict(first_positive_annex_iv=Evaluation(True), second_positive_annex_iv=Evaluation(True),
            first_test="test-1", second_test="test-2", first_sample="sample-A", second_sample="sample-A",
            first_extract="extract-A", second_extract="extract-B", same_extract_route_appropriate=Evaluation(False),
            first_genome_target="target-A", second_genome_target="target-B", inside_demarcated_area=Evaluation(False))
        def result(**changes):
            return evaluate(self.snapshot, "EU-2020-1201:2(6)", AT,
                confirmation_facts(self.snapshot, AT, **(args | changes))).effect
        self.assertEqual(result(), "PRESENCE_CONFIRMED")
        self.assertEqual(result(second_sample="different-plant-sample"), "SECOND_CONFIRMATORY_TEST_REQUIRED")
        self.assertEqual(result(second_test="test-1"), "SECOND_CONFIRMATORY_TEST_REQUIRED")
        self.assertEqual(result(second_genome_target="target-A"), "SECOND_CONFIRMATORY_TEST_REQUIRED")
        self.assertIsNone(result(second_genome_target=None))
        self.assertEqual(result(inside_demarcated_area=Evaluation(True), second_genome_target=None), "PRESENCE_CONFIRMED")


class CalendarBoundaries(unittest.TestCase):
    def test_continuous_duration_combines_records_without_erasing_a_gap(self):
        from cordon_c.quantities import continuous_duration_support
        s = Snapshot.load()
        args = dict(anchor=date(2026,8,1), required_start=datetime(2026,8,2,tzinfo=ROME),
            evaluated_at=datetime(2026,8,9,tzinfo=ROME), records_complete=True,
            zone=ROME, rule=PeriodRule(False))
        clock = "B-CLK-DGR1075-albo-publication"
        # Explicit counting fixture, not adjudication of the publication rule.
        spans = {"first": (datetime(2026,8,1,12,tzinfo=ROME),datetime(2026,8,5,tzinfo=ROME)),
                 "continuation": (datetime(2026,8,5,tzinfo=ROME),None)}
        self.assertTrue(continuous_duration_support(s,clock,AT,intervals=spans,**args).truth)
        spans["continuation"] = datetime(2026,8,5,0,1,tzinfo=ROME),None
        self.assertFalse(continuous_duration_support(s,clock,AT,intervals=spans,**args).truth)
        self.assertIsNone(continuous_duration_support(s,clock,AT,intervals=spans,
            **(args | {"records_complete":False})).truth)
        ongoing = {"posting": (datetime(2026,8,1,12,tzinfo=ROME),None)}
        self.assertIsNone(continuous_duration_support(s,clock,AT,intervals=ongoing,
            **(args | {"evaluated_at":datetime(2026,8,4,tzinfo=ROME)})).truth)

    def test_custody_same_day_is_composed_with_transport_and_proven_failure(self):
        from cordon_c.bindings import custody_facts
        s = Snapshot.load()
        identity = "REG-PUGLIA-U181-DIR-2025-00045:sample-custody-transfer"
        row = s.version(identity,AT)
        args = dict(collected_at=datetime(2026,9,1,23,45,tzinfo=ROME),
            evaluated_at=datetime(2026,9,2,1,tzinfo=ROME), delivery_records_complete=True,
            refrigerated_transport=Evaluation(True),other_mandatory_failure=Evaluation(False),zone=ROME)
        other = { (row["provision_version_id"], p): p != "a proven personnel-authority defect legally defeats this official custody proof"
                  for p in leaves(row["condition_ast"])
                  if p not in {"same-day delivery and refrigerated transport", "evidence proves a mandatory source custody condition failed"}}
        for delivered, expected in [(datetime(2026,9,1,23,55,tzinfo=ROME),"SOURCE_SAMPLE_CUSTODY_TRANSFER_COMPLETE"),
                                    (datetime(2026,9,2,0,5,tzinfo=ROME),"SOURCE_SAMPLE_CUSTODY_NONCOMPLIANT")]:
            computed = custody_facts(s,identity,AT,delivered_at=delivered,**args)
            self.assertEqual(evaluate(s,identity,AT,merge_facts(other,computed)).effect,expected)
        computed = custody_facts(s,identity,AT,delivered_at=None,**(args | {"delivery_records_complete":False}))
        self.assertIsNone(evaluate(s,identity,AT,merge_facts(other,computed)).effect)

    def test_completion_compares_hour_instants_and_whole_days_differently(self):
        from cordon_c.quantities import timely_completion
        s = Snapshot.load()
        start = datetime(2026,9,1,10,30,tzinfo=ROME)
        args = dict(anchor=start,evaluated_at=datetime(2026,9,10,tzinfo=ROME),
                    completion_history_complete=True,zone=ROME)
        hours = "B-CLK-DM169819-14(3)-research-lab-24h"
        self.assertTrue(timely_completion(s,hours,AT,completed_at=datetime(2026,9,2,10,30,tzinfo=ROME),**args).truth)
        self.assertFalse(timely_completion(s,hours,AT,completed_at=datetime(2026,9,2,10,30,1,tzinfo=ROME),**args).truth)
        days = "B-CLK-DGR1075-owner-election"
        self.assertTrue(timely_completion(s,days,AT,completed_at=datetime(2026,9,4,23,59,tzinfo=ROME),rule=PeriodRule(False),**args).truth)
        self.assertFalse(timely_completion(s,days,AT,completed_at=datetime(2026,9,5,tzinfo=ROME),rule=PeriodRule(False),**args).truth)
        self.assertFalse(timely_completion(s,days,AT,completed_at=None,rule=PeriodRule(False),**args).truth)
        args['completion_history_complete'] = False
        self.assertIsNone(timely_completion(s,days,AT,completed_at=None,rule=PeriodRule(False),**args).truth)
        args['evaluated_at'] = start
        args['completion_history_complete'] = True
        self.assertIsNone(timely_completion(s,days,AT,completed_at=None,rule=PeriodRule(False),**args).truth)

    def calendar(self):
        return WorkingCalendar(date(2025, 1, 1), date(2027, 1, 1), frozenset({date(2026, 4, 6)}), frozenset({5, 6}))

    def test_month_end_and_leap_anniversary(self):
        self.assertEqual(add_months(date(2024, 2, 29), 12), date(2025, 2, 28))
        self.assertEqual(add_months(date(2026, 1, 31), 1), date(2026, 2, 28))
        self.assertEqual(add_months(date(2026, 3, 31), -1), date(2026, 2, 28))

    def test_working_days_exclude_anchor_and_holidays(self):
        self.assertEqual(deadline(date(2026, 4, 3), 3, "working_days", calendar=self.calendar(), roll_forward=False), date(2026, 4, 9))
        with self.assertRaises(MissingInput):
            deadline(date(2027, 1, 1), 1, "working_days", calendar=self.calendar(), roll_forward=False)

    def test_weekend_extension_and_two_working_days(self):
        self.assertEqual(deadline(date(2026, 4, 3), 2, "calendar_days", calendar=self.calendar(), roll_forward=True, minimum_working_days=2), date(2026, 4, 8))
        self.assertEqual(deadline(date(2026, 4, 3), 2, "calendar_days", calendar=None, roll_forward=False), date(2026, 4, 5))

    def test_elapsed_hours_across_dst(self):
        start = datetime(2026, 3, 28, 12, tzinfo=ROME)
        end = elapsed_hours(start, 48)
        self.assertEqual(end, datetime(2026, 3, 30, 13, tzinfo=ROME))
        self.assertEqual((end.astimezone(timezone.utc) - start.astimezone(timezone.utc)).total_seconds(), 48 * 3600)
        with self.assertRaises(ValueError):
            elapsed_hours(datetime(2026, 3, 29, 2, 30, tzinfo=ROME), 48)

    def test_same_day_is_not_24_hours(self):
        s = Snapshot.load()
        start = datetime(2026, 9, 8, 23, 50, tzinfo=ROME)
        end = clock_boundary(s, "B-CLK-DDS45-custody-same-day", AT, start, zone=ROME)
        self.assertEqual(end, datetime(2026, 9, 9, 0, 0, tzinfo=ROME))

    def test_wait_facts_change_at_exact_48_hours(self):
        s = Snapshot.load()
        identity = "REG-PUGLIA-U181-DIR-2025-00045:treatment-removal-sequence"
        start = datetime(2026, 9, 6, 10, tzinfo=ROME)
        row = s.version(identity, AT)
        key = row["provision_version_id"], "regional 48-hour wait completed"
        self.assertFalse(wait_facts(s, identity, AT, treatment_completed=start, evaluated_at=start + timedelta(hours=48, microseconds=-1))[key])
        self.assertTrue(wait_facts(s, identity, AT, treatment_completed=start, evaluated_at=start + timedelta(hours=48))[key])

    def test_reset_does_not_erase_survey_requirement(self):
        established = date(2021, 1, 1)
        self.assertEqual(no_detection_anchor(established, (date(2024, 1, 1),), AT, detection_record_complete=True), date(2024, 1, 1))
        with self.assertRaises(MissingInput):
            no_detection_anchor(established, (), AT, detection_record_complete=False)
        periods = ((date(2024, 1, 1), date(2025, 1, 1)), (date(2025, 1, 1), date(2026, 1, 1)))
        self.assertFalse(recurrence_coverage(periods, {"survey-1": date(2024, 6, 1)}, records_complete=True))

    def test_wrapping_month_window(self):
        included = [m for m in range(1, 13) if month_window(date(2026, m, 1), 11, 3)]
        self.assertEqual(included, [1, 2, 3, 11, 12])


class SpatialPopulations(unittest.TestCase):
    def test_hectare_outside_sliver_must_survive_declared_spatial_error(self):
        s = Snapshot.load()
        zone = shape(box(0,0,200,200))
        reported = shape(box(100.1,50,200.1,150),1)
        value = pest_free_hectare(s,AT,reported,zone,contains_specified_species=Evaluation(True))
        self.assertIsNone(value.truth)
        self.assertTrue(value.needs)
        for hectare, expected in [(shape(box(99.1,50,199.1,150)),False),
                                  (shape(box(100.1,50,200.1,150)),True),
                                  (shape(box(102,50,202,150),1),True)]:
            self.assertIs(pest_free_hectare(s,AT,hectare,zone,contains_specified_species=Evaluation(True)).truth,expected)

    def test_hectare_requires_the_same_surviving_surface_within_the_band(self):
        s = Snapshot.load()
        hectare = shape(MultiPolygon([box(-10,0,.5,10), box(500,0,600,98.95)]))
        self.assertEqual(hectare.geometry.area,10000)
        nominal = box(-100,-100,0,100)
        possible = box(-100,-100,1,100)
        self.assertEqual(nominal.boundary.hausdorff_distance(possible.boundary),1)
        for zone, expected in [(shape(nominal),True), (shape(nominal,1),None),
                               (shape(possible),False)]:
            self.assertIs(pest_free_hectare(s,AT,hectare,zone,
                contains_specified_species=Evaluation(True)).truth,expected)
        # A nominally inside component can also become outside; the remote
        # component cannot establish exclusion of that possible band surface.
        inside = shape(MultiPolygon([box(-10,0,-.5,10),box(500,0,600,99.05)]))
        self.assertIsNone(pest_free_hectare(s,AT,inside,shape(nominal,1),
            contains_specified_species=Evaluation(True)).truth)
        self.assertTrue(pest_free_hectare(s,AT,inside,shape(box(-100,-100,-1,100)),
            contains_specified_species=Evaluation(True)).truth)
        # Certain exclusion remains useful away from either boundary.
        deep_inside = shape(MultiPolygon([box(-20,0,-10,10),box(500,0,600,99)]))
        self.assertFalse(pest_free_hectare(s,AT,deep_inside,shape(nominal,1),
            contains_specified_species=Evaluation(True)).truth)

    def test_surface_band_does_not_bridge_disconnected_components(self):
        from cordon_c.spatial import surface_in_band
        origin = shape(Point(0,0))
        disconnected = shape(MultiPolygon([box(-1,-1,1,1),box(500,0,501,1)]))
        self.assertFalse(surface_in_band(disconnected,origin,50,400).truth)
        crossing = shape(box(49,-1,51,1))
        self.assertTrue(surface_in_band(crossing,origin,50,400).truth)
        self.assertFalse(surface_in_band(shape(box(450,0,451,1)),origin,50,400).truth)
        self.assertIsNone(surface_in_band(shape(box(450,0,451,1),.1),origin,50,400).truth)
        self.assertTrue(containment_outer(Snapshot.load(),AT,crossing,(origin,),
            surface_qualification=Evaluation(True)).truth)

    def test_projection_error_and_pni_band_preserve_the_same_population(self):
        from cordon_c.spatial import projection_distance_error
        from cordon_c.bindings import pni_geography_facts
        self.assertAlmostEqual(projection_distance_error(5000, (.9996, 1.0002)), 2.000800320128, places=10)
        s = Snapshot.load()
        identity = "IT-PNI-2026:Xylella:Puglia-plant-survey-design"
        vid = s.version(identity, AT)["provision_version_id"]
        qualifications = {"Olea europaea in orchards or vineyards": Evaluation(True),
                          "Prunus sp. or Citrus sp.": Evaluation(False), "Vitis sp.": Evaluation(False),
                          "the workbook-listed spontaneous-host vegetation": Evaluation(False)}
        area = shape(box(-50, -50, 50, 50))
        for x, high, medium in [(1050, True, False), (1051, False, True), (0, False, False)]:
            facts = pni_geography_facts(s, AT, shape(Point(x, 0)), area,
                         target_is_in_puglia_pest_free_area=Evaluation(x > 50), host_qualifications=qualifications)
            self.assertIs(facts[vid, "target population is Olea europaea in orchards or vineyards within the 1 km pest-free band around demarcated areas"].truth, high)
            self.assertIs(facts[vid, "target population is Olea europaea in orchards or vineyards in remaining Puglia pest-free areas"].truth, medium)

    def test_island_separation_uses_whole_geometry_and_complete_other_land(self):
        from cordon_c.bindings import island_distance_facts
        s = Snapshot.load()
        island = shape(box(0, 0, 100, 100))
        for coast_x, complete, expected in [(5100, True, False), (5101, True, True), (5101, None, None), (5000, None, False)]:
            result = island_distance_facts(s, AT, island, shape(box(coast_x, 0, coast_x + 1000, 1000)),
                         other_union_land_complete=Evaluation(complete, needs=frozenset({"other land"}) if complete is None else frozenset()))
            self.assertIs(next(iter(result.values())).truth, expected)

    def test_minimum_enclosure_checks_width_and_holes_without_creating_legal_area(self):
        from cordon_c.spatial import minimum_enclosure
        origin = shape(Point(0, 0))
        self.assertTrue(minimum_enclosure(origin, shape(box(-60, -60, 60, 60)), 50).truth)
        self.assertFalse(minimum_enclosure(origin, shape(box(-60, -60, 49, 60)), 50).truth)
        holed = box(-100, -100, 100, 100).difference(box(20, 20, 30, 30))
        self.assertFalse(minimum_enclosure(origin, shape(holed), 50).truth)
        self.assertIsNone(minimum_enclosure(origin, shape(box(-50, -50, 50, 50), 1), 50).truth)

    def test_candidate_envelope_does_not_shrink_radius(self):
        from math import cos, sin, pi
        origin = shape(Point(0, 0))
        envelope = distance_envelope(origin, 50, .01)
        self.assertLessEqual(envelope.error_m, .01)
        for i in range(361):
            p = Point(50 * cos(i * pi / 180), 50 * sin(i * pi / 180))
            self.assertTrue(envelope.geometry.covers(p))
    def test_band_outer_is_450_not_400(self):
        s = Snapshot.load()
        plant = shape(Point(500000, 4500000))
        for offset, expected in [(49.9, False), (50, True), (400, True), (449.9, True), (450, True), (450.1, False)]:
            p = shape(Point(500000 + offset, 4500000))
            self.assertIs(containment_outer(s, AT, p, (plant,), surface_qualification=Evaluation(True)).truth, expected)

    def test_metric_units_precision_and_adopted_membership(self):
        with self.assertRaises(ValueError):
            MetricGeometry(Point(16, 41), CRS.from_epsg(4326), 0)
        p = shape(Point(0, 0), .2)
        q = shape(Point(50, 0))
        self.assertIsNone(distance_test(p, q, 50, "<=").truth)
        self.assertTrue(adopted_membership(shape(Point(0, 5)), shape(box(0, 0, 10, 10))).truth)
        self.assertFalse(adopted_membership(shape(Point(-1, 5)), shape(box(0, 0, 10, 10))).truth)
        self.assertAlmostEqual(ground_distance((0, 0), (1, 0)), 111319.49079327357, places=6)

    def test_different_population_same_radius(self):
        s = Snapshot.load()
        plant, neighbour = shape(Point(0, 0)), shape(Point(40, 0))
        self.assertTrue(post_finding_inner(s, AT, neighbour, (plant,), containment=True, population_qualification=Evaluation(True)).truth)
        self.assertFalse(post_finding_inner(s, AT, neighbour, (plant,), containment=False, population_qualification=Evaluation(False)).truth)

    def test_hectare_band_uses_zone_not_finding(self):
        s = Snapshot.load()
        zone = shape(box(0, 0, 200, 200))
        hectare = shape(box(550, 0, 650, 100))
        self.assertTrue(pest_free_hectare(s, AT, hectare, zone, contains_specified_species=Evaluation(True)).truth)
        self.assertFalse(pest_free_hectare(s, AT, hectare, zone, contains_specified_species=Evaluation(False)).truth)

    def test_only_boundary_shared_with_buffer_defines_inward_band(self):
        zone = shape(box(0, 0, 10000, 10000))
        interface = shape(LineString([(10000, 0), (10000, 10000)]))
        self.assertFalse(inward_band(shape(Point(10, 5000)), zone, interface, 2000).truth)
        self.assertTrue(inward_band(shape(Point(8000, 5000)), zone, interface, 2000).truth)

    def test_partial_parcel_does_not_expand_plant_membership(self):
        area, parcel = shape(box(0, 0, 10, 10)), shape(box(9, 9, 20, 20))
        self.assertTrue(partial_parcel(parcel, area).truth)
        self.assertFalse(adopted_membership(shape(Point(19, 19)), area).truth)
        self.assertFalse(partial_parcel(shape(box(10, 0, 20, 10)), area).truth)

    def test_shared_performance_and_incomplete_population(self):
        req = {"plant-1": Evaluation(True), "plant-2": Evaluation(None, needs=frozenset({"species"}))}
        self.assertTrue(population_coverage(req, frozenset(req), required_population_complete=True, completion_records_complete=False).truth)
        self.assertIsNone(population_coverage(req, frozenset(req), required_population_complete=False, completion_records_complete=True).truth)
        self.assertFalse(population_coverage(req, frozenset(), required_population_complete=False, completion_records_complete=True).truth)

    def test_computed_support_covers_each_required_area_without_majority_substitution(self):
        from cordon_c.spatial import population_support
        required = {"infected-zone":Evaluation(True),"buffer":Evaluation(True),"optional-area":Evaluation(False)}
        support = {"infected-zone":Evaluation(True),"buffer":Evaluation(None,needs=frozenset({"buffer observations"}))}
        result = population_support(required,support,required_population_complete=True)
        self.assertIsNone(result.truth)
        self.assertEqual(result.needs,frozenset({"buffer observations"}))
        support['buffer'] = Evaluation(True)
        self.assertTrue(population_support(required,support,required_population_complete=True).truth)
        support['buffer'] = Evaluation(False)
        self.assertFalse(population_support(required,support,required_population_complete=False).truth)

    @given(st.floats(min_value=0, max_value=10000, allow_nan=False), st.floats(min_value=0, max_value=10000, allow_nan=False))
    def test_radius_membership_monotone(self, distance, radius):
        a, b = shape(Point(0, 0)), shape(Point(distance, 0))
        small = distance_test(a, b, radius, "<=").truth
        larger = distance_test(a, b, radius + 1, "<=").truth
        self.assertFalse(small and not larger)


class SurveyMathematics(unittest.TestCase):
    def test_observed_survey_counts_units_and_requires_a_coherent_stratum_partition(self):
        from cordon_c.survey import observed_binomial_support
        s = Snapshot.load()
        args = dict(proportions=(1.,), relative_risks=(1.,), method_sensitivities=(.546,),
                    positive_units=frozenset(), observation_inventory_complete=True, population_and_method_qualification=Evaluation(True),
                    required_risk_structure=Evaluation(True), required_performances_complete=Evaluation(True),
                    official_method_and_scope=Evaluation(True), independence_established=True)
        parameter = "B-PAR-PNI2026-authorized-sites-design"
        for n, expected in [(293, False), (294, True)]:
            result = observed_binomial_support(s, parameter, AT,
                        negative_units=(frozenset(f"unit-{i}" for i in range(n)),), **args)
            self.assertIs(result.truth, expected)
        args['observation_inventory_complete'] = False
        self.assertIsNone(observed_binomial_support(s, parameter, AT, negative_units=(frozenset(),), **args).truth)
        args['observation_inventory_complete'] = True
        args.update(proportions=(.5,.5),relative_risks=(1.,2.),method_sensitivities=(.546,.546))
        with self.assertRaises(ValueError):
            observed_binomial_support(s, parameter, AT,
                        negative_units=(frozenset({"same-unit"}),frozenset({"same-unit"})), **args)
        args.update(positive_units=frozenset({"positive-unit"}),independence_established=False,
                    population_and_method_qualification=Evaluation(None))
        self.assertFalse(observed_binomial_support(s, parameter, AT, negative_units=(), **args).truth)

    def test_two_stage_unequal_inner_designs_do_not_pool_plant_counts(self):
        from cordon_c.survey import two_stage_independent_confidence
        inner = tuple(1 - Fraction(99,100) ** n for n in (20,30))
        expected = 1 - (1 - Fraction(1,50)*inner[0])*(1-Fraction(1,50)*inner[1])
        result = two_stage_independent_confidence(tuple(float(x) for x in inner), .02,
                                                  independence_established=True)
        self.assertAlmostEqual(result,float(expected),places=15)
        self.assertNotAlmostEqual(result,binomial_confidence(50,.02,.5))

    def test_binomial_equality_and_two_stage_independent_recomputation(self):
        from cordon_c.survey import binomial_meets, stratified_binomial_meets, two_stage_binomial_confidence
        for digit in range(1, 10):
            value = digit / 10
            self.assertTrue(binomial_meets(1, 1, value, value))
            self.assertEqual(binomial_sample_size(value, 1, value), 1)
            self.assertTrue(stratified_binomial_meets(1, (BinomialStratum(1, 1, value, 1),), value,
                                                    independence_established=True))
        within = 1 - Fraction(99, 100) ** 20
        independent = 1 - (1 - Fraction(1, 50) * within) ** 100
        computed = two_stage_binomial_confidence(units_inspected=100, unit_prevalence=.02,
                    plants_per_unit=20, within_unit_prevalence=.02, plant_method_sensitivity=.5,
                    homogeneous_unit_design_established=True)
        self.assertAlmostEqual(computed, float(independent), places=14)
        self.assertNotAlmostEqual(computed, binomial_confidence(2000, .02, .5))

    def test_finite_model_against_exact_combinatorics(self):
        for N, d, n in [(10, 5, 7), (20, 1, 19), (100, 2, 86), (10, 10, 8), (20, 3, 20)]:
            sensitivity = Fraction(3, 5)
            exact = 1 - sum(Fraction(comb(d, k) * comb(N-d, n-k), comb(N, n)) * (1-sensitivity)**k
                            for k in range(max(0, n-(N-d)), min(d, n)+1))
            self.assertAlmostEqual(finite_confidence(N, d, n, float(sensitivity)), float(exact), places=12)
        self.assertEqual(finite_sample_size(20, 1, 1, .95), 19)
        self.assertTrue(finite_meets(20, 1, 19, 1, .95))
        for sensitivity in [.1, .2, .3, .4, .5, .6, .7, .8, .9]:
            self.assertEqual(finite_sample_size(100, 1, sensitivity, sensitivity), 100)

    def test_published_approximation_can_undershoot(self):
        self.assertAlmostEqual(finite_confidence(100, 2, 86, .9), .9499090909090909)
        self.assertEqual(finite_sample_size(100, 2, .9, .95), 87)
        self.assertEqual(finite_sample_size(1000, 10, .6, .95), 431)
        with self.assertRaises(ValueError):
            finite_sample_size(10, 1, .6, .95)

    def test_large_population_single_infected_unit(self):
        # One infected unit is selected with probability n/N; detection then
        # succeeds with sensitivity s. This does not use the PMF implementation.
        population = 100_000_000
        for n in (1, population // 2, population - 1, population):
            exact = Fraction(n, population) * Fraction(9, 10)
            self.assertAlmostEqual(finite_confidence(population, 1, n, .9), float(exact), places=14)
        self.assertEqual(finite_sample_size(population, 1, .9, .45), population // 2)

    def test_survey_adequacy_qualifications_and_positive_finding(self):
        s = Snapshot.load()
        parameter = "B-PAR-EU-10-sub2-C90-p1"
        strata = (BinomialStratum(.1, 2, .8, 100), BinomialStratum(.9, 1, .8, 300))
        adequate = binomial_design_adequacy(s, parameter, AT, strata,
                                           population_and_method_qualification=Evaluation(True),
                                           required_risk_structure=Evaluation(True), independence_established=True)
        self.assertTrue(adequate.truth)
        self.assertFalse(negative_survey_support(adequate, confirmed_positive_units=1,
                                                required_performances_complete=Evaluation(True),
                                                official_method_and_scope=Evaluation(True)).truth)

    def test_published_binomial_examples(self):
        self.assertEqual(binomial_sample_size(.95, .01, .6), 498)
        self.assertEqual(binomial_sample_size(.95, .01, .55), 544)
        self.assertEqual(binomial_sample_size(.8, .01, .55), 292)

    def test_independent_rational_recomputation(self):
        # Exact enumeration of the complement at a rational per-unit probability.
        for n in [1, 10, 50]:
            exact = 1 - Fraction(99, 100) ** n
            self.assertAlmostEqual(binomial_confidence(n, .02, .5), float(exact), places=14)

    def test_risk_weighting_preserves_overall_prevalence(self):
        proportions = (.016, .984)
        values = risk_prevalences(.004, proportions, (2, 1))
        self.assertAlmostEqual(sum(p * v for p, v in zip(proportions, values)), .004)
        self.assertAlmostEqual(values[0] / values[1], 2)
        with self.assertRaises(ValueError):
            risk_prevalences(.9, (.01, .99), (100, 1))

    def test_group_confidence_and_stage_sensitivity_are_not_products_of_sample_counts(self):
        target = equal_group_target(.95, 4)
        self.assertAlmostEqual(independent_system_confidence((target,) * 4, independence_established=True), .95)
        self.assertAlmostEqual(method_sensitivity(.7, .78), .546)
        with self.assertRaises(MissingInput):
            independent_system_confidence((.8, .8), independence_established=False)

    def test_workload_counts_do_not_prove_adequacy(self):
        s = Snapshot.load()
        self.assertEqual(planned_workload_difference(s, "B-PAR-PNI2026-olea-medium-workload", AT, 5537, 791), (0, 0))
        self.assertLess(binomial_confidence(791, .0005, .55), .95)

    def test_held_pni_method_components_are_not_rounded_before_computation(self):
        # PNI-2026 workbook row 146: sampling effectiveness .7, diagnostic
        # sensitivity .78, 292 planned samples, C=.8 and p=.01. These source
        # assumptions do not independently demonstrate actual survey performance.
        sensitivity = method_sensitivity(.7, .78)
        self.assertAlmostEqual(binomial_confidence(292, .01, sensitivity), .7978385011673838)
        self.assertEqual(binomial_sample_size(.8, .01, sensitivity), 294)

    @given(st.integers(0, 100000), st.lists(st.integers(1, 100000), min_size=1, max_size=20))
    def test_integer_allocation_preserves_total(self, total, weights):
        result = proportional_allocation(total, tuple(weights))
        self.assertEqual(sum(result), total)
        self.assertTrue(all(n >= 0 for n in result))

    @settings(max_examples=60)
    @given(st.floats(min_value=.001, max_value=.2, allow_nan=False), st.floats(min_value=.1, max_value=.99, allow_nan=False))
    def test_sample_count_is_minimal(self, prevalence, sensitivity):
        n = binomial_sample_size(.95, prevalence, sensitivity)
        self.assertGreaterEqual(binomial_confidence(n, prevalence, sensitivity), .95)
        self.assertLess(binomial_confidence(n - 1, prevalence, sensitivity), .95)


class ComposedTemporalCases(unittest.TestCase):
    def test_regional_compound_conditions_keep_their_basis_event_time(self):
        from cordon_c.bindings import continuing_conditions_facts
        s = Snapshot.load()
        identity = "REG-PUGLIA-U181-DIR-2021-00069:canosa-reduced-buffer"
        basis = date(2021,6,1)
        visited = []
        def source_facts(row, text):
            visited.append(row["provision_version_id"])
            return True
        old = continuing_conditions_facts(s,identity,date(2021,8,1),basis_at=basis,reader=source_facts)
        self.assertTrue(next(iter(old.values())).truth)
        self.assertIn("EU-2020-1201:5(1)(c):v1",visited)
        self.assertNotIn("EU-2020-1201:5(1)(c):v2",visited)
        annual = s.version("EU-2020-1201:5(1)(b)",basis)
        failed = {(annual["provision_version_id"],next(leaves(annual["condition_ast"]))):False}
        current = continuing_conditions_facts(s,identity,date(2021,8,1),basis_at=basis,facts=failed,reader=source_facts)
        self.assertFalse(next(iter(current.values())).truth)
        lifting = "REG-PUGLIA-U181-DIR-2021-00177:revoke-canosa"
        # Evidence for lifting is distinct from exercising the lifting decision.
        def evidence(row,text):
            self.assertNotEqual(row["provision_version_id"],"EU-2020-1201:5(1)(c):v2")
            if text == "the Member State decides to lift the demarcated area":
                raise AssertionError("An evidence calculation must not require this decision")
            return text != "12 months from initial establishment"
        incomplete = continuing_conditions_facts(s,lifting,AT,basis_at=basis,reader=evidence)
        self.assertFalse(next(iter(incomplete.values())).truth)
        with self.assertRaises(MissingInput):
            continuing_conditions_facts(s,identity,AT,basis_at=basis,reader=source_facts)

    def test_species_population_is_distinct_from_individual_health_and_retention(self):
        from cordon_c.bindings import eradication_species_facts
        s = Snapshot.load()
        args = dict(plant_species="species-B",finding_species="species-A",
            species_found_infected_elsewhere=frozenset({"species-B"}),
            infected_species_inventory_complete=True,specified_plant=Evaluation(True))
        facts = eradication_species_facts(s,AT,**args)
        self.assertFalse(evaluate(s,"EU-2020-1201:7(1)(c)",AT,facts).truth)
        self.assertTrue(evaluate(s,"EU-2020-1201:7(1)(d)",AT,facts).truth)
        residual_key = s.version("EU-2020-1201:7(1)(e)",AT)["provision_version_id"],"specified plants other than points (c) and (d)"
        self.assertFalse(facts[residual_key].truth)
        incomplete = eradication_species_facts(s,AT,**(args | {
            "species_found_infected_elsewhere":frozenset(),"infected_species_inventory_complete":False}))
        self.assertIsNone(incomplete[residual_key].truth)
        absent = eradication_species_facts(s,AT,**(args | {"species_found_infected_elsewhere":frozenset()}))
        self.assertTrue(absent[residual_key].truth)
        # The classification does not create an individual negative result or
        # establish the separately conditioned retention decision.
        self.assertIsNone(evaluate(s,"EU-2020-1201:7(3)",AT,absent).truth)

    def test_pre_lifting_tests_use_the_own_target_and_practical_ordering(self):
        from cordon_c.bindings import early_lifting_survey_facts
        s = Snapshot.load()
        args = dict(tests_completed=datetime(2026,9,7,tzinfo=ROME),
            intended_lifting=datetime(2026,9,9,tzinfo=ROME),evaluated_at=datetime(2026,9,8,tzinfo=ROME),
            tests_close_as_practicable=True,population_and_method_qualification=Evaluation(True),
            required_risk_structure=Evaluation(True),performed_test_support=Evaluation(True),
            independence_established=True)
        # 250 at p=.01,s=1 exceeds .90 but fails this provision's .95 target.
        for n, expected in [(250,False),(299,True)]:
            f = early_lifting_survey_facts(s,AT,strata=(BinomialStratum(1,1,1,n),),**args)
            self.assertIs(evaluate(s,"EU-2020-1201:6(2)(b)",AT,f).truth,expected)
        f = early_lifting_survey_facts(s,AT,strata=(BinomialStratum(1,1,1,299),),
            **(args | {"tests_close_as_practicable":None}))
        self.assertIsNone(evaluate(s,"EU-2020-1201:6(2)(b)",AT,f).truth)

    def test_four_year_lifting_uses_each_area_and_annual_survey_basis(self):
        from cordon_c.bindings import four_year_lifting_facts
        from cordon_c.survey import observed_binomial_support, negative_recurrence_support
        from cordon_c.spatial import population_support
        s = Snapshot.load()
        at = date(2026,1,2)
        periods = tuple((date(y,1,1),date(y+1,1,1)) for y in range(2022,2026))
        required = {"infected":Evaluation(True),"buffer":Evaluation(True)}
        def survey(parameter, count):
            return observed_binomial_support(s,parameter,at,
                proportions=(.5,.5),relative_risks=(2,1),method_sensitivities=(.9,.9),
                negative_units=tuple(frozenset(f"{stratum}:{i}" for i in range(count)) for stratum in range(2)),
                positive_units=frozenset(),observation_inventory_complete=True,
                population_and_method_qualification=Evaluation(True),required_risk_structure=Evaluation(True),
                required_performances_complete=Evaluation(True),official_method_and_scope=Evaluation(True),
                independence_established=True)
        inner = survey("B-PAR-EU-10-sub1-C90-p0.5",300)
        buffer = survey("B-PAR-EU-10-sub2-C90-p1",300)
        def result(buffer_support, detections=()):
            all_areas = population_support(required,{"infected":inner,"buffer":buffer_support},
                required_population_complete=True)
            annual = negative_recurrence_support(periods,
                {str(y):(date(y,9,1),all_areas) for y in range(2022,2026)},required_occurrences=1,
                records_complete=True,evaluated_on=at,period_population_complete=Evaluation(True),
                no_detection_in_required_scope=Evaluation(not detections))
            f = four_year_lifting_facts(s,at,date(2022,1,1),detections,datetime(2026,1,2,12,tzinfo=ROME),
                detection_history_complete=True,article10_survey_basis=annual,
                zone=ROME)
            row = s.version("EU-2020-1201:6(1)",at)
            f[row["provision_version_id"],"the Member State decides to lift the demarcation"] = True
            return evaluate(s,"EU-2020-1201:6(1)",at,f)
        self.assertEqual(result(buffer).effect,"DEMARCATED_AREA_LIFTED")
        self.assertEqual(result(survey("B-PAR-EU-10-sub2-C90-p1",0)).effect,"AREA_REMAINS_DEMARCATED")
        self.assertIsNone(result(Evaluation(None,needs=frozenset({"buffer observations"}))).effect)
        self.assertEqual(result(buffer,(date(2025,12,1),)).effect,"AREA_REMAINS_DEMARCATED")

    def test_complete_buffer_reduction_depends_on_the_same_performed_plant_population(self):
        from cordon_c.bindings import (reduced_buffer_removal_facts, reduced_buffer_first_year_facts,
            reduced_buffer_survey_facts, negative_recurrence_facts, bind)
        from cordon_c.survey import observed_binomial_support
        s = Snapshot.load()
        calendar = WorkingCalendar(date(2024,1,1),date(2028,1,1),frozenset(),frozenset({5,6}))
        area_survey = observed_binomial_support(s, "B-PAR-EU-5(1)(c)-v2-C90-p1", AT,
            proportions=(.2,.8),relative_risks=(2.,1.),method_sensitivities=(.9,.9),
            negative_units=(frozenset(f"high-{i}" for i in range(400)),frozenset(f"base-{i}" for i in range(400))),
            positive_units=frozenset(),observation_inventory_complete=True,population_and_method_qualification=Evaluation(True),
            required_risk_structure=Evaluation(True),required_performances_complete=Evaluation(True),
            official_method_and_scope=Evaluation(True),independence_established=True)
        root = bind(s.version("EU-2020-1201:5(1)", AT), {
            "high degree of confidence that the initial presence of the specified pest did not result in its spread": True,
            "the Member State decides to reduce the buffer zone": True})
        annual = negative_recurrence_facts(s,"EU-2020-1201:5(1)(b)",AT,
            periods=((date(2025,6,4),date(2026,6,5)),),evaluated_on=AT,
            performances={"official-test-occasion":(date(2026,5,4),Evaluation(True))},
            records_complete=True,period_population_complete=Evaluation(True),no_detection_in_required_scope=Evaluation(True))
        vectors = negative_recurrence_facts(s,"EU-2020-1201:5(1)(d)",AT,
            periods=((date(2025,6,4),date(2025,11,1)),),evaluated_on=AT,
            performances={"occasion-1":(date(2025,7,4),Evaluation(True)),"occasion-2":(date(2025,9,4),Evaluation(True))},
            records_complete=True,period_population_complete=Evaluation(True),
            no_detection_in_required_scope=Evaluation(True),natural_spread_excluded=Evaluation(True))
        extent = reduced_buffer_first_year_facts(s,AT,identification=datetime(2025,6,4,12,tzinfo=ROME),
            evaluated_at=datetime(2026,9,8,tzinfo=ROME),infected_zone=shape(box(-50,-50,50,50)),
            surveyed_enclosure=shape(box(-2600,-2600,2600,2600)),survey_completed=datetime(2026,5,4,tzinfo=ROME),
            negative_survey_basis=area_survey,host_sampling_and_testing=Evaluation(True),zone=ROME,calendar=calendar)
        design = reduced_buffer_survey_facts(s,AT,(BinomialStratum(.2,2,.9,400),BinomialStratum(.8,1,.9,400)),
            population_and_method_qualification=Evaluation(True),required_risk_structure=Evaluation(True),independence_established=True)
        common = merge_facts(root,annual,vectors,extent,design)
        plants = {"infected":Evaluation(True),"healthy-specified":Evaluation(True)}
        for removed, complete, expected in [
            (frozenset(plants),True,"BUFFER_ZONE_REDUCED"),
            (frozenset({"infected"}),True,"BUFFER_ZONE_NOT_REDUCED"),
            (frozenset({"infected"}),False,None)]:
            work = reduced_buffer_removal_facts(s,AT,required_specified_plants=plants,
                sampled_plants=frozenset(plants),removed_plants=removed,required_population_complete=True,
                sampling_records_complete=True,removal_records_complete=complete,immediacy=Evaluation(True))
            self.assertEqual(evaluate(s,"EU-2020-1201:5(1)",AT,merge_facts(common,work)).effect,expected)

    def test_vector_condition_needs_two_occasions_and_exclusion_of_spread(self):
        from cordon_c.bindings import negative_recurrence_facts
        s = Snapshot.load()
        args = dict(periods=((date(2026, 4, 1), date(2026, 11, 1)),), evaluated_on=AT,
                    records_complete=True, period_population_complete=Evaluation(True),
                    no_detection_in_required_scope=Evaluation(True))
        identity = "EU-2020-1201:5(1)(d)"
        events = {"occasion-1": (date(2026, 5, 1), Evaluation(True))}
        one = negative_recurrence_facts(s, identity, AT, **args, performances=events,
                                        natural_spread_excluded=Evaluation(True))
        self.assertIsNone(next(iter(one.values())).truth)
        closed = negative_recurrence_facts(s, identity, AT, **(args | {"evaluated_on": date(2026,11,1)}),
            performances=events, natural_spread_excluded=Evaluation(True))
        self.assertFalse(next(iter(closed.values())).truth)
        events["occasion-2"] = (date(2026, 7, 1), Evaluation(True))
        two = negative_recurrence_facts(s, identity, AT, **args, performances=events)
        self.assertIsNone(next(iter(two.values())).truth)
        two = negative_recurrence_facts(s, identity, AT, **args, performances=events,
                                        natural_spread_excluded=Evaluation(True))
        self.assertTrue(evaluate(s, identity, AT, two).truth)
        args["no_detection_in_required_scope"] = Evaluation(False)
        positive = negative_recurrence_facts(s, identity, AT, **args, performances=events,
                                        natural_spread_excluded=Evaluation(True))
        self.assertFalse(evaluate(s, identity, AT, positive).truth)

    def test_reduced_buffer_first_year_uses_identification_and_whole_extent(self):
        from cordon_c.bindings import reduced_buffer_first_year_facts, reduced_buffer_survey_facts
        s = Snapshot.load()
        calendar = WorkingCalendar(date(2024, 1, 1), date(2028, 1, 1), frozenset(), frozenset({5, 6}))
        args = dict(identification=datetime(2025, 6, 4, 12, tzinfo=ROME),
                    evaluated_at=datetime(2026, 9, 8, tzinfo=ROME),
                    infected_zone=shape(box(-50, -50, 50, 50)),
                    surveyed_enclosure=shape(box(-2600, -2600, 2600, 2600)),
                    survey_completed=datetime(2026, 5, 4, tzinfo=ROME),
                    negative_survey_basis=Evaluation(True), host_sampling_and_testing=Evaluation(True),
                    zone=ROME, calendar=calendar)
        adequate = reduced_buffer_survey_facts(s, AT, (BinomialStratum(.2, 2, .9, 400), BinomialStratum(.8, 1, .9, 400)),
                    population_and_method_qualification=Evaluation(True), required_risk_structure=Evaluation(True),
                    independence_established=True)
        scope = reduced_buffer_first_year_facts(s, AT, **args)
        self.assertTrue(evaluate(s, "EU-2020-1201:5(1)(c)", AT, merge_facts(adequate, scope)).truth)
        args["surveyed_enclosure"] = shape(box(-2400, -2600, 2600, 2600))
        scope = reduced_buffer_first_year_facts(s, AT, **args)
        self.assertFalse(evaluate(s, "EU-2020-1201:5(1)(c)", AT, merge_facts(adequate, scope)).truth)
        args["surveyed_enclosure"] = shape(box(-2600, -2600, 2600, 2600))
        args["survey_completed"] = datetime(2026, 6, 5, tzinfo=ROME)
        scope = reduced_buffer_first_year_facts(s, AT, **args)
        self.assertFalse(evaluate(s, "EU-2020-1201:5(1)(c)", AT, merge_facts(adequate, scope)).truth)

    def test_case_commencement_is_not_completion_and_requires_evidence(self):
        from cordon_c.bindings import noncommencement_facts
        from test_prescribed_terms import CLOCK, snapshot_fixture, term
        s = snapshot_fixture()
        # This source-bound fixture isolates temporal behavior. The explicit
        # candidate tests exercise the operative clause's remaining legal guards.
        args = dict(notification=datetime(2026, 8, 3, 10, tzinfo=ROME),
                    evaluated_at=datetime(2026, 8, 14, tzinfo=ROME),
                    prescribed_term=term(),
                    zone=ROME, calendar=WorkingCalendar(date(2026,1,1),date(2027,1,1),frozenset(),frozenset({5,6})))
        for events, complete, expected in [({}, True, "TEMPORAL_CONDITION_ESTABLISHED"),
                ({"actual-start": datetime(2026, 8, 5, 12, tzinfo=ROME)}, True, "NOT_ESTABLISHED"),
                ({}, False, None)]:
            computed = noncommencement_facts(s, CLOCK, AT, **args,
                        qualifying_commencements=events, commencement_records_complete=complete)
            self.assertEqual(evaluate(s, "fixture", AT, computed).effect, expected)
        # Work that began before notification does not need to begin again.
        computed = noncommencement_facts(s, CLOCK, AT, **args,
                    qualifying_commencements={"early-start": datetime(2026, 8, 2, tzinfo=ROME)},
                    commencement_records_complete=False)
        self.assertEqual(evaluate(s, "fixture", AT, computed).effect, "NOT_ESTABLISHED")

    def test_early_election_defeats_silence_without_waiting_for_publication_end(self):
        from cordon_c.bindings import election_window_facts
        s = Snapshot.load()
        identity = "PUG-DGR1075-2025:§4.5:silence-route"
        row = s.version(identity, AT)
        facts = election_window_facts(s, "B-CLK-DGR1075-owner-election", identity, AT,
                publication_end_day=date(2026, 8, 7),
                first_valid_election_time=datetime(2026, 8, 1, tzinfo=ROME),
                evaluated_at=datetime(2026, 8, 4, tzinfo=ROME),
                qualifying_elections={"election": datetime(2026, 8, 3, tzinfo=ROME)},
                election_records_complete=False, zone=ROME, calendar=WorkingCalendar(date(2026,1,1),date(2027,1,1),frozenset(),frozenset({5,6})))
        self.assertFalse(facts[row["provision_version_id"], "affirmative no-response evidence"])
        self.assertFalse(facts[row["provision_version_id"], "completed election window"])

    def test_lookback_known_detection_defeats_absence_despite_incomplete_history(self):
        from cordon_c.bindings import sampling_lookback_facts
        s = Snapshot.load()
        args = dict(evaluated_at=datetime(2026, 9, 8, 12, tzinfo=ROME), history_complete=False, zone=ROME)
        result = sampling_lookback_facts(s, AT, qualifying_detections={"finding": datetime(2024, 9, 8, tzinfo=ROME)}, **args)
        self.assertIs(next(iter(result.values())), False)
        result = sampling_lookback_facts(s, AT, qualifying_detections={"old": datetime(2024, 9, 7, tzinfo=ROME)}, **args)
        self.assertIsNone(next(iter(result.values())).truth)




class OperativeMethods(unittest.TestCase):
    def test_finite_rounding_and_published_reconstruction(self):
        from cordon_c.survey import FiniteStratum, finite_design_counts, finite_design_samples
        self.assertEqual(finite_design_counts(Decimal('.025'), (FiniteStratum(Decimal(100),1,.9,0),)), ((100,2),))
        # Distinguishes half-up, and also exercises a genuinely estimated capacity.
        self.assertEqual(finite_design_counts(Decimal('.025'), (FiniteStratum(Decimal('100.75'),1,.9,0),)), ((100,3),))
        examples = [
            (('58371255','990804'),'.0005',.95,(5537,2765)),
            (('107846160','2109000'),'.0009',.95,(3084,1541)),
            (('17039438','568331'),'.0009',.95,(3123,1560)),
            (('47674191','641688'),'.007',.9,(303,151))]
        for populations,p,c,expected in examples:
            strata=tuple(FiniteStratum(Decimal(n),risk,.55,0) for n,risk in zip(populations,(1,2)))
            self.assertEqual(finite_design_samples(Decimal(p),strata,c,independence_established=True),expected)
        # The source approximation's 86 is insufficient under exact probability.
        self.assertEqual(finite_design_samples(Decimal('.02'),(FiniteStratum(Decimal(100),1,.9,0),),.95,independence_established=True),(87,))

    def test_finite_reallocation_and_two_stage_composition(self):
        from dataclasses import replace
        from cordon_c.survey import FiniteStratum, finite_design_samples, stratified_finite_meets, two_stage_finite_confidence
        strata=(FiniteStratum(Decimal('684.23'),2,.05,0),FiniteStratum(Decimal('7339.52'),1,.05,0))
        counts=finite_design_samples(Decimal('.01'),strata,.9,independence_established=True)
        self.assertEqual(counts,(684,3489))
        self.assertTrue(stratified_finite_meets(Decimal('.01'),tuple(replace(s,inspection_units=n) for s,n in zip(strata,counts)),.9,independence_established=True))
        self.assertFalse(stratified_finite_meets(Decimal('.01'),(replace(strata[0],inspection_units=684),replace(strata[1],inspection_units=3488)),.9,independence_established=True))
        with self.assertRaises(ValueError):
            finite_design_samples(Decimal('.01'),(FiniteStratum(Decimal(100),1,.1,0),),.95,independence_established=True)
        # One infected plant: inner detection is .5 * .8 = .4. One infected
        # hectare in ten, inspecting five, gives .5 * .4 = .2, independently.
        self.assertAlmostEqual(two_stage_finite_confidence(outer_population=10,outer_infected=1,units_inspected=5,
            inner_population=10,inner_infected=1,plants_per_unit=5,plant_method_sensitivity=.8,
            homogeneous_unit_design_established=True),.2)

    def test_clock_classes_distinguish_weekends_and_continuous_publication(self):
        snapshot=Snapshot.load()
        calendar=WorkingCalendar(date(2025,1,1),date(2028,1,1),frozenset(),frozenset({5,6}))
        # A procedural submission extends Saturday expiry to Monday.
        result=clock_boundary(snapshot,'B-CLK-DGR1075-owner-election',AT,date(2026,9,2),zone=ROME,calendar=calendar)
        self.assertEqual(result,datetime(2026,9,8,tzinfo=ROME))
        # A physical execution deadline is a separate calendar convention.
        result=clock_boundary(snapshot,'B-CLK-DGR1075-owner-execution',AT,date(2026,8,26),zone=ROME,calendar=calendar)
        self.assertEqual(result,datetime(2026,9,6,tzinfo=ROME))
        # Sunday expiry extends to Monday. Publication itself is uninterrupted.
        result=clock_boundary(snapshot,'B-CLK-DGR1075-owner-election',AT,date(2026,9,3),zone=ROME,calendar=calendar)
        self.assertEqual(result,datetime(2026,9,8,tzinfo=ROME))
        result=clock_boundary(snapshot,'B-CLK-DGR1075-albo-publication',AT,date(2026,9,5),zone=ROME)
        self.assertEqual(result,datetime(2026,9,13,tzinfo=ROME))
        result=clock_boundary(snapshot,'B-CLK-EU-5(1)(c)-v2-first-year-survey',AT,date(2025,9,5),zone=ROME,calendar=calendar)
        self.assertEqual(result,datetime(2026,9,8,tzinfo=ROME))
        result=clock_boundary(snapshot,'B-CLK-DDS45-cnr-analysis-return',AT,date(2026,9,4),zone=ROME,calendar=calendar)
        self.assertEqual(result,datetime(2026,9,10,tzinfo=ROME))
        with self.assertRaises(MissingInput):
            clock_boundary(snapshot,'B-CLK-DGR1075-owner-election',AT,date(2026,9,2),zone=ROME)

    def test_election_adapter_uses_canonical_rule_and_received_election_defeats_silence(self):
        from cordon_c.bindings import election_window_facts
        s=Snapshot.load()
        identity='PUG-DGR1075-2025:§4.5:silence-route'
        row=s.version(identity,AT)
        calendar=WorkingCalendar(date(2026,1,1),date(2027,1,1),frozenset(),frozenset({5,6}))
        for publication_end in (date(2026,9,2),date(2026,9,3)):
            args=dict(publication_end_day=publication_end,
                first_valid_election_time=datetime(2026,8,25,tzinfo=ROME),
                evaluated_at=datetime(2026,9,7,12,tzinfo=ROME),
                election_records_complete=True,zone=ROME,calendar=calendar)
            facts=election_window_facts(s,'B-CLK-DGR1075-owner-election',identity,AT,
                **args,qualifying_elections={'communication':datetime(2026,9,6,10,tzinfo=ROME)})
            self.assertFalse(facts[row['provision_version_id'],'completed election window'])
            self.assertFalse(facts[row['provision_version_id'],'affirmative no-response evidence'])
            remaining={(row['provision_version_id'],p):p in {
                'substantive prescription is valid and effective against the recipient', 'valid recipient notice'}
                for p in leaves(row['condition_ast']) if (row['provision_version_id'],p) not in facts}
            self.assertEqual(evaluate(s,identity,AT,merge_facts(remaining,facts)).effect,
                'PLAN_ONLY_SUBSTANTIVE_EVIDENCE_REQUIRED')
            args['evaluated_at']=datetime(2026,9,8,tzinfo=ROME)
            facts=election_window_facts(s,'B-CLK-DGR1075-owner-election',identity,AT,
                **args,qualifying_elections={})
            self.assertEqual(evaluate(s,identity,AT,merge_facts(remaining,facts)).effect,
                'PLAN_ONLY_EFFECT_APPLIES')

    def test_clock_rule_population_has_one_disposition(self):
        snapshot=Snapshot.load()
        groups=json.loads((Path(__file__).parent/'calendar-rules.json').read_text())
        selected=[item for group in groups.values() for item in group]
        expected={r['clock_id'] for r in snapshot.clocks.values() if r['kind'] not in {'recurrence','ordering_constraint','promptness_standard'}}
        self.assertEqual(set(selected),expected)
        self.assertEqual(len(selected),len(set(selected)))

    def test_finite_observations_feed_lifting_and_ignore_planned_counts(self):
        from cordon_c.survey import FiniteStratum, observed_survey_support
        from cordon_c.bindings import early_lifting_survey_facts
        snapshot=Snapshot.load(); yes=Evaluation(True)
        strata=(FiniteStratum(Decimal(100),1,.99,100),)
        kw=dict(population_and_method_qualification=yes,required_risk_structure=yes,
                required_performances_complete=yes,official_method_and_scope=yes,independence_established=True)
        param='B-PAR-EU-6(2)(b)-C95-p1'
        def support(count,complete=True):
            return observed_survey_support(snapshot,param,AT,strata=strata,negative_units=(frozenset(map(str,range(count))),),
                positive_units=frozenset(),observation_inventory_complete=complete,**kw)
        self.assertFalse(support(95).truth) # one infected: .95*.99 < .95
        self.assertTrue(support(96).truth)
        self.assertIsNone(support(96,False).truth)
        bound=early_lifting_survey_facts(snapshot,AT,tests_completed=datetime(2026,9,7,tzinfo=ROME),
            intended_lifting=datetime(2026,9,8,tzinfo=ROME),evaluated_at=datetime(2026,9,8,tzinfo=ROME),
            tests_close_as_practicable=True,strata=(FiniteStratum(Decimal(100),1,.99,96),),
            population_and_method_qualification=yes,required_risk_structure=yes,performed_test_support=support(96),
            independence_established=True)
        result=evaluate(snapshot,'EU-2020-1201:6(2)(b)',AT,facts=bound)
        self.assertTrue(result.truth)

    def test_accepted_regional_targets_have_material_consumer_effect(self):
        from cordon_c.survey import FiniteStratum, survey_design_adequacy
        from cordon_c.quantities import planned_sample_difference
        snapshot=Snapshot.load(); root=Path(__file__).resolve().parents[2]
        proposal=json.loads((root/'corpus/evidence/stage-c-regional-survey-amendment-2026-09-08.json').read_text())
        self.assertEqual(proposal['status'],'PROPOSED_FOR_REVIEW_NOT_ACCEPTED')
        # The accepted owner now contains the exact reviewed additions. The
        # unchanged proposal remains dated evidence, not a runtime ledger.
        for row in proposal['stage_a_additions']:
            self.assertEqual(snapshot.versions[row['provision_version_id']],row)
        for row in proposal['stage_b_additions']['parameters']:
            self.assertEqual(snapshot.quantity(row['parameter_id'],AT),row)
        candidate=snapshot
        strata=(FiniteStratum(Decimal(100000),1,.55,1000),)
        kw=dict(population_and_method_qualification=Evaluation(True),required_risk_structure=Evaluation(True),independence_established=True)
        self.assertTrue(survey_design_adequacy(candidate,'B-PAR-EU-15(4)-C90-p1',AT,strata,**kw).truth)
        self.assertFalse(survey_design_adequacy(candidate,'B-PAR-DGR1075-T4-olive-design',AT,strata,**kw).truth)
        self.assertEqual(planned_sample_difference(candidate,'B-PAR-DGR1075-T4-olive-high-samples',AT,5000),116)


if __name__ == "__main__":
    unittest.main()
