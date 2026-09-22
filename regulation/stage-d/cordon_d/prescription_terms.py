"""Carry source-stated clause components into C without asserting applicability."""
from decimal import Decimal
import json

from cordon_c.core import MissingInput, PrescribedTerm


CLOCK = 'B-CLK-prescription-notification-noncommencement'
UNITS = {'days': 'calendar_days', 'working-days': 'working_days',
         'months': 'months', 'years': 'years', 'hours': 'hours'}


def measure_prescribed_term(snapshot, at, measure, direction_id, component_index, *,
                            document, recipient, commencement_work, source_context):
    """Prepare a quantity candidate for an explicitly supplied operative context.

    `source_context` retains the caller's existing target, recipient and operative
    relationship evidence unchanged. Neither its presence nor equal identifiers
    proves correspondence, lawful scope, notice or the A interpretation's form.
    In particular, the principal measure cannot supply an inherited prescription
    identity by default. The remaining A predicates receive no truth value here.

    `measure` supplies the ordinary commencement_components accessor; this module
    does not load another reader, scan responses or choose an acceptance snapshot.
    """
    reading = measure.commencement_components(direction_id)
    components = reading['components']
    if components is None:
        raise MissingInput(reading['cause'])
    if not components:
        raise MissingInput('The examined direction supplies no commencement component')
    if type(component_index) is not int or not 0 <= component_index < len(components):
        raise ValueError('Select one existing commencement component')
    component = components[component_index]
    direction = reading['direction']
    period = component['period']
    if period is None:
        raise MissingInput('Source-stated commencement period; see component issues')
    if 'bound' not in period:
        raise MissingInput('Source period bound is unavailable')
    for name, value, required in (
            ('direction mode', direction['mode'], 'conditional-order'),
            ('direction work', direction['work'], 'removal'),
            ('trigger', component['trigger'], 'noncommencement'),
            ('performance', component['performance'], 'concrete-commencement'),
            ('anchor', period['anchor'], 'notification'),
            ('period bound', period['bound'], 'within-maximum'),
            ('commitment', component['commitment'], 'will-direct')):
        if value == 'unresolved':
            raise MissingInput(f'Source component {name}; see component issues')
        if value != required:
            raise ValueError(f'Source {name} is outside this notification/noncommencement quantity form')
    for name in ('required_actor', 'commencement_work'):
        if not component[name]:
            raise MissingInput(f'Source {name} statement; see component issues')
    if period['magnitude'] is None or period['unit'] == 'unresolved':
        raise MissingInput('Source period magnitude and unit; see component issues')
    if period['unit'] not in UNITS:
        raise ValueError('Source period unit has no supported counting convention')
    for name, value in (('operative prescription document relationship', document),
                        ('recipient context', recipient),
                        ('commencement-work context', commencement_work)):
        if not isinstance(value, str) or not value.strip():
            raise MissingInput(name)
    if not component['support']:
        raise MissingInput('Source support for the operative clause components')
    clause = json.dumps([(c['source'], c['page'], c['locator']) for c in component['support']],
                        ensure_ascii=False, separators=(',', ':'))
    term = PrescribedTerm(document, clause, recipient, commencement_work,
                          Decimal(period['magnitude']), UNITS[period['unit']])
    if CLOCK not in snapshot.clocks:
        raise MissingInput('Source-bound prescription clock is not available in the supplied A/B snapshot')
    quantity = snapshot.quantity(CLOCK, at, prescribed_term=term)
    return dict(term=term, quantity=quantity, direction=direction, component=component,
                readings=reading['readings'], issues=reading['issues'], source_context=source_context)
