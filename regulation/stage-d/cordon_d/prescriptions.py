"""Hold a prescription's lawful dueness to the accepted A rows that govern its instrument."""

from collections.abc import Iterable, Mapping
from datetime import date

from cordon_c.core import Evaluation, Snapshot


def lawfully_due(snapshot: Snapshot, at: date, *, instrument: str, governing_references: Iterable[str],
                 results: Mapping[str, Evaluation], reading: bool) -> Evaluation:
    """Return the reading of lawful dueness only once every governing A row is reached and resolved.

    `governing_references` is the `case-prescription` record's field. The governing
    A rows in force are those of the order's instrument and every correction or
    supplement whose `corrects_instrument_ids` names it. A governing row the record
    does not reach, or a reached row without a resolved result, leaves lawful
    dueness unknown. D adds no condition.
    """
    day = at.isoformat()
    required = {sid for sid, rows in snapshot.stable.items() for row in rows
                if (row["instrument_id"] == instrument or instrument in row.get("corrects_instrument_ids", ()))
                and row["effective_from"] <= day
                and (not row["effective_to_exclusive"] or day < row["effective_to_exclusive"])}
    reached = set(governing_references)
    needs = {f"governing A reference: {sid}" for sid in required - reached}
    needs |= {f"result of {sid}" for sid in reached if sid not in results or results[sid].truth is None}
    return Evaluation(None, needs=frozenset(needs)) if needs else Evaluation(reading)
