"""Codex subscription transport; the calling reader owns document meaning."""
from datetime import datetime, timezone
from hashlib import sha256
import fcntl
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import monotonic

from .store import blob_path


def _call(prompt, schema, images, directory, model, effort, timeout):
    schema_path = directory / 'schema.json'
    schema_path.write_text(json.dumps(schema))
    output = directory / 'reading.json'
    command = ['codex', 'exec', '--ignore-user-config', '--ephemeral',
               '--skip-git-repo-check', '--sandbox', 'read-only', '-C', str(directory),
               '-m', model, '-c', f'model_reasoning_effort="{effort}"',
               '-c', 'features.shell_tool=false', '-c', 'features.multi_agent=false',
               '-c', 'web_search="disabled"', '--json', '--output-schema', str(schema_path),
               '-o', str(output)]
    for image in images:
        command.extend(['-i', str(image)])
    env = dict(os.environ)
    for key in ('OPENAI_API_KEY', 'CODEX_API_KEY'):
        env.pop(key, None)
    result = subprocess.run(command + ['-'], input=prompt, text=True,
                            capture_output=True, env=env, timeout=timeout)
    if result.returncode:
        raise RuntimeError('Codex subscription failed: ' + result.stderr[-1500:])
    return output.read_text()


def read_documents(digests, store, *, prompt, schema, model='gpt-5.6-luna',
                   effort='high', dpi=180, timeout=240, execute=False):
    """Supply complete PDFs to a caller-owned contract; return a proposed reading.

    Digests are ordered: an act and its annexes can share one request. This does
    not classify documents, allocate a population, or certify output semantics.
    Identical requests replay their response, including after a caller rejects it.
    A source-review request must state its changed instruction explicitly.
    """
    import pymupdf
    digests = list(digests)
    if not digests or len(set(digests)) != len(digests):
        raise ValueError('Supply distinct source hashes in document order')
    if any(len(d) != 64 or any(c not in '0123456789abcdef' for c in d) for d in digests):
        raise ValueError('Expected source SHA-256 identifiers')
    if effort not in {'low', 'medium', 'high', 'xhigh', 'max'} or dpi <= 0 or timeout <= 0:
        raise ValueError('Invalid reading configuration')
    with TemporaryDirectory(prefix='cordon-codex-documents-') as temporary:
        directory = Path(temporary)
        supplied = (prompt + '\nOriginal source images follow in document order, then physical '
                    'page order. Source hashes identify bytes, not interpreted document relationships.\n')
        images, image_hashes = [], []
        for digest in digests:
            source = blob_path(store, digest)
            if sha256(source.read_bytes()).hexdigest() != digest:
                raise ValueError('Source bytes do not match their hash')
            with pymupdf.open(source) as document:
                supplied += f'\nDOCUMENT {digest}; {len(document)} page images\n'
                for number, page in enumerate(document, 1):
                    supplied += f'PHYSICAL PAGE {number}\n{page.get_text(sort=True)}\n'
                    png = page.get_pixmap(dpi=dpi).tobytes('png')
                    image = directory / f'{digest}-{number}.png'
                    image.write_bytes(png)
                    images.append(image)
                    image_hashes.append(sha256(png).hexdigest())
                supplied += 'END DOCUMENT\n'
        request = {'transport_version': 1, 'provider': 'codex-subscription', 'model': model,
                   'effort': effort, 'sources': digests, 'prompt': supplied,
                   'schema': schema, 'images': image_hashes, 'dpi': dpi}
        request_id = sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        target = store / 'derived/document-readings' / (request_id + '.json')
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.with_suffix('.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if target.exists():
                response = json.loads(target.read_text())
                if response['request'] != request or response['request_sha256'] != request_id:
                    raise ValueError('Retained request identity mismatch')
            else:
                if not execute:
                    raise FileNotFoundError('No retained response for this exact request')
                started = monotonic()
                output = _call(supplied, schema, images, directory, model, effort, timeout)
                response = {'request_sha256': request_id, 'request': request, 'output': output,
                            'captured_at': datetime.now(timezone.utc).isoformat(),
                            'seconds': round(monotonic() - started, 3)}
                temporary_response = target.with_suffix('.tmp')
                temporary_response.write_text(json.dumps(response, ensure_ascii=False) + '\n')
                os.replace(temporary_response, target)
        return dict(response, reading=json.loads(response['output']))
