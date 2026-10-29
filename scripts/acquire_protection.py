#!/usr/bin/env python3
"""Capture the protected-plant sources row 9 reads: the instruments that give a tree monumental or historic-interest
status, and the statutes A reads them from.

`register` captures SIT `Operationals/UliviMonumentali` layers 1 (listed trees) and 0 (provisional trees):
the layer description, the complete object-id list, and every feature page, each page's response bytes as
one store blob. `acts` captures the named L.R. 14/2007 list acts and other routes, one record per attempt.
`national-list` captures MASAF's page of the elenco degli alberi monumentali d'Italia (L. 10/2013 Art. 7), its
decrees page, each decree's page with every annex it links, the current Puglia sheet, and each decree's notice
in the Gazzetta Ufficiale. `declarations` captures the PPTR layer "Immobili e aree di notevole interesse
pubblico" (D.lgs. 42/2004 Art. 136) in every PPTR version the SIT service publishes, then runs
`declaration-decrees`: the Gazzetta Ufficiale issue that published each declaration's decree, placed through the
G.U.'s yearly archive where the layer's number or date names none. `declaration-supplements` adds each ordinary
supplement whose issue's own index places an act of notable public interest in it; `declaration-schede` the PPTR
scheda of each declaration whose layer motivation reaches the field's length; `declaration-search` the G.U. issues
since the PPTR version before the latest, for declarations the layer does not yet print. Run them in that order:
`declarations` rewrites the record. `statutes` captures from Normattiva each version, in force since
2020, of L. 10/2013 Art. 7 and D.lgs. 42/2004 Arts 136, 139-141, 141-bis, 146 and 157, with its vigency.
Records go to `corpus/sources/protected-status/`; the bytes go to the store. A failed attempt keeps its cause.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import re
from pathlib import Path
import sys
import time
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'regulation/stage-d'), str(ROOT / 'regulation/stage-c')]
from cordon_d.store import put_bytes, store_root  # noqa: E402

OUT = ROOT / 'corpus/sources/protected-status'
SERVICE = 'https://webapps.sit.puglia.it/arcgis/rest/services/Operationals/UliviMonumentali/MapServer'
AGENT = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)'}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _get(url, *, attempts=4, timeout=(20, 180), session=None):
    import requests
    for attempt in range(attempts):
        try:
            response = (session or requests).get(url, headers=AGENT, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException:
            if attempt == attempts - 1:
                raise
            time.sleep(5 * (attempt + 1))


def _capture(store, url, purpose, *, expect: bytes | None = None, session=None, timeout=(20, 300), attempts=3,
             **extra) -> tuple[dict, bytes | None]:
    """One attempt record, with the bytes put in the store; a failed attempt keeps its cause."""
    record = {'url': url, 'purpose': purpose, **extra, 'captured_at': _now()}
    try:
        response = _get(url, attempts=attempts, timeout=timeout, session=session)
        record.update(status=response.status_code, final_url=response.url,
                      content_type=response.headers.get('Content-Type'), bytes=len(response.content))
        if expect is not None and not response.content.lstrip()[:len(expect)] == expect:
            raise ValueError(f'the route did not return {expect!r}')
        record['sha256'] = put_bytes(store, response.content)
        return record, response.content
    except Exception as error:  # the attempt and its cause are kept
        record['error'] = str(error)[:400]
        return record, None


def _anchors(content: bytes) -> list[tuple[str, str]]:
    """(href, text) of every anchor on a page, entities resolved."""
    import html
    text = content.decode('utf-8', errors='replace')
    text = re.sub(r'<script.*?</script>|<style.*?</style>', '', text, flags=re.S)
    return [(html.unescape(m.group(1)), re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', m.group(2)))).strip())
            for m in re.finditer(r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', text, re.S)]


def _page_text(content: bytes) -> str:
    import html
    text = content.decode('utf-8', errors='replace')
    text = re.sub(r'<script.*?</script>|<style.*?</style>', '', text, flags=re.S)
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', text)))


def _write(name: str, record) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(record, ensure_ascii=False, indent=1) + '\n')


# --- L. 10/2013 Art. 7: the elenco degli alberi monumentali d'Italia (MASAF) ----------------------------------

MASAF = 'https://www.masaf.gov.it'
MASAF_PAGE = MASAF + '/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/{}'
LIST_PAGE, DECREES_PAGE = 11260, 11268
# The implementing decree of 23 October 2014 and the census instructions: the frame of a scheda's coordinates (GPS
# in WGS 84) and where a row's or a group's single point is taken.
METHOD_PAGES = {11270: r'D\.M\. 23/10/2014', 11274: r'^(Guida Tecnica|Allegato 3 - Scheda di identificazione|'
                                                     r'Allegato 4 - Istruzioni)'}
REGION = 'Puglia'
GU = 'https://www.gazzettaufficiale.it'
# "Con decreto ... prot. n. 661 del 09/08/2018, pubblicato in G.U. n. 231 del 04/10/2018" as the list page prints it.
DECREE_SENTENCE = re.compile(r"prot\.\s*n\.\s*(\d+)\s+del\s+(\d{1,2}(?:/\d{1,2}/|\s+\w+\s+)\d{4}),\s*pubblicat\w\s+in\s+"
                             r"G\.\s*U\.\s*n\.\s*(\d+)\s+del\s+(\d{1,2})/(\d{1,2})/(\d{4})", re.I)


def national_list():
    store = store_root(OUT)
    pages, documents, notices = [], [], []
    list_record, list_page = _capture(store, MASAF_PAGE.format(LIST_PAGE), 'the elenco page: each decree, its date and '
                                      'its G.U. publication as MASAF states them, and the current regional sheets')
    pages.append(list_record)
    decrees_record, decrees_page = _capture(store, MASAF_PAGE.format(DECREES_PAGE), 'the national rules page: one '
                                            'link per approving or updating decree')
    pages.append(decrees_record)
    if list_page is None or decrees_page is None:
        raise SystemExit('the MASAF pages were not captured: ' + json.dumps(pages))
    sheets = [(h, t) for h, t in _anchors(list_page) if 'ServeAttachment' in h and t.startswith(REGION)]
    if len(sheets) != 1:
        raise SystemExit(f'{len(sheets)} {REGION} sheets on the list page')
    record, _ = _capture(store, urllib.parse.urljoin(MASAF, sheets[0][0]), f'the current {REGION} sheet of the elenco',
                         label=sheets[0][1], page=list_record['url'])
    documents.append(record)
    decree_pages = [(h, t) for h, t in _anchors(decrees_page)
                    if re.search(r"(aggiornamento|Approvazione) dell'elenco nazionale degli Alberi Monumentali", t, re.I)]
    for href, label in decree_pages:
        page_record, page = _capture(store, urllib.parse.urljoin(MASAF, href), 'a decree page: the decree and its annexes',
                                     label=label)
        pages.append(page_record)
        for attachment, text in ([] if page is None else _anchors(page)):
            if 'ServeAttachment' in attachment:
                record, _ = _capture(store, urllib.parse.urljoin(MASAF, attachment), 'a document the decree page links',
                                     label=text, page=page_record['url'])
                documents.append(record)
                print(json.dumps({k: record.get(k) for k in ('label', 'bytes', 'sha256', 'error')}), flush=True)
    for number, wanted in METHOD_PAGES.items():
        page_record, page = _capture(store, MASAF_PAGE.format(number), 'a census method page')
        pages.append(page_record)
        for attachment, text in ([] if page is None else _anchors(page)):
            if 'ServeAttachment' in attachment and '/E/pdf' in attachment and re.search(wanted, text):
                record, _ = _capture(store, urllib.parse.urljoin(MASAF, attachment), 'the census method: the frame '
                                     "of a scheda's coordinates and the point of a row or group", label=text,
                                     page=page_record['url'])
                documents.append(record)
    for number, adopted, gu_number, day, month, year in DECREE_SENTENCE.findall(_page_text(list_page)):
        issue = f'{GU}/eli/gu/{year}/{int(month):02d}/{int(day):02d}/{gu_number}/sg/html'
        issue_record, issue_page = _capture(store, issue, f'the G.U. issue that MASAF states published decree prot. '
                                            f'n. {number} of {adopted}', decree=number)
        notices.append(issue_record)
        acts = {h for h, t in ([] if issue_page is None else _anchors(issue_page))
                if 'caricaDettaglioAtto' in h and re.search(r'alberi monumentali', t, re.I)}
        for href in sorted(acts):
            record, page = _capture(store, urllib.parse.urljoin(GU, href), f'the G.U. notice of decree prot. n. {number}',
                                    decree=number)
            notices.append(record)
            # The notice's text is served into the act page by its own route.
            body = re.search(r'src="(/atto/serie_generale/caricaArticoloDefault/[^"]+)"',
                             (page or b'').decode('utf-8', 'replace'))
            if body:
                record, _ = _capture(store, urllib.parse.urljoin(GU, body.group(1).replace('&amp;', '&')),
                                     f'the text of the G.U. notice of decree prot. n. {number}', decree=number)
                notices.append(record)
        if not acts:
            notices.append({'url': issue, 'decree': number, 'captured_at': _now(),
                            'error': 'the issue lists no act whose title names the alberi monumentali'})
    _write('national-list.json', {'source': MASAF_PAGE.format(LIST_PAGE), 'region': REGION, 'captured_at': _now(),
                                  'pages': pages, 'documents': documents, 'notices': notices})


# --- D.lgs. 42/2004 Art. 136: declarations of notable public interest (the PPTR layer and the decrees) ----------

PPTR = 'https://webapps.sit.puglia.it/arcgis/rest/services/Operationals/PPTR_APPROVATO/MapServer'
DECLARATIONS_LAYER = 'Immobili e aree di notevole interesse pubblico'
# "G.U. n. 149 del 15-06-1971", as the layer's PUBBLICATO prints a G.U. publication.
GU_PUBLICATION = re.compile(r'G\.\s*U\.\s*n\.\s*(\d*)\s*d\w*\s*(\d{1,2})[-/](\d{1,2})[-/](\d{4})', re.I)


def declarations(workers: int):
    store = store_root(OUT)
    service_record, service = _capture(store, f'{PPTR}?f=json', 'the PPTR service: one group per PPTR version')
    if service is None:
        raise SystemExit(json.dumps(service_record))
    layers = json.loads(service)['layers']
    by_id = {layer['id']: layer for layer in layers}

    def version_of(layer):
        while layer['parentLayerId'] != -1:
            layer = by_id[layer['parentLayerId']]
        return layer
    versions = []
    for layer in layers:
        if layer['name'].strip() != DECLARATIONS_LAYER:
            continue
        root = version_of(layer)
        base = f"{PPTR}/{layer['id']}"
        description, _ = _capture(store, f'{base}?f=json', 'the layer description')
        ids = sorted(json.loads(_get(f'{base}/query?where=1%3D1&returnIdsOnly=true&f=json').content)['objectIds'])
        count = json.loads(_get(f'{base}/query?where=1%3D1&returnCountOnly=true&f=json').content)['count']
        if count != len(ids):
            raise SystemExit(f'layer {layer["id"]}: count {count} differs from its object-id list {len(ids)}')
        pages = []
        for window in (ids[i:i + 500] for i in range(0, len(ids), 500)):
            query = f'{base}/query?' + urllib.parse.urlencode({
                'where': f'OBJECTID>={window[0]} AND OBJECTID<={window[-1]}', 'outFields': '*', 'returnGeometry': 'true',
                'outSR': 32633, 'orderByFields': 'OBJECTID', 'f': 'json'})
            page, content = _capture(store, query, 'the declarations of the version in one object-id window, '
                                     'attributes and polygon', first_oid=window[0], last_oid=window[-1])
            rows = len(json.loads(content)['features']) if content else None
            if rows is not None and rows != len(window):
                page['error'] = f'{rows} of {len(window)} rows returned'
            pages.append(page)
        versions.append({'version': root['name'].strip(), 'group': root['id'], 'layer': layer['id'], 'rows': count,
                         'description': description, 'pages': pages})
        print(json.dumps({'version': root['name'].strip(), 'layer': layer['id'], 'rows': count}), flush=True)
    _write('declarations.json', {'service': PPTR, 'layer': DECLARATIONS_LAYER, 'captured_at': _now(),
                                 'service_description': service_record, 'versions': versions, 'decrees': []})
    declaration_decrees(workers)


def declaration_decrees(workers: int):
    """The decree of each declaration the held layers print as published in the G.U.: the whole issue, as the G.U.
    publishes issues before 1986 only as page images. A publication printing no issue number keeps its cause."""
    from cordon_d.store import blob_path
    store = store_root(OUT)
    record = json.loads((OUT / 'declarations.json').read_text())
    issues, unplaced, decree_year = {}, {}, {}
    for page in (p for version in record['versions'] for p in version['pages'] if 'sha256' in p):
        for feature in json.loads(blob_path(store, page['sha256']).read_bytes())['features']:
            a = feature['attributes']
            year = re.search(r'(\d{4})\s*$', a.get('NUMERO_DEC') or '')
            if year:
                decree_year[a.get('CODICE')] = year.group(1)
            found = GU_PUBLICATION.search(a.get('PUBBLICATO') or '')
            if found and found.group(1):
                number, day, month, year = found.groups()
                key = (year, f'{int(month):02d}', f'{int(day):02d}', number)
                issues.setdefault(key, set()).add(a.get('CODICE'))
            elif re.search(r'G\.\s*U', a.get('PUBBLICATO') or ''):
                unplaced.setdefault(a.get('PUBBLICATO').strip(), set()).add(a.get('CODICE'))

    held = {d['url']: d for d in record.get('decrees') or () if d.get('sha256') and d.get('url')}

    def issue(item):
        import shutil
        (year, month, day, number), codes = item
        if f'{GU}/eli/gu/{year}/{month}/{day}/{number}/sg/pdf' in held:
            return held[f'{GU}/eli/gu/{year}/{month}/{day}/{number}/sg/pdf'] | {'declarations': sorted(codes)}
        if shutil.disk_usage(store).free < 3.05e9:  # the working floor of free disk (3 GB)
            return {'url': f'{GU}/eli/gu/{year}/{month}/{day}/{number}/sg/pdf', 'declarations': sorted(codes),
                    'captured_at': _now(), 'error': 'not attempted: free disk below the 3 GB floor'}
        record, _ = _capture(store, f'{GU}/eli/gu/{year}/{month}/{day}/{number}/sg/pdf',
                             'the G.U. issue the layer states published the declaration', expect=b'%PDF',
                             timeout=(30, 1800), attempts=3, declarations=sorted(codes))
        print(json.dumps({k: record.get(k) for k in ('url', 'bytes', 'error')}), flush=True)
        return record
    with ThreadPoolExecutor(workers) as pool:
        decrees = list(pool.map(issue, sorted(issues.items())))
    # Where the G.U. names no issue for the printed number and date, or the layer prints only one of them, the
    # G.U.'s own archive of the year places it: the issue of that date, or of that number.
    archives = {}

    def archive(year):
        if year not in archives:
            page_record, page = _capture(store, f'{GU}/ricercaArchivioCompleto/serie_generale/{year}',
                                         'the G.U. serie generale issues of the year')
            archives[year] = (page_record, [m.groups() for h, _ in ([] if page is None else _anchors(page))
                                            for m in [re.search(r'dataPubblicazioneGazzetta=(\d{4}-\d{2}-\d{2})'
                                                                r'&numeroGazzetta=(\d+)', h)] if m])
        return archives[year]

    def placed_by_archive(codes, year, day=None, number=None, supplement=None, cause=''):
        page_record, listed = archive(year)
        found = [(d, n) for d, n in listed if (day is None or d == day) and (number is None or n == number)]
        if len(found) != 1:
            return {'declarations': sorted(codes), 'archive': page_record.get('sha256'), 'captured_at': _now(),
                    'error': f'{cause}; the {year} archive lists {len(found)} issues for it'}
        d, n = found[0]
        y, m, dd = d.split('-')
        tail = f'so/{supplement}/sg/pdf' if supplement else 'sg/pdf'
        record, _ = _capture(store, f'{GU}/eli/gu/{y}/{m}/{dd}/{n}/{tail}', 'the G.U. issue the year\'s archive places '
                             'for the publication the layer prints', expect=b'%PDF', timeout=(30, 1800),
                             declarations=sorted(codes), archive=page_record.get('sha256'), printed=cause)
        return record
    for i, d in enumerate(decrees):
        if 'notFound' in (d.get('final_url') or ''):
            y, m, dd, n = re.search(r'/eli/gu/(\d{4})/(\d{2})/(\d{2})/(\d+)/', d['url']).groups()
            by_date = placed_by_archive(d['declarations'], y, day=f'{y}-{m}-{dd}', cause=f'G.U. n. {n} of {dd}-{m}-{y}: '
                                        'the G.U. names no issue by that number on that date')
            decrees[i] = by_date if 'sha256' in by_date else placed_by_archive(
                d['declarations'], y, number=n, cause=by_date['error'])
            print(json.dumps({k: decrees[i].get(k) for k in ('url', 'bytes', 'error')}), flush=True)
    for text, codes in sorted(unplaced.items()):
        dated = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})', text)
        numbered = re.search(r'G\.\s*U\.\s*n\.\s*(\d+)', text)
        supplement = re.search(r'Suppl\w*\.?\s*Ord\w*\.?\s*n\.\s*(\d+)', text, re.I)
        years = sorted({decree_year[c] for c in codes if c in decree_year})
        if dated:
            y = dated.group(3)
            placed = placed_by_archive(codes, y, day=f'{y}-{int(dated.group(2)):02d}-{int(dated.group(1)):02d}',
                                       cause=f'"{text}" prints a date and no issue number')
        elif numbered and len(years) == 1:
            # The layer prints the decree's own date: its publication is placed in that year.
            placed = placed_by_archive(codes, years[0], number=numbered.group(1),
                                       supplement=supplement and supplement.group(1),
                                       cause=f'"{text}" prints an issue number and no date; the decree is of {years[0]}')
        else:
            placed = {'publication': text, 'declarations': sorted(codes), 'captured_at': _now(),
                      'error': 'the layer prints no G.U. issue number and date that name one issue'}
        decrees.append(placed)
        print(json.dumps({k: placed.get(k) for k in ('url', 'bytes', 'error')}), flush=True)
    record['decrees'] = decrees
    _write('declarations.json', record)


# An issue's own index on the G.U.'s site lists each act it publishes, an act printed in an ordinary supplement marked
# "(Suppl. Ordinario n. N)": the issue's pages then print only the act's title. Where the index of an issue that
# published a declaration places an act of notable public interest in a supplement, the supplement is captured for the
# issue's declarations; the reader finds each declaration's act in it by its title and date.
def declaration_supplements(workers: int):
    import shutil
    store = store_root(OUT)
    record = json.loads((OUT / 'declarations.json').read_text())
    held = {d['url'] for d in record['decrees'] if d.get('sha256')}
    issues = [d for d in record['decrees'] if d.get('sha256') and re.search(r'/eli/gu/\d{4}/\d{2}/\d{2}/\d+/sg/pdf$', d['url'])]

    def placed(issue):
        y, m, d, n = re.search(r'/eli/gu/(\d{4})/(\d{2})/(\d{2})/(\d+)/sg/pdf$', issue['url']).groups()
        url = f'{GU}/gazzetta/serie_generale/caricaDettaglio?dataPubblicazioneGazzetta={y}-{m}-{d}&numeroGazzetta={n}'
        try:
            content = _get(url).content
        except Exception as error:
            return [{'index': url, 'declarations': issue['declarations'], 'captured_at': _now(),
                     'error': f"the issue's index is not read: {str(error)[:300]}"}]
        numbers = sorted({m.group(1) for block in content.decode('utf-8', errors='replace').split('class="risultato"')[1:]
                          if re.search(r'notevole\s+interesse\s+pubblico', _page_text(block.encode()), re.I)
                          for m in [re.search(r'Suppl\.\s*Ordinario\s*n\.\s*(\d+)', _page_text(block.encode()))] if m})
        out = []
        for number in numbers:
            target = f'{GU}/eli/gu/{y}/{m}/{d}/{n}/so/{number}/sg/pdf'
            if target in held:
                continue
            if shutil.disk_usage(store).free < 3.05e9:  # the working floor of free disk (3 GB)
                out.append({'url': target, 'declarations': issue['declarations'], 'captured_at': _now(),
                            'error': 'not attempted: free disk below the 3 GB floor'})
                continue
            supplement, _ = _capture(store, target, "the ordinary supplement the issue's index places an act of notable "
                                     'public interest in', expect=b'%PDF', timeout=(30, 1800),
                                     declarations=issue['declarations'], index=put_bytes(store, content))
            out.append(supplement)
        return out
    with ThreadPoolExecutor(workers) as pool:
        found = [r for records in pool.map(placed, issues) for r in records]
    for r in found:
        print(json.dumps({k: r.get(k) for k in ('url', 'index', 'bytes', 'error')}), flush=True)
    record['decrees'] += [r for r in found if r.get('url')]
    _write('declarations.json', record)


# The PPTR's elaborato 6.4: one scheda per declaration, whose text layer prints the declaration's motivation
# ("riconoscimento") whole. Held for each declaration whose layer motivation reaches the field's length, where the
# layer may cut it (a scheda is about 26 MB; all of them would not fit the store's disk floor).
SCHEDE = ('https://pugliacon.regione.puglia.it/web/sit-puglia-paesaggio/6.4.-schede-di-identificazione-e-di-'
          'definizione-delle-prescrizioni-d-uso-degli-immobili-e-delle-aree-di-notevole-interesse-pubblico')
FIELD_LENGTH = 254


def declaration_schede(workers: int):
    import shutil
    from cordon_d.store import blob_path
    store = store_root(OUT)
    record = json.loads((OUT / 'declarations.json').read_text())
    latest = record['versions'][0]
    cut = set()
    for page in (p for p in latest['pages'] if 'sha256' in p):
        for feature in json.loads(blob_path(store, page['sha256']).read_bytes())['features']:
            a = feature['attributes']
            if len((a.get('MOTIVAZI_1') or '').strip()) >= FIELD_LENGTH - 4:
                cut.add(a['CODICE'].strip())
    index, content = _capture(store, SCHEDE, 'the elaborato 6.4 page: one scheda per declaration')
    links = {}
    for href, text in ([] if content is None else _anchors(content)):
        found = re.search(r'(PAE\d{4})', href + ' ' + text)
        if '/documents/' in href and found:
            links.setdefault(found.group(1), urllib.parse.urljoin(SCHEDE, href))
    held = {s['code']: s for s in record.get('schede', {}).get('schede', []) if s.get('sha256')}

    def scheda(code):
        if code in held:
            return held[code]
        if code not in links:
            return {'code': code, 'captured_at': _now(), 'error': 'the elaborato 6.4 page links no scheda for it'}
        if shutil.disk_usage(store).free < 3.05e9:
            return {'code': code, 'url': links[code], 'captured_at': _now(),
                    'error': 'not attempted: free disk below the 3 GB floor'}
        captured, _ = _capture(store, links[code], 'the scheda of a declaration whose layer motivation reaches the '
                               'field length', expect=b'%PDF', timeout=(30, 1800), code=code)
        print(json.dumps({k: captured.get(k) for k in ('code', 'bytes', 'error')}), flush=True)
        return captured
    with ThreadPoolExecutor(workers) as pool:
        schede = list(pool.map(scheda, sorted(cut)))
    record['schede'] = {'page': index, 'schede': schede}
    _write('declarations.json', record)


# The G.U.'s own issues from the version before the latest PPTR version to the capture: every declaration the
# Ministry (Art. 138(3), 141) or the Region (Art. 140) publishes there, to check the layer against.
SEARCH_FROM = '2026-03-31'   # DGR 328/2026, the PPTR version before DGR 1155/2026
_DECLARATION_TITLE = re.compile(r'notevole\s+interesse\s+pubblico', re.I)


def declaration_search():
    store = store_root(OUT)
    record = json.loads((OUT / 'declarations.json').read_text())
    today = datetime.now(timezone.utc).date().isoformat()
    issues, matches, years = [], [], range(int(SEARCH_FROM[:4]), int(today[:4]) + 1)
    for year in years:
        archive, page = _capture(store, f'{GU}/ricercaArchivioCompleto/serie_generale/{year}',
                                 'the G.U. serie generale issues of the year')
        issues.append(archive)
        for href, _ in ([] if page is None else _anchors(page)):
            found = re.search(r'dataPubblicazioneGazzetta=(\d{4}-\d{2}-\d{2})&numeroGazzetta=(\d+)', href)
            if not found or not SEARCH_FROM <= found.group(1) <= today:
                continue
            y, m, d = found.group(1).split('-')
            summary, content = _capture(store, f'{GU}/eli/gu/{y}/{m}/{d}/{found.group(2)}/sg/html',
                                        'an issue of the search window: its table of contents')
            issues.append(summary)
            for act, title in ([] if content is None else _anchors(content)):
                if 'caricaDettaglioAtto' in act and _DECLARATION_TITLE.search(title):
                    hit, _ = _capture(store, urllib.parse.urljoin(GU, act), 'an act the issue titles a declaration of '
                                      'notable public interest', title=title)
                    matches.append(hit)
    record['gazette_search'] = {'from': SEARCH_FROM, 'to': today, 'captured_at': _now(), 'issues': issues,
                                'matches': matches}
    _write('declarations.json', record)
    print(json.dumps({'issues': len(issues), 'matches': [m.get('title') for m in matches]}, ensure_ascii=False))


# --- proposals of declaration of notable public interest (D.lgs. 42/2004 Arts 138-141, 157(2)) ------------------

PROPOSALS = 'proposals.json'
FLOOR = 3.05e9   # free bytes below which nothing more is captured (the 3 GB floor)
BURP = 'https://burp.regione.puglia.it'
BURP_PORTLET = 'it_indra_regione_puglia_burp_web_SearchDocumentiPortlet_INSTANCE_LylqGTMESls6'
# The BURP's document search matches a quoted phrase in an act's title and abstract (not its text); its index begins
# with the bulletins of 2001. The phrases a proposal, its publication, its outcome or the Art. 137 commission print.
BURP_QUERIES = ('"notevole interesse"', '"dichiarazione di notevole"', '"proposta di dichiarazione"',
                '"proposta di vincolo"', '"vincolo paesaggistico"', '"bellezze naturali"', '"interesse pubblico"',
                '"dichiarazione d’interesse"', "\"dichiarazione d'interesse\"", '"interesse paesaggistico"',
                '"tutela paesaggistica"', '"determinazione negativa"', '"commissioni regionali"', '"art. 137"',
                '"art. 138"', '"art. 139"', '"art. 140"', '"art. 141"', '"490/99"', '"1497"', '"ulivi secolari"',
                '"albero monumentale"', '"alberi monumentali"', '"albero"')
# A result whose abstract proposes, opens, rectifies, declares or refuses a declaration, or names the Art. 137
# commission: its act is captured.
_BURP_ACT = re.compile(r"(?:propost\w*|avvio\s+del\s+procedimento|rettifica|dichiarazione|provvedimento|determinazione\s+"
                       r"negativa)\W+(?:\w+\W+){0,6}?(?:notevole\s+interesse|d.\s*interesse\s+pubblico|vincolo\s+paesaggistico)|"
                       r"commission\w*\s+regional\w*\s+(?:di\s+cui\s+)?(?:all.\s*)?art\.?\s*137|art\.?\s*137\s+del\s+D", re.I)
PORTAL = 'https://pugliacon.regione.puglia.it'
# The Region's landscape portal (paesaggio.regione.puglia.it redirects here) and the PPTR's own report on its system of
# protections, which would list a proposal in progress when the plan was made.
PORTAL_PAGES = ('/web/sit-puglia-paesaggio/home', '/web/sit-puglia-paesaggio/il-sistema-delle-tutele',
                '/web/sit-puglia-paesaggio/il-sistema-delle-tutele1', '/web/sit-puglia-paesaggio/news-paesaggio',
                '/web/sit-puglia-paesaggio/normativa')
PPTR_REPORTS = ('/documents/96721/759101/6._Sistema+delle+tutele+relazione.pdf/807e8df7-4014-b01f-0923-0bd0d421c27c',
                '/documents/96721/759101/PPTR_Sistema_tutele_quadro_sinottico.pdf/812763bb-2698-e2f5-1ca4-c90972372ec5')
# The Ministry's proposers in Puglia (the DG's list of Soprintendenze) and the DG that adopts their declarations. A
# WordPress site's own lists are its archive; Bari's site left WordPress in June 2026 and is read by its sections.
MINISTRY = (
    ('Soprintendenza ABAP per le province di Barletta-Andria-Trani e Foggia', 'https://sabapfoggia.cultura.gov.it',
     'wordpress', ()),
    ('Soprintendenza ABAP per le province di Brindisi, Lecce e Taranto', 'https://sabap-le.cultura.gov.it', 'wordpress',
     ()),
    ('Soprintendenza ABAP per la città metropolitana di Bari', 'https://sabapba.cultura.gov.it', 'sections',
     ('/bandi-e-avvisi', '/bandi-e-avvisi/archivio', '/eventi-e-news', '/eventi-e-news/archivio',
      '/amministrazione-trasparente', '/modulistica-e-documenti', '/aree-di-intervento')),
    ('Direzione generale Archeologia, belle arti e paesaggio', 'https://dgabap.cultura.gov.it', 'wordpress', ()),
)
ARCHIVE = 'https://web.archive.org'
# The Internet Archive's index of each Ministry host (and the hosts before 2022), filtered to the words a proposal's
# page or document prints in its address.
ARCHIVE_HOSTS = ('sabapfoggia.cultura.gov.it', 'sabap-le.cultura.gov.it', 'sabapba.cultura.gov.it',
                 'dgabap.cultura.gov.it', 'www.sabap-le.beniculturali.it', 'www.sabap-ba.beniculturali.it',
                 'www.sabap-fg.beniculturali.it')
ARCHIVE_FILTER = 'original:.*(notevole|propost|dichiarazion|vincol|paesagg).*'
_PROPOSAL_ADDRESS = re.compile(r'propost\w*-di-dichiarazione|proposta.*notevole', re.I)


def _room(store) -> bool:
    import shutil
    return shutil.disk_usage(store).free >= FLOOR


def _burp_url(query: str, delta: int = 500) -> str:
    p = f'_{BURP_PORTLET}_'
    return f'{BURP}/documenti?' + urllib.parse.urlencode({
        'p_p_id': BURP_PORTLET, 'p_p_lifecycle': '0', 'p_p_state': 'normal', 'p_p_mode': 'view', p + 'numeroDoc': '',
        p + 'searchContent': query, p + 'toggler': 'false', p + 'datefilter': '', p + 'docanno': '', p + 'bolnumero': '',
        p + 'bolnumeroSupplemento': '', p + 'Argomenti': '', p + 'Sezioni': '', p + 'resetCur': 'false',
        p + 'delta': str(delta), p + 'cur': '1'})


def burp_items(content: bytes) -> list[dict]:
    """Each result of a BURP document-search page: its title, abstract, section and the act's own document. The page
    is split on each result's markup (no pattern spans results)."""
    import html

    def clean(s):
        return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()
    out, bulletin = [], None
    parts = content.decode('utf-8', errors='replace').split('titolo-body">')
    for before, part in zip(parts, parts[1:]):
        header = before.rsplit('<h2 class="titolo">', 1)   # the bulletin a run of results is in heads it
        bulletin = clean(header[1].split('</h2>', 1)[0]) if len(header) > 1 else bulletin
        part = part[:8000]
        link = next((a.split('"', 1)[0] for a in part.split('href="')[1:]
                     if a.startswith(f'{BURP}/documents/')), None)
        abstract = part.split('class="blocco">', 1)
        section = part.split('Sezione: </span>', 1)
        out.append({'title': clean(part.split('</div>', 1)[0]),
                    'abstract': clean(abstract[1].split('</div>', 1)[0]) if len(abstract) > 1 else '',
                    'section': clean(section[1].split('</span>', 1)[0]) if len(section) > 1 else '', 'url': link,
                    'bulletin': bulletin})
    return out


def proposals():
    """The routes that publish a proposal of declaration in Puglia (Art. 139(2): the Region's site and the proposer's),
    each captured with what it holds. The record's `proposals` (each proposal found, with its printed fields and their
    sources) are kept as they are."""
    import requests
    store = store_root(OUT)
    path = OUT / PROPOSALS
    record = json.loads(path.read_text()) if path.exists() else {}
    routes = {}
    # The BURP: each query's result page, and each act a result's abstract names as a proposal, its outcome or the
    # commission's.
    pages, acts, seen = [], [], {}
    for query in BURP_QUERIES:
        if not _room(store):
            pages.append({'query': query, 'captured_at': _now(), 'error': 'not attempted: free disk below the floor'})
            continue
        captured, content = _capture(store, _burp_url(query), 'the BURP document search for a phrase', query=query)
        items = [] if content is None else burp_items(content)
        captured['results'] = len(items)
        pages.append(captured)
        print(json.dumps({'query': query, 'results': len(items), 'error': captured.get('error')}, ensure_ascii=False),
              flush=True)
        for item in items:
            if item['url'] and _BURP_ACT.search(item['abstract']):
                seen.setdefault(item['url'].split('?', 1)[0], item)   # one act under its document path
    for item in seen.values():
        url = item['url']
        if not _room(store):
            acts.append({**item, 'captured_at': _now(), 'error': 'not attempted: free disk below the floor'})
            continue
        captured, _ = _capture(store, url, 'an act a BURP result names as a proposal, its outcome or the commission\'s',
                               expect=b'%PDF', timeout=(30, 1800), title=item['title'], abstract=item['abstract'],
                               section=item['section'])
        acts.append(captured)
        print(json.dumps({k: captured.get(k) for k in ('title', 'bytes', 'error')}, ensure_ascii=False), flush=True)
    routes['burp'] = {'publisher': 'Regione Puglia: Bollettino Ufficiale (BURP), document search',
                      'search': f'{BURP}/documenti', 'index': 'a quoted phrase matches in an act\'s title and abstract; '
                      'the index begins with the bulletins of 2001 (two acts of 1999)', 'queries': pages, 'acts': acts}
    # The Region's landscape portal and the PPTR's report on its protections.
    portal = []
    for page in PORTAL_PAGES:
        captured, _ = _capture(store, PORTAL + page, 'a page of the Region\'s landscape portal')
        portal.append(captured)
    for report in PPTR_REPORTS:
        captured, _ = (_capture(store, PORTAL + report, 'the PPTR\'s report on its system of protections', expect=b'%PDF',
                                timeout=(30, 1800)) if _room(store) else
                       ({'url': PORTAL + report, 'captured_at': _now(), 'error': 'not attempted: free disk below the floor'},
                        None))
        portal.append(captured)
    routes['region_portal'] = {'publisher': 'Regione Puglia: landscape portal (http://paesaggio.regione.puglia.it '
                               'redirects here) and the PPTR', 'pages': portal}
    # The Ministry's proposers and its DG: each site's own lists or sections; a site that does not answer keeps its
    # cause and is not read further.
    ministry = []
    session = requests.Session()
    for name, host, kind, sections in MINISTRY:
        home, content = _capture(store, host + '/', 'the site\'s home page', session=session, attempts=2,
                                 timeout=(30, 120))
        entry = {'publisher': name, 'host': host, 'kind': kind, 'home': home, 'lists': []}
        if content is not None and kind == 'wordpress':
            for listing in ('posts', 'pages', 'media'):
                for number in range(1, 100):
                    captured, content = _capture(store, f'{host}/wp-json/wp/v2/{listing}?per_page=100&page={number}',
                                                 f'the site\'s own list of {listing}', session=session)
                    entry['lists'].append(captured)
                    if content is None or not json.loads(content):
                        break
        elif content is not None:
            for section in sections:
                captured, _ = _capture(store, host + section, 'a section of the site', session=session)
                entry['lists'].append(captured)
        ministry.append(entry)
        print(json.dumps({'host': host, 'home': home.get('status') or home.get('error'), 'lists': len(entry['lists'])}),
              flush=True)
    routes['ministry'] = ministry
    # The Internet Archive's index of each Ministry host, and its copy of each page whose address names a proposal
    # of declaration, with the documents that page links on the host.
    archive, documents = [], []
    for host in ARCHIVE_HOSTS:
        url = f'{ARCHIVE}/cdx/search/cdx?' + urllib.parse.urlencode({
            'url': f'{host}/*', 'output': 'json', 'collapse': 'urlkey', 'filter': ARCHIVE_FILTER,
            'fl': 'timestamp,original,mimetype,statuscode'})
        captured, content = _capture(store, url, 'the Internet Archive\'s index of the host, filtered', host=host,
                                     expect=b'[', timeout=(30, 300))
        rows = [] if content is None or not content.strip() else json.loads(content)[1:]
        captured['rows'] = len(rows)
        archive.append(captured)
        print(json.dumps({'host': host, 'rows': len(rows), 'error': captured.get('error')}), flush=True)
        time.sleep(10)   # the archive refuses quick successive queries
        for timestamp, original, _, status in rows:
            if status != '200' or not _PROPOSAL_ADDRESS.search(original) or 'wp-json' in original:
                continue
            page, content = _capture(store, f'{ARCHIVE}/web/{timestamp}id_/{original}', 'the Internet Archive\'s copy '
                                     'of a page whose address names a proposal of declaration', original=original,
                                     archived=timestamp)
            documents.append(page)
            for href, _ in ([] if content is None else _anchors(content)):
                if href.startswith(f'https://{host}/') and href.lower().endswith('.pdf'):
                    copy, _ = _capture(store, f'{ARCHIVE}/web/{timestamp}id_/{href}', 'the Internet Archive\'s copy of '
                                       'a document that page links', original=href, linked_from=original, expect=b'%PDF')
                    documents.append(copy)
    routes['archive'] = {'publisher': 'Internet Archive (Wayback Machine): copies of the Ministry\'s pages, a lead '
                         'route where the publisher does not answer', 'indexes': archive, 'documents': documents}
    record['routes'] = {**record.get('routes', {}), **routes, 'captured_at': _now()}
    _write(PROPOSALS, record)


# --- the Region's recognitions of monumentality (L. 10/2013 Art. 7(2) as in force from 20 September 2025) ----------

RECOGNITIONS = 'recognitions.json'
RECOGNISED_FROM = '2025-09-20'   # L. 131/2025: the Region recognises a tree as monumental, before a decree lists it
# The Region publishes its list acts in the BURP: the forestry section's determinations ("elenco regionale n. N") and
# the Giunta's deliberations ("elenco ... (Elenco L)"). The phrases their abstracts print.
RECOGNITION_QUERIES = ('"alberi monumentali"', '"Alberi Monumentali della Regione Puglia"',
                       '"alberi monumentali di Puglia"', '"elenco regionale"', '"monumentalità"')
_ELENCO = re.compile(r'Approvazione\s+(?:\w+\s+)?elenco\b.{0,60}?Alberi\s+Monumentali', re.I | re.S)
_BULLETIN_DATE = re.compile(r'del\s+(\d{2})/(\d{2})/(\d{4})')
# The Region's other routes the acts name (the forestry section's site, the transparency section) and MASAF's list
# page, which names the Web GIS the regions enter their trees in only as an application, with no public address.
RECOGNITION_ROUTES = ('https://foreste.regione.puglia.it/', 'https://www.regione.puglia.it/web/amministrazione-trasparente')


def recognitions():
    """Each act by which the Region approves a list of monumental trees and that its bulletin publishes from
    RECOGNISED_FROM on, held whole, with the routes tried."""
    store = store_root(OUT)
    pages, acts, seen = [], [], {}
    for query in RECOGNITION_QUERIES:
        captured, content = _capture(store, _burp_url(query), 'the BURP document search for a phrase', query=query)
        items = [] if content is None else burp_items(content)
        captured['results'] = len(items)
        pages.append(captured)
        for item in items:
            found = _BULLETIN_DATE.search(item.get('bulletin') or '')
            day = found and f'{found.group(3)}-{found.group(2)}-{found.group(1)}'
            if item['url'] and _ELENCO.search(item['abstract']) and day and day >= RECOGNISED_FROM:
                seen.setdefault(item['url'].split('?', 1)[0], item)
    for item in seen.values():
        if not _room(store):
            acts.append({**item, 'captured_at': _now(), 'error': 'not attempted: free disk below the floor'})
            continue
        captured, _ = _capture(store, item['url'], 'an act approving a list of monumental trees', expect=b'%PDF',
                               timeout=(30, 900), title=item['title'], abstract=item['abstract'],
                               bulletin=item['bulletin'])
        acts.append(captured)
        print(json.dumps({k: captured.get(k) for k in ('title', 'bulletin', 'bytes', 'error')}, ensure_ascii=False),
              flush=True)
    routes = [_capture(store, url, 'a route of the Region the acts name', attempts=2, timeout=(30, 60))[0]
              for url in RECOGNITION_ROUTES]
    _write(RECOGNITIONS, {'from': RECOGNISED_FROM, 'captured_at': _now(), 'burp': {
        'publisher': 'Regione Puglia: Bollettino Ufficiale (BURP), document search', 'search': f'{BURP}/documenti',
        'index': 'a quoted phrase matches in an act\'s title and abstract', 'queries': pages, 'acts': acts},
        'routes': routes})


# The G.U.'s issues from the selection margin's start to the day before row 9's own search: every declaration the
# Ministry or the Region publishes there recites the proposal it concludes.
PROPOSAL_SEARCH = ('2021-01-01', '2026-03-30')


def proposal_search(workers: int):
    from cordon_d.administrative import AdministrativeUnits
    store = store_root(OUT)
    path = OUT / PROPOSALS
    record = json.loads(path.read_text()) if path.exists() else {}
    start, end = PROPOSAL_SEARCH
    # A Puglia act is one whose title names a Puglia comune as ISTAT prints it (accents and case folded).
    import unicodedata

    def fold(text):
        return re.sub(r"[^a-z]+", ' ', unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower())
    comuni = sorted({fold(c.name).strip() for c in AdministrativeUnits(ROOT).comuni_of('Puglia')}, key=len,
                    reverse=True)
    archives, wanted = [], []
    for year in range(int(start[:4]), int(end[:4]) + 1):
        archive, page = _capture(store, f'{GU}/ricercaArchivioCompleto/serie_generale/{year}',
                                 'the G.U. serie generale issues of the year')
        archives.append(archive)
        for href, _ in ([] if page is None else _anchors(page)):
            found = re.search(r'dataPubblicazioneGazzetta=(\d{4}-\d{2}-\d{2})&numeroGazzetta=(\d+)', href)
            if found and start <= found.group(1) <= end:
                wanted.append(found.groups())
    wanted = sorted(set(wanted))
    # An issue an earlier run holds is read again from the store; only the others are fetched.
    from cordon_d.store import blob_path
    held = {i['url']: i for i in (record.get('routes', {}).get('gazette') or {}).get('issues') or ()
            if i.get('sha256')}
    print(f'{len(wanted)} issues, {len(held)} held', flush=True)

    def issue(item):
        day, number = item
        y, m, d = day.split('-')
        url = f'{GU}/eli/gu/{y}/{m}/{d}/{number}/sg/html'
        if url in held:
            summary, content = held[url], blob_path(store, held[url]['sha256']).read_bytes()
        elif not _room(store):
            return {'url': url, 'captured_at': _now(), 'error': 'not attempted: free disk below the floor'}, []
        else:
            summary, content = _capture(store, url, 'an issue of the search window: its table of contents')
        hits = []
        for act, title in ([] if content is None else _anchors(content)):
            if 'caricaDettaglioAtto' in act and _DECLARATION_TITLE.search(title):
                hit, _ = _capture(store, urllib.parse.urljoin(GU, act), 'an act the issue titles a declaration of '
                                  'notable public interest', title=title)
                # The whole act (a Ministry title may name only its context): Puglia's where it names a Puglia
                # comune or Puglia (since 2019 the Ministry declares through each region's commission).
                query = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(act).query))
                whole, text = _capture(store, f'{GU}/atto/vediMenuHTML?' + urllib.parse.urlencode({
                    'atto.dataPubblicazioneGazzetta': query.get('atto.dataPubblicazioneGazzetta'),
                    'atto.codiceRedazionale': query.get('atto.codiceRedazionale'), 'tipoSerie': 'serie_generale',
                    'tipoVigenza': 'originario'}), 'the act whole')
                padded = f' {fold(_page_text(text))} ' if text else f' {fold(title)} '
                hit.update(act_text=whole, puglia_comuni=[c for c in comuni if f' {c} ' in padded],
                           names_puglia=' puglia ' in padded)
                hits.append(hit)
        return summary, hits
    issues, matches = [], []
    with ThreadPoolExecutor(workers) as pool:
        for n, (summary, hits) in enumerate(pool.map(issue, wanted), 1):
            issues.append({k: summary[k] for k in ('url', 'captured_at', 'status', 'bytes', 'sha256', 'error')
                           if k in summary})   # each an issue's table of contents
            matches.extend(hits)
            if n % 50 == 0 or hits:
                print(json.dumps({'done': n, 'issue': summary.get('url'), 'matches': [h.get('title', '')[:90]
                                                                                      for h in hits]},
                                 ensure_ascii=False), flush=True)
    routes = record.setdefault('routes', {})
    routes['gazette'] = {'publisher': 'Gazzetta Ufficiale, serie generale: each issue\'s table of contents',
                         'from': start, 'to': end, 'captured_at': _now(), 'years': archives, 'issues': issues,
                         'matches': matches}
    _write(PROPOSALS, record)
    print(json.dumps({'issues': len(issues), 'failed': sum(1 for i in issues if i.get('error')),
                      'matches': len(matches), 'puglia': [m.get('title') for m in matches
                                                          if m.get('puglia_comuni') or m.get('names_puglia')]},
                     ensure_ascii=False), flush=True)


# --- the statutes A reads the instruments from (Normattiva) -----------------------------------------------------

NORMATTIVA = 'https://www.normattiva.it'
STATUTES = (
    ('L. 10/2013', 'urn:nir:stato:legge:2013-01-14;10~art7', '13G00031', ('7',)),
    ('D.lgs. 42/2004', 'urn:nir:stato:decreto.legislativo:2004-01-22;42~art136', '004G0066',
     ('136', '139', '140', '141', '141-bis', '146', '157')),
)
SINCE = '2020-01-01'
_VIGENCY = re.compile(r'in vigore dal:\s*(\d{1,2})-(\d{1,2})-(\d{4})(?:\s*al:\s*(\d{1,2})-(\d{1,2})-(\d{4}))?')


def statutes():
    import requests
    store = store_root(OUT)
    session = requests.Session()
    records = []
    for act, urn, code, articles in STATUTES:
        landing = _get(f'{NORMATTIVA}/uri-res/N2Ls?{urn}', session=session).content.decode('utf-8', 'replace')
        links = {}
        for href in re.findall(r'caricaArticolo\?[^"\' ]+', landing):
            href = href.replace('&amp;', '&')
            q = dict(urllib.parse.parse_qsl(href.split('?', 1)[1]))
            if q.get('art.codiceRedazionale') != code:
                continue
            article = q['art.idArticolo'] + ('' if q.get('art.idSottoArticolo') == '1' else
                                             {'2': '-bis', '3': '-ter'}.get(q.get('art.idSottoArticolo'), '?'))
            if article in articles:
                keep = {k: q[k] for k in ('art.versione', 'art.idGruppo', 'art.flagTipoArticolo', 'art.codiceRedazionale',
                                          'art.idArticolo', 'art.idSottoArticolo', 'art.idSottoArticolo1',
                                          'art.dataPubblicazioneGazzetta', 'art.progressivo')}
                links[(article, int(q['art.versione']))] = f'{NORMATTIVA}/atto/caricaArticolo?' + urllib.parse.urlencode(keep)
        missing = set(articles) - {a for a, _ in links}
        if missing:
            raise SystemExit(f'{act}: Normattiva lists no version of Art. {sorted(missing)}')
        for (article, version), url in sorted(links.items()):
            content = _get(url, session=session).content
            found = _VIGENCY.search(_page_text(content))
            if not found:
                records.append({'act': act, 'article': article, 'version': version, 'url': url, 'captured_at': _now(),
                                'error': 'the page states no vigency'})
                continue
            d1, m1, y1, d2, m2, y2 = found.groups()
            start = f'{y1}-{int(m1):02d}-{int(d1):02d}'
            end = y2 and f'{y2}-{int(m2):02d}-{int(d2):02d}'
            if end and end < SINCE:
                continue  # not in force since 2020
            record = {'act': act, 'article': article, 'version': version, 'in_force_from': start, 'in_force_to': end,
                      'url': url, 'captured_at': _now(), 'bytes': len(content), 'sha256': put_bytes(store, content)}
            records.append(record)
            print(json.dumps({k: record.get(k) for k in ('act', 'article', 'version', 'in_force_from', 'in_force_to')}),
                  flush=True)
    _write('statutes.json', records)


def register(workers: int):
    store = store_root(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    captured = {'service': SERVICE, 'captured_at': _now(), 'layers': []}
    for layer in (1, 0):
        base = f'{SERVICE}/{layer}'
        description = _get(f'{base}?f=json')
        ids = _get(f'{base}/query?' + urllib.parse.urlencode({'where': '1=1', 'returnIdsOnly': 'true', 'f': 'json'}))
        object_ids = sorted(ids.json()['objectIds'])
        count = _get(f'{base}/query?' + urllib.parse.urlencode({'where': '1=1', 'returnCountOnly': 'true', 'f': 'json'})).json()['count']
        if count != len(object_ids):
            raise ValueError(f'layer {layer}: count {count} differs from its object-id list {len(object_ids)}')
        windows = [object_ids[i:i + 1000] for i in range(0, len(object_ids), 1000)]

        def page(window):
            params = {'where': f'OBJECTID>={window[0]} AND OBJECTID<={window[-1]}', 'outFields': '*',
                      'returnGeometry': 'true', 'orderByFields': 'OBJECTID', 'f': 'json'}
            url = f'{base}/query?' + urllib.parse.urlencode(params)
            response = _get(url)
            features = response.json().get('features', [])
            if len(features) != len(window):
                raise ValueError(f'layer {layer} page {window[0]}..{window[-1]}: {len(features)} of {len(window)} rows')
            return {'url': url, 'first_oid': window[0], 'last_oid': window[-1], 'rows': len(features),
                    'bytes': len(response.content), 'sha256': put_bytes(store, response.content)}

        with ThreadPoolExecutor(workers) as pool:
            pages = list(pool.map(page, windows))
        captured['layers'].append({
            'layer': layer, 'url': base, 'name': description.json().get('name'),
            'description': {'bytes': len(description.content), 'sha256': put_bytes(store, description.content)},
            'object_ids': {'bytes': len(ids.content), 'sha256': put_bytes(store, ids.content)},
            'rows': count, 'pages': pages})
        print(f'layer {layer}: {count} rows in {len(pages)} pages', flush=True)
    captured['finished_at'] = _now()
    (OUT / 'register.json').write_text(json.dumps(captured, ensure_ascii=False, indent=1) + '\n')


def acts(routes: list[tuple[str, str]]):
    store = store_root(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'acts.json'
    records = json.loads(path.read_text()) if path.exists() else []
    for url, purpose in routes:
        record = {'url': url, 'purpose': purpose, 'captured_at': _now()}
        try:
            response = _get(url, attempts=2, timeout=(20, 300))
            record.update(status=response.status_code, final_url=response.url,
                          content_type=response.headers.get('Content-Type'), bytes=len(response.content))
            if not response.content.startswith(b'%PDF'):
                raise ValueError('the route did not return a PDF')
            record['sha256'] = put_bytes(store, response.content)
        except Exception as error:  # the attempt and its cause are kept
            record['error'] = str(error)[:400]
        records.append(record)
        print(json.dumps({k: record.get(k) for k in ('url', 'status', 'bytes', 'sha256', 'error')}), flush=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=1) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    r = sub.add_parser('register')
    r.add_argument('--workers', type=int, default=4)
    a = sub.add_parser('acts')
    a.add_argument('route', nargs='+', help='URL|purpose')
    sub.add_parser('national-list')
    d = sub.add_parser('declarations')
    d.add_argument('--workers', type=int, default=4)
    dd = sub.add_parser('declaration-decrees')
    dd.add_argument('--workers', type=int, default=4)
    sub.add_parser('declaration-search')
    dp = sub.add_parser('declaration-supplements')
    dp.add_argument('--workers', type=int, default=4)
    ds = sub.add_parser('declaration-schede')
    ds.add_argument('--workers', type=int, default=3)
    sub.add_parser('statutes')
    sub.add_parser('proposals')
    sub.add_parser('recognitions')
    ps = sub.add_parser('proposal-search')
    ps.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if args.command == 'register':
        register(args.workers)
    elif args.command == 'national-list':
        national_list()
    elif args.command == 'declarations':
        declarations(args.workers)
    elif args.command == 'declaration-decrees':
        declaration_decrees(args.workers)
    elif args.command == 'declaration-search':
        declaration_search()
    elif args.command == 'declaration-supplements':
        declaration_supplements(args.workers)
    elif args.command == 'declaration-schede':
        declaration_schede(args.workers)
    elif args.command == 'statutes':
        statutes()
    elif args.command == 'proposals':
        proposals()
    elif args.command == 'recognitions':
        recognitions()
    elif args.command == 'proposal-search':
        proposal_search(args.workers)
    else:
        acts([tuple(item.split('|', 1)) if '|' in item else (item, 'list act') for item in args.route])
