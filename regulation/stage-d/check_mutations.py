"""Bounded discriminating mutations of the lawful-dueness class (PR #35), of the join's rule
table (PR #40) and of row 9's instrument rules (PR #47), in memory.

No canonical file is edited. Each named regression must pass as built and fail on its
associated wrong A meaning or wrong implementation; this is evidence about these
failures, not a coverage score. Run with PYTHONPATH=regulation/stage-c:regulation/stage-d.
"""
import copy
import importlib
from pathlib import Path
import unittest
from unittest import mock

from cordon_c.core import Snapshot

WITHDRAWAL = 'REG-PUGLIA-U181-DIR-2024-00018:case-delta:named-orders-50m-host-removal-withdrawn'
HOLD = 'REG-PUGLIA-U181-DIR-2023-00045:case-delta:pending-monumental-recognition-hold'


def drop_124(rows):
    row = next(r for r in rows if r['stable_provision_id'] == WITHDRAWAL)
    row['corrects_instrument_ids'].remove('REG-PUGLIA-U181-DIR-2023-00124')


def restore_hold_prose(rows):
    v1 = next(r for r in rows if r['provision_version_id'] == f'{HOLD}:v1')
    v2 = next(r for r in rows if r['provision_version_id'] == f'{HOLD}:v2')
    v2.update(condition_ast=copy.deepcopy(v1['condition_ast']), true_effect=v1['true_effect'])


DATA = (
    ('drop 124/2023 from the withdrawal row', drop_124,
     'test_prescriptions.StatedTermRule.test_a_124_record_of_fifty_metre_hosts_reaching_the_row_is_not_due'),
    ("restore v1's prose true effect in the hold v2", restore_hold_prose,
     'test_prescriptions.StatedTermRule.test_a_population_wholly_of_held_olives_is_not_due_while_the_hold_resolves'),
)
CODE = (
    ('remove the adoption-date check', 'cordon_d.case_prescriptions',
     "        if change.get('adopted') and at < date.fromisoformat(change['adopted']):\n            continue\n", '',
     'test_case_prescriptions.CasePrescriptionRecords.test_before_14_march_2024_dueness_is_the_orders_own_reading'),
    ('remove the no-position rule', 'cordon_d.prescriptions',
     'if partial and predicate == WORK and not positioned:', 'if False:',
     'test_prescriptions.StatedTermRule.test_in_part_never_makes_a_record_without_a_position_due'),
    ('let a row that neither bears on dueness nor corrects gate it', 'cordon_d.prescriptions',
     '        if not gates_dueness(snapshot.version(sid, at)):\n            continue\n', '',
     'test_prescriptions.StatedTermRule.test_a_96_letter_a_holder_reads_due_in_part'),
    ('let a correction or supplement that bears on no dueness outcome not gate it', 'cordon_d.prescriptions',
     '    return bears_on_dueness(row) or bool(row.get("corrects_instrument_ids"))\n',
     '    return bears_on_dueness(row)\n',
     'test_prescriptions.StatedTermRule.test_correction_holds_the_order_it_corrects'),
    ('let other rows\' needs outrank a resolved not due', 'cordon_d.prescriptions',
     '    if withheld and reading is not None:\n', '    if withheld and reading is not None and not needs:\n',
     'test_prescriptions.StatedTermRule.test_a_resolved_not_due_decides_whatever_other_rows_still_need'),
    ("let the order's stated unknown replace a not due", 'cordon_d.case_prescriptions',
     '        if stated is not None and due.truth is True:\n',
     '        if stated is not None and due.truth is not None:\n',
     'test_annex_positions.AnnexPositions.test_a_96_hosts_only_position_with_its_tar_387_2026_closure_reads_not_due'),
    ("let a court's reason drop its need without an A row recording the act it names", 'cordon_d.case_prescriptions',
     '    return bool(later) and later <= recorded\n', '    return bool(later)\n',
     'test_annex_positions.AnnexPositions.test_tar_1007_2023_keeps_its_need_on_dds_119_2022'),
    ("let one recorded act among those a court's reason cites drop its need", 'cordon_d.case_prescriptions',
     '    return bool(later) and later <= recorded\n', '    return bool(later & recorded)\n',
     'test_annex_positions.AnnexPositions.test_a_court_reason_decides_nothing_a_does_not_record'),
    ("read a court's citations by act type alone, not by number and date", 'cordon_d.case_prescriptions',
     "    cited = {act_id(number, year) for number, year, _, _ in printed_identities(' '.join(reason))}\n",
     "    cited = {act_id(number, year) for number, year, printed, _ in printed_identities(' '.join(reason))"
     " if printed is None}\n",
     'test_annex_positions.AnnexPositions.test_a_court_reason_decides_nothing_a_does_not_record'),
    ("keep every court reason's need, A row or not", 'cordon_d.case_prescriptions',
     '            if not _decided_in_a(closure[\'stated_reason\'], record):\n', '            if True:\n',
     'test_annex_positions.AnnexPositions.test_a_court_reason_decides_nothing_a_does_not_record'),
    # The join's rule table (PR #40): one mutation per row family.
    ('count a host-only performance', 'cordon_d.case_prescriptions',
     "    'host-only parcel': {'T<': REPORT, 'T≥': REPORT, 'D<': REPORT, 'D∋': REPORT, 'D>': REPORT, '?': REPORT},\n",
     "    'host-only parcel': {'T<': COUNT, 'T≥': REPORT, 'D<': REPORT, 'D∋': REPORT, 'D>': REPORT, '?': REPORT},\n",
     'test_annex_positions.SuppliedRecordsAtPositions.'
     'test_row_7_a_performance_on_a_host_only_parcel_is_reported_on_any_date'),
    ('hold a parcel-only performance after the deadline', 'cordon_d.case_prescriptions',
     "    'plant parcel': {'T<': HOLD, 'T≥': REPORT, 'D<': HOLD, 'D∋': HOLD, 'D>': REPORT, '?': HOLD},\n",
     "    'plant parcel': {'T<': HOLD, 'T≥': HOLD, 'D<': HOLD, 'D∋': HOLD, 'D>': REPORT, '?': HOLD},\n",
     'test_annex_positions.SuppliedRecordsAtPositions.'
     'test_row_6_a_performance_printed_only_by_the_plants_parcel_holds_only_inside_the_term'),
    ('count a parcel-only performance inside the term', 'cordon_d.case_prescriptions',
     "    'plant parcel': {'T<': HOLD, 'T≥': REPORT, 'D<': HOLD, 'D∋': HOLD, 'D>': REPORT, '?': HOLD},\n",
     "    'plant parcel': {'T<': COUNT, 'T≥': REPORT, 'D<': HOLD, 'D∋': HOLD, 'D>': REPORT, '?': HOLD},\n",
     'test_annex_positions.SuppliedRecordsAtPositions.'
     'test_row_6_a_performance_printed_only_by_the_plants_parcel_holds_only_inside_the_term'),
    ('require the delivery to name the plant', 'cordon_d.case_prescriptions',
     "            deliveries.setdefault(recipient, {}).setdefault(r['event'].occurred, []).append(r['record'])\n",
     "            if position is None or [p for w in r['works'] for p in targets(w)]: "
     "deliveries.setdefault(recipient, {}).setdefault(r['event'].occurred, []).append(r['record'])\n",
     'test_annex_positions.SuppliedRecordsAtPositions.'
     'test_row_2_a_delivery_naming_only_a_host_only_parcel_is_notice_and_the_parcel_is_withdrawn'),
    ('hold a day-only plant record whose day ends before the boundary', 'cordon_d.case_prescriptions',
     "    'plant': {'T<': COUNT, 'T≥': COUNT, 'D<': COUNT, 'D∋': HOLD, 'D>': REPORT, '?': COUNT},\n",
     "    'plant': {'T<': COUNT, 'T≥': COUNT, 'D<': HOLD, 'D∋': HOLD, 'D>': REPORT, '?': COUNT},\n",
     'test_annex_positions.SuppliedRecordsAtPositions.'
     'test_row_5_a_performance_naming_the_plant_counts_by_where_it_falls_against_the_deadline'),
    # The grant at a position (PR #40 round 1).
    ("let a co-holder's delivery outside the grant withhold", 'cordon_d.case_prescriptions',
     "                    or r['kind'] != 'personal-delivery'\n                    and (set(r['works'])",
     "                    or (set(r['works'])",
     'test_osservatorio_records.OsservatorioRecords.'
     'test_a_partial_grant_withholds_what_the_full_evidence_leaves_unresolved'),
    ('key a recipient by its raw printed string', 'cordon_d.case_prescriptions',
     "            recipient = _printed(r['recipient'])", "            recipient = (r['recipient'] or '').strip()",
     'test_annex_positions.SuppliedRecordsAtPositions.'
     'test_through_the_writer_a_narrower_grant_withholds_a_result_at_a_position_and_never_changes_it'),
    # Row 9's instruments besides the register (PR #47): one mutation per rule.
    ('let an area declaration name the plant', 'cordon_d.instruments',
     "            if decl.reading in ('names a tree', 'names a row or group'):\n",
     "            if decl.reading in ('names a tree', 'names a row or group', 'area'):\n",
     'test_instruments.Rules.test_an_area_declaration_gives_no_status'),
    ('read no tree a motivation names', 'cordon_d.instruments',
     "    for reading, pattern in (('names a tree', _NAMES_TREE), ('names a row or group', _NAMES_GROUP)):\n",
     "    for reading, pattern in (('names a row or group', _NAMES_GROUP),):\n",
     'test_instruments.Rules.test_a_tree_the_motivation_names_gets_status'),
    ("let a whole text naming no tree overrule one that names it", 'cordon_d.instruments',
     "    return naming[0] if naming else readings[0]\n", "    return readings[0]\n",
     'test_instruments.Rules.test_a_tree_any_text_names_is_not_overruled_by_a_whole_text_naming_none'),
    ('read a cut motivation as an area', 'cordon_d.instruments',
     "    if len(motivation or '') >= FIELD_LENGTH - 4:\n", "    if False:\n",
     'test_instruments.Rules.test_a_motivation_cut_at_the_field_length_is_not_read_whole'),
    ('ignore the deleting decree', 'cordon_d.instruments', "    if off is True:\n", "    if False:\n",
     'test_instruments.Rules.test_an_entry_deleted_by_a_later_decree_reads_false_after_the_deletion'),
    ("take a decree to have effect on its own date, choosing for A", 'cordon_d.instruments',
     "        if decree.published <= at and decree.adopted <= at:\n", "        if decree.adopted <= at:\n",
     'test_instruments.Rules.test_an_entry_deleted_by_a_later_decree_reads_false_after_the_deletion'),
    ("take a declaration to have effect on its decree's date, choosing for A", 'cordon_d.instruments',
     "        dates = (own.declaration.adopted(), own.declaration.published())\n",
     "        dates = (own.declaration.adopted(),)\n",
     'test_instruments.Rules.test_a_tree_the_motivation_names_gets_status'),
    ('read an entry no held annex lists as not listed', 'cordon_d.instruments',
     "    if entry.listed_by is None:\n        return None, ", "    if entry.listed_by is None:\n        return False, ",
     'test_instruments.Rules.test_an_entry_no_held_annex_lists_is_unknown_not_false'),
    ('place against the zone radius alone', 'cordon_d.instruments',
     "            d = ZONE_M + p.error_m + record.term_m\n", "            d = ZONE_M\n",
     'test_instruments.Rules.test_an_unseen_entry_inside_a_zone_is_admitted_with_its_instrument'),
    ('match an entry of another genus', 'cordon_d.instruments',
     "        near = [e for e in near if genus is None or e.genus is None or e.genus == genus]\n", "",
     'test_instruments.Rules.test_a_plant_near_an_entry_of_another_genus_reads_false_and_of_its_genus_unknown'),
    ("drop the list bound's floor", 'cordon_d.instruments',
     "        return ListBound(round(max(measured or 0.0, LIST_FLOOR_M), 2)",
     "        return ListBound(round(measured or 0.0, 2)",
     'test_instruments.Rules.test_the_list_bound_takes_the_floor_under_twenty_fixes'),
)


def run(case):
    result = unittest.TestResult()
    unittest.defaultTestLoader.loadTestsFromName(case).run(result)
    return result


def loading(mutate):
    original = Snapshot.load.__func__

    def load(cls, *args, **kwargs):
        snapshot = original(cls, *args, **kwargs)
        rows = copy.deepcopy(list(snapshot.versions.values()))
        mutate(rows)
        clone = copy.copy(snapshot)
        clone.versions = {r['provision_version_id']: r for r in rows}
        clone.stable = {}
        for row in rows:
            clone.stable.setdefault(row['stable_provision_id'], []).append(row)
        for versions in clone.stable.values():
            versions.sort(key=lambda row: row['effective_from'])
        return clone
    return classmethod(load)


def main():
    for label, mutate, case in DATA:
        if not run(case).wasSuccessful():
            raise AssertionError(f'Baseline already fails: {case}')
        with mock.patch.object(Snapshot, 'load', loading(mutate)):
            result = run(case)
        if result.testsRun != 1 or result.errors or not result.failures:
            raise AssertionError(f'Regression did not discriminate mutation: {label}: {case}')
        print(f'Discriminated: {label}: {case}')
    for label, name, before, after, case in CODE:
        module = importlib.import_module(name)
        path = Path(module.__file__)
        source = path.read_text()
        if not run(case).wasSuccessful():
            raise AssertionError(f'Baseline already fails: {case}')
        if source.count(before) != 1:
            raise AssertionError(f'Mutation location changed: {name}: {before}')
        namespace = dict(module.__dict__)
        exec(compile(source.replace(before, after), str(path), 'exec'), namespace)
        originals, tables = [], {}
        try:
            for key, value in namespace.items():
                original = module.__dict__.get(key)
                if callable(value) and getattr(value, '__module__', None) == name and hasattr(value, '__code__') \
                        and hasattr(original, '__code__'):
                    originals.append((original, original.__code__))
                    original.__code__ = value.__code__
                elif isinstance(value, dict) and isinstance(original, dict) and value != original:
                    # A mutated module-level table (the join's rule table) replaces the module's for the run.
                    tables[key] = original
                    module.__dict__[key] = value
            result = run(case)
            if result.testsRun != 1 or result.errors or not result.failures:
                raise AssertionError(f'Regression did not discriminate mutation: {label}: {case}')
            print(f'Discriminated: {label}: {case}')
        finally:
            for function, code in originals:
                function.__code__ = code
            module.__dict__.update(tables)


if __name__ == '__main__':
    main()
