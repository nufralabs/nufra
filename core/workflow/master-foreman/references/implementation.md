# Phase 6 — Implementation

How code gets written in this pipeline. Read before editing. Project-specific rules in the config's
`house rules` come on top of these and win when they conflict.

## Before writing

- **Follow the repo.** Read its own conventions, its neighbours and its CI config. Copy patterns, not mistakes.
- **Anchor on the exact action the brief names.** Implement at that trigger, not in the pipeline you assume
  it belongs to. A path that is merely hard is not blocked.
- **Only this job.** Adjacent issues are reported, not fixed. If the brief's stated cause is wrong, say so,
  because that changes the fix. Never silently build to a wrong premise or silently widen the scope.
- **Check every caller before changing shared code.** A shared helper is used by flows you did not open.

## Design rules

- **Shared code does not know its customers.** A generic function must not branch on a specific customer,
  tenant or client. The engine owns a capability in neutral terms, and data or config says which fields, which
  values, which customer. An existing special case is precedent for the seam, not licence to add another.
- **Authorisation is a permission, never a role name.** Role names are labels and they drift. A second check
  behind the real one creates two sources of truth. If a permission is too broad, narrow the permission.
- **Log fields are named by domain, never by ticket or change.** Logs are read months later by someone debugging
  a subsystem. Follow the namespace the file already uses.
- **Feature flags,** when the project uses them: named after the capability, follow the repo's convention, and
  register them where the repo requires.
- **Dates:** decide which timezone a date belongs to and normalise at the boundary. A strict parser that silently
  falls back to "today" is a defect.

## Data changes and migrations

- **Skip, never throw, when the target is absent.** A migration runs on every environment. An absent row is
  normal there, and throwing fails the whole deploy.
- **Update in place, never delete and reinsert.** The id is referenced. If the insert fails, the data is gone.
  Delete only a row this change created, or when the work asks for it.
- **Idempotent by construction.** A re-run stacks nothing.
- **The rollback actually reverses.** Write it, don't stub it.
- **Derive rather than hardcode** when the source of truth is already in the data.
- **Never rewrite a historical record.** Patch in-flight drafts. A submitted snapshot is what a person was shown.
- **Rows that move together, move together.** Enumerate the whole set first: live row, version history, in-flight
  references. Updating one and leaving its siblings stale is the same defect each time.
- **Does this reach what already exists?** A change to a definition often does not reach records in flight.
  Decide deliberately and say so.

## What "done" includes for a defect

1. **The guard at the named trigger.**
2. **The opposite case.** A complete input passes, and the untouched case is still allowed. An over-blocking guard
   is worse than the bug.
3. **A new capacity or uniqueness guard excludes the record being converted,** or it blocks itself.
4. **Tests drive the public path, not just the extracted helper.** A helper test leaves the call site unprotected.
   Confirm a test can fail by breaking the code and watching it go red.
5. **Realistic data.** Real-looking human names and random ids, never "Test User".
6. **Never seed a missing row just to make a crash go away.** The absence may be the defect.

## One real-database test per test case

If the project has a database, every case in `test-cases.md` gets an integration test against a real one. N cases
in, N tests out. A unit test that hand-builds an event proves the consumer and never the publisher, and the cases
most likely to be skipped, such as recipient filters, retries and cross-group negatives, are the ones a mock cannot
honestly carry. A case that genuinely cannot be expressed this way is named in `implementation.md` with the reason.

Before you fix anything, the failing test exists and is red. Save that output: it is half the proof in phase 7.

## Adversarial concurrency audit

For any async or transactional flow, before coding, trace the race windows: read-check-write sequences, capacity
conversion, producer and consumer timing, terminal states and retry, idempotency and duplicates, locks, transaction
boundaries. For each one that applies, add a deterministic test at the real seam. Happy-path cases are the floor,
not the proof.

## Scale check

**Local data is not production size.** It fires when the change touches a loop over rows or a collection, a cache
built at startup or per request, bulk reads or writes, an N+1 risk, or nested iteration. When it fires, all four:

1. **Counts** per table the change reads: total rows, largest group, group count. Measure locally or take them from
   a handed-over source and name it. `unknown` is allowed only with the reason, and say that local counts may be far
   below live ones.
2. **Complexity per hot path:** startup, per request, per event, background. Quadratic on a startup path is a defect
   even when every test is green.
3. **A size test** seeded to a bounded but representative shape, asserting a linear operation budget or a generous
   time bound.
4. **`## Scale` in `implementation.md`** carrying the above. If the check does not fire, say so in one line.

## The proof bar

- **Run the repo's own gates, by the commands its CI uses.** Read the CI file rather than assuming the tool. Name
  the tool you ran, never the one you expected.
- **Never skip a hook with `--no-verify`.** A hook that blocks you is the gate working.
- **A gate you cannot run is a blocker you report,** not a step you skip.
- **Never make a gate pass by changing the gate:** not the lint config, not a ceiling, not a suppression, not a
  weakened test. If a rule is genuinely wrong, that is a conversation with the user.
- **"Not mine" needs the same proof as "it passes":** run it on a clean base-branch worktree and diff the results.
- **Prove deferred work is scheduled.** Assert the pending job or row exists.
- **Prove "unchanged" by comparing the value to its own earlier snapshot,** not to a hardcoded expectation.
- **Report faithfully.** If a step was skipped, mocked or proven at one layer, say so beside the result.

## Environment discipline

- Never assume a listening port is yours. Map port to pid to working directory before using or killing it.
- Local environment fixes stay uncommitted and reversible.

## Commits

Local commits on the run's branch. Never push: that is phase 8 and needs a direct ask.

## Write `implementation.md`

Changed files per repo, flag key, migration name, design decisions especially anything rejected, any deviation from
the fix location in `investigation.md`, concurrency findings, `## Scale`, the test run output and which gates ran. If
a late change lands after takes were recorded: why the earlier takes are still valid, or that they were re-recorded.
