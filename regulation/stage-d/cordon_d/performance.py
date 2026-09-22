"""Source-scoped performance reports, without invented case or target attachment."""
from dataclasses import dataclass
from datetime import date
from hashlib import sha256
from pathlib import Path

from bs4 import BeautifulSoup

from .document_subscription import read_documents, read_retained
from .evidence import Support
from .store import blob_path


def _object(**properties):
    return dict(type='object', properties=properties, required=list(properties),
                additionalProperties=False)


def _array(items):
    return dict(type='array', items=items)


TEXT = {'type': 'string'}
OPTIONAL_TEXT = {'type': ['string', 'null']}
CAUSE = {'type': ['string', 'null'], 'enum': [None, 'source-not-stated', 'unreadable',
                                           'not-recovered', 'not-supplied', 'conflict']}
CITATION = _object(source=TEXT, locator=TEXT, quote=TEXT)
CITATIONS = _array(CITATION)
VALUE = _object(value=OPTIONAL_TEXT, cause=CAUSE)
DAY = _object(value=OPTIONAL_TEXT, cause=CAUSE, support=CITATIONS)
ISSUES = _array(_object(aspect=TEXT, cause=dict(CAUSE, type='string',
                       enum=CAUSE['enum'][1:]), detail=TEXT))
SCHEMA = _object(
    documents=_array(_object(source=TEXT, issuer=TEXT, title=TEXT,
                            published_on=DAY, support=CITATIONS)),
    statements=_array(_object(source=TEXT,
        operation={'type': 'string', 'enum': ['removal', 'treatment', 'destruction',
                                            'verification', 'other']},
        evidence={'type': 'string', 'enum': ['direct-record', 'reported-event', 'intended']},
        scope_literal=TEXT, performer=VALUE, reported_by=VALUE, occurred_on=DAY,
        time_statement=TEXT, support=CITATIONS, issues=ISSUES)),
    issues=ISSUES,
)
PROMPT = (Path(__file__).resolve().parents[1] / 'performance-reading.txt').read_text()


def _validate(response, store):
    """Check supplied native citations and distinctions, not their semantic truth."""
    request, reading = response['request'], response['reading']
    sources = request['sources']
    if request.get('source_formats') != {source: 'text/html' for source in sources}:
        raise ValueError('Performance report reading requires explicit native HTML sources')
    documents = {row['source']: row for row in reading['documents']}
    if set(documents) != set(sources) or len(documents) != len(reading['documents']):
        raise ValueError('Identify each supplied source document exactly once')
    native = {}
    for source in sources:
        raw = blob_path(store, source).read_bytes()
        if sha256(raw).hexdigest() != source:
            raise ValueError('Source bytes do not match their hash')
        native[source] = BeautifulSoup(raw.decode('utf-8'), 'html.parser')

    def citation(item, source):
        if item['source'] != source or not item['locator'].strip() or not item['quote'].strip():
            raise ValueError('Citation needs its own supplied source, native locator and quotation')
        try:
            matches = native[source].select(item['locator'])
        except Exception as error:
            raise ValueError('Citation locator is not a native CSS selector') from error
        if len(matches) != 1:
            raise ValueError('Citation must locate exactly one native source element')
        element = matches[0]
        if any(parent.name in {'script', 'style', 'template'}
               for parent in (element, *element.parents)):
            raise ValueError('Executable or template text is not visible report evidence')
        visible = ' '.join(element.get_text(' ', strip=True).split())
        if ' '.join(item['quote'].split()) not in visible:
            raise ValueError('Quotation is not contiguous text in its source element')

    def supports(items, source):
        if not items:
            raise ValueError('A source claim requires support')
        for item in items:
            citation(item, source)

    def value(item):
        if item['value'] is None:
            if item['cause'] is None:
                raise ValueError('An unrecovered value must retain its absence cause')
        elif not item['value'].strip() or item['cause'] is not None:
            raise ValueError('A recovered value and an absence cause cannot substitute for each other')

    def day(item, source):
        value(item)
        if item['value'] is None:
            if item['support']:
                raise ValueError('An unknown exact day cannot carry exact-day support')
        else:
            parsed = date.fromisoformat(item['value'])
            if parsed.isoformat() != item['value']:
                raise ValueError('Preserve a source-supported ISO calendar day')
            supports(item['support'], source)

    for source, document in documents.items():
        if not document['issuer'].strip() or not document['title'].strip():
            raise ValueError('Preserve the source document issuer and title')
        supports(document['support'], source)
        day(document['published_on'], source)
    for statement in reading['statements']:
        source = statement['source']
        if source not in documents:
            raise ValueError('Statement belongs to an unsupplied source')
        if not statement['scope_literal'].strip() or not statement['time_statement'].strip():
            raise ValueError('Preserve the stated performance scope and timing')
        supports(statement['support'], source)
        value(statement['performer'])
        value(statement['reported_by'])
        day(statement['occurred_on'], source)
        publication = documents[source]['published_on']
        operation = statement['occurred_on']
        if (operation['value'] is not None and operation['value'] == publication['value']
                and all(c in publication['support'] for c in operation['support'])):
            raise ValueError('Publication-day support alone cannot establish the operation day')
    for issue in [*reading['issues'], *(issue for s in reading['statements'] for issue in s['issues'])]:
        if not issue['aspect'].strip() or not issue['detail'].strip():
            raise ValueError('An issue must identify its affected meaning and cause')


@dataclass(frozen=True)
class PerformanceReading:
    response: dict

    @property
    def values(self):
        return self.response['reading']

    def removal_occurrences(self):
        """Actual reported/direct removal in its literal scope, not adjudicated completion."""
        for index, statement in enumerate(self.values['statements']):
            if (statement['operation'] != 'removal'
                    or statement['evidence'] not in {'direct-record', 'reported-event'}):
                continue
            yield dict(statement=statement, occurrence=f'{self.response["request_sha256"]}:{index}',
                       support=tuple(Support(c['source'], c['locator'], c['quote'])
                                     for c in statement['support']),
                       provenance='model_proposed_reading',
                       request_sha256=self.response['request_sha256'],
                       attachment_limit='Source-stated scope; no prescribed-target correspondence established')


def read_performance(digests, store, *, execute=False, **options):
    """Read complete retained HTML reports with the subscription transport."""
    digests, store = tuple(digests), Path(store)
    response = read_documents(digests, store, prompt=PROMPT, schema=SCHEMA,
                              source_formats={source: 'text/html' for source in digests},
                              execute=execute, **options)
    _validate(response, store)
    return PerformanceReading(response)


def retained_performance(request_id, store):
    """Replay this reader's retained proposal without another provider call."""
    store = Path(store)
    response = read_retained(request_id, store)
    if response['request']['schema'] != SCHEMA:
        raise ValueError('Retained response uses another source-reading contract')
    _validate(response, store)
    return PerformanceReading(response)
