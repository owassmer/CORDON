"""Bounded discriminating mutations of the lawful-dueness class (PR #35), in memory.

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
        originals = []
        try:
            for key, value in namespace.items():
                original = module.__dict__.get(key)
                if callable(value) and getattr(value, '__module__', None) == name and hasattr(value, '__code__') \
                        and hasattr(original, '__code__'):
                    originals.append((original, original.__code__))
                    original.__code__ = value.__code__
            result = run(case)
            if result.testsRun != 1 or result.errors or not result.failures:
                raise AssertionError(f'Regression did not discriminate mutation: {label}: {case}')
            print(f'Discriminated: {label}: {case}')
        finally:
            for function, code in originals:
                function.__code__ = code


if __name__ == '__main__':
    main()
