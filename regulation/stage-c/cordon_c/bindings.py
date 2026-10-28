"""Explicit mathematical bindings into A's semantic predicate inputs.

The returned mapping is consumed directly by core.evaluate. Quantities are read
from B at the legal event date. Qualitative facts retain their A identity; D will
bind those facts and the typed mathematical inputs to evidence.
"""

from datetime import date, datetime, time, timedelta
from collections.abc import Mapping
from decimal import Decimal

from .core import Evaluation, MissingInput, Snapshot, evaluate, _leaves, negation, disjunction, predicate_value
from .diagnostic import AssayResult, analytical_predicates
from .quantities import scalar, clock_boundary, PeriodRule, timely_completion, clock_ordering, continuous_duration_support, _local_day
from .quantities import compare_scalar
from .temporal import elapsed_hours, end_of_day, utc, WorkingCalendar, occurrence_in_window
from .core import conjunction
from zoneinfo import ZoneInfo
from .spatial import MetricGeometry, adopted_membership, partial_parcel, distance_test, population_coverage
from .survey import BinomialStratum, FiniteStratum, survey_design_adequacy
from .survey import negative_recurrence_support
from .spatial import minimum_enclosure
from .quantities import metres


def leaves(ast: dict):
    return _leaves(ast)


def bind(row: dict, values: Mapping[str, bool | Evaluation]) -> dict[tuple[str, str], bool | Evaluation]:
    admitted = set(leaves(row["condition_ast"]))
    result = {(row["provision_version_id"], text): value for text, value in values.items() if text in admitted}
    if not result:
        raise ValueError(f"Calculation has no matching predicate in {row['provision_version_id']}")
    return result


def assay_facts(snapshot: Snapshot, identity: str, at: date, result: AssayResult) -> dict:
    row = snapshot.version(identity, at)
    parameters = [p for p in snapshot.parameters.values()
                  if p["consumer_decision"] == row["stable_provision_id"] and p["unit"] == "Cq"]
    lower = [p for p in parameters if p["comparator"] == "<"]
    upper = [p for p in parameters if p["comparator"] == ">"]
    if len(lower) != 1 or len(upper) > 1:
        raise ValueError("Selected analytical route has no unique Cq boundary binding")
    return bind(row, analytical_predicates(result, scalar(snapshot, lower[0]["parameter_id"], at),
                                          scalar(snapshot, upper[0]["parameter_id"], at) if upper else None))


def wait_facts(snapshot: Snapshot, identity: str, at: date, *,
               treatment_completed: datetime | None, evaluated_at: datetime) -> dict:
    row = snapshot.version(identity, at)
    clocks = [c for c in snapshot.clocks.values() if c["consumer_decision"] == row["stable_provision_id"] and c["kind"] == "not_before"]
    if len(clocks) != 1:
        raise ValueError("Selected treatment route has no unique waiting-period binding")
    clock = snapshot.quantity(clocks[0]["clock_id"], at)
    if clock["unit"] != "hours":
        raise ValueError("Waiting-period unit changed")
    completed = treatment_completed is not None
    reached = completed and utc(evaluated_at) >= utc(elapsed_hours(treatment_completed, int(clock["magnitude"])))
    return bind(row, {
        "regional 48-hour wait completed": reached if completed else Evaluation(None, needs=frozenset({"treatment completion time"})),
        "48-hour wait evidence missing": not completed,
        "evidence proves 48-hour wait not satisfied": completed and not reached,
    })


def adopted_area_facts(snapshot: Snapshot, identity: str, at: date,
                       point: MetricGeometry, area: MetricGeometry) -> dict:
    row = snapshot.version(identity, at)
    membership = (adopted_membership(point, area) if point.geometry.geom_type == "Point"
                  else partial_parcel(point, area))
    return bind(row, {"the point or parcel lies within the geography adopted by this act and its annexes": membership})


def merge_facts(*mappings: Mapping) -> dict:
    """Reject contradictory derivations instead of allowing last-writer precedence."""
    merged = {}
    for mapping in mappings:
        for key, value in mapping.items():
            if key in merged and merged[key] != value:
                raise ValueError(f"Conflicting semantic inputs: {key}")
            merged[key] = value
    return merged


def _precedes(first: date | datetime, second: date | datetime, zone: ZoneInfo) -> bool:
    """Earlier instant, or earlier local day when either side is a printed date."""
    if isinstance(first, datetime) and isinstance(second, datetime):
        return utc(first) < utc(second)
    return _local_day(first, zone) < _local_day(second, zone)


def custody_facts(snapshot: Snapshot, identity: str, at: date, *,
                  collected_at: date | datetime, delivered_at: date | datetime | None,
                  evaluated_at: datetime, delivery_records_complete: bool,
                  refrigerated_transport: Evaluation, other_mandatory_failure: Evaluation,
                  zone: ZoneInfo) -> dict:
    row = snapshot.version(identity, at)
    clocks = [c for c in snapshot.clocks.values()
              if snapshot.versions[c["producer_provision_version_id"]]["stable_provision_id"] == row["stable_provision_id"]
              and c["kind"] == "same_calendar_day"]
    if len(clocks) != 1:
        raise ValueError("Custody route has no unique same-day clock")
    if delivered_at is not None and _precedes(delivered_at, collected_at, zone):
        raise ValueError("Delivery cannot precede collection of this sample")
    timing = timely_completion(snapshot, clocks[0]["clock_id"], at,
        anchor=collected_at, completed_at=delivered_at, evaluated_at=evaluated_at,
        completion_history_complete=delivery_records_complete, zone=zone)
    transport = conjunction([timing, refrigerated_transport])
    return bind(row, {
        "same-day delivery and refrigerated transport": transport,
        "same-day delivery in refrigerated transport": transport,
        "evidence proves a mandatory source custody condition failed":
            disjunction([negation(transport), other_mandatory_failure]),
    })


def _same_identity(first: str | None, second: str | None, meaning: str) -> Evaluation:
    if first is None or second is None:
        return Evaluation(None, needs=frozenset({meaning}))
    if not first or not second:
        raise ValueError("Identity must be present or explicitly unavailable")
    return Evaluation(first == second)


def confirmation_facts(snapshot: Snapshot, at: date, *,
                       first_positive_annex_iv: Evaluation, second_positive_annex_iv: Evaluation,
                       first_test: str | None, second_test: str | None,
                       first_sample: str | None, second_sample: str | None,
                       first_extract: str | None, second_extract: str | None,
                       same_extract_route_appropriate: Evaluation,
                       first_genome_target: str | None, second_genome_target: str | None,
                       inside_demarcated_area: Evaluation) -> dict:
    """Compute identity and scope conditions of Article 2(6).

    Inputs are already qualified results and resolved identities, not raw assay
    records or a protocol. A method name is not a genome-target identity. The
    resulting Article 2(6) conclusion still enters the separate national
    official-confirmation and laboratory-authority conditions in A.
    """
    row = snapshot.version("EU-2020-1201:2(6)", at)
    distinct_test = negation(_same_identity(first_test, second_test, "distinct confirmation-test identities"))
    same_origin = disjunction([
        _same_identity(first_sample, second_sample, "plant-sample identities"),
        conjunction([same_extract_route_appropriate,
            _same_identity(first_extract, second_extract, "plant-extract identities")]),
    ])
    target = negation(_same_identity(first_genome_target, second_genome_target, "resolved genome-target identities"))
    return bind(row, {
        "positive Annex IV molecular test": first_positive_annex_iv,
        "second positive Annex IV molecular test on the same plant sample or, where appropriate, the same plant extract":
            conjunction([second_positive_annex_iv, distinct_test, same_origin]),
        "different genome target": target,
        "area inside a demarcated area": inside_demarcated_area,
        "area outside demarcated areas": negation(inside_demarcated_area),
    })


def eradication_species_facts(snapshot: Snapshot, at: date, *,
                               plant_species: str | None, finding_species: str | None,
                               species_found_infected_elsewhere: frozenset[str],
                               infected_species_inventory_complete: bool,
                               specified_plant: Evaluation) -> dict:
    """Classify points (c), (d) and the residual specified-plant population.

    The comparison concerns the same operative infected-zone/removal context;
    the elsewhere-infected species inventory is for its demarcated area. A
    missing species identity or incomplete inventory is not an uninfected
    species. Points (a)/(b), testing, retention and actual removal stay separate.
    """
    same = _same_identity(plant_species, finding_species, "plant and finding species identities")
    if plant_species is None:
        elsewhere = Evaluation(None, needs=frozenset({"plant species identity"}))
    elif plant_species in species_found_infected_elsewhere:
        elsewhere = Evaluation(True)
    elif infected_species_inventory_complete:
        elsewhere = Evaluation(False)
    else:
        elsewhere = Evaluation(None, needs=frozenset({"species found infected elsewhere in this demarcated area"}))
    other = conjunction([negation(same), elsewhere])
    residual = conjunction([specified_plant, negation(same), negation(other)])
    return merge_facts(
        bind(snapshot.version("EU-2020-1201:7(1)(c)", at),
             {"plants of the same species as the infected plant, whatever their health": same}),
        bind(snapshot.version("EU-2020-1201:7(1)(d)", at),
             {"plants of other species found infected elsewhere in the demarcated area": other}),
        bind(snapshot.version("EU-2020-1201:7(1)(e)", at),
             {"specified plants other than points (c) and (d)": residual}),
    )


def early_lifting_survey_facts(snapshot: Snapshot, at: date, *,
                               tests_completed: datetime | None, intended_lifting: datetime,
                               evaluated_at: datetime, tests_close_as_practicable: bool | None,
                               strata: tuple[BinomialStratum | FiniteStratum, ...],
                               population_and_method_qualification: Evaluation,
                               required_risk_structure: Evaluation,
                               performed_test_support: Evaluation,
                               independence_established: bool) -> dict:
    """Combine the computed survey basis with its own completion and ordering.

    The explicitly qualified operative design is recomputed against this
    provision's own B target. Counts concern completed usable inspections in
    the same demarcated area. Practical proximity is a qualified input, not a made-up
    number of days. The intended decision may be prospective.
    """
    row = snapshot.version("EU-2020-1201:6(2)(b)", at)
    assurance = survey_design_adequacy(snapshot, "B-PAR-EU-6(2)(b)-C95-p1", at, strata,
        population_and_method_qualification=population_and_method_qualification,
        required_risk_structure=required_risk_structure,
        independence_established=independence_established)
    if tests_completed is None:
        timing = Evaluation(None, needs=frozenset({"completed qualifying pre-lifting tests"}))
    else:
        if utc(tests_completed) > utc(evaluated_at):
            raise ValueError("Completed tests cannot follow evaluation")
        try:
            timing = Evaluation(clock_ordering(snapshot, "B-CLK-EU-6(2)(b)-tests-close-to-lifting", at,
                tests_completed, intended_lifting, as_close_as_practicable=tests_close_as_practicable))
        except MissingInput as error:
            timing = Evaluation(None, needs=frozenset({str(error)}))
    return bind(row, {"official tests within the area as close to the lifting as practicable, under a survey design and sampling scheme able to identify with at least 95 % confidence a 1 % level of presence of infected plants":
                      conjunction([assurance, performed_test_support, timing])})


def continuing_conditions_facts(snapshot: Snapshot, identity: str, at: date, *,
                                 basis_at: date, facts=None, reader=None, performances=None,
                                 historical_results=None) -> dict:
    """Evaluate explicit compound cross-references that A retains in a leaf.

    basis_at is the legal event time for the referenced requirements. An older
    act's original basis is not silently re-tested under today's amended law.
    This computes conditions; it does not establish an act's operative validity.
    """
    row = snapshot.version(identity, at)
    bindings = {
        "all Article 5(1)(a)–(d) conditions established":
            tuple(f"EU-2020-1201:5(1)({letter})" for letter in "abcd"),
        "continuing Article 7(3) conditions": ("EU-2020-1201:7(3)(a)", "EU-2020-1201:7(3)(b)"),
    }
    values = {}
    for predicate in set(leaves(row["condition_ast"])) & bindings.keys():
        values[predicate] = conjunction([evaluate(snapshot, reference, basis_at,
            facts=facts, reader=reader, performances=performances) for reference in bindings[predicate]])
    lifting = "complete Article 6(2) evidence established"
    if lifting in set(leaves(row["condition_ast"])):
        reduction = snapshot.historical_result("EU-2020-1201:6(2)", "EU-2020-1201:5(1)",
            basis_at, historical_results or {})
        reduced = Evaluation(None if reduction.effect is None else reduction.effect == "BUFFER_ZONE_REDUCED",
                             needs=reduction.needs, provisions=reduction.provisions)
        elapsed = predicate_value(snapshot.version("EU-2020-1201:6(2)", basis_at),
            "12 months from initial establishment", facts or {}, reader)
        values[lifting] = conjunction([reduced, elapsed, *[
            evaluate(snapshot, reference, basis_at, facts=facts, reader=reader, performances=performances)
            for reference in ("EU-2020-1201:6(2)(a)", "EU-2020-1201:6(2)(b)")]])
    return bind(row, values)


def reduced_buffer_survey_facts(snapshot: Snapshot, at: date, strata: tuple[BinomialStratum | FiniteStratum, ...], *,
                                population_and_method_qualification: Evaluation,
                                required_risk_structure: Evaluation,
                                independence_established: bool) -> dict:
    row = snapshot.version("EU-2020-1201:5(1)(c)", at)
    value = survey_design_adequacy(snapshot, "B-PAR-EU-5(1)(c)-v2-C90-p1", at, strata,
                                    population_and_method_qualification=population_and_method_qualification,
                                    required_risk_structure=required_risk_structure,
                                    independence_established=independence_established)
    return bind(row, {"survey design and sampling scheme able to identify with at least 90 % confidence a level of presence of infected plants of 1 %, the first 400 m surrounding the infected plants at higher risk": value})


def reduced_buffer_removal_facts(snapshot: Snapshot, at: date, *,
                                 required_specified_plants: Mapping[str, Evaluation],
                                 sampled_plants: frozenset[str], removed_plants: frozenset[str],
                                 required_population_complete: bool,
                                 sampling_records_complete: bool, removal_records_complete: bool,
                                 immediacy: Evaluation) -> dict:
    """Both required performances cover the same specified-plant population.

    Membership is in the operative infected zone, regardless of plant health.
    Immediacy is the source's qualified timing assessment, not an invented grace
    period. The sampling condition does not add a separate testing requirement.
    """
    row = snapshot.version("EU-2020-1201:5(1)(a)", at)
    sampling = population_coverage(required_specified_plants, sampled_plants,
                required_population_complete=required_population_complete,
                completion_records_complete=sampling_records_complete)
    removal = population_coverage(required_specified_plants, removed_plants,
                required_population_complete=required_population_complete,
                completion_records_complete=removal_records_complete)
    return bind(row, {"all specified plants in the infected zone, whatever their health, immediately sampled and removed":
                      conjunction([sampling, removal, immediacy])})


def early_lifting_period_facts(snapshot: Snapshot, at: date, established: date, evaluated_at: datetime, *,
                               zone: ZoneInfo, rule: PeriodRule | None = None, calendar: WorkingCalendar | None = None) -> dict:
    row = snapshot.version("EU-2020-1201:6(2)", at)
    boundary = clock_boundary(snapshot, "B-CLK-EU-6(2)-v1-early-lift-12-months", at,
                              established, zone=zone, calendar=calendar, rule=rule)
    return bind(row, {"12 months from initial establishment": utc(evaluated_at) >= utc(boundary)})


def four_year_lifting_facts(snapshot: Snapshot, at: date, established: date,
                           detections: tuple[date, ...], evaluated_at: datetime, *,
                           detection_history_complete: bool,
                           article10_survey_basis: Evaluation,
                           zone: ZoneInfo, rule: PeriodRule | None = None, calendar: WorkingCalendar | None = None) -> dict:
    row = snapshot.version("EU-2020-1201:6(1)", at)
    # Known recent detection disproves four negative years even if other records
    # are missing. Establishing the positive conclusion needs complete history.
    through = utc(evaluated_at).astimezone(zone).date()
    if through < established or any(d > through for d in detections):
        raise ValueError("Detection history and decision interval disagree")
    anchor = max((established, *detections))
    boundary = clock_boundary(snapshot, "B-CLK-EU-6(1)-four-negative-years", at, anchor,
                              zone=zone, calendar=calendar, rule=rule)
    reached = utc(evaluated_at) >= utc(boundary)
    if not reached:
        value = False
    else:
        complete = Evaluation(True) if detection_history_complete else Evaluation(None, needs=frozenset({"complete detection history"}))
        value = conjunction([complete, article10_survey_basis])
    return bind(row, {"pest not detected in the demarcated area for four years on the Article 10 surveys": value})


def noncommencement_facts(snapshot: Snapshot, clock_id: str, at: date, *,
                          notification: date | datetime | None, evaluated_at: datetime,
                          qualifying_commencements: Mapping[str, datetime],
                          commencement_records_complete: bool,
                          zone: ZoneInfo, rule: PeriodRule | None = None,
                          calendar: WorkingCalendar | None = None,
                          stated_term: tuple[str, str] | None = None) -> dict:
    """Only the temporal components of the case-qualified enforcement condition.

    The period is the prescription's own stated term (number, printed unit
    word); without it the deadline is unknown. Without a notification day or
    instant there is no deadline: both components stay unknown.
    Whether notification is legally sufficient, work identity and lawful
    prescription remain A's conditions. The performances must concern this
    exact work. Commencement before notice also defeats noncommencement; no
    second commencement is demanded.
    """
    clock = snapshot.quantity(clock_id, at)
    row = snapshot.version(clock["consumer_decision"], at)
    required = {"the source notification-based commencement deadline has elapsed",
                "noncommencement of that work by the source deadline is established"}
    if not required <= set(leaves(row["condition_ast"])):
        raise ValueError("Clock does not feed the case noncommencement condition")
    if notification is None:
        unknown = Evaluation(None, needs=frozenset({"legally sufficient notification of the prescription to this recipient"}))
        return bind(row, dict.fromkeys(required, unknown))
    end = clock_boundary(snapshot, clock_id, at, notification, zone=zone, rule=rule, calendar=calendar,
                         stated_term=stated_term)
    through = utc(evaluated_at)
    if any(utc(t) > through for t in qualifying_commencements.values()):
        raise ValueError("Performance evidence is later than the evaluation time")
    elapsed = through >= utc(end)
    begun = any(utc(t) < utc(end) for t in qualifying_commencements.values())
    absent = (False if begun else True if elapsed and commencement_records_complete
              else Evaluation(None, needs=frozenset({"commencement evidence through the source deadline"})))
    return bind(row, {"the source notification-based commencement deadline has elapsed": elapsed,
                      "noncommencement of that work by the source deadline is established": absent})


def mass_publicity_facts(snapshot: Snapshot, at: date, *,
                         ground_stated: bool | Evaluation, annulled_on_ground: bool | Evaluation,
                         posting_start: date | datetime | None,
                         postings: Mapping[str, tuple[date | datetime, date | datetime | None]],
                         postings_complete: bool, stated_period: tuple[str, str] | None,
                         evaluated_at: datetime, zone: ZoneInfo) -> tuple[dict, date | None]:
    """Law 241/1990 Art. 21-bis mass publicity for one act, from its own text and posting records.

    ground_stated is whether the act states its own ground for public posting;
    stated_period is the posting period the act prints (number, unit word),
    never a plan's default. The period is a display duration: the posting must
    run continuously from its start through the end of the last of that many
    consecutive days, the first day of display included. A posting record given
    as dates is kept whole days: a start date is that day's start, and an end
    date (a certificate's inclusive "al 17/03") runs through that day's end.
    Returns the bound facts and the notice day, only when A's row gives
    effectiveness on those facts: the stated number of days counted from the
    day of publication, that day excluded ("decorso il settimo giorno dalla data
    di pubblicazione"). Otherwise no notification day, so no Art. 21-ter
    deadline can run from it.
    """
    identity = "IT-L241-A21BIS:Art.21-bis(1):mass-publicity-route"
    row = snapshot.version(identity, at)
    clocks = [c for c in snapshot.clocks.values()
              if c["consumer_decision"] == row["stable_provision_id"] and c["kind"] == "minimum_duration"]
    if len(clocks) != 1:
        raise ValueError("Mass-publicity route has no unique stated-period clock")

    def instant(value: date | datetime | None, *, end: bool) -> datetime | None:
        if value is None or isinstance(value, datetime):
            return value
        return end_of_day(value, zone) if end else datetime.combine(value, time(), zone)

    period = stated_period
    start = instant(posting_start, end=False)
    intervals = {name: (instant(first, end=False), instant(last, end=True)) for name, (first, last) in postings.items()}
    if start is None:
        completed = Evaluation(None, needs=frozenset({"start of the posting the act states"}))
        publication = None
    else:
        publication = utc(start).astimezone(zone).date()
        # Counting from the day before the first day includes the first day of display.
        completed = continuous_duration_support(snapshot, clocks[0]["clock_id"], at,
            anchor=publication - timedelta(days=1), required_start=start, intervals=intervals,
            evaluated_at=evaluated_at, records_complete=postings_complete, zone=zone, stated_term=period)
    facts = bind(row, {
        "the act states its own ground for reaching its recipients by public posting": ground_stated,
        "the publicity form the act states has been completed": completed,
        "a court has annulled the act on its stated ground for public posting": annulled_on_ground,
    })
    if evaluate(snapshot, identity, at, facts).effect != "ACT_EFFECTIVE_AGAINST_RECIPIENT":
        return facts, None
    end = clock_boundary(snapshot, clocks[0]["clock_id"], at, publication, zone=zone, stated_term=period)
    return facts, end.astimezone(zone).date() - timedelta(days=1)


def notice_instant(snapshot: Snapshot, identity: str, at: date, facts: Mapping, *,
                   instants: Mapping[str, date | datetime | None], zone: ZoneInfo) -> date | datetime | None:
    """The instant from which a consumer's notice-based term runs for one recipient.

    The consumer row holds one any_of of notice branches. A evaluates each
    branch on `facts`: a predicate branch by its own leaf, a provision_ref
    branch through the bound reference outcome. `instants` maps a branch (its
    predicate text or referenced stable id) to the instant its own events give
    this recipient. Returns the earliest instant among the branches A finds
    true, or none when no branch is true. A branch that is false or unknown
    never supplies its instant; a true branch must have one.
    """
    row = snapshot.version(identity, at)
    groups = []

    def walk(node):
        if isinstance(node, dict):
            if "any_of" in node:
                groups.append(node["any_of"])
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(row["condition_ast"])
    if len(groups) != 1:
        raise ValueError(f"{identity}: no single notice any_of")
    truths = {}
    for branch in groups[0]:
        if set(branch) == {"predicate"}:
            truths[branch["predicate"]] = predicate_value(row, branch["predicate"], facts).truth
        elif set(branch) == {"provision_ref"}:
            reference = branch["provision_ref"]
            outcomes = snapshot.reference_outcomes.get((row["stable_provision_id"], reference))
            if outcomes is None:
                raise ValueError(f"{identity}: notice branch {reference} has no bound outcomes")
            effect = evaluate(snapshot, reference, at, facts).effect
            truths[reference] = None if effect is None else outcomes[effect]
        else:
            raise ValueError(f"{identity}: unsupported notice branch {sorted(branch)}")
    if set(instants) - set(truths):
        raise ValueError(f"{identity}: an instant names no notice branch of this row")
    held = []
    for branch, truth in truths.items():
        if truth is True:
            if instants.get(branch) is None:
                raise ValueError(f"{identity}: branch A finds true has no instant: {branch}")
            held.append(instants[branch])
    if not held:
        return None
    return min(held, key=lambda value: utc(value) if isinstance(value, datetime)
               else utc(datetime.combine(value, time(), zone)))


def trunk_diameter_facts(snapshot: Snapshot, at: date, *, diameter_cm: Decimal | None,
                         measured_height_cm: Decimal | None) -> dict:
    """L.R. Puglia 14/2007 Art. 2(1)(a) from the trunk diameter a plant's official record states.

    diameter_cm is the recorded diameter (for a fragmented trunk, of the
    reconstructed whole trunk). measured_height_cm is the height the record
    states for it, or None when it states none, which A reads as the
    criterion's own height. A diameter taken at another height is not this
    measure and leaves the criterion unknown.
    """
    identity = "PUG-LR14-2007:Art.2(1)(a):trunk-diameter-criterion"
    row = snapshot.version(identity, at)
    parameters = {p["kind"]: p["parameter_id"] for p in snapshot.parameters.values()
                  if p["consumer_decision"] == row["stable_provision_id"] and p["unit"] == "cm"}
    if set(parameters) != {"floor", "exact"}:
        raise ValueError("Article 2(1)(a) has no unique diameter floor and measurement height")
    height = scalar(snapshot, parameters["exact"], at)
    if diameter_cm is None:
        value = Evaluation(None, needs=frozenset({"the trunk diameter the plant's official record states"}))
    elif measured_height_cm is not None and measured_height_cm != height:
        value = Evaluation(None, needs=frozenset({f"the trunk diameter measured {height} cm above the ground"}))
    else:
        value = Evaluation(compare_scalar(snapshot, parameters["floor"], at, diameter_cm))
    return bind(row, {"the trunk diameter the plant's official record states, measured 130 cm above the ground "
                      "(for a fragmented trunk, of the reconstructed whole trunk), is at least 100 cm": value})


def listing_facts(snapshot: Snapshot, at: date, *, own_entry: bool | None,
                  first_publication: date | None, definitive_decision: tuple[date, bool] | None,
                  deletion: date | None, entry_history_complete: bool) -> dict:
    """L.R. Puglia 14/2007 Art. 5 status of one tree at the event date `at`.

    own_entry is whether the tree has an entry of its own (a listed grove is
    not one). first_publication is the BURP date of the provisional list
    carrying the entry; definitive_decision is the BURP date of the Giunta's
    definitive decision on it and whether that decision approved the entry;
    deletion is the date of an act deleting it. An absent date is no such act
    only when the entry's act history is complete; otherwise it is unknown.
    """
    if first_publication and definitive_decision and definitive_decision[0] < first_publication:
        raise ValueError("A definitive decision cannot precede the entry's first publication")

    def dated(day: date | None, need: str) -> Evaluation:
        if day is not None:
            return Evaluation(day <= at)
        return Evaluation(False) if entry_history_complete else Evaluation(None, needs=frozenset({need}))

    own = Evaluation(None, needs=frozenset({"whether the tree has its own list entry"})) if own_entry is None \
        else Evaluation(own_entry)
    published = conjunction([own, dated(first_publication, "the entry's first BURP publication date")])
    if definitive_decision is None:
        decided = approved = dated(None, "the Giunta's definitive decision on the entry and its BURP publication date")
    else:
        day, approves = definitive_decision
        decided = Evaluation(day <= at)
        approved = Evaluation(day <= at and approves)
    return merge_facts(
        bind(snapshot.version("PUG-LR14-2007:Art.5(3):definitive-listing", at), {
            "the tree has its own entry in an Article 5 list": own,
            "the Giunta approved that entry definitively and the list containing it was republished on BURP on or before the event date": approved,
            "the entry was deleted from the list on or before the event date": dated(deletion, "the entry's deletion act and date"),
        }),
        bind(snapshot.version("PUG-LR14-2007:Art.5(2):provisional-listing-pending-recognition", at), {
            "the tree has its own entry in a list approved provisionally and published on BURP under Article 5(2) on or before the event date": published,
            "the Giunta's definitive decision on that entry was published on BURP on or before the event date": decided,
        }),
    )


def election_window_facts(snapshot: Snapshot, clock_id: str, consumer: str, at: date, *,
                           publication_end_day: date, first_valid_election_time: datetime,
                           evaluated_at: datetime, qualifying_elections: Mapping[str, datetime],
                           election_records_complete: bool,
                           zone: ZoneInfo, rule: PeriodRule | None = None,
                           calendar: WorkingCalendar | None = None) -> dict:
    """The end-of-publication date anchors the upper bound, not the opening.

    A valid early election is allowed by the accepted regional meaning. The
    caller supplies the earliest valid time for this recipient and prescription.
    Executor identity and the other validity requirements stay factual inputs.
    """
    row = snapshot.version(consumer, at)
    if clock_id not in {"B-CLK-DGR538-owner-election", "B-CLK-DGR343-owner-election",
                        "B-CLK-DGR1866-owner-election", "B-CLK-DGR1593-owner-election",
                        "B-CLK-DGR1075-owner-election"}:
        raise ValueError("An accepted owner-election clock is required")
    clock = snapshot.quantity(clock_id, at)
    producer = snapshot.versions[clock["producer_provision_version_id"]]
    if producer["instrument_id"] != row["instrument_id"]:
        raise ValueError("The election window and its consumer belong to different plans")
    end = clock_boundary(snapshot, clock_id, at, publication_end_day,
                         zone=zone, rule=rule, calendar=calendar)
    elapsed = utc(evaluated_at) >= utc(end)
    if any(utc(t) > utc(evaluated_at) for t in qualifying_elections.values()):
        raise ValueError("Election evidence is later than the evaluation time")
    try:
        occurred = occurrence_in_window(qualifying_elections, first_valid_election_time, end,
                                         records_complete=election_records_complete and elapsed)
        absence = not occurred
    except MissingInput as error:
        occurred = absence = Evaluation(None, needs=frozenset({str(error)}))
    return bind(row, {"owner communication within the source-stated window": occurred,
                      "evidenced absence of any owner communication within the source-stated window": absence,
                      "evidenced absence of any owner communication within the source-stated post-publication window": absence,
                      "completed election window": elapsed,
                      "affirmative no-response evidence": absence})


def sampling_lookback_facts(snapshot: Snapshot, at: date, *, evaluated_at: datetime,
                            qualifying_detections: Mapping[str, datetime], history_complete: bool,
                            zone: ZoneInfo) -> dict:
    identity = "EU-2020-1201:7(1)(e)-sub2"
    row = snapshot.version(identity, at)
    start = clock_boundary(snapshot, "B-CLK-EU-7(1)(e)-sub2-two-year-lookback", at,
                           evaluated_at, zone=zone)
    if any(utc(t) > utc(evaluated_at) for t in qualifying_detections.values()):
        raise ValueError("Detection lies after the evaluation time")
    found = any(utc(start) <= utc(t) <= utc(evaluated_at) for t in qualifying_detections.values())
    value = False if found else True if history_complete else Evaluation(None, needs=frozenset({"complete relevant cohort detection history"}))
    return bind(row, {"referenced plants/cohort not found infected in that demarcated area during prior two years": value})


def negative_recurrence_facts(snapshot: Snapshot, identity: str, at: date, *,
                              periods: tuple[tuple[date, date], ...],
                              performances: Mapping[str, tuple[date, Evaluation]],
                              evaluated_on: date,
                              records_complete: bool,
                              period_population_complete: Evaluation,
                              no_detection_in_required_scope: Evaluation,
                              natural_spread_excluded: Evaluation | None = None) -> dict:
    bindings = {
        "EU-2020-1201:5(1)(b)": ("B-CLK-EU-5(1)(b)-tests-once-a-year", "no other plants found infected in the infected zone since the measures were taken, on official tests at least once in the year"),
        "EU-2020-1201:5(1)(d)": ("B-CLK-EU-5(1)(d)-vector-tests-twice-in-flight-season", "no vectors carrying the pest detected in the infected zone or its immediate vicinity since the measures, on tests twice in the flight season, concluding natural spread is excluded"),
        "EU-2020-1201:7(3)(a)": ("B-CLK-EU-7(3)(a)-annual-retention-testing", "annual inspection, sampling and testing by an Annex IV test confirming the plant is not infected"),
    }
    clock_id, predicate = bindings[identity]
    row = snapshot.version(identity, at)
    clock = snapshot.quantity(clock_id, at)
    occurrences = clock["recurrence"]["occurrences_per_period"]
    result = negative_recurrence_support(periods, performances,
                evaluated_on=evaluated_on,
                required_occurrences=int(occurrences["count"]) if occurrences else 1,
                records_complete=records_complete, period_population_complete=period_population_complete,
                no_detection_in_required_scope=no_detection_in_required_scope)
    if identity == "EU-2020-1201:5(1)(d)":
        spread = (natural_spread_excluded if natural_spread_excluded is not None else
                  Evaluation(None, needs=frozenset({"operative conclusion excluding natural spread"})))
        result = conjunction([result, spread])
    return bind(row, {predicate: result})


def reduced_buffer_first_year_facts(snapshot: Snapshot, at: date, *,
                                    identification: datetime, evaluated_at: datetime,
                                    infected_zone: MetricGeometry, surveyed_enclosure: MetricGeometry,
                                    survey_completed: datetime | None,
                                    negative_survey_basis: Evaluation,
                                    host_sampling_and_testing: Evaluation,
                                    zone: ZoneInfo, calendar: WorkingCalendar) -> dict:
    """Surveyed enclosure is the infected zone plus its surveyed surroundings.

    Its shape tests outer extent; negative_survey_basis and host sampling apply
    to the source-required surrounding zone, not an invented inner-zone duty.
    """
    row = snapshot.version("EU-2020-1201:5(1)(c)", at)
    # The two accepted versions share the first-year/radius condition; the
    # current version adds its statistical/risk condition in a separate leaf.
    candidates = [c for c in snapshot.clocks.values()
                  if c["producer_provision_version_id"] == row["provision_version_id"] and c["kind"] == "deadline"]
    distances = [p for p in snapshot.parameters.values()
                 if p["producer_provision_version_id"] == row["provision_version_id"] and p["unit"] == "km"]
    if len(candidates) != 1 or len(distances) != 1:
        raise ValueError("First-year survey has no unique accepted clock and radius")
    end = clock_boundary(snapshot, candidates[0]["clock_id"], at, identification,
                         zone=zone, calendar=calendar)
    if survey_completed is None:
        timing = Evaluation(None, needs=frozenset({"qualifying first-year survey completion"}))
    else:
        if utc(survey_completed) > utc(evaluated_at):
            raise ValueError("Survey completion is later than evaluation")
        timing = Evaluation(utc(identification) <= utc(survey_completed) < utc(end))
    extent = minimum_enclosure(infected_zone, surveyed_enclosure,
                               float(metres(snapshot, distances[0]["parameter_id"], at)))
    return bind(row, {
        "a survey at least once in the first year, in a zone at least 2,5 km around the infected zone, showing the pest absent":
            conjunction([timing, extent, negative_survey_basis]),
        "host plants located in that zone sampled and tested": host_sampling_and_testing,
    })


def island_distance_facts(snapshot: Snapshot, at: date, island: MetricGeometry,
                          other_union_land: MetricGeometry, *,
                          other_union_land_complete: Evaluation) -> dict:
    row = snapshot.version("EU-2020-1201:15(3)", at)
    separation = distance_test(island, other_union_land,
                               float(metres(snapshot, "B-PAR-EU-15(3)-island-exemption-5km", at)), ">")
    return bind(row, {"distance to nearest Union land territory > 5 km":
                      conjunction([separation, other_union_land_complete])})


def pni_geography_facts(snapshot: Snapshot, at: date, point: MetricGeometry,
                        complete_demarcated_areas: MetricGeometry, *,
                        target_is_in_puglia_pest_free_area: Evaluation,
                        host_qualifications: Mapping[str, Evaluation]) -> dict:
    """Partition the four outdoor target populations by the operative PNI band.

    Qualifications concern the exact source-listed host/land-use populations;
    a point, cadastral class or distance alone cannot establish those facts.
    The separate authorized-production-site population is not classified here.
    """
    from .populations import exterior_band
    row = snapshot.version("IT-PNI-2026:Xylella:Puglia-plant-survey-design", at)
    radius = float(metres(snapshot, "B-PAR-PNI2026-pest-free-band-1km", at))
    high = exterior_band(point, complete_demarcated_areas, radius)
    medium = distance_test(point, complete_demarcated_areas, radius, ">")
    values = {}
    for population in ("Olea europaea in orchards or vineyards", "Prunus sp. or Citrus sp.",
                       "Vitis sp.", "the workbook-listed spontaneous-host vegetation"):
        qualification = host_qualifications.get(population, Evaluation(None, needs=frozenset({population + " qualification"})))
        values[f"target population is {population} in remaining Puglia pest-free areas"] = conjunction(
            [qualification, target_is_in_puglia_pest_free_area, medium])
        values[f"target population is {population} within the 1 km pest-free band around demarcated areas"] = conjunction(
            [qualification, target_is_in_puglia_pest_free_area, high])
    return bind(row, values)
