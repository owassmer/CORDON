"""Hold a prescription's lawful dueness to the accepted A rows that govern its instrument."""

from collections.abc import Iterable, Mapping
from datetime import date

from cordon_c.core import Evaluation, Snapshot, evaluate

# The Art. 21-ter rule's two dueness predicates: the commencement work due from this recipient, and the
# population the prescription names for coercion.
WORK = "the commencement work the prescription states is lawfully due from this recipient"
COERCE = "removal of the population the prescription names for coercion is lawfully due"
# The two generic consequences a governing row's result may state for the population in question.
NOT_DUE = "POPULATION_NOT_LAWFULLY_DUE"
IN_PART = "LAWFULLY_DUE_IN_PART"


def required_rows(snapshot: Snapshot, at: date, instrument: str) -> set[str]:
    """Governing A rows in force at `at`: the instrument's own and every row whose
    `corrects_instrument_ids` names it."""
    day = at.isoformat()
    return {sid for sid, rows in snapshot.stable.items() for row in rows
            if (row["instrument_id"] == instrument or instrument in row.get("corrects_instrument_ids", ()))
            and row["effective_from"] <= day
            and (not row["effective_to_exclusive"] or day < row["effective_to_exclusive"])}


def lawfully_due(snapshot: Snapshot, at: date, *, instrument: str, governing_references: Iterable[str],
                 results: Mapping[tuple[str, str], Evaluation], reading: bool | None, predicate: str,
                 positioned: bool = False, cohort: Iterable[str] = ()) -> Evaluation:
    """The reading of lawful dueness for `predicate`, held to every governing A row.

    `governing_references` is the `case-prescription` record's field. `results` holds a
    governing row's result per (row, predicate); only this predicate's are read. Effects
    and needs come only from rows that are both required (in force, and the record's
    instrument or named in `corrects_instrument_ids`) and reached. A required row the
    record does not reach names itself. A reached row without a resolved result for this
    predicate passes its own needs through (the supplied result's, else those of the row
    evaluated with no facts), so the need names the row's predicate. With every required
    row reached and resolved:

    - a row whose effect is POPULATION_NOT_LAWFULLY_DUE makes it False, naming the row;
    - else a row whose effect is LAWFULLY_DUE_IN_PART keeps the reading and names the row
      in `provisions`; for WORK on a record that carries no annex position (`positioned`)
      it is unknown instead, naming the recipient's position in the order's annex, which
      that row limits in part: never true;
    - else the reading.

    Only these two names are read. D adds no condition and reads no row by identity.
    """
    required = required_rows(snapshot, at, instrument)
    reached = set(governing_references)
    needs = {f"governing A reference: {sid}" for sid in required - reached}
    effects = {}
    for sid in sorted(required & reached):
        result = results.get((sid, predicate))
        if result is None:
            result = evaluate(snapshot, sid, at, {})
        if result.truth is None and result.effect is None:
            needs |= result.needs or {f"result of {sid}"}
            continue
        vid = snapshot.version(sid, at)["provision_version_id"]
        effects[sid] = (result.effect, result.provisions | {vid})
    if needs:
        return Evaluation(None, needs=frozenset(needs))
    if reading is None:
        return Evaluation(None)
    withheld = [provisions for effect, provisions in effects.values() if effect == NOT_DUE]
    if withheld:
        return Evaluation(False, provisions=frozenset().union(*withheld))
    partial = {sid: provisions for sid, (effect, provisions) in effects.items() if effect == IN_PART}
    if partial and predicate == WORK and not positioned:
        printed = ", ".join(cohort) or "no cohort printed"
        return Evaluation(None, needs=frozenset(
            f"this recipient's position in {instrument}'s annex ({printed}), which {sid} limits in part"
            for sid in partial))
    return Evaluation(reading, provisions=frozenset().union(*partial.values()))
