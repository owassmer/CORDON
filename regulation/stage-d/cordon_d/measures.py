"""Whole-measure evidence for existing prescription, position and event consumers."""
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from cordon_c.core import MissingInput
from .document_subscription import read_documents, read_retained
from .evidence import Support
from .events import AdministrativeEvent
from .removal_events import act_id
from .store import blob_path
from .measure_sources import (source_material, material_context, context_matches,
                              table_fields, native_span, selected_association)


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
FIELD_ROLE = _choice('plant_id', 'reference_plant_id', 'municipality', 'cadastral_section',
                     'sheet', 'parcel', 'addressee')
SPAN = _object(line_ref=TEXT, first_word={'type': 'integer', 'minimum': 0},
               end_word={'type': 'integer', 'minimum': 1})
FIELD_FRAGMENT = {'anyOf': [_object(table_ref=TEXT, cell=TEXT), SPAN]}
ASSOCIATION_REF = {'anyOf': [
    _object(table_ref=TEXT, row={'type': 'integer', 'minimum': 1}), {'type': 'null'}]}
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
    target_scopes=_array(_object(table_ref=TEXT,
                        first_row={'type': 'integer', 'minimum': 1},
                        last_row={'type': 'integer', 'minimum': 1},
                        columns=_array(_object(role=FIELD_ROLE, column={'type': 'integer', 'minimum': 1},
                                               fragments=_array(FIELD_FRAGMENT))),
                        direction_ids=_array(TEXT), meaning=TEXT, support=CITATIONS)),
    prose_positions=_array(_object(fields=_array(_object(role=FIELD_ROLE, spans=_array(SPAN))),
                                   direction_ids=_array(TEXT), meaning=TEXT, support=CITATIONS)),
    image_positions=_array(_object(image_ref=TEXT, association_ref=ASSOCIATION_REF,
                         fields=_array(_object(role=FIELD_ROLE, transcription=TEXT)),
                         direction_ids=_array(TEXT), meaning=TEXT, support=CITATIONS)),
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
    material: dict
    association_readings: tuple

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
        def identifies_target(target):
            # A locality mention does not identify a plant or land position. Map
            # labels remain available in targets(), but their interpreted part
            # role does not make them an operative target population.
            for role in ('plant_id', 'parcel'):
                field = target['fields'].get(role)
                if not field or not (field.get('text') or '').strip():
                    continue
                fragments = field.get('fragments', [field])
                for fragment in fragments:
                    source = fragment.get('source')
                    page = fragment.get('page')
                    if target.get('source_position') is not None:
                        source = target['source_position']['source']
                        page = target['source_position']['page']
                    elif target['association'] is not None:
                        source = target['association']['source_sha256']
                        page = target['association']['page']
                    parts = [p for p in self.values['parts'] if p['source'] == source and page in p['pages']]
                    if any(p['role'] in {'map', 'blank-form'} for p in parts):
                        continue
                    if any(p['role'] in {'act', 'target-table'} for p in parts):
                        return True
            return False
        return tuple(t for t in self.targets()
                     if directions.intersection(t['direction_ids']) and identifies_target(t))

    @staticmethod
    def _target(fields, association, scope, occurrence):
        def value(role):
            return fields.get(role, {}).get('text')
        return dict(occurrence=occurrence, fields=fields, association=association,
                    reference=value('plant_id'), municipality=value('municipality'),
                    cadastral_section=value('cadastral_section'), sheet=value('sheet'), parcel=value('parcel'),
                    addressee_text=value('addressee'), position_scope=scope['meaning'],
                    direction_ids=scope['direction_ids'], support=scope['support'])

    def targets(self):
        """Project source-owned values after interpretation selects their scope."""
        targets = {}
        for scope in self.values['target_scopes']:
            columns = {c['role']: c['column'] for c in scope['columns']}
            selected = {c['role']: c.get('fragments', []) for c in scope['columns']}
            for row in range(scope['first_row'], scope['last_row'] + 1):
                fields, association = table_fields(self.material, scope['table_ref'], row, columns, selected)
                native = self.material['tables'][scope['table_ref']]['rows'][row - 1]
                occurrence = native.get('continuation_of', f"{scope['table_ref']}R{row}")
                if occurrence not in targets:
                    targets[occurrence] = self._target(fields, association, scope, occurrence)
                else:
                    target = targets[occurrence]
                    target['direction_ids'] = sorted(set(target['direction_ids']) | set(scope['direction_ids']))
                    target['support'] = [*target['support'], *scope['support']]
                    for role in columns:
                        new = fields[role]
                        prior = target['fields'].get(role)
                        fragments = prior.get('fragments', [prior]) if prior else []
                        for fragment in new.get('fragments', [new]):
                            if not any(f['locator'] == fragment['locator'] for f in fragments):
                                fragments = [*fragments, fragment]
                        target['fields'][role] = {'text': '\n'.join(f['text'] or '' for f in fragments),
                                                  'fragments': fragments}
                    target['addressee_text'] = target['fields'].get('addressee', {}).get('text')
        yield from targets.values()
        for index, position in enumerate(self.values['prose_positions']):
            fields = {}
            for field in position['fields']:
                fragments = [native_span(self.material, span) for span in field['spans']]
                fields[field['role']] = {'text': ' '.join(f['text'] for f in fragments),
                                         'fragments': fragments}
            yield self._target(fields, None, position, f'prose:{index}')
        for index, position in enumerate(self.values['image_positions']):
            image = (self.material['images'] | self.material['pages'])[position['image_ref']]
            association = selected_association(self.material, position.get('association_ref'))
            fields = dict(association['fields']) if association else {}
            for field in position['fields']:
                if field['role'] in fields:
                    raise ValueError('Selected association already supplies this image-position field')
                fields[field['role']] = dict(image, text=field['transcription'],
                                             derivation='model transcription of source image')
            target = self._target(fields, association, position, f"{position['image_ref']}/position:{index}")
            target['source_position'] = image
            yield target

    def associations(self, store):
        """Reuse the accepted report-association owner without another table reader."""
        return self.association_readings

    def target_associations(self, store):
        """Attach the explicitly selected source-native association occurrence.

        Parcel-only target rows need not have a report association. Empty matches
        remain empty; a corrected image position can select a predecessor row only
        through its source-supported relationship, never by matching a field value.
        """
        for target in self.prescribed_targets():
            matches = (target['association'],) if target['association'] is not None else ()
            yield target, matches

    def administrative_events(self):
        """Exact dated facts about this measure; instructions never become events.

        Reported events retain that qualification in their support. Other payloads
        remain source records until their own document relationship is resolved.
        """
        identity = self.identity
        support = _supports(self.values['identity']['support'])[0]
        yield AdministrativeEvent(identity + ':adoption',
                                  'adoption', identity, None, self.adopted, support)
        for event in self.values['events']:
            if (event['kind'] == 'adoption' or event['evidence'] not in {'direct-record', 'reported-event'}
                    or event['document_reference'] != 'this-act' or event['occurred_on'] is None):
                continue
            cites = _supports(event['support'])
            support = Support(cites[0].source, cites[0].selector,
                              event['evidence'] + ': ' + event['scope'] + '; ' + cites[0].reading)
            occurrence = ':'.join((support.source, support.selector, event['kind'], event['recipient'] or ''))
            yield AdministrativeEvent(occurrence,
                                      event['kind'], identity, event['recipient'],
                                      date.fromisoformat(event['occurred_on']), support)


def _validate_reading(reading, sources, store, material):
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
    for target in [*reading['target_scopes'], *reading['prose_positions'], *reading['image_positions']]:
        if not set(target['direction_ids']) <= set(ids):
            raise ValueError('Target refers to an absent direction')
    occupied = set()
    for scope in reading['target_scopes']:
        table = material['tables'][scope['table_ref']]
        if not 1 <= scope['first_row'] <= scope['last_row'] <= len(table['rows']):
            raise ValueError('Selected rows outside their source table')
        roles = [c['role'] for c in scope['columns']]
        if len(roles) != len(set(roles)):
            raise ValueError('A source field has more than one column assignment')
        for row in range(scope['first_row'], scope['last_row'] + 1):
            key = scope['table_ref'], row
            if key in occupied:
                raise ValueError('One source occurrence needs one composed scope')
            occupied.add(key)
            fields, _ = table_fields(material, scope['table_ref'], row,
                                    {c['role']: c['column'] for c in scope['columns']},
                                    {c['role']: c.get('fragments', []) for c in scope['columns']})
            for column in scope['columns']:
                if column.get('fragments'):
                    cited = {(c['source'], c['page']) for c in scope['support']}
                    required = {(f['source'], f['page'])
                                for f in fields[column['role']]['fragments']}
                    if not required <= cited:
                        raise ValueError('Field continuation needs every source page as support')
    for position in [*reading['prose_positions'], *reading['image_positions']]:
        roles = [f['role'] for f in position['fields']]
        if len(roles) != len(set(roles)):
            raise ValueError('A source position assigns the same field more than once')
    for position in reading['prose_positions']:
        for field in position['fields']:
            if not field['spans']:
                raise ValueError('Native fields require a source span')
            for span in field['spans']:
                native_span(material, span)
    for position in reading['image_positions']:
        image = (material['images'] | material['pages'])[position['image_ref']]
        association = selected_association(material, position.get('association_ref'))
        if association and any(f['role'] in association['fields'] for f in position['fields']):
            raise ValueError('Selected association already supplies this image-position field')
        if association:
            cited = {(c['source'], c['page']) for c in position['support']}
            required = {(image['source'], image['page']),
                        (association['source_sha256'], association['page'])}
            if not required <= cited:
                raise ValueError('Association continuity needs both source positions as support')
        if any(t['source'] == image['source'] and t['page'] == image['page']
               for t in material['tables'].values()):
            raise ValueError('Use native table cells rather than retranscribing that page')
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


def read_measure(sources, store, *, execute=False, review_instruction='', timeout=1800,
                 model='gpt-6-astra', effort='medium'):
    """One whole act and its necessary annex context on the allocated Codex worker."""
    sources = tuple(sources)
    material, associations = source_material(sources, store)
    response = read_documents(sources, store, prompt=PROMPT + material_context(material) + '\n' + review_instruction,
                              schema=SCHEMA, model=model, effort=effort,
                              execute=execute, timeout=timeout)
    _validate_reading(response['reading'], response['request']['sources'], store, material)
    return MeasureReading(response, material, associations)


def retained_measure(request_id, store):
    """Consume a named interpretation with its original context, without re-extraction."""
    response = read_retained(request_id, store)
    from jsonschema import Draft202012Validator
    from copy import deepcopy
    # Additive source roles need not invalidate an otherwise compatible reading.
    # The old generated-target contract still cannot satisfy this composition.
    compatible = deepcopy(response['reading'])
    for scope in compatible['target_scopes']:
        for column in scope['columns']:
            # Earlier readings select only the physical row's own field cell.
            column.setdefault('fragments', [])
    for position in compatible['image_positions']:
        # Earlier contracts could not select an association for an image row.
        # Absence means no selection, never an inferred cross-document match.
        position.setdefault('association_ref', None)
    Draft202012Validator(SCHEMA).validate(compatible)
    sources = response['request']['sources']
    material, associations = source_material(sources, store)
    if not context_matches(response['request']['prompt'], material):
        raise ValueError('Retained interpretation source addresses differ from the current source material')
    _validate_reading(response['reading'], sources, store, material)
    return MeasureReading(response, material, associations)
