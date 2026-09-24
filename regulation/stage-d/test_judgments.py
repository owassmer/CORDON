"""TAR decision events attach one kind each, by block, to the order and person the decision names.

Block text is TAR Bari 546/2023 (GA XML), shortened; the reading around it is the
shape the reader returns.
"""
from datetime import date
import copy
import unittest

from cordon_d.judgments import (annulment_basis, blocks, decision_identity, judgment_events, liveness_closures,
                                validate, validate_disposition)

XML = ('<?xml version="1.0" encoding="UTF-8"?><GA xmlns:h="http://www.w3.org/HTML/1998/html4"><Provvedimento>'
       '<h:div>SENTENZA</h:div><h:div><h:div>-dell’atto dirigenziale n. 137 dell’11.11.2021 del Resp. Sezione '
       'Osservatorio Fitosanitario</h:div></h:div><h:div> </h:div>'
       '<h:div>pubblicato sull’Albo Pretorio del Comune di Ostuni dal 12 al 19 novembre 2021</h:div>'
       '<h:div>nota prot. n. 1412 dell’11.2.2022, trasmessa alla ricorrente Anna Antonia Crescenza a mezzo pec '
       'in data 14.2.2022</h:div></Provvedimento></GA>').encode()
TEXTS = blocks(XML)
ORDER = dict(number='137', adopted_words='11.11.2021', year='2021',
             support=dict(block=2, quote='atto dirigenziale n. 137 dell’11.11.2021'))
POSTING = dict(order_index=0, recipient='', municipality='Comune di Ostuni', date_words='dal 12 al 19 novembre 2021',
               attribution='court', support=dict(block=3, quote='Albo Pretorio del Comune di Ostuni dal 12 al 19 novembre 2021'))
READING = dict(orders=[ORDER], issues=[], events=[
    dict(POSTING, kind='municipal-publication-start', date='2021-11-12'),
    dict(POSTING, kind='municipal-publication-end', date='2021-11-19'),
    dict(kind='recipient-pec-delivery', order_index=0, recipient='Anna Antonia Crescenza', municipality='',
         date_words='14.2.2022', date='2022-02-14', attribution='court',
         support=dict(block=4, quote='trasmessa alla ricorrente Anna Antonia Crescenza a mezzo pec in data 14.2.2022'))])
HELD = 'REG-PUGLIA-U181-DIR-2021-00137'


def response(values=READING):
    return dict(request_sha256='0' * 64, request=dict(sources=['f' * 64]), reading=values)


class JudgmentEvents(unittest.TestCase):
    def test_blocks_are_the_nonempty_leaf_divisions_in_order(self):
        self.assertEqual(len(TEXTS), 4)
        self.assertTrue(TEXTS[1].startswith('-dell’atto dirigenziale n. 137'))

    def test_quotations_and_copied_words_bind_to_their_blocks(self):
        validate(READING, TEXTS)
        for path, value in ((('events', 2, 'recipient'), 'Mario Rossi'),
                            (('events', 2, 'date'), '2022-02-15'),
                            (('events', 0, 'recipient'), 'Anna Antonia Crescenza'),
                            (('orders', 0, 'number'), '173'),
                            (('events', 1, 'support', 'block'), 4)):
            broken = copy.deepcopy(READING)
            target = broken
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate(broken, TEXTS)

    def test_events_attach_one_kind_each_to_the_held_order_and_named_person(self):
        attached, unattached = judgment_events(response(), held_instruments={HELD})
        self.assertEqual(unattached, ())
        self.assertEqual([(e.kind, e.document, e.recipient, e.occurred) for e in attached], [
            ('municipal-publication-start', HELD, None, date(2021, 11, 12)),
            ('municipal-publication-end', HELD, None, date(2021, 11, 19)),
            ('recipient-pec-delivery', HELD, 'Anna Antonia Crescenza', date(2022, 2, 14))])
        self.assertEqual(attached[2].support.selector, 'block:4')
        self.assertTrue(attached[2].support.reading.startswith('court: '))

    def test_an_order_D_does_not_hold_leaves_the_event_unattached_with_its_cause(self):
        attached, unattached = judgment_events(response(), held_instruments=set())
        self.assertEqual(attached, ())
        self.assertEqual({u['cause'] for u in unattached}, {'the decision names an order D does not hold'})


DISPOSITION_XML = (
    '<?xml version="1.0" encoding="UTF-8"?><GA xmlns:h="http://www.w3.org/HTML/1998/html4"><Provvedimento>'
    '<meta><descrittori><registro anno="2022" n="00281"/><fascicolo anno="2023" n="00546"/>'
    '<urn>urn:nir:tar.puglia;sezione.3:sentenza:00000-0000</urn></descrittori><tipologia>Sentenza</tipologia>'
    '<dataPubblicazione>24/03/2023</dataPubblicazione></meta>'
    '<h:div>Anna Antonia Crescenza, rappresentata e difesa</h:div>'
    '<h:div>-dell’atto dirigenziale n. 137 dell’11.11.2021 del Resp. Sezione Osservatorio Fitosanitario</h:div>'
    '<h:div>La misura decisa dalla Regione Puglia risulta affetta dalla denunciata violazione del principio di '
    'proporzionalità</h:div>'
    '<h:div>lo accoglie e, per l’effetto, annulla gli atti impugnati nei limiti dell’interesse dei ricorrenti e per '
    'quanto in motivazione</h:div><dataeluogo norm="15/12/2022"/></Provvedimento></GA>').encode()
DTEXTS = blocks(DISPOSITION_XML)
ANNULLED = dict(
    number='137', adopted_words='11.11.2021', year='2021', effect='annulled',
    scope=dict(kind='applicants', dispositive='nei limiti dell’interesse dei ricorrenti', stated=[]),
    applicants=dict(literal='Anna Antonia Crescenza', support=dict(block=1, quote='Anna Antonia Crescenza')),
    grounds=[dict(literal='violazione del principio di proporzionalità',
                  support=dict(block=3, quote='violazione del principio di proporzionalità'))],
    stated_reason=[], support=dict(block=2, quote='atto dirigenziale n. 137 dell’11.11.2021'))
DISPOSITION = dict(outcome=dict(literal='lo accoglie e, per l’effetto, annulla gli atti impugnati', kind='accoglie',
                                support=dict(block=4, quote='annulla gli atti impugnati')),
                   acts=[ANNULLED], issues=[])


class CourtDispositions(unittest.TestCase):
    def test_the_decision_identity_is_its_own_GA_descriptors(self):
        self.assertEqual(decision_identity(DISPOSITION_XML), dict(
            kind='Sentenza', number='546/2023', section='3', register='202200281', decided=date(2022, 12, 15),
            published=date(2023, 3, 24)))

    def test_outcome_act_scope_and_applicants_bind_to_their_blocks(self):
        validate_disposition(DISPOSITION, DTEXTS)
        for path, value in ((('outcome', 'literal'), 'lo respinge'),
                            (('acts', 0, 'scope', 'dispositive'), 'nei limiti delle particelle indicate'),
                            (('acts', 0, 'applicants', 'literal'), 'Mario Rossi'),
                            (('acts', 0, 'grounds', 0, 'literal'), 'difetto di istruttoria'),
                            (('acts', 0, 'number'), '173')):
            broken = copy.deepcopy(DISPOSITION)
            target = broken
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_disposition(broken, DTEXTS)

    def test_the_latest_disposition_of_each_ricorso_states_what_closes(self):
        response = dict(request_sha256='0' * 64, request=dict(sources=['f' * 64]), reading=DISPOSITION)
        identity = decision_identity(DISPOSITION_XML)
        entries, unattached = annulment_basis(response, identity, held_instruments={HELD})
        self.assertEqual((len(entries), unattached), (1, []))
        interim = dict(entries[0], effect='suspended',
                       decision=dict(identity, kind='Ordinanza cautelare', published=date(2022, 5, 6)))
        closures = liveness_closures([interim, entries[0]])
        self.assertEqual([(c['effect'], c['scope'], c['applicants'], c['since']) for c in closures[HELD]],
                         [('annulled', 'applicants', 'Anna Antonia Crescenza', date(2023, 3, 24))])
        ended = dict(entries[0], effect='not-annulled', decision=dict(identity, published=date(2026, 3, 25)),
                     stated_reason=[dict(literal='superamento della DDS da parte della successiva', support=None)])
        self.assertEqual([c['effect'] for c in liveness_closures([interim, ended])[HELD]],
                         ['ended-with-stated-reason'])
        refused = dict(entries[0], effect='suspension-refused')
        self.assertEqual(liveness_closures([refused]), {})
        self.assertEqual(annulment_basis(response, identity, held_instruments=set())[0], [])


if __name__ == '__main__':
    unittest.main()
