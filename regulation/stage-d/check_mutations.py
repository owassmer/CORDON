"""Bounded discriminating mutations of the lawful-dueness class (PR #35), of the join's rule
table (PR #40) and of row 9's naming-record rule (PR #48), in memory.

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
    # Row 9's naming records (PR #48): one mutation per rule.
    ('let a record naming a candidate not decide it', 'cordon_d.protection',
     "        return Candidates(plant, tuple(within), next(iter(entries), noted), '; '.join(said))\n",
     "        return Candidates(plant, tuple(within), 'unknown', '; '.join(said))\n",
     'test_protection.NamingRecords.'
     'test_a_record_naming_the_one_candidate_decides_it_and_the_other_plants_keep_it_marked'),
    ('drop a candidate a record names for another plant', 'cordon_d.protection',
     "                                    if marks[e['entry']] else e for e in p['candidates']['entries']]\n",
     "                                    if False else e for e in p['candidates']['entries'] if not marks[e['entry']]]\n",
     'test_protection.NamingRecords.'
     'test_a_record_naming_the_one_candidate_decides_it_and_the_other_plants_keep_it_marked'),
    ('let an entry beyond d within 50 m decide', 'cordon_d.protection',
     '        return BEYOND if exact <= PAIRING_M else FAR, round(exact, 2), d_of(plant, entry)\n',
     '        return WITHIN if exact <= PAIRING_M else FAR, round(exact, 2), d_of(plant, entry)\n',
     'test_protection.NamingRecords.test_an_entry_beyond_d_within_50_m_makes_the_identity_unknown_and_never_decides'),
    ('take an entry that prints no point for another tree', 'cordon_d.protection',
     '            return UNPLACED, None, d_of(plant, entry)\n', '            return FAR, None, d_of(plant, entry)\n',
     'test_protection.NamingRecords.test_an_entry_beyond_d_within_50_m_makes_the_identity_unknown_and_never_decides'),
    ('let a record naming an entry beyond 50 m change the identity', 'cordon_d.protection',
     '        return BEYOND if exact <= PAIRING_M else FAR, round(exact, 2), d_of(plant, entry)\n',
     '        return BEYOND, round(exact, 2), d_of(plant, entry)\n',
     'test_protection.NamingRecords.test_an_entry_beyond_50_m_is_a_conflict_and_the_identity_is_unchanged'),
    ('let a tag or COD naming several entries name the first', 'cordon_d.protection',
     '            if len(one) == 1:\n', '            if one:\n',
     'test_protection.NamingRecords.test_a_repeated_cod_or_a_card_repeated_in_its_comune_names_nothing'),
    ('decide an entry named for several plants', 'cordon_d.protection', '    elif named_elsewhere:\n',
     '    elif False:\n',
     'test_protection.NamingRecords.test_an_entry_named_for_several_plants_decides_for_none'),
    ('decide where records disagree', 'cordon_d.protection', '    elif len(entries) > 1:\n', '    elif False:\n',
     'test_protection.NamingRecords.test_records_that_disagree_decide_nothing'),
    ('let a record overrule the note', 'cordon_d.protection',
     '    elif entries and codes and {c.entry for c in codes} != entries:\n', '    elif False:\n',
     'test_protection.NamingRecords.test_a_record_and_the_note_that_disagree_decide_nothing'),
    ('let a reference naming separate plants decide', 'cordon_d.protection',
     '        cause = SEPARATE if len({plants[p].printer for p in mine}) > 1 else NO_PLANT if not all(named) else None\n',
     '        cause = NO_PLANT if not all(named) else None\n',
     'test_protection.NamingRecords.test_a_reference_naming_separate_plants_decides_nothing_and_is_reported'),
    ('let a record outside the grant name an entry', 'cordon_d.protection', '        if need is not None:\n',
     '        if False:\n', 'test_protection.NamingRecords.test_a_record_outside_the_grant_names_nothing'),
    ('read a printed comune upper-cased only, as the note-code rule did', 'cordon_d.protection',
     "    return ' '.join(text.split()).upper().replace(\"' \", \"'\").rstrip(\"'\")\n",
     "    return str(text or '').strip().upper()\n", 'test_protection.NamingRecords.test_one_reader_of_a_printed_card'),
    ('attach a group row 9 reads and does not decide', 'cordon_d.landscape',
     "            if n['cause'] == WITHIN and n['entries'] != [p['candidates']['identity']]:\n", '            if False:\n',
     'test_landscape.LandscapeRecords.test_a_register_entry_against_a_decided_plant_or_one_that_is_not_a_register_tree'),
    ("attach through PR #30's identity without the run's records", 'cordon_d.landscape',
     '    rows = named_rows(rows, register, supplied, evaluated_at=evaluated_at, zone=zone,\n',
     '    rows = named_rows(rows, register, [], evaluated_at=evaluated_at, zone=zone,\n',
     'test_landscape.LandscapeRecords.test_a_negative_olive_whose_identity_is_unknown'),
    ('let a record outside the grant that could change an identity withhold nothing in row 10', 'cordon_d.landscape',
     "        for need in identities.needs.get(plant, ()):\n", "        for need in ():\n",
     'test_landscape.LandscapeRecords.test_an_ungranted_record_withholds_what_it_could_change_and_shows_nothing_else'),
    ('withhold an ungranted record only for the plants its references name', 'cordon_d.protection',
     '            reached |= {plant for plant, placed in plants.items() if set(entries) & {oid for oid, _, _ in '
     'placed.within}}\n', '',
     'test_protection.NamingRecords.test_a_record_outside_the_grant_names_nothing'),
    # PR #48 implementation review round 1.
    ("let a note-decided plant keep an entry a record names for another plant", 'cordon_d.protection',
     '        if noted and not others({noted}):\n', '        if noted:\n',
     'test_protection.NamingRecords.test_a_note_and_a_record_naming_one_entry_for_two_plants_leave_both_unknown'),
    ("leave a note-decided plant out of the rule when its entry is named for another plant", 'cordon_d.protection',
     "        if any(n.cause != FAR for n in naming) or marks.get(candidate['identity']):\n",
     "        if any(n.cause != FAR for n in naming):\n",
     'test_protection.NamingRecords.test_a_note_and_a_record_naming_one_entry_for_two_plants_leave_both_unknown'),
    ("let a group whose parcel is not the entry's decide", 'cordon_d.protection',
     '                (PARCEL_DISAGREES, False in agree),', '                (PARCEL_DISAGREES, False),',
     'test_protection.NamingRecords.test_a_group_whose_parcel_or_other_identifier_disagrees_decides_nothing'),
    ("let an entry whose parcel this reader does not read confirm one", 'cordon_d.protection',
     '    if parcel(entry.comune, entry.foglio, entry.particella) is None:\n', '    if False:\n',
     'test_protection.NamingRecords.test_a_group_whose_parcel_or_other_identifier_disagrees_decides_nothing'),
    ("call a record's parcel this reader does not read a disagreement", 'cordon_d.protection',
     "    if parcel(form['comune'], form['foglio'], form['particella']) is None:\n", '    if False:\n',
     'test_protection.NamingRecords.test_a_group_whose_parcel_or_other_identifier_disagrees_decides_nothing'),
    ("report an unread entry parcel in row 10 as the entry printing none", 'cordon_d.landscape',
     '                else parcel_unread(form, identities.entries[identity]))) for form in outcome',
     "                else f'entry {identity} prints no parcel')) for form in outcome",
     'test_landscape.LandscapeRecords.test_a_register_entry_against_a_decided_plant_or_one_that_is_not_a_register_tree'),
    ('let a group whose other tag or COD names another entry decide', 'cordon_d.protection',
     "                (KEYS_DISAGREE, any(entry.oid not in {e.oid for e in one} for one in hits)),",
     "                (KEYS_DISAGREE, False),",
     'test_protection.NamingRecords.test_a_group_whose_parcel_or_other_identifier_disagrees_decides_nothing'),
    ("take a run's rows as PR #30's", 'cordon_d.protection', '    as_written(rows)\n', '',
     'test_protection.ReadProtectionRun.test_a_runs_rows_fed_back_through_read_landscape_are_refused'),
    ('reach a plant an ungranted record names beside an entry beyond 50 m', 'cordon_d.protection',
     '                       if not cause and placement(plant, entry)[0] != FAR}\n', '                       if not cause}\n',
     'test_protection.NamingRecords.test_a_record_outside_the_grant_names_nothing'),
    ('reach the plants holding an entry of a tag or COD that names several', 'cordon_d.protection',
     '            if len(one) == 1:\n', '            if one:\n',
     'test_protection.NamingRecords.test_a_record_outside_the_grant_names_nothing'),
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
