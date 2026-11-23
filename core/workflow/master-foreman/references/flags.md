# Flags — read only when a flag was actually passed

Three flags, all off by default, independent of mode and of each other. None of them widens what the pipeline may
read: the boundary in `SKILL.md` holds under every flag.

---

## `--relentless` — the coordinator takes every pipeline decision itself

For running with no user available to clear a gate. It is not a quality tier. It supplies the persistence a present
user normally supplies, and adds the self-checks that presence used to provide.

**Gates 2.5 and 6.5 are replaced, not skipped, by:**

1. **A bounded adversarial review.** Before any driver is written, a separate subagent critiques the storyboard.
2. **A mandatory pilot.** Record the P0 case, read the frames back, and only then shoot the rest.
3. **The critique and pilot verdicts are the approval record,** in `critique.md`, referenced from `proof-plan.md`.

### The critique charter

**At most two rounds. A hard cap.** Round 1 critiques. If it rejects, revise once and re-critique. If round 2 still
rejects, the pipeline parks and hands to the user with both critiques. An unbounded review loop is not thoroughness.

**It reviews proof quality only:** will this take, as storyboarded, honestly show the claim to someone watching it?
Grounds to reject:

- a load-bearing fact with no on-screen beat
- no establishing shot
- a claim no outcome could refute
- an entry point that is not the real click a person makes
- a fixture fact that is not true, so the take would burn
- a money shot on a screen nobody would really inspect
- a test that cannot fail, or fails for a different reason than the claim

**Out of scope, a note and never a block:** whether a flag's entry gate was honoured, cleanup perfectionism beyond
what the run created, wording, theoretical completeness.

**Calibration.** Reject a material defect. Accept with notes otherwise. A settled ruling from the user stays settled.

**Two hard stops survive and this flag clears neither:**

- **Rule zero.** A path that cannot be rehearsed parks and waits for a direct turn.
- **Leaving this machine.** No push and no post. A relentless run ends with branches, green tests, every take reviewed,
  and files in `runs/<name>/`. Then it stops.

**What the flag adds:**

| Obligation | Why |
|---|---|
| Every take reviewed before acceptance, frames read back | Nobody else will notice an unwatchable take |
| A refuted take triggers fix, regression test, record again | Stopping to ask wastes the finding |
| A control beat on every blocking take | "Nothing happened" is satisfied by a blank page |
| Cleanup verified by query | With nobody watching it must be evidenced |
| The report leads with what was NOT proven | The user reads it cold |
| Detours logged in `decisions.md` as they happen | A long run is otherwise unreviewable |

**Forbidden in this mode:** the cheaper path when a more convincing one exists, accepting a first take that is merely
green, trimming the test matrix to fit a budget.

---

## `--sprint` — fewer artifacts, never less verification

For work whose shape is already understood: a copy change, a config toggle. It cuts artifacts and must never cut
verification, because a fast wrong answer arrives with the same confidence.

| Phase | Under `--sprint` |
|---|---|
| 0 workspace | full, run by the coordinator directly |
| 1 + 2 | one combined agent, writing both files |
| 2.5 + 3 repro | cut, no before-state video. The failing test still exists |
| 4 analysis note | full |
| 5 test cases | full |
| 6 implementation | full |
| 6.5 plan | full, including the adversarial review |
| 7 evidence | one video, post-fix only, plus every test |

**May never weaken:** the adversarial review at 6.5, rule zero, a positive assertion beside every negative, control
beats, captured bodies, proving a test can fail, cleanup verified by query, the footprint rule, the scale check, and
one real-database test per case.

**The flag refuses itself.** Do not run it, say why, and fall back when: the premise is unproven, because the repro is
the premise check and it is what gets cut; the change needs a structural migration; the audit cannot name one fix
location; or the claim depends on a before and after contrast that one take cannot carry.

**Mandatory output:** every `--sprint` run states what it did not prove, in the report and in `README.md`. Afterwards a
fast run looks exactly like a thorough one, so naming the gap is what keeps it honest.

---

## `--autotune` — the coordinator picks tier and effort per phase

Tiers are roles: `judge` (top reasoning), `worker` (mid), `mechanical` (cheap). Map them to what the runtime offers
and state the mapping in the first progress message. If the runtime cannot switch models per subagent, tune effort and
instructions only, record `model: session-inherited`, and never pretend a tier switch happened.

| Phase | Starting tier and effort |
|---|---|
| 0 workspace | `mechanical`, low |
| 1 investigate | `judge`, high |
| 2 audit | `judge`, medium |
| 1+2 combined | `judge`, high, never lower |
| 2.5 / 6.5 draft | `judge`, medium |
| critique | `judge`, xhigh |
| 3 / 7 record | `judge`, medium |
| 4 analysis note | `mechanical`, medium |
| 5 test cases | `judge`, medium |
| 6 implementation | `judge`, high |

**Downgrade one effort step** when reuse already paid for the difficulty: a donor driver records the same claim, a
single fix location with an existing pattern to follow, or what remains is confirmation, not discovery. Record the step
and the reason in the ledger. Floors: the critique never below the second-highest effort, combined 1+2 never below
high, implementation never below medium. A thin result after a downgrade escalates, and the next run starts higher.

**Escalate one tier** when a phase comes back thin or wrong: the footprint is absent or does not say what the reply
claims, it contradicts a previous phase without evidence, or a verification pass fails. Log every escalation with its
trigger.

**`mechanical` is never given a judgement phase.** Its failure mode is silent. Over budget means cut artifacts, never
verification.
