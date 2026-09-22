# Stage C computational reference

This package derives calculations for the Osservatorio's positive-finding-to-
removal chain from the accepted A/B owners. Its current status, acceptance and
next gate belong to [`CURRENT`](../../state/CURRENT.json). Execution evidence
and method adjudication are recorded in the
[dated derivation](../../corpus/evidence/stage-c-derivation-2026-09-08.md).
The regional survey additions have been accepted and promoted into the A/B
owners. `Snapshot.load()` consumes those owners normally. The original
[amendment snapshot](../../corpus/evidence/stage-c-regional-survey-amendment-2026-09-08.json)
is retained as dated evidence; its original proposal status describes the reviewed
snapshot. Acceptance, convergence and promotion are recorded in the
[acceptance record](../../corpus/evidence/stage-c-acceptance-2026-09-08.json).

## Contract

The canonical C owner is this package: the functions in `cordon_c`, their explicit
reference bindings, and this mathematical contract. A owns legal predicates and
effects. B owns quantities, units, anchors and dispositions. C reads them directly;
it neither copies legal thresholds into configuration nor derives meaning from
identifier spelling at runtime. `Snapshot.load()` checks the accepted input
hashes. Dates select half-open legal-version intervals. Unchanged adjacent legal
versions preserve a B quantity's applicability; a semantic change ends it.

The consumer is Stage D: typed mathematical inputs and A's remaining semantic
facts need evidence contracts. Inputs here describe the fact required, not its
database, acquisition route, source priority or record owner. E owns write
actions, F the necessary nouns and relationships, G their platform compilation.
These reference functions perform no network request, operational write or
implicit current-time lookup.

## Proposed prescription-clause amendment

The exact temporary [owner patch](../../corpus/workbench/prescription-clause-amendment.json)
is **not accepted**. It changes no accepted A/B file or acceptance record.
`test_prescription_candidate.py` checks the stated accepted A/B hashes and exact
affected D-owner bases. It expands the patch only into temporary files, verifies
A/B and the copied D owner graph, and constructs an explicit review `Snapshot`.
The review tree's A/B state is OPEN; ordinary `Snapshot.load()` rejects it.
The candidate includes removal/addition of factual and declared-evidence bindings
in the existing D owners, so proposed predicates must pass the ordinary Evidence
contract before they can reach the decision consumer. A qualified source clause
does not supply missing applicability, notice, lawfulness or performance facts.
Ordinary `Snapshot.load()` retains its accepted-owner hash gates.
The changed C package intentionally does not match the CLOSED C digest in
`CURRENT`; review checks are not acceptance. Promotion requires Owen's acceptance
of the exact reviewed content, updated acceptance bindings and deletion of the
temporary patch and its expansion harness.

`test_prescription_migration.py` preserves the retired registration tests'
substantive condition, source-bound serialization and correction-meaning demands
against the candidate. The C noncommencement regression uses an explicit source
fixture rather than a retired act ID. Actual differing-population and inherited
recipient/work/notice relationships still require their ordinary D source evidence;
these mechanism tests do not establish them.

In the proposed A content, statutory execution rules and the
`SOURCE-CLAUSE:notification-noncommencement-direction` interpretation have
different identities. The interpretation is explicitly typed, has no legislative
instrument identity, and names the original operative clauses that support the
understood form. It reuses the condition evaluator without presenting the
particular act's conditional command as the text of Article 21-quater. Each
instance remains responsible for its own operative clause, actual command,
recipient, commencement work, coercive population, executor and legal context.
An absent, recited, discretionary or materially different clause cannot supply
this interpretation's affirmative operative-form predicate.

The proposed B row binds `magnitude: {"source_input": "prescribed-term"}`
instead of registering a fixed number for each act. `PrescribedTerm` retains the
document, clause, recipient and **commencement work** identities, together with
a positive whole Decimal magnitude and its source-qualified unit. These identities
preserve context; they do not establish legal validity or correspondence to
notice/performance evidence. The coercive population is a distinct A/D input.
`bound: exact` fixes the stated maximum period's length; it does not require
commencement exactly on its last day. A missing period has no default.

`Snapshot.quantity`, `scalar`, `clock_boundary`, `timely_completion` and
`noncommencement_facts` accept this typed term only for that source-bound clock
shape. Resolution returns a fresh row and cannot replace a fixed quantity or
mutate the snapshot. The semantic form selects existing physical-execution
calendar conventions by unit: Sunday/public-holiday final-day extension for
calendar days/months/years, the existing working-day convention when expressly
stated, and exact elapsed hours. A caller cannot override this qualification
with `PeriodRule`. A different or unresolved counting form requires its own
source disposition. Missing commencement history remains unresolved; qualifying
earlier commencement defeats noncommencement. The result establishes neither
physical execution nor its separate procedural readiness.

The candidate retires the eighteen duplicated clock registrations and their
calendar assignments while retaining genuine correction, authority-conflict and
other execution routes. Different scope and inherited terms must survive through
the ordinary D source/relationship consumer before this amendment is complete.

To verify the proposed owners and arithmetic explicitly:

```sh
PYTHONPATH=regulation/stage-c .venv/bin/python -m unittest discover -s regulation/stage-c -p 'test_prescri*.py'
python3 -m unittest discover -s scripts -p test_prescribed_clock_schema.py
```

## Mathematical surface

| Requirement | Calculation and required semantic inputs |
|---|---|
| Applicability and legal routes | `core.evaluate`: event date, exact A-version predicate facts, and contextual reference facts. Three-valued conjunction/disjunction; `otherwise` follows proven failure, never mere missing evidence. A result is compared as the complete exact effect. Branch order supplies no precedence. |
| Referenced performance and outcome | `reference-bindings.json`: the small set of contextual edges where actual performance or a particular legal outcome is needed. A duty's applicability does not establish its performance. A matched “unavailable” branch does not satisfy the referenced proposition. All other edges preserve their accepted condition meaning. |
| Source quantities | `quantities`: explicit legal event date and B identity; Decimal conversion; metres/kilometres; exact comparator; month-window membership; planned sample/test differences. B's conditional/conflict classification remains in force regardless of the numerical answer. |
| Clocks | `temporal`, `quantities` and `calendar-rules.json`: qualified event date/instant, selected clock class, local zone and a bounded holiday calendar. Calendar months/years use anniversary dates with month-end clamping; elapsed hours use UTC duration. Whole-day periods expose the following midnight as an exclusive end. Fixed dates, recurrence counts, ordering, reset and lookback calculations stay distinct. |
| Open temporal terms | A biological interval, practicability determination or promptness standard receives its operative semantic input. C does not manufacture days from “immediately,” “periodic,” or vector biology. Before/during treatment uses actual phase performance, not a continuous-spraying interval. |
| Spatial predicates | `spatial`: valid 2D geometry, explicit compatible metric CRS, and spatial error bounds. Adopted-area membership includes its boundary; ambiguous precision affects only that classification. Radius/band membership uses distance directly. `minimum_enclosure` tests containment and clearance from every boundary, including holes; it does not establish legal geography. |
| Post-finding populations | `populations`: DDS45's two inner 50 m populations remain differently qualified; the containment outer band extends from 50 to 450 m; the pest-free/buffer outer width runs from the infected zone and covers the operative hectares containing specified species. No invented hectare grid or plant census. |
| Other spatial scope | The inward band uses the actual infected/buffer interface. PNI's outdoor populations use the exterior of the complete operative demarcation union; host/land-use qualifications remain distinct. Island separation uses the whole island and other Union land, including completeness of that land population. A partial-parcel relation does not expand infected-plant membership. Shared performance is counted by semantic identity; incomplete population or completion evidence is scoped to the unsatisfied claim. |
| Analytical classification | `diagnostic`, bound through `bindings.assay_facts`: selected assay, validity, Decimal Cq or explicit no-Cq. DDS31 and DDS45 retain different ranges; exact 32 and 35 follow their accepted unresolved boundaries. A numeric analytical class never creates official finding status. |
| Survey assurance | `survey`: full-method sensitivity, inspection-unit population, risk proportions and relative risks, qualified sampling/independence and sample counts. Binomial and finite hypergeometric kernels; minimum integer count; population weighting; stratum composition; integer allocation. Design adequacy, performed-survey support and planned workload are different conclusions. |
| Composition | `bindings` returns facts under the exact owning A version/wording for `evaluate`. It connects analytical classification, confirmation identities, custody, species populations, waiting periods, adopted geography, reduction/lifting survey conditions, recurring negative support, cohort lookback, election windows and case noncommencement. Regional compound references are evaluated from their underlying conditions at an explicit basis event date. Finite and binomial assurance use the same legal consumers. |

`Evaluation.truth` describes the evaluated condition or route match, not a
general success/permission flag. The exact `effect` owns a legal route's outcome.
Calling `bool(evaluation)` is rejected. Unknown inputs are not false. A false
conjunct or true disjunct resolves a conclusion despite irrelevant missing facts.
An explicit calculation with no matching A predicate is rejected. Election
timing uses the end-of-publication date as its upper-bound anchor while allowing
a valid earlier election. Case noncommencement uses concrete commencement of the
exact required work, including a commencement before notice. Neither elapsed
time nor an incomplete execution record proves noncommencement.
`timely_completion` compares this clock's own qualifying performance with its
boundary. Equality satisfies an elapsed-hour deadline; the following midnight
is outside a whole-day deadline. Missing performance evidence and a still-open
deadline remain distinguishable from proven late or omitted performance.

Explicit computed facts take precedence over the optional reader for remaining
semantic facts. Performance references accept computed `Evaluation` values, so
their scoped unknowns survive composition. Predicate/performance inputs contribute
truth, needs and provenance; their incoming effect is discarded. Only the
consuming A provision's own evaluation supplies its legal effect.
Actual completion and timely completion
are different claims: a late electronic entry can still have occurred and trigger
its downstream notification. One evaluation concerns one coherent semantic context;
evaluations for different plants, areas or occasions are combined only through
their applicable population/recurrence operation.

An explicitly bound historical `result_ref` consumes an established result at its
own event date through `historical_results`. Article 6(2)'s earlier Article 5(1)
reduction is such a reference: the original reduction is not recomputed under
the lifting date's amended requirements. The supplied result must retain its
owning event-time provision and a source-owned effect; it cannot postdate the
consumer. Missing antecedent evidence stays unresolved. Current applicability
references continue to evaluate in the current legal context. Regional lifting
evidence uses the same historical reduction input alongside its own later basis.

Execution-cost reference bindings require their own lawful work/cost basis.
The duty to undertake substitute execution does not establish determined costs
or cost recourse. Prospective cost determination does not universally require
completed physical work; the particular consumer controls the required fact.

`interval_coverage` merges adjacent and overlapping performance intervals without
erasing gaps. `continuous_duration_support` uses it for genuinely continuous duties
such as consecutive publication, under an explicit counting convention. A survey
follow-up duration does not require continuous observation. An ongoing performance
is established only through evaluation, never into the future.

`custody_facts` combines the source's same-calendar-day delivery with refrigerated
transport and any other established mandatory failure. `confirmation_facts`
compares distinct result identities, sample/extract identity, genome-target identity
and operative geography under Article 2(6). It consumes qualified results rather
than prescribing an analytical protocol. Species membership for Article 7(1)(c),
(d) and the residual point-(e) population uses explicit species identities and the
complete relevant inventory; it neither establishes individual health nor exercises
retention. `continuing_conditions_facts` expands the regional reduction, lifting
and continuing-retention compound leaves. The lifting evidence calculation does
not itself require exercise of the separate lifting decision.

For whole polygon surfaces, `surface_in_band` tests positive-area intersection
with a circular band using each component's minimum and maximum distance to its
point origin. Disconnected components cannot bridge an empty radial gap. A point
on a band boundary and a polygon merely touching it are different spatial claims.
Hectare membership requires the same positive-area outside surface to survive
the combined spatial error and reach the band. A remote surviving component
cannot substantiate a nearby sliver that may disappear. Exclusion also accounts
for inside components that could move outside. These ambiguous cases are scoped
unknowns. Conservative enclosure of the error neighbourhood prevents polygonal
approximation from manufacturing certain outside membership; touching only the
outer boundary does not place hectare area in the band.

## Survey formulas

For independently inspected units with prevalence `p`, complete-method
sensitivity `s`, and count `n`, detection confidence is
`1 − (1 − p s)^n`. The minimum integer sample is the first `n` meeting the
target, not a rounded real-valued estimate. Sampling effectiveness and
conditional diagnostic sensitivity multiply; combining parallel methods requires
their joint dependence to be established.

For a finite population `N` with an explicit integer infected count `D`, sampling
`n` units without replacement gives

`P(detect) = 1 − Σ[k] {choose(D,k) choose(N−D,n−k) / choose(N,n)} (1−s)^k`.

The sum spans the feasible infected counts in the sample. Adjacent hypergeometric
probability ratios and SciPy log-sum-exp normalization avoid cancellation from
large log-factorials; exact rational comparison resolves values close to a decision boundary.
Binary search finds the least sufficient integer. Inspecting the entire
population can still be insufficient when the method is imperfect. The kernel
never clips the sample count and then calls the target achieved.

For the operative RiBESS finite design, `finite_design_counts` uses the held
software's discrete convention: capacity is `floor(N_estimated)` and infected
count is nearest `N_estimated * p_i`, with ties to even. Decimal/Fraction arithmetic
avoids rounding caused by binary representation. Each stratum must contain at least
one modeled unit; an absent stratum is omitted, not allocated confidence. A
derived count exceeding capacity is rejected. Population estimates remain estimates;
their qualification does not become a census claim. Exact probability evaluation
replaces the held approximation while retaining this explicit population convention.
The alternate half-up reconstruction lacked discriminating evidence.

For disjoint risk strata with proportions `q_i` and relative risks `r_i`,
`p_i = p r_i / Σ(q_j r_j)`. The proportions must cover the whole target
population and every `p_i` must be possible. Under the established independence
assumption, global confidence is `1 − Π(1 − C_i)`. Equal target allocation uses
`C_i = 1 − (1 − C)^(1/k)`; this is an allocation method, not an optimizer.
In a two-stage survey the achieved confidence inside the epidemiological unit
becomes the detection sensitivity of the next stage. Multiplying numbers of
plants and hectares gives workload; it does not multiply their confidences.
`two_stage_binomial_confidence` executes that composition for the same qualified
within-unit design in each unit. Heterogeneous unit designs require their own
justified strata. The historical DGR1866 two-stage method and the one-stage method
already stated in DGR1593 and continued in DGR1075 are distinct operative contexts,
not interchangeable defaults.
`two_stage_independent_confidence` also composes differing achieved within-unit
confidences for independent outer units sharing the same prevalence/risk stratum.
It preserves each unit's sensitivity instead of pooling its plant count.
`two_stage_finite_confidence` provides the finite inner/outer composition for a
qualified common within-unit design. Its achieved inner confidence, not its
requested target or plant count, is the outer sensitivity.

`finite_design_samples` starts with equal stratum targets. If a stratum cannot
reach that target even at capacity, it uses the actually attainable confidence
there and redistributes the residual negative probability equally over the
remaining strata. An impossible whole design fails explicitly. Integer samples
are checked against the exact composed probability. This is an allocation
convention, not an optimizer or proof that a historical publication used the
same numerical kernel.

Finite sampling applies when the operative design supplies a qualified finite
population, including an explicitly qualified estimate; unknown/statistically
infinite population uses binomial sampling. The source context selects one or
two stages. `FiniteStratum` supplies a population and risk; `BinomialStratum`
supplies its proportion and risk. `survey_design_adequacy` accepts either coherent
partition; a mixture is rejected. Method sensitivity and independence must be
qualified for the inspection units, including pooling. There is no universal .55
override of .7 × .78, automatic independence from an assay count, or workload-derived
proof of sensitivity. These are mathematical inputs, not operator-facing choices.

These formulas follow the operative model, not the illustrative confidence,
prevalence, sensitivity or radius in an EFSA example. Required source targets
come from B; risk and method qualifications must apply to the same population.
Completed usable observations, rather than planned, repeated or undetermined
tests, support a negative-survey conclusion.
`observed_survey_support` derives counts from distinct usable negative
inspection-unit identities, rejects overlap between disjoint strata, and scopes
incomplete observation inventories to the negative-survey conclusion. A known
positive in the required scope defeats that conclusion independently. These
identities follow the operative inspection unit, not the number of assays.
Any supplied planned counts are replaced by the actual usable identity counts.
`observed_binomial_support` is the existing binomial input adapter to this same
operation. `planned_sample_difference` handles plant-only regional workload,
independently of assurance.
`negative_recurrence_support` counts distinct qualifying survey/test occasions
inside their operative periods. Samples from one occasion do not become multiple
annual or flight-season performances. The complete required period set and
absence of detection in the same legal scope remain necessary semantic inputs;
the function does not infer either from missing records. Article 5(1)(d)'s
natural-spread conclusion remains separate from its twice-per-season count.
When the required count has not yet been achieved in an open period, the result
remains unresolved; it is not a proven annual/seasonal omission. A closed period
with a complete insufficient history fails, while a known positive defeats the
negative conclusion even during an open period. Four-year lifting composes this
annual basis with support for every required area and the resettable no-detection
period. Pre-lifting testing separately binds its own C95/p1 target and practical
ordering; meeting a lower assurance target cannot satisfy it.

## Numerical and input boundaries

Use exact Decimal source quantities and integer counts. Floats are for numerical
geometry/probability evaluation, with explicit finite-domain checks. Coordinates
are not metres merely because they are numbers. Shapely supplies topology;
PROJ/pyproj supplies transformations and WGS84 geodesics. Metric-frame and source
error bounds must support any ground-distance conclusion.
`projection_distance_error` calculates the distortion contribution from a
qualified bound on directional projection scale over the whole relevant domain.
That contribution and source/transformation errors must be included in the
supplied geometry error bounds. Sampled projection factors or PROJ's nominal
accuracy do not establish such a bound. D must qualify the supplied transformation,
population and performance inputs; C computes their consequence. Providing an
arbitrary error bound is not proof of accuracy. EPSG:32633 is the captured SIT
frame and is appropriate for regional metric work with qualified distortion and
source errors; it is not a universal zero-error ground-distance convention.

No source geometry is silently repaired. Known invalid input is rejected;
unavailable evidence names the needed input. A missing coordinate or survey
observation cannot become a negative finding. Source-retained conflicts and
the accepted historical gaps keep their conclusion-specific scope.

## Calendar conventions and remaining input boundary

The completed research was collectively adjudicated in the dated derivation.
The methods and calendar conventions below are the accepted C position. Their
evidential footing does not imply that every convention is expressly stated in
a plant-health act.

`calendar-rules.json` assigns every quantified clock once. `clock_boundary` uses
that assignment by default, including through the ordinary election,
noncommencement, lifting and first-year survey adapters. An explicit `PeriodRule` remains available for a
qualified exceptional context or mathematical fixture, not an operator menu.
New quantified clocks without an assignment require a C disposition.

- Calendar durations, consecutive publication, lookbacks, eligibility periods,
  temporary designation validity and the adaptation period use calendar arithmetic
  without weekend extension. Elapsed duration does not prove continuous performance.
- The EU first-year survey deadline uses EU1182's period convention, including
  final-day roll and its two-working-day minimum. Act effect/validity and retroactive
  periods do not inherit those extensions.
- Italian calendar-day deadlines exclude the event day and include intervening
  nonworking days. The five owner-election clocks concern procedural submissions:
  their Saturday, Sunday or public-holiday expiry extends to the next working day.
  This adopts ANAC479/2024's general procedural reasoning by analogy to the
  communication selecting the execution route. Its actual Sunday PEC example
  also shows why electronic submission does not defeat the extension. No direct
  Osservatorio-specific Saturday ruling is claimed. Other Italian calendar-day
  deadlines retain Sunday/public-holiday extension; physical removal and
  commencement do not become procedural submissions by association.
- Express working-day clocks use Monday–Friday excluding applicable public holidays.
  This is the accepted administrative convention; holiday coverage and any
  established special counting rule must be qualified by D. Contact opening hours
  do not prove an executor's actual working schedule.
- Source hour clocks use exact elapsed time; same-day custody ends at the next
  local midnight. Neither becomes working days or invokes EU1182's distinct
  exclusion of the initial clock hour as its justification.

The A/B owners now contain the accepted regional source quantities, retaining
area, campaign and risk qualifications and independent Union requirements.
Ordinary accepted-owner loading exercises their effect. Displayed population estimates and table totals cannot set
future populations or certify assurance.

Geography continues to use adopted geometry, the supplied operative hectare
partition and qualified precision. The captured SIT frame is EPSG:32633; this is
evidence for a useful metric frame, not a legal distance tolerance. AdE's ordinary
2 m accuracy statement is not a guaranteed bound for each parcel or for plant
coordinates. These evidence qualifications belong to D, not to a further generic
choice of geographic model. Biological intervals, practicability, promptness and
qualifying commencement likewise remain semantic inputs where A/B do not quantify
them. A monitoring calendar does not define actual flight season, and a planned
work schedule does not prove commencement. Research has not displaced these
existing input boundaries.

Required inputs also include ordinary facts owned by D's eventual evidence
contracts: legal act and recipient effectiveness, authority and task scope,
individual status, actual qualified performances and completeness of the relevant
population/history. These are not unresolved mathematical research questions.
They enter A's exact condition language directly; C does not invent computations
for an official designation, competent decision, signature or factual judgment.
The accepted Cq boundaries, legal conflicts and historical gaps stay as owned
upstream. Research limits do not justify changing them or broadening the aperture.

## Reproduction

The reference environment uses Python 3.12 and the pinned versions in
`requirements.txt`. NumPy/SciPy support probability evaluation; Shapely/pyproj
support geometry; Hypothesis supports boundary properties. The choice follows
the component's job and is not limited to previously installed libraries.

From the repository root:

```sh
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r regulation/stage-c/requirements.txt
PYTHONPATH=regulation/stage-c .venv/bin/python -m unittest discover -s regulation/stage-c -p test_reference.py
PYTHONPATH=regulation/stage-c .venv/bin/python regulation/stage-c/check_mutations.py
```

The tests include independent rational recomputation, source examples, material
route differences and boundaries. Mutation checks change actual functions in
memory, require a passing baseline and verify that the relevant regression then
fails. Neither passing tests nor this specification certify semantic coverage.
Primary whole-state verification and the five independent facet reviews must
precede presenting the completed stage for Owen's acceptance.
