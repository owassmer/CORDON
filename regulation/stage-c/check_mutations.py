"""Bounded discriminating mutations of actual reference functions, in memory.

No canonical file is edited. Each named regression must fail on its associated
wrong implementation; this is evidence about these failures, not a coverage score.
"""

import importlib
from pathlib import Path
import unittest

import test_reference


MUTATIONS = (
    ("cordon_c.survey", 'round(Fraction(s.population) * p)', 'int(Fraction(s.population) * p + Fraction(1, 2))',
     "OperativeMethods.test_finite_rounding_and_published_reconstruction"),
    ("cordon_c.quantities", 'if name == "italian_deadline" else', 'if False else',
     "OperativeMethods.test_clock_classes_distinguish_weekends_and_continuous_publication"),
    ("cordon_c.survey", 'replace(s, inspection_units=len(units)) for s,units in zip(strata,negative_units)',
     's for s,units in zip(strata,negative_units)',
     "OperativeMethods.test_finite_observations_feed_lifting_and_ignore_planned_counts"),
    ("cordon_c.quantities", 'if name == "italian_deadline" else',
     'if name in {"italian_deadline", "italian_procedural_submission"} else',
     "OperativeMethods.test_election_adapter_uses_canonical_rule_and_received_election_defeats_silence"),
    ("cordon_c.populations", 'surviving.distance(infected_zone.geometry) + error < width',
     'hectare.geometry.distance(infected_zone.geometry) + error < width',
     "SpatialPopulations.test_hectare_requires_the_same_surviving_surface_within_the_band"),
    ("cordon_c.temporal", "(utc(anchor) + timedelta(hours=hours))", "(anchor + timedelta(hours=hours))",
     "CalendarBoundaries.test_elapsed_hours_across_dst"),
    ("cordon_c.diagnostic", "present and cq < lower", "present and cq <= lower",
     "DiagnosticBoundaries.test_exact_boundaries_and_no_cq"),
    ("cordon_c.spatial", 'distance_test(point, origin, inner_m + width_m, "<=")', 'distance_test(point, origin, width_m, "<=")',
     "SpatialPopulations.test_band_outer_is_450_not_400"),
    ("cordon_c.core", 'result.effect == ref["allowed_effect"]', 'result.effect.startswith(ref["allowed_effect"])',
     "LegalComposition.test_compound_effect_is_not_prefix_matched"),
    ("cordon_c.core", 'if edge in snapshot.reference_outcomes:', 'if False and edge in snapshot.reference_outcomes:',
     "LegalComposition.test_doubtful_route_uses_doubtful_class_not_any_matched_route"),
    ("cordon_c.spatial", 'if not required_population_complete:', 'if False and not required_population_complete:',
     "SpatialPopulations.test_shared_performance_and_incomplete_population"),
    ("cordon_c.survey", '>= target.numerator * denominator', '> target.numerator * denominator',
     "SurveyMathematics.test_finite_model_against_exact_combinatorics"),
    ("cordon_c.survey", 'if not observation_inventory_complete:', 'if False and not observation_inventory_complete:',
     "SurveyMathematics.test_observed_survey_counts_units_and_requires_a_coherent_stratum_partition"),
    ("cordon_c.bindings", 'begun = any(', 'begun = False and any(',
     "ComposedTemporalCases.test_case_commencement_is_not_completion_and_requires_evidence"),
    ("cordon_c.core", 'facts[key] if key in facts or reader is None else reader(row, text)',
     'reader(row, text) if reader is not None else facts[key]',
     "LegalComposition.test_computed_facts_and_performances_compose_with_remaining_semantic_reader"),
    ("cordon_c.survey", 'records_complete and evaluated_on >= end and proven', 'records_complete and proven',
     "ComposedTemporalCases.test_vector_condition_needs_two_occasions_and_exclusion_of_spread"),
    ("cordon_c.core", 'if edge in snapshot.historical_references else provision(edge[1])',
     'if False and edge in snapshot.historical_references else provision(edge[1])',
     "LegalComposition.test_early_lifting_preserves_a_pre_amendment_reduction_result"),
    ("cordon_c.core", 'if isinstance(value, Evaluation):\n        return Evaluation(value.truth, needs=value.needs, provisions=value.provisions)',
     'if isinstance(value, Evaluation):\n        return value',
     "LegalComposition.test_input_evaluations_cannot_replace_the_consuming_legal_effect"),
    ("cordon_c.bindings", 'approved = Evaluation(day <= at and approves)', 'approved = published',
     "OwnerRulings20260924.test_listing_follows_definitive_republication"),
    ("cordon_c.bindings", 'period = stated_period', 'period = stated_period or ("7", "giorni")',
     "OwnerRulings20260924.test_mass_publicity_needs_the_acts_own_ground_period_and_completed_posting"),
    ("cordon_c.bindings", '    if notification is None:\n', '    if False:\n',
     "ComposedTemporalCases.test_case_commencement_is_not_completion_and_requires_evidence"),
    ("cordon_c.spatial", 'parcel_core = parcel.geometry.buffer(-parcel.error_m, quad_segs=QUAD_SEGMENTS)\n'
     '    area_core = adopted_area.geometry.buffer(-adopted_area.error_m, quad_segs=QUAD_SEGMENTS)',
     'parcel_core = parcel.geometry.buffer(-error, quad_segs=QUAD_SEGMENTS)\n'
     '    area_core = adopted_area.geometry.buffer(-error, quad_segs=QUAD_SEGMENTS)',
     "SpatialPopulations.test_partial_parcel_cores_shrink_by_each_geometrys_own_error"),
    ("cordon_c.spatial", 'parcel_core = parcel.geometry.buffer(-parcel.error_m, quad_segs=QUAD_SEGMENTS)\n'
     '    area_core = adopted_area.geometry.buffer(-adopted_area.error_m, quad_segs=QUAD_SEGMENTS)',
     'parcel_core = parcel.geometry.buffer(-adopted_area.error_m, quad_segs=QUAD_SEGMENTS)\n'
     '    area_core = adopted_area.geometry.buffer(-parcel.error_m, quad_segs=QUAD_SEGMENTS)',
     "SpatialPopulations.test_partial_parcel_cores_shrink_by_each_geometrys_own_error"),
    ("cordon_c.spatial", 'cos(3 * pi / (8 * QUAD_SEGMENTS))', 'cos(pi / (4 * QUAD_SEGMENTS))',
     "ComposedTemporalCases.test_survey_extent_counts_the_whole_grown_enclosure_at_a_convex_corner"),
    ("cordon_c.spatial", 'if (parcel.geometry.contains(x) and adopted_area.geometry.contains(x)\n'
     '                and x.distance(parcel.geometry.boundary) > parcel.error_m\n'
     '                and x.distance(adopted_area.geometry.boundary) > adopted_area.error_m):',
     'if True:',
     "SpatialPopulations.test_partial_parcel_drawn_core_past_the_inscribed_radius_stays_unknown"),
    ("cordon_c.spatial", 'if (parcel.geometry.contains(x) and adopted_area.geometry.contains(x)\n'
     '                and x.distance(parcel.geometry.boundary) > parcel.error_m\n'
     '                and x.distance(adopted_area.geometry.boundary) > adopted_area.error_m):',
     'if True:',
     "SpatialPopulations.test_partial_parcel_chord_at_a_reflex_corner_stays_unknown"),
    ("cordon_c.spatial", '\n            and parcel.geometry.distance(adopted_area.geometry.boundary) > error)', ')',
     "SpatialPopulations.test_partial_parcel_wholly_inside_needs_the_combined_error_from_the_boundary"),
    ("cordon_c.spatial", 'enclosure.geometry.buffer(_circumscribed(error), quad_segs=QUAD_SEGMENTS)',
     'enclosure.geometry.buffer(error, quad_segs=QUAD_SEGMENTS)',
     "ComposedTemporalCases.test_survey_extent_counts_the_whole_grown_enclosure_at_a_convex_corner"),
    ("cordon_c.populations", 'surviving = hectare.geometry.difference(possible_zone)',
     'surviving = hectare.geometry.difference(infected_zone.geometry)',
     "SpatialPopulations.test_hectare_outside_sliver_must_survive_declared_spatial_error"),
)


def main():
    for name, before, after, case in MUTATIONS:
        module = importlib.import_module(name)
        path = Path(module.__file__)
        source = path.read_text()
        baseline = unittest.TestResult()
        unittest.defaultTestLoader.loadTestsFromName(case, test_reference).run(baseline)
        if not baseline.wasSuccessful():
            raise AssertionError(f"Baseline already fails: {case}: {baseline.failures + baseline.errors}")
        if source.count(before) != 1:
            raise AssertionError(f"Mutation location changed: {name}: {before}")
        # Mutate function objects in place: consumers importing the function
        # directly must see the mutation too. Restore all code in finally.
        namespace = dict(module.__dict__)
        exec(compile(source.replace(before, after), str(path), "exec"), namespace)
        originals = []
        try:
            for key, value in namespace.items():
                original = module.__dict__.get(key)
                if callable(value) and getattr(value, "__module__", None) == name and hasattr(value, "__code__") and hasattr(original, "__code__"):
                    originals.append((original, original.__code__))
                    original.__code__ = value.__code__
            suite = unittest.defaultTestLoader.loadTestsFromName(case, test_reference)
            result = unittest.TestResult()
            suite.run(result)
            if result.wasSuccessful() or result.testsRun != 1:
                raise AssertionError(f"Regression did not discriminate mutation: {name}: {case}")
            print(f"Discriminated: {case}")
        finally:
            for function, code in originals:
                function.__code__ = code


if __name__ == "__main__":
    main()
