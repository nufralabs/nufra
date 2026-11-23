# Phase 1 — Investigate

Find the cause with proof, not speculation from the brief. You are the delegated worker, so do the work
yourself and do not launch another agent.

## The boundary

Read `runs/<name>/sources.md` first. That file is the complete list of what you may read.

- **Default:** the local code and the local database. Nothing else, however available it looks.
- **Extra sources** listed there were handed over for this run. Read every one of them **before** forming
  a theory, and read the thing itself, not its title. A source that will not open is a gate: stop and
  return that to the coordinator. Never conclude around it.
- If proving the cause would need something not listed, write it under `Unknown` and name what would
  close it. Do not fetch it.

## Non-negotiables

- Start from the exact behaviour, actor, record and time window the brief gives.
- When data decides the truth, query the local database first, with the config's read command. Read the
  schema before writing the query. Never guess a table or column name.
- Trace the code's call sites and write paths before naming an owner or a fix location.
- Separate confirmed facts, inferred conclusions and unknowns.
- Use absolute timestamps when the sequence matters.
- Keep secrets out of everything you write.

## Workflow

1. **Pin scope.** Actor, entity, requested behaviour, observed behaviour, time window, and which world is
   truth. If the brief does not say and it changes the answer, return the question to the coordinator.
2. **Verify data.** Exact target rows and relationships before broad scans. Check status and history
   tables, config rows and soft-delete columns relevant to the behaviour. Compare expected against actual
   with counts or exact ids. Measure volume for the tables in the path: total rows, largest group if the
   system is multi-tenant, number of groups. Volume is often the cause.
3. **Corroborate.** Local logs the stack writes, and any handed-over log source. Start with a tight window
   and exact identifiers, then widen. A log line is a sequence, not a cause.
4. **Trace code.** The handler and its downstream services. Decide whether behaviour is controlled by code,
   config, data state or the client's payload. Check call sites before proposing a shared-component fix.
5. **Conclude.** Root cause in one or two sentences, proof bullets, impact, the smallest safe fix.

## Disqualifiers — a root cause fails unless each is ruled out

- It is a symptom, not a cause. The error string or failed row is the effect. Keep tracing.
- Correlation without the write path traced. Not yet a root cause.
- The world is not named. Local data, a fixture and code behaviour are different claims. A fixture bug is
  not a live bug, and local data cannot prove what a live system holds.
- A data question concluded from logs alone, with no database confirmation. Unproven.

## Name one fix location

If two seem true, you have not traced far enough.

- **config:** behaviour flips on a setting or flag value, the code is correct.
- **data:** the code is correct, a specific row or state is wrong.
- **frontend:** the payload or render differs, the backend behaves correctly for what it received.
- **backend:** the logic itself produces the wrong result for correct input.
- **setup:** a required row, trigger or configuration is missing rather than wrong.

## Write `investigation.md`

Root cause first, then evidence, then the fix decision. Also record the queries run and the theories
rejected, because a later session cannot re-derive those.

```text
Root Cause: <one sentence, the single concrete cause>

Scope
- Entity: <what is affected>
- Time window: <absolute timestamps, or n/a>
- World: <code behaviour | local data | handed-over source>
- Scale: <total rows, largest group, group count per table on the path, with the source, or unknown + why>

Evidence (sequenced)
- Data: <exact rows or query result>
- Logs: <line + timestamp, or none available>
- Code: <file:line of the write path or call site>

Fact / Inference / Unknown
- Fact:      <proven from data, logs or code>
- Inference: <reasoning, marked as such>
- Unknown:   <still unproven, and what would close it>

Sources used: <from sources.md>

Impact: <who or what is affected, how many, since when, as far as local evidence shows>

Fix location: <config | data | frontend | backend | setup>
- <the smallest correct change, and why it belongs there>

Confidence: <high | medium | low>, <what would raise it>
```
