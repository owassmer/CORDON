"""Evaluate the accepted A condition language with explicit semantic inputs.

An effect is the exact A result, including compound results. Satisfying a legal
condition does not assert that the required performance occurred. Unknown input
is distinct from a false assertion; the source's otherwise branch is not a
catch-all for missing evidence.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]


class MissingInput(Exception):
    """A named semantic input is not available for this calculation."""


@dataclass(frozen=True)
class Evaluation:
    truth: bool | None
    effect: str | None = None
    needs: frozenset[str] = frozenset()
    provisions: frozenset[str] = frozenset()

    def __post_init__(self):
        if self.truth is not None and type(self.truth) is not bool:
            raise TypeError("Truth must be an explicit boolean or unresolved")

    def __bool__(self):
        raise TypeError("Use .truth explicitly; an unresolved evaluation is not false")


def conjunction(values: list[Evaluation]) -> Evaluation:
    decisive = [v for v in values if v.truth is False]
    if decisive:
        return Evaluation(False, provisions=frozenset().union(*(v.provisions for v in decisive)))
    return Evaluation(None if any(v.truth is None for v in values) else True,
                      needs=frozenset().union(*(v.needs for v in values)),
                      provisions=frozenset().union(*(v.provisions for v in values)))


def disjunction(values: list[Evaluation]) -> Evaluation:
    decisive = [v for v in values if v.truth is True]
    if decisive:
        return Evaluation(True, provisions=frozenset().union(*(v.provisions for v in decisive)))
    return Evaluation(None if any(v.truth is None for v in values) else False,
                      needs=frozenset().union(*(v.needs for v in values)),
                      provisions=frozenset().union(*(v.provisions for v in values)))


def negation(value: Evaluation) -> Evaluation:
    return Evaluation(None if value.truth is None else not value.truth,
                      needs=value.needs, provisions=value.provisions)


def _leaves(ast: dict):
    if "predicate" in ast:
        yield ast["predicate"]
    for value in ast.values():
        if isinstance(value, dict):
            yield from _leaves(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    yield from _leaves(item)


# A wordings that ask whether the event date lies in an interval A states. Each
# names the interval's source: the carrying row's own version ("within" or
# "outside" it), or the start or end of a named A version; then the stable
# provisions carrying it (None: the wording itself names "this version").
# evaluate decides them from `at` alone, start included and end excluded.
DATE_INTERVALS = {
    "decision time within this version's effective interval": ("within", None, None),
    "decision time within programme year 2026": ("within", None, ("IT-PNI-2026:adoption-and-publication-status",)),
    "effective 2022 national plan interval": ("within", None, ("IT-DM-2022-XYLELLA-PLAN:§6.5:containment-buffer-5km",)),
    "effective plan interval": ("within", None, tuple(f"PUG-DGR{n}:Art7(3)-policy" for n in (
        "538-2021", "343-2022", "1866-2022", "1593-2024", "1075-2025"))),
    "evidence proves event outside PNI binding interval": ("outside", None, ("IT-PNI-2026:Xylella:Puglia-plant-survey-design",)),
    "post-M5 case date": ("from_start_of", "EU-2020-1201:7(1)(e):v2", tuple(
        f"REG-PUGLIA-U181-DIR-{n}:case-delta:post-m5-stale-article7-text" for n in (
            "2024-00138", "2024-00151", "2025-00115", "2026-00035"))),
    "pre-M4 event time": ("before_end_of", "REG-PUGLIA-U181-DIR-2024-00018:area-state-transition:v1", (
        "REG-PUGLIA-U181-DIR-2023-00096:case-delta:pre-m4-monopoli-eradication-fork",
        "REG-PUGLIA-U181-DIR-2024-00027:case-delta:pre-m4-containment-authority-conflict")),
}


def _date_interval(snapshot: Snapshot, row: dict, text: str, at: date, facts: Mapping,
                  reader: PredicateReader | None) -> Evaluation:
    key = row["provision_version_id"], text
    supplied = key in facts
    if not supplied and reader is not None:
        try:
            answer = reader(row, text)
        except (KeyError, MissingInput):
            answer = None
        supplied = (answer.truth if isinstance(answer, Evaluation) else answer) is not None
    if supplied:
        raise ValueError(f"C evaluates this interval from the event date; it cannot be supplied: {key}")
    kind, named, _ = DATE_INTERVALS[text]
    source, day = row if named is None else snapshot.versions[named], at.isoformat()
    if kind == "before_end_of":
        return Evaluation(day < source["effective_to_exclusive"])
    if kind == "from_start_of":
        return Evaluation(source["effective_from"] <= day)
    inside = source["effective_from"] <= day and (
        not source["effective_to_exclusive"] or day < source["effective_to_exclusive"])
    return Evaluation(inside if kind == "within" else not inside)


class Snapshot:
    """A/B owners loaded once. Instances have no mutable evaluation cache."""

    def __init__(self, provisions: list[dict], ledger: dict, reference_bindings: list[dict] = ()):
        self.versions = {r["provision_version_id"]: r for r in provisions}
        if len(self.versions) != len(provisions):
            raise ValueError("Duplicate provision version")
        self.stable: dict[str, list[dict]] = {}
        for row in provisions:
            self.stable.setdefault(row["stable_provision_id"], []).append(row)
        for rows in self.stable.values():
            rows.sort(key=lambda row: row["effective_from"])
        self.clocks = {r["clock_id"]: r for r in ledger["clocks"]}
        self.parameters = {r["parameter_id"]: r for r in ledger["parameters"]}
        self.dispositions = ledger["dispositions"]
        self.conventions = ledger.get("conventions", {})
        self.performance = {(r["consumer"], r["reference"]): r["required_fact"] for r in reference_bindings if "required_fact" in r}
        self.reference_outcomes = {(r["consumer"], r["reference"]): r["outcomes"] for r in reference_bindings if "outcomes" in r}
        self.historical_references = {(r["consumer"], r["reference"]) for r in reference_bindings if r.get("historical_result")}

    @classmethod
    def load(cls, root: Path = ROOT) -> Snapshot:
        current = json.loads((root / "state/CURRENT.json").read_text())
        stages = current["stages"]
        entries = list(stages["A"]["canonical_artifacts"].values())
        entries += [stages["B"]["canonical"], stages["B"]["population"]]
        documents = []
        for entry in entries:
            raw = (root / entry["path"]).read_bytes()
            if sha256(raw).hexdigest() != entry["sha256"]:
                raise ValueError(f"Upstream owner changed: {entry['path']}")
            documents.append(json.loads(raw))
        if stages["A"]["status"] != "CLOSED" or stages["B"]["status"] != "CLOSED":
            raise ValueError("C requires accepted upstream meaning")
        references = json.loads((root / "regulation/stage-c/reference-bindings.json").read_text())
        snapshot = cls(documents[0] + documents[1], documents[2], references)
        for text, (kind, named, carriers) in DATE_INTERVALS.items():
            carrying = {r["stable_provision_id"] for r in snapshot.versions.values() if text in set(_leaves(r["condition_ast"]))}
            if not carrying or carriers is not None and carrying != set(carriers):
                raise ValueError(f"A's carriers of an interval wording changed: {text}")
            if named is not None and (named not in snapshot.versions or kind == "before_end_of"
                                      and not snapshot.versions[named]["effective_to_exclusive"]):
                raise ValueError(f"A version naming an interval changed: {named}")
        return snapshot

    def version(self, identity: str, at: date) -> dict:
        if type(at) is not date:
            raise TypeError("Version selection requires an explicit legal event date")
        rows = ([self.versions[identity]] if identity in self.versions
                else self.stable.get(identity, []))
        candidates = [r for r in rows if r["effective_from"] <= at.isoformat()
                      and (not r["effective_to_exclusive"] or at.isoformat() < r["effective_to_exclusive"])]
        if not candidates:
            raise MissingInput(f"applicable legal version: {identity} at {at}")
        if len(candidates) != 1:
            raise ValueError(f"Overlapping legal versions: {identity} at {at}")
        row = candidates[0]
        return row

    def quantity_interval(self, row: dict) -> tuple[date, date | None]:
        producer = self.versions[row["producer_provision_version_id"]]
        versions = self.stable[producer["stable_provision_id"]]
        end = producer["effective_to_exclusive"]
        for following in versions[versions.index(producer) + 1:]:
            if following["semantic_change"].upper() != "NO":
                break
            if end != following["effective_from"]:
                raise ValueError("A quantity cannot extend over a gap in legal versions")
            end = following["effective_to_exclusive"]
        return date.fromisoformat(producer["effective_from"]), date.fromisoformat(end) if end else None

    def quantity(self, identity: str, at: date) -> dict:
        row = self.clocks.get(identity) or self.parameters.get(identity)
        if row is None:
            raise KeyError(identity)
        start, end = self.quantity_interval(row)
        if not start <= at or end is not None and at >= end:
            raise MissingInput(f"applicable clock/parameter: {identity} at {at}")
        return row

    def historical_result(self, consumer: str, reference: str, at: date,
                          results: Mapping[tuple[str, str], tuple[date, Evaluation]]) -> Evaluation:
        """Read a specifically bound antecedent result in its own event context."""
        edge = consumer, reference
        if edge not in self.historical_references:
            raise ValueError(f"Reference is not an established historical result: {edge}")
        if edge not in results:
            return Evaluation(None, needs=frozenset({f"established result of {reference} at its own legal event time"}))
        event_date, result = results[edge]
        row = self.version(reference, event_date)
        if event_date > at:
            raise ValueError("An antecedent legal result cannot follow its consumer")
        if not isinstance(result, Evaluation) or row["provision_version_id"] not in result.provisions:
            raise ValueError("Antecedent result must retain its owning event-time provision")
        ast = row["condition_ast"]
        effects = ({b["effect"] for b in ast["route_table"]} | {ast["otherwise"]["effect"]}
                   if "route_table" in ast else {row["true_effect"], row["false_effect"]})
        if result.effect is not None and result.effect not in effects:
            raise ValueError("Antecedent result effect is not owned by the referenced provision")
        return result


# A predicate identity is its owning version and exact accepted wording. C
# computations override only explicitly bound leaves; all remaining facts are
# semantic inputs for D, not guesses extracted from prose at evaluation time.
PredicateReader = Callable[[dict, str], bool | Evaluation]


def predicate_value(row: dict, text: str, facts: Mapping,
                    reader: PredicateReader | None = None) -> Evaluation:
    if text == "no additional condition":
        return Evaluation(True)
    key = row["provision_version_id"], text
    try:
        value = facts[key] if key in facts or reader is None else reader(row, text)
    except (KeyError, MissingInput) as error:
        need = str(error) if isinstance(error, MissingInput) else f"predicate: {key[0]} :: {text}"
        return Evaluation(None, needs=frozenset({need}))
    if isinstance(value, Evaluation):
        return Evaluation(value.truth, needs=value.needs, provisions=value.provisions)
    if type(value) is not bool:
        raise TypeError(f"Predicate must be true, false or explicit unresolved: {key}")
    return Evaluation(value)


def evaluate(snapshot: Snapshot, identity: str, at: date,
             facts: Mapping[tuple[str, str], bool | Evaluation] | None = None,
             reader: PredicateReader | None = None,
             performances: Mapping[tuple[str, str], bool | Evaluation] | None = None,
             historical_results: Mapping[tuple[str, str], tuple[date, Evaluation]] | None = None) -> Evaluation:
    facts = {} if facts is None else facts
    performances = {} if performances is None else performances
    historical_results = {} if historical_results is None else historical_results
    if historical_results.keys() - snapshot.historical_references:
        raise ValueError("Historical results may only supply explicitly bound antecedent references")
    cache: dict[str, Evaluation] = {}
    active: set[str] = set()

    def provision(ref: str) -> Evaluation:
        try:
            row = snapshot.version(ref, at)
        except MissingInput as error:
            return Evaluation(None, needs=frozenset({str(error)}))
        vid = row["provision_version_id"]
        if vid in cache:
            return cache[vid]
        if vid in active:
            raise ValueError(f"Circular computational dependency: {vid}")
        active.add(vid)
        value = node(row["condition_ast"], row)
        effect = value.effect
        if effect is None and value.truth is not None:
            effect = row["true_effect"] if value.truth else row["false_effect"]
            if effect in ("", "-", None):
                effect = None
        value = Evaluation(value.truth, effect, value.needs, value.provisions | {vid})
        cache[vid] = value
        active.remove(vid)
        return value

    def node(ast: dict[str, Any], row: dict) -> Evaluation:
        if ast.get("predicate") in DATE_INTERVALS:
            return _date_interval(snapshot, row, ast["predicate"], at, facts, reader)
        if "predicate" in ast:
            return predicate_value(row, ast["predicate"], facts, reader)
        if "result_ref" in ast:
            ref = ast["result_ref"]
            edge = row["stable_provision_id"], ref["producer_stable_provision_id"]
            result = (snapshot.historical_result(*edge, at, historical_results)
                      if edge in snapshot.historical_references else provision(edge[1]))
            if result.effect is None:
                return Evaluation(None, needs=result.needs, provisions=result.provisions)
            return Evaluation(result.effect == ref["allowed_effect"], provisions=result.provisions)
        if "provision_ref" in ast:
            edge = row["stable_provision_id"], ast["provision_ref"]
            if edge in snapshot.performance:
                if edge not in performances:
                    return Evaluation(None, needs=frozenset({snapshot.performance[edge]}))
                value = performances[edge]
                if isinstance(value, Evaluation):
                    return Evaluation(value.truth, needs=value.needs, provisions=value.provisions)
                if type(value) is not bool:
                    raise TypeError(f"Performance must be true, false or explicit unresolved: {edge}")
                return Evaluation(value)
            result = provision(ast["provision_ref"])
            if edge in snapshot.reference_outcomes:
                if result.effect is None:
                    return Evaluation(None, needs=result.needs, provisions=result.provisions)
                outcomes = snapshot.reference_outcomes[edge]
                if result.effect not in outcomes:
                    raise ValueError(f"Unbound referenced outcome: {edge}: {result.effect}")
                truth = outcomes[result.effect]
                return Evaluation(truth, needs=frozenset({f"{edge[1]}: {result.effect}"}) if truth is None else frozenset(), provisions=result.provisions)
            return Evaluation(result.truth, needs=result.needs, provisions=result.provisions)
        if "not" in ast:
            value = node(ast["not"], row)
            return negation(value)
        if "route_table" in ast:
            evaluated = [(branch, node(branch["when"], row)) for branch in ast["route_table"]]
            proven = [(branch, value) for branch, value in evaluated if value.truth is True]
            possible = [(branch, value) for branch, value in evaluated if value.truth is None]
            if len(proven) > 1:
                raise ValueError(f"Nonexclusive legal routes: {row['provision_version_id']}")
            if proven and all(branch["effect"] == proven[0][0]["effect"] for branch, _ in possible):
                return Evaluation(True, proven[0][0]["effect"], provisions=proven[0][1].provisions)
            if not proven and not possible:
                return Evaluation(False, ast["otherwise"]["effect"],
                                  provisions=frozenset().union(*(v.provisions for _, v in evaluated)))
            outcomes = {branch["effect"] for branch, _ in proven + possible}
            if not proven:
                outcomes.add(ast["otherwise"]["effect"])
            effect = next(iter(outcomes)) if len(outcomes) == 1 else None
            return Evaluation(None, effect,
                              needs=frozenset().union(*(v.needs for _, v in possible)),
                              provisions=frozenset().union(*(v.provisions for _, v in evaluated)))
        if "all_of" in ast or "any_of" in ast:
            kind = "all_of" if "all_of" in ast else "any_of"
            values = [node(part, row) for part in ast[kind]]
            result = conjunction(values) if kind == "all_of" else disjunction(values)
            if result.truth is False and "otherwise" in ast:
                return Evaluation(False, ast["otherwise"]["effect"], provisions=result.provisions)
            return result
        raise ValueError(f"Unsupported accepted AST shape: {sorted(ast)}")

    return provision(identity)
