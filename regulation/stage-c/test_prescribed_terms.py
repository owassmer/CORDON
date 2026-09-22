"""Source-period arithmetic in explicit fixtures, independent of accepted owners."""

import copy
from dataclasses import FrozenInstanceError, replace
from datetime import date, datetime, timedelta
from decimal import Decimal
import unittest
from zoneinfo import ZoneInfo

from cordon_c import Evaluation, MissingInput, PrescribedTerm, Snapshot, evaluate
from cordon_c.bindings import noncommencement_facts
from cordon_c.quantities import clock_boundary, PeriodRule, scalar, timely_completion
from cordon_c.temporal import WorkingCalendar


AT = date(2026, 9, 8)
ROME = ZoneInfo("Europe/Rome")
CLOCK = "fixture-prescribed-deadline"
ELAPSED = "the source notification-based commencement deadline has elapsed"
ABSENT = "noncommencement of that work by the source deadline is established"


def snapshot_fixture(**clock_changes):
    provision = dict(provision_version_id="fixture:v1", stable_provision_id="fixture",
                     effective_from="2020-01-01", effective_to_exclusive="",
                     semantic_change="YES", condition_ast={"all_of": [
                         {"predicate": ELAPSED}, {"predicate": ABSENT}]},
                     true_effect="TEMPORAL_CONDITION_ESTABLISHED", false_effect="NOT_ESTABLISHED")
    clock = dict(clock_id=CLOCK, producer_provision_version_id="fixture:v1",
                 consumer_decision="fixture", kind="deadline", bound="exact",
                 magnitude={"source_input": "prescribed-term"}, unit=None,
                 anchor={"kind": "event", "event": "notification"},
                 completion={"kind": "record", "ref": "concrete commencement of specified work"})
    clock.update(clock_changes)
    return Snapshot([provision], dict(clocks=[clock], parameters=[], dispositions=[]))


def term(**changes):
    return replace(PrescribedTerm("unseen-order-873", "clause-4", "recipient-Z",
                                  "specified-removal-work-Z", Decimal("3"), "calendar_days"), **changes)


class PrescribedTerms(unittest.TestCase):
    def setUp(self):
        self.snapshot = snapshot_fixture()
        self.calendar = WorkingCalendar(date(2024, 1, 1), date(2029, 1, 1),
                                        frozenset(), frozenset({5, 6}))

    def boundary(self, prescribed_term, anchor=date(2026, 9, 4), **kwargs):
        return clock_boundary(self.snapshot, CLOCK, AT, anchor, zone=ROME,
                              calendar=self.calendar, prescribed_term=prescribed_term, **kwargs)

    def facts(self, prescribed_term, *, evaluated_at=datetime(2026, 9, 9, tzinfo=ROME),
              events=None, complete=True, notification=datetime(2026, 9, 4, 12, tzinfo=ROME)):
        return noncommencement_facts(self.snapshot, CLOCK, AT, notification=notification,
                                    evaluated_at=evaluated_at, qualifying_commencements=events or {},
                                    commencement_records_complete=complete, zone=ROME,
                                    calendar=self.calendar, prescribed_term=prescribed_term)

    def test_unseen_source_context_is_retained_without_changing_the_owner(self):
        original = copy.deepcopy(self.snapshot.clocks[CLOCK])
        actual = term(document="another-unregistered-order", clause="annex-A:paragraph-9",
                      recipient="unseen-recipient", commencement_work="unseen-work", magnitude=Decimal("7"))
        resolved = self.snapshot.quantity(CLOCK, AT, prescribed_term=actual)
        self.assertIs(resolved["prescribed_term"], actual)
        self.assertEqual((resolved["magnitude"], resolved["unit"]), ("7", "calendar_days"))
        self.assertEqual(scalar(self.snapshot, CLOCK, AT, prescribed_term=actual), Decimal("7"))
        resolved["magnitude"] = "99"
        self.assertEqual(self.snapshot.clocks[CLOCK], original)
        self.assertEqual(self.snapshot.quantity(CLOCK, AT, prescribed_term=term())["magnitude"], "3")
        with self.assertRaises(FrozenInstanceError):
            actual.recipient = "other-recipient"

    def test_missing_untyped_and_unsupported_source_terms_are_rejected(self):
        with self.assertRaises(MissingInput):
            self.snapshot.quantity(CLOCK, AT)
        with self.assertRaises(TypeError):
            self.snapshot.quantity(CLOCK, AT, prescribed_term={"magnitude": "3", "unit": "calendar_days"})
        for changes in [dict(magnitude={"source_input": "another-input"}),
                        dict(magnitude={"source_input": "prescribed-term", "default": "10"}),
                        dict(kind="minimum_duration"), dict(bound="at_least"), dict(unit="calendar_days")]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                snapshot_fixture(**changes).quantity(CLOCK, AT, prescribed_term=term())

    def test_invalid_source_magnitudes_units_and_context_are_rejected(self):
        for value in [Decimal("0"), Decimal("-2"), Decimal("NaN"), Decimal("sNaN"),
                      Decimal("Infinity"), Decimal("-Infinity"), Decimal("1.5")]:
            with self.subTest(magnitude=value), self.assertRaises(ValueError):
                term(magnitude=value)
        for value in [3, "3", 3.0, True]:
            with self.subTest(magnitude=value), self.assertRaises(TypeError):
                term(magnitude=value)
        for value in ["days", "m", "", None]:
            with self.subTest(unit=value), self.assertRaises(ValueError):
                term(unit=value)
        for field in ["document", "clause", "recipient", "commencement_work"]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                term(**{field: " "})

    def test_a_source_term_cannot_override_a_fixed_clock(self):
        fixed = snapshot_fixture(magnitude="10", unit="calendar_days")
        self.assertIs(fixed.quantity(CLOCK, AT), fixed.clocks[CLOCK])
        self.assertEqual(scalar(fixed, CLOCK, AT), Decimal("10"))
        for consumer in [
                lambda: fixed.quantity(CLOCK, AT, prescribed_term=term()),
                lambda: clock_boundary(fixed, CLOCK, AT, date(2026, 9, 4), zone=ROME,
                                       calendar=self.calendar, prescribed_term=term())]:
            with self.assertRaises(ValueError):
                consumer()
        # An unregistered fixed clock still needs its own accepted calendar rule.
        with self.assertRaises(MissingInput):
            clock_boundary(fixed, CLOCK, AT, date(2026, 9, 4), zone=ROME, calendar=self.calendar)

    def test_producer_and_event_date_checks_still_apply(self):
        with self.assertRaises(MissingInput):
            self.snapshot.quantity(CLOCK, date(2019, 12, 31), prescribed_term=term())
        self.snapshot.versions["fixture:v1"]["effective_to_exclusive"] = "2026-09-08"
        with self.assertRaises(MissingInput):
            self.snapshot.quantity(CLOCK, AT, prescribed_term=term())
        with self.assertRaises(KeyError):
            snapshot_fixture(producer_provision_version_id="absent:v1").quantity(CLOCK, AT,
                                                                                prescribed_term=term())

    def test_actual_period_changes_the_boundary_and_noncommencement_result(self):
        self.assertEqual(self.boundary(term()), datetime(2026, 9, 8, tzinfo=ROME))
        self.assertEqual(self.boundary(term(magnitude=Decimal("7"))), datetime(2026, 9, 12, tzinfo=ROME))
        self.assertTrue(evaluate(self.snapshot, "fixture", AT, self.facts(term())).truth)
        self.assertFalse(evaluate(self.snapshot, "fixture", AT, self.facts(term(magnitude=Decimal("7")))).truth)
        self.assertIsNone(evaluate(self.snapshot, "fixture", AT, self.facts(term(), complete=False)).truth)

    def test_earlier_commencement_and_incomplete_history_remain_distinct(self):
        early = {"before-notice": datetime(2026, 9, 3, tzinfo=ROME)}
        self.assertFalse(evaluate(self.snapshot, "fixture", AT,
                                 self.facts(term(), events=early, complete=False)).truth)
        at_midnight = {"too-late": datetime(2026, 9, 8, tzinfo=ROME)}
        self.assertTrue(evaluate(self.snapshot, "fixture", AT,
                                self.facts(term(), events=at_midnight)).truth)
        with self.assertRaises(ValueError):
            self.facts(term(), events={"future": datetime(2026, 9, 10, tzinfo=ROME)})

    def test_execution_days_roll_sunday_and_holidays_but_not_saturday(self):
        self.assertEqual(self.boundary(term(magnitude=Decimal("1"))), datetime(2026, 9, 6, tzinfo=ROME))
        self.assertEqual(self.boundary(term(magnitude=Decimal("2"))), datetime(2026, 9, 8, tzinfo=ROME))
        self.calendar = replace(self.calendar, holidays=frozenset({date(2026, 9, 7)}))
        self.assertEqual(self.boundary(term(magnitude=Decimal("2"))), datetime(2026, 9, 9, tzinfo=ROME))

    def test_working_days_months_and_years_reuse_their_counting_conventions(self):
        self.assertEqual(self.boundary(term(magnitude=Decimal("1"), unit="working_days")),
                         datetime(2026, 9, 8, tzinfo=ROME))
        self.assertEqual(self.boundary(term(magnitude=Decimal("1"), unit="months"), date(2026, 1, 31)),
                         datetime(2026, 3, 1, tzinfo=ROME))
        self.assertEqual(self.boundary(term(magnitude=Decimal("1"), unit="years"), date(2024, 2, 29)),
                         datetime(2025, 3, 1, tzinfo=ROME))

    def test_elapsed_hours_preserve_exact_boundary_and_daylight_saving_time(self):
        actual = term(magnitude=Decimal("24"), unit="hours")
        notification = datetime(2026, 3, 28, 18, tzinfo=ROME)
        end = datetime(2026, 3, 29, 19, tzinfo=ROME)
        self.assertEqual(clock_boundary(self.snapshot, CLOCK, AT, notification, zone=ROME,
                                        prescribed_term=actual), end)
        result = timely_completion(self.snapshot, CLOCK, AT, anchor=notification,
                                   completed_at=end, evaluated_at=end, completion_history_complete=False,
                                   zone=ROME, prescribed_term=actual)
        self.assertTrue(result.truth)
        facts = self.facts(actual, notification=notification, evaluated_at=end)
        self.assertFalse(facts[("fixture:v1", ELAPSED)])
        self.assertIsInstance(facts[("fixture:v1", ABSENT)], Evaluation)
        just_after = end + timedelta(microseconds=1)
        facts = self.facts(actual, notification=notification, evaluated_at=just_after,
                           events={"at-boundary": end}, complete=False)
        self.assertFalse(facts[("fixture:v1", ABSENT)])
        self.assertTrue(evaluate(self.snapshot, "fixture", AT,
                                self.facts(actual, notification=notification, evaluated_at=just_after)).truth)

    def test_source_bound_counting_cannot_be_overridden_or_left_unresolved(self):
        for actual in [term(), term(unit="hours")]:
            with self.subTest(unit=actual.unit), self.assertRaises(ValueError):
                self.boundary(actual, datetime(2026, 9, 4, tzinfo=ROME), rule=PeriodRule(False))
        with self.assertRaises(MissingInput):
            clock_boundary(self.snapshot, CLOCK, AT, date(2026, 9, 4), zone=ROME, prescribed_term=term())
        with self.assertRaises(MissingInput):
            clock_boundary(self.snapshot, CLOCK, AT, date(2026, 9, 4), zone=ROME,
                           prescribed_term=term(unit="hours"))


if __name__ == "__main__":
    unittest.main()
