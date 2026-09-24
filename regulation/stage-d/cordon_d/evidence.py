"""Carry source values into accepted A–C without changing their scope."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from hashlib import sha256
from pathlib import Path
from collections.abc import Mapping
import json

from cordon_c.core import Evaluation, MissingInput, Snapshot, evaluate


def file_digest(path: Path) -> str:
    digest = sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def instant(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError('Evidence knowledge time requires a timezone-aware instant')
    return value


@dataclass(frozen=True)
class Source:
    identity: str
    path: str
    sha256: str
    role: str
    access: str

    def verify(self, root: Path):
        path = (root / self.path).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError('Source must be inside the supplied source root')
        if file_digest(path) != self.sha256:
            raise ValueError(f'Source changed: {self.identity}')
        if self.role not in {'official-record', 'official-dataset', 'qualified-observation',
                             'official-format'}:
            raise ValueError(f'Unclassified source role: {self.role}')
        if self.access not in {'public', 'controlled'}:
            raise ValueError('Source access must be public or controlled')


@dataclass(frozen=True)
class Support:
    source: str
    selector: str
    reading: str

    def __post_init__(self):
        if not self.source or not self.selector or not self.reading:
            raise ValueError('Support requires a source, exact locator and semantic reading')


@dataclass(frozen=True)
class Assertion:
    identity: str
    contract: str
    context: str
    event_date: date
    known_at: datetime
    consumer_version: str
    predicate: str
    value: bool
    support: tuple[Support, ...]
    supersedes: tuple[str, ...] = ()

    def __post_init__(self):
        if type(self.event_date) is not date or type(self.value) is not bool:
            raise TypeError('A factual reading requires an explicit event date and boolean value')
        instant(self.known_at)
        if not all((self.identity, self.contract, self.context, self.consumer_version, self.predicate, self.support)):
            raise ValueError('A factual reading must identify its exact consumer, context and evidence')

    @property
    def key(self):
        return self.context, self.event_date, self.consumer_version, self.predicate


def require_admissible(contract: dict, sources):
    """Every source's role is one the contract admits for an instance fact."""
    permitted = set(contract['admissible_instance_roles'])
    for source in sources:
        if source.role not in permitted:
            raise ValueError(f'{source.role} does not establish an instance fact under {contract["id"]}')


class Evidence:
    def __init__(self, snapshot: Snapshot, sources: tuple[Source, ...], assertions: tuple[Assertion, ...],
                 contracts: Mapping[str, dict], bindings: Mapping[str, frozenset[str]], root: Path):
        self.snapshot, self.root = snapshot, root
        # The D owner controls admission even for direct construction and custom
        # evidence roots; caller-supplied family bindings cannot widen aperture.
        owner = Path(__file__).resolve().parents[1] / 'predicate-contracts.json'
        self.deferred_consumers = json.loads(owner.read_text())['deferred_consumers']
        self.sources = {source.identity: source for source in sources}
        self.assertions = {row.identity: row for row in assertions}
        if len(self.sources) != len(sources) or len(self.assertions) != len(assertions):
            raise ValueError('Duplicate source or assertion identity')
        for source in sources:
            source.verify(root)
        for row in assertions:
            owner = snapshot.version(row.consumer_version, row.event_date)
            self.require_admitted(owner['provision_version_id'])
            if row.consumer_version != owner['provision_version_id']:
                raise ValueError('Assertion requires the exact event-time provision version')
            if row.contract not in contracts or row.contract not in bindings.get(row.predicate, ()):
                raise ValueError('Assertion is outside the authored consumer contract')
            from cordon_c.bindings import leaves
            if row.predicate not in set(leaves(owner['condition_ast'])):
                raise ValueError('Assertion predicate is not owned by its event-time A version')
            require_admissible(contracts[row.contract], [self.sources[s.source] for s in row.support])
            for predecessor in row.supersedes:
                previous = self.assertions[predecessor]
                if previous.key != row.key or previous.known_at >= row.known_at:
                    raise ValueError('Correction must concern the same fact and follow its predecessor')

    def require_admitted(self, consumer_version: str):
        if consumer_version in self.deferred_consumers:
            raise ValueError(f'D consumer is deferred: {consumer_version}; '
                             f'{self.deferred_consumers[consumer_version]}')

    def view(self, *, context: str, event_date: date, known_through: datetime,
             permitted_controlled_sources: frozenset[str] = frozenset()):
        return EvidenceView(self, context, event_date, instant(known_through), permitted_controlled_sources)


class EvidenceView:
    def __init__(self, evidence: Evidence, context: str, event_date: date, known_through: datetime,
                 permitted_controlled_sources: frozenset[str]):
        if not context or type(event_date) is not date:
            raise ValueError('Evaluation requires an exact context and legal event date')
        self.evidence, self.context, self.event_date = evidence, context, event_date
        self.known_through, self.permitted = known_through, permitted_controlled_sources

    def reader(self, row: dict, predicate: str) -> Evaluation:
        self.evidence.require_admitted(row['provision_version_id'])
        key = self.context, self.event_date, row['provision_version_id'], predicate
        # Corrections apply even when their private replacement is not readable:
        # permission loss cannot resurrect a known superseded public assertion.
        candidates = [a for a in self.evidence.assertions.values()
                      if a.key == key and a.known_at <= self.known_through]
        superseded = {old for a in candidates for old in a.supersedes}
        current = [a for a in candidates if a.identity not in superseded]
        conflicted = len({a.value for a in current}) > 1
        unreadable = []
        for a in current:
            if any(self.evidence.sources[s.source].access == 'controlled' and s.source not in self.permitted
                   for s in a.support):
                unreadable.append(a)
        current = [a for a in current if a not in unreadable]
        if not current:
            need = (f'authorized evidence for {predicate} in {self.context}' if unreadable
                    else f'{predicate} in {self.context} at {self.event_date}')
            return Evaluation(None, needs=frozenset({need}))
        for a in current:
            for support in a.support:
                self.evidence.sources[support.source].verify(self.evidence.root)
        values = {a.value for a in current}
        provenance = frozenset(s.source for a in current for s in a.support)
        if conflicted and unreadable:
            return Evaluation(None, needs=frozenset({f'authorized evidence for {predicate} in {self.context}'}),
                              provisions=provenance)
        if len(values) != 1:
            return Evaluation(None, needs=frozenset({f'unresolved conflicting evidence for {predicate}'}),
                              provisions=provenance)
        return Evaluation(next(iter(values)), provisions=provenance)

    def evaluate(self, identity: str) -> Evaluation:
        # This adapter supplies factual readings only. Mathematical performance
        # and historical-result inputs use their separate contracts; accepting
        # arbitrary kwargs here would bypass this reader's source checks.
        try:
            row = self.evidence.snapshot.version(identity, self.event_date)
        except MissingInput as error:
            return Evaluation(None, needs=frozenset({str(error)}))
        self.evidence.require_admitted(row['provision_version_id'])
        return evaluate(self.evidence.snapshot, identity, self.event_date,
                        reader=self.reader)


@dataclass(frozen=True)
class PublishedPopulation:
    """Acquisition completeness for a publisher's explicit record population."""
    scope: str
    expected_ids: frozenset[str]
    acquired_ids: frozenset[str]
    source: str

    def __post_init__(self):
        if not self.scope or not self.source:
            raise ValueError('A published population needs source and selection scope')

    @property
    def acquisition_complete(self):
        return self.expected_ids == self.acquired_ids


@dataclass(frozen=True)
class RequiredPopulation:
    """A separately evidenced real-world required population, never a file count."""
    scope: str
    members: frozenset[str]
    complete: bool
    qualification: Support

    def __post_init__(self):
        if not self.scope or type(self.complete) is not bool or not isinstance(self.qualification, Support):
            raise ValueError('Required-population completeness needs its own scoped evidence')


def completion_support(required: RequiredPopulation, completed: frozenset[str], *,
                       completion_scope: str, completion_history_complete: bool) -> Evaluation:
    from cordon_c.spatial import population_coverage
    if not isinstance(required, RequiredPopulation):
        raise TypeError('Published acquisition cannot establish required-population completeness')
    if completion_scope != required.scope:
        raise ValueError('Performance belongs to a different required population')
    return population_coverage({key: Evaluation(True) for key in required.members}, completed,
                               required_population_complete=required.complete,
                               completion_records_complete=completion_history_complete)
