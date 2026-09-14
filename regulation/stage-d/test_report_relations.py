"""Identity and correction graph boundaries; no provider access."""
from types import SimpleNamespace
import unittest

from cordon_d.report_relations import (correspondences, validate, validated_components, project_identity,
                                       current_limitation)


def reading(number='31/2024', date='01/03/2024', *, issuer='Laboratory A', previous=None, effect='replaces'):
    component_support = {
        'issuer': [{'page': 1, 'text': issuer}] if issuer else [],
        'number': [{'page': 1, 'text': number}] if number else [],
        'date': [{'page': 1, 'text': date}] if date else [],
        'protocol': [],
    }
    identity = dict(issuer=issuer, number=number, date=date, protocol=None,
                    issuer_labels=[{'value': issuer, 'support': component_support['issuer']}] if issuer else [],
                    component_support=component_support,
                    support=[{'page': 1, 'text': 'Report identity'}])
    corrections = [] if previous is None else [dict(predecessor=previous, effect=effect,
        scope='Cancels and replaces the preceding report', changed_columns=['Client code'],
        support=[{'page': 1, 'text': 'Cancels and replaces the preceding report'}])]
    return SimpleNamespace(relations=dict(identity=identity, corrections=corrections,
                                          limitations=[], reading_complete=True))


class ReportRelationships(unittest.TestCase):
    def test_explicit_replacement_and_abbreviated_year_keep_source_identity(self):
        old = reading()
        target = dict(old.relations['identity'], number='31/24')
        new = reading(date='04/03/2024', previous=target)
        edge, = correspondences({'old': old, 'new': new})
        self.assertEqual(edge['predecessor'], 'old')
        self.assertEqual(edge['declared_predecessor']['number'], '31/24')
        self.assertEqual(edge['successor'], 'new')

    def test_later_date_and_same_number_alone_do_not_create_replacement(self):
        self.assertEqual(correspondences({'old': reading(), 'later': reading(date='04/03/2024')}), [])

    def test_different_issuer_and_conflicting_protocol_are_not_correspondence(self):
        old = reading(); old.relations['identity']['protocol'] = '101'
        target = dict(old.relations['identity'], protocol='102')
        new = reading(previous=target)
        self.assertIsNone(correspondences({'old': old, 'new': new})[0]['predecessor'])
        target['protocol'] = None
        old.relations['identity']['issuer'] = 'Laboratory B'
        old.relations['identity']['issuer_labels'] = [{
            'value': 'Laboratory B', 'support': [{'page': 1, 'text': 'Laboratory B'}]}]
        self.assertIsNone(correspondences({'old': old, 'new': new})[0]['predecessor'])

    def test_multiple_renditions_remain_ambiguous(self):
        old = reading(); new = reading(date='04/03/2024', previous=old.relations['identity'])
        edge, = correspondences({'old': old, 'another': reading(), 'new': new})
        self.assertIsNone(edge['predecessor'])
        self.assertEqual(edge['candidates'], ['another', 'old'])

    def test_amendment_is_not_whole_report_replacement(self):
        old = reading(); new = reading(date='04/03/2024', previous=old.relations['identity'], effect='amends')
        self.assertEqual(correspondences({'old': old, 'new': new})[0]['effect'], 'amends')

    def test_cyclic_readings_do_not_cancel_both_reports(self):
        first, second = reading(date=None), reading(date=None)
        first.relations['corrections'] = reading(previous=second.relations['identity']).relations['corrections']
        second.relations['corrections'] = reading(previous=first.relations['identity']).relations['corrections']
        edges = correspondences({'first': first, 'second': second})
        self.assertTrue(all(e['predecessor'] is None and 'cyclic' in e['cause'] for e in edges))

    def test_method_protocol_is_never_a_document_registration_identifier(self):
        value = dict(protocol='Example et al. (2020)', support=[
            {'page': 1, 'text': 'analisi eseguite con protocollo Example et al. (2020)'}])
        projected = project_identity(value)
        self.assertIsNone(projected['protocol'])
        self.assertEqual(projected['protocol_proposal'], value['protocol'])
        value = dict(protocol='3203', support=[{'page': 1, 'text': 'Prot. N. 3203'}])
        self.assertEqual(project_identity(value)['protocol'], '3203')

    def test_missing_candidate_protocol_is_exposed_without_defeating_unique_report_identity(self):
        old = reading()
        new = reading(date='04/03/2024', previous=dict(old.relations['identity'], protocol='170245'))
        edge, = correspondences({'old': old, 'new': new})
        self.assertEqual(edge['predecessor'], 'old')
        self.assertEqual(edge['status'], 'resolved')
        self.assertEqual(edge['unobserved_candidate_components'], ['protocol'])

    def test_contained_issuer_label_does_not_establish_institutional_identity(self):
        old = reading(issuer='Unit Laboratory A')
        new = reading(date='04/03/2024', previous=dict(old.relations['identity'], issuer='Laboratory A'))
        new.relations['corrections'][0]['predecessor']['issuer_labels'] = [{
            'value': 'Laboratory A', 'support': [{'page': 1, 'text': 'Laboratory A'}]}]
        edge, = correspondences({'old': old, 'new': new})
        self.assertIsNone(edge['predecessor'])
        self.assertNotEqual(edge['status'], 'resolved')

    def test_competing_replacements_cannot_both_be_current(self):
        old = reading()
        first = reading(date='04/03/2024', previous=old.relations['identity'])
        second = reading(date='05/03/2024', previous=old.relations['identity'])
        edges = correspondences({'old': old, 'first': first, 'second': second})
        self.assertIn('competing', current_limitation(edges, 'first'))
        self.assertIn('competing', current_limitation(edges, 'second'))

    def test_native_quote_validation_rejects_fabricated_support(self):
        value = {key: value for key, value in reading().relations.items()
                 if key != 'reading_complete'}
        validate(value, ['Laboratory A 31/2024 01/03/2024 Report identity'])
        with self.assertRaisesRegex(ValueError, 'quote'):
            validate(value, ['A different source'])

    def test_text_layer_confirms_but_cannot_refute_on_an_image_bearing_page(self):
        value = {key: value for key, value in reading().relations.items() if key != 'reading_complete'}
        # Split values, glued punctuation and interleaved columns in a text layer still confirm.
        self.assertEqual(validate(value, ['Laboratory - A 31 / 2024 01/03/2024 Report identity']), [])
        # Unconfirmed on a page whose text layer is the whole page: refuted.
        with self.assertRaisesRegex(ValueError, 'quote'):
            validate(value, ['A different source'], [False])
        # Unconfirmed on a page that also carries an image: retained, and said so.
        notes = validate(value, ['A different source'], [True])
        self.assertTrue(notes)
        self.assertTrue(all('not confirmed by the text layer' in note for note in notes))

    def test_issuer_outside_its_labels_is_recorded_not_rejected(self):
        value = {key: value for key, value in reading().relations.items() if key != 'reading_complete'}
        value['identity']['issuer_labels'] = [{'value': 'Lab A', 'support': [{'page': 1, 'text': 'Lab A'}]}]
        notes = validate(value, ['Laboratory A 31/2024 01/03/2024 Report identity Lab A'])
        self.assertTrue(any('not among the issuer labels' in note for note in notes))

    def test_reference_without_annex_wording_is_a_reference_not_a_rejected_correction(self):
        old = reading()
        new = reading(date='04/03/2024', previous=old.relations['identity'], effect='annex')
        new.relations['corrections'][0].update(scope='Same data as the preceding report', changed_columns=[],
            support=[{'page': 1, 'text': 'Same data as the preceding report'}])
        value = {key: value for key, value in new.relations.items() if key != 'reading_complete'}
        page = 'Laboratory A 31/2024 01/03/2024 04/03/2024 Report identity Same data as the preceding report'
        result, failures = validated_components(value, [page])
        self.assertEqual(failures, [])
        self.assertEqual(result['corrections'], [])
        self.assertEqual(len(result['references']), 1)
        self.assertIn('cross-reference', result['references'][0]['cause'])
        # The same wording claimed as an amendment is consequential, and is rejected.
        value['corrections'][0]['effect'] = 'amends'
        result, failures = validated_components(value, [page])
        self.assertEqual(result['corrections'], [])
        self.assertTrue(failures and 'not explicit' in failures[0])


if __name__ == '__main__':
    unittest.main()
