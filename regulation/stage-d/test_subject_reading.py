"""Reject incorrect imagery readings at the ordinary inspection-unit consumer."""
from dataclasses import asdict, replace
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from test_subjects import observation, names_fixture, subject
from cordon_d.subject_reading import compile_scene, compile_scenes, observation_key, source_view
from cordon_d.subjects import survey_unit_sets


def placed(reference, host='Olea europaea', result='published-negative'):
    row = observation(reference, host=host, result=result)
    return replace(row, members=(replace(row.members[0], coordinates=(690000., 4500000.), crs='EPSG:32633'),))


def proposed(rows, edges):
    """Deliberately permissive proposed readings, to exercise consumer rejection."""
    support = lambda row: dict(source=row.members[0].sha256, selector=row.members[0].locator,
                               reading='A proposed source reading, not a test of source interpretation.')
    context = dict(frames=[], observations=[dict(observation=observation_key(row),
        publications=[asdict(m) for m in row.members], host=dict(taxa=[])) for row in rows])
    result = dict(request=dict(prompt='\nSOURCE CONTEXT\n'+json.dumps(context)+'\nOriginal source images follow'),
        reading=dict(memberships=[dict(observation=observation_key(row), grain='individual-plant',
            subject='one depicted individual', basis='Direct membership claimed',
            temporal_basis='Continuity claimed', alternatives='', support=[support(row)]) for row in rows],
            relations=[dict(left=observation_key(rows[a]), right=observation_key(rows[b]),
                relationship=relation, basis='Direct correspondence claimed', support=[support(rows[a]),support(rows[b])])
                for a,b,relation in edges]))
    for a, b, relation in edges:
        if relation == 'different':
            result['reading']['memberships'][b]['subject'] = 'a separate depicted individual'
    result['request_sha256'] = sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()
    return result


class ImageMembership(unittest.TestCase):
    def setUp(self):
        self.names = names_fixture()

    def consumer(self, rows, units):
        subjects = [subject(row, self.names, units.get(row.identity, (None, ()))[0]) for row in rows]
        subjects = [replace(s, distinct_units=units.distinct_from(s.inspection_unit)) for s in subjects]
        return survey_unit_sets(subjects, period=(date(2023,1,1),date(2024,1,1)),
            stratum_of=lambda _: 'required population', result_of=lambda s: s.observation.positive)

    def test_note_free_direct_reading_connects_repeated_negative_unit(self):
        rows = [placed('earlier'), placed('later')]
        response = proposed(rows, [(0,1,'same')])
        units = compile_scene(response, rows, self.names)
        negative, positive, unavailable = self.consumer(rows, units)
        self.assertEqual(len(negative['required population']), 1)
        self.assertFalse(positive)
        self.assertFalse(unavailable)

    def test_same_crown_cannot_merge_almond_and_olive(self):
        rows = [placed('earlier', 'Prunus dulcis'), placed('later')]
        response = proposed(rows, [(0,1,'same')])
        units = compile_scene(response, rows, self.names)
        negative, _, unavailable = self.consumer(rows, units)
        self.assertFalse(negative)
        self.assertEqual(set(unavailable), {r.identity for r in rows})

    def test_genus_bridge_conflict_is_reconciled_across_scenes(self):
        rows = [placed('almond', 'Prunus dulcis'), placed('genus', 'Prunus'), placed('cherry', 'Prunus avium')]
        first, second = rows[:2], rows[1:]
        units = compile_scenes([(proposed(first, [(0,1,'same')]), first),
                                (proposed(second, [(0,1,'same')]), second)], self.names)
        negative, _, unavailable = self.consumer(rows, units)
        self.assertFalse(negative)
        self.assertEqual(len(unavailable), 3)

    def test_aggregate_missing_time_and_conflicting_positions_do_not_become_units(self):
        rows = [placed('first'), placed('second')]
        response = proposed(rows, [(0,1,'same')])
        response['reading']['memberships'][0]['grain'] = 'aggregate'
        negative, _, unavailable = self.consumer(rows, compile_scene(response, rows, self.names))
        self.assertEqual(len(negative['required population']), 1)
        self.assertEqual(unavailable, (rows[0].identity,))
        population = [replace(rows[0], day=None), rows[1]]
        units = compile_scene(proposed(population, [(0,1,'same')]), population, self.names)
        negative, _, unavailable = self.consumer(population, units)
        self.assertEqual(len(negative['required population']), 1)
        self.assertEqual(unavailable, (population[0].identity,))
        conflicting = replace(rows[0], members=(rows[0].members[0],
                replace(rows[0].members[0], locator='other publication', coordinates=(690030.,4500000.))))
        population = [conflicting, rows[1]]
        units = compile_scene(proposed(population, [(0,1,'same')]), population, self.names)
        self.assertTrue(all(unit is None for unit, _ in units.values()))

    def test_different_reading_survives_and_other_observation_stays_useful(self):
        rows = [placed('negative'), placed('other', result='published-visual-observation')]
        response = proposed(rows, [(0,1,'same')])
        units = compile_scene(response, rows, self.names)
        negative, _, unavailable = self.consumer(rows, units)
        self.assertEqual(len(negative['required population']), 1)
        self.assertEqual(unavailable, (rows[1].identity,))
        opposing = proposed(rows, [(0,1,'different')])
        contested = compile_scenes([(response, rows), (opposing, rows)], self.names)
        self.assertTrue(all(unit is None for unit, _ in contested.values()))

    def test_missing_candidate_or_changed_publication_cannot_replay(self):
        rows = [placed('first'), placed('second')]
        response = proposed(rows, [(0,1,'same')])
        with self.assertRaises(ValueError):
            compile_scene(response, rows[:1], self.names)
        changed = replace(rows[0], members=(replace(rows[0].members[0], species='Prunus dulcis'),))
        with self.assertRaises(ValueError):
            compile_scene(response, [changed,rows[1]], self.names)

    def test_distinct_observation_codes_do_not_establish_different_plants(self):
        rows = [placed('first'), placed('second')]
        unsupported = proposed(rows, [(0,1,'different')])
        for member in unsupported['reading']['memberships']:
            member.update(grain='unresolved', subject=None)
        supported = proposed(rows, [(0,1,'same')])
        units = compile_scenes([(supported, rows), (unsupported, rows)], self.names)
        self.assertEqual(len(self.consumer(rows, units)[0]['required population']), 1)

    def test_separate_same_subject_components_are_not_implicitly_distinct(self):
        from cordon_d.evidence import Support
        from cordon_d.subjects import inspection_units, SubjectCorrespondence
        rows = [placed(str(i)) for i in range(4)]
        support = (Support('source', 'field observations', 'Direct subject correspondence'),)
        edges = [SubjectCorrespondence(rows[0].identity, rows[1].identity, True, support),
                 SubjectCorrespondence(rows[2].identity, rows[3].identity, True, support)]
        ambiguous = inspection_units((), edges)
        self.assertFalse(self.consumer(rows, ambiguous)[0])
        edges.append(SubjectCorrespondence(rows[0].identity, rows[2].identity, False, support))
        distinct = inspection_units((), edges)
        self.assertEqual(len(self.consumer(rows, distinct)[0]['required population']), 2)

    def test_distinctness_is_scoped_after_consumer_population_and_time(self):
        from cordon_d.evidence import Support
        from cordon_d.subjects import DirectSubjectMembership, inspection_units
        rows = [placed('first'), replace(placed('outside-period'), day=date(2020,1,1)), placed('outside-population')]
        support = (Support('field record', 'plant photograph', 'Direct individual membership'),)
        units = inspection_units((), memberships=[DirectSubjectMembership(row.identity,
            ('independent source '+str(i), 'one distinguished plant'), support) for i,row in enumerate(rows)])
        subjects = [replace(subject(row,self.names,units[row.identity][0]),
                            distinct_units=units.distinct_from(units[row.identity][0])) for row in rows]
        negatives,_,unavailable = survey_unit_sets(subjects, period=(date(2023,1,1),date(2024,1,1)),
            stratum_of=lambda s: None if s.observation.reference=='outside-population' else 'required population',
            result_of=lambda s: False)
        self.assertEqual(len(negatives['required population']),1)
        self.assertFalse(unavailable)

    def test_source_view_replays_identical_bytes_without_authored_crowns(self):
        import pymupdf
        from cordon_d.store import put_bytes, blob_path
        with TemporaryDirectory() as temporary:
            store = Path(temporary)/'store'
            image = pymupdf.open()
            page = image.new_page(width=80, height=80)
            source = put_bytes(store, page.get_pixmap().tobytes('png'))
            image.close()
            frame = dict(sha256=source, edition=2023, crs='EPSG:32633',
                         extent=[689960,4499960,690040,4500040], width=80, height=80)
            with patch('cordon_d.subject_reading.store_root', return_value=store), \
                 patch('cordon_d.subject_reading.population_revision', return_value='fixed source revision'):
                args = (Path(temporary), [frame], [placed('first')], self.names)
                a, context = source_view(*args, period=(date(2023,1,1),date(2024,1,1)))
                b, other = source_view(*args, period=(date(2023,1,1),date(2024,1,1)))
            self.assertEqual(a, b)
            self.assertEqual(context, other)
            with pymupdf.open(blob_path(store,a)) as view:
                self.assertEqual(len(view), 2)
                self.assertIn('unmarked original pixels', view[0].get_text())
                self.assertIn('published coordinate marks', view[1].get_text())


class RetainedScenes(unittest.TestCase):
    """Fixed scenes selected by observation identity/date before reading answers.

    Expected memberships were checked against original SIT feature bytes and
    unmarked 2019/2022/2023 images, separately from the source reader's output.
    No extraction is launched by these checks.
    """
    @classmethod
    def setUpClass(cls):
        from cordon_d.hosts import HostNames
        from cordon_d.subjects import Municipalities
        from cordon_d.store import store_root
        cls.root = Path(__file__).resolve().parents[2]
        cls.requests = (
            'b6cf91ef6a2de559021a6423e20888b09868052b4fc1dd9c68b57377a14b8cb9',
            'efdc0fc3e3e62312343a31a2179bb59e16926cd912dc4fb2c11e2927b7e7d141',
            '2c0ac845577ddc3d23fbd4d8e3cc238e02ea59d30e202b986b5cfd120e90aba9')
        if not all((store_root(cls.root)/'derived/document-readings'/(r+'.json')).exists()
                   for r in cls.requests):
            raise unittest.SkipTest('Retained semantic responses are absent from this checkout store')
        cls.names = HostNames.load(cls.root)
        cls.municipalities = Municipalities.load(cls.root)

    def read(self, index):
        from cordon_d.subject_reading import retained_scene
        from cordon_d.subjects import observed_subjects
        scene = retained_scene(self.root, self.requests[index], self.names)
        self.assertIsNotNone(scene[0])
        units = compile_scenes([scene], self.names)
        return list(observed_subjects(scene[1], self.names, self.municipalities, units))

    def test_five_standalone_note_free_olives_reach_C_as_five_units(self):
        from decimal import Decimal
        from cordon_c.core import Snapshot, Evaluation
        from cordon_c.survey import FiniteStratum, observed_survey_support
        from cordon_d.subjects import observed_subject_survey
        subjects = self.read(0)
        self.assertEqual({s.observation.reference for s in subjects if s.inspection_unit},
                         {'1036102','1036115','1036127','1036136','1036148'})
        self.assertEqual(len(subjects), 6)
        unknown = Evaluation(None, needs=frozenset({'official method and complete survey population'}))
        # Inspect the actual C call while preserving its evaluation, including
        # unknown method/population: monitoring negatives are not certification.
        with patch('cordon_c.survey.observed_survey_support', wraps=observed_survey_support) as consumer:
            result = observed_subject_survey(Snapshot.load(self.root), 'B-PAR-EU-6(2)(b)-C95-p1',
                date(2024,11,1), subjects, period=(date(2020,1,1),date(2021,1,1)),
                stratum_labels=('scene',), stratum_of=lambda s:'scene',
                result_of=lambda s:s.observation.positive,
                strata=(FiniteStratum(Decimal(100),1,1,0),), observation_inventory_complete=False,
                population_and_method_qualification=unknown, required_risk_structure=unknown,
                required_performances_complete=unknown, official_method_and_scope=unknown,
                independence_established=False)
        self.assertEqual(tuple(map(len,consumer.call_args.kwargs['negative_units'])), (5,))
        self.assertIsNone(result.truth)
        other = next(s for s in subjects if s.observation.reference=='1036062')
        self.assertIsNone(other.inspection_unit)
        self.assertIsNone(other.observation.positive)

    def test_scrub_visual_observations_keep_taxonomy_without_invented_plants(self):
        subjects = self.read(1)
        self.assertEqual({s.observation.reference for s in subjects}, {'933580','933581'})
        self.assertEqual({code for s in subjects for code in s.host.taxa}, {'CSTIC','PLRLA'})
        self.assertTrue(all(s.inspection_unit is None and s.observation.positive is None for s in subjects))

    def test_nursery_negatives_preserve_samples_without_assigning_nearest_plant(self):
        subjects = self.read(2)
        self.assertEqual(len(subjects), 6)
        self.assertTrue(all(s.inspection_unit is None and s.observation.positive is False for s in subjects))
        self.assertEqual({code for s in subjects for code in s.host.taxa}, {'PLRLA','LURNO'})


if __name__ == '__main__':
    unittest.main()
