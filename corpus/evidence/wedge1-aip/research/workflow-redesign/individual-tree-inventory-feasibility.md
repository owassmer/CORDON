# Individual-tree inventory feasibility

Status: auxiliary evidence note; may selectively refine Gate 3 Individual Plant supportability and Gate 4 observation relationships; does not alter the seven-family Gate 4 mainline by itself
Date: 22 August 2026

## Verdict

CORDON can plausibly build a real, operator-useful individual-tree inventory on validated bounded areas. Current evidence does not support a stable, complete region-wide inventory.

The viable route is native 0.15–0.20 m orthophotography or equivalently validated crown-resolving imagery, a baseline inventory and explicit cross-epoch identity adjudication.

Sentinel-2, including 2.5 m super-resolution, is not a defensible individual-tree identity source. The local DiffFuSR result is null and matches bicubic control. Two output pixels across a typical five-metre spacing cannot establish stable crown identity, especially when the pixels are inferred rather than independently measured.

## Verified local evidence

### Crecco OQDS-Insight v5

Direct parsing of the downloaded v5 shapefile verifies:

- 76,637 point records;
- 76,637 unique `fid` values;
- 70 duplicate-coordinate rows;
- 5.062 m median nearest-neighbor spacing;
- 2,340 records with `infection = true`;
- 432 labelled 2019 and 1,908 labelled 2020.

These labels are photointerpreted disappearance/infection candidates from 2019–2021 WorldView-2 observations. They do not establish official infection, legal removal, disappearance cause or exact event date.

Figshare's article description still reports 77,068 trees and 2,225 likely infected/removed trees. The current downloadable v5 vector differs. `olive-xylella/data/CRECCO.md` now records the verified file values.

Source: https://api.figshare.com/v2/articles/28191245

### Image and coordinate grain

- Held WorldView-2 RGB and rendered-NDVI files are 0.5 m.
- Existing point-to-raster analysis found a shallow registration optimum around +1 m east and +5 m north.
- This uncertainty is comparable to the 5.062 m median inter-tree spacing.
- Naive nearest-neighbor matching cannot establish plant sameness.
- The subagent measured official-to-Crecco matching with median nearest distance 6.64 m; only 40.9% of 3,600 official 2021 olive samples fell within 5 m, and 18.9% of those had first-versus-second-nearest margin below 1 m.
- Existing project analysis warns that coordinate recurrence does not guarantee tree identity.

### Puglia orthophotos

The official services expose:

- 2015 color-infrared at 0.15 m;
- 2022 RGB at 0.20 m;
- 2023 RGB at 0.20 m.

The live 2023 service confirms 0.20 m pixel size, three RGB bands and EPSG:32633.

Source: https://webapps.sit.puglia.it/arcgis/rest/services/BaseMaps/Ortofoto2023/ImageServer?f=pjson

At 0.20 m, a five-metre inter-tree spacing spans about 25 native pixels. Crown separation is plausible for mature separated trees, but remains unvalidated for dense, pruned, dead, young or overlapping Puglian crowns.

### Existing super-resolution result

`olive-xylella/nowcast/SR.md` and `NEGATIVE.md` show:

- DiffFuSR crown-masked paired results have p ≥ 0.22;
- only about 40% of sample arms contain a crown pixel;
- high-crown-fraction results are null or wrong-signed;
- bicubic control matches the pattern.

This disproves neither crown detection nor within-crown physiology. It does show that the current 2.5 m Sentinel-2 reconstruction is not an independent individual-tree identity measurement.

## Supported proposition ladder

| Proposition | Current support |
|---|---|
| Detect crown/location | Plausible on bounded areas with native crown-resolving imagery; requires local validation by orchard form |
| Assign stable observation-derived identity | Plausible only after validated baseline detection and explicit cross-epoch continuation, split and merge adjudication |
| Link observation-derived identity to official Plant/Proceeding | Candidate match until identifier or adjudicated multi-evidence resolution establishes sameness |
| Infer disappearance or appearance | Observation/change candidate; does not prove cause, legal removal, planting date or survival |
| Establish infection or legal status | Not supported by imagery alone; requires official diagnostic and governing process |
| Corroborate documented planting/removal | Potential audit evidence if timing, visibility and count error are valid |
| Establish fraud | Not supported by imagery alone; requires operative obligation, claim/payment evidence, field verification and competent finding |

## Existing tree populations and inventory candidates

### Monumental-tree registry

The official registry contains 341,428 individually recorded monumental trees. It is a large real inventory, but only of the registered/protected subset rather than the complete olive population.

### Official CAMP monitoring

The 12 official campaign workbooks contain approximately 1.3–1.5 million tree/sample records. They are a moving surveillance frame, not a census. Coordinates identify observations, recurrence is sparse, and no stable source identifier establishes that equal or nearby coordinates across campaigns are the same plant.

### Crecco OQDS-Insight

Crecco v5 is a real 76,637-tree bounded inventory over 25 km². It is the strongest inventory currently held by CORDON and the best local falsification environment.

### Zarco-Tejada airborne campaigns

The 2016–2017 airborne campaigns scanned approximately 200,000 olive trees at sub-meter resolution over about 1,200 ha. The public reproducibility repository releases:

- one 7,296-row analytical table containing 4,033 distinct `TREE` values but no X/Y coordinates;
- one 67-row Parcel qPCR table with coordinates; and
- one 100-row Orchard qPCR table with coordinates.

The full scanned crown inventory or crown vectors are not in the public repository.

Sources:

- https://digital.csic.es/handle/10261/167916
- https://github.com/Quantalab/Xf-NPlants-2018

### CSIC/JRC 2019 regional crown work

A CSIC repository abstract for *Monitoring the impact of Xylella on Apulia's olive orchards using Sentinel-2 satellite data and aerial photographs* states that the team used summer-2013 aerial photographs to delineate each olive tree in the region and 2015/2018 photographs to determine crown loss. It describes a Mask R-CNN and 27,188 olive orchards covering 2,261 km².

The downloadable 37-page conference presentation is primarily orchard-level and explicitly says, “We work at the level of orchards, not trees.” It does not expose the claimed regional crown vectors, tree count, model weights or validation table. The abstract therefore establishes that an inventory-producing research effort existed, not that its inventory is currently public or held by CORDON.

Sources:

- https://digital.csic.es/handle/10261/215092
- https://digital.csic.es/bitstream/10261/207915/1/monitoring_impact_Xylella.pdf

### Acquisition consequence

The strongest acquisition routes are:

1. obtain the 2013/2015/2018 crown vectors, model artifacts and validation record from the named CSIC/JRC authors or holding institution;
2. search the underlying Regione/JRC project custody and any linked research-data records;
3. if the vectors are unavailable or unusable, reproduce a current inventory from explicitly licensed native orthophotos, using Crecco and official individual-tree sources for validation.

Any acquired 2013 inventory is a historical baseline, not a current population. It must be reconciled across later imagery with explicit disappearance, appearance, split, merge and ambiguity handling.

## Proposed selective Gate 3 refinement

Current accepted boundary:

> Individual Plant is admitted where an external authority, registry, field process or operative Governing Instrument preserves identity.

Evidence-supported refinement:

> Individual Plant is admitted where identity is preserved by an external process **or by a validated, reproducible observation-derived inventory**.

An observation-derived inventory is valid only after measuring, by relevant orchard stratum:

- detection precision and recall;
- duplicate, split and merge rates;
- omission rate;
- geolocation error;
- fixed-image reproducibility;
- cross-epoch identity precision and recall;
- explicit handling of ambiguous continuation, appearance and disappearance.

An emitted point is not sufficient.

## Gate 4 consequences

The tree-inventory work does not itself require another relationship family. The later Gate 5 MECE correction independently adds F8 Formal Proceeding Subject and Scope and F9 Plant Material Allocation and Custody.

- **F3 Scoped Governing Instrument Effect and Applicability:** a governing effect reaches an observation-derived Individual Plant only after plant sameness with the instrument subject is established. Proximity, Parcel overlap or crown detection alone is insufficient.
- **F5 Intervention Physical and Material Scope:** validated observation-derived Plants can participate as intended, authorized or independently preserved as-built scope. Observations and acceptance outcomes can evidence or change that relationship but are not F5 predicates.
- **Plant–Parcel location:** contextual spatial association unless a real authority/process preserves independent relationship facts.
- **Official-record correspondence:** identity resolution and provenance, not a real-world fact-bearing relationship. Resolved records describe one Plant; unresolved matches remain candidates.
- Appearance, disappearance, survival, pruning and crown change remain observations/events/outcomes.
- Imagery creates no Plant–Organism infection, legal-status or fraud relationship.

## Falsification sequence

1. **Fixed-image detection:** validate stratified mature, dense, monumental, pruned, dead and young groves against dual-review reference. Require mature-tree precision and recall at least 0.95; report every stratum and split/merge/duplicate rates.
2. **Cross-epoch identity:** register epochs using stable non-tree controls and orchard topology. Require unchanged-tree precision/recall at least 0.98, fixed-image ID reproducibility at least 0.99, and explicit split/merge treatment.
3. **Official-coordinate challenge:** test monumental and official sample records. Require adjudication for ambiguous matches. Reject coordinate-only linkage if positional ambiguity remains material.
4. **Change detection:** validate removal, planting and survival separately. Do not transfer removal performance to young-tree planting/survival.
5. **Document-versus-observation audit:** use one real proceeding with authorized/as-built count, Parcel footprint, completion date and payment evidence. A discrepancy creates an audit candidate. Kill the use case if imagery count error is not materially smaller than the discrepancy.

These thresholds are proposed falsification gates, not measured current performance.

## Licensing boundary

- Figshare declares OQDS-Insight CC BY 4.0, but that does not necessarily override underlying WorldView pixel rights.
- Puglia 2015 orthophoto metadata states IODL 2.0.
- 2019/2022 AGEA terms and 2023 service metadata do not yet establish commercial derivative-vector rights.
- A commercial inventory requires imagery with explicit derivative-use rights, commissioned capture or written clearance.

## Claims prohibited

CORDON must not claim:

- complete Puglia-wide tree coverage;
- official/observed plant sameness from proximity alone;
- individual-tree identity from 2.5 m Sentinel super-resolution;
- infection, legal status or cause from crown appearance;
- funded planting or successful establishment from a new crown alone;
- absence of a plant from absence of a visible crown;
- fraud from a count discrepancy;
- commercial imagery rights from a public endpoint.

## Sources

- `olive-xylella/data/CRECCO.md`
- `olive-xylella/data/ORTOFOTO.md`
- `olive-xylella/nowcast/CROWN_DILUTION.md`
- `olive-xylella/nowcast/SR.md`
- `olive-xylella/nowcast/NEGATIVE.md`
- https://api.figshare.com/v2/articles/28191245
- https://webapps.sit.puglia.it/arcgis/rest/services/BaseMaps/Ortofoto2023/ImageServer?f=pjson
- https://www.mdpi.com/2504-446X/6/8/197
- https://www.mdpi.com/2072-4292/14/6/1523
