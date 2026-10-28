#!/usr/bin/env python3
"""Keep the store's irreplaceable data in Cloudflare R2, and bring back what is missing.

    scripts/replicate_store.py              push: every kept file to R2, after checking each is whole
    scripts/replicate_store.py --restore    pull: only kept files missing locally; never rewrites one
    scripts/replicate_store.py --compare    say which kept files R2 lacks or holds differently; transfers nothing

What is kept is `cordon_d.store.kept`: the blobs, and every file under `derived/` outside `REGENERABLE`. A push lists
R2 once and sends only what R2 lacks or holds at another size. It first re-hashes each blob it will send and checks each
reading it will send against its own name (`kept_problems`), and refuses when one fails, so a damaged file never
replaces the good copy. A blob is content-addressed and never changes, so a local blob whose size differs from R2's copy
is damage and refuses the push; a reading may be rewritten while its extraction runs, and is sent again once it passes
its check. A restore refuses when a local file already differs in size from R2's copy, copies only what is missing,
then makes blobs read-only and audits them. The pre-push hook runs the push before any branch push.

The store is `$CORDON_STORE`, else `<main checkout>-store` (`cordon_d.store.store_root`). The account is
`$CORDON_R2_ACCOUNT`; `$CORDON_R2_BUCKET` overrides the bucket (`cordon-store`). Credentials: the AWS CLI profile `r2`.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'regulation/stage-d'))
from cordon_d.store import REGENERABLE, TRANSIENT, audit, kept, kept_problems, store_root  # noqa: E402


def fail(message: str) -> None:
    print(f'replicate_store: {message}', file=sys.stderr)
    sys.exit(1)


def aws(*args: str, capture: bool = False) -> str:
    account = os.environ.get('CORDON_R2_ACCOUNT')
    if not account:
        fail('CORDON_R2_ACCOUNT is not set, so R2 cannot be reached; nothing was replicated')
    command = ['aws', *args, '--endpoint-url', f'https://{account}.r2.cloudflarestorage.com', '--profile', 'r2']
    try:
        done = subprocess.run(command, check=True, text=True, capture_output=capture)
    except FileNotFoundError:
        fail('the AWS CLI is not installed')
    except subprocess.CalledProcessError as error:
        fail(f'{" ".join(args[:2])} failed ({error.returncode}): {(error.stderr or "").strip()[:400]}')
    return done.stdout if capture else ''


def roots(names) -> list[tuple[str, list[str]]]:
    """The kept roots to sync, each with its exclusions: `blobs`, and each top-level `derived/<folder>` that is not
    wholly regenerable, excluding the regenerable folders inside it and transient files.

    Syncing each kept root by itself keeps the CLI from walking regenerable folders at all: a reader rebuilding
    them (the monitoring readings) adds and removes files while a walk runs, and the CLI then fails on files that
    vanished, though none of them is kept.
    """
    transient = [x for pattern in TRANSIENT for x in ('--exclude', pattern, '--exclude', f'*/{pattern}')]
    out = [('blobs', transient)]
    for name in sorted(names):
        if name in REGENERABLE:
            continue
        inner = [x for folder in REGENERABLE if folder.startswith(name + '/')
                 for x in ('--exclude', folder[len(name) + 1:] + '/*')]
        out.append((f'derived/{name}', inner + transient))
    return out


def sync(source: str, target: str, names) -> None:
    """Sync every kept root from `source` to `target` (one is a local store, the other the bucket)."""
    for root, excludes in roots(names):
        aws('s3', 'sync', f'{source}/{root}', f'{target}/{root}', '--size-only', '--no-progress',
            '--only-show-errors', *excludes)


def remote(bucket: str) -> dict[str, tuple[int, str]]:
    """Every object in the bucket: key -> (size, etag)."""
    listing = aws('s3api', 'list-objects-v2', '--bucket', bucket, '--output', 'json', capture=True)
    contents = json.loads(listing or '{}').get('Contents', []) if listing.strip() else []
    return {o['Key']: (int(o['Size']), o['ETag'].strip('"')) for o in contents}


def md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--restore', action='store_true')
    mode.add_argument('--compare', action='store_true')
    args = parser.parse_args()
    store = store_root(ROOT / 'corpus/sources')
    bucket = os.environ.get('CORDON_R2_BUCKET', 'cordon-store')
    if not args.restore and not (store / 'blobs').is_dir():
        fail(f'no store at {store}; nothing was replicated')

    if args.compare:
        objects = remote(bucket)
        missing, differs = [], []
        files = list(kept(store))
        for relative in files:
            key = relative.as_posix()
            if key not in objects:
                missing.append(key)
                continue
            size, etag = objects[key]
            path = store / relative
            # A single-part upload's ETag is the object's MD5; a multipart one's is not, so size alone is compared.
            if size != path.stat().st_size or ('-' not in etag and etag != md5(path)):
                differs.append(key)
        print(json.dumps({'kept_local': len(files), 'in_r2': len(objects), 'missing_in_r2': len(missing),
                          'different_in_r2': len(differs), 'examples': (missing + differs)[:20]}))
        sys.exit(1 if missing or differs else 0)

    if args.restore:
        objects = remote(bucket)
        selected = {k: v for k, v in objects.items()
                    if (k.startswith('blobs/') or k.startswith('derived/'))
                    and not any(k.startswith(f'derived/{f}/') for f in REGENERABLE)}
        conflicts = [k for k, (size, _) in selected.items()
                     if (store / k).exists() and (store / k).stat().st_size != size]
        if conflicts:
            fail(f'{len(conflicts)} local files differ in size from R2 and would be rewritten; nothing was restored. '
                 f'First: {conflicts[:5]}')
        missing = [k for k in selected if not (store / k).exists()]
        print(f'restoring {len(missing)} of {len(selected)} kept files into {store}', flush=True)
        if missing:
            # Every local file has R2's size, so a size-only sync copies only what is missing.
            sync(f's3://{bucket}', str(store), {k.split('/')[1] for k in missing if k.startswith('derived/')})
        for path in (store / 'blobs').rglob('*'):
            if path.is_file():
                path.chmod(0o444)
        bad = audit(store)
        if bad:
            fail(f'{len(bad)} restored blobs do not match their names: {[str(b) for b in bad[:5]]}')
        print(f'restored; {sum(1 for _ in kept(store))} kept files present; every blob matches its name')
        return

    objects = remote(bucket)
    files = list(kept(store))
    send = [r for r in files if r.as_posix() not in objects or objects[r.as_posix()][0] != (store / r).stat().st_size]
    changed = [r for r in send if r.parts[0] == 'blobs' and r.as_posix() in objects]
    if changed:
        fail(f'{len(changed)} blobs differ in size from their copy in R2, so they are damaged here; nothing was '
             f'replicated: {[str(r) for r in changed[:5]]}')
    bad = [r for r in send if r.parts[0] == 'blobs' and hashlib.sha256((store / r).read_bytes()).hexdigest() != r.name]
    if bad:
        fail(f'{len(bad)} blobs no longer match their names; nothing was replicated: {[str(r) for r in bad[:5]]}')
    problems = list(kept_problems(store, only=[r for r in send if r.parts[0] == 'derived']))
    if problems:
        fail(f'{len(problems)} kept readings fail their check; nothing was replicated: '
             + '; '.join(f'{p} ({why})' for p, why in problems[:5]))
    if send:
        sync(str(store), f's3://{bucket}', {r.parts[1] for r in send if r.parts[0] == 'derived'})
    print(f'replicated: {len(send)} kept files sent; {len(files)} kept files in s3://{bucket}')


if __name__ == '__main__':
    main()
