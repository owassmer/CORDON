# Resistance Decoder v1 — sources

Every citation used in `v1-targets.md`, with DOI/URL and whether the file is on disk. "On disk" paths are relative to the repo root (`olive-xylella/`).

## Primary papers — full text on disk

| Paper | DOI / URL | On disk |
|---|---|---|
| Giampetruzzi et al. 2016, BMC Genomics 17:475, "Transcriptome profiling of two olive cultivars…CoDiRO strain" | 10.1186/s12864-016-2833-9 | `raw/articles/giampetruzzi-2016.pdf.txt`; PDF `raw/papers/giampetruzzi-2016-bmc-genomics.pdf` |
| La Notte et al. 2024, Front. Plant Sci. 15:1457831, "A survey in natural olive resources…resistance…in Leccino offspring" | 10.3389/fpls.2024.1457831 | `raw/articles/la-notte-2024.pdf.txt`; PDF `raw/papers/la-notte-2024-frontiers.pdf` |
| Montilon et al. 2022, Plant Pathology 72(1):144-153, "Xylella fastidiosa subsp. pauca ST53 exploits pit membranes…" | 10.1111/ppa.13646 | **NEW** `raw/articles/montilon-2022.pdf.txt` (PDF `raw/supp/montilon-2022.pdf`, IRIS-CNR green OA) |
| Sabella et al. 2019, Sci Rep 9:9602, "Xylem cavitation susceptibility and refilling mechanisms in olive trees infected by Xylella fastidiosa" | 10.1038/s41598-019-46092-0 | **NEW** `raw/articles/sabella-2019.pdf.txt` (PDF `raw/supp/sabella-2019.pdf`, Nature OA) |
| Ahern et al. 2014, J. Bacteriol. 196(2):459-471, "Characterization of Novel Virulent Broad-Host-Range Phages of Xylella fastidiosa and Xanthomonas" | 10.1128/JB.01080-13 | **NEW** `raw/articles/ahern-2014.pdf.txt` (Europe PMC / PMC3911242 full text) |
| Surano et al. 2022, Front. Plant Sci., hydraulics | (Frontiers) | `raw/articles/surano-2022.pdf.txt` |
| Pavan et al. 2021, Front. Plant Sci., germplasm screen | (Frontiers) | `raw/articles/pavan-2021.pdf.txt` |
| Sabri et al. 2024, Front. Microbiol. 15:1412650, phage MATE 2 | 10.3389/fmicb.2024.1412650; GenBank PP816325 | `raw/papers/sabri-2024-frontiers-mate2.pdf`, `raw/extracts/sabri-2024-frontiers-mate2.txt` |
| EFSA 2016, treatments statement | (EFSA) | `raw/papers/efsa-2016-treatments.pdf` |

## Supplementary files — parsed, on disk

| File | Content | On disk | Where IDs came from |
|---|---|---|---|
| Giampetruzzi Additional file 3 (MOESM3) | Leccino DEG matrix: 73 up + 586 down `lc_xylem_*` contigs, Mercator BIN, DESeq2 log2FC/padj, BLASTX | `raw/supp/giampetruzzi-2016-MOESM3.xlsx` | Rank 1 RLP contigs; Rank 2 FLA/PME/PG/laccase contigs |
| Giampetruzzi Additional file 4 (MOESM4) | Ogliarola DEG matrix: 92 up + 354 down `og_xylem_*` contigs | `raw/supp/giampetruzzi-2016-MOESM4.xlsx` | Rank 2 Ogliarola expansins |
| Giampetruzzi Additional file 9 (MOESM9) | Selected RT-qPCR candidate transcripts with olive TSA accessions (GBKW/GABQ) | `raw/supp/giampetruzzi-2016-MOESM9.xlsx` | TSA accessions FLA/LAC17/PME/expansin |
| La Notte Supplementary Table S4 | S105 upregulated DEGs (Xf_DDpos vs Xf_neg), `OE9A*` IDs, shrunkFC, FDR | `raw/supp/lanotte-epmc/Table4.xlsx` (sheet "Suppl.Table 4") | **Rank 1 SOBIR1, WAK2, RPM1-like, RGA3, R1A-10, R1B-19, lectin-RLK — all resolved here** |
| La Notte Suppl. Tables S5–S9 | GO sets and S215/S234 up/down DEGs | `raw/supp/lanotte-epmc/Table4.xlsx` (sheets Suppl. Table 5–9) | cross-check |
| La Notte Suppl. Tables S10–S15 | further DEG lists incl. downregulated / PC1 loadings | `raw/supp/lanotte-epmc/Table5.xlsx` | Rank 4 collapse-axis genes |
| La Notte full supplementary bundle | Europe PMC supplementaryFiles zip for PMC11471571 | `raw/supp/epmc-supp.zip` + extracted `raw/supp/lanotte-epmc/` | source archive |

Retrieval note: La Notte supplementary tables were obtained via the Europe PMC REST supplementaryFiles endpoint for PMC11471571 (the Frontiers `.s001` DOI and PMC `/bin/` links returned HTML wrappers, not the files). Giampetruzzi Additional files via Springer static-content MOESM URLs.

## Cited but NOT on disk (secondary / abstract only) — explicit gaps

| Item | DOI / URL | Status |
|---|---|---|
| Sabella et al. 2018, J. Plant Physiol. 220:60-68 (lignin genes, CCR/C4H/4CL primer accessions) | 10.1016/j.jplph.2017.10.007 | abstract + primer table read from web; PDF not frozen |
| Cara, Sabri et al. 2026, Sci Rep 16:11969 (Phi1/Phi3) | (Sci Rep 2026) | secondary; not on disk |
| Das et al. 2015 (grape phage cocktail, APS abstract) | APS 2014 abstract | secondary; not on disk |
| Moll et al. 2021, Front. Microbiol. 12:753874 (AMP 1036/RIJK2) | 10.3389/fmicb.2021.753874 | abstract only |
| El Handi et al. 2022, Biology 11:1685 (GF19/IL14) | 10.3390/biology11111685 | **GAP: MDPI HTML 404 on fetch; not on disk** |
| Clavijo-Coppens 2021 (Mediterranean Xf phages) | — | not on disk |
| De Donno genome CDS (PilA/XadA/MopB locus tags) | GenBank (De Donno); Temecula1 PilA `NP_780105.1` | **GAP: not parsed** |
| BIOVEXO H2020 887281 | biovexo.eu | project deliverable language, web |
