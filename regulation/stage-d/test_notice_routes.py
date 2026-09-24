"""An order's own mass-publicity basis reaches Art. 21-bis without D deciding it.

Page text and quotations are DDS 63/2026 (store bd7f7bd2…f8dcf8375), pages 4-6,
as the transport supplies them, shortened. The reading around them is the shape
the reader returns.
"""
from datetime import date
from pathlib import Path
import copy
import unittest

from cordon_c.core import Snapshot
from cordon_d.notice_routes import COMPLETED, RULE, STATED_GROUND, c_result, mass_publicity_basis, validate

ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'bd7f7bd2162ad5a14eaf9e3e8114733f2170f20f8f0486261d05f72dadcf8375'
GENERAL = ('Qualora per il numero dei destinatari la comunicazione personale non sia possibile o risulti '
           'particolarmente gravosa, l’amministrazione provvede mediante forme di pubblicità idonee')
GROUND = ('tenuto conto dell’irreperibilità di alcuni destinatari e della gravosità per l’amministrazione di '
          'notificare i provvedimenti ai singoli beneficiari')
PAGES = {
    4: '• L’art. 21 bis della legge 7 agosto 1990, n. 241 prevede che ... ' + GENERAL + ' di volta in volta\n',
    6: ('Di adempiere agli obblighi di pubblicità del presente provvedimento mediante affissione per 7 giorni '
        'nell’albo pretorio del Comune in cui ricadono le piante da estirpare ' + GROUND + ';\n'
        'al Comune di Cagnano Varano (FG) affinché provveda con urgenza dalla data di invio del presente atto '
        'all’affissione all’Albo Pretorio della presente determinazione per la durata di 7 (sette) giorni '
        'naturali e consecutivi. Tale affissione, ai sensi dell’art. 21 bis L. 241/1990 e s.m.i., decorso il '
        'settimo giorno dalla data di pubblicazione assume valore di notifica ai proprietari/conduttori\n'),
}
FORM = ('all’affissione all’Albo Pretorio della presente determinazione per la durata di 7 (sette) giorni '
        'naturali e consecutivi')
EFFECT = 'decorso il settimo giorno dalla data di pubblicazione assume valore di notifica'
READING = dict(
    grounds=[dict(literal=GENERAL, about='general-law', part='recital', support=[dict(page=4, quote=GENERAL)]),
             dict(literal=GROUND, about='this-act', part='operative', support=[dict(page=6, quote=GROUND)])],
    forms=[dict(literal=FORM, duration=dict(number='7', unit_word='giorni naturali e consecutivi',
                                            literal='per la durata di 7 (sette) giorni naturali e consecutivi'),
                effect=EFFECT, part='operative', support=[dict(page=6, quote=FORM + '. Tale affissione')])],
    issues=[])


def response(values=READING):
    return dict(request_sha256='0' * 64, request=dict(sources=[SOURCE]), reading=values)


class MassPublicityBasis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Snapshot.load(ROOT)
        cls.at = date(2026, 9, 23)
        cls.vid = cls.s.version(RULE, cls.at)['provision_version_id']

    def test_quotations_and_copied_words_bind_to_their_pages(self):
        validate(READING, PAGES)
        for path, value in ((('grounds', 1, 'literal'), 'tenuto conto del numero elevato dei destinatari'),
                            (('forms', 0, 'effect'), 'assume valore di notifica individuale'),
                            (('forms', 0, 'duration', 'number'), '10')):
            broken = copy.deepcopy(READING)
            target = broken
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate(broken, PAGES)

    def test_a_stated_ground_is_the_acts_own_and_completion_stays_open(self):
        # Owen's 2026-09-24 ruling: the act's own stated ground meets Art. 21-bis; C does not re-judge it.
        basis = mass_publicity_basis(response(), instrument='REG-PUGLIA-U181-DIR-2026-00063')
        self.assertEqual([g['literal'] for g in basis['stated_ground']], [GROUND])
        self.assertEqual([g['literal'] for g in basis['restated_rule']], [GENERAL])
        result = c_result(self.s, basis, self.at)
        self.assertIsNone(result.truth)
        self.assertNotIn(f'predicate: {self.vid} :: {STATED_GROUND}', result.needs)
        self.assertIn(f'predicate: {self.vid} :: {COMPLETED}', result.needs)

    def test_a_restated_rule_alone_supplies_nothing(self):
        values = copy.deepcopy(READING)
        values['grounds'] = values['grounds'][:1]
        result = c_result(self.s, mass_publicity_basis(response(values), instrument='X'), self.at)
        self.assertIsNone(result.truth)
        self.assertIn(f'predicate: {self.vid} :: {STATED_GROUND}', result.needs)

    def test_a_held_posting_is_named_for_A_and_does_not_complete_publicity(self):
        basis = mass_publicity_basis(response(), instrument='I')
        result = c_result(self.s, basis, self.at, postings=[dict(publisher='Comune di Taranto',
                                                                start='2021-12-14', end=None)])
        self.assertIsNone(result.truth)
        self.assertTrue(any('held posting (Comune di Taranto from 2021-12-14, end not established)' in n for n in result.needs))
        self.assertNotIn(f'predicate: {self.vid} :: {COMPLETED}', result.needs)


if __name__ == '__main__':
    unittest.main()
