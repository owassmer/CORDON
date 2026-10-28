"""Content-addressed store for source bytes, the model readings of them, and caches.

Two kinds of data here are irreplaceable, and both are replicated to R2 on every
branch push (`scripts/replicate_store.py`):

- source bytes: a blob is named by its SHA-256, written once through a temporary
  name, and never rewritten;
- every reading that cannot be rebuilt without a model call: a model's answer
  costs subscription time to repeat, and a repeat can read differently.

The rest of `derived/` is a cache a reader rebuilds from blobs and the tree
alone; those folders are named in `REGENERABLE`. A folder not named there is
kept, so a new reader's readings are kept until shown to be regenerable.
"""
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import tempfile


def _git_common_dir(start: Path):
    """The main checkout's .git directory when `start` lies inside a checkout or worktree."""
    for directory in (start.resolve(), *start.resolve().parents):
        marker = directory / '.git'
        if marker.is_dir():
            return marker
        if marker.is_file():
            target = marker.read_text().strip().removeprefix('gitdir:').strip()
            gitdir = (directory / target).resolve()
            common = gitdir / 'commondir'
            return (gitdir / common.read_text().strip()).resolve() if common.is_file() else gitdir
    return None


def store_root(root: Path) -> Path:
    """`$CORDON_STORE`; else `<repository>-store` beside the main checkout; else beside the root."""
    configured = os.environ.get('CORDON_STORE')
    if configured:
        return Path(configured).expanduser()
    common = _git_common_dir(Path(root))
    if common is not None:
        checkout = common.parent
        return checkout.parent / f'{checkout.name}-store'
    return Path(root).resolve().parent / 'store'


def blob_path(store: Path, digest: str) -> Path:
    return store / 'blobs' / 'sha256' / digest[:2] / digest


def file_digest(path: Path) -> str:
    digest = sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _place(target: Path, prepare):
    """Write through a temporary sibling, rename into place, then make read-only."""
    target.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=target.parent, prefix='.tmp-')
    os.close(handle)
    temporary = Path(temporary)
    try:
        prepare(temporary)
        os.chmod(temporary, 0o444)
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def put_bytes(store: Path, data: bytes) -> str:
    """Store bytes under their hash; identical bytes are one blob."""
    digest = sha256(data).hexdigest()
    target = blob_path(store, digest)
    if not target.exists():
        _place(target, lambda temporary: temporary.write_bytes(data))
    return digest


def adopt(store: Path, path: Path) -> str:
    """Move a captured file into the store under its hash and return the hash."""
    path = Path(path)
    digest = file_digest(path)
    target = blob_path(store, digest)
    if target.exists():
        path.unlink()
        return digest

    def move(temporary: Path):
        temporary.unlink()
        try:
            os.rename(path, temporary)
        except OSError:
            shutil.copyfile(path, temporary)
            path.unlink()
    _place(target, move)
    return digest


def derived_path(store: Path, dataset: str, digest: str, version: str) -> Path:
    return store / 'derived' / dataset / f'{digest}-{version}.parquet'


def write_derived(target: Path, table) -> None:
    import pyarrow.parquet as parquet
    _place(target, lambda temporary: parquet.write_table(table, temporary, compression='zstd'))


# Folders under `derived/` that a reader rebuilds from blobs and the tree with no
# model call. Everything else under `derived/` is kept and replicated.
REGENERABLE = (
    'monitoring',                   # monitoring occurrences, readings and groups (Parquet)
    'source_associations',          # native-table caches of retained sources
    'protected-status',             # row 9 rows, read from the register and list acts
    'areas/cadastral-fix-errors',   # measurements from held fixes
    'areas/region-layer-samples',
    'areas/row1-positives',
)
# Files a writer is still writing or locking; never replicated or restored.
TRANSIENT = ('*.tmp', '*.lock', '.tmp-*', '.DS_Store')


def _transient(name: str) -> bool:
    from fnmatch import fnmatch
    return any(fnmatch(name, pattern) for pattern in TRANSIENT)


def kept(store: Path):
    """Every kept file, relative to the store: blobs, and derived files outside `REGENERABLE`."""
    store = Path(store)
    for top in ('blobs', 'derived'):
        root = store / top
        if not root.is_dir():
            continue
        for path in sorted(root.rglob('*')):
            # A symlink holds no data of its own: the Claude CLI's `latest` points at whichever debug log it is
            # writing now, and the file it points at is kept under its own name.
            if path.is_symlink() or not path.is_file() or _transient(path.name):
                continue
            relative = path.relative_to(store)
            inside = relative.relative_to('derived').as_posix() if top == 'derived' else None
            if inside is not None and any(inside == r or inside.startswith(r + '/') for r in REGENERABLE):
                continue
            yield relative


def kept_problems(store: Path, only=None):
    """Kept readings that are not whole or do not match their own name; blobs are audited by `audit`.

    `only`, when given, limits the check to those relative paths (the files about to be sent).

    A document reading names its request, an assembled report its source and extraction
    version, and a relationship reading its source and reading version; each is checked
    against where it sits. Any other kept reading must at least be complete JSON.
    """
    import json
    from hashlib import sha256
    store = Path(store)
    for relative in (sorted(Path(r) for r in only) if only is not None else kept(store)):
        parts = relative.parts
        if parts[0] != 'derived' or relative.suffix != '.json':
            continue
        path = store / relative
        try:
            value = json.loads(path.read_text())
        except (OSError, ValueError) as error:
            yield relative, f'not whole JSON: {error}'
            continue
        if parts[1] == 'document-readings':
            request = value.get('request') if isinstance(value, dict) else None
            if (value.get('request_sha256') != path.stem or request is None
                    or sha256(json.dumps(request, sort_keys=True).encode()).hexdigest() != path.stem):
                yield relative, 'its request does not hash to its name'
        elif parts[1] == 'reports' and len(parts) == 5 and parts[4] == 'report.json':
            if value.get('source_sha256') != parts[3] or value.get('extraction_version') != parts[2]:
                yield relative, 'its source or extraction version is not where it sits'
        elif parts[1] == 'reports' and len(parts) == 5 and parts[2] == 'relationships':
            if value.get('source_sha256') != Path(parts[4]).stem or value.get('reading_version') != parts[3]:
                yield relative, 'its source or reading version is not where it sits'


def audit(store: Path):
    """Re-hash every blob; return the blobs whose bytes no longer match their name."""
    mismatches = []
    blobs = store / 'blobs' / 'sha256'
    for path in sorted(blobs.glob('*/*')) if blobs.is_dir() else ():
        if path.is_file() and file_digest(path) != path.name:
            mismatches.append(path)
    return mismatches


# --- lossless encoding of native source rows ----------------------------------

def encode(value):
    """Type-tagged JSON so a round trip returns the same Python type and value."""
    from datetime import date, datetime, time, timedelta
    if value is None:
        return None
    if isinstance(value, bool):
        return ['bool', value]
    if isinstance(value, int):
        return ['int', str(value)]
    if isinstance(value, float):
        return ['float', repr(value)]
    if isinstance(value, str):
        return ['str', value]
    if isinstance(value, datetime):
        return ['datetime', value.isoformat()]
    if isinstance(value, date):
        return ['date', value.isoformat()]
    if isinstance(value, time):
        return ['time', value.isoformat()]
    if isinstance(value, timedelta):
        return ['timedelta', [value.days, value.seconds, value.microseconds]]
    if isinstance(value, dict):
        return ['dict', [[k, encode(v)] for k, v in value.items()]]
    if isinstance(value, (list, tuple)):
        return ['list', [encode(v) for v in value]]
    raise TypeError(f'Uninterpreted source value type: {type(value).__name__}')


def decode(value):
    from datetime import date, datetime, time, timedelta
    if value is None:
        return None
    kind, payload = value
    if kind == 'bool':
        return payload
    if kind == 'int':
        return int(payload)
    if kind == 'float':
        return float(payload)
    if kind == 'str':
        return payload
    if kind == 'datetime':
        return datetime.fromisoformat(payload)
    if kind == 'date':
        return date.fromisoformat(payload)
    if kind == 'time':
        return time.fromisoformat(payload)
    if kind == 'timedelta':
        return timedelta(days=payload[0], seconds=payload[1], microseconds=payload[2])
    if kind == 'dict':
        return {k: decode(v) for k, v in payload}
    if kind == 'list':
        return [decode(v) for v in payload]
    raise TypeError(f'Unknown encoded type: {kind}')


def dumps(value) -> str:
    return json.dumps(encode(value), ensure_ascii=False, separators=(',', ':'))


def loads(text: str):
    return decode(json.loads(text))
