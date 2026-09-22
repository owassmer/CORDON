"""Whole-measure evidence for existing prescription, position and event consumers."""
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from copy import deepcopy
from decimal import Decimal, InvalidOperation
import json

from cordon_c.core import MissingInput
from .document_subscription import read_documents, read_retained
from .evidence import Support
from .events import AdministrativeEvent
from .removal_events import act_id
from .store import blob_path
from .measure_sources import (source_material, material_context, context_matches,
                              table_fields, native_span, field_fragment,
                              selected_association, native_text_issue,
                              span_overlaps, association_areas)
from .source_associations import HEADINGS


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
FIELD_ROLE = _choice(*sorted(set(HEADINGS.values()) |
                            {'reference_plant_id', 'cadastral_section', 'addressee'}))
SPAN = _object(line_ref=TEXT, first_word={'type': 'integer', 'minimum': 0},
               end_word={'type': 'integer', 'minimum': 1})
FIELD_FRAGMENT = {'anyOf': [_object(table_ref=TEXT, cell=TEXT), SPAN,
                            _object(table_ref=TEXT, cell=TEXT, transcription=TEXT)]}
HOST_POPULATION = {'anyOf': [{'type': 'null'}, _object(
    scope=_choice('whole-report', 'selected-occurrences', 'unresolved'),
    host_fragments=_array(FIELD_FRAGMENT), support=CITATIONS)]}
ASSOCIATION_REF = {'anyOf': [
    _object(table_ref=TEXT, row={'type': 'integer', 'minimum': 1}), {'type': 'null'}]}
COMMENCEMENT_COMPONENTS = {'anyOf': [
    {'type': 'null'}, _array(_object(
        trigger=_choice('noncommencement', 'other', 'unresolved'),
        performance=_choice('concrete-commencement', 'completion', 'other', 'unresolved'),
        required_actor=OPTIONAL_TEXT, commencement_work=OPTIONAL_TEXT,
        commencement_direction_ids=_array(TEXT),
        period={'anyOf': [{'type': 'null'}, _object(
            magnitude=OPTIONAL_TEXT,
            unit=_choice('days', 'working-days', 'months', 'years', 'hours', 'other', 'unresolved'),
            bound=_choice('within-maximum', 'other', 'unresolved'),
            literal=TEXT, anchor=_choice('notification', 'other', 'unresolved'),
            anchor_statement=TEXT)]},
        commitment=_choice('will-direct', 'may-direct', 'other', 'unresolved'),
        support=CITATIONS))]}
ISSUES = _array(_object(source=TEXT, page={'type': ['integer', 'null'], 'minimum': 1},
                       aspect=_choice('identity', 'targets', 'scope', 'timing',
                                      'relationships', 'events', 'coverage'),
                       cause=_choice('source-not-stated', 'unreadable', 'not-recovered',
                                     'not-supplied', 'conflict'), detail=TEXT))
SCHEMA = _object(
    identity=_object(issuer=TEXT, authority=_choice('puglia-osservatorio', 'other', 'unresolved'),
                     number=OPTIONAL_TEXT, adopted=OPTIONAL_TEXT, title=TEXT, support=CITATIONS),
    directions=_array(_object(
        id=TEXT, mode=_choice('ordered-now', 'conditional-order', 'deferred-prescription',
                             'recited-general-requirement', 'exclusion', 'declared-effect'),
        work=_choice('removal', 'treatment', 'destruction', 'supervision', 'communication',
                     'response', 'effectiveness', 'other'),
        scope=TEXT, recipients=TEXT, conditions=TEXT, timing=TEXT,
        authority_references=_array(TEXT), support=CITATIONS,
        commencement_components=COMMENCEMENT_COMPONENTS)),
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
                             affected_payload=TEXT, support=CITATIONS,
                             documents=_array(_object(source=TEXT, support=CITATIONS,
                                                      host_population=HOST_POPULATION)),
                             acts=_array(_object(
                                 issuer=OPTIONAL_TEXT,
                                 authority=_choice('puglia-osservatorio', 'other', 'unresolved'),
                                 number=OPTIONAL_TEXT,
                                 year={'type': ['string', 'null'], 'pattern': '^[0-9]{4}$'},
                                 adopted=OPTIONAL_TEXT, support=CITATIONS)))),
    events=_array(_object(kind=TEXT, document_reference=TEXT, sender=OPTIONAL_TEXT,
                         recipient=OPTIONAL_TEXT,
                         evidence=_choice('direct-record', 'reported-event', 'intended', 'blank-form'),
                         occurred_on=OPTIONAL_TEXT, time_statement=TEXT,
                         scope=TEXT, support=CITATIONS)),
    issues=ISSUES,
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
    component_responses: tuple = ()

    @property
    def values(self):
        return self.response['reading']

    def commencement_components(self, direction_id):
        """Source components only; their presence does not qualify an A form.

        Explicit follow-ups supply only the selected component projection. The
        original direction, scope, targets and response remain unchanged.
        """
        directions = [d for d in self.values['directions'] if d['id'] == direction_id]
        if len(directions) != 1:
            raise ValueError('Select one existing direction from this reading')
        direction = directions[0]
        readings = tuple(
            dict(request_sha256=response['request_sha256'],
                 components=entry['commencement_components'],
                 issues=tuple(response['reading']['issues']))
            for response in self.component_responses
            for entry in response['reading']['directions'] if entry['id'] == direction_id)
        if readings and direction.get('commencement_components') is not None:
            # A selected supplement does not supersede an already stated base
            # reading, including an explicit source absence. An unread base can
            # gain recovered components without manufacturing a contradiction.
            readings = (dict(request_sha256=self.response['request_sha256'],
                             components=direction['commencement_components'],
                             issues=tuple(self.values['issues'])), *readings)
        if not readings:
            if 'commencement_components' not in direction:
                return dict(direction=direction, components=None,
                            cause='not-recovered: retained contract did not request structured commencement components',
                            readings=(), issues=tuple(self.values['issues']))
            readings = (dict(request_sha256=self.response['request_sha256'],
                             components=direction['commencement_components'],
                             issues=tuple(self.values['issues'])),)
        values = [reading['components'] for reading in readings]
        issues = tuple(issue for reading in readings for issue in reading['issues'])
        if any(value != values[0] for value in values[1:]):
            return dict(direction=direction, components=None,
                        cause='conflict: explicitly selected component readings disagree',
                        readings=readings, issues=issues)
        return dict(direction=direction,
                    components=tuple(values[0]) if values[0] is not None else None,
                    cause=None if values[0] is not None else
                    'unresolved: structured commencement reading; see source-scoped issues',
                    readings=readings, issues=issues)

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
            text = fields.get(role, {}).get('text')
            return text if native_text_issue(text) is None else None
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
                    issue = self.material['tables'][scope['table_ref']].get('native_field_issue')
                    missing_columns = set(range(1, len(native['cells']) + 1)) - set(columns.values())
                    if association is None and 'plant_id' in fields and issue and missing_columns:
                        targets[occurrence]['native_field_issue'] = issue
                    unavailable = []
                    for field in fields.values():
                        for fragment in field.get('fragments', [field]):
                            issue = native_text_issue(fragment.get('text'))
                            if fragment.get('text') is None:
                                issue = fragment.get('native_text_issue', issue)
                            if issue:
                                unavailable.append(issue)
                    if unavailable:
                        targets[occurrence]['native_field_issue'] = '; '.join(dict.fromkeys(unavailable))
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

    def report_population(self, report_readings):
        """Resolve native row references and supplied selections through their owners."""
        from .findings import _associations
        from .report_relations import correspondences, replacements, current_limitation, number, dated
        report_readings = tuple(report_readings)
        readings = {r.sha256: r for r in report_readings}
        if len(readings) != len(report_readings):
            raise ValueError('Supply one ordinary report reading per source')
        edges = correspondences(readings)
        population = {}
        targets = tuple(self.prescribed_targets())

        def bind(source, support, occurrences, *, reference_cause=None):
            for digest, chain in replacements(edges, source).items():
                reading = readings.get(digest)
                relations = getattr(reading, 'relations', None)
                identity = relations.get('identity') if relations else None
                cause = current_limitation(edges, digest)
                if reading is None:
                    cause = 'selected report has no supplied ordinary reading'
                elif not relations or relations.get('reading_complete') is not True:
                    cause = 'selected report identity and relationship reading is incomplete'
                elif not identity.get('issuer') or not identity.get('number'):
                    cause = 'selected report lacks a source-supported issuer or report identity'
                binding = population.setdefault(digest, dict(
                    references=[], target_occurrences=(), report_identity=identity,
                    relationship_reading=relations,
                    reading_issues=getattr(reading, 'issues', ()), cause=cause,
                    request_sha256=self.response.get('request_sha256'),
                    provenance='model_proposed_reading'))
                if reference_cause is None:
                    binding['target_occurrences'] = tuple(dict.fromkeys(
                        (*binding['target_occurrences'], *occurrences)))
                binding['references'].append(dict(support, target_occurrences=occurrences,
                                                  replacement_chain=chain, cause=reference_cause))

        for target in targets:
            association = target['association']
            if association is None:
                continue
            for digest, reading in readings.items():
                if _associations(reading, [association]):
                    bind(digest, dict(association=association), (target['occurrence'],))

        unbound = tuple(target['occurrence'] for target in targets
                        if target['association'] is None)
        selections = []
        for reference in self.values['references']:
            if reference['relationship'] != 'laboratory-evidence':
                continue
            for selected in reference.get('documents', []):
                bind(selected['source'], dict(reference=reference, selection=selected), unbound)
                selections.append((reference, selected))

        for target in targets:
            association = target['association']
            if association is None:
                continue
            fields = association['fields']
            literal = fields.get('report_reference', {}).get('text')
            day = dated(''.join((fields.get('report_date', {}).get('text') or '').split()))
            if not literal or day is None:
                continue
            candidates = []
            for reference, selected in selections:
                reading = readings.get(selected['source'])
                relations = getattr(reading, 'relations', None)
                identity = relations.get('identity') if relations else None
                # The selection supplies document context; the complete native
                # reference and its own date still constrain this particular row.
                if (identity and dated(identity.get('date')) == day
                        and number(literal, {'date': day.isoformat()})
                        == number(identity.get('number'), identity)):
                    candidates.append((reference, selected))
            cause = ('native report reference matches several explicitly selected documents'
                     if len({selected['source'] for _, selected in candidates}) > 1 else None)
            for reference, selected in candidates:
                bind(selected['source'], dict(association=association, reference=reference,
                     selection=selected), (target['occurrence'],), reference_cause=cause)
        for digest, binding in population.items():
            claims = []
            for reference, selected in selections:
                claim = selected.get('host_population')
                # A whole-report replacement does not establish an unchanged host
                # population. Keep the original selection without extending its claim.
                if selected['source'] != digest or claim is None:
                    continue
                fragments = [field_fragment(self.material, f) for f in claim['host_fragments']]
                claims.append(dict(claim=claim, reference=reference, selection=selected,
                    host=dict(text=(' '.join(f['text'] for f in fragments)
                                    if fragments and all(f.get('text') and
                                        native_text_issue(f['text']) is None for f in fragments) else None),
                              fragments=fragments)))
            if claims:
                binding['host_populations'] = tuple(claims)
                binding['targets'] = tuple(t for t in targets
                    if t['occurrence'] in binding['target_occurrences'])
                def position_pages(target):
                    fields = [f for field in target['fields'].values()
                              for f in field.get('fragments', [field])]
                    located = {(f['source'], f['page']) for f in fields
                               if 'source' in f and 'page' in f}
                    if target.get('source_position'):
                        position = target['source_position']
                        located.add((position['source'], position['page']))
                    if target.get('association'):
                        association = target['association']
                        located.add((association['source_sha256'], association['page']))
                    return located or {(c['source'], c['page']) for c in target.get('support', ())}
                reached_pages = {(c['source'], c['page']) for claim in claims
                                 for c in claim['claim']['support']}
                reached_pages.update(p for t in binding['targets'] for p in position_pages(t))
                other_occurrences = {o for source, other in population.items() if source != digest
                                     and not other.get('cause') for o in other['target_occurrences']}
                other_pages = {p for t in targets if t['occurrence'] in other_occurrences
                               and t['occurrence'] not in binding['target_occurrences']
                               for p in position_pages(t)} - reached_pages
                reached_sources = {source for source, _ in reached_pages} | {digest}
                binding['measure_population_issues'] = tuple(i for i in self.values.get('issues', ())
                    if i['aspect'] in {'targets', 'coverage'} and i['source'] in reached_sources
                    and (i['source'] == digest or i['page'] is None
                         or (i['source'], i['page']) not in other_pages))
        return population

    def finding_links(self, joined, report_readings):
        """Connect prescribed positions to the existing ordinary finding results."""
        from .findings import report_rows
        from .measure_findings import measure_findings
        joined, report_readings = tuple(joined), tuple(report_readings)
        return measure_findings(self, report_population=self.report_population(report_readings),
                                findings=joined, report_rows=tuple(report_rows(report_readings, joined)))

    def referenced_measures(self, readings):
        """Correspond source references to existing readings without applying their scope."""
        from .measure_references import referenced_measures
        return referenced_measures(self, readings)

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


def _validate_direction_components(direction, ids, issues):
    if 'commencement_components' not in direction:
        return
    components = direction['commencement_components']

    def needs_issue(support, *, unresolved=False):
        pages = {(c['source'], c['page']) for c in support}
        causes = {'unreadable', 'not-recovered', 'not-supplied', 'conflict'}
        if not unresolved:
            causes.add('source-not-stated')
        if not any(i['aspect'] in {'scope', 'timing', 'relationships', 'coverage'}
                   and i['cause'] in causes and i['detail'].strip()
                   and any(i['source'] == source and i['page'] in {None, number}
                           for source, number in pages) for i in issues):
            raise ValueError('Unavailable commencement component needs its source-scoped cause')

    if components is None:
        needs_issue(direction['support'], unresolved=True)
        return
    for component in components:
        selected = component['commencement_direction_ids']
        if len(selected) != len(set(selected)) or not set(selected) <= set(ids):
            raise ValueError('Commencement work refers to an absent or repeated direction')
        missing = any(component[field] is None for field in ('required_actor', 'commencement_work'))
        for field in ('required_actor', 'commencement_work'):
            if component[field] is not None and not component[field].strip():
                raise ValueError('A recovered commencement statement cannot be blank')
        missing |= any(component[field] == 'unresolved' for field in ('trigger', 'performance', 'commitment'))
        period = component['period']
        if period is None:
            missing = True
        else:
            if not period['literal'].strip() or not period['anchor_statement'].strip():
                raise ValueError('A period needs its literal source term and anchor statement')
            magnitude = period['magnitude']
            if magnitude is not None:
                try:
                    finite = Decimal(magnitude).is_finite()
                except InvalidOperation:
                    finite = False
                if not finite:
                    raise ValueError('A recovered period magnitude must be a finite source number')
            missing |= (magnitude is None or period['unit'] == 'unresolved'
                        or period['anchor'] == 'unresolved' or period['bound'] == 'unresolved')
        if missing:
            needs_issue(component['support'])


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

    def visit(value, selected_blank_pages=()):
        if isinstance(value, dict):
            if set(value) == {'source', 'page', 'locator', 'quote'}:
                page(value['source'], value['page'])
                if (not value['locator'].strip() or
                        (not value['quote'].strip() and
                         (value['source'], value['page']) not in selected_blank_pages)):
                    raise ValueError('Evidence needs a quotation and exact source locator')
            for key, item in value.items():
                if key == 'support' and not item:
                    raise ValueError('A source claim needs source support')
                if key == 'target_scopes':
                    for scope in item:
                        blank_pages = set()
                        for column in scope['columns']:
                            for fragment in column.get('fragments', []):
                                if 'table_ref' not in fragment:
                                    continue
                                table = material['tables'][fragment['table_ref']]
                                text = table['cells'][fragment['cell']]['text']
                                # A selected blank cell can evidence continuation;
                                # unavailable text cannot. Composition is checked below.
                                if isinstance(text, str) and not text.strip():
                                    blank_pages.add((table['source'], table['page']))
                        visit(scope, blank_pages)
                else:
                    visit(item, selected_blank_pages if key == 'support' else ())
        elif isinstance(value, list):
            for item in value:
                visit(item, selected_blank_pages)
    visit(reading)
    for reference in reading.get('references', []):
        selected_sources = set()
        citing_sources = {c['source'] for c in reference['support']}
        for act in reference.get('acts', []):
            if not ({c['source'] for c in act['support']} & citing_sources):
                raise ValueError('Referenced act identity needs support from its citing source')
            if act['adopted'] is not None:
                date.fromisoformat(act['adopted'])
        for selected in reference.get('documents', []):
            source = selected['source']
            if source not in counts or source == sources[0] or source in selected_sources:
                raise ValueError('Reference must select distinct supplied context documents')
            selected_sources.add(source)
            cited = {c['source'] for c in selected['support']}
            if source not in cited or not (cited & (citing_sources - {source})):
                raise ValueError('Document relationship needs both citing and referenced source support')
            claim = selected.get('host_population')
            if claim is not None:
                if reference['relationship'] != 'laboratory-evidence':
                    raise ValueError('Host population belongs to a laboratory document relationship')
                support_pages = {(c['source'], c['page']) for c in claim['support']}
                if not ({s for s, _ in support_pages} & (citing_sources - {source})):
                    raise ValueError('Host population needs its citing source connecting clause')
                fragments = [field_fragment(material, f) for f in claim['host_fragments']]
                if any(f['source'] not in citing_sources - {source}
                       or (f['source'], f['page']) not in support_pages for f in fragments):
                    raise ValueError('Host words need supported fragments from the citing source')
                keys = [(f['source'], f['page'], f['locator']) for f in fragments]
                if len(keys) != len(set(keys)):
                    raise ValueError('Host population repeats a source fragment')
    ids = [d['id'] for d in reading['directions']]
    if any(not x for x in ids) or len(ids) != len(set(ids)):
        raise ValueError('Direction references must be distinct within this reading')
    for direction in reading['directions']:
        _validate_direction_components(direction, ids, reading['issues'])
    for target in [*reading['target_scopes'], *reading['prose_positions'], *reading['image_positions']]:
        if not set(target['direction_ids']) <= set(ids):
            raise ValueError('Target refers to an absent direction')
    occupied = set()
    visual_cells = {}
    table_position_areas = []
    table_position_words = set()
    for scope in reading['target_scopes']:
        table = material['tables'][scope['table_ref']]
        if not 1 <= scope['first_row'] <= scope['last_row'] <= len(table['rows']):
            raise ValueError('Selected rows outside their source table')
        roles = [c['role'] for c in scope['columns']]
        if len(roles) != len(set(roles)):
            raise ValueError('A source field has more than one column assignment')
        for column in scope['columns']:
            for fragment in column.get('fragments', []):
                if 'transcription' in fragment:
                    key = fragment['table_ref'], fragment['cell']
                    text = fragment['transcription']
                    if key in visual_cells and visual_cells[key] != text:
                        raise ValueError('One source cell has conflicting visual readings')
                    visual_cells[key] = text
        for row in range(scope['first_row'], scope['last_row'] + 1):
            key = scope['table_ref'], row
            if key in occupied:
                raise ValueError('One source occurrence needs one composed scope')
            occupied.add(key)
            fields, _ = table_fields(material, scope['table_ref'], row,
                                    {c['role']: c['column'] for c in scope['columns']},
                                    {c['role']: c.get('fragments', []) for c in scope['columns']})
            cited = {(c['source'], c['page']) for c in scope['support']}
            if (table['source'], table['page']) not in cited:
                raise ValueError('A selected table position needs its source page as support')
            # Shared contextual fields do not identify another position. Plants
            # within one printed parcel retain their separate plant occurrences.
            identifying_role = next((role for role in ('plant_id', 'parcel') if fields.get(role)), None)
            if identifying_role:
                identifying = fields[identifying_role]
                spans = {native_span(material, span)['locator']: span
                         for column in scope['columns'] if column['role'] == identifying_role
                         for span in column.get('fragments', []) if 'line_ref' in span}
                for fragment in identifying.get('fragments', [identifying]):
                    if fragment.get('locator') in spans:
                        span = spans[fragment['locator']]
                        table_position_words.update((span['line_ref'], index)
                            for index in range(span['first_word'], span['end_word']))
                        continue
                    table_position_areas.append(dict(
                        source=fragment.get('source', table['source']),
                        page=fragment.get('page', table['page']), bbox=fragment['bbox']))
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
    owned_areas = tuple(association_areas(material))
    selected_words = set()
    for position in reading['prose_positions']:
        cited = {(c['source'], c['page']) for c in position['support']}
        source_pages = set()
        spans_by_role = {}
        for field in position['fields']:
            if not field['spans']:
                raise ValueError('Native fields require a source span')
            field_words = set()
            for span in field['spans']:
                fragment = native_span(material, span)
                source_pages.add((fragment['source'], fragment['page']))
                words = {(span['line_ref'], index)
                         for index in range(span['first_word'], span['end_word'])}
                if field_words & words:
                    raise ValueError('A native field has repeated or overlapping source spans')
                field_words.update(words)
                if span_overlaps(material, span, owned_areas):
                    raise ValueError('The association owner already supplies this source field')
            spans_by_role[field['role']] = field['spans']
        if len({source for source, _ in source_pages}) > 1:
            raise ValueError('A native position must stay within its source document')
        if not source_pages <= cited:
            raise ValueError('A native position needs every selected source page as support')
        identifying = spans_by_role.get('plant_id') or spans_by_role.get('parcel', ())
        position_words = {(span['line_ref'], index) for span in identifying
                          for index in range(span['first_word'], span['end_word'])}
        if position_words & (selected_words | table_position_words) or any(
                span_overlaps(material, span, table_position_areas) for span in identifying):
            raise ValueError('One source position needs one selection, without overlapping identifying spans')
        selected_words.update(position_words)
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
        x0, y0, x1, y1 = image['bbox']
        if any(t['source'] == image['source'] and t['page'] == image['page']
               and (position['image_ref'] in material['pages']
                    or (max(x0, t['bbox'][0]) < min(x1, t['bbox'][2])
                        and max(y0, t['bbox'][1]) < min(y1, t['bbox'][3])))
               for t in material['tables'].values()):
            raise ValueError('Use native table cells rather than retranscribing their source area')
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
                              execute=execute, timeout=timeout,
                              supplement_page_rotations=True)
    _validate_reading(response['reading'], response['request']['sources'], store, material)
    return MeasureReading(response, material, associations)


def retained_measure(request_id, store, *, component_requests=()):
    """Consume a named interpretation with its original context, without re-extraction."""
    response = read_retained(request_id, store)
    from jsonschema import Draft202012Validator
    # Additive source roles need not invalidate an otherwise compatible reading.
    # The old generated-target contract still cannot satisfy this composition.
    compatible = deepcopy(response['reading'])
    for direction in compatible['directions']:
        # Validation compatibility is not a source-stated absence. The original
        # response stays unchanged and the accessor names its missing reading.
        direction.setdefault('commencement_components', None)
    for reference in compatible['references']:
        reference.setdefault('documents', [])
        reference.setdefault('acts', [])
        for selected in reference['documents']:
            selected.setdefault('host_population', None)
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
    measure = MeasureReading(response, material, associations)
    component_requests = tuple(component_requests)
    if len(component_requests) != len(set(component_requests)):
        raise ValueError('Select distinct component-reading requests')
    supplements = []
    for identity in component_requests:
        supplement = read_retained(identity, store)
        _validate_component_response(measure, supplement, store)
        supplements.append(supplement)
    return MeasureReading(response, material, associations, tuple(supplements))


def _component_schema(base_request, direction_ids):
    return _object(base_request={'type': 'string', 'const': base_request},
                   directions=_array(_object(id=_choice(*direction_ids),
                                             commencement_components=COMMENCEMENT_COMPONENTS)),
                   issues=ISSUES)


def _validate_component_response(measure, response, store):
    from jsonschema import Draft202012Validator
    base = measure.response['request_sha256']
    reading = response['reading']
    if reading.get('base_request') != base:
        raise ValueError('Component reading belongs to another retained base request')
    if response['request']['sources'] != measure.response['request']['sources']:
        raise ValueError('Component reading must supply the same complete original sources')
    if not context_matches(response['request']['prompt'], measure.material):
        raise ValueError('Component reading source addresses differ from the retained measure')
    directions = {d['id']: d for d in measure.values['directions']}
    schema = response['request']['schema']
    try:
        selected = schema['properties']['directions']['items']['properties']['id']['enum']
    except KeyError as error:
        raise ValueError('Component request has no explicit direction selection') from error
    if (not selected or len(selected) != len(set(selected)) or not set(selected) <= directions.keys()
            or schema != _component_schema(base, selected)):
        raise ValueError('Component request differs from its exact base and source-direction contract')
    Draft202012Validator(schema).validate(reading)
    returned = [entry['id'] for entry in reading['directions']]
    if len(returned) != len(set(returned)) or set(returned) != set(selected):
        raise ValueError('Component response must account for every selected direction exactly once')
    projected = deepcopy(measure.values)
    by_id = {d['id']: d for d in projected['directions']}
    for entry in reading['directions']:
        target = by_id[entry['id']]
        target['commencement_components'] = entry['commencement_components']
        selected_pages = {(c['source'], c['page']) for c in target['support']}
        for component in entry['commencement_components'] or ():
            if not selected_pages.intersection((c['source'], c['page']) for c in component['support']):
                raise ValueError('Component support must attach to the selected source clause')
        _validate_direction_components(target, directions, reading['issues'])
    projected['issues'].extend(reading['issues'])
    _validate_reading(projected, response['request']['sources'], store, measure.material)


def read_measure_components(base_request, direction_ids, store, *, execute=False,
                            review_instruction='', timeout=1800,
                            model='gpt-6-astra', effort='medium'):
    """Read only reached components against the same complete original sources.

    This is the measure owner's additive reading, bound to an exact retained
    request. It supplies no old period, scope or expected interpretation as an
    answer, and never replaces the parent's targets, events or raw response.
    """
    measure = retained_measure(base_request, store)
    selected = tuple(direction_ids)
    directions = {d['id']: d for d in measure.values['directions']}
    if not selected or len(selected) != len(set(selected)) or not set(selected) <= directions.keys():
        raise ValueError('Select distinct existing directions from the retained request')
    schema = _component_schema(base_request, selected)
    instructions = PROMPT.split('\nCommencement components\n', 1)[1]
    prompt = (
        'Read the selected source clauses from the supplied complete originals. '
        'Return only the requested commencement components and their scoped issues, '
        'bound to the exact base_request in the schema. The retained IDs and quotations '
        'locate source clauses; the actual original prevails over any prior interpretation. '
        'Do not reconstruct identity, targets, unrelated directions or events. '
        'Return every selected direction, using null with a cause when unresolved.\n'
        + instructions + material_context(measure.material)
        + '\nSELECTED COMPONENT OUTPUT IDS\n' + json.dumps(selected)
        + '\nDIRECTION SOURCE SUPPORT (all retained direction addresses; only selected IDs are outputs)\n'
        + json.dumps([dict(id=identity, support=direction['support'])
                      for identity, direction in directions.items()], ensure_ascii=False)
        + '\n' + review_instruction)
    response = read_documents(measure.response['request']['sources'], store,
                              prompt=prompt, schema=schema, model=model, effort=effort,
                              execute=execute, timeout=timeout,
                              supplement_page_rotations=True)
    _validate_component_response(measure, response, store)
    return response
