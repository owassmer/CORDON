"""Mechanical performance boundaries; independent source reading qualifies meaning."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch

from cordon_d.performance import (PerformanceReading, _validate, read_performance,
                                  retained_performance)
from cordon_d.store import put_bytes


class PerformanceTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.store = Path(temporary.name)
        self.source = put_bytes(self.store, b'''<!doctype html><html><body>
          <h1>Authority report</h1><time>20 May 2025</time>
          <article><p id="actual">The director reports prior removal of affected plants.
          The sampling team subsequently inspected the area.</p>
          <p id="planned">Additional removal is planned for next month.</p>
          <p id="verified">Inspection took place on 19 May 2025.</p></article>
          <script id="hidden">Unsupported hidden claim.</script>
          </body></html>''')
        self.other = put_bytes(self.store, b'''<html><body><h1>Earlier report</h1>
          <p id="intended">Removal in the affected zone will take place soon.</p>
          </body></html>''')
        self.reading = dict(documents=[
            dict(source=self.source, issuer='Authority', title='Authority report',
                 published_on=self.day('2025-05-20', 'time', '20 May 2025'),
                 support=[self.cite('h1', 'Authority report')]),
            dict(source=self.other, issuer='Municipality', title='Earlier report',
                 published_on=self.day(),
                 support=[self.cite('h1', 'Earlier report', self.other)])],
            statements=[self.statement(), self.statement(evidence='intended',
                source=self.other, scope_literal='the affected zone',
                support=[self.cite('#intended', 'Removal in the affected zone will take place soon.',
                                   self.other)]),
                self.statement(operation='verification', evidence='direct-record',
                               occurred_on=self.day('2025-05-19', '#verified',
                                                    'Inspection took place on 19 May 2025.'),
                               support=[self.cite('#verified', 'Inspection took place on 19 May 2025.')])],
            issues=[])
        self.response = dict(request=dict(sources=[self.source, self.other],
            source_formats={self.source: 'text/html', self.other: 'text/html'}),
            reading=self.reading, request_sha256='a' * 64)

    def cite(self, locator, quote, source=None):
        return dict(source=source or self.source, locator=locator, quote=quote)

    def day(self, value=None, locator=None, quote=None):
        return dict(value=value, cause=None if value else 'source-not-stated',
                    support=[self.cite(locator, quote)] if value else [])

    def statement(self, **changes):
        result = dict(source=self.source, operation='removal', evidence='reported-event',
            scope_literal='affected plants', performer=dict(value=None, cause='source-not-stated'),
            reported_by=dict(value='the director', cause=None), occurred_on=self.day(),
            time_statement='prior removal',
            support=[self.cite('#actual', 'The director reports prior removal of affected plants.')],
            issues=[dict(aspect='target correspondence', cause='source-not-stated',
                         detail='No individual target identifiers are stated.')])
        result.update(changes)
        return result

    def test_partial_timing_keeps_positive_report_and_its_unattached_scope(self):
        _validate(self.response, self.store)
        reading = PerformanceReading(self.response)
        occurrence, = tuple(reading.removal_occurrences())
        self.assertIs(occurrence['statement'], self.reading['statements'][0])
        self.assertEqual(occurrence['provenance'], 'model_proposed_reading')
        self.assertIsNone(occurrence['statement']['occurred_on']['value'])
        self.assertIsNone(occurrence['statement']['performer']['value'])
        self.assertEqual(occurrence['statement']['reported_by']['value'], 'the director')
        self.assertEqual(occurrence['support'][0].source, self.source)
        self.assertIn('no prescribed-target correspondence', occurrence['attachment_limit'])
        self.assertEqual(len(reading.values['statements']), 3)
        self.assertNotIn('truth', occurrence)
        self.assertNotIn('completed_targets', occurrence)

    def test_intentions_and_other_operations_never_become_actual_removal(self):
        reading = PerformanceReading(self.response)
        for operation, evidence in [('removal', 'intended'), ('treatment', 'direct-record'),
                                    ('verification', 'reported-event'), ('other', 'direct-record')]:
            with self.subTest(operation=operation, evidence=evidence):
                self.response['reading']['statements'] = [self.statement(
                    operation=operation, evidence=evidence)]
                self.assertEqual(tuple(reading.removal_occurrences()), ())
                self.assertEqual(len(reading.values['statements']), 1)
        self.response['reading']['statements'] = [self.statement(evidence='direct-record')]
        self.assertEqual(len(tuple(reading.removal_occurrences())), 1)

    def test_publication_date_cannot_supply_operation_date_support(self):
        statement = self.reading['statements'][0]
        statement['occurred_on'] = deepcopy(self.reading['documents'][0]['published_on'])
        with self.assertRaisesRegex(ValueError, 'Publication-day support alone'):
            _validate(self.response, self.store)
        statement['occurred_on']['support'] = []
        with self.assertRaisesRegex(ValueError, 'requires support'):
            _validate(self.response, self.store)

    def test_missing_values_keep_their_own_cause(self):
        for field in ('performer', 'reported_by', 'occurred_on'):
            with self.subTest(field=field):
                response = deepcopy(self.response)
                response['reading']['statements'][0][field].update(value=None, cause=None)
                with self.assertRaisesRegex(ValueError, 'absence cause'):
                    _validate(response, self.store)
        self.reading['statements'][0]['performer'] = dict(value='someone', cause='not-recovered')
        with self.assertRaisesRegex(ValueError, 'cannot substitute'):
            _validate(self.response, self.store)

    def test_citations_require_their_own_source_and_exact_native_element(self):
        for updates in (dict(source=self.other), dict(locator='p'), dict(locator='#absent'),
                        dict(quote='Removal was completed on 20 May.'), dict(locator=''),
                        dict(locator='#hidden', quote='Unsupported hidden claim.')):
            with self.subTest(updates=updates):
                response = deepcopy(self.response)
                response['reading']['statements'][0]['support'][0].update(updates)
                with self.assertRaises(ValueError):
                    _validate(response, self.store)

    def test_supplied_population_and_source_integrity_are_checked(self):
        response = deepcopy(self.response)
        response['reading']['documents'].pop()
        with self.assertRaisesRegex(ValueError, 'each supplied source'):
            _validate(response, self.store)
        response = deepcopy(self.response)
        response['request']['source_formats'] = {}
        with self.assertRaisesRegex(ValueError, 'explicit native HTML'):
            _validate(response, self.store)

    def test_ordinary_transport_retains_both_sources_and_replays_without_dispatch(self):
        sources = [self.source, self.other]
        with patch('cordon_d.document_subscription._call', return_value=json.dumps(self.reading)) as call:
            reading = read_performance(sources, self.store, execute=True)
            prompt, schema, images, *_ = call.call_args.args
            for source in sources:
                self.assertIn(source, prompt)
            self.assertIn('The sampling team subsequently inspected', prompt)
            self.assertIn('Removal in the affected zone will take place soon.', prompt)
            self.assertEqual(images, [])
            retained = retained_performance(reading.response['request_sha256'], self.store)
            self.assertEqual(retained.response, reading.response)
            self.assertEqual(read_performance(sources, self.store).response, reading.response)
            self.assertEqual(call.call_count, 1)

    def test_unretained_request_does_not_dispatch_without_execution(self):
        with patch('cordon_d.document_subscription._call') as call:
            with self.assertRaises(FileNotFoundError):
                read_performance([self.source, self.other], self.store)
            call.assert_not_called()


if __name__ == '__main__':
    unittest.main()
