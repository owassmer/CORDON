# CSIC/JRC individual-tree inventory acquisition and replication handoff

Status: delegated research workstream
Date: 22 August 2026
Parent objective: reduce realized Xylella loss by giving the cooperative operator a real, persistent individual-tree operating universe where evidence supports it

## Mission

Find, acquire, recover, or independently reproduce the strongest available individual-olive-tree inventory created by the CSIC/JRC/POnTE/XF-ACTORS remote-sensing work in Puglia.

The priority target is the reported 2013 regional crown baseline and its 2015/2018 change products. A secondary target is the full crown population from the 2016–2017 airborne hyperspectral campaigns.

Do not stop at confirming that a paper or presentation exists. Determine what data, vectors, model artifacts, imagery, code, derived outputs, institutional holdings, archives, or reproducible methods can actually be obtained now.

## Known starting evidence

1. A CSIC repository abstract for *Monitoring the impact of Xylella on Apulia's olive orchards using Sentinel-2 satellite data and aerial photographs* states that the team:
   - used summer-2013 aerial photographs to delineate each olive tree in the region;
   - used 2015 and 2018 photographs to identify trees that became crownless or disappeared;
   - trained a Mask R-CNN for crown delineation;
   - worked from 27,188 olive orchards covering 2,261 km².

2. The downloadable 37-page conference presentation is primarily orchard-level, says “We work at the level of orchards, not trees,” and does not expose crown vectors, model weights, validation tables, or a regional tree count.

3. The 2016–2017 airborne campaigns scanned approximately 200,000 olive trees over about 1,200 ha at sub-meter resolution.

4. The public QuantaLab reproduction repository contains:
   - a 7,296-row analytical table with 4,033 distinct `TREE` values and no X/Y fields;
   - a 67-row coordinate-bearing qPCR subset;
   - a 100-row coordinate-bearing qPCR subset;
   - code for the published analyses;
   - no visible full 200,000-tree crown inventory.

5. CORDON already holds:
   - 76,637 Crecco tree points over 25 km²;
   - 2019–2021 WorldView-2 imagery for part of that work;
   - official CAMP observations and repeat-coordinate cohorts;
   - 341,428 monumental-tree records;
   - Puglia native orthophoto services for several years;
   - current and historical public GIS, Parcel, Plant and Proceeding sources.

6. Current evidence note:
   `research/workflow-redesign/individual-tree-inventory-feasibility.md`

## Success

The strongest success is an actual usable tree-level artifact with clear custody and rights:

- crown polygons or plant points;
- stable source identifiers where available;
- acquisition epoch and spatial reference;
- spatial coverage and population count;
- validation or error record;
- change labels or cross-epoch correspondence if available;
- license or written reuse basis.

If the original inventory cannot be acquired, success is a reproducible reconstruction that uses real obtainable imagery and produces measured, falsifiable tree identities at the supported area and orchard grains.

A reconstruction is not successful merely because a model emits points. It must measure detection, omission, duplicates, split/merge behavior, location error and cross-epoch identity stability against real controls.

## Freedom to explore

Choose the methods. Follow any promising route, including institutional repositories, code and data archives, project portals, publication supplements, API metadata, web archives, author/project custody, public imagery, held imagery, model reconstruction, transfer learning, manual validation, or alternative inventory sources.

Do not assume the parent’s current acquisition theory is correct. Challenge the reported regional scope, the meaning of “each olive tree,” the availability of the imagery, the reliability of the model, and whether a historical baseline can support current identity.

Use the full available iteration and wall-clock budget. Continue until the best acquisition path is exhausted or a real artifact/reconstruction is produced and verified.

## Required distinctions

Keep these separate:

- detected crown or point;
- reproducible observation-derived Individual Plant identity;
- official Plant identity;
- correspondence between observed and official identity;
- appearance/disappearance or crown change;
- planting, removal, survival or replacement;
- infection or legal status;
- documentary discrepancy;
- audit candidate;
- competent fraud finding.

## Claims prohibited without matching evidence

Do not claim:

- complete current Puglia coverage;
- official identity from proximity alone;
- infection or legal status from imagery alone;
- cause from crown disappearance;
- planting or establishment from appearance alone;
- fraud from a discrepancy alone;
- commercial reuse rights from public technical access.

## Work area and deliverables

Work only inside:

`research/tree-inventory/`

Do not edit current Gate 2–4 authority files, `olive-xylella`, legacy design files, Ontology files, platform files, or interfaces. Do not run Git.

Write:

1. `CSIC_JRC_TREE_INVENTORY_RESULT.md` — evidence-linked conclusion, acquisition log, artifacts obtained, rights, measured quality, remaining uncertainty, exact recommendation.
2. `artifacts/` — acquired metadata, small vectors/tables, manifests, validation outputs and reusable scripts. Do not copy restricted imagery or secrets.
3. `RUNBOOK.md` — exact reproduction or continuation steps for any successful or partially successful route.

Report absolute artifact paths and checksums where practical. If an external request or paid/proposal-gated source is the remaining route, prepare but do not send the exact request and identify the recipient.

## Mainline relationship

This is a priority evidence workstream, but the parent continues Gate 4 closure and source-of-truth realignment. Return any verified contradiction or recommended selective noun/relationship correction explicitly. Do not assume that priority evidence work must become a new function, noun, relationship family, Ontology shape, or interface.
