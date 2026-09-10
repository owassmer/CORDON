"""Survey probabilities under the explicitly supplied operative design.

EFSA EN-1873 sections 2.2–2.4 and RiBESS/RiPEST supply the model. Sensitivity is
that of the complete inspection method. Independent inspection units and risk
strata must be justified by the design; repeated tests are not new plants.
"""

from decimal import Decimal
from datetime import date
from collections.abc import Mapping
from dataclasses import dataclass, replace
from fractions import Fraction
from math import ceil, comb, expm1, isfinite, log1p, prod
import numpy as np
from scipy.special import logsumexp

from .core import Evaluation, MissingInput, Snapshot, conjunction


def probability(value: float, *, positive: bool = False) -> float:
    if isinstance(value, bool):
        raise TypeError("A probability is not a status flag")
    if not isfinite(value) or not 0 <= value <= 1 or positive and value == 0:
        raise ValueError("Probability outside its valid domain")
    return value


def method_sensitivity(sampling_effectiveness: float, diagnostic_sensitivity: float) -> float:
    return probability(sampling_effectiveness) * probability(diagnostic_sensitivity)


def independent_parallel_sensitivity(sensitivities: tuple[float, ...], *, independence_established: bool) -> float:
    if not sensitivities:
        raise ValueError("No methods supplied")
    if not independence_established:
        raise MissingInput("joint sensitivity of the combined detection methods")
    return 1 - prod(1 - probability(s) for s in sensitivities)


def binomial_confidence(n: int, prevalence: float, sensitivity: float) -> float:
    if type(n) is not int or n < 0:
        raise ValueError("Nonnegative integer count of independent inspection units required")
    p = probability(prevalence) * probability(sensitivity)
    if not n or not p:
        return 0.0
    if p == 1:
        return 1.0
    return -expm1(n * log1p(-p))


def binomial_sample_size(confidence: float, prevalence: float, sensitivity: float) -> int:
    probability(confidence, positive=True)
    p = probability(prevalence, positive=True) * probability(sensitivity, positive=True)
    if p == 1:
        return 1
    if confidence == 1:
        raise ValueError("Certainty cannot be reached by a finite imperfect sample")
    n = ceil(log1p(-confidence) / log1p(-p))
    while not binomial_meets(n, prevalence, sensitivity, confidence):
        n += 1
    while n > 1 and binomial_meets(n - 1, prevalence, sensitivity, confidence):
        n -= 1
    return n


def binomial_meets(n: int, prevalence: float, sensitivity: float, confidence: float) -> bool:
    probability(confidence)
    observed = binomial_confidence(n, prevalence, sensitivity)
    if abs(observed - confidence) > 1e-12:
        return observed >= confidence
    p = Fraction(str(prevalence)) * Fraction(str(sensitivity))
    return 1 - (1 - p) ** n >= Fraction(str(confidence))


def risk_prevalences(prevalence: float, proportions: tuple[float, ...],
                     relative_risks: tuple[float, ...]) -> tuple[float, ...]:
    probability(prevalence, positive=True)
    if not proportions or len(proportions) != len(relative_risks):
        raise ValueError("One proportion and relative risk per disjoint stratum required")
    if abs(sum(proportions) - 1) > 1e-12:
        raise ValueError("Strata must partition the whole target population")
    if any(not isfinite(r) or r <= 0 for r in relative_risks):
        raise ValueError("Relative risks must be finite and positive")
    for p in proportions:
        probability(p, positive=True)
    mean_risk = sum(p * r for p, r in zip(proportions, relative_risks))
    values = tuple(prevalence * r / mean_risk for r in relative_risks)
    for p in values:
        probability(p)
    return values


def independent_system_confidence(group_confidences: tuple[float, ...], *,
                                  independence_established: bool) -> float:
    if not group_confidences:
        raise ValueError("No survey groups supplied")
    if not independence_established:
        raise MissingInput("survey dependence model")
    return 1 - prod(1 - probability(c) for c in group_confidences)


def equal_group_target(confidence: float, groups: int) -> float:
    probability(confidence, positive=True)
    if type(groups) is not int or groups < 1 or confidence == 1:
        raise ValueError("Positive group count and attainable confidence required")
    return -expm1(log1p(-confidence) / groups)


def proportional_allocation(total: int, weights: tuple[int, ...]) -> tuple[int, ...]:
    """Integer apportionment preserves the count; it does not prove design adequacy."""
    if type(total) is not int or total < 0 or not weights or any(type(w) is not int or w < 0 for w in weights) or sum(weights) == 0:
        raise ValueError("Nonnegative count and nonzero integer population weights required")
    denominator = sum(weights)
    quotients = [divmod(total * w, denominator) for w in weights]
    allocated = [q for q, _ in quotients]
    order = sorted(range(len(weights)), key=lambda i: (-quotients[i][1], i))
    for i in order[:total - sum(allocated)]:
        allocated[i] += 1
    return tuple(allocated)


def design_targets(parameter: dict) -> tuple[Decimal, Decimal]:
    if parameter["unit"] != "percent" or parameter["kind"] != "design_target":
        raise ValueError("A survey design parameter is required")
    value = parameter["value"]
    return Decimal(value["confidence"]) / 100, Decimal(value["design_prevalence"]) / 100


@dataclass(frozen=True)
class BinomialStratum:
    proportion: float
    relative_risk: float
    method_sensitivity: float
    inspection_units: int


@dataclass(frozen=True)
class FiniteStratum:
    population: Decimal
    relative_risk: float
    method_sensitivity: float
    inspection_units: int


def finite_design_counts(prevalence: Decimal, strata: tuple[FiniteStratum, ...]) -> tuple[tuple[int, int], ...]:
    """RiBESS population convention, with exact decimal/rational arithmetic.

    Estimated populations are a qualified design input, not a census. As in the
    held RiBESS source, capacity is floor(N) and infected count is nearest N*p_i,
    ties to even. Exact probability then replaces the tool's approximation.
    """
    if not isinstance(prevalence, Decimal) or not prevalence.is_finite() or not 0 < prevalence <= 1:
        raise ValueError("Finite Decimal design prevalence required")
    if not strata or any(not isinstance(s, FiniteStratum) for s in strata):
        raise TypeError("A nonempty finite stratum population is required")
    if any(not isinstance(s.population, Decimal) or not s.population.is_finite() or s.population < 1 for s in strata):
        raise ValueError("Each represented finite stratum needs at least one inspection unit")
    if any(isinstance(s.relative_risk, bool) or not isfinite(s.relative_risk) or s.relative_risk <= 0 for s in strata):
        raise ValueError("Positive finite relative risk required")
    total = sum(Fraction(s.population) for s in strata)
    mean_risk = sum(Fraction(s.population) * Fraction(str(s.relative_risk)) for s in strata) / total
    result = []
    for s in strata:
        p = Fraction(prevalence) * Fraction(str(s.relative_risk)) / mean_risk
        if p > 1:
            raise ValueError("Risk-adjusted prevalence exceeds one")
        n, d = int(s.population), round(Fraction(s.population) * p)
        if d > n:
            raise ValueError("Infected-count convention exceeds finite capacity")
        result.append((n, d))
    return tuple(result)


def stratified_finite_confidence(prevalence: Decimal, strata: tuple[FiniteStratum, ...], *,
                                 independence_established: bool) -> float:
    counts = finite_design_counts(prevalence, strata)
    groups = tuple(finite_confidence(n, d, s.inspection_units, s.method_sensitivity)
                   for (n, d), s in zip(counts, strata))
    return independent_system_confidence(groups, independence_established=independence_established)


def _finite_negative_fraction(n: int, d: int, inspected: int, sensitivity: float) -> Fraction:
    # Symmetry limits exact work to the smaller of infected and sampled counts.
    d, inspected = max(d, inspected), min(d, inspected)
    lo, hi = max(0, inspected - (n - d)), min(inspected, d)
    s = Fraction(str(sensitivity))
    return sum((Fraction(comb(d, k) * comb(n-d, inspected-k), comb(n, inspected)) * (1-s)**k
                for k in range(lo, hi+1)), Fraction(0))


def stratified_finite_meets(prevalence: Decimal, strata: tuple[FiniteStratum, ...], confidence: float, *,
                            independence_established: bool) -> bool:
    probability(confidence)
    achieved = stratified_finite_confidence(prevalence, strata, independence_established=independence_established)
    if abs(achieved - confidence) > 1e-10:
        return achieved >= confidence
    counts = finite_design_counts(prevalence, strata)
    negative = prod(_finite_negative_fraction(n, d, s.inspection_units, s.method_sensitivity)
                    for (n, d), s in zip(counts, strata))
    return 1-negative >= Fraction(str(confidence))


def finite_design_samples(prevalence: Decimal, strata: tuple[FiniteStratum, ...], confidence: float, *,
                          independence_established: bool) -> tuple[int, ...]:
    """Equal stratum targets, redistributing unattainable targets as RiBESS does.

    No ranking or optimization. Capacity never certifies a missed target.
    Zero-population risk strata must be omitted from the operative partition.
    """
    probability(confidence, positive=True)
    if confidence == 1:
        raise ValueError("Use an attainable confidence below one")
    counts = finite_design_counts(prevalence, strata)
    maximum = tuple(finite_confidence(n, d, n, s.method_sensitivity) for (n,d),s in zip(counts,strata))
    full = tuple(replace(s, inspection_units=n) for (n,_),s in zip(counts,strata))
    if not stratified_finite_meets(prevalence, full, confidence, independence_established=independence_established):
        raise ValueError("Requested confidence is unattainable for the whole design")
    capped = set()
    while True:
        remaining = len(strata)-len(capped)
        if not remaining:
            return tuple(n for n,_ in counts)
        negative_capped = prod(1-maximum[i] for i in capped)
        target = -expm1(log1p(-confidence)/remaining - np.log(negative_capped)/remaining)
        newly_capped = {i for i,c in enumerate(maximum) if i not in capped and c < target}
        if not newly_capped:
            break
        capped |= newly_capped
    result = [n if i in capped else finite_sample_size(n,d,s.method_sensitivity,float(target))
              for i,((n,d),s) in enumerate(zip(counts,strata))]
    # Root rounding must not produce a false global pass at exact boundaries.
    while not stratified_finite_meets(prevalence, tuple(replace(s, inspection_units=k) for s,k in zip(strata,result)),
                                      confidence, independence_established=independence_established):
        i = next(i for i,(n,_) in enumerate(counts) if result[i] < n and maximum[i] > 0)
        result[i] += 1
    return tuple(result)


def stratified_binomial_confidence(prevalence: float, strata: tuple[BinomialStratum, ...], *,
                                   independence_established: bool) -> float:
    prevalences = risk_prevalences(prevalence, tuple(s.proportion for s in strata),
                                  tuple(s.relative_risk for s in strata))
    groups = tuple(binomial_confidence(s.inspection_units, p, s.method_sensitivity)
                   for s, p in zip(strata, prevalences))
    return independent_system_confidence(groups, independence_established=independence_established)


def stratified_binomial_meets(prevalence: float, strata: tuple[BinomialStratum, ...], confidence: float, *,
                              independence_established: bool) -> bool:
    probability(confidence)
    observed = stratified_binomial_confidence(prevalence, strata, independence_established=independence_established)
    if abs(observed - confidence) > 1e-12:
        return observed >= confidence
    mean_risk = sum(Fraction(str(s.proportion)) * Fraction(str(s.relative_risk)) for s in strata)
    negative = prod((1 - Fraction(str(prevalence)) * Fraction(str(s.relative_risk))
                     / mean_risk * Fraction(str(s.method_sensitivity))) ** s.inspection_units for s in strata)
    return 1 - negative >= Fraction(str(confidence))


def two_stage_binomial_confidence(*, units_inspected: int, unit_prevalence: float,
                                  plants_per_unit: int, within_unit_prevalence: float,
                                  plant_method_sensitivity: float,
                                  homogeneous_unit_design_established: bool) -> float:
    """EN-1873 composition for the same qualified within-unit design in each unit.

    Heterogeneous unit designs must be represented as separate justified strata;
    an average sensitivity cannot silently stand in for the joint design.
    """
    if not homogeneous_unit_design_established:
        raise MissingInput("qualified within-unit detection sensitivity for each epidemiological-unit stratum")
    unit_sensitivity = binomial_confidence(plants_per_unit, within_unit_prevalence, plant_method_sensitivity)
    return binomial_confidence(units_inspected, unit_prevalence, unit_sensitivity)


def two_stage_independent_confidence(within_unit_confidences: tuple[float, ...],
                                     unit_prevalence: float, *,
                                     independence_established: bool) -> float:
    """Different achieved sensitivities in independently sampled outer units.

    Each supplied confidence is calculated for that unit's within-unit design,
    conditional on infection at its operative design prevalence. Units here
    share the same outer prevalence/risk stratum. No averaging or pooling of
    their plant counts replaces the distinct within-unit calculations.
    """
    probability(unit_prevalence)
    if not within_unit_confidences:
        return 0.0
    if not independence_established:
        raise MissingInput("joint model for the sampled epidemiological units")
    probabilities = [unit_prevalence * probability(c) for c in within_unit_confidences]
    if any(p == 1 for p in probabilities):
        return 1.0
    return -expm1(sum(log1p(-p) for p in probabilities))


def binomial_design_adequacy(snapshot: Snapshot, parameter: str, at,
                             strata: tuple[BinomialStratum, ...], *,
                             population_and_method_qualification: Evaluation,
                             required_risk_structure: Evaluation,
                             independence_established: bool) -> Evaluation:
    """Design assurance, not an assertion that the survey was performed or pest absent."""
    qualifications = conjunction([population_and_method_qualification, required_risk_structure])
    if qualifications.truth is False:
        return qualifications
    target, prevalence = design_targets(snapshot.quantity(parameter, at))
    try:
        sufficient = stratified_binomial_meets(float(prevalence), strata, float(target),
                                               independence_established=independence_established)
    except MissingInput as error:
        return conjunction([qualifications, Evaluation(None, needs=frozenset({str(error)}))])
    return conjunction([qualifications, Evaluation(sufficient)])


def survey_design_adequacy(snapshot: Snapshot, parameter: str, at: date,
                           strata: tuple[BinomialStratum | FiniteStratum, ...], *,
                           population_and_method_qualification: Evaluation,
                           required_risk_structure: Evaluation,
                           independence_established: bool) -> Evaluation:
    """Evaluate the qualified operative population model against this B target."""
    if strata and all(isinstance(s, BinomialStratum) for s in strata):
        return binomial_design_adequacy(snapshot, parameter, at, strata,
            population_and_method_qualification=population_and_method_qualification,
            required_risk_structure=required_risk_structure,
            independence_established=independence_established)
    qualifications = conjunction([population_and_method_qualification, required_risk_structure])
    if qualifications.truth is False:
        return qualifications
    target, prevalence = design_targets(snapshot.quantity(parameter, at))
    try:
        sufficient = stratified_finite_meets(prevalence, strata, float(target),
                                             independence_established=independence_established)
    except MissingInput as error:
        return conjunction([qualifications, Evaluation(None, needs=frozenset({str(error)}))])
    return conjunction([qualifications, Evaluation(sufficient)])


def negative_survey_support(adequacy: Evaluation, *, confirmed_positive_units: int,
                            required_performances_complete: Evaluation,
                            official_method_and_scope: Evaluation) -> Evaluation:
    if type(confirmed_positive_units) is not int or confirmed_positive_units < 0:
        raise ValueError("Nonnegative positive-unit count required")
    # Adequacy here must be recomputed using completed, usable observations.
    # An unprocessed or undetermined sample contributes no negative observation.
    return conjunction([adequacy, Evaluation(confirmed_positive_units == 0),
                        required_performances_complete, official_method_and_scope])


def observed_binomial_support(snapshot: Snapshot, parameter: str, at: date, *,
                               proportions: tuple[float, ...], relative_risks: tuple[float, ...],
                               method_sensitivities: tuple[float, ...],
                               negative_units: tuple[frozenset[str], ...],
                               positive_units: frozenset[str],
                               observation_inventory_complete: bool,
                               population_and_method_qualification: Evaluation,
                               required_risk_structure: Evaluation,
                               required_performances_complete: Evaluation,
                               official_method_and_scope: Evaluation,
                               independence_established: bool) -> Evaluation:
    """Recompute negative-survey support from distinct usable inspection units.

    Input identities concern the inspection unit selected by the operative
    design, not assays, aliquots or photographs. Each negative set contains only
    completed usable negative observations in one disjoint stratum. Unprocessed
    and undetermined samples contribute no unit. Positive units concern the
    same required scope and observation period.
    """
    if not positive_units and observation_inventory_complete and (not negative_units or len({len(proportions), len(relative_risks), len(method_sensitivities), len(negative_units)}) != 1):
        raise ValueError("One risk, sensitivity and negative-unit set per stratum required")
    strata = tuple(BinomialStratum(q, r, sensitivity, 0)
                   for q, r, sensitivity in zip(proportions, relative_risks, method_sensitivities))
    return observed_survey_support(snapshot, parameter, at, strata=strata, negative_units=negative_units,
        positive_units=positive_units, observation_inventory_complete=observation_inventory_complete,
        population_and_method_qualification=population_and_method_qualification,
        required_risk_structure=required_risk_structure, required_performances_complete=required_performances_complete,
        official_method_and_scope=official_method_and_scope, independence_established=independence_established)


def observed_survey_support(snapshot: Snapshot, parameter: str, at: date, *,
                            strata: tuple[BinomialStratum | FiniteStratum, ...],
                            negative_units: tuple[frozenset[str], ...], positive_units: frozenset[str],
                            observation_inventory_complete: bool,
                            population_and_method_qualification: Evaluation,
                            required_risk_structure: Evaluation,
                            required_performances_complete: Evaluation,
                            official_method_and_scope: Evaluation,
                            independence_established: bool) -> Evaluation:
    """Count usable inspection identities; disregard any planned counts in strata."""
    if not isinstance(positive_units, frozenset) or type(observation_inventory_complete) is not bool:
        raise TypeError("Explicit positive-unit set and observation completeness required")
    if positive_units:
        return Evaluation(False)
    if not observation_inventory_complete:
        return conjunction([population_and_method_qualification, required_risk_structure,
            required_performances_complete, official_method_and_scope,
            Evaluation(None, needs=frozenset({"complete usable observation inventory for the negative-survey conclusion"}))])
    if not negative_units or len(strata) != len(negative_units):
        raise ValueError("One risk, sensitivity and negative-unit set per stratum required")
    if any(not isinstance(units, frozenset) for units in negative_units):
        raise TypeError("Distinct inspection-unit sets required")
    seen = set()
    for units in negative_units:
        if seen & units:
            raise ValueError("One inspection unit cannot be counted in multiple disjoint strata")
        seen.update(units)
    strata = tuple(replace(s, inspection_units=len(units)) for s,units in zip(strata,negative_units))
    adequacy = survey_design_adequacy(snapshot, parameter, at, strata,
                population_and_method_qualification=population_and_method_qualification,
                required_risk_structure=required_risk_structure,
                independence_established=independence_established)
    return negative_survey_support(adequacy, confirmed_positive_units=0,
                required_performances_complete=required_performances_complete,
                official_method_and_scope=official_method_and_scope)


def two_stage_finite_confidence(*, outer_population: int, outer_infected: int,
                                units_inspected: int, inner_population: int, inner_infected: int,
                                plants_per_unit: int, plant_method_sensitivity: float,
                                homogeneous_unit_design_established: bool) -> float:
    """Achieved within-unit confidence is the outer-stage sensitivity."""
    if not homogeneous_unit_design_established:
        raise MissingInput("qualified common within-unit design for the finite outer population")
    inner = finite_confidence(inner_population, inner_infected, plants_per_unit, plant_method_sensitivity)
    return finite_confidence(outer_population, outer_infected, units_inspected, inner)


def negative_recurrence_support(periods: tuple[tuple[date, date], ...],
                                 performances: Mapping[str, tuple[date, Evaluation]], *,
                                 required_occurrences: int, records_complete: bool,
                                 evaluated_on: date,
                                 period_population_complete: Evaluation,
                                 no_detection_in_required_scope: Evaluation) -> Evaluation:
    """Combine cadence with the actual negative support of each survey occasion.

    Keys identify distinct performances of the required survey/test occasion,
    not samples within one occasion. Periods follow the operative annual cycle
    or biological season. D must establish the complete required period set.
    """
    if not periods or any(type(a) is not date or type(b) is not date or a >= b for a, b in periods):
        raise ValueError("Nonempty operative date periods required")
    if type(required_occurrences) is not int or required_occurrences < 1:
        raise ValueError("Positive required occasion count required")
    if type(evaluated_on) is not date or any(type(day) is not date or day > evaluated_on for day, _ in performances.values()):
        raise ValueError("Completed survey occasions must not lie after evaluation")
    conclusions = [period_population_complete, no_detection_in_required_scope]
    for start, end in periods:
        candidates = [support for day, support in performances.values() if start <= day < end]
        proven = sum(c.truth is True for c in candidates)
        possible = [c for c in candidates if c.truth is None]
        if proven >= required_occurrences:
            conclusions.append(Evaluation(True))
        elif records_complete and evaluated_on >= end and proven + len(possible) < required_occurrences:
            conclusions.append(Evaluation(False))
        else:
            needs = frozenset().union(*(c.needs for c in possible))
            if not records_complete:
                needs |= {f"qualifying survey occasions during {start} to {end} (exclusive)"}
            if evaluated_on < end:
                needs |= {f"required survey occasions in the still-open period ending {end} (exclusive)"}
            conclusions.append(Evaluation(None, needs=needs))
    return conjunction(conclusions)


def finite_confidence(population: int, infected: int, inspected: int, sensitivity: float) -> float:
    """Exact hypergeometric model, evaluated numerically (no finite-population approximation).

    Fixed infected count, uniform sampling without replacement, independent
    detection conditional on an infected inspection unit, and specificity 1.
    Conversion of design prevalence to an integer count is a separate method
    binding; this function does not silently choose a rounding convention.
    """
    if any(type(v) is not int for v in (population, infected, inspected)) or not 0 <= infected <= population or not 0 <= inspected <= population or population < 1:
        raise ValueError("Invalid finite population, infected count or inspection count")
    probability(sensitivity)
    if not infected or not inspected or sensitivity == 0:
        return 0.0
    low, high = max(0, inspected - (population - infected)), min(inspected, infected)
    k = np.arange(low, high + 1)
    # Relative PMF weights avoid subtracting large log-factorials. That
    # cancellation can change a minimum integer sample even with very few
    # infected units. Normalize the adjacent-probability ratios about the mode.
    mode = min(high, max(low, (inspected + 1) * (infected + 1) // (population + 2))) - low
    adjacent = k[:-1]
    ratios = (np.log(infected - adjacent) + np.log(inspected - adjacent)
              - np.log(adjacent + 1) - np.log(population - infected - inspected + adjacent + 1))
    weights = np.zeros(len(k))
    weights[mode + 1:] = np.cumsum(ratios[mode:])
    weights[:mode] = -np.cumsum(ratios[:mode][::-1])[::-1]
    normalizer = logsumexp(weights)
    if sensitivity == 1:
        log_negative = weights[0] - normalizer if low == 0 else -np.inf
    else:
        log_negative = logsumexp(weights + k * log1p(-sensitivity)) - normalizer
    return float(-np.expm1(min(0.0, log_negative)))


def finite_meets(population: int, infected: int, inspected: int, sensitivity: float, confidence: float) -> bool:
    probability(confidence)
    observed = finite_confidence(population, infected, inspected, sensitivity)
    if abs(observed - confidence) > 1e-10:
        return observed >= confidence
    # Compare exact rational probabilities near the boundary. Merely increasing
    # floating precision can still classify exact equality on the wrong side.
    s, target = Fraction(str(sensitivity)), Fraction(str(confidence))
    # Hypergeometric symmetry keeps the exact denominator small when a very
    # large population contains only a few infected units.
    infected, inspected = max(infected, inspected), min(infected, inspected)
    low, high = max(0, inspected - (population - infected)), min(inspected, infected)
    denominator = comb(population, inspected) * s.denominator ** high
    negative = sum(comb(infected, k) * comb(population - infected, inspected - k)
                   * (s.denominator - s.numerator) ** k * s.denominator ** (high - k)
                   for k in range(low, high + 1))
    return (denominator - negative) * target.denominator >= target.numerator * denominator


def finite_sample_size(population: int, infected: int, sensitivity: float, confidence: float) -> int:
    probability(confidence, positive=True)
    if not finite_meets(population, infected, population, sensitivity, confidence):
        raise ValueError("Requested confidence is unattainable even by inspecting the whole population under this method")
    low, high = 0, population
    while low < high:
        middle = (low + high) // 2
        if finite_meets(population, infected, middle, sensitivity, confidence):
            high = middle
        else:
            low = middle + 1
    return low
