"""Whole-measure evidence for existing prescription, position and event consumers."""
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from cordon_c.core import MissingInput
from .document_subscription import read_documents
from .evidence import Support
from .events import AdministrativeEvent
from .removal_events import act_id
from .store import blob_path


def _object(**properties):
    return {'type': 'object', 'properties': properties,
            'required': list(properties), 'additionalProperties': False}


def _array(items):
    return {'type': 'array', 'items': items}


def _choice(*values):
    return {'type': 'string', 'enum': list(values)}


TEXT = {'type': 'string'}
OPTIONAL_TEXT = {'type': ['string', 'null']}
CITATION = _object(source=TEXT, page={'type': 'integer', 'minimum': 1},
                   locator=TEXT, quote=TEXT)
CITATIONS = _array(CITATION)
SCHEMA = _object(
    identity=_object(issuer=TEXT, authority=_choice('puglia-osservatorio', 'other', 'unresolved'),
                     number=OPTIONAL_TEXT, adopted=OPTIONAL_TEXT, title=TEXT, support=CITATIONS),
    directions=_array(_object(
        id=TEXT, mode=_choice('ordered-now', 'conditional-order', 'deferred-prescription',
                             'recited-general-requirement', 'exclusion', 'declared-effect'),
        work=_choice('removal', 'treatment', 'destruction', 'supervision', 'communication',
                     'response', 'effectiveness', 'other'),
        scope=TEXT, recipients=TEXT, conditions=TEXT, timing=TEXT,
        authority_references=_array(TEXT), support=CITATIONS)),
    parts=_array(_object(label=TEXT, source=TEXT, pages=_array({'type': 'integer', 'minimum': 1}),
                        role=_choice('act', 'target-table', 'map', 'blank-form',
                                     'completed-record', 'other'),
                        incorporation=TEXT, qualifications=TEXT, support=CITATIONS)),
    targets=_array(_object(reference={'type': 'string', 'description': 'Exact printed target identifier value, without invented prefixes or row labels.'},
                          reference_label={'type': 'string', 'description': 'Exact printed heading identifying that value; not an authored description of the row.'}, annex=TEXT,
                          municipality=OPTIONAL_TEXT, sheet=OPTIONAL_TEXT, parcel=OPTIONAL_TEXT,
                          addressee_text=OPTIONAL_TEXT, position_scope=TEXT,
                          direction_ids=_array(TEXT), support=CITATIONS)),
    references=_array(_object(identity_literal=TEXT,
                             relationship=_choice('incorporates', 'corrects', 'replaces',
                                                  'supplements', 'adopted-geography',
                                                  'laboratory-evidence', 'governing-law', 'other'),
                             affected_payload=TEXT, support=CITATIONS)),
    events=_array(_object(kind=TEXT, document_reference=TEXT, sender=OPTIONAL_TEXT,
                         recipient=OPTIONAL_TEXT,
                         evidence=_choice('direct-record', 'reported-event', 'intended', 'blank-form'),
                         occurred_on=OPTIONAL_TEXT, time_statement=TEXT,
                         scope=TEXT, support=CITATIONS)),
    issues=_array(_object(source=TEXT, page={'type': ['integer', 'null'], 'minimum': 1},
                         aspect=_choice('identity', 'targets', 'scope', 'timing',
                                        'relationships', 'events', 'coverage'),
                         cause=_choice('source-not-stated', 'unreadable', 'not-recovered',
                                       'not-supplied', 'conflict'), detail=TEXT)),
)
PROMPT = (Path(__file__).resolve().parents[1] / 'measure-reading.txt').read_text()


def _supports(citations):
    return tuple(Support(c['source'], f"page:{c['page']}/{c['locator']}", c['quote'])
                 for c in citations)


@dataclass(frozen=True)
class MeasureReading:
    response: dict

    @property
    def values(self):
        return self.response['reading']

    @property
    def identity(self):
        identity = self.values['identity']
        if identity['authority'] != 'puglia-osservatorio' or not identity['number']:
            raise MissingInput('Resolved issuing authority and adopted act number')
        return act_id(identity['number'], self.adopted.year)

    @property
    def adopted(self):
        value = self.values['identity']['adopted']
        if value is None:
            raise MissingInput('Source adoption date, distinct from publication')
        return date.fromisoformat(value)

    def prescribed_targets(self):
        """Listed targets of present removal directions, not A–C's required population."""
        directions = {d['id'] for d in self.values['directions']
                      if d['mode'] == 'ordered-now' and d['work'] == 'removal'}
        return tuple(t for t in self.values['targets'] if directions.intersection(t['direction_ids']))

    def associations(self, store):
        """Reuse the accepted report-association owner without another table reader."""
        from .source_associations import read_associations
        return tuple(read_associations(h, store) for h in self.response['request']['sources'])

    def target_associations(self, store):
        """Attach source-native sample references at their actual cited pages.

        Parcel-only target rows need not have a report association. Empty matches
        remain empty; neither a name nor a nearby location supplies a report join.
        """
        rows = [row for reading in self.associations(store) for row in reading.rows]
        for target in self.prescribed_targets():
            locations = {(c['source'], c['page']) for c in target['support']}
            label = ''.join(target['reference_label'].split()).casefold()
            matches = tuple(row for row in rows
                            if (row['source_sha256'], row['page']) in locations
                            and label == ''.join(row['basis']['headers'].get('plant_id', {})
                                                 .get('text', '').split()).casefold()
                            and row['fields'].get('plant_id', {}).get('text') == target['reference'])
            yield target, matches

    def administrative_events(self):
        """Exact dated facts about this measure; instructions never become events.

        Reported events retain that qualification in their support. Other payloads
        remain source records until their own document relationship is resolved.
        """
        identity = self.identity
        support = _supports(self.values['identity']['support'])[0]
        yield AdministrativeEvent(self.response['request_sha256'] + ':adoption',
                                  'adoption', identity, None, self.adopted, support)
        for index, event in enumerate(self.values['events']):
            if (event['evidence'] not in {'direct-record', 'reported-event'}
                    or event['document_reference'] != 'this-act' or event['occurred_on'] is None):
                continue
            cites = _supports(event['support'])
            support = Support(cites[0].source, cites[0].selector,
                              event['evidence'] + ': ' + event['scope'] + '; ' + cites[0].reading)
            yield AdministrativeEvent(self.response['request_sha256'] + f':event:{index}',
                                      event['kind'], identity, event['recipient'],
                                      date.fromisoformat(event['occurred_on']), support)


def _validate_reading(reading, sources, store):
    """Check source bindings and internal references; this does not certify meaning."""
    import pymupdf
    counts = {}
    for digest in sources:
        with pymupdf.open(blob_path(store, digest)) as document:
            counts[digest] = len(document)

    def page(source, number):
        if source not in counts or not 1 <= number <= counts[source]:
            raise ValueError('Reading cites an unsupplied source page')

    def visit(value):
        if isinstance(value, dict):
            if set(value) == {'source', 'page', 'locator', 'quote'}:
                page(value['source'], value['page'])
                if not value['quote'].strip() or not value['locator'].strip():
                    raise ValueError('Evidence needs a quotation and exact source locator')
            for key, item in value.items():
                if key == 'support' and not item:
                    raise ValueError('A source claim needs source support')
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)
    visit(reading)
    ids = [d['id'] for d in reading['directions']]
    if any(not x for x in ids) or len(ids) != len(set(ids)):
        raise ValueError('Direction references must be distinct within this reading')
    for target in reading['targets']:
        if not set(target['direction_ids']) <= set(ids):
            raise ValueError('Target refers to an absent direction')
    for part in reading['parts']:
        for number in part['pages']:
            page(part['source'], number)
    for issue in reading['issues']:
        if issue['source'] not in counts:
            raise ValueError('A reading limitation must identify a supplied source')
        if issue['page'] is not None:
            page(issue['source'], issue['page'])
    for value in [reading['identity']['adopted'], *(e['occurred_on'] for e in reading['events'])]:
        if value is not None:
            date.fromisoformat(value)


def read_measure(sources, store, *, execute=False, review_instruction='', timeout=1800):
    """One whole act and its necessary annex context on the allocated Codex worker."""
    response = read_documents(sources, store, prompt=PROMPT + '\n' + review_instruction,
                              schema=SCHEMA, model='gpt-5.6-luna', effort='high',
                              execute=execute, timeout=timeout)
    _validate_reading(response['reading'], response['request']['sources'], store)
    return MeasureReading(response)
