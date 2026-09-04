---
title: Previsual detection
created: 2026-08-15
updated: 2026-08-15
type: concept
tags: [detection, method]
sources: [raw/papers/zarco-tejada-2021-natcomm.pdf]
confidence: high
contested: false
---

# Previsual detection

Airborne imaging spectroscopy + thermography can see [[xylella-fastidiosa]] in olive **before** visual symptoms.

Zarco-Tejada et al. 2018 *Nature Plants*: >80% vs qPCR when fluorescence, thermal stress, and fast pigment traits are combined. Trees the spectrometer called affected, though still visually healthy, later developed symptoms at almost double the rate of trees it called clear.

Zarco-Tejada et al. 2021 *Nature Communications*: the hard problem is drought looking like disease. After uncoupling biotic vs abiotic spectral pathways, uncertainty in Xf detection fell below 6%; vs *Verticillium* the routes stayed pathogen- and host-specific, accuracies >92%.

## What CORDON does with this

We do **not** fly a plane. We test whether **Sentinel-2 + official PCR** can carry a weaker version of the same idea at 10 m. If it cannot beat NDVI-only and drought-only, we publish the negative. Hyperspectral comes only with a [[cnr-ipsp]] / Zarco-Tejada partner.

This is the Vesuvius object: hidden signal in a noisy volume, scored by an external oracle (official PCR).

## Related

[[front-nowcast]] · [[puglia-monitoring]] · [[oqds]] · [[camp-csv]]
