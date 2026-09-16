"""Read native publication inputs and separately select interpreted evidence."""
from datetime import date, datetime
from pathlib import Path







def publication_declarations(path: Path, *, publisher: str, encoding: str = 'utf-8'):
    """Read the native annual CSV declarations without case registration.

    Displayed publication dates are register declarations, not certificates of
    continuity or recipient delivery. Retain all original columns and records.
    """
    from .releases import Occurrence, csv_occurrences
    if not publisher or not publisher.strip():
        raise ValueError('A native export needs its source publisher scope')
    required = {'Tipo', 'numero atto', 'Data atto', 'Oggetto',
                'Inizio pubblicazione', 'Fine pubblicazione'}
    for row in csv_occurrences(path, encoding=encoding, delimiter=','):
        if not required <= row.values.keys():
            raise ValueError('Annual publication export lacks its native columns')
        dates = {}
        issues = {}
        for field in ('Data atto', 'Inizio pubblicazione', 'Fine pubblicazione'):
            value = row.values[field]
            parsed = _register_date(value)
            dates[field] = parsed.isoformat() if parsed else None
            if value and parsed is None:
                issues[field] = 'Unrecognized source date; original value retained'
        yield Occurrence(row.path, row.sha256, row.locator, {
            'publisher': publisher, 'source_fields': row.values, 'declared_dates': dates,
            'date_issues': issues,
        })


def _register_date(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.strptime(value, '%d/%m/%Y').date()
        return parsed if parsed.strftime('%d/%m/%Y') == value else None
    except ValueError:
        return None


def publication_detail(path: Path, *, publisher: str, source_url: str):
    """Read a retained SoluzioneIPA detail page and its emitted document routes.

    A document link is a route, not proof that its content was acquired. Source
    protocol, register and act references stay separate. Unknown fields survive.
    """
    import re
    from urllib.parse import urljoin
    from bs4 import BeautifulSoup
    from .evidence import file_digest
    from .releases import Occurrence
    if not publisher or not publisher.strip():
        raise ValueError('A detail page needs its source publisher scope')
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    headings = soup.select('.card-title h3')
    if len(headings) != 1:
        raise ValueError('Expected one native publication-detail title')
    fields = {}
    for label in soup.find_all('label'):
        if 'visually-hidden' in label.get('class', []):
            continue
        parent = label.parent
        values = [item.get_text(' ', strip=True) for item in
                  parent.find_all('div', recursive=False)]
        if not values:
            continue
        key = label.get_text(' ', strip=True)
        if key in fields:
            raise ValueError('Repeated native detail field requires interpretation')
        fields[key] = ' '.join(values)
    for key in ('Pubblicazione nr.', 'Atto', 'Data affissione', 'Data scadenza'):
        if key not in fields:
            raise ValueError('Publication detail lacks ' + key)
    end = re.fullmatch(r'(\d{2}/\d{2}/\d{4})(?:\s*-\s*\(\d+\)\s*giorni)?', fields['Data scadenza'])
    act = re.fullmatch(r'(.+?)(?: - n\. (.+?))? del (\d{2}/\d{2}/\d{4})', fields['Atto'])
    dates = {'Data atto': _register_date(act.group(3)) if act else None,
             'Inizio pubblicazione': _register_date(fields['Data affissione']),
             'Fine pubblicazione': _register_date(end.group(1)) if end else None}
    links = []
    for index, a in enumerate(soup.find_all('a', href=True)):
        if 'getDoc.php?' in a['href']:
            links.append({'locator': f'a[{index}]', 'label': a.get_text(' ', strip=True),
                          'href': a['href'], 'url': urljoin(source_url, a['href']),
                          'information_link': '&info' in a['href']})
    return Occurrence(str(path), file_digest(path), 'publication-detail', {
        'publisher': publisher, 'source_url': source_url, 'subject': headings[0].get_text(' ', strip=True),
        'source_fields': fields,
        'act_type': act.group(1) if act else None,
        'act_number': act.group(2) if act else None,
        'declared_dates': {k: v.isoformat() if v else None for k, v in dates.items()},
        'document_routes': links,
    })


def declaration_detail_matches(declaration, details):
    """Return all exact declared-tuple candidates within a caller's issuer scope.

    The CSV has no publication ID. Agreement is a source-reference candidate,
    not permission, recipient effect, or a unique global instrument identity.
    Missing dates cannot match each other as if they supplied evidence.
    """
    from html import unescape
    def normalized(value):
        return ' '.join(unescape(value or '').split())
    values = declaration.values
    raw = values['source_fields']
    dates = values['declared_dates']
    if not all(dates.values()):
        return ()
    return tuple(detail for detail in details
                 if detail.values['publisher'] == values['publisher']
                 and detail.values['declared_dates'] == dates
                 and normalized(detail.values['subject']) == normalized(raw['Oggetto'])
                 and normalized(detail.values['act_type']) == normalized(raw['Tipo'])
                 and normalized(detail.values['act_number']) == normalized(raw['numero atto']))


def read_publications(annual_paths, detail_sources, *, publisher: str):
    """Ordinary native-source path; emit every record, including unmatched ones.

    detail_sources contains (retained_path, original_url) pairs, not authored
    conclusions. Callers supply a coherent publisher scope. No case repository
    or list of supported act identities is consulted.
    """
    from dataclasses import asdict
    from .releases import Occurrence
    details = tuple(publication_detail(path, publisher=publisher, source_url=url)
                    for path, url in detail_sources)
    for path in annual_paths:
        for row in publication_declarations(path, publisher=publisher):
            matches = declaration_detail_matches(row, details)
            yield Occurrence(row.path, row.sha256, row.locator, {
                **row.values,
                'detail_candidates': [asdict(detail) for detail in matches],
            })


def parsec_publication_declarations(path: Path, *, publisher: str, source_url: str):
    """Read native Parsec rows, including a retained ICEfaces table response.

    Register number, requesting office, subject and attachment routes remain
    source fields. Neither a referenced act nor a PEC subject identifies the
    attached document's legal effect or proves recipient delivery.
    """
    import re
    from urllib.parse import urljoin
    from xml.etree import ElementTree
    from bs4 import BeautifulSoup
    from .evidence import file_digest
    from .releases import Occurrence

    if not publisher.strip() or not source_url:
        raise ValueError('Publication declarations need their publisher and source URL')
    path = Path(path)
    content = path.read_bytes()
    if content.lstrip().startswith(b'<partial-response>'):
        updates = [e for e in ElementTree.fromstring(content).findall('.//update')
                   if e.get('id', '').endswith(':elencoPubblicazioni')]
        if len(updates) != 1:
            raise ValueError('Expected the native publication table update')
        content = updates[0].text or ''
    soup = BeautifulSoup(content, 'html.parser')
    tables = soup.select('div[id$=":elencoPubblicazioni"] > div > table')
    if len(tables) != 1:
        raise ValueError('Expected one native Parsec publication table')
    table = tables[0]
    headers = [e.get_text(' ', strip=True) for e in table.select('thead > tr > th')]
    required = {'Nro', 'Tipo atto', 'Oggetto', 'Richiedente',
                'Data inizio pubb.', 'Data fine pubb.'}
    named = [h for h in headers if h]
    if not required <= set(named) or len(named) != len(set(named)):
        raise ValueError('Unrecognized native publication columns')
    digest = file_digest(path)
    for index, row in enumerate(table.select('tbody > tr')):
        cells = row.find_all('td', recursive=False)
        if len(cells) != len(headers):
            raise ValueError('Publication row does not match its source columns')
        fields = {h: c.get_text(' ', strip=True) for h, c in zip(headers, cells) if h}
        routes = []
        for a in row.find_all('a', onclick=True):
            # The publisher emits a literal repository URL in window.open.
            # Copy that route; do not execute JavaScript or classify its text.
            match = re.search(r"(/repo/docs/[^\s'\"\\]+)", a['onclick'])
            if match:
                routes.append({'url': urljoin(source_url, match.group(1)),
                               'label': a.img.get('title', '') if a.img else ''})
        dates = {key: _register_date(fields[key]) for key in
                 ('Data inizio pubb.', 'Data fine pubb.')}
        yield Occurrence(str(path), digest, f'publication-table/row[{index}]', {
            'publisher': publisher, 'source_url': source_url,
            'source_fields': fields,
            'declared_dates': {k: v.isoformat() if v else None for k, v in dates.items()},
            'date_issues': {k: 'Unrecognized source date; original value retained'
                            for k, v in dates.items() if fields[k] and v is None},
            'document_routes': routes,
        })
