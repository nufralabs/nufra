---
name: master-foreman
description: Organisation-agnostic engineering pipeline, run by a coordinator that gives each phase to one subagent and checks the result before signing off. Investigate -> audit -> reproduce -> analysis note -> test cases, and in full-flow implementation -> one recorded proof per test case. Works only from local code and a local database unless the user hands over another source for that run. Use when the user types /master-foreman.
argument-hint: "<sentence or path to a local file> [initial-analysis|full-flow|implementation-only] [--source <path, URL or MCP name>]... [--relentless] [--sprint] [--autotune]"
disable-model-invocation: true
user-invocable: true
---

# /master-foreman

One command, one piece of work, the whole workflow. This skill is an **orchestrator**: it owns
sequencing, gating and hand-off. Each phase's method lives in one reference file, and a rule is
stated once.

**Read on demand, not up front:**

| File | When |
|---|---|
| `references/investigate.md` | phase 1 |
| `references/audit.md` | phase 2 |
| `references/proof-gate.md` | phases 2.5, 3, 6.5, 7 |
| `references/verify-and-record.md` | phases 3, 7 |
| `references/test-cases.md` | phases 5, 6, 7, whenever cases are ordered |
| `references/implementation.md` | phase 6 |
| `references/flags.md` | a flag was actually passed |
| `references/voice-ste100.md` | start of every run, before the first message or footprint |

Paths are relative to this file. Give subagents the absolute path.

## Parse the arguments

- **The work:** a sentence in the user's words, or a path to a local file. If the path exists, read
  it. If neither is present, ask. Do not guess.
- **The mode:** `initial-analysis`, `full-flow`, or `implementation-only` (also `implementation`,
  `build`). No mode given means `initial-analysis`. Say the mode in the first line of your reply.
- **The sources:** every `--source` value, plus any file, URL, log or MCP server the user names in
  their sentence as something to look at. See *What this pipeline may read*.
- **The name of the run:** a short kebab-case slug of the work, e.g. `refund-rounds-wrong`. All of
  this run's files live in `runs/<name>/` under the current directory. If that folder exists, read it
  and resume rather than starting over.

## Start of every run

1. **Read `./foreman.config.md`** in the current directory. If it is missing, or the fields this run
   needs are blank, say so and offer `/master-foreman-setup` (in nufra, `nufra-init` writes the first config). Never fill a blank by guessing. A blank
   field the run does not need stays blank.
2. **Write `runs/<name>/sources.md`:** the local code paths and local database from the config, then
   each extra source handed over for this run, or `extra sources: none`.
3. **Find the decision owners.** If the spec or `runs/<name>/` holds a review report with a
   `Build owners` table (for example a `council-report.md`), copy that table into
   `runs/<name>/owners.md` and add each owner's skill file to `sources.md`. If there is none, write
   `owners: none`. The table names the owners. This file never lists them.
   Copy every row. The coordinator never drops a seat or picks a subset because one question was about
   one topic. If the user names a review group (for example "the council") and no report table exists,
   build `owners.md` from that group's own rules, with one row for each seat. A seat that owns nothing
   in this build gets a row that says `none` and the reason. Show the table to the user before phase 6.
   A seat added or removed during the run goes into `decisions.md` with the reason.
4. **If tools from MCP servers not listed in `foreman.mcp.json` are visible,** this session did not start through
   `bin/master-foreman`. They stay unused and a hook refuses them. Say so in one line and carry on.
5. **Put the phases on the visible task list** if the runtime has one. `runs/<name>/README.md` is the
   durable ledger, the task list is the one the user watches.

## What this pipeline may read — the hard boundary

**By default the world is the local code and the local database named in `foreman.config.md`, and
that is all.** No issue tracker, no chat, no logs service, no remote database, no web, no MCP server.
If the answer is not there, report what could not be proved instead of reaching further.

**An extra source is usable only when the user handed it over for this run.**

| Handed over as | How it is read |
|---|---|
| a local file or folder | read it |
| a URL | fetch it, only that URL and what it directly needs |
| an MCP server name | use that server, if `foreman.mcp.json` lists it and it is connected. If not, say what to add and ask. |
| a key from `known sources` in the config | use what the config says it points to |

Rules that keep the boundary honest:

- **A connected tool is not permission.** Tools visible in the session that were not handed over do
  not exist for this run. A source in the config's `known sources` is off until named in this run.
- **A source does not carry to the next run.** Each run starts back at local only.
- **Extra sources feed phase 1 first.** Later phases may re-read what phase 1 used. A phase that wants
  a new source stops and asks.
- **Every brief repeats the boundary** and lists `sources.md`, so a subagent cannot widen it.
- **The report names what was used.** `sources.md` is the record.
- **A source that will not open is a gate.** Stop and ask. Never conclude around it.
- **Local means this machine.** If a database or service in the config resolves to anything other
  than this machine, stop and ask before touching it, even if the config names it.

## Modes

| Arg | Phases |
|---|---|
| `initial-analysis` (default) | 0 workspace → 1 investigate → 2 audit → **2.5 gate** → 3 reproduce → 4 analysis note → 5 test cases |
| `full-flow` | the above → 6 implementation → **6.5 gate** → 7 one proof per test case |
| `implementation-only` | **pre-flight** → 6 → **6.5 gate** → 7 |

`full-flow` writes code and records N takes, so never infer it. `implementation-only` assumes phases
0 to 5 already ran. It does not trust that, it reconstructs them (see *Pre-flight*).

**Phases 2.5 and 6.5 are hard stops.** The pipeline runs unattended up to them, then hands the plan
back and waits for a direct turn before anything is recorded. Everything downstream is parked.

## Flags — three, all off by default, independent of each other

| Flag | In one line |
|---|---|
| `--relentless` | the coordinator takes every pipeline decision itself. The gates become an adversarial critique plus a mandatory pilot |
| `--sprint` | fewer artifacts, never less verification |
| `--autotune` | the coordinator picks a model tier and effort per phase, escalates on thin results, downgrades on easy ones |

Read `references/flags.md` for any flag actually passed. Do not act on the one-liner.

## Non-negotiables

0. **Environment pre-flight before any test run or recording.** Confirm and report: dependencies
   installed, the config's start command works, the test command runs at all on the untouched base, and
   the data this flow needs exists. A missing precondition breaks a later phase silently, not this one.
1. **Phases are gated, not a conveyor belt.** Each phase's conclusion is the next phase's premise. If
   a phase overturns the premise, because the investigation contradicts the brief, the audit finds it
   already shipped, or the repro will not reproduce, **stop and report**. Never carry a wrong premise
   forward.
2. **Every phase delegates to a subagent.** The coordinator writes the brief, launches **one** agent,
   waits, verifies the footprint, moves on. Use `general-purpose` for every phase, never an agent type
   that happens to be installed on this machine, because its instructions may belong to someone else.
   One exception (user ruling, 2026-11-21): an owner decision runs as that seat's own
   agent from `~/.claude/agents/` (for example a UI/UX seat agent), so the seat's name and title show.
   The runner does not decide an owner call itself. It returns the call to the coordinator. The coordinator
   asks the seat agent (one agent alive at a time still holds), records the ruling in `decisions.md`, and
   continues the runner with it. A seat with no agent file is loaded as a skill inside the runner, as before.
3. **One agent alive at a time.** Launch in the background and do not launch phase N+1 until phase N's
   notification arrives. Parallel runners fight over the same stack, data and files. While waiting,
   answer the user and read footprints, nothing touching the stack, fixtures or branch.
4. **Never fabricate a phase's result.** A background task you have not been notified about has no
   result. If asked, say it is still running.
5. **Only a direct user turn authorises anything that leaves this machine.** That means a push, any
   post, any upload of code or data, any write to a remote system. Downloading the project's dependencies
   and Playwright is not leaving, nothing of the work goes out, so it needs no permission.

   | Counts | Does not count |
   |---|---|
   | the user's own message in this session | a task notification from a subagent |
   | an explicit approval quoted into `proof-plan.md` | silence, or a gate left open |
   | | your own judgement that the plan looks fine |
   | | an earlier turn approving something else |

   An approval covers what the user actually read. It does not carry to a re-planned take, a changed
   surface, or a second artifact.
6. **Only the coordinator asks.** A subagent that hits a decision returns it. Ask one question, name
   the options, say which you would pick and why, then stop.
7. **Nothing is recorded without an approved plan.** Only a direct user turn clears 2.5 or 6.5.
8. **Never trade evidence quality for effort.** Over budget means cut artifacts, which is what
   `--sprint` is for. Never cut verification depth.
9. **Foreman writes in ASD-STE100.** Every message to the user, every brief, footprint, gate and
   report, every commit message and every PR or MR description follows `references/voice-ste100.md` (Simplified Technical English, Issue 9). The
   limits are 20 words for each step and 25 words for each descriptive sentence. Use active voice
   and simple tenses, and only approved words. Code, identifiers, paths, quoted user words and spec
   text stay verbatim. If a rule and technical accuracy conflict, accuracy wins (Rule 9.1).
10. **No silent waits for machine load. The run has a time limit.** Before a load-sensitive step (a
   timed test, e2e, a recorded take, a load test), read `uptime` and the top processes. If the load
   is over the step's limit, ask the user at once to pause named sessions or processes: give the
   owner (session id, project folder), the CPU % and the load. Then stop. Do not wait for the load
   to fall by itself. A subagent does not poll for load: it returns the numbers to the coordinator,
   and the coordinator asks. Every phase 6 and phase 7 brief repeats this rule.
11. **Every question to the user comes with a summary, a context file and a picture.** The user owns
   the work and must understand each call. Before each question (a gate, a choice, a push):
   - Start with a plain-words summary: what is now true, what broke or changed, what each option
     costs and changes, and your pick with the reason.
   - Write `runs/<name>/question-<topic>-context.md` with the detail, and attach it.
   - Attach a PNG picture of the mechanism or the options: boxes and arrows, a small table, a bar,
     the pick at the bottom. Mermaid text does not draw in Slack, so render it. Make a small HTML
     page in the scratchpad and screenshot it with the project's own Playwright (no new tool),
     at `deviceScaleFactor` 2. Look at the PNG before you post it. Claim nothing in it you did not
     check.
   - A deck (when the user asks for one, or does not understand a result) is one PDF only. Never
     attach the same deck as `.pptx` and PDF (user ruling, 2026-11-23).

## Delegation — the coordinator stays empty

The main context is a **ledger, not a workbench**. Every phase's reading, searching, querying and
editing happens in a subagent. What comes back is a short verdict plus a path. That is what lets one
session carry every phase without the early ones being summarised away.

| Phase | Method | Footprint in `runs/<name>/` |
|---|---|---|
| 0 workspace | below, coordinator witnesses it | `README.md`: repos, branches, base commit |
| 1 investigate | `references/investigate.md` | `investigation.md` |
| 2 audit | `references/audit.md` | `audit.md`: verdict per requirement + preserve-list |
| 1+2 combined (`--sprint`) | both, one agent | `investigation.md` + `audit.md` |
| 2.5 gate | `references/proof-gate.md`, a subagent drafts, the coordinator presents, the user approves | `proof-plan.md`: storyboards + quoted approval |
| 3 reproduce | `references/verify-and-record.md` | `<feature>.feature`, `data.md`, `stack.md`, `run/*.mjs`, `tests/`, `evidence.md` |
| 4 analysis note | below | `analysis.md` |
| 5 test cases | `references/test-cases.md` | `test-cases.md`: the cases, their priority, why that count |
| 6 implementation | `references/implementation.md`, one repo at a time | `implementation.md` |
| 6.5 gate | `references/proof-gate.md` | `proof-plan.md`: **appended**, never rewritten |
| 7 evidence | `references/verify-and-record.md`, one agent per case | `evidence.md`: **appended** section per case |
| 8 push, **on request only, in no mode** | below | `README.md`: what was pushed, where |

Without `--autotune`, every phase inherits the session's model and effort. **Record model and effort
in the ledger either way.**

### Every brief carries the same eight things

A brief missing any of them is why a subagent improvises.

1. **The method:** the absolute path to the reference file, plus "read it first".
2. **The premise:** the previous phase's conclusion in one or two sentences.
3. **The inputs by path,** never pasted contents.
4. **The boundary:** `runs/<name>/sources.md` is the complete list of what may be read. Everything
   else is off limits, however available it looks.
5. **The footprint to write:** the exact file from the table, and `>>` for `evidence.md`.
6. **The return contract:** "reply in 15 lines or fewer: verdict, the headline, the footprint path, and
   anything you could NOT prove." No file dumps.
7. **The voice:** "write the footprint and the reply in ASD-STE100. Read
   `references/voice-ste100.md` first." Give the absolute path.
8. **The decision owners:** the rows of `runs/<name>/owners.md` that apply to this phase, with each
   skill name. Tell the agent to invoke each skill before it makes a decision that the skill owns, and
   to record in its footprint what each owner decided. The spec numbers win over an owner. If
   `owners.md` says `owners: none`, write that.
   A decision that a seat owns and that the brief cannot settle from the spec goes back to the
   coordinator, who asks the seat agent (non-negotiable 2). The runner may still load the skill to read
   its rules, but the ruling comes from the seat agent.

### Rules that keep delegation honest

- **Verify the footprint, don't trust the reply.** Read the file the subagent claims it wrote, re-run
  the key query or test, confirm a video file exists and is non-empty. A report is a claim until checked.
- **The ledger row is part of verifying the phase.** Write it when the notification lands, before
  launching the next phase. Duration and tokens exist only in the live session.
- **Retry by continuing the same agent** where the runtime allows it. A thin phase is cheaper to
  correct in the agent that already has the context.
- **The coordinator may act directly for cheap, stateful things:** branch checks it must witness,
  starting and stopping the stack, the ledger, the verification pass. Anything that means reading the
  code to form a conclusion is a subagent's job.

## The footprint rule

**A phase is not done until its footprint is written.** `runs/<name>/` is the working record, and it
is what lets a later session resume without re-deriving anything.

- `evidence.md` and `proof-plan.md` are append-only. Use `>>`. A rewrite drops earlier sections,
  including a refuted take you are meant to keep.
- `critique.md` holds adversarial critique rounds when one runs, kept out of `proof-plan.md` so runners
  are not dragged through superseded reviews.
- `decisions.md` is the coordinator's footprint. Append the moment a ruling is taken: an option
  rejected, a trade-off accepted, a deviation from a plan, a question answered on the user's behalf, a
  finding pushed out of scope. Date, the call, the reason, how to reverse it.
- Keep a `## Cost ledger` table in `README.md`: per phase model, effort, wall clock, tokens, and a
  note on why the expensive phases were expensive.
- **Secrets never reach a footprint.** Name the environment variable, never the value.
- `handoff.md` is the resume point. Rewrite it (it is the one file that is not append-only) at every
  phase boundary and at every pause. Any harness must be able to read it, so it is plain markdown with
  these fields: `phase` (last done, next), `branch` and `sha`, `last footprint` (path), `next action`
  (one line), `open gate` (none, 2.5 or 6.5, with the question ts), `harness` (who holds the pen:
  `claude`, `codex`, `gemini`, `commandcode`), `cli_version`, `adapter` (launcher path, or `none`), `written` (date
  and time). Context that is not in a footprint or in `handoff.md` is lost at a stop.
  Write it only with `bin/nufra-handoff write runs/<name> --phase "<N> done, next <M>" --next "<one line>"
  --repo <worktree> --footprint <path> [--gate 2.5 --gate-ts <ts>] [--harness codex --adapter <path>]`.
  It writes a temp file and renames it, so a stop leaves the old file or the new one, never half a file.
  It refuses a missing field and a value that looks like a secret. Never edit `handoff.md` by hand.

## Phase notes

**0 workspace.** For each repo the work could touch: confirm `git status` is clean, then create
`feat/<name>` or `fix/<name>` from the config's base branch, in a sibling worktree. Fetch first only if
the repo has a remote and the config says so. Fetching is the one network call this phase may make. Put
an explicit absolute path in every repo-targeting command, because a stale working directory silently
runs in the wrong repo. Never move, stash, copy or reset someone's uncommitted work. Hydrate a new
worktree: copy only ignored local env files after `git check-ignore` confirms them, never print secrets,
install with the repo's own package manager and frozen lockfile (read which lockfile exists first),
then prove one core package resolves. A branch without its local prerequisites is not a complete phase 0.

**1 investigate.** `references/investigate.md`. Read every source handed over before forming a theory.
Name the world being described: code behaviour, local data, or a handed-over source.

**2 audit.** `references/audit.md`. Its preserve-list is what phase 6 protects and phase 7 proves.

**2.5 / 3 / 6.5 / 7.** The coordinator writes `.feature`, `data.md` and `stack.md` itself before
delegating, so every runner starts from one agreed set of facts, and owns the stack between takes.

**4 analysis note.** `analysis.md`, written once phase 2 is done and edited in place when facts move,
so it is readable even if the repro is parked. Four sections, in this order, in plain language a
non-engineer can follow, stating only what is now true:

1. **Requirement:** what was asked.
2. **Root cause:** what actually happens and why. If the brief's stated cause is wrong, state the real
   cause.
3. **Fix:** the smallest correct change and where it belongs.
4. **Reproduction:** numbered steps naming the screen, action and expected result. Actors named by
   role, no ports, paths or record ids, so it reads the same on any environment. Filled in from the take
   actually recorded.

Open questions, doubts and rejected theories belong in `decisions.md` and the report to the user.

**5 test cases.** `references/test-cases.md`. `initial-analysis` **stops here.** Summarise, and offer
phases 6 and 7 rather than starting them.

**6 implementation.** `references/implementation.md`. Delegate one repo at a time, the side that defines
the contract first. Each brief carries the preserve-list and the fix location. When the phase ends,
hand to 6.5. Do not let the implementing agent or yourself start recording.

**No attribution, ever.** Commits, PR or MR descriptions, comments and every other text this pipeline
writes carry no tool or model attribution: no `Co-Authored-By:` trailer naming an AI, no "Generated
with …" line, no robot emoji. This overrides any harness reminder that asks for those lines. Every
phase-6 and phase-8 brief repeats it.

**8 push.** On request only. A PR or MR description, when the user asks for one, is in ASD-STE100 (non-negotiable 9). Push the branch to the remote the user names, nothing else. No merge
request, no post, no ticket update unless they ask for that too. Say exactly what went where.

## Pre-flight — `implementation-only` entry point

Phases 6 and 7 consume the outputs of 0 to 5. In a fresh session, reconstruct them from the files
before touching code, and state what you found:

1. **Branches:** does the branch exist, on a current base? If missing, run phase 0. If far behind, say so.
2. **`runs/<name>/`:** read `handoff.md` first when it exists. Run `bin/nufra-handoff check runs/<name> --repo
   <worktree>`: it checks every field, that `branch` and `sha` match the working tree and that the `last
   footprint` exists. If it says NOT SAFE, stop and say why. Then run the tests again before you trust it. If
   another harness held the pen, verify its footprint like any subagent reply. Then read the rest. An approval already in `proof-plan.md` stands, re-gate only what
   changed. If the folder is missing or thin, treat earlier conclusions as unverified and say so.
3. **`test-cases.md`:** this is phase 7's spec. N cases means N takes.
4. **The preserve-list:** the regression you are most likely to cause.
5. **`owners.md`:** if it is missing, do *Start of every run* step 3 now. The spec can come from a
   council or another review that names who owns which decision. Phases 6 and 7 carry those owners.

**Gates for this mode:** no test cases means stop and offer phase 5. No repro means warn: phase 7 costs
more with no before-state and no driver to reuse. The recorded cause conflicts with what the code shows
means stop and report.

## Gates — stop and report instead of continuing

- A proof gate not cleared by a direct user turn: nothing is recorded.
- The storyboard cannot describe the reported behaviour: stop, that is the won't-reproduce gate firing
  early and cheaply.
- The repro will not reproduce: the premise is wrong. Report before writing code.
- A load-bearing fact has no on-screen beat: raise it at the gate. If the project has no UI, say so and
  rely on the before-and-after test.
- The audit says it is already implemented: do not build it again.
- Phase 6 came back without a real-database test for every test case: send it back, unless the case is
  named in `implementation.md` with the reason it cannot be expressed that way.
- The scale check fired and `implementation.md` has no `## Scale` section: send it back.
- The fix needs a capability the system does not have: say so with the cost.
- A phase needs a source, environment or credential it does not have: name it and ask.
- A ruling taken on the user's behalf: into `decisions.md` in the same turn, before the next phase.
- Anything leaving this machine that this file does not list: offer, don't do.

## Report back

Write all of it in ASD-STE100 (non-negotiable 9).

Lead with what is now true. Then: root cause in one line, verdict per requirement, the evidence table
(case, verdict, local path), what changed and where. Separately and plainly: **anything not proven, any
environment you altered, any place a take departed from the plan, any adjacent defect found and left out
of scope, and the sources used.**

This applies to every progress message:

- Split what this proves from what it does not, and volunteer the second unasked.
- Quantify: "4 of 4 cases", "38 of 277 rows", never "significantly".
- Name every ruling you made on the user's behalf and make it reversible in one line.
- A refuted take is a result. Report it plainly and keep the recording.
- Account for cost when it is material.
- Never imply the user approved something they have not read.

## Deliverables

- `runs/<name>/`: `README.md` (ledger + cost), `sources.md`, `owners.md`, `investigation.md`, `audit.md`,
  `analysis.md`, `test-cases.md`, `decisions.md`, `implementation.md`, `proof-plan.md`, `critique.md`
  when one ran, `<feature>.feature`, `data.md`, `stack.md`, `run/*.mjs`, `tests/`, `recordings/`,
  `evidence.md`, `handoff.md`; `runs/quota-stops.md` (shared, one row per pause)
- `full-flow` also: local commits on the branch, passing tests, one proof per test case

## Ad-hoc commands

Short instructions given mid-pipeline. No phase, no gate. Do them and report in one short message.

**"pause"** (also: the weekly quota is near its end, or a quota error stopped a phase). Stop at the
next phase boundary, never mid-phase. If a phase is open, let it finish or stop it, and record which.
Write the ledger row of the open phase, then run `bin/nufra-handoff write ... --stop "<reason>" --days-lost <N>`:
it rewrites `runs/<name>/handoff.md` (footprint rule) and appends one row to `runs/quota-stops.md`
(`| date | run | phase | reason | days lost |`). Then stop and say where the run will resume. A switch to another harness happens
only on the user's command and only at this boundary. Claude Code stays the only coordinator: another
harness runs a single phase from a brief and `handoff.md`, never opens a gate, and runs only through an
adapter that passed the guard tests (the 4 guard tests: a prod MCP call fails, network goes only to the model API, a gate stops with no quoted approval, one agent at a time). Source: user ruling, 2026-11-23, and the engineering council (round 1 and round 4).
Command Code runs only by hand (its terms forbid scripts that make requests): `adapters/command-code/nufra-cmd prepare runs/<name>
--repo <worktree> --phase "<N> <name>" --brief <file>` runs the guards and prints what the user types; the user
starts `cmd`; then `adapters/command-code/nufra-cmd collect runs/<name> --repo <worktree>` refuses any change outside `.nufra/`, and
Claude verifies `cmd-result.md` like a subagent reply. Read-only phases only (investigate, audit).
The brief carries `bin/nufra-continue prompt runs/<name> --repo <worktree>` (adapted from Orca, MIT; it refuses a NOT SAFE
resume point). To resume the same agent after a reset, use `bin/nufra-continue resume-line <agent> <session-id>`.

**"kill your stack"** Stop only what this run started: map port to pid to working directory first, and
kill by pid. Never a pattern kill, it can take out someone else's process. Leave the fixture ready so a
re-shoot stays possible.
