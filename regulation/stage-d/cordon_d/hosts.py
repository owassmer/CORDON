"""Source names and event-time Annex II qualification of observed hosts."""
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from hashlib import sha256
from functools import lru_cache
from pathlib import Path
import json
import re
import unicodedata
from urllib.parse import urlsplit, parse_qs

from cordon_c.core import Evaluation
from .store import blob_path, store_root


def norm(value):
    return ' '.join(unicodedata.normalize('NFC', value).replace('_',' ').casefold().split())


@dataclass(frozen=True)
class Taxon:
    code: str
    name: str
    rank: str
    names: frozenset[str]
    lineage: tuple[tuple[str, str], ...]
    source: tuple[str, ...]

    @property
    def species(self):
        return dict(self.lineage).get('Species')


@dataclass(frozen=True)
class Host:
    labels: tuple[str, ...]
    taxa: frozenset[str]
    unresolved: tuple[str, ...]
    support: tuple[tuple[str, str], ...]

    def species(self, names):
        identities = {names.taxa[t].species for t in self.taxa if names.taxa[t].species}
        if len(identities) != 1 or self.unresolved:
            return None
        species = next(iter(identities))
        resolved = [t for t in self.taxa if names.taxa[t].species == species]
        lineage = set().union(*(set(dict(names.taxa[t].lineage).values()) for t in resolved))
        return species if self.taxa <= lineage else None


def read_taxon(names, ancestry, overview, digests):
    """The documented EPPO v2 shapes; names and ancestry are separate sources."""
    code = overview['eppocode']
    preferred = [n['fullname'] for n in names if n['lang_iso'] == 'la' and n['preferred']]
    lineage = tuple((v['type'],v['eppocode']) for v in ancestry)
    ranks = [rank for rank,identity in lineage if identity == code]
    if len(preferred) != 1 or len(ranks) != 1:
        raise ValueError(f'Unresolved EPPO preferred name or rank: {code}')
    return Taxon(code,preferred[0],ranks[0],
                 frozenset(norm(n['fullname']+suffix) for n in names if n['lang_iso']=='la'
                           for suffix in ('', ' '+(n.get('author') or '')) if suffix == '' or n.get('author')),
                 lineage,tuple(digests))


class HostNames:
    def __init__(self, taxa, common=()):
        self.taxa = {t.code: t for t in taxa}
        self.scientific, self.common = defaultdict(set), defaultdict(set)
        for taxon in taxa:
            for name in taxon.names:
                self.scientific[name].add(taxon.code)
        for name, code in common:
            self.common[norm(name)].add(code)

    @classmethod
    def load(cls, root):
        store = store_root(root)
        records = json.loads((root/'corpus/sources/host-names/api.json').read_text())
        by_code, lookups = defaultdict(dict), {}
        for record in records:
            data = blob_path(store,record['sha256']).read_bytes()
            if sha256(data).hexdigest() != record['sha256']:
                raise ValueError('Host-name source hash mismatch')
            url = urlsplit(record['url'])
            values = json.loads(data)
            if url.path.endswith('/tools/name2codes'):
                query = norm(parse_qs(url.query)['name'][0])
                lookups[query] = ({v['eppocode'] for v in values},record['sha256'])
            else:
                parts = url.path.split('/')
                by_code[parts[-2]][parts[-1]] = (values,record['sha256'])
        taxa, common = [], []
        for code, parts in by_code.items():
            if set(parts) != {'overview','names','taxonomy'}:
                continue
            if parts['overview'][0].get('is_active') is False:
                continue
            taxa.append(read_taxon(*(parts[k][0] for k in ('names','taxonomy','overview')),
                                   tuple(parts[k][1] for k in ('names','taxonomy','overview'))))
        result = cls(taxa)
        result.lookup_support = {}
        result.incomplete_names = set()
        for label,(codes,digest) in lookups.items():
            result.lookup_support[label] = (digest,'name2codes: '+label)
            if not codes <= set(result.taxa):
                result.incomplete_names.add(label)
            for code in codes & set(result.taxa):
                names = by_code[code]['names'][0]
                if any(norm(n['fullname']) == label and n['lang_iso']=='it' for n in names):
                    result.common[label].add(code)
        # The publisher's own explicit vernacular/Latin pairs qualify its
        # language too. EPPO's common-name dictionary is not exhaustive Italian.
        result.publisher_support = defaultdict(set)
        result.bind_publisher_names(root)
        return result

    def bind_publisher_names(self, root):
        import duckdb
        from .monitoring import releases,reader_version,_ensure_derived
        store = store_root(root)
        files = [str(_ensure_derived(store,r,reader_version())[1])
                 for r in releases(root/'corpus/sources/monitoring')]
        connection = duckdb.connect()
        connection.execute("SET memory_limit='512MB'")
        connection.execute('SET threads=2')
        try:
            rows = connection.execute('select species, min(sha256 || chr(9) || locator) from read_parquet(?) '
                                      'where species is not null group by species',[files]).fetchall()
        finally:
            connection.close()
        for label,source in rows:
            parts = [p.strip() for p in re.split(r'[()]',label) if p.strip()]
            scientific = set().union(*(self.scientific_part(p) for p in parts))
            if not scientific:
                continue
            for part in parts:
                if not self.scientific_part(part) and re.fullmatch(r'[\w à-ÿ-]{3,}', norm(part)):
                    self.common[norm(part)].update(scientific)
                    self.publisher_support[norm(part)].add(tuple(source.split('\t',1)))

    @lru_cache(maxsize=8192)
    def scientific_part(self, text):
        """Longest source-supported name, allowing a botanical authority suffix.

        An unknown epithet cannot silently degrade to a known genus. No edit
        distance, typo repair, or vernacular guess supplies a scientific name.
        """
        literal = ' '.join(unicodedata.normalize('NFC',text).replace('_',' ').split())
        text = norm(text).strip()
        if text in self.scientific:
            return set(self.scientific[text])
        choices = []
        for name in self.scientific:
            if not text.startswith(name + ' '):
                continue
            remainder = text[len(name):].strip()
            # Botanical authority syntax is distinct from a lowercase epithet.
            # Full authorities are also retained in the structured name index.
            authority = literal[len(name):].strip()
            author_tokens = re.sub(r'[(),]', ' ', authority).split()
            is_authority = bool(author_tokens) and '.' in authority and all(
                token in {'ex','in','&'} or re.fullmatch(r"[A-ZÀ-ÖØ-Þ][\w.’'\-]*",token)
                for token in author_tokens)
            if re.fullmatch(r'spp?\.?', remainder) or is_authority:
                choices.append(name)
        if not choices:
            return set()
        longest = max(map(len, choices))
        return set().union(*(self.scientific[n] for n in choices if len(n) == longest))

    def resolve(self, labels, support=()):
        scientific_labels, common_labels, unknown = [], [], []
        support = list(support)
        for label in sorted(set(labels)):
            whole = self.scientific_part(label)
            parts = re.split(r'[()]', label)
            scientific = whole or set().union(*(self.scientific_part(p) for p in parts if p.strip()))
            if scientific:
                scientific_labels.append(scientific)
                continue
            common = self.common.get(norm(label), set())
            support.extend(getattr(self,'publisher_support',{}).get(norm(label),()))
            if norm(label) in getattr(self,'lookup_support',{}):
                support.append(self.lookup_support[norm(label)])
            if norm(label) in getattr(self,'incomplete_names',set()) or not common:
                unknown.append(label)
            if common:
                common_labels.append(common)
        # Explicit scientific ranks govern precision. Vernacular alternatives
        # can expose a conflict but cannot refine a stated genus to a species.
        alternatives = scientific_labels or common_labels
        found = set().union(*alternatives) if alternatives else set()
        viable = {t for t in found if all(any(c in dict(self.taxa[t].lineage).values() for c in choices)
                                         for choices in alternatives)}
        if viable:
            found = viable
        if scientific_labels:
            for choices in common_labels:
                compatible = any(c in dict(self.taxa[t].lineage).values() or
                                 t in dict(self.taxa[c].lineage).values()
                                 for c in choices for t in found)
                if not compatible:
                    found.update(choices)
        evidence = tuple(support) + tuple((digest, 'EPPO names and taxonomy: ' + t)
                    for t in sorted(found) for digest in self.taxa[t].source)
        return Host(tuple(sorted(set(labels))), frozenset(found), tuple(unknown), evidence)


@dataclass(frozen=True)
class SpecifiedHosts:
    effective_from: date
    source: str
    digest: str
    by_subspecies: dict[str, tuple[str, ...]]


def specified_versions(root):
    """Read the retained, date-labelled EU consolidations, without source rewrites."""
    for path in sorted((root / 'regulation/source/consolidations').glob('02020R1201-*.txt')):
        text = path.read_text()
        matches = list(re.finditer(r'^ANNEX II\s*$', text, re.M))
        if len(matches) != 1:
            raise ValueError(f'Unresolved Annex II boundaries: {path.name}')
        section = text[matches[0].end():].split('ANNEX III')[0]
        headings = list(re.finditer(r'Specified plants susceptible to Xylella fastidiosa subspecies (\w+)', section))
        if not headings:
            raise ValueError(f'No specified-host scopes read: {path.name}')
        lists = {}
        for i, match in enumerate(headings):
            block = section[match.end():headings[i+1].start() if i+1 < len(headings) else len(section)]
            entries = tuple(line.strip() for line in block.splitlines() if line.strip())
            lists[match[1]] = entries
        yield SpecifiedHosts(date.fromisoformat(path.stem[-8:][:4]+'-'+path.stem[-4:-2]+'-'+path.stem[-2:]),
                             str(path.relative_to(root)), sha256(path.read_bytes()).hexdigest(), lists)


def specified_host(host, names, versions, at, subspecies, *, plant_for_planting):
    """Annex membership plus A's non-seed plant-for-planting requirement."""
    from cordon_c.core import conjunction
    applicable = [v for v in versions if v.effective_from <= at]
    if not applicable or not subspecies:
        return conjunction([Evaluation(None, needs=frozenset({'event-time Annex II and relevant pest subspecies'})), plant_for_planting])
    version = max(applicable, key=lambda v: v.effective_from)
    entries = version.by_subspecies.get(subspecies)
    if entries is None:
        return conjunction([Evaluation(None, needs=frozenset({'Annex II subspecies scope'})), plant_for_planting])
    if not host.taxa or host.unresolved:
        return conjunction([Evaluation(None, needs=frozenset({'specified host identity'})), plant_for_planting])
    results = []
    for code in host.taxa:
        taxon = names.taxa[code]
        lineage = set(dict(taxon.lineage).values())
        matched = any(names.scientific_part(entry) & lineage for entry in entries)
        unresolved_entry = any(not names.scientific_part(entry) and
                               any(norm(entry).startswith(alias+' ') for alias in taxon.names)
                               for entry in entries)
        results.append(True if matched else None if taxon.rank != 'Species' or unresolved_entry else False)
    value = results[0] if len(set(results)) == 1 else None
    membership = Evaluation(value, needs=frozenset({'specified-host rank or conflicting identity'}) if value is None else frozenset())
    return conjunction([membership, plant_for_planting])
