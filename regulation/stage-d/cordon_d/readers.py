"""Read original observations with source occurrence and precision intact."""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook



def camp_row(path: Path, sheet: str, source_row: int) -> dict:
    if type(source_row) is not int or source_row < 2:
        raise ValueError('CAMP reference must identify a physical data row after its header')
    book = load_workbook(path, read_only=True, data_only=False)
    try:
        page = book[sheet]
        page.reset_dimensions()
        rows = page.iter_rows(values_only=True)
        header = next(rows)
        names = [str(x).strip() if x is not None else None for x in header]
        active = [x for x in names if x is not None]
        if len(active) != len(set(active)):
            raise ValueError('CAMP header contains duplicate column identities')
        for number, values in enumerate(rows, 2):
            if number == source_row:
                if len(values) > len(names) and any(x is not None for x in values[len(names):]):
                    raise ValueError('Data beyond the declared CAMP header needs source interpretation')
                result = {key: value for key, value in zip(names, values) if key is not None}
                if any(isinstance(v, str) and v.startswith('=') for v in result.values()):
                    raise ValueError('Formula cell requires an explicit source-value disposition')
                return result
        raise KeyError(f'No physical row {source_row} in {sheet}')
    finally:
        book.close()




def published_result(row: dict) -> str | None:
    raw = row.get('RISULTATO')
    if raw is None or not str(raw).strip():
        return None
    value = str(raw).strip().upper()
    if value not in {'POSITIVO', 'NEGATIVO'}:
        raise ValueError(f'Unadjudicated CAMP result label: {raw}')
    return value


def sampling_date(row: dict) -> date | None:
    """Read the CAMP date column; callers retain its source event meaning."""
    values = [row[k] for k in ('DATA_RILEVAMENTO', 'DATA_PRELIVEO', 'DATA_PRELIEVO', 'DATA_CAMPIONE')
              if row.get(k) is not None]
    if not values:
        return None
    days = {v.date() if isinstance(v, datetime) else v for v in values}
    if len(days) != 1 or type(next(iter(days))) is not date:
        raise ValueError('Sampling-date fields disagree or have unqualified precision')
    # Excel's midnight representation is a date, not an evidenced midnight event.
    return next(iter(days))




