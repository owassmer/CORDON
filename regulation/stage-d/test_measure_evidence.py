"""Blank source cells support their selected scope, never unrelated source claims."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cordon_d.measure_sources import source_material
from cordon_d.measures import _validate_reading
from test_source_associations import source


class SelectedBlankEvidence(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.store = Path(temporary.name)
        self.digest = source(self.store, [
            {'rows': [['A', 'R 1', '1/2/2025', 'OWNER A']]},
            {'rows': [['B', 'R 1', '1/2/2025', '']]},
            {'rows': [['C', 'R 1', '1/2/2025', '']]},
        ])
        self.material, _ = source_material([self.digest], self.store)
        fragments = []
        for table_ref in ('S0P1T1', 'S0P2T1'):
            cell = self.material['tables'][table_ref]['rows'][1]['cells'][3]
            fragments.append(dict(table_ref=table_ref, cell=cell))
        self.blank = dict(source=self.digest, page=2, locator='Selected continuation cell', quote='')
        self.values = dict(identity=dict(adopted=None), references=[], events=[], issues=[],
            directions=[dict(id='work')], parts=[], prose_positions=[], image_positions=[],
            target_scopes=[dict(table_ref='S0P2T1', first_row=2, last_row=2,
                columns=[dict(role='addressee', column=4, fragments=fragments)],
                direction_ids=['work'], meaning='Published addressee across pages',
                support=[dict(source=self.digest, page=1, locator='Owner cell', quote='OWNER A'),
                         self.blank])])

    def validate(self, values=None):
        _validate_reading(self.values if values is None else values,
                          [self.digest], self.store, self.material)

    def test_explicit_selected_blank_native_fragment_is_admissible(self):
        self.validate()
        self.blank['locator'] = 'Visible empty continuation, differently worded locator'
        self.validate()  # No interpretation of free-form locator spelling.

    def test_nonblank_unrecovered_unselected_and_other_page_cannot_supply_empty_quote(self):
        reference = self.values['target_scopes'][0]['columns'][0]['fragments'][1]
        cell = self.material['tables'][reference['table_ref']]['cells'][reference['cell']]
        for text in ('ANOTHER OWNER', None):
            with self.subTest(text=text):
                cell['text'] = text
                with self.assertRaisesRegex(ValueError, 'quotation'):
                    self.validate()
        cell['text'] = ''
        for page in (1, 3):
            with self.subTest(unselected_page=page):
                self.blank['page'] = page
                with self.assertRaisesRegex(ValueError, 'quotation'):
                    self.validate()
        self.blank['page'] = 2
        self.values['target_scopes'][0]['columns'][0]['fragments'] = []
        with self.assertRaisesRegex(ValueError, 'quotation'):
            self.validate()

    def test_permission_does_not_escape_its_scope_or_reach_other_claims(self):
        for family in ('identity', 'directions', 'events'):
            with self.subTest(family=family):
                values = deepcopy(self.values)
                # Reusing the same citation object must not transfer scope permission.
                citation = values['target_scopes'][0]['support'][1]
                if family == 'identity':
                    values[family]['support'] = [citation]
                else:
                    values[family].append(dict(support=[citation]))
                with self.assertRaisesRegex(ValueError, 'quotation'):
                    self.validate(values)
        scope = deepcopy(self.values['target_scopes'][0])
        scope['columns'][0]['fragments'] = []
        self.values['target_scopes'].append(scope)
        with self.assertRaisesRegex(ValueError, 'quotation'):
            self.validate()

    def test_blank_support_still_needs_locator_and_full_composition_support(self):
        self.blank['locator'] = ''
        with self.assertRaisesRegex(ValueError, 'quotation'):
            self.validate()
        self.blank['locator'] = 'Blank continuation'
        self.values['target_scopes'][0]['support'] = [self.blank]
        with self.assertRaisesRegex(ValueError, 'every source page'):
            self.validate()


if __name__ == '__main__':
    unittest.main()
