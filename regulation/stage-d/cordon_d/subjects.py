"""Observed hosts, qualified inspection units and source-stated cadastral connections.

Every connection retains the observation. Neither a sample code nor a parcel
reference manufactures an individual plant or a complete host population.
"""
from collections import defaultdict
from dataclasses import dataclass, replace
from datetime import date
from hashlib import sha256
from pathlib import Path
import csv
import io
import json
import re

from cordon_c.core import Evaluation
from .hosts import Host, norm, specified_host
from .monitoring import DistinctObservation
from .store import blob_path, store_root
from .correspondence import ReferenceReading
from .evidence import Support


@dataclass(frozen=True)
class ParcelReference:
    comune_code: str | None
    comune: str | None
    province: str | None
    section: str | None
    sheet: str | None
    parcel: str | None
    published_id: str | None
    support: tuple[tuple[str, str], ...]
    issues: tuple[str, ...] = ()

    @property
    def question(self):
        return dict(comune=self.comune, province=self.province, section=self.section,
                    foglio=self.sheet, particella=self.parcel)


class Municipalities:
    def __init__(self, rows, digest):
        self.rows, self.digest = rows, digest

    @classmethod
    def load(cls, root):
        record = json.loads((root/'corpus/sources/host-names/municipalities.json').read_text())
        data = blob_path(store_root(root), record['sha256']).read_bytes()
        if sha256(data).hexdigest() != record['sha256']:
            raise ValueError('Municipality source hash mismatch')
        rows = defaultdict(list)
        for row in csv.DictReader(io.StringIO(data.decode('cp1252')), delimiter=';'):
            rows[row['Codice Catastale del comune']].append(row)
        return cls(rows, record['sha256'])

    def place(self, code):
        values = self.rows.get(code, [])
        if len(values) != 1:
            return None, None
        row = values[0]
        return (row['Denominazione in italiano'].upper(),
                row["Denominazione dell'Unità territoriale sovracomunale \n(valida a fini statistici)"].upper())


def parcel_references(observation, municipalities):
    references = []
    for member in observation.members:
        raw = dict(member.carried)
        if not any(raw.get(k) for k in ('COD_COMUNE', 'FOGLIO', 'PARTICELLA', 'ID_PART')):
            continue
        code, section = raw.get('COD_COMUNE'), raw.get('SEZIONE')
        sheet, parcel = raw.get('FOGLIO'), raw.get('PARTICELLA')
        comune, province = municipalities.place(code)
        issues = []
        if comune and member.attribute('COMUNE') and norm(member.attribute('COMUNE')) != norm(comune):
            issues.append('observation municipality conflicts with its cadastral municipality')
        if not comune:
            issues.append('cadastral municipality code not resolved by the retained ISTAT population')
        support = (member.occurrence, (municipalities.digest, 'Codice Catastale del comune: ' + str(code)))
        printed = raw.get('ID_PART')
        if printed:
            parts = [part.strip() for part in printed.split('-')]
            expected = [code or '', section or '', sheet or '', parcel or '']
            if parts != expected:
                issues.append('published compound cadastral reference disagrees with component fields')
        references.append(ParcelReference(code, comune, province, section, sheet, parcel,
                                          printed, support, tuple(issues)))
    return tuple(references)


@dataclass(frozen=True)
class ObservedSubject:
    observation: DistinctObservation
    host: Host
    parcels: tuple[ParcelReference, ...]
    inspection_unit: tuple | None
    unit_support: tuple[tuple[str, str], ...]
    references: tuple[ReferenceReading, ...] = ()


def observed_subjects(observations, names, municipalities, units=None):
    """One output per input observation, without a polarity or source-family filter."""
    units = units or {}
    for observation in observations:
        labels = observation.values('species')
        host = names.resolve(labels, tuple(m.occurrence for m in observation.members if m.species))
        identity, support = units.get(observation.identity, (None, ()))
        yield ObservedSubject(observation, host, parcel_references(observation, municipalities), identity, support, tuple(subject_references(observation)))


# A literal prior-sample relation, not fuzzy note interpretation. Numeric strings
# embedded in decimal coordinates do not match. No sample number is registered.
_PREVIOUS = re.compile(r'\bid\s+del\s+precedente\s+campione\s+(\d+)(?![\d.,])\b', re.I)


def previous_samples(observation):
    for member in observation.members:
        for field, value in member.attributes:
            if field not in {'NOTE', 'NOTE_RILEVATORE', 'NOTE_SIT'}:
                continue
            for match in _PREVIOUS.finditer(value):
                yield match[1], (member.sha256, member.locator + '/' + field + ': ' + value)


def subject_references(observation):
    """Recover literal reference candidates; no pattern establishes identity."""
    for member in observation.members:
        for field,value in member.attributes:
            if field not in {'NOTE','NOTE_RILEVATORE','NOTE_SIT'}:
                continue
            selector = member.locator+'/'+field
            support = (Support(member.sha256,selector,value),)
            for pattern,role,component in [
                (r'\btarghetta\s+(?:n\.?\s*)?(\d+)(?![\d.,])\b','published-tag-reference','tag'),
                (_PREVIOUS.pattern,'previous-sample-reference','sample-reference'),
                (r'\b(pianta\s+ricampionata)\b','resampling-reference','literal')]:
                for match in re.finditer(pattern,value,re.I):
                    yield ReferenceReading(member.sha256,selector,role,((component,match[1]),),
                                           support,None,observation.day.isoformat() if observation.day else None)


@dataclass(frozen=True)
class InspectionUnitReading:
    """Source-established observation-to-unit membership, supplied by its owner.

    The source must establish the unit's identity scheme and this observation's
    membership in it. A tag candidate or a previous-sample reference is neither.
    No production note parser constructs this type.
    """
    observation: tuple
    unit: tuple[str,str]
    scheme: ReferenceReading
    membership: ReferenceReading

    def __post_init__(self):
        if self.scheme.role != 'inspection-unit-identity-scheme' or self.membership.role != 'observation-unit-membership':
            raise ValueError('Inspection identity needs separate scheme and membership evidence')
        if dict(self.scheme.components).get('namespace') != self.unit[0]:
            raise ValueError('Unit namespace differs from its source scheme')
        components = dict(self.membership.components)
        if (components.get('namespace'), components.get('unit')) != self.unit:
            raise ValueError('Membership differs from its source unit reference')
        if components.get('observation') != json.dumps(self.observation, separators=(',', ':')):
            raise ValueError('Membership must name this exact observation identity')


@dataclass(frozen=True)
class SubjectCorrespondence:
    """A source-supported same/different-subject reading, without a registry.

    This is a semantic reading of direct evidence, not a pattern match or a
    requirement that the source publish a persistent identifier scheme.
    """
    left: tuple
    right: tuple
    same_subject: bool
    support: tuple[Support, ...]

    def __post_init__(self):
        if not self.left or not self.right or self.left == self.right:
            raise ValueError('Correspondence needs two distinct observation identities')
        if type(self.same_subject) is not bool or not self.support or not all(isinstance(s, Support) for s in self.support):
            raise ValueError('Subject correspondence needs a supported direct reading')


def inspection_units(readings, correspondences=()):
    """Reconcile formal identities and sufficient direct subject evidence.

    All evidence survives. Contradictory same/different-subject readings or
    competing formal identities prevent a unit conclusion for their component.
    """
    by_observation = defaultdict(list)
    parent = {}
    def root(observation):
        parent.setdefault(observation, observation)
        head = observation
        while parent[head] != head:
            head = parent[head]
        while parent[observation] != observation:
            previous = parent[observation]
            parent[observation] = head
            observation = previous
        return head
    def connect(left, right):
        a, b = root(left), root(right)
        if a != b:
            parent[b] = a
    for reading in readings:
        if not isinstance(reading, InspectionUnitReading):
            raise TypeError('Literal reference candidates cannot establish inspection units')
        by_observation[reading.observation].append(reading)
        root(reading.observation)
    correspondences = tuple(correspondences)
    for reading in correspondences:
        if not isinstance(reading, SubjectCorrespondence):
            raise TypeError('Direct subject correspondence requires a supported semantic reading')
        root(reading.left); root(reading.right)
        if reading.same_subject:
            connect(reading.left, reading.right)
    formal = defaultdict(list)
    conflicts = set()
    for observation, values in by_observation.items():
        for value in values:
            formal[value.unit].append(observation)
    for observations in formal.values():
        for observation in observations[1:]:
            connect(observations[0], observation)
    components = defaultdict(set)
    for observation in parent:
        components[root(observation)].add(observation)
    for reading in correspondences:
        if not reading.same_subject and root(reading.left) == root(reading.right):
            conflicts.add(reading.left)
    result = {}
    for members in components.values():
        values = [v for observation in members for v in by_observation[observation]]
        direct = [r for r in correspondences if r.left in members or r.right in members]
        support = {s for v in values for r in (v.scheme, v.membership) for s in r.support}
        support.update(s for r in direct for s in r.support)
        identities = {v.unit for v in values}
        schemes = defaultdict(set)
        for namespace, identifier in identities:
            schemes[namespace].add(identifier)
        # A correspondence component is an evidence-scoped inspection unit,
        # not a new permanent plant identifier or a registry entry.
        unit = (next(iter(identities)) if len(identities) == 1 else
                ('subject-correspondence', min(json.dumps(o, separators=(',', ':')) for o in members)))
        if (conflicts & members or any(len(ids) > 1 for ids in schemes.values())
                or (not values and not any(r.same_subject for r in direct))):
            unit = None
        provenance = tuple(sorted((s.source, s.selector + ': ' + s.reading) for s in support))
        for observation in members:
            result[observation] = unit, provenance
    return result


def survey_unit_sets(subjects, *, stratum_of, result_of, period):
    """Count source-connected units; method and population qualifications stay in C.

    result_of supplies the source-qualified result at the survey's own scope:
    True = infection, False = negative, None = unavailable/other. It may use the
    report join; this function never upgrades a monitoring display to confirmation.
    period is the required operative [start, end) observation period.
    Identity correspondence never moves a result to another observation date.
    A missing date remains unavailable within the selected spatial stratum.
    Result availability/knowledge time is separately qualified by result_of.
    """
    if (not isinstance(period, tuple) or len(period) != 2
            or any(type(day) is not date for day in period) or period[0] >= period[1]):
        raise ValueError('Survey observation period requires start < end, end exclusive')
    negatives, positives, unavailable = defaultdict(set), set(), []
    for subject in subjects:
        stratum = stratum_of(subject)
        if stratum is None:
            continue
        day = subject.observation.day
        if day is None:
            unavailable.append(subject.observation.identity)
            continue
        if not period[0] <= day < period[1]:
            continue
        unit = subject.inspection_unit
        result = result_of(subject)
        if result is True:
            # A qualified local detection disproves a negative survey even
            # without a persistent plant identity; it is not a plant count.
            positives.add(unit or ('positive-observation',*subject.observation.identity))
        elif unit is None or result is None:
            unavailable.append(subject.observation.identity)
        elif result is False:
            negatives[stratum].add(unit)
        else:
            raise TypeError('A source-qualified survey result is True, False or None')
    return ({key: frozenset(values) for key, values in negatives.items()},
            frozenset(positives), tuple(unavailable))


def finding_host(joined, names):
    """Read the host of the unambiguous #7 row separately from monitoring's host."""
    if joined.get('status') not in {'matched', 'provisional-match'}:
        return names.resolve(())
    labels, support, unread = set(), [], False
    for candidate in joined['matches']:
        row = candidate['row']
        for cell in row.cells:
            if cell['role'] == 'host':
                if cell.get('role_cause') or cell.get('reading_issues') or not cell.get('text'):
                    unread = True
                else:
                    labels.add(cell['text'])
                    support.append((candidate['key'][0], row.locator + ': ' + cell['text']))
    host = names.resolve(labels, support)
    return replace(host, unresolved=host.unresolved + ('unresolved report host cell',)) if unread else host


def subject_with_finding(subject, joined, names):
    """Refine this observed host with its own unambiguous report host evidence."""
    if subject.observation.identity != joined['observation'].identity:
        raise ValueError('Report host belongs to another observation')
    report_host = finding_host(joined, names)
    if not report_host.labels:
        return subject
    host = names.resolve((*subject.host.labels, *report_host.labels),
                         subject.host.support + report_host.support)
    return replace(subject, host=replace(host, unresolved=tuple(sorted(set(
        host.unresolved + report_host.unresolved)))))


def _area_scope(version, statement):
    """Use the annex's named area before its zone, within one adopted version."""
    heading = re.split(r'\s*[-–—]\s*ZONA\b', statement.zone_heading, flags=re.I)[0]
    if heading == statement.zone_heading:
        return None
    return version.provision_version_id, norm(heading.strip(' -–—'))


@dataclass(frozen=True)
class SubjectMembership:
    area: tuple[str, str] | None
    zone: str
    whole_parcel: Evaluation
    parcel_intersects: Evaluation
    subject_inside: Evaluation
    sources: tuple
    assertions: tuple
    support: tuple[tuple[str, str], ...]


def cadastral_memberships(subject, versions, root, at, *, known_at=None):
    """Compose reported parcel locations with #8, never with invented geometry."""
    from .areas import in_force, membership_evidence
    from .evidence import Source, Support
    # Distinct source references are alternatives. An agreed spelling is not
    # chosen from genuine conflicting cadastral identities.
    keys = {(p.comune_code,p.section,p.sheet,p.parcel) for p in subject.parcels}
    conflict = len(keys) > 1 or any(p.issues for p in subject.parcels)
    output = []
    for reference in subject.parcels:
        if reference.comune is None:
            continue
        sources, assertions = membership_evidence(versions, root, at, **reference.question, known_at=known_at)
        sources += tuple(Source(d, str(blob_path(store_root(root),d).relative_to(store_root(root))),
                                d, 'official-dataset', 'public') for d in sorted({d for d,_ in reference.support}))
        for version in in_force(versions, at):
            for statement in version.statements:
                reached = statement.covers(**reference.question, grain='sheet')
                if reached is not True:
                    continue
                whole = statement.covers(**reference.question, grain='parcel')
                if whole is False:
                    continue
                scope = _area_scope(version, statement)
                matched = tuple(a for a in assertions if a.consumer_version == version.provision_version_id
                                and a.identity.endswith('|' + str(statement.locator)))
                # The published cadastral fields locate the observed subject at
                # that cadastral extent; all publications must agree. A fully
                # included sheet/comune can locate an observation even without
                # a parcel number; partial coverage cannot place it inside.
                inside = True if whole is True and not conflict and matched else None
                reason = 'conflicting cadastral references' if conflict else 'individual subject location within the intersected parcel'
                subject_assertions = tuple(replace(a, context=str(subject.observation.identity),
                    identity=a.identity+'|'+str(subject.observation.identity),
                    support=a.support + tuple(Support(source=d, selector=s,
                        reading='published cadastral location of this observation') for d,s in reference.support))
                    for a in matched) if inside is True else ()
                parcel_named = any(sheet.number == reference.sheet and reference.parcel in sheet.parcels
                                   for sheet in statement.sheets)
                intersects = True if reference.parcel and (whole is True or parcel_named) else None
                output.append(SubjectMembership(scope, statement.zone,
                    Evaluation(True) if whole is True and reference.parcel else Evaluation(None, needs=frozenset({'partial cadastral extent' if reference.parcel else 'identified parcel'})),
                    Evaluation(intersects, needs=frozenset({'parcel location in the intersected sheet'}) if intersects is None else frozenset()),
                    Evaluation(inside, needs=frozenset({reason}) if inside is None else frozenset()),
                    sources, subject_assertions, reference.support))
    return tuple(output)


@dataclass(frozen=True)
class InfectedSpecies:
    finding: tuple
    host: Host
    day: date
    area: tuple[str, str]
    qualification: Evaluation
    support: tuple[tuple[str, str], ...]


def infected_species(joined, names, memberships, *, result_occurrences, confirmed):
    """Use explicitly qualified Xylella result occurrences from the #7 join.

    The caller qualifies the analyte, finding and applicability to the area's
    operative pest scope; heading spellings are
    not canonical pest identities. This admits species and subspecies result
    columns without guessing their meaning from a name fragment.
    """
    from cordon_c.core import conjunction
    host = finding_host(joined, names)
    observation = joined['observation']
    if joined.get('status') not in {'matched', 'provisional-match'}:
        raise ValueError('An unambiguous source relationship is required')
    selected = {tuple(key) for key in result_occurrences}
    recovered = defaultdict(list)
    for candidate in joined.get('matches', ()):
        for result in candidate['row'].results:
            if (candidate['key'][0], result.locator) in selected:
                recovered[(candidate['key'][0], result.locator)].append((candidate, result))
    if selected - set(recovered) or any(len(rows) != 1 for rows in recovered.values()):
        raise ValueError('Xylella results must identify unique joined source occurrences')
    reported = []
    support = []
    for key, ((candidate, result),) in recovered.items():
        usable = candidate['reading_complete'] and not result.cause
        value = (True if result.kind in {'positive','detected'} else
                 False if result.kind in {'negative','not-detected'} else None) if usable else None
        reported.append(value)
        support.append((key[0], result.locator + ': ' + (result.text or '')))
    value = True if True in reported else False if reported and all(v is False for v in reported) else None
    qualification = conjunction([Evaluation(value, needs=frozenset({'qualified reported Xylella result'})
                                             if value is None else frozenset()), confirmed])
    if observation.day is None:
        return ()
    return tuple(InfectedSpecies(observation.identity, host, observation.day, m.area,
                 qualification, host.support + tuple(support) + m.support)
                 for m in memberships if m.area and m.subject_inside.truth is True)


def species_category_facts(snapshot, at, *, subject, finding, names, host_versions,
                           subspecies, plant_for_planting, area, infections,
                           inventory=None):
    """Supply the exact accepted C category inputs in the chosen adopted area."""
    from cordon_c.bindings import eradication_species_facts
    from .evidence import RequiredPopulation
    scope = json.dumps([area, at.isoformat()], separators=(',', ':'))
    if inventory is not None and (area is None or not isinstance(inventory, RequiredPopulation) or inventory.scope != scope):
        raise ValueError('Species inventory must be qualified for this adopted area and event date')
    if inventory is not None and not inventory.members <= {t.species for t in names.taxa.values() if t.species}:
        raise ValueError('Inventory members must be resolved species identities')
    elsewhere = frozenset(record.host.species(names) for record in infections
        if area is not None and record.area == area and record.day <= at and record.finding != finding['observation'].identity
        and record.qualification.truth is True and record.host.species(names) is not None)
    if inventory is not None:
        elsewhere |= inventory.members
    return eradication_species_facts(snapshot, at,
        plant_species=subject.host.species(names), finding_species=finding_host(finding,names).species(names),
        species_found_infected_elsewhere=elsewhere, infected_species_inventory_complete=bool(inventory is not None and inventory.complete),
        specified_plant=specified_host(subject.host,names,host_versions,at,subspecies,plant_for_planting=plant_for_planting))


def observed_subject_survey(snapshot, parameter, at, subjects, *, stratum_labels, stratum_of,
                            result_of, observation_inventory_complete, period, **qualifications):
    from cordon_c.survey import observed_survey_support
    negative,positive,unavailable = survey_unit_sets(subjects,stratum_of=stratum_of,result_of=result_of,period=period)
    if set(negative)-set(stratum_labels):
        raise ValueError('An observed stratum is absent from the survey design')
    return observed_survey_support(snapshot,parameter,at,
        negative_units=tuple(negative.get(label,frozenset()) for label in stratum_labels),positive_units=positive,
        observation_inventory_complete=observation_inventory_complete and not unavailable,**qualifications)
