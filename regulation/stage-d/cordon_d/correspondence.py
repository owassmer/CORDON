"""Compare qualified source references without inventing persistent entities.

A match concerns only its enumerated reference components. Source dates, rights,
portions and independently repeated occurrences survive the comparison.
"""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from .evidence import Source, Support, instant


@dataclass(frozen=True)
class ReferenceReading:
    source: str
    selector: str
    role: str
    components: tuple[tuple[str, str], ...]
    support: tuple[Support, ...]
    known_at: datetime | None
    source_as_of: str | None = None

    def __post_init__(self):
        if not self.source or not self.selector or not self.role or not self.support:
            raise ValueError('A reference needs an occurrence, field role and source reading')
        keys = [k for k, _ in self.components]
        if len(keys) != len(set(keys)) or any(not k or not isinstance(v, str) or not v for k, v in self.components):
            raise ValueError('Reference components must be distinct, explicit nonempty strings')
        if self.known_at is not None:
            instant(self.known_at)

    @property
    def identity(self):
        return self.source, self.selector, self.role

    def key(self, components):
        values = dict(self.components)
        if any(k not in values for k in components):
            return None
        return tuple(values[k] for k in components)


@dataclass(frozen=True)
class ReferenceMatch:
    left: ReferenceReading
    right: ReferenceReading
    components: tuple[str, ...]
    claim: str = 'same published reference components'


class ReferenceInventory:
    """Read-only index; no match establishes current title, notice or metric use.

    Family readers own normalization and support. Unknown components are absent,
    never wildcards. Unknown knowledge time prevents use in a historical view.
    """
    def __init__(self, sources: tuple[Source, ...], readings: tuple[ReferenceReading, ...], *, root: Path):
        self.root = root
        self.sources = {s.identity: s for s in sources}
        self.readings = {r.identity: r for r in readings}
        if len(self.sources) != len(sources) or len(self.readings) != len(readings):
            raise ValueError('Duplicate source or source-reference occurrence')
        for source in sources:
            source.verify(root)
        for reading in readings:
            if reading.source not in self.sources:
                raise ValueError('Reference occurrence names an unknown source')
            if not any(s.source == reading.source and s.selector == reading.selector for s in reading.support):
                raise ValueError('Reference needs support at its own physical occurrence')
            for support in reading.support:
                source = self.sources[support.source]
                if source.role not in {'official-record', 'official-dataset', 'qualified-observation'}:
                    raise ValueError('Source role cannot establish an instance reference')

    def matches(self, *, components: tuple[str, ...], known_through: datetime,
                permitted_controlled_sources: frozenset[str] = frozenset(),
                left_sources: frozenset[str] | None = None,
                right_sources: frozenset[str] | None = None) -> tuple[ReferenceMatch, ...]:
        instant(known_through)
        if not components or len(set(components)) != len(components):
            raise ValueError('A comparison needs distinct named reference components')
        readable = []
        checked = set()
        for reading in self.readings.values():
            if reading.known_at is None or reading.known_at > known_through:
                continue
            if reading.key(components) is None:
                continue
            support_sources = [self.sources[s.source] for s in reading.support]
            if any(s.access == 'controlled' and s.identity not in permitted_controlled_sources for s in support_sources):
                continue
            for source in support_sources:
                if source.identity not in checked:
                    source.verify(self.root)
                    checked.add(source.identity)
            readable.append(reading)
        right = defaultdict(list)
        for reading in readable:
            if right_sources is None or reading.source in right_sources:
                right[reading.key(components)].append(reading)
        matches = []
        for left in readable:
            if left_sources is not None and left.source not in left_sources:
                continue
            for candidate in right[left.key(components)]:
                if candidate.source != left.source:
                    matches.append(ReferenceMatch(left, candidate, components))
        return tuple(matches)
