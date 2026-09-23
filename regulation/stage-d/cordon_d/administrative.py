"""Italian administrative units: identity from ISTAT's code list, extent from its boundaries.

Identity is ISTAT's `Elenco comuni italiani`: one row per comune with its ISTAT and
cadastral codes, its province (unità territoriale sovracomunale) and that province's
name and sigla. A province written `LE` or `Lecce` is one province because that list
says so; nothing here holds a table of spellings. Extent is ISTAT's non-generalised
`Confini delle unità amministrative a fini statistici`, published in WGS 84 / UTM 32N
and transformed to EPSG:32633 without a datum change.

ISTAT states no positional accuracy for these boundaries: its note says their scale
"non è certificabile uniformemente", the acquisition scale varying between 1:5.000 and
1:25.000. So this module supplies geometry and never an error bound; a metric consumer
receives one only from a separate qualification.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from io import BytesIO
import json
from pathlib import Path
import unicodedata
from zipfile import ZipFile

import numpy
from pyproj import CRS, Transformer
import shapely
from shapely.geometry import shape

from .store import blob_path, file_digest, store_root

TARGET_CRS = 'EPSG:32633'
RECORDS = 'corpus/sources/areas/geometry.json'


def _key(text) -> str:
    """Compare names as printed, ignoring case, accents, spacing and apostrophe glyphs."""
    text = unicodedata.normalize('NFKD', str(text or '')).encode('ascii', 'ignore').decode()
    return ' '.join(text.replace("'", ' ').replace('-', ' ').upper().split())


@dataclass(frozen=True)
class Province:
    code: int          # ISTAT code of the unità territoriale sovracomunale
    name: str
    sigla: str
    region: str


@dataclass(frozen=True)
class Comune:
    istat: str         # alphanumeric ISTAT code, e.g. '072046'
    catastale: str     # Codice Catastale, e.g. 'L425'
    name: str
    province: Province


def records(root: Path, kind: str) -> list[dict]:
    path = Path(root) / RECORDS
    if not path.exists():
        return []
    return [r for r in json.loads(path.read_text()) if r['kind'] == kind]


def _blob(root: Path, record: dict) -> Path:
    path = blob_path(store_root(root), record['sha256'])
    if not path.exists():
        raise FileNotFoundError(f"{record['url']} is not in this store")
    if file_digest(path) != record['sha256']:
        raise ValueError(f"{record['url']}: stored bytes do not match their record")
    return path


class AdministrativeUnits:
    """ISTAT comuni and provinces, joined by code, and their boundaries in EPSG:32633."""

    def __init__(self, root: Path):
        self.root = Path(root)
        codes, = records(root, 'istat-codes')
        boundaries, = records(root, 'istat-boundaries')
        self.codes_record, self.boundaries_record = codes, boundaries
        self.comuni: dict[str, Comune] = {}
        self.provinces: dict[int, Province] = {}
        import openpyxl
        book = openpyxl.load_workbook(BytesIO(_blob(root, codes).read_bytes()), read_only=True)
        rows = book[codes['sheet']].iter_rows(values_only=True)
        header = [' '.join(str(h or '').split()) for h in next(rows)]
        at = {name: header.index(name) for name in (
            'Denominazione Regione', "Codice dell'Unità territoriale sovracomunale (valida a fini statistici)",
            "Denominazione dell'Unità territoriale sovracomunale (valida a fini statistici)",
            'Sigla automobilistica', 'Codice Comune formato alfanumerico', 'Denominazione in italiano',
            'Codice Catastale del Comune')}
        # The list states each comune's earlier numeric codes (the provinces were
        # renumbered in 1995, 2006, 2010 and 2017), so a record printing a superseded
        # code joins through ISTAT's own columns, not through a table kept here.
        history = [i for i, name in enumerate(header) if name.startswith('Codice Comune numerico con')]
        aliases: dict[str, set] = {}
        for row in rows:
            if not row or not row[at['Codice Comune formato alfanumerico']]:
                continue
            code = int(row[at["Codice dell'Unità territoriale sovracomunale (valida a fini statistici)"]])
            province = self.provinces.setdefault(code, Province(
                code, row[at["Denominazione dell'Unità territoriale sovracomunale (valida a fini statistici)"]],
                row[at['Sigla automobilistica']], row[at['Denominazione Regione']]))
            comune = Comune(str(row[at['Codice Comune formato alfanumerico']]),
                            str(row[at['Codice Catastale del Comune']]),
                            row[at['Denominazione in italiano']], province)
            self.comuni[comune.istat] = comune
            for i in history:
                if row[i] is not None:
                    aliases.setdefault(str(row[i]).zfill(6), set()).add(comune.istat)
        self.by_catastale = {c.catastale: c for c in self.comuni.values()}
        self.by_earlier_code = {code: self.comuni[next(iter(found))] for code, found in aliases.items()
                                if len(found) == 1 and code not in self.comuni}
        self._province_labels = {}
        for province in self.provinces.values():
            for label in (province.name, province.sigla):
                self._province_labels.setdefault(_key(label), set()).add(province)

    # --- identity -------------------------------------------------------------

    def province(self, label) -> Province | None:
        """The province a label names, by ISTAT's own name or sigla; None if it names none."""
        found = self._province_labels.get(_key(label), set())
        return next(iter(found)) if len(found) == 1 else None

    def comune(self, *, catastale=None, istat=None, name=None, province=None, region=None) -> Comune | None:
        """One comune by cadastral code, ISTAT code, or name within an optional province label.

        A province label that ISTAT does not state (an act's `BAT`) does not narrow the
        name; a name that stays ambiguous is not resolved. Within a region, a name the
        list does not print whole is the one comune whose ISTAT name begins with it
        (an act's "Polignano" for Polignano a Mare).
        """
        if catastale:
            return self.by_catastale.get(str(catastale).strip().upper())
        if istat:
            code = str(istat).strip().zfill(6)
            return self.comuni.get(code) or self.by_earlier_code.get(code)
        if not name:
            return None
        found = [c for c in self.comuni.values() if _key(c.name) == _key(name)]
        if region is not None:
            found = [c for c in found if c.province.region == region] or [
                c for c in self.comuni.values()
                if c.province.region == region and _key(c.name).startswith(_key(name) + ' ')]
        within = self.province(province) if province else None
        if within is not None and any(c.province == within for c in found):
            found = [c for c in found if c.province == within]
        return found[0] if len(found) == 1 else None

    # --- extent ---------------------------------------------------------------

    @cached_property
    def _archive(self):
        return ZipFile(_blob(self.root, self.boundaries_record))

    @cached_property
    def _extracted(self) -> Path:
        """A private directory the shapefile members are read from: pyshp reads a shape by
        seeking, so the members stay on disk rather than in memory."""
        import tempfile
        import weakref
        import shutil
        directory = Path(tempfile.mkdtemp(prefix='istat-'))
        weakref.finalize(self, shutil.rmtree, directory, True)
        return directory

    def _reader(self, member):
        import shapefile
        stem = member[:-4]
        archive = self._archive
        projection = archive.read(stem + '.prj').decode('utf-8-sig')
        paths = {}
        for suffix in ('.shp', '.shx', '.dbf'):
            path = self._extracted / Path(stem + suffix).name
            if not path.exists():
                with archive.open(stem + suffix) as source, path.open('wb') as target:
                    while chunk := source.read(1 << 20):
                        target.write(chunk)
            paths[suffix[1:]] = path.open('rb')
        reader = shapefile.Reader(**paths, encoding=self.boundaries_record['encoding'])
        transformer = Transformer.from_crs(CRS.from_wkt(projection), CRS.from_user_input(TARGET_CRS),
                                           always_xy=True, allow_ballpark=False, only_best=True)
        return reader, transformer

    def _geometry(self, reader, transformer, index):
        native = shape(reader.shape(index).__geo_interface__)

        def to_target(coordinates):
            x, y = transformer.transform(coordinates[:, 0], coordinates[:, 1])
            return numpy.column_stack((x, y))
        return shapely.transform(native, to_target)

    @cached_property
    def _comune_index(self):
        reader, transformer = self._reader(self.boundaries_record['comuni_member'])
        index = {record['PRO_COM_T']: number for number, record in enumerate(reader.iterRecords())}
        return reader, transformer, index

    @cached_property
    def _province_index(self):
        reader, transformer = self._reader(self.boundaries_record['provinces_member'])
        index = {record['COD_UTS']: number for number, record in enumerate(reader.iterRecords())}
        return reader, transformer, index

    @cached_property
    def _built(self):
        return {}

    def comune_geometry(self, comune: Comune):
        reader, transformer, index = self._comune_index
        if comune.istat not in index:
            return None
        key = 'comune', comune.istat
        if key not in self._built:
            self._built[key] = self._geometry(reader, transformer, index[comune.istat])
        return self._built[key]

    def province_geometry(self, province: Province):
        reader, transformer, index = self._province_index
        if province.code not in index:
            return None
        key = 'province', province.code
        if key not in self._built:
            self._built[key] = self._geometry(reader, transformer, index[province.code])
        return self._built[key]

    def comuni_of(self, region: str):
        return tuple(c for c in self.comuni.values() if c.province.region == region)

    def comuni_near(self, x: float, y: float, within_m: float, candidates) -> tuple[Comune, ...]:
        """The candidate comuni whose ISTAT boundary lies within `within_m` of a point.

        The caller supplies the bound: the point's own error plus the boundary's. With a
        bound of zero this is the plain containing comune, which is not a qualified answer.
        """
        point = shapely.Point(x, y)
        return tuple(c for c, geometry in candidates if geometry.distance(point) <= within_m)
