# Phase 2 — Audit

Answer one question with proof: **is this already implemented in the code?** The output is a verdict
backed by evidence. If you cannot prove it, say so. Stay inside `runs/<name>/sources.md`.

## Non-negotiables

1. **Read the brief in full first,** and every source handed over for this run.
2. **Anchor on the exact action the brief names.** The literal verb is the spec for where the code must
   live. "Block on submit" is not "block on approval". Extract the trigger and hunt for that, not for where
   you think the logic belongs. This is the most common way an audit goes wrong.
3. **Do not assume.** Something similar existing does not make this implemented. Not finding it on the
   first grep does not make it missing. A flag key existing does not make the behaviour wired.
4. **Separate fact from inference.** Every claim is proven (file:line, commit, test you read), inferred
   (marked), or unknown (said out loud).
5. **One grep is not an audit.** Exhaust the angles below.

## Step 1 — Comprehend the brief

Write down: the exact trigger, including whether it is synchronous or asynchronous; each requirement as a
separate checkable item; the scope boundaries; any feature flag implied. If the brief is ambiguous, note
it rather than silently resolving it.

## Step 2 — Hunt from every angle

- **Trigger location:** the exact method or action named. Read the call site and confirm the check runs there.
- **Flag key:** across code and config. A registered key with no guard reading it is registered, not implemented.
- **Domain terms:** entity names, error codes, message strings.
- **Git history:** `git log --all --oneline --grep=<term>`, branch list. A commit on the base branch is
  strong evidence, an unmerged branch is in progress.
- **Tests:** a passing test asserting the behaviour is the strongest single proof. If none exists, note it.
- **Hot paths:** each path the change will sit on (startup, per request, per event, background), with the
  counts from `investigation.md` beside it. A path that is linear today is behaviour to preserve.
- **Adjacent features:** understand how this differs from any predecessor, and check whether only the old
  behaviour is present.

Distinguish **already correct** from **correct by accident**. Behaviour that matches today because nothing
enforces it is what most likely regresses when the fix lands.

## Step 3 — Each requirement individually

Do not collapse to one yes or no. Mark each: met, partial, missing, or can't tell.

**A requirement is met only with both:** proof at the exact trigger with file:line, and code on the base
branch or a passing test that asserts it.

It cannot be met if: the flag is registered with no guard at the trigger; an adjacent feature gives similar
behaviour; the code is only on an unmerged branch; the method exists but the check never runs at that call
site. With no test asserting the behaviour, the most it earns is partial.

## Write `audit.md`

```text
Audit Verdict: <Implemented | Partial | Not implemented | Inconclusive>

Trigger audited: <literal phrase from the brief>, expected to live in <where>

Requirements
- <met | partial | missing | can't tell> <requirement>: <file:line, commit, test, or "no code found">

Evidence
- Proven:   <what you read>
- Inferred: <marked as inference>
- Unknown:  <what you could not determine, and why>

What I searched: <the angles and terms, so the negative can be trusted>

Hot paths: <path + counts, or unknown + why>

Gaps: <what is missing, and where it would live>

Preserve-list: <behaviour phase 6 must not break and phase 7 must prove, including scale-sensitive
behaviour such as "startup stays linear in rows">
```

Inconclusive is a real verdict: state exactly what blocks it rather than guessing.
