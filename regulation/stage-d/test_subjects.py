"""Observed-subject composition at the accepted C and D consumer surfaces."""
from dataclasses import replace
from datetime import date,datetime,timezone
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
import json
import unittest

from cordon_c.core import Evaluation,Snapshot
from cordon_c.survey import FiniteStratum,observed_survey_support
from cordon_d.hosts import HostNames,Taxon,specified_versions,specified_host
from cordon_d.monitoring import Member,DistinctObservation
from cordon_d.subjects import (ObservedSubject,inspection_units,observed_subjects,survey_unit_sets,
                               species_category_facts,InfectedSpecies,Municipalities,cadastral_memberships,
                               InspectionUnitReading,SubjectCorrespondence,subject_references,finding_host,subject_with_finding,infected_species,observed_subject_survey)

ROOT=Path(__file__).resolve().parents[2]
YES=Evaluation(True)


def observation(reference,day=date(2023,9,18),*,host='Olea europaea',result='published-negative',note=None,parcel=None):
    member=Member('regional monitoring','all observations','source','a'*64,'row:'+reference,
        result,'sample',host,None,None,None,None,None,(),(),
        attributes=(('COMUNE','MONOPOLI'),)+((('NOTE_RILEVATORE',note),) if note else ()),
        carried=tuple((parcel or {}).items()))
    return DistinctObservation(reference,day,(member,))


def names_fixture():
    return HostNames([
        Taxon('1OLVG','Olea','Genus',frozenset({'olea'}),(('Genus','1OLVG'),),('s1',)),
        Taxon('OLVEU','Olea europaea','Species',frozenset({'olea europaea'}),(('Genus','1OLVG'),('Species','OLVEU')),('s2',)),
        Taxon('1PRNG','Prunus','Genus',frozenset({'prunus'}),(('Genus','1PRNG'),),('s3',)),
        Taxon('PRNDU','Prunus dulcis','Species',frozenset({'prunus dulcis','amygdalus communis'}),(('Genus','1PRNG'),('Species','PRNDU')),('s4',)),
        Taxon('PRNAV','Prunus avium','Species',frozenset({'prunus avium'}),(('Genus','1PRNG'),('Species','PRNAV')),('s5',)),
    ])


def subject(group,names,unit=None):
    return ObservedSubject(group,names.resolve(group.values('species')),(),unit,())


def joined(group,label):
    row=SimpleNamespace(locator='page:1/table:1/row:1',cells=[dict(role='host',text=label)])
    return dict(observation=group,status='matched',matches=[dict(row=row,key=('b'*64,row.locator))])


class Composition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.names=names_fixture();cls.snapshot=Snapshot.load(ROOT)
        cls.host_versions=tuple(specified_versions(ROOT))

    def test_general_synonyms_genus_conflict_and_unknown_epithet(self):
        n=self.names
        self.assertEqual(n.resolve(['Amygdalus communis','Prunus dulcis']).species(n),'PRNDU')
        self.assertIsNone(n.resolve(['Prunus L.']).species(n))
        self.assertEqual(n.resolve(['Prunus L.','Prunus dulcis']).species(n),'PRNDU')
        self.assertIsNone(n.resolve(['Prunus avium','Prunus dulcis']).species(n))
        self.assertIsNone(n.resolve(['Prunus invented']).species(n))

    def test_historical_genus_membership_does_not_become_species_identity(self):
        n=self.names;host=n.resolve(['Prunus L.'])
        old=specified_host(host,n,self.host_versions,date(2020,9,1),'pauca',plant_for_planting=YES)
        new=specified_host(host,n,self.host_versions,date(2024,11,1),'pauca',plant_for_planting=YES)
        self.assertTrue(old.truth)
        self.assertTrue(new.truth)
        self.assertIsNone(host.species(n))
        self.assertFalse(specified_host(n.resolve(['unknown']), n, self.host_versions, date(2024,11,1),
                                        'pauca', plant_for_planting=Evaluation(False)).truth)
        self.assertFalse(specified_host(host,n,self.host_versions,date(2020,9,1),'pauca',plant_for_planting=Evaluation(False)).truth)

    def test_species_categories_use_finding_and_area_history_not_subject_result(self):
        n=self.names;day=date(2024,11,1);area=('version','area one')
        plant=subject(observation('negative',host='Prunus dulcis'),n)
        finding=joined(observation('finding',host='Olea europaea'),'Olea europaea')
        infection=InfectedSpecies(('observation','elsewhere','2023-09-18'),n.resolve(['Amygdalus communis']),
                                  date(2023,9,18),area,YES,(('s','row'),))
        args=dict(subject=plant,finding=finding,names=n,host_versions=self.host_versions,
                  subspecies='pauca',plant_for_planting=YES,area=area)
        def category(records):
            facts=species_category_facts(self.snapshot,day,infections=records,**args)
            return {self.snapshot.versions[key[0]]['stable_provision_id']:value.truth for key,value in facts.items()}
        self.assertTrue(category([infection])['EU-2020-1201:7(1)(d)'])
        self.assertIsNone(category([])['EU-2020-1201:7(1)(d)'])
        self.assertIsNone(category([replace(infection,area=('version','different area'))])['EU-2020-1201:7(1)(d)'])
        self.assertIsNone(category([replace(infection,qualification=Evaluation(None))])['EU-2020-1201:7(1)(d)'])
        self.assertIsNone(category([replace(infection,day=date(2025,1,1))])['EU-2020-1201:7(1)(d)'])
        args['finding']=joined(finding['observation'],'Prunus dulcis')
        self.assertTrue(category([])['EU-2020-1201:7(1)(c)'])

    def test_reference_candidates_do_not_establish_identity_or_overwrite(self):
        rows=[observation(str(i),note='targhetta n. 000123; id del precedente campione 321',
                          parcel={'COD_COMUNE':'F376'}) for i in range(3)]
        self.assertEqual({r.role for r in subject_references(rows[0])},
                         {'published-tag-reference','previous-sample-reference'})
        with self.assertRaises(TypeError):inspection_units(subject_references(rows[0]))
        self.assertEqual(inspection_units(()),{})

    def test_source_qualified_units_deduplicate_and_conflicting_readings_survive(self):
        from cordon_d.correspondence import ReferenceReading
        from cordon_d.evidence import Support
        support=(Support('source','scheme','The survey defines each inspection unit by its persistent unit code.'),)
        scheme=ReferenceReading('source','scheme','inspection-unit-identity-scheme',(('namespace','survey'),),support,None)
        rows=[observation(str(i)) for i in range(3)]
        def reading(g,code):
            member=ReferenceReading('source','row:'+g.reference,'observation-unit-membership',(('namespace','survey'),('unit',code),('observation',json.dumps(g.identity,separators=(',', ':')))),
                (Support('source','row:'+g.reference,'Observation of unit '+code),),None)
            return InspectionUnitReading(g.identity,('survey',code),scheme,member)
        with self.assertRaises(ValueError):
            replace(reading(rows[0],'A'), observation=rows[1].identity)
        source_readings=[reading(g,'A') for g in rows]
        units=inspection_units(source_readings)
        subjects=[subject(g,self.names,units[g.identity][0]) for g in rows]
        negatives,positives,unavailable=survey_unit_sets(subjects,period=(date(2023,1,1),date(2024,1,1)),stratum_of=lambda s:'one',result_of=lambda s:False)
        self.assertEqual(len(negatives['one']),1)
        self.assertFalse(unavailable)
        answer=observed_subject_survey(self.snapshot,'B-PAR-EU-6(2)(b)-C95-p1',date(2024,11,1),subjects,
            period=(date(2023,1,1),date(2024,1,1)),stratum_labels=('one',),stratum_of=lambda s:'one',result_of=lambda s:False,
            strata=(FiniteStratum(Decimal(3),1,1,100),),
            observation_inventory_complete=True,population_and_method_qualification=YES,
            required_risk_structure=YES,required_performances_complete=YES,official_method_and_scope=YES,
            independence_established=True)
        self.assertFalse(answer.truth)
        competing=inspection_units([*source_readings,reading(rows[0],'B')])
        self.assertIsNone(competing[rows[0].identity][0])
        self.assertTrue(any('unit A' in text for _,text in competing[rows[0].identity][1]))
        self.assertTrue(any('unit B' in text for _,text in competing[rows[0].identity][1]))
        # Direct evidence cannot silently erase incompatible codes in one scheme.
        from cordon_d.evidence import Support
        cross=SubjectCorrespondence(rows[0].identity,rows[1].identity,True,
            (Support('field','two observations','The same subject was inspected twice.'),))
        conflict=inspection_units([reading(rows[0],'A'),reading(rows[1],'B')],[cross])
        self.assertTrue(all(unit is None for unit,_ in conflict.values()))
        # Different schemes can name the same subject; neither is overwritten.
        other=reading(rows[1],'X')
        other=replace(other,unit=('other-survey','X'),
            scheme=replace(other.scheme,components=(('namespace','other-survey'),)),
            membership=replace(other.membership,components=tuple((k,'other-survey' if k=='namespace' else v)
                for k,v in other.membership.components)))
        aliases=inspection_units([reading(rows[0],'A'),other],[cross])
        self.assertTrue(all(unit is not None for unit,_ in aliases.values()))
        self.assertEqual(aliases[rows[0].identity],aliases[rows[1].identity])

    def test_direct_subject_evidence_needs_no_identifier_scheme(self):
        from cordon_d.evidence import Support
        rows=[observation(str(i)) for i in range(3)]
        first=SubjectCorrespondence(rows[0].identity,rows[1].identity,True,
            (Support('field-record','observations 0 and 1','The two observations concern the same plant.'),))
        second=SubjectCorrespondence(rows[1].identity,rows[2].identity,True,
            (Support('field-record','observations 1 and 2','The later observation is of that same plant.'),))
        units=inspection_units((),[first,second])
        subjects=[subject(g,self.names,units[g.identity][0]) for g in rows]
        negative,_,unavailable=survey_unit_sets(subjects,period=(date(2023,1,1),date(2024,1,1)),stratum_of=lambda s:'one',result_of=lambda s:False)
        self.assertEqual(len(negative['one']),1)
        self.assertFalse(unavailable)
        contradiction=SubjectCorrespondence(rows[0].identity,rows[2].identity,False,
            (Support('correction','observations 0 and 2','These observations concern different plants.'),))
        contested=inspection_units((),[first,second,contradiction])
        self.assertTrue(all(unit is None for unit,support in contested.values()))
        self.assertTrue(all(len(support)==3 for unit,support in contested.values()))

    def test_survey_population_and_period_precede_result_qualification(self):
        unit=('field','one plant')
        rows=[observation('negative',date(2023,7,28)),
              observation('positive',date(2023,9,29),result='published-positive'),
              observation('other',date(2023,7,29),result='published-visual-observation'),
              observation('outside',date(2023,7,28),result='published-positive')]
        subjects=[subject(g,self.names,unit) for g in rows]
        calls=[]
        def result(s):
            calls.append(s.observation.reference)
            return {'negative':False,'positive':True,'other':None}[s.observation.reference]
        scope=lambda s: None if s.observation.reference=='outside' else 'required population'
        period=(date(2023,7,1),date(2023,9,29))
        negative,positive,unavailable=survey_unit_sets(subjects,stratum_of=scope,result_of=result,period=period)
        self.assertEqual(calls,['negative','other'])
        self.assertEqual(negative,{'required population':frozenset({unit})})
        self.assertFalse(positive)
        self.assertEqual(unavailable,(rows[2].identity,))
        kwargs=dict(stratum_labels=('required population',),stratum_of=scope,result_of=result,
            strata=(FiniteStratum(Decimal(3),1,1,0),),observation_inventory_complete=True,
            population_and_method_qualification=YES,required_risk_structure=YES,
            required_performances_complete=YES,official_method_and_scope=YES,independence_established=True)
        answer=observed_subject_survey(self.snapshot,'B-PAR-EU-6(2)(b)-C95-p1',date(2024,11,1),subjects,
            period=period,**kwargs)
        self.assertIsNone(answer.truth)
        answer=observed_subject_survey(self.snapshot,'B-PAR-EU-6(2)(b)-C95-p1',date(2024,11,1),subjects,
            period=(date(2023,7,1),date(2023,9,30)),**kwargs)
        self.assertFalse(answer.truth)
        with self.assertRaises(ValueError):
            survey_unit_sets(subjects,stratum_of=scope,result_of=result,period=None)

    def test_other_and_negative_observations_are_not_filtered(self):
        class NoParcels:
            def place(self,code):return None,None
        rows=[observation('n'),observation('v',result='published-visual-observation'),observation('p',result='published-positive')]
        output=list(observed_subjects(iter(rows),self.names,NoParcels()))
        self.assertEqual([s.observation for s in output],rows)
        self.assertTrue(all(s.inspection_unit is None for s in output))


class RetainedSources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:cls.names=HostNames.load(ROOT);cls.municipalities=Municipalities.load(ROOT)
        except FileNotFoundError as e:raise unittest.SkipTest('Retained source store unavailable: '+str(e))

    def test_structured_common_name_coverage_and_source_defined_genus(self):
        n=self.names
        self.assertIsNone(n.resolve(['FILLIREA']).species(n))
        self.assertEqual(n.resolve(['Fillirea (Phillyrea latifolia)','FILLIREA']).species(n),'PLRLA')
        self.assertEqual(n.resolve(['Vite europea (Vitis L.)']).taxa,frozenset({'1VITG'}))
        self.assertEqual(n.resolve(['Prugno o susina (Prunus L.)']).taxa,frozenset({'1PRNG'}))
        self.assertIsNone(n.resolve(['Asparago']).species(n))
        self.assertEqual(n.resolve(['VITE','Vite europea (Vitis L.)']).taxa, frozenset({'1VITG'}))
        self.assertEqual(n.resolve(['PRUGNO O SUSINA','Prugno o susina (Prunus L.)']).taxa, frozenset({'1PRNG'}))
        self.assertEqual(n.resolve(['Rosmarinus officinalis','Salvia rosmarinus']).species(n),'RMSOF')

    def test_actual_repeated_tag_is_preserved_without_an_invented_identity_scheme(self):
        from cordon_d.store import store_root,blob_path
        from cordon_d.releases import arcgis_occurrences
        from cordon_d.monitoring import observation as read_observation,_reading_row,_member_from_row
        digest='f91638ece421a28f93d2edfe761cab19e05ecf8ac8ce857cccb7d4c94e2581f2'
        store=store_root(ROOT)
        raw=list(arcgis_occurrences(blob_path(store,digest),oid_field='OBJECTID'))
        originals=[r for r in raw if 'targhetta n. 0158330' in (r.values['attributes'].get('NOTE_RILEVATORE') or '')]
        self.assertEqual(len(originals),3)
        groups=[]
        for original in originals:
            reading=read_observation(original,release='retained regional monitoring',view_name='PuntiStampa 2023')
            row=_reading_row(reading,store,0)
            groups.append(DistinctObservation(row['reference'],row['day'],(_member_from_row(row),)))
        self.assertEqual(len({g.identity for g in groups}),3)
        connected=list(observed_subjects(groups,self.names,self.municipalities))
        self.assertTrue(all(s.inspection_unit is None for s in connected))
        self.assertTrue(all(dict(s.references[0].components)['tag']=='0158330' for s in connected))
        negative,positive,unavailable=survey_unit_sets(connected,period=(date(2020,1,1),date(2025,1,1)),stratum_of=lambda s:'one',result_of=lambda s:s.observation.positive)
        self.assertEqual(len(positive),3)
        self.assertFalse(negative)
        self.assertFalse(unavailable)

    def test_annex_time_changes_membership_independently_of_taxonomy(self):
        n=self.names;host=n.resolve(['Pelargonium graveolens'])
        versions=tuple(specified_versions(ROOT))
        self.assertFalse(specified_host(host,n,versions,date(2020,9,1),'pauca',plant_for_planting=YES).truth)
        self.assertTrue(specified_host(host,n,versions,date(2021,10,11),'pauca',plant_for_planting=YES).truth)
        self.assertTrue(specified_host(host,n,versions,date(2024,10,17),'pauca',plant_for_planting=YES).truth)

    def test_original_reports_refine_hosts_and_actual_parcels_reach_consumers(self):
        from cordon_d.store import store_root,blob_path
        from cordon_d.releases import arcgis_occurrences
        from cordon_d.monitoring import observation as read_observation,_reading_row,_member_from_row
        from cordon_d.findings import findings
        from cordon_d.areas import versions
        from cordon_d.evidence import Evidence
        store=store_root(ROOT)
        # Original source records, independently checked against CNR 75/2024,
        # CNR 114/2024, the rosemary confirmation annex and DDS 45/2024 p6.
        digests=['9b7f657f7be111b21ef921c7370e1a8823b51acd3013e3e5a3de9c22873e4b79',
                 'f0ea00236e86d48ca13104d19bdeeeb0317262b08b7b8f80bcaaafeead7399ed']
        requested={'1674936','1675139','1699562','968560','967662'}
        groups=[]
        for digest in digests:
            for raw in arcgis_occurrences(blob_path(store,digest),oid_field='OBJECTID'):
                reading=read_observation(raw,release='retained original',view_name='original source view')
                if reading.observation_reference not in requested:continue
                row=_reading_row(reading,store,0)
                groups.append(DistinctObservation(row['reference'],row['day'],(_member_from_row(row),)))
        self.assertEqual({g.reference for g in groups},requested)
        joined_rows={j['observation'].reference:j for j in findings(groups,ROOT/'corpus/sources/reports',store,
            extraction_version='bf12550befda11586c24',known_through=datetime.now(timezone.utc))}
        for j in joined_rows.values():self.assertIn(j.get('status'),{'matched','provisional-match'})
        n=self.names;subjects={s.observation.reference:s for s in observed_subjects(groups,n,self.municipalities)}
        self.assertIsNone(subjects['1699562'].host.species(n))
        plum=subject_with_finding(subjects['1699562'],joined_rows['1699562'],n)
        self.assertEqual(plum.host.species(n),'PRNDO')
        self.assertEqual(finding_host(joined_rows['968560'],n).species(n),'RMSOF')
        self.assertEqual(finding_host(joined_rows['1674936'],n).species(n),'PRNDU')
        with self.assertRaises(ValueError):subject_with_finding(plum,joined_rows['1674936'],n)
        at=date(2024,5,3);areas=versions(ROOT)
        whole=cadastral_memberships(subjects['1674936'],areas,ROOT,at)
        partial=cadastral_memberships(subjects['1675139'],areas,ROOT,at)
        self.assertTrue(any(m.subject_inside.truth is True for m in whole))
        self.assertTrue(partial)
        self.assertTrue(all(m.subject_inside.truth is None for m in partial))
        self.assertTrue(all(m.parcel_intersects.truth is None for m in partial))
        # A partly included sheet does not even establish that this particular
        # parcel intersects it; the source names only the sheet.
        j=joined_rows['1674936'];source=j['matches'][0]['key'][0]
        positive=(source,'p2/p2-t1/p2-t1-row1/c11')
        negative=(source,'p2/p2-t1/p2-t1-row1/c10')
        detected=infected_species(j,n,whole,result_occurrences=[positive],confirmed=YES)
        not_detected=infected_species(j,n,whole,result_occurrences=[negative],confirmed=YES)
        self.assertTrue(detected and all(r.qualification.truth is True for r in detected))
        self.assertTrue(not_detected and all(r.qualification.truth is False for r in not_detected))
        unresolved=infected_species(j,n,whole,result_occurrences=[positive],confirmed=Evaluation(None))
        self.assertTrue(all(r.qualification.truth is None for r in unresolved))
        sources={v.identity:v for m in whole for v in m.sources}
        assertions={v.identity:v for m in whole for v in m.assertions}
        contracts={v['id']:v for v in json.loads((ROOT/'regulation/stage-d/contracts.json').read_text())['contracts']}
        bindings={}
        for b in json.loads((ROOT/'regulation/stage-d/predicate-contracts.json').read_text())['bindings']:
            bindings.setdefault(b['predicate'],set()).update(b['contracts'])
        snapshot=Snapshot.load(ROOT)
        evidence=Evidence(snapshot,tuple(sources.values()),tuple(assertions.values()),contracts,bindings,store)
        self.assertTrue(assertions)
        for a in assertions.values():
            self.assertTrue(evidence.view(context=a.context,event_date=at,known_through=datetime.now(timezone.utc)).reader(
                snapshot.versions[a.consumer_version],a.predicate).truth)
        facts=species_category_facts(snapshot,plum.observation.day,subject=plum,finding=joined_rows['1699562'],
            names=n,host_versions=tuple(specified_versions(ROOT)),subspecies='multiplex',plant_for_planting=YES,
            area=None,infections=())
        self.assertTrue(next(v for k,v in facts.items() if snapshot.versions[k[0]]['stable_provision_id']=='EU-2020-1201:7(1)(c)').truth)
        # The source gives a rosemary finding and a separate olive finding.
        # At this event the adopted annex includes their published Ostuni parcel.
        # YES below exercises the explicit qualification interface; this test
        # does not certify the Service's official finding or Article 7 applicability.
        event=date(2025,2,1);rosemary=subjects['968560'];rose_join=joined_rows['968560']
        rose_memberships=cadastral_memberships(rosemary,areas,ROOT,event)
        chosen=next(m for m in rose_memberships if m.area and m.subject_inside.truth is True)
        result_key=('05f2cecd4c120b81af84ae4de766275d6c42f1fc34e06848d27134aaf089910a','p2/p2-t1/r15/c7')
        args=dict(subject=rosemary,finding=joined_rows['967662'],names=n,host_versions=tuple(specified_versions(ROOT)),
                  subspecies='pauca',plant_for_planting=YES,area=chosen.area)
        def other_species(qualification):
            records=infected_species(rose_join,n,rose_memberships,result_occurrences=[result_key],confirmed=qualification)
            facts=species_category_facts(snapshot,event,infections=records,**args)
            return next(v for k,v in facts.items() if snapshot.versions[k[0]]['stable_provision_id']=='EU-2020-1201:7(1)(d)')
        self.assertTrue(other_species(YES).truth)
        self.assertIsNone(other_species(Evaluation(None)).truth)


    def test_actual_adopted_parcel_scope_reaches_the_evidence_consumer(self):
        from cordon_d.areas import versions
        from cordon_d.evidence import Evidence
        n=self.names
        # DDS 8/2024 Annex: Triggiano foglio 5, 818* is wholly contained;
        # 817 is listed without *. Both are source statements, not invented maps.
        groups=[observation('test-'+parcel,day=date(2024,2,24),parcel={'COD_COMUNE':'L425','FOGLIO':'5','PARTICELLA':parcel,
                                                                  'ID_PART':'L425- -5-'+parcel}) for parcel in ('818','817')]
        groups=[replace(g,members=(replace(g.members[0],attributes=(('COMUNE','TRIGGIANO'),)),)) for g in groups]
        subjects=list(observed_subjects(groups,n,self.municipalities))
        readings=[cadastral_memberships(s,versions(ROOT),ROOT,date(2024,2,24)) for s in subjects]
        self.assertTrue(any(m.subject_inside.truth is True for m in readings[0]))
        self.assertFalse(any(m.subject_inside.truth is True for m in readings[1] if m.zone=='infetta'))
        self.assertTrue(any(m.parcel_intersects.truth is True and m.whole_parcel.truth is None
                            for m in readings[1] if m.zone=='infetta'))
        sources={s.identity:s for m in readings[0] for s in m.sources}
        assertions={a.identity:a for m in readings[0] for a in m.assertions}
        contracts=json.loads((ROOT/'regulation/stage-d/contracts.json').read_text())['contracts']
        bindings={}
        for b in json.loads((ROOT/'regulation/stage-d/predicate-contracts.json').read_text())['bindings']:
            bindings.setdefault(b['predicate'],set()).update(b['contracts'])
        # Materialize the synthetic observation source in a temporary store;
        # preserve every support through the ordinary Evidence reader.
        from tempfile import TemporaryDirectory
        from hashlib import sha256
        from cordon_d.store import store_root,blob_path
        with TemporaryDirectory() as directory:
            target=Path(directory)
            fixture=json.dumps([dict(members=[dict(g.members[0].carried)]) for g in groups]).encode()
            digest=sha256(fixture).hexdigest()
            old='a'*64
            for identity,source in list(sources.items()):
                if identity==old:
                    sources.pop(old)
                    sources[digest]=replace(source,identity=digest,sha256=digest,
                                            path=str(blob_path(target,digest).relative_to(target)))
                    dest=blob_path(target,digest);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(fixture)
                else:
                    dest=target/source.path;dest.parent.mkdir(parents=True,exist_ok=True)
                    dest.write_bytes((store_root(ROOT)/source.path).read_bytes())
            assertions={key:replace(a,support=tuple(replace(x,source=digest) if x.source==old else x for x in a.support))
                        for key,a in assertions.items()}
            evidence=Evidence(Snapshot.load(ROOT),tuple(sources.values()),tuple(assertions.values()),
                              {c['id']:c for c in contracts},bindings,target)
            for a in assertions.values():
                result=evidence.view(context=a.context,event_date=a.event_date,known_through=datetime.now(timezone.utc)).reader(
                    evidence.snapshot.versions[a.consumer_version],a.predicate)
                self.assertTrue(result.truth)



if __name__=='__main__':unittest.main()
