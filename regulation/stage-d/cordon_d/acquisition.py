"""Immutable public-source captures for D research, separate from source validity."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request


def capture_public(url: str, destination: Path, *, parent: str, timeout: float = 90):
    """Make one fresh capture; an existing directory can never act as a cache.

    A refresh uses a new destination even if source IDs or URLs are unchanged.
    Interrupted bodies remain explicitly partial. HTTP success records acquired
    bytes only: source type, completeness, identity and meaning need inspection.
    """
    destination.mkdir(parents=True, exist_ok=False)
    record = {'url': url, 'parent': parent,
              'started_at': datetime.now(timezone.utc).isoformat(), 'complete_body': False}
    manifest = destination/'retrieval.json'
    manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2))
    partial = destination/'body.partial'
    digest = hashlib.sha256()
    size = 0
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            response = urllib.request.urlopen(request, timeout=timeout)
        except urllib.error.HTTPError as error:
            response = error  # Preserve the actual failure response as evidence.
        with response:
            record.update(status=response.status, final_url=response.url,
                          headers={key: value for key, value in response.headers.items()
                                   if key.lower() in {'content-type', 'content-length',
                                                      'last-modified', 'etag', 'content-disposition'}})
            manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2))
            with partial.open('xb') as handle:
                while block := response.read(1024 * 1024):
                    handle.write(block)
                    digest.update(block)
                    size += len(block)
            declared_size = response.headers.get('Content-Length')
            if declared_size is not None and int(declared_size) != size:
                raise ValueError('Response body differs from its declared byte length')
        partial.rename(destination/'body')
        record.update(complete_body=True, body='body')
    except Exception as error:
        record['error'] = str(error)
        if partial.exists():
            record['body'] = 'body.partial'
    record.update(bytes=size, sha256=digest.hexdigest(),
                  finished_at=datetime.now(timezone.utc).isoformat())
    manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2))
    return record
