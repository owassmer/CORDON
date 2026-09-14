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
    def test_source_review_rereads_completed_inventory_and_retains_its_reason(self):
        import json
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        import pymupdf
        from cordon_d import report_relations
        from cordon_d.store import put_bytes
        from cordon_d.report_extraction import ExtractionConfig, extract_relationships
        with TemporaryDirectory() as directory:
            store = Path(directory)
            document = pymupdf.open()
            document.new_page().insert_text((40, 40), 'Laboratory A\n31/2024\n01/03/2024\nReport identity')
            digest = put_bytes(store, document.tobytes())
            document.close()
            value = reading().relations
            value.pop('reading_complete')
            target = report_relations.path(store, digest)
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps({'source_sha256': digest,
                'reading_version': report_relations.READING_VERSION, 'complete': True, 'reading': value}))
            config = ExtractionConfig(provider='subscription', effort='high')
            with patch('cordon_d.report_extraction._subscription_call', return_value=value) as call:
                extract_relationships(digest, store, config=config, budget=None,
                                      source_review='Examine correction scope against the source.')
                self.assertEqual(call.call_count, 1)
                self.assertIn('Examine correction scope', call.call_args.kwargs['prompt'])
                extract_relationships(digest, store, config=config, budget=None)
                self.assertEqual(call.call_count, 1)
            self.assertEqual(json.loads(target.read_text())['source_review'],
                             'Examine correction scope against the source.')

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

    def test_analytical_text_does_not_supply_a_registration_role(self):
        # The source reader assigns analytical meaning; projection must not promote
        # a number from another statement to administrative identity.
        identity = dict(protocol=None, component_support={'protocol': []}, support=[
            {'page': 1, 'text': 'protocollo analitico 2010'}])
        self.assertIsNone(project_identity(identity)['protocol'])
        identity['protocol'] = '2010'
        projected = project_identity(identity)
        self.assertIsNone(projected['protocol'])
        self.assertEqual(projected['protocol_proposal'], '2010')

    def test_protocol_projection_checks_component_attachment_not_identifier_shape(self):
        for literal in ('Prot. Selge 17/2018', 'Prot. ABC-123/2024', '3203'):
            with self.subTest(literal=literal):
                identity = dict(protocol=literal, component_support={'protocol': [
                    {'page': 1, 'text': literal}]}, support=[])
                self.assertEqual(project_identity(identity)['protocol'], literal)
        # Even a wrongly assigned role is a reader defect, not something an
        # identifier-format classifier can certify or correct.
        identity = dict(protocol='protocollo analitico 2010', component_support={'protocol': [
            {'page': 1, 'text': 'protocollo analitico 2010'}]})
        self.assertEqual(project_identity(identity)['protocol'], identity['protocol'])
        unsupported = dict(protocol='ABC-123/2024', component_support={'protocol': [
            {'page': 1, 'text': 'Prot. ABC-124/2024'}]}, support=[
            {'page': 2, 'text': 'ABC-123/2024'}])
        self.assertIsNone(project_identity(unsupported)['protocol'])
        split = dict(protocol='ABC-123/2024', component_support={'protocol': [
            {'page': 1, 'text': 'ABC-'}, {'page': 2, 'text': '123/2024'}]})
        self.assertIsNone(project_identity(split)['protocol'])

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

    def test_literal_validation_does_not_require_a_cancellation_catchphrase(self):
        old = reading()
        clause = 'si trasmette il documento corretto con preghiera di voler annullare la precedente comunicazione'
        new = reading(date='04/03/2024', previous=old.relations['identity'])
        new.relations['corrections'][0].update(scope=clause, changed_columns=[],
            support=[{'page': 1, 'text': clause}])
        value = {key: value for key, value in new.relations.items() if key != 'reading_complete'}
        page = 'Laboratory A 31/2024 01/03/2024 04/03/2024 Report identity ' + clause
        result, failures = validated_components(value, [page])
        self.assertEqual(failures, [])
        self.assertEqual(result['corrections'][0]['effect'], 'replaces')
        result, failures = validated_components(value, [page.replace(clause, '')])
        self.assertEqual(result['corrections'], [])
        self.assertTrue(failures)

    def test_date_conflict_does_not_erase_an_explicitly_named_predecessor(self):
        old = reading()
        new = reading(number='32/2024', date='01/03/2023', previous=old.relations['identity'])
        edge, = correspondences({'old': old, 'new': new})
        self.assertEqual(edge['predecessor'], 'old')
        self.assertIn('date_conflict', edge)
        self.assertEqual(edge['successor_identity']['date'], '01/03/2023')
        self.assertEqual(edge['changed_columns'], [])


if __name__ == '__main__':
    unittest.main()
