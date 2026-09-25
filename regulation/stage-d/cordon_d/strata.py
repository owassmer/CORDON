"""Per-campaign survey strata for C's survey calculations, from the operative design accepted A holds.

The design is DGR 1075/2025 §4.1.2-§4.1.10 (Tables 2-10); its §4.1.2 is printed identically in the PNI
2026 RiPEST workbook (`regulation/jurisdiction/national/PNI-2026/xylella-ripest.xlsx`). One stratum is a
zone, a host group and a risk level. Its population is the design's target population of specified
plants, an estimate for that campaign and not a census; its relative risk and planned plants to sample
are B's; its inspection unit is the plant, as B describes it ("plants to sample").

Method sensitivity only where the design states it: the workbook prints sampling effectiveness and
diagnostic sensitivity (Real-time PCR) for §4.1.2; §4.1.3-§4.1.10 state none, so their adequacy is
unknown and nothing is borrowed from §4.1.2. Samples are pooled (DGR 1075/2025 §4.1.1: "7 piante/ettaro
per olivo e da 4 piante/ettaro per tutte le altre specie"), so plants sharing a test are not independent
inspection units and no held source states their dependence model.

DGR 1075/2025 has no text layer and its retained transcription has not been checked cell by cell against
the page images, so no cell of Tables 3-10 is read here; §4.1.2's cells are read from the workbook.

Observed support: a negative record is a negative inspection unit only where it identifies its plant,
and none does (`plants.IDENTITY_CAUSE`); a positive observation in the campaign's scope is a positive
unit on its own reference. §4.1.2's 1 km band is placed by C's `pni_geography_facts`; §4.1.3-§4.1.10
rings around the previous campaign's infected plants have no C function, so membership there is
unavailable (`RING_CAUSE`).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import json
from pathlib import Path

from cordon_c.bindings import pni_geography_facts
from cordon_c.core import Evaluation
from cordon_c.survey import BinomialStratum, method_sensitivity, observed_survey_support, survey_design_adequacy
from .plants import IDENTITY_CAUSE, unknown

DGR = 'PUG-DGR1075-2025'
PNI = 'IT-PNI-2026'
WORKBOOK = 'regulation/jurisdiction/national/PNI-2026/xylella-ripest.xlsx'
HOSTS = ('olive', 'vine', 'fruit', 'other')
SENSITIVITY_CAUSE = 'method sensitivity of the complete inspection method'
DEPENDENCE_CAUSE = 'dependence of plants pooled in one test (7 per olive test, 4 for other species)'
RING_CAUSE = 'membership of the ring around the previous campaign\'s infected plants: no C function'
# The workbook's Puglia rows for §4.1.2, by host group (column F, 'Specie ospiti').
WORKBOOK_HOSTS = {'olive': 'Olea europaea', 'fruit': 'Prunus sp.; Citrus sp.', 'vine': 'Vitis sp.',
                  'other': 'Asparagus acutifolius'}
PNI_PARAMETERS = {'olive': 'B-PAR-PNI2026-olea-design', 'fruit': 'B-PAR-PNI2026-prunus-citrus-design',
                  'vine': 'B-PAR-PNI2026-vitis-design', 'other': 'B-PAR-PNI2026-spontaneous-design'}


@dataclass(frozen=True)
class Stratum:
    design: str                             # DGR or PNI
    section: str                            # '§4.1.2' ... '§4.1.10'
    host: str                               # olive | vine | fruit | other
    risk: str                               # high | base
    parameter: str                          # B's design target for the host group
    relative_risk: float                    # B's
    inspection_units: int                   # B's planned plants to sample
    population: Decimal | None = None       # the design's target population estimate, where read
    proportion: float | None = None
    sampling_effectiveness: float | None = None
    diagnostic_sensitivity: float | None = None
    cells: tuple[str, ...] = ()             # the workbook cells read


def _workbook(root: Path) -> dict:
    """{host: {risk: row}} for Puglia's §4.1.2 rows of the workbook: the host row (medium, 'Rimanenti aree
    indenni') and the row below it (high, '1 km ... attorno alle aree delimitate')."""
    from openpyxl import load_workbook
    sheet = load_workbook(Path(root) / WORKBOOK, data_only=True, read_only=True).worksheets[0]
    rows = [[c.value for c in row] for row in sheet.iter_rows()]
    column = {name: i for i, name in enumerate(
        ('A B C D E F G H I J K L M N O P Q R S T U V W X Y Z AA AB AC AD AE AF').split())}
    out, puglia = {}, False
    for number, row in enumerate(rows):
        if row[column['C']] is not None:
            puglia = row[column['C']] == 'Puglia'
        printed = str(row[column['F']] or '')
        host = next((h for h, words in WORKBOOK_HOSTS.items()
                     if printed == words or h == 'other' and printed.startswith(words + ';')), None)
        if not puglia or host is None:
            continue
        for risk, cells, line in (('base', row, number + 1), ('high', rows[number + 1], number + 2)):
            if {'medio': 'base', 'alto': 'high'}.get(cells[column['R']]) != risk:
                raise ValueError(f'Workbook row {line}: risk level {cells[column["R"]]!r}')
            out.setdefault(host, {})[risk] = {
                # H x U, to whole plants as DGR 1075/2025 Table 2 prints it (990.804 olive high).
                'population': (Decimal(str(row[column['H']])) * Decimal(str(cells[column['U']]))).to_integral_value(),
                'proportion': float(cells[column['U']]), 'relative_risk': float(cells[column['T']]),
                'effectiveness': float(row[column['O']]), 'sensitivity': float(row[column['P']]),
                'samples': int(cells[column['X']]),
                'cells': tuple(f'{c}{r}' for c, r in (('H', number + 1), ('U', line), ('T', line),
                                                      ('O', number + 1), ('P', number + 1), ('X', line)))}
    return out


def strata(root: Path, design: str = DGR) -> dict:
    """{(section, host): (Stratum high, Stratum base)} for the design's campaign."""
    ledger = json.loads((Path(root) / 'regulation/stage-b/clocks-and-parameters.json').read_text())
    b = {p['parameter_id']: p for p in ledger['parameters']}
    risk = {'high': float(b['B-PAR-DGR1075-survey-high-risk']['value']),
            'base': float(b['B-PAR-DGR1075-survey-base-risk']['value'])}
    printed = _workbook(root)
    sections = range(2, 11) if design == DGR else (2,)
    out = {}
    for table in sections:
        for host in HOSTS:
            if design == DGR:
                parameter = f'B-PAR-DGR1075-T{table}-{host}-design'
                samples = {r: int(b[f'B-PAR-DGR1075-T{table}-{host}-{r}-samples']['value']) for r in risk}
            else:
                parameter = PNI_PARAMETERS[host]
                name = parameter.removesuffix('-design')
                samples = {r: int(b[f'{name}-{w}-workload']['value']['samples'])
                           for r, w in (('high', 'high'), ('base', 'medium'))}
            pair = []
            for level in ('high', 'base'):
                stratum = Stratum(design, f'§4.1.{table}', host, level, parameter, risk[level], samples[level])
                if table == 2:
                    cell = printed[host][level]
                    if (cell['samples'], cell['relative_risk']) != (samples[level], risk[level]):
                        raise ValueError(f'§4.1.2 {host} {level}: the workbook and B disagree')
                    stratum = Stratum(design, stratum.section, host, level, parameter, risk[level], samples[level],
                                      cell['population'], cell['proportion'], cell['effectiveness'],
                                      cell['sensitivity'], cell['cells'])
                pair.append(stratum)
            out[(f'§4.1.{table}', host)] = tuple(pair)
    return out


def _binomial(group) -> tuple:
    return tuple(BinomialStratum(s.proportion, s.relative_risk,
                                 method_sensitivity(s.sampling_effectiveness, s.diagnostic_sensitivity),
                                 s.inspection_units) for s in group)


def design_adequacy(snapshot, group, at: date) -> Evaluation:
    """C's `survey_design_adequacy` for one host group's strata, where the design states its sensitivity."""
    if any(s.diagnostic_sensitivity is None or s.sampling_effectiveness is None for s in group):
        return unknown(SENSITIVITY_CAUSE)
    return survey_design_adequacy(snapshot, group[0].parameter, at, _binomial(group),
                                  population_and_method_qualification=Evaluation(True),
                                  required_risk_structure=Evaluation(True), independence_established=False)


def observed_support(snapshot, group, at: date, *, positive_units: frozenset) -> Evaluation:
    """C's `observed_survey_support` for one host group: no negative record identifies its plant, so the
    observation inventory is not complete; a positive unit in the campaign's scope defeats the claim."""
    if any(s.diagnostic_sensitivity is None for s in group):
        if positive_units:
            return Evaluation(False)
        return unknown(SENSITIVITY_CAUSE)
    return observed_survey_support(
        snapshot, group[0].parameter, at, strata=_binomial(group),
        negative_units=tuple(frozenset() for _ in group), positive_units=frozenset(positive_units),
        observation_inventory_complete=False, population_and_method_qualification=Evaluation(True),
        required_risk_structure=Evaluation(True), required_performances_complete=unknown(IDENTITY_CAUSE),
        official_method_and_scope=Evaluation(True), independence_established=False)


def band_placement(snapshot, at: date, place, demarcated_union, *, in_puglia: Evaluation,
                   host_qualifications: dict) -> dict:
    """§4.1.2's 1 km band for one observation: C's `pni_geography_facts` on the complete demarcated union."""
    return pni_geography_facts(snapshot, at, place, demarcated_union,
                               target_is_in_puglia_pest_free_area=in_puglia,
                               host_qualifications=host_qualifications)
