# Compute and spend

How a builder, a reviewer and the coordinator spend time, memory and the subscription. The aim is the result in the
least wall time with the same checks. The machine has 8 cores and 8 GB of memory, and swap lives on the system disk.

## Time

- Before a pass you expect to take more than two minutes, time it on a slice (one version, about 1% of rows) and say
  the estimate.
- If the estimate is over ten minutes, make the pass faster before running it:
  - Vectorize: shapely 2 array functions and `STRtree` queries rather than Python loops over geometries, prepared
    geometries for repeated containment, and numpy or DuckDB for tabular work.
  - Cache intermediate results under keys made of their inputs' hashes, and reuse what an earlier step saved.
  - Parallelize across independent units (versions, documents, releases) with a process pool that stays under the
    memory gate.
- Iterate on a slice. Run a whole-population pass once, at the end, after the code is final.
- Run a job longer than a few minutes in the background with its own log, check the log between other work, and never
  wait in a sleep loop. Never end your run with a job still running.

## Memory and disk

- Start a heavy job only while `memory_pressure -Q | tail -1` shows at least 20% free.
- Take `$CORDON_STORE/heavy.lock` (`mkdir`, with a line naming your run and the date) only for a whole-store pass.
  Release it with `rm -r` the moment the pass ends, and never remove another holder's lock.
- Keep at least 3 GB of disk free.

## The store

- Set `CORDON_STORE` inline on each command that reads the store. Never export it in a shared shell.
- Never delete in the shared store, except your own unit's derived outputs.
- A branch that changes a reader's version (`monitoring.py`, `evidence.py`, `releases.py`, `campaign.py` or
  `store.py`) runs its tests and readers against an empty store, because against the shared store it re-derives other
  units' readings.

## Model readings

- Model readings run on the Claude subscription (`claude -p` through the readers' transports), never on a metered API.
  At most two run at once, since every builder shares the subscription.
- Before a reading pass, name the fields and cells its consumer reads, and read only those. Place the reading against
  what is already held (dates, titles, listings, text layers). Read deterministically wherever a text layer carries the
  content.
- State the request count before the pass starts. A pass the coordinator has not cleared with Owen does not start.
- When a reading fails on a session or usage limit, stop the pass. That failure is never recorded as a limit of the
  source.
