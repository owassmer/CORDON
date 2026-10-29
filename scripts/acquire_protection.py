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
G.U.'s yearly archive where the layer's number or date names none. `declaration-schede` adds the PPTR scheda of each
declaration whose layer motivation reaches the field's length; `declaration-search` the G.U. issues since the PPTR
version before the latest, for declarations the layer does not yet print. Run them in that order: `declarations`
rewrites the record. `statutes` captures from Normattiva each version, in force since
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
    ds = sub.add_parser('declaration-schede')
    ds.add_argument('--workers', type=int, default=3)
    sub.add_parser('statutes')
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
    elif args.command == 'declaration-schede':
        declaration_schede(args.workers)
    elif args.command == 'statutes':
        statutes()
    else:
        acts([tuple(item.split('|', 1)) if '|' in item else (item, 'list act') for item in args.route])
