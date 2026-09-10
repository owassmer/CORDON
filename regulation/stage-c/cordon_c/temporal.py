"""Calendar operations. A/B own anchors and consequences; C selects counting.

Intervals use an exclusive end, avoiding invented microsecond precision. Working
calendars are bounded inputs: an absent holiday file is never an empty calendar.
"""

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from collections.abc import Mapping

from .core import Evaluation, MissingInput


def add_months(day: date, months: int) -> date:
    if type(day) is not date or type(months) is not int:
        raise TypeError("Calendar date and integer months required")
    y, m = divmod(day.year * 12 + day.month - 1 + months, 12)
    return date(y, m + 1, min(day.day, monthrange(y, m + 1)[1]))


def utc(instant: datetime) -> datetime:
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("An instant requires an explicit timezone")
    result = instant.astimezone(timezone.utc)
    if result.astimezone(instant.tzinfo).replace(tzinfo=None) != instant.replace(tzinfo=None):
        raise ValueError("Nonexistent local time")
    return result


def elapsed_hours(anchor: datetime, hours: int) -> datetime:
    if type(hours) is not int:
        raise TypeError("Integer source hours required")
    return (utc(anchor) + timedelta(hours=hours)).astimezone(anchor.tzinfo)


@dataclass(frozen=True)
class WorkingCalendar:
    start: date
    end_exclusive: date
    holidays: frozenset[date]
    weekend: frozenset[int]

    def __post_init__(self):
        if self.start >= self.end_exclusive or not self.weekend <= set(range(7)) or len(self.weekend) == 7:
            raise ValueError("Invalid working calendar")
        if any(not self.start <= d < self.end_exclusive for d in self.holidays):
            raise ValueError("Holiday outside supplied calendar coverage")

    def working(self, day: date) -> bool:
        if not self.start <= day < self.end_exclusive:
            raise MissingInput(f"working calendar for {day}")
        return day.weekday() not in self.weekend and day not in self.holidays


def working_days_after(anchor: date, count: int, calendar: WorkingCalendar) -> date:
    if type(count) is not int or count < 0:
        raise ValueError("Nonnegative integer working-day count required")
    day = anchor
    while count:
        day += timedelta(days=1)
        count -= calendar.working(day)
    return day


def end_of_day(day: date, zone: ZoneInfo) -> datetime:
    """Exclusive end of the whole local day, including daylight-saving changes."""
    return datetime.combine(day + timedelta(days=1), time(), zone)


def deadline(anchor: date, magnitude: int, unit: str, *,
             calendar: WorkingCalendar | None, roll_forward: bool,
             minimum_working_days: int = 0) -> date:
    """Return the inclusive final date; exclude the event day.

    For Article 3 of 1182/71, select roll_forward and (for periods >=2 days)
    minimum_working_days=2. These are not defaults for every Italian clock.
    Entry/effect/expiry under Article 4 does not receive those extensions.
    """
    if type(anchor) is not date or type(magnitude) is not int or magnitude < 1:
        raise ValueError("Positive whole period and event date required")
    if minimum_working_days < 0:
        raise ValueError("Invalid minimum working days")
    if (roll_forward or minimum_working_days or unit == "working_days") and calendar is None:
        raise MissingInput("applicable working calendar")
    if unit == "working_days":
        last = working_days_after(anchor, magnitude, calendar)
    elif unit == "calendar_days":
        last = anchor + timedelta(days=magnitude)
    elif unit in {"months", "years"}:
        last = add_months(anchor, magnitude * (12 if unit == "years" else 1))
    else:
        raise ValueError(f"Unsupported date period: {unit}")
    if minimum_working_days:
        last = max(last, working_days_after(anchor, minimum_working_days, calendar))
    if roll_forward:
        while not calendar.working(last):
            last += timedelta(days=1)
    return last


def month_window(day: date, first: int, last: int) -> bool:
    if not 1 <= first <= 12 or not 1 <= last <= 12:
        raise ValueError("Month outside 1..12")
    return first <= day.month <= last if first <= last else day.month >= first or day.month <= last


def no_detection_anchor(established: date, detections: tuple[date, ...],
                        through: date, *, detection_record_complete: bool) -> date:
    if through < established or any(d > through for d in detections):
        raise ValueError("Detection history and decision interval disagree")
    if not detection_record_complete:
        raise MissingInput("complete detection history through the evaluation date")
    return max((established, *detections))


def recurrence_coverage(periods: tuple[tuple[date, date], ...],
                        qualifying_performances: Mapping[str, date], *,
                        records_complete: bool, required_count: int = 1) -> bool:
    """Count only performances already qualified for the required population/method."""
    if not periods or any(a >= b for a, b in periods) or type(required_count) is not int or required_count < 1:
        raise ValueError("Invalid recurrence period")
    covered = all(sum(a <= d < b for d in qualifying_performances.values()) >= required_count for a, b in periods)
    if covered:
        return True
    if not records_complete:
        raise MissingInput("qualifying performance history for uncovered recurrence periods")
    return False


def occurrence_in_window(performances: Mapping[str, datetime], start: datetime,
                         end_exclusive: datetime, *, records_complete: bool) -> bool:
    start, end = utc(start), utc(end_exclusive)
    if start >= end:
        raise ValueError("Nonempty performance interval required")
    if any(start <= utc(t) < end for t in performances.values()):
        return True
    if not records_complete:
        raise MissingInput("complete qualifying performance history for the interval")
    return False


def interval_coverage(start: datetime, end_exclusive: datetime,
                      intervals: Mapping[str, tuple[datetime, datetime | None]], *,
                      evaluated_at: datetime, records_complete: bool) -> Evaluation:
    """Continuous qualified performance throughout a required interval.

    Adjacent or overlapping records may prove the same continuous performance.
    An open record is established only through evaluation, never into the
    future. Missing records differ from a proven past interruption. Interval
    identities and qualifications follow the exact duty supplied by the caller.
    """
    start, end, through = utc(start), utc(end_exclusive), utc(evaluated_at)
    if start >= end:
        raise ValueError("Nonempty required interval required")
    spans = []
    for beginning, ending in intervals.values():
        a, b = utc(beginning), utc(ending) if ending is not None else through
        if a > through or b > through or a > b:
            raise ValueError("Performed intervals must be ordered and no later than evaluation")
        spans.append((a, b))
    cursor = start
    for a, b in sorted(spans):
        if b <= cursor:
            continue
        if a > cursor:
            break
        cursor = max(cursor, b)
        if cursor >= end:
            return Evaluation(True)
    if records_complete and cursor < min(end, through):
        return Evaluation(False)
    need = ("continued qualifying performance through the required interval"
            if cursor >= through else "continuous performance evidence for the uncovered interval")
    return Evaluation(None, needs=frozenset({need}))


def precedes(first: datetime, second: datetime, *, equality_allowed: bool) -> bool:
    return utc(first) <= utc(second) if equality_allowed else utc(first) < utc(second)


def calendar_periods(first_year: int, first_month: int, count: int, months_per_period: int) -> tuple[tuple[date, date], ...]:
    if count < 1 or months_per_period < 1:
        raise ValueError("Positive number and length of periods required")
    origin = date(first_year, first_month, 1)
    return tuple((add_months(origin, i * months_per_period), add_months(origin, (i + 1) * months_per_period))
                 for i in range(count))


def ordering(relation: str, performance: datetime, anchor: datetime, *,
             during_phase_performed: bool | None = None,
             as_close_as_practicable: bool | None = None,
             next_campaign: tuple[datetime, datetime] | None = None) -> bool:
    before, after = utc(performance) < utc(anchor), utc(performance) > utc(anchor)
    if relation == "before":
        return before
    if relation == "after":
        return after
    if relation == "before_and_during":
        if not before:
            return False
        if during_phase_performed is None:
            raise MissingInput("required treatment performed during the removal phase")
        return during_phase_performed
    if relation == "as_close_as_practicable_before":
        if not before:
            return False
        if as_close_as_practicable is None:
            raise MissingInput("operative practicability assessment")
        return as_close_as_practicable
    if relation == "in_next_campaign_after":
        if next_campaign is None:
            raise MissingInput("next operative campaign interval")
        start, end = map(utc, next_campaign)
        if not utc(anchor) < start < end:
            raise ValueError("Campaign does not follow the triggering event")
        return start <= utc(performance) < end
    raise ValueError(f"Unknown source ordering relation: {relation}")
