"""Declared act correspondence preserves source scope, ambiguity and old readings."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

import pymupdf
from jsonschema import Draft202012Validator, ValidationError

from cordon_d.measure_sources import source_material, material_context
from cordon_d.measures import MeasureReading, SCHEMA, _validate_reading, retained_measure
from cordon_d.store import put_bytes


def citation(source='principal', quote='source-stated act reference'):
    return dict(source=source, page=1, locator='operative clause', quote=quote)


def act(number='315', year='2025', adopted=None, **changes):
    value = dict(issuer='Sezione Osservatorio Fitosanitario', authority='puglia-osservatorio',
                 number=number, year=year, adopted=adopted, support=[citation()])
    return value | changes


def reference(*acts, relationship='incorporates', payload='stated predecessor work', documents=()):
    return dict(identity_literal='literal reference is not executable', relationship=relationship,
                affected_payload=payload, support=[citation()], acts=list(acts), documents=list(documents))


def reading(source='predecessor', number='315', adopted='2025-04-17', authority='puglia-osservatorio',
            references=(), plants=()):
    values = dict(identity=dict(issuer='Sezione Osservatorio Fitosanitario', authority=authority,
        number=number, adopted=adopted, title='source title', support=[citation(source)]),
        directions=[], parts=[], target_scopes=[], prose_positions=[], image_positions=[],
        references=list(references), events=[], issues=[])
    material = dict(tables={}, lines={}, images={}, pages={})
    if plants:
        values['directions'] = [dict(id='removal', mode='ordered-now', work='removal', scope='source scope',
            recipients='published addressees', conditions='', timing='', authority_references=[],
            support=[citation(source)])]
        values['parts'] = [dict(label='act', source=source, pages=[1], role='act', incorporation='',
                                qualifications='', support=[citation(source)])]
        material['pages']['S0P1'] = dict(source=source, page=1, bbox=[0, 0, 100, 100])
        for plant in plants:
            values['image_positions'].append(dict(image_ref='S0P1', association_ref=None,
                fields=[dict(role='plant_id', transcription=plant)], direction_ids=['removal'],
                meaning='source position', support=[citation(source)]))
    return MeasureReading(dict(reading=values, request=dict(sources=[source]),
                               request_sha256=source+'-request'), material, ())


class MeasureReferenceCorrespondence(unittest.TestCase):
    def test_new_number_resolves_without_case_registration_and_preserves_originals(self):
        for number, year in [('731', '2023'), ('902', '2026')]:
            with self.subTest(number=number):
                declared = act(number, year)
                ref = reference(declared)
                predecessor = reading(number=number, adopted=year+'-02-03')
                principal = reading('principal', references=[ref])
                result, = principal.referenced_measures([predecessor])
                self.assertIs(result['reference'], ref)
                self.assertIs(result['act'], declared)
                self.assertIs(result['reading'], predecessor)
                self.assertIs(result['candidates'][0], predecessor)
                self.assertIsNone(result['cause'])

    def test_office_year_and_date_cannot_be_replaced_by_number_agreement(self):
        predecessor = reading()
        for declared in [act(year='2024'), act(authority='other'),
                         act(adopted='2025-04-18'), act(year='2024', adopted='2025-04-17')]:
            with self.subTest(declaration=declared):
                result, = reading('principal', references=[reference(declared)]).referenced_measures([predecessor])
                self.assertIsNone(result['reading'])
                self.assertTrue(result['cause'])
        result, = reading('principal', references=[reference(act(adopted='2025-04-18'))]).referenced_measures([predecessor])
        self.assertIs(result['conflicts'][0]['reading'], predecessor)
        self.assertIn('adoption date', result['conflicts'][0]['cause'])
        other = reading(authority='other')
        result, = reading('principal', references=[reference(act())]).referenced_measures([other])
        self.assertIsNone(result['reading'])

    def test_unknown_components_stay_unknown_and_prose_never_supplies_them(self):
        predecessor = reading()
        for missing in ['number', 'year']:
            declared = act(**{missing: None})
            before = deepcopy(declared)
            ref = reference(declared)
            ref['identity_literal'] = 'Sezione Osservatorio Fitosanitario DDS 315/2025 del 17/04/2025'
            result, = reading('principal', references=[ref]).referenced_measures([predecessor])
            self.assertIsNone(result['reading'])
            self.assertIn(missing, result['cause'])
            self.assertEqual(declared, before)
        declared = act(year=None, adopted='2025-04-17')
        result, = reading('principal', references=[reference(declared)]).referenced_measures([predecessor])
        self.assertIs(result['reading'], predecessor)
        self.assertIsNone(declared['year'])

    def test_supported_authority_resolves_without_a_duplicate_literal_issuer(self):
        predecessor = reading()
        declared = act(issuer=None)
        before = deepcopy(declared)
        principal = reading('principal', references=[reference(declared)])
        result, = principal.referenced_measures([predecessor])
        self.assertIs(result['reading'], predecessor)
        self.assertIsNone(result['cause'])
        self.assertEqual(declared, before)
        for authority in ['unresolved', 'other']:
            with self.subTest(authority=authority):
                declared['authority'] = authority
                result, = principal.referenced_measures([predecessor])
                self.assertIsNone(result['reading'])
                self.assertIn('authority', result['cause'])
                self.assertIsNone(declared['issuer'])
        declared['authority'] = 'puglia-osservatorio'
        declared['support'] = []
        result, = principal.referenced_measures([predecessor])
        self.assertIsNone(result['reading'])
        self.assertIn('source support', result['cause'])

    def test_two_renditions_are_ambiguous_and_explicit_date_can_discriminate(self):
        first, second = reading('first'), reading('second')
        principal = reading('principal', references=[reference(act())])
        result, = principal.referenced_measures([first, second])
        self.assertIsNone(result['reading'])
        self.assertEqual(result['candidates'], (first, second))
        self.assertIn('ambiguous', result['cause'])
        second.values['identity']['adopted'] = '2025-04-18'
        principal.values['references'][0]['acts'][0]['adopted'] = '2025-04-17'
        result, = principal.referenced_measures([first, second])
        self.assertIs(result['reading'], first)
        self.assertIs(result['conflicts'][0]['reading'], second)

    def test_missing_predecessor_does_not_suppress_independent_correspondences(self):
        declared = [act(str(number)) for number in range(310, 320)]
        predecessors = [reading(str(number), str(number)) for number in range(310, 319)]
        results = reading('principal', references=[reference(*declared)]).referenced_measures(predecessors)
        self.assertEqual([r['reading'] for r in results[:9]], predecessors)
        self.assertIsNone(results[-1]['reading'])
        self.assertIn('no supplied measure reading', results[-1]['cause'])

    def test_partial_correction_keeps_scope_and_both_target_owners(self):
        correction = reference(act(), relationship='corrects', payload='addressee for one stated parcel only')
        supplement = reference(act(), relationship='supplements', payload='separate conditional work')
        predecessor = reading(plants=['old one', 'unaffected two'])
        principal = reading('principal', references=[correction, supplement], plants=['corrected one'])
        prior_state = deepcopy(predecessor.values)
        current_state = deepcopy(principal.values)
        results = principal.referenced_measures([predecessor])
        self.assertEqual(len(results), 2)
        self.assertIs(results[0]['reference'], correction)
        self.assertIs(results[1]['reference'], supplement)
        self.assertIs(results[0]['reading'], predecessor)
        self.assertEqual(principal.values, current_state)
        self.assertEqual(predecessor.values, prior_state)
        self.assertEqual([t['reference'] for t in principal.prescribed_targets()], ['corrected one'])
        self.assertEqual([t['reference'] for t in predecessor.prescribed_targets()], ['old one', 'unaffected two'])

    def test_selected_documents_resolve_principal_hash_and_do_not_turn_reports_into_gaps(self):
        selected = dict(source='predecessor', support=[citation(), citation('predecessor')])
        ref = reference(documents=[selected])
        del ref['acts']
        predecessor = reading()
        principal = reading('principal', references=[ref])
        result, = principal.referenced_measures([predecessor])
        self.assertIs(result['reading'], predecessor)
        self.assertIs(result['selection'], selected)
        unrelated = reading('another-principal')
        unrelated.response['request']['sources'].append('predecessor')
        result, = principal.referenced_measures([unrelated])
        self.assertIsNone(result['reading'])
        self.assertIn('no supplied principal', result['cause'])
        for relationship in ['laboratory-evidence', 'governing-law']:
            ref['relationship'] = relationship
            self.assertEqual(principal.referenced_measures([]), ())
        missing = reading(adopted=None)
        ref['relationship'] = 'incorporates'
        result, = principal.referenced_measures([missing])
        self.assertIsNone(result['reading'])
        self.assertIs(result['candidates'][0], missing)
        self.assertIn('adoption date', result['cause'])

    def test_hash_selection_cannot_bypass_explicit_identity_contradiction(self):
        selected = dict(source='predecessor', support=[citation(), citation('predecessor')])
        declared = act(year='2024', adopted='2025-04-17')
        principal = reading('principal', references=[reference(declared, documents=[selected])])
        results = principal.referenced_measures([reading()])
        self.assertTrue(all(r['reading'] is None for r in results))
        self.assertTrue(all(r['cause'] for r in results))

    def test_conflicting_selection_does_not_suppress_independent_act_correspondences(self):
        selected = dict(source='unrelated', support=[citation(), citation('unrelated')])
        ref = reference(act(number='316'), act(number='317'), documents=[selected],
                        payload='the exact work stated by this reference')
        first, second = reading('first', number='316'), reading('second', number='317')
        unrelated = reading('unrelated', number='900')
        principal = reading('principal', references=[ref])
        before = deepcopy(principal.values)
        results = principal.referenced_measures([first, unrelated, second])
        self.assertIs(results[0]['reading'], first)
        self.assertIs(results[1]['reading'], second)
        self.assertTrue(all(r['cause'] is None for r in results[:2]))
        conflict = results[2]
        self.assertIsNone(conflict['reading'])
        self.assertIs(conflict['reference'], ref)
        self.assertIs(conflict['selection'], selected)
        self.assertIs(conflict['candidates'][0], unrelated)
        self.assertIs(conflict['conflicts'][0]['reading'], unrelated)
        self.assertIn('conflicts with every declared act identity', conflict['cause'])
        self.assertEqual(principal.values, before)

    def test_old_prose_reference_stays_unresolved_without_a_new_source_reading(self):
        ref = reference()
        del ref['acts']
        del ref['documents']
        ref['identity_literal'] = 'DDS 315/2025'
        result, = reading('principal', references=[ref]).referenced_measures([reading()])
        self.assertIsNone(result['reading'])
        self.assertIn('no structured act identity', result['cause'])


class RetainedReferenceCompatibility(unittest.TestCase):
    def test_old_response_replays_with_actual_source_addresses_and_is_not_patched(self):
        with TemporaryDirectory() as directory:
            store = Path(directory)
            with pymupdf.open() as document:
                page = document.new_page()
                page.insert_text((50, 50), 'Act cites DDS 315/2025 for predecessor work.')
                digest = put_bytes(store, document.tobytes())
            ref = reference()
            del ref['acts']
            del ref['documents']
            ref['support'] = [citation(digest)]
            old = reading(digest, references=[ref])
            material, _ = source_material([digest], store)
            old.response['request']['prompt'] = material_context(material)
            before = deepcopy(old.response)
            with patch('cordon_d.measures.read_retained', return_value=old.response):
                actual = retained_measure('old-request', store)
            self.assertIs(actual.response, old.response)
            self.assertEqual(actual.response, before)
            self.assertNotIn('acts', actual.values['references'][0])
            result, = actual.referenced_measures([reading()])
            self.assertIsNone(result['reading'])

    def test_schema_accepts_unknown_components_but_not_short_years_or_absent_citations(self):
        value = reading('principal', references=[reference(act(issuer=None, number=None, year=None))]).values
        Draft202012Validator(SCHEMA).validate(value)
        value['references'][0]['acts'][0]['year'] = '25'
        with self.assertRaises(ValidationError):
            Draft202012Validator(SCHEMA).validate(value)
        with TemporaryDirectory() as directory:
            store = Path(directory)
            with pymupdf.open() as document:
                document.new_page()
                digest = put_bytes(store, document.tobytes())
            value = reading(digest, references=[reference(act())]).values
            ref = value['references'][0]
            ref['support'] = [citation(digest)]
            ref['acts'][0]['support'] = []
            with self.assertRaisesRegex(ValueError, 'source support'):
                _validate_reading(value, [digest], store, {})


if __name__ == '__main__':
    unittest.main()
