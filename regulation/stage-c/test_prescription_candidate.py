"""Explicit temporary amendment verification; never an accepted-owner loader."""

import contextlib
import copy
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zoneinfo import ZoneInfo

from cordon_c import PrescribedTerm, Snapshot, evaluate
from cordon_c.bindings import leaves, noncommencement_facts
from cordon_c.quantities import clock_boundary
from cordon_c.temporal import WorkingCalendar


ROOT = Path(__file__).resolve().parents[2]
PROPOSAL = 'corpus/workbench/prescription-clause-amendment.json'
EU = 'regulation/stage-a/authoring-eu.json'
JURISDICTION = 'regulation/jurisdiction/canonical/authoring.json'
LEDGER = 'regulation/stage-b/clocks-and-parameters.json'
POPULATION = 'regulation/stage-b/population.json'
CALENDAR = 'regulation/stage-c/calendar-rules.json'
sys.path.insert(0, str(ROOT / 'scripts'))
import verify_jurisdiction_stage_a as jurisdiction_verifier
import verify_stage_b as b_verifier


def _patch_rows(rows, key, *, remove=(), replace=(), add=()):
    """Apply exact patch targets; an unmatched target is a failed amendment."""
    existing = {key(row): row for row in rows}
    removed = set(remove)
    replacements = {key(row): row for row in replace}
    added = {key(row): row for row in add}
    if (len(existing) != len(rows) or len(removed) != len(remove)
            or len(replacements) != len(replace) or len(added) != len(add)):
        raise ValueError('Duplicate amendment row or target')
    if not (removed | replacements.keys()) <= existing.keys() or removed & replacements.keys():
        raise ValueError('Amendment removal/replacement target is absent or conflicting')
    if added.keys() & existing.keys():
        raise ValueError('Amendment addition already exists')
    return [replacements.get(key(row), row) for row in rows if key(row) not in removed] + list(add)


def expand_candidate(proposal=None, *, root=ROOT):
    """Return copied candidate owners only after checking their exact accepted base."""
    current = json.loads((root / 'state/CURRENT.json').read_text())
    stages = current['stages']
    if any(stages[name]['status'] != 'CLOSED' for name in ('A', 'B')):
        raise ValueError('Candidate requires the stated accepted A/B base')
    proposal = json.loads((root / PROPOSAL).read_text()) if proposal is None else proposal
    if (proposal['schema'] != 'cordon-prescription-clause-amendment-v1'
            or proposal['status'] != 'PROPOSED_FOR_REVIEW_NOT_ACCEPTED'):
        raise ValueError('Candidate must remain an explicit unaccepted amendment')
    entries = list(stages['A']['canonical_artifacts'].values())
    entries += [stages['B'][name] for name in ('canonical', 'population')]
    expected = {entry['path']: entry['sha256'] for entry in entries}
    if proposal['accepted_base'] != expected:
        raise ValueError('Candidate accepted-base hashes differ from CURRENT')
    documents = {}
    for path, digest in expected.items():
        raw = (root / path).read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError(f'Accepted base changed: {path}')
        documents[path] = json.loads(raw)

    a = proposal['stage_a']
    original = documents[JURISDICTION]
    rows = _patch_rows(original, lambda row: row['provision_version_id'],
                       remove=a['remove'], replace=a['replace'], add=a['add'])
    added_ids = {row['provision_version_id'] for row in a['add']}
    retained = [row for row in rows if row['provision_version_id'] not in added_ids]
    regional = lambda row: row['instrument_id'].startswith(('PUG-', 'REG-PUGLIA-'))
    split = next((i for i, row in enumerate(retained) if regional(row)), len(retained))
    rows = (retained[:split] + [row for row in a['add'] if not regional(row)]
            + retained[split:] + [row for row in a['add'] if regional(row)])
    prefix_count = stages['A']['canonical_artifacts']['italy_and_puglia']['national_prefix_rows']
    if rows[:prefix_count] != original[:prefix_count]:
        raise ValueError('Amendment changes the accepted national prefix')
    documents[JURISDICTION] = rows

    b = proposal['stage_b']
    ledger = documents[LEDGER]
    ledger['schema'] = b['schema']
    ledger['conventions'].update(b['conventions'])
    ledger['clocks'] = _patch_rows(ledger['clocks'], lambda row: row['clock_id'],
                                 remove=b['remove_clocks'], add=b['add_clocks'])
    removed_producers = set(b['remove_disposition_producers'])
    if not removed_producers <= {row['provision_version_id'] for row in ledger['dispositions']}:
        raise ValueError('Disposition-removal producer is absent')
    disposition_key = lambda row: (row['provision_version_id'],
                                    ('expression', row['expression']) if 'expression' in row else ('ref', row['ref']))
    removals = [disposition_key(row) for row in ledger['dispositions']
                if row['provision_version_id'] in removed_producers]
    ledger['dispositions'] = _patch_rows(ledger['dispositions'], disposition_key, remove=removals,
                                       replace=b['replace_dispositions'], add=b['add_dispositions'])
    for manifest in ledger['closure_manifest']:
        manifest.update(status='OPEN', reread=None, semantic_acceptance='NOT_ASSERTED',
                        semantic_reviewer=None, acceptance_act=None, acceptance_evidence=None,
                        accepted_content_sha256=None)

    population = documents[POPULATION]['seams']
    removed = set(proposal['population']['remove'])
    existing = [identity for identities in population.values() for identity in identities]
    additions = proposal['population']['add']
    added = [identity for identities in additions.values() for identity in identities]
    if (len(removed) != len(proposal['population']['remove']) or not removed <= set(existing)
            or len(added) != len(set(added)) or set(added) & set(existing)
            or not additions.keys() <= population.keys()):
        raise ValueError('Population amendment targets are absent, duplicated or conflicting')
    for seam in population:
        population[seam] = [identity for identity in population[seam] if identity not in removed]
        population[seam].extend(additions.get(seam, []))

    calendar = json.loads((root / CALENDAR).read_text())
    removed = set(proposal.get('stage_c', {}).get('remove_calendar_clocks', []))
    if not removed <= {identity for identities in calendar.values() for identity in identities}:
        raise ValueError('Calendar-removal clock is absent')
    documents[CALENDAR] = {group: [identity for identity in identities if identity not in removed]
                           for group, identities in calendar.items()}
    return documents


def verified_candidate_snapshot(proposal=None):
    """Run A/B mechanics on temporary expansion, then construct C explicitly."""
    documents = expand_candidate(proposal)
    with tempfile.TemporaryDirectory(prefix='cordon-prescription-candidate-') as directory:
        temporary = Path(directory)
        for relative, document in documents.items():
            path = temporary / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n')
        jurisdiction_verifier.verify(temporary / JURISDICTION, check_projection=False, check_authority=False)
        b_verifier.main(temporary / LEDGER, (temporary / EU, temporary / JURISDICTION), temporary / POPULATION)
    references = json.loads((ROOT / 'regulation/stage-c/reference-bindings.json').read_text())
    return Snapshot(documents[EU] + documents[JURISDICTION], documents[LEDGER], references)


class PrescriptionCandidate(unittest.TestCase):
    def test_expanded_candidate_passes_existing_owner_verifiers(self):
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                snapshot = verified_candidate_snapshot()
        except SystemExit:
            self.fail(output.getvalue())
        self.assertIsInstance(snapshot, Snapshot)

    def test_candidate_cannot_claim_another_base_or_accepted_status(self):
        original = json.loads((ROOT / PROPOSAL).read_text())
        changed = copy.deepcopy(original)
        changed['accepted_base'][EU] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'accepted-base hashes'):
            expand_candidate(changed)
        changed = copy.deepcopy(original)
        changed['status'] = 'ACCEPTED'
        with self.assertRaisesRegex(ValueError, 'explicit unaccepted'):
            expand_candidate(changed)

    def test_open_or_changed_base_cannot_be_used_as_accepted_input(self):
        proposal = json.loads((ROOT / PROPOSAL).read_text())
        current = json.loads((ROOT / 'state/CURRENT.json').read_text())
        with tempfile.TemporaryDirectory(prefix='cordon-candidate-invalid-base-') as directory:
            root = Path(directory)
            state = root / 'state/CURRENT.json'
            state.parent.mkdir(parents=True)
            current['stages']['A']['status'] = 'OPEN'
            state.write_text(json.dumps(current))
            with self.assertRaisesRegex(ValueError, 'accepted A/B base'):
                expand_candidate(proposal, root=root)
            current['stages']['A']['status'] = 'CLOSED'
            state.write_text(json.dumps(current))
            changed_source = root / EU
            changed_source.parent.mkdir(parents=True)
            changed_source.write_bytes((ROOT / EU).read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'Accepted base changed'):
                expand_candidate(proposal, root=root)

    def test_expansion_discards_all_copied_acceptance_claims(self):
        ledger = expand_candidate()[LEDGER]
        self.assertEqual([row['seam'] for row in ledger['closure_manifest']], [1, 2, 3, 4])
        for row in ledger['closure_manifest']:
            self.assertEqual(row['semantic_acceptance'], 'NOT_ASSERTED')
            self.assertEqual(row['status'], 'OPEN')
            for field in ('reread', 'semantic_reviewer', 'acceptance_act', 'acceptance_evidence', 'accepted_content_sha256'):
                self.assertIsNone(row[field])

    def test_interpretation_cannot_masquerade_as_a_statutory_provision(self):
        proposal = json.loads((ROOT / PROPOSAL).read_text())
        interpretation = next(row for row in proposal['stage_a']['add']
                              if row.get('record_kind') == 'SOURCE_CLAUSE_INTERPRETATION')
        interpretation['instrument_id'] = 'IT-L241-1990'
        with self.assertRaisesRegex(AssertionError, 'interpretation presented as a source provision'):
            verified_candidate_snapshot(proposal)


class CandidateComposition(unittest.TestCase):
    """Synthetic qualified inputs test composition, not ordinary D source reading."""

    consumer = 'SOURCE-CLAUSE:notification-noncommencement-direction'
    recognized = 'the operative prescription expressly directs coercive removal after noncommencement within its stated notification-based term'
    context = 'this operative prescription, including applicable corrections, governs this recipient and commencement work'
    lawful_commencement = 'the prescribed commencement work is lawfully due from this recipient under this clause'
    lawful_coercion = 'the prescribed coercive population remains lawfully due under this direction'
    notified = 'legally sufficient notification of that prescription to this recipient has occurred'
    elapsed = 'the source notification-based commencement deadline has elapsed'
    absent = 'noncommencement of that work by the source deadline is established'
    required = 'CASE_NONCOMMENCEMENT_COERCIVE_DIRECTION_REQUIRED'
    not_established = 'CASE_NONCOMMENCEMENT_DIRECTION_NOT_ESTABLISHED'
    at = date(2026, 9, 8)
    zone = ZoneInfo('Europe/Rome')

    @classmethod
    def setUpClass(cls):
        with contextlib.redirect_stdout(io.StringIO()):
            cls.snapshot = verified_candidate_snapshot()

    def setUp(self):
        self.row = self.snapshot.version(self.consumer, self.at)
        clocks = [row for row in self.snapshot.clocks.values() if row['consumer_decision'] == self.consumer]
        self.assertEqual(len(clocks), 1)
        self.clock = clocks[0]['clock_id']
        self.term = PrescribedTerm('unseen-document-849', 'unregistered-clause-23', 'unseen-recipient-62',
                                   'exact-commencement-work-71', Decimal('3'), 'calendar_days')
        self.calendar = WorkingCalendar(date(2026, 1, 1), date(2027, 1, 1), frozenset(), frozenset({5, 6}))
        self.contextual = {predicate: True for predicate in (
            self.recognized, self.context, self.lawful_commencement, self.lawful_coercion, self.notified)}
        self.assertEqual(set(leaves(self.row['condition_ast'])), set(self.contextual) | {self.elapsed, self.absent})

    def facts(self, *, events=None, complete=True):
        facts = {(self.row['provision_version_id'], predicate): value for predicate, value in self.contextual.items()}
        facts.update(noncommencement_facts(
            self.snapshot, self.clock, self.at, prescribed_term=self.term,
            notification=datetime(2026, 9, 4, 12, tzinfo=self.zone),
            evaluated_at=datetime(2026, 9, 9, tzinfo=self.zone),
            qualifying_commencements=events or {}, commencement_records_complete=complete,
            zone=self.zone, calendar=self.calendar))
        return facts

    def result(self, facts):
        return evaluate(self.snapshot, self.consumer, self.at, facts)

    def test_qualified_clause_and_proven_noncommencement_require_the_direction(self):
        self.assertEqual(self.result(self.facts()).effect, self.required)

    def test_missing_notice_remains_unknown_despite_a_calculated_boundary(self):
        facts = self.facts()
        del facts[(self.row['provision_version_id'], self.notified)]
        self.assertIsNone(self.result(facts).truth)
        self.assertIsNone(self.result(facts).effect)

    def test_false_or_unestablished_clause_form_cannot_be_supplied_by_elapsed_time(self):
        for value, expected in ((False, self.not_established), (None, None)):
            with self.subTest(recognized=value):
                facts = self.facts()
                key = self.row['provision_version_id'], self.recognized
                if value is None:
                    del facts[key]
                else:
                    facts[key] = value
                self.assertEqual(self.result(facts).effect, expected)

    def test_known_earlier_commencement_defeats_the_condition_with_incomplete_history(self):
        facts = self.facts(events={'qualified-early-start': datetime(2026, 9, 3, tzinfo=self.zone)}, complete=False)
        self.assertEqual(self.result(facts).effect, self.not_established)

    def test_incomplete_history_cannot_prove_noncommencement(self):
        result = self.result(self.facts(complete=False))
        self.assertIsNone(result.truth)
        self.assertIsNone(result.effect)

    def test_unregistered_source_context_is_preserved_by_ordinary_candidate_arithmetic(self):
        resolved = self.snapshot.quantity(self.clock, self.at, prescribed_term=self.term)
        self.assertIs(resolved['prescribed_term'], self.term)
        self.assertEqual((resolved['magnitude'], resolved['unit']), ('3', 'calendar_days'))
        boundary = clock_boundary(self.snapshot, self.clock, self.at, date(2026, 9, 4),
                                  prescribed_term=self.term, zone=self.zone, calendar=self.calendar)
        self.assertEqual(boundary, datetime(2026, 9, 8, tzinfo=self.zone))

    def test_commencement_and_coercive_lawfulness_are_independent_guards(self):
        for guard in (self.lawful_commencement, self.lawful_coercion):
            for value, expected in ((False, self.not_established), (None, None)):
                with self.subTest(guard=guard, value=value):
                    facts = self.facts()
                    key = self.row['provision_version_id'], guard
                    if value is None:
                        del facts[key]
                    else:
                        facts[key] = value
                    self.assertEqual(self.result(facts).effect, expected)


if __name__ == '__main__':
    unittest.main()
