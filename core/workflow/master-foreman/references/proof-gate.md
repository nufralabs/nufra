# The proof gate — phases 2.5, 3, 6.5 and 7

Phase 2.5 gates phase 3 (the repro). Phase 6.5 gates phase 7 (the evidence). Same mechanism, same file,
different content.

`verify-and-record.md` owns how a take is recorded. This file owns what happens before a driver is written:
finding what exists, designing the storyboard, getting it approved.

**Why gate first:** the driver is the expensive artifact. A take that is green but unwatchable costs a full re-shoot.
Five minutes of the user's attention on the plan is cheaper.

## 1. Reuse before you script

Search before writing a driver, and quote the result in the plan.

```bash
ls runs/*/run/*.mjs                               # every driver in this workspace
grep -rli "<the claim's verb>" runs/*/run/*.mjs
grep -rli "<the surface>" runs/*/run/*.mjs
```

Also look for the project's own end-to-end tests and page objects, in the repos from the config. Report one of:

| Outcome | What the plan says |
|---|---|
| a driver covers this already | name it, and what changes, usually only the assertions |
| parts transfer | name each donor and the part taken |
| nothing | what you searched and how many files you read, then budget a first take |

**Do not copy blindly:** assertions of the old behaviour (a repro asserts the bug, so in phase 7 it must be
**inverted** or the take passes by proving nothing), environment workarounds, stale selectors and fixtures.

## 2. The plan, one storyboard per take

A subagent drafts `runs/<name>/proof-plan.md`. Per take:

1. **What it is for:** the repro (2.5), or the test case and priority (6.5).
2. **The claim, and what would refute it.** A claim no outcome can refute is decoration.
3. **The test:** the failing test or script that proves this without a browser, and the output that will be saved.
4. **Fixture:** account and role, records, the exact starting state, how it is seeded, reversible cleanup. Realistic
   names. **Local database only,** and say which.
5. **Surface and entry point:** which app, which screen, and the exact button a person clicks, never the endpoint
   that button calls. A step that truly cannot be clicked, like a cron or a webhook, is named as a labelled event.
6. **Beats:** the numbered on-screen sequence. Two are mandatory and labelled: the **establishing shot** (the
   reference state before the action) and the **money shot** (the frame proving the outcome, in contrast with the
   establishing shot, on the screen someone would really inspect).
7. **Legibility check:** for every load-bearing fact, the beat that makes it visible without the network panel. When
   the step that causes the fact happens off-screen (an API call, a request body, a CLI command, a test), its result
   still gets a beat on a screen. A fact with no beat is raised as an open question.
8. **No contradicting screen:** list every value that is visible during the take and describes the subject of the
   claim: a setting, a slider, a status, a label, a counter. Each one must agree with the evidence. If the take sets
   a value in a way that the visible control does not see, for example a per-request value while a global slider
   shows another, drive the step through that control. If that is not possible, put the real value on screen next
   to it and say on screen why the two differ. A frame that contradicts the claim is a defect of the take, even when
   the off-screen backing is correct.
9. **Off-screen proof:** requests captured with bodies, the query confirming the row. Backing, not primary.
10. **Base driver and preconditions:** what the sweep found and what must exist for the screen to be drivable.
11. **Cost:** takes, rough runtime, any stack change the coordinator owns between takes.

**Only if the project has no UI at all,** the storyboard is the test alone, and the plan says the video is not
applicable. A project with a UI always gets the video. Never put "skip the video" to the user as a recommendation.

End with **open questions:** every place the drafter guessed which surface, which direction, or what "expected"
really means. That list is the point of the gate.

## 3. Running the gate

- Show the user a compact summary, not the file: take, surface, establishing shot, money shot, verdict if true, then
  the open questions, then the cost.
- **Stop and ask.** Options: approve all, pilot first, refine. Free-text changes are the expected answer.
- **Wait for a direct user turn.** While waiting, answer questions and update the ledger, nothing touching stack,
  fixtures or branch.
- On approval, write into `proof-plan.md` the date, what the user changed, and their wording. Every runner brief
  quotes that file.
- **Re-gate on material deviation:** an impossible beat, a surface that does not exist, a case needing splitting, a
  money shot landing elsewhere. Cosmetic fixes like a selector or a wait go in `stack.md`.

## 4. Per-gate differences

**Phase 2.5, the repro.** The only place the before state gets designed.

- One storyboard, in the **reported direction**. Not the mirror image that hits the same code.
- The establishing shot matters most here: what the value should be is on screen before the action gets it wrong.
- This driver is phase 7's base. Say which assertions will need inverting after the fix.
- **If no fixture reproduces it,** report it, the premise may be wrong. Never film an adjacent flow that happens to
  be reachable.

**Phase 6.5, the evidence.**

- **The work-list is `test-cases.md`,** not your reading of the change. N cases means N storyboards, ordered by
  priority. A plan with fewer names the case dropped and why.
- Each storyboard names which assertions from the repro are inverted.
- The **preserve-list from `audit.md`** gets storyboards too where the cases cover it. The over-blocking cases are
  the ones that catch real bugs in the fix.
- **Recommend the pilot:** record P0 first, hand back the path, pause for a quality read before the rest.

## 5. Recording-time rules

- **Record the approved storyboard, not your reading of the case.** A runner that finds a better path reports it and
  stops.
- **One runner at a time.** Give the next runner the previous runner's finished driver as its base. This compounding
  only works in order.
- **Fix the environment rather than shipping a workaround into evidence.**
- **Trust, then verify:** confirm the video exists, is non-empty and plays, and search the capture for passwords using
  a literal string count, because shell quoting silently miscounts values with special characters.
- **Watch the take for contradiction before you accept it.** Read frames across the whole take, not only the money
  shot, and check them against storyboard item 8. A frame that contradicts the claim fails the take, and the take is
  recorded again.
- **A refuted take is a success.** Fix the code, add a regression test, record again. Keep the refuted take,
  cross-linked as superseded, because it is the bug report.
- If takes were recorded before a late code change, **prove** they still hold, or record them again.
