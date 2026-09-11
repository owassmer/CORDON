"""Distinct observations across releases, and the shapes C's entry points take."""
from datetime import date, datetime, timezone
import gzip
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from openpyxl import Workbook

from cordon_c.core import Evaluation, MissingInput
from cordon_c.survey import observed_survey_support
from cordon_c.temporal import no_detection_anchor
from cordon_d.evidence import file_digest
from cordon_d.monitoring import distinct_observations, detection_days, occasion_sets, located_positives, ingest, observations, reader_version
from cordon_d.store import audit, blob_path, derived_path, store_root
from cordon_d.spatial import metric_point


def local_midnight_ms(year, month, day):
    # Early SIT epochs encode Puglia midnight as 23:00 UTC of the prior day.
    return int(datetime(year, month, day - 1, 23, tzinfo=timezone.utc).timestamp() * 1000)


def build_root(directory):
    root = Path(directory) / 'monitoring'
    campaign = root / 'campaign'
    campaign.mkdir(parents=True)
    book = Workbook()
    sheet = book.active
    sheet.append(['ID', 'DATA_RILEVAMENTO', 'TIPOLOGIA', 'SPECIE', 'CULTIVAR', 'LATITUDINE', 'LONGITUDINE',
                  'COMUNE', 'RISULTATO', 'SINTOMO'])
    for row in [
        [101, datetime(2022, 3, 4), 'Campione', 'Olivo', None, 40.5, 17.5, 'A', 'POSITIVO', 'Presente'],
        [101, datetime(2022, 3, 10), 'Campione', 'Olivo', None, 40.5, 17.5, 'A', 'NEGATIVO', 'Assente'],
        [202, datetime(2022, 3, 4), 'Campione', 'Olivo', None, 40.6, 17.6, 'A', 'POSITIVO', 'Assente'],
        [202, datetime(2022, 3, 4), 'Campione', 'Olivo', None, 40.7, 17.7, 'A', 'NEGATIVO', 'Assente'],
        [None, datetime(2022, 3, 5), 'Campione', 'Mandorlo', None, 40.8, 17.8, 'A', 'NEGATIVO', 'Assente'],
        [None, datetime(2022, 3, 5), 'Campione', 'Mandorlo', None, 40.8, 17.8, 'A', 'NEGATIVO', 'Assente'],
        [303, datetime(2022, 3, 6), 'Campione', 'Olivo', None, 40.9, 17.9, 'A', 'POSITIVO DUPLICATO', 'Assente'],
        [404, datetime(2022, 3, 7), 'Campione', 'Olivo', None, 41.0, 18.0, 'A', 'NEGATIVO', 'Assente'],
        [505, datetime(2022, 3, 8), 'Campione', 'Olivo', None, 41.1, 18.1, 'A', 'POSITIVO DUPLICATO', 'Assente'],
        [606, datetime(2022, 3, 9), 'Campione', 'Olivo', None, 41.2, 18.2, 'A', 'POSITIVO', 'Assente'],
    ]:
        sheet.append(row)
    book.save(campaign / 'camp.xlsx')
    (campaign / 'camp.csv').write_text(
        'ID;DATA_RILEVAMENTO;TIPOLOGIA;SPECIE;CULTIVAR;LATITUDINE;LONGITUDINE;COMUNE;RISULTATO;SINTOMO;PROVINCIA\n'
        '101;04/03/2022;Campione;Olivo;;40,5;17,5;A;POSITIVO;Presente;TA\n', encoding='latin-1')
    releases = [
        {'url': 'http://publisher/camp.xlsx', 'path': 'camp.xlsx', 'captured_at': 'x',
         'sha256': file_digest(campaign / 'camp.xlsx')},
        {'url': 'http://publisher/camp.csv', 'path': 'camp.csv', 'captured_at': 'x',
         'sha256': file_digest(campaign / 'camp.csv'), 'encoding': 'latin-1', 'delimiter': ';'},
    ]
    (campaign / 'releases.json').write_text(json.dumps(releases))
    layer = root / 'sit' / 'Operationals2' / 'View' / '1'
    layer.mkdir(parents=True)
    features = [
        {'attributes': {'OBJECTID': 1, 'ID_CAMPIONE': '101', 'DATA_CAMPIONE': local_midnight_ms(2022, 3, 4),
                        'RISULTATO': 'Positivo', 'SPECIE': 'Olivo', 'TIPOLOGIA': 'Campione',
                        'DOCUMENTO_CONFERMA': 'https://publisher/report-101.pdf'},
         'geometry': {'x': 600000.0, 'y': 4500000.0}},
        {'attributes': {'OBJECTID': 2, 'ID_CAMPIONE': '303', 'DATA_CAMPIONE': local_midnight_ms(2022, 3, 6),
                        'RISULTATO': 'Positivo', 'SPECIE': 'Olivo', 'TIPOLOGIA': 'Campione'},
         'geometry': {'x': 610000.0, 'y': 4510000.0}},
        {'attributes': {'OBJECTID': 3, 'ID_CAMPIONE': '606', 'DATA_CAMPIONE': local_midnight_ms(2022, 3, 9),
                        'RISULTATO': 'Negativo', 'SPECIE': 'Olivo', 'TIPOLOGIA': 'Campione'},
         'geometry': {'x': 620000.0, 'y': 4520000.0}},
        # An early-style view: one counter value for two different plants on one day.
        {'attributes': {'OBJECTID': 4, 'ID_CAMPIONE': '1', 'DATA_CAMPIONE': local_midnight_ms(2022, 3, 11),
                        'RISULTATO': 'Negativo', 'SPECIE': 'Oleandro'},
         'geometry': {'x': 630000.0, 'y': 4530000.0}},
        {'attributes': {'OBJECTID': 5, 'ID_CAMPIONE': '1', 'DATA_CAMPIONE': local_midnight_ms(2022, 3, 11),
                        'RISULTATO': 'Positivo', 'SPECIE': 'Olivo'},
         'geometry': {'x': 640000.0, 'y': 4540000.0}},
    ]
    page = layer / '00000000.json.gz'
    page.write_bytes(gzip.compress(json.dumps({'features': features, 'spatialReference': {'wkid': 32633}}).encode()))
    (layer / 'layer.json').write_text('{}')
    (layer / 'release.json').write_text(json.dumps({
        'url': 'https://webapps.sit.puglia.it/arcgis/rest/services/Operationals2/View/MapServer/1',
        'name': 'Positivi - Campioni 2022 sub. pauca', 'oid_field': 'OBJECTID', 'rows': 5, 'unique_oids': 5,
        'pages': [{'path': page.name, 'sha256': file_digest(page)}]}))
    return root


class ObservationStream(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = TemporaryDirectory()
        cls.root = build_root(cls.directory.name)
        cls.groups = list(distinct_observations(cls.root))
        cls.by_reference = {}
        for group in cls.groups:
            cls.by_reference.setdefault(group.reference, []).append(group)

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_same_reference_and_day_is_one_observation_across_workbook_csv_and_view(self):
        march_fourth, march_tenth = sorted(self.by_reference['101'], key=lambda g: g.day)
        self.assertEqual(len(march_fourth.members), 3)
        self.assertEqual({m.view for m in march_fourth.members},
                         {'camp.xlsx', 'camp.csv', 'Positivi - Campioni 2022 sub. pauca'})
        self.assertEqual(march_fourth.result, 'published-positive')
        self.assertTrue(march_fourth.positive)
        self.assertEqual(march_fourth.disagreements, ())
        self.assertEqual(dict(march_fourth.locations), {None: (17.5, 40.5), 'EPSG:32633': (600000.0, 4500000.0)})
        self.assertEqual(march_fourth.report_routes, ('https://publisher/report-101.pdf',))
        self.assertEqual(len(march_tenth.members), 1)
        self.assertFalse(march_tenth.positive)

    def test_a_value_one_view_gives_several_rows_on_one_day_is_a_counter_not_a_reference(self):
        self.assertNotIn('202', self.by_reference)
        self.assertNotIn('1', self.by_reference)
        reused = [g for g in self.by_reference[None]
                  if g.uncorrelated_because == 'reference reused within its publishing view on this day']
        self.assertEqual(len(reused), 4)  # two workbook rows and two view rows
        self.assertEqual(sorted(g.positive for g in reused), [False, False, True, True])
        self.assertTrue(all(len(g.members) == 1 and g.day is not None for g in reused))

    def test_cross_release_disagreement_is_exposed_not_merged_or_chosen(self):
        group, = self.by_reference['606']
        self.assertEqual({m.view for m in group.members}, {'camp.xlsx', 'Positivi - Campioni 2022 sub. pauca'})
        self.assertEqual(group.disagreements, ('result',))
        self.assertIsNone(group.result)
        self.assertIsNone(group.positive)
        self.assertEqual(len(group.locations), 2)  # each frame agrees with itself; the result does not

    def test_observations_without_a_reference_stay_separate_even_at_the_same_place(self):
        unreferenced = [g for g in self.by_reference[None] if g.uncorrelated_because == 'no publisher reference']
        self.assertEqual(len(unreferenced), 2)
        self.assertNotEqual(unreferenced[0].identity, unreferenced[1].identity)
        self.assertTrue(all(not g.correlatable and g.positive is False and g.day == date(2022, 3, 5)
                            for g in unreferenced))

    def test_duplicate_label_restates_a_positive_but_is_not_one_by_itself(self):
        restated, = self.by_reference['303']
        self.assertTrue(restated.positive)
        self.assertEqual(restated.result, 'published-positive')
        alone, = self.by_reference['505']
        self.assertIsNone(alone.positive)

    def test_detection_days_count_each_observation_once_and_exclude_disagreements(self):
        # 4 March: 101 (three publications) and one reused-counter positive; 6 March: 303; 11 March: a counter positive.
        self.assertEqual(detection_days(self.groups), (date(2022, 3, 4), date(2022, 3, 6), date(2022, 3, 11)))
        self.assertEqual(detection_days(self.groups, select=lambda g: g.correlatable), (date(2022, 3, 4), date(2022, 3, 6)))

    def test_occasion_sets_are_observation_identities_split_by_agreed_result(self):
        sets = occasion_sets(self.groups, lambda g: g.day.month)
        self.assertEqual(set(sets), {3})
        self.assertEqual(len(sets[3]['positive']), 4)  # 101, 303, and two reused-counter positives
        self.assertEqual(len(sets[3]['negative']), 6)  # 101 on 10 March, 404, two unreferenced, two reused-counter negatives
        self.assertEqual(len(sets[3]['other']), 2)     # the cross-release disagreement and the duplicate-only label
        self.assertTrue(sets[3]['positive'].isdisjoint(sets[3]['negative']))

    def test_c_entry_points_take_the_candidates_and_refuse_to_conclude_without_the_missing_inputs(self):
        with self.assertRaises(MissingInput):
            no_detection_anchor(date(2022, 1, 1), detection_days(self.groups), date(2022, 12, 31),
                                detection_record_complete=False)
        sets = occasion_sets(self.groups, lambda g: g.day.month)[3]
        given = dict(population_and_method_qualification=Evaluation(True), required_risk_structure=Evaluation(True),
                     required_performances_complete=Evaluation(True), official_method_and_scope=Evaluation(True),
                     independence_established=False, observation_inventory_complete=False)
        with_positives = observed_survey_support(None, '', date(2022, 3, 31), strata=(), negative_units=(),
                                                 positive_units=sets['positive'], **given)
        self.assertIs(with_positives.truth, False)
        without = observed_survey_support(None, '', date(2022, 3, 31), strata=(), negative_units=(sets['negative'],),
                                          positive_units=frozenset(), **given)
        self.assertIsNone(without.truth)
        self.assertTrue(any('complete usable observation inventory' in need for need in without.needs))

    def test_located_positives_carry_sources_but_no_spatial_support(self):
        located = list(located_positives(self.groups))
        self.assertEqual(len(located), 6)  # 101: two frames; 303: two frames; two reused-counter positives, one frame each
        for observation in located:
            self.assertEqual(observation.support, ())
            self.assertTrue(all(s.role == 'official-dataset' for s in observation.sources))
            for source in observation.sources:
                source.verify(store_root(self.root))
            with self.assertRaises(MissingInput):
                metric_point(observation, context='test', event_date=date(2022, 3, 4), root=store_root(self.root))

    def test_bytes_live_in_the_store_once_and_the_tree_keeps_only_records(self):
        store = store_root(self.root)
        self.assertEqual(store.resolve(), (Path(self.directory.name) / 'store').resolve())
        self.assertFalse((self.root / 'campaign' / 'camp.xlsx').exists())
        for record in json.loads((self.root / 'campaign' / 'releases.json').read_text()):
            self.assertTrue(blob_path(store, record['sha256']).is_file())
        digests = {m.sha256 for g in self.groups for m in g.members}
        self.assertEqual(len(digests), 3)  # workbook, CSV, one view page
        self.assertTrue(all(blob_path(store, d).stat().st_mode & 0o222 == 0 for d in digests))

    def test_derived_files_are_keyed_by_reader_version_and_a_stale_one_is_not_read(self):
        store = store_root(self.root)
        digest = next(iter({m.sha256 for g in self.groups for m in g.members if m.view == 'camp.csv'}))
        current = derived_path(store, 'monitoring/readings', digest, reader_version())
        self.assertTrue(current.is_file())
        stale = derived_path(store, 'monitoring/readings', digest, 'stale000000')
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.write_bytes(b'not parquet')
        self.assertEqual(sum(1 for o in observations(self.root) if o.view_name == 'camp.csv'), 1)

    def test_audit_fails_on_a_corrupted_blob(self):
        store = store_root(self.root)
        self.assertEqual(audit(store), [])
        digest = next(iter({m.sha256 for g in self.groups for m in g.members if m.view == 'camp.csv'}))
        blob = blob_path(store, digest)
        blob.chmod(0o644)
        original = blob.read_bytes()
        try:
            blob.write_bytes(original + b'\n')
            self.assertEqual(audit(store), [blob])
        finally:
            blob.write_bytes(original)
            blob.chmod(0o444)
        self.assertEqual(audit(store), [])


if __name__ == '__main__':
    unittest.main()
