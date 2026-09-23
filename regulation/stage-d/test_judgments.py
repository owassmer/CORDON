"""TAR decision events attach one kind each, by block, to the order and person the decision names.

Block text is TAR Bari 546/2023 (GA XML), shortened; the reading around it is the
shape the reader returns.
"""
from datetime import date
import copy
import unittest

from cordon_d.judgments import blocks, judgment_events, validate

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


if __name__ == '__main__':
    unittest.main()
