"""Supply the evidenced national baseline; C owns counting conventions."""
from datetime import date
from pathlib import Path
import json

from cordon_c.temporal import WorkingCalendar


def national_calendar() -> WorkingCalendar:
    data = json.loads((Path(__file__).resolve().parents[1] / 'calendar.json').read_text())
    start, end = date.fromisoformat(data['start']), date.fromisoformat(data['end_exclusive'])
    holidays = set()
    for rule in data['fixed_rules']:
        first = date.fromisoformat(rule['effective_from'])
        for year in range(start.year, end.year + 1):
            day = date(year, rule['month'], rule['day'])
            if max(start, first) <= day < end:
                holidays.add(day)
    holidays.update(date.fromisoformat(day) for day in data['easter_mondays'])
    return WorkingCalendar(start, end, frozenset(holidays), frozenset({5, 6}))
