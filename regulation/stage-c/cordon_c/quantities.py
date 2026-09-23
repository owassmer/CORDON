"""Bind accepted B quantities to mathematics, without copying source magnitudes.

These functions calculate a component. A still determines applicability and the
legal result. In particular, computing a conflict-retained month window does not
make that window a permission to omit treatment.
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from .core import Evaluation, MissingInput, Snapshot
from .temporal import WorkingCalendar, add_months, deadline, elapsed_hours, end_of_day, month_window, utc, recurrence_coverage, ordering, interval_coverage


def scalar(snapshot: Snapshot, identity: str, at: date) -> Decimal:
    row = snapshot.quantity(identity, at)
    value = row.get("value", row.get("magnitude"))
    if not isinstance(value, str):
        raise TypeError("This quantity has no scalar magnitude")
    return Decimal(value)


def metres(snapshot: Snapshot, identity: str, at: date) -> Decimal:
    row = snapshot.quantity(identity, at)
    if row["unit"] not in {"m", "km"}:
        raise TypeError("Distance parameter required")
    return scalar(snapshot, identity, at) * (1000 if row["unit"] == "km" else 1)


def in_source_month_window(snapshot: Snapshot, identity: str, at: date, event_day: date) -> bool:
    row = snapshot.quantity(identity, at)
    if row["unit"] != "month":
        raise TypeError("Month-window parameter required")
    value = row["value"]
    return month_window(event_day, int(value["from_month"]), int(value["to_month"]))


def compare_scalar(snapshot: Snapshot, identity: str, at: date, observed: Decimal) -> bool:
    """Compare in the source unit. Spatial membership uses spatial.py instead."""
    if not isinstance(observed, Decimal) or not observed.is_finite():
        raise TypeError("Finite Decimal measurement in the source unit required")
    row = snapshot.quantity(identity, at)
    value = scalar(snapshot, identity, at)
    comparator = row["comparator"]
    if comparator is None:
        raise ValueError("Source does not define a scalar comparison")
    return {"<": observed < value, "<=": observed <= value, "=": observed == value,
            ">=": observed >= value, ">": observed > value}[comparator]


def planned_workload_difference(snapshot: Snapshot, identity: str, at: date,
                                samples: int, tests: int) -> tuple[int, int]:
    if any(type(n) is not int or n < 0 for n in (samples, tests)):
        raise ValueError("Nonnegative sample and test counts required")
    row = snapshot.quantity(identity, at)
    if row["unit"] != "count":
        raise TypeError("Workload parameter required")
    return int(row["value"]["samples"]) - samples, int(row["value"]["tests"]) - tests


def planned_sample_difference(snapshot: Snapshot, identity: str, at: date, samples: int) -> int:
    if type(samples) is not int or samples < 0:
        raise ValueError("Nonnegative completed sample count required")
    row = snapshot.quantity(identity, at)
    if row["unit"] != "count" or row["kind"] != "design_target" or not isinstance(row["value"], str):
        raise TypeError("A source sample-workload target is required")
    return int(row["value"]) - samples


@dataclass(frozen=True)
class PeriodRule:
    """Selected operative counting convention, not an operator-facing option."""
    roll_final_day: bool
    two_working_days: bool = False


def operative_period_rule(identity: str, calendar: WorkingCalendar | None) -> tuple[PeriodRule, WorkingCalendar | None]:
    """C's selected clock classes; holiday evidence remains a bounded D input.

    Saturday is excluded for working-day counting, EU periods and the owner’s
    procedural submission. It is not
    declared a universal holiday for Italian administrative deadlines.
    """
    groups = json.loads((Path(__file__).parents[1] / "calendar-rules.json").read_text())
    matches = [name for name, identities in groups.items() if identity in identities]
    if len(matches) != 1:
        raise MissingInput(f"{identity}: adjudicated calendar-counting rule")
    name = matches[0]
    if name == "calendar_duration":
        return PeriodRule(False), calendar
    if name not in {"eu_period", "italian_deadline", "italian_procedural_submission", "working_days"}:
        raise ValueError("This clock is not a calendar period")
    if calendar is None:
        raise MissingInput(f"{identity}: applicable bounded holiday calendar")
    weekends = frozenset({6}) if name == "italian_deadline" else frozenset({5,6})
    selected = WorkingCalendar(calendar.start, calendar.end_exclusive, calendar.holidays, weekends)
    return PeriodRule(True, name == "eu_period"), selected


def clock_boundary(snapshot: Snapshot, identity: str, at: date, anchor: date | datetime,
                   *, zone: ZoneInfo, calendar: WorkingCalendar | None = None,
                   rule: PeriodRule | None = None,
                   stated_term: tuple[str, str] | None = None) -> datetime:
    """`stated_term` is the (number, printed unit word) the instrument states.

    It is read only for a magnitude B reserves to that instrument. A missing
    term is unknown, never a default; a stated term cannot replace a fixed one.
    """
    row = snapshot.quantity(identity, at)
    kind, unit = row["kind"], row["unit"]
    reserved = row.get("magnitude") if isinstance(row.get("magnitude"), dict) else None
    if reserved is None and stated_term is not None:
        raise ValueError(f"{identity}: B fixes this period; a stated term cannot replace it")
    if reserved is not None and stated_term is None:
        raise MissingInput(f"{identity}: the term the {reserved['reserved_to']} states")
    if kind == "same_calendar_day":
        day = utc(anchor).astimezone(zone).date() if isinstance(anchor, datetime) else anchor
        return end_of_day(day, zone)
    if kind in {"promptness_standard", "ordering_constraint", "recurrence"}:
        raise MissingInput(f"{identity}: operative timing/period input ({row['anchor']})")
    if reserved is None:
        magnitude = scalar(snapshot, identity, at)
    else:
        number, word = stated_term
        unit = snapshot.conventions["clock.unit_words"].get(" ".join(word.lower().split()))
        if unit is None or not number.isdigit():
            raise MissingInput(f"{identity}: stated term {number} {word} in a unit B maps")
        magnitude = Decimal(number)
    if magnitude != int(magnitude):
        raise ValueError("Fractional source period needs a specific counting rule")
    magnitude = int(magnitude)
    if unit == "hours":
        if not isinstance(anchor, datetime):
            raise MissingInput(f"{identity}: anchor time, not just its date")
        return elapsed_hours(anchor, magnitude)
    day = utc(anchor).astimezone(zone).date() if isinstance(anchor, datetime) else anchor
    if kind == "lookback_window":
        if unit not in {"months", "years"}:
            raise ValueError("Unsupported lookback unit")
        return datetime.combine(add_months(day, -magnitude * (12 if unit == "years" else 1)), datetime.min.time(), zone)
    if rule is None:
        rule, calendar = operative_period_rule(identity, calendar)
    last = deadline(day, magnitude, unit, calendar=calendar,
                    roll_forward=rule.roll_final_day,
                    minimum_working_days=2 if rule.two_working_days and (unit != "calendar_days" or magnitude >= 2) else 0)
    return end_of_day(last, zone)


def before_boundary(event: datetime, exclusive_end: datetime) -> bool:
    return utc(event) < utc(exclusive_end)


def threshold_reached(event: datetime, inclusive_start: datetime) -> bool:
    return utc(event) >= utc(inclusive_start)


def timely_completion(snapshot: Snapshot, identity: str, at: date, *,
                        anchor: date | datetime, completed_at: datetime | None,
                        evaluated_at: datetime, completion_history_complete: bool,
                        zone: ZoneInfo, calendar: WorkingCalendar | None = None,
                        rule: PeriodRule | None = None) -> Evaluation:
    """Whether this clock's own qualifying performance occurred in time.

    The event must satisfy B's exact completion and anchor meanings. This is
    not downstream legal operativity or performance of a different duty.
    Before expiry, an unperformed deadline is still open; after expiry, absence
    is established only from a complete performance history. Early performance
    is not rejected by a generic lower bound absent a source requirement.
    """
    row = snapshot.quantity(identity, at)
    if row["kind"] not in {"deadline", "same_calendar_day"}:
        raise ValueError("A deadline or same-day completion clock is required")
    boundary = clock_boundary(snapshot, identity, at, anchor, zone=zone,
                               calendar=calendar, rule=rule)
    through = utc(evaluated_at)
    if completed_at is not None:
        completed = utc(completed_at)
        if completed > through:
            raise ValueError("Performance cannot be later than evaluation")
        if row["kind"] == "same_calendar_day":
            day = utc(anchor).astimezone(zone).date() if isinstance(anchor, datetime) else anchor
            return Evaluation(completed.astimezone(zone).date() == day)
        # Elapsed-hour boundaries are instants; exact equality meets 'within'.
        # Whole-day boundaries are following midnight, hence exclusive.
        return Evaluation(completed <= utc(boundary) if row["unit"] == "hours" else completed < utc(boundary))
    expired = through > utc(boundary) if row["unit"] == "hours" else through >= utc(boundary)
    if expired and completion_history_complete:
        return Evaluation(False)
    need = "qualifying completion before the still-open deadline" if not expired else "complete performance history through the deadline"
    return Evaluation(None, needs=frozenset({f"{identity}: {need}"}))


def fixed_recurrence_date(snapshot: Snapshot, identity: str, at: date, due_year: int) -> date:
    row = snapshot.quantity(identity, at)
    due = row["recurrence"]["calendar_deadline"] if row["kind"] == "recurrence" else None
    if due is None:
        raise MissingInput(f"{identity}: no fixed source recurrence deadline")
    return date(due_year, int(due["month"]), int(due["day"]))


def continuous_duration_support(snapshot: Snapshot, identity: str, at: date, *,
                                 anchor: date | datetime, required_start: datetime,
                                 intervals, evaluated_at: datetime, records_complete: bool,
                                 zone: ZoneInfo, calendar: WorkingCalendar | None = None,
                                 rule: PeriodRule | None = None) -> Evaluation:
    """Continuous performance where the operative duty actually requires it.

    This does not turn a survey follow-up duration into continuous observation.
    Its consumer must require continuity (for example consecutive publication).
    required_start preserves the separately established counting convention.
    """
    row = snapshot.quantity(identity, at)
    if row["kind"] != "minimum_duration":
        raise ValueError("Minimum-duration clock required")
    try:
        end = clock_boundary(snapshot, identity, at, anchor, zone=zone,
                             calendar=calendar, rule=rule)
    except MissingInput as error:
        return Evaluation(None, needs=frozenset({str(error)}))
    return interval_coverage(required_start, end, intervals,
                             evaluated_at=evaluated_at, records_complete=records_complete)


def clock_recurrence_coverage(snapshot: Snapshot, identity: str, at: date, periods, performances, *, records_complete: bool) -> bool:
    row = snapshot.quantity(identity, at)
    if row["kind"] != "recurrence":
        raise TypeError("Recurrence clock required")
    occurrences = row["recurrence"]["occurrences_per_period"]
    if occurrences is None and row["recurrence"]["period"] is None:
        raise MissingInput(f"{identity}: operative timing and occurrence requirement")
    return recurrence_coverage(periods, performances, records_complete=records_complete,
                               required_count=int(occurrences["count"]) if occurrences else 1)


def clock_ordering(snapshot: Snapshot, identity: str, at: date, performance: datetime, anchor: datetime, **qualifications) -> bool:
    row = snapshot.quantity(identity, at)
    if row["kind"] != "ordering_constraint":
        raise TypeError("Ordering clock required")
    return ordering(row["relation"], performance, anchor, **qualifications)
