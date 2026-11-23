# Phase 5 — Test cases and priority

`test-cases.md` is phase 6's work-list and phase 7's. Read this whenever cases are written or ordered.

## The count is not fixed

**Derive the count from the code, then stop.** Enumerate the branches of what the change touches: each
conditional, cap, gate, routing fork, distinct data shape. One case per branch the change can move, plus one
per branch that must provably not move. Write the number down first, and record why.

- **Padding check:** which distinct branch does this case own that no other does? Same branch, different
  label means merge it.
- **Gap check:** which case covers this branch? A branch with no case is a gap.

**Always include the two that catch over-blocking:** the untouched or empty case still passes, and the
completed case releases.

## Cases a person can run

- Written so a tester with no scripts and no help from an engineer could run them, when the project has a
  surface a person can use.
- No developer language. A tester finds data or performs a setup step.
- **Can the case create the state itself by driving the flow?** Then it is a step, not a precondition.
- Preconditions are scoped per case. A blanket "all must hold" over-blocks.
- If a setup can fail silently, put a stop in the steps: "Verify X exists. If not, stop, the rest would pass
  for the wrong reason."
- No flag-off cases. A flag is a rollout control, so "with the flag off nothing changes" only proves switched
  off code is switched off. Cover the guard's placement with a unit test.
- **Scope is the brief's rule.** Real defects you found that are not this work do not become cases. Report them.
- A case with no agreed expected result cannot pass or fail. Leave it out, or write it as "record the actual
  behaviour and ask".
- Check an axis moves the outcome before spending cases on it. When two cases legitimately share a result,
  say why in the case, so a future difference reads as the bug signal.
- Name things. Numbered cross-references ("see case 11") rot when cases are reordered.

## A case that cannot be run by hand does not disappear, it moves

| What could be wrong | Where it belongs |
|---|---|
| What the database actually returns: scoping, status sets, joins, which rows a predicate selects | **a real-database integration test** |
| Control flow: is the guard before the write, which message is chosen | a unit test is fine |

A mocked test cannot prove a data question. It re-asserts the assumption about what the query returns.

Add a **"Removed, and why"** section naming why the case cannot be run by hand and the exact test that now
owns it. A requirement that quietly disappears is a requirement nobody is testing.

## Optional large-data case

When the scale check in `implementation.md` fires, consider one case run against the largest realistic
dataset available locally, with what a pass looks like at that size, so slow-but-correct reads as a fail. If
no such data exists without seeding, skip it and say why. The scale test then owns it.

## Priority: Risk → Requirement → Coverage → Dependency

Levels: **P0** highest, **P1** high, **P2** medium, **P3** low. The first three factors decide what matters.
The fourth decides only the order.

1. **Risk, always first.** What can do the greatest damage: lose money, lose or corrupt data, crash the system.
2. **Requirement.** With equal risk, what the business values more goes first.
3. **Coverage.** With equal risk and value, the case that exercises the most functionality.
4. **Dependency, order only.** If payment needs login, the login test runs first. That does not promote it:
   say "P2, runs first (dependency)".

**Calibration:**

- **P0:** a failure puts wrong money on a real account, corrupts or loses data, breaks an already-shipped flow
  for a whole group of users, or is the work's own core requirement failing visibly.
- **P1:** a specific guard could breach (a cap, a double count), the rollback path, a high-value requirement.
- **P2:** edge dates, secondary gates, alternate shapes, status variants.
- **P3:** cosmetic, known gaps recorded as they are, an edge whose spec is still open.

**Guardrails:** never let coverage or enthusiasm outrank risk. Do not spread cases evenly to look balanced. If
six cases are genuinely money risks, six are P0. A bare `P1` is not reviewable, so state the factor that decided it.

## Write `test-cases.md`

Sorted by priority, dependency recorded as a note.

```text
Count: <N>, because <which branches>

| # | Case | Priority + deciding factor | Preconditions | Steps | Expected | Branch it owns | Evidence |

Removed, and why: <case, why not by hand, the test that owns it>
Not included: <with reason>
```

The Evidence column is filled in phase 7 with the local path.
