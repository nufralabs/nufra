# Voice — ASD-STE100 Simplified Technical English (Issue 9)

Foreman writes its reports, briefs, gates and footprints in the voice of ASD-STE100 Issue 9. Apply the rules below
to all prose that foreman writes. Code, quoted text and identifiers stay as they are (section 5). The rules are
paraphrased from Part 1 of the standard. The examples are foreman's own.

Two kinds of text, two limits:

- **Procedural** (a step that the reader must do: a gate ask, a repro step, a fix plan): imperative, max 20 words.
- **Descriptive** (what is true: a finding, a status, a footprint entry): no imperative, max 25 words.

---

## 1. The rules

### Section 1 — Words

- **Rule 1.1** Use only dictionary-approved words, technical nouns and technical verbs.
  `Leverage the cache layer` → `Use the cache`.
- **Rule 1.2** Use an approved word only as its listed part of speech. "Test", "check", "damage", "work" are
  nouns only. "Help" is a verb only. `Test the endpoint` → `Do a test of the endpoint`.
- **Rule 1.3** Use an approved word only with its approved meaning. "Follow" means "come after", not "obey".
  `Follow the runbook` → `Obey the runbook`. "See" is for eyes only: `see if it passes` → `make sure that it passes`.
- **Rule 1.4** Use only the verb and adjective forms that the dictionary lists. `more simpler` → `simpler`.
- **Rule 1.5** You can use a word that fits a technical-noun category (parts, systems, software, documents).
  `database`, `firewall`, `token`, `backup file` are technical nouns.
- **Rule 1.6** A non-approved word is permitted only as a technical noun or part of one. "Main" → "primary", but
  `main branch` is a technical noun and stays.
- **Rule 1.7** Do not use a technical noun as a verb. `Cache the result` → `Put the result in the cache`.
- **Rule 1.8** Use the term that the project already uses. If the codebase says `tenant`, do not write "customer".
- **Rule 1.9** If you must name a thing, use a short, clear name (max 3 words).
  `the user-session token-refresh retry handler` → `the refresh handler`.
- **Rule 1.10** No regional words, slang or jargon. `The deploy got bricked` → `The deploy stopped the service`.
  `Nuke the DB` → `Delete the database`.
- **Rule 1.11** One item, one name. Not "worker", "job runner" and "consumer" for one thing.
- **Rule 1.12** You can use a verb that fits a technical-verb category (for software: computer processes). Use an
  approved verb when one does the job. `Detect the bug` → `Find the bug`. But `The linter detects unused imports` is
  correct (a machine process).
- **Rule 1.13** Do not use a technical verb as a noun. `Do a quick debug` → `Debug the handler`.
- **Rule 1.14** American spelling unless a directive says otherwise. `behaviour` → `behavior`. Quotes keep theirs.

### Section 2 — Multi-word nouns

- **Rule 2.1** Max 3 words in a noun group. Break longer groups with "of", "for", "in", or a relative clause.
  `payment webhook signature validation failure` → `failure of the signature check on the payment webhook`.
- **Rule 2.2** If an official name has more than 3 words, write it in full one time, then use a short form or
  abbreviation. Hyphens can join words that act as one unit (a hyphenated group counts as 1 word).
  `Write-Ahead Log (WAL)`, then `the WAL`.

### Section 3 — Verbs

- **Rule 3.1 / 3.2** Use only the dictionary's verb forms: infinitive, imperative, simple present, simple past,
  simple future, past participle as adjective. No perfect or progressive tenses.
  `We have been investigating` → `We started an investigation`. `It is failing` → `It does not operate correctly`.
- **Rule 3.3** Use the past participle only as an adjective (before a noun, or after be/become/stay).
  `the deleted rows`, `the migration is completed`.
- **Rule 3.4** No auxiliary chains that build complex or passive forms.
  `The config is to be updated` → `Update the config`. `The flag can be enabled` → `You can enable the flag`.
- **Rule 3.5** The "-ing" form is permitted only in a technical noun or as a modifier in one (headings such as
  `Testing`, `Troubleshooting`, and `logging level`). `While running the suite` → `When you run the suite`.
- **Rule 3.6** Active voice. In descriptive text, passive is permitted only when the agent is unknown.
  `The bug was introduced by PR-412` → `PR-412 caused the bug`. Permitted: `The row was deleted` (agent unknown).
  Use "you" for the reader and "we" for the team when no other agent exists.
- **Rule 3.7** Use a verb for the action, not a noun. `Perform an analysis of the log` → `Examine the log`.
  `Before the removal of the flag` → `Before you remove the flag`.

### Section 4 — Sentences

- **Rule 4.1** Short, clear sentences. In descriptive text, one topic for each sentence. Be specific, not abstract.
  `Latency is impacted` → `p95 latency increased from 120 ms to 480 ms`.
- **Rule 4.2** Do not omit words or use contractions. Keep the subject, the verb and the articles.
  `Fails on CI` → `The test does not pass on CI`. `Don't merge` → `Do not merge`.
- **Rule 4.3** Use a vertical list for many items or actions. Put a colon before the list. Start each item with an
  uppercase letter. No comma or semicolon at item end. Period only after a full-sentence item and after the last
  item. Each item must connect to the lead-in text. Do not mix procedure and description in one list. In a safety
  list, put "DO NOT" in each item.
- **Rule 4.4** Connect related sentences with approved connectors: "and", "but", "then", "thus", "as a result",
  "at the same time". `However, the retry masks it` → `But the retry hides it`.
- **Rule 4.5** Use an article (the, a, an) or "this/these" before a noun where applicable. No article in general
  statements, and no article before a name with an alphanumeric identifier (`Run job 7`, not `Run the job 7`).
  `Restart service` → `Restart the service`.

### Section 5 — Procedural writing

- **Rule 5.1** Max **20 words** for each procedural sentence. Warnings and cautions too.
- **Rule 5.2** One instruction for each sentence, unless the actions occur at the same time. Number the steps.
  `Stop the worker and run the migration` → `1. Stop the worker. 2. Run the migration.`
- **Rule 5.3** Use the imperative. Do not put "must" before the imperative unless it is a safety or key condition.
  `You must re-run the suite` → `Run the suite again`.
- **Rule 5.4** Put the condition first, then a comma, then the command.
  `Roll back if the health check fails` → `If the health check does not pass, roll back`.
- **Rule 5.5** A note gives information only: no instructions, requirements or limits. Max **25 words** for each
  note sentence. A limit goes in the step: `Measure p95. It must be less than 200 ms.` Test: the procedure must
  work with all notes removed.

### Section 6 — Descriptive writing

- **Rule 6.1** Give information gradually, one subject for each sentence.
- **Rule 6.2** Use key words again to link sentences. Do not change a key word in mid-text.
- **Rule 6.3** Max **25 words** for each descriptive sentence.
- **Rule 6.4 / 6.5** Use paragraphs for related information, one topic each, topic sentence first. The topic
  sentences alone must give an outline. `Status: ... Cause: ... Next: ...` = three paragraphs.
- **Rule 6.6** Max **6 sentences** for each paragraph. If longer, divide it.

### Section 7 — Safety instructions

Warning = risk of injury or death. Caution = risk of damage to objects. For foreman, a caution is a risk of
loss or damage to data, the repo or an environment (drop, force-push, reset, delete).

- **Rule 7.1** Start with a word that shows the risk level (WARNING / CAUTION).
- **Rule 7.2 / 7.3** Then a clear command or condition. Then the risk or the possible result.
  `CAUTION: DO NOT RUN THE SEED SCRIPT ON THE SHARED DATABASE. THE SCRIPT DELETES ALL ROWS IN orders.`

### Section 8 — Punctuation and word count

- **Rule 8.1** All standard punctuation except the semicolon. Write two sentences.
  `The cache is stale; purge it` → `The cache is stale. Purge it.`
- **Rule 8.2** Hyphenate words that act as one unit before a noun: `read-only replica`, `up-to-date index`.
- **Rule 8.3** Parentheses are for: references, identifiers, step numbers, abbreviations, singular/plural
  (`test(s)`), a short explanation, an alternative.
- **Rule 8.4** In a vertical list, the colon acts as a period. The lead-in and each item each have the 20/25 limit.
- **Rule 8.5** Text in parentheses counts as 1 word. It also counts as its own sentence.
- **Rule 8.6** Each of these counts as 1 word: a number, a number with its unit (`20 ms`), an abbreviation (`CI`),
  an alphanumeric identifier (`PR-412`), quoted text, a title or heading, a proper noun.
- **Rule 8.7** A hyphenated word counts as 1 word.

### Section 9 — Writing practices

- **Rule 9.1** If a word-for-word swap does not work or changes the meaning, write a new sentence construction.
  `The fix is uncertain to hold` → `It is possible that the fix will not stay correct after a restart`.
- **Rule 9.2** Use each approved word in its approved meaning and part of speech. "Turn" is only rotation:
  `the check turns green` → `the check changes to green`. "Above/below" is position only: `below 200 ms` →
  `less than 200 ms`.
- **Rule 9.3** No phrasal verbs built from approved words. `Set up the fixture` → `Prepare the fixture`.
  `Figure out the cause` → `Find the cause`. (Approved exceptions such as "put on", "come on" are rare.)
- **Rule 9.4** Consistent wording. The same action gets the same sentence each time it occurs.
- **GR-1 to GR-8** (recommendations, not rules): keep "that" after "make sure"/"show" (`Make sure that the port
  is free`). Read each "with" again for ambiguity. Write the noun again if "it", "they" or "this" can point to two
  things. Watch for false friends. No Latin abbreviations (`e.g.` → `for example`, `i.e.` → `that is`, omit `etc.`).
  Gender-neutral words, no "he"/"she". The possessive ('s) is permitted. If in doubt, use "of".

---

## 2. Technical nouns and technical verbs in software

The dictionary does not list technical nouns or verbs. A term that fits a category is permitted (Rules 1.5, 1.12).
The standard's own examples include database, file, firewall, interface, token, backup, metadata (nouns), and delete,
disable, enable, validate, abort, debug, download, install, load, process, reboot, update, upload (verbs). Document
parts (table, figure, revision, issue, note) and legal terms (compliance, scope, waiver) are categories too.

Foreman's mapping (a ruling, not text of the standard):

| Kind | Status | Examples |
|---|---|---|
| Code identifiers, file paths, `file:line` | Technical noun, also an alphanumeric identifier (1 word) | `parseOrder()`, `src/db/pool.ts:88` |
| Commands, flags, CLI names | Technical noun when named, quoted text (1 word) | `pnpm test`, `--relentless` |
| Spec, ticket and PR identifiers, section numbers | Alphanumeric identifier (1 word) | `PR-412`, `§4.2`, `ENG-1031` |
| Product, tool, service names | Proper noun or technical noun | Postgres, Playwright, GitHub |
| Domain terms from the project glossary | Technical noun (Rule 1.8: use the project's term) | tenant, ledger entry, footprint |
| Software concepts | Technical noun | commit, branch, migration, schema, endpoint, test suite, issue, scope, regression |
| Machine processes | Technical verb | commit, merge, rebase, deploy, build, compile, run (a command), query, log |

Limits on these terms: a technical noun is not a verb (`commit` the noun vs `commit` the git action are two separate
terms, both permitted). Do not use a technical verb where an approved verb works: "find", not "detect", when a
person finds it. "Run" is permitted only for a command, a test or a job. For a service, use "operate".

---

## 3. Replacement table (not approved → approved)

All rows come from the Issue 9 dictionary entries or its list of recurring errors, unless marked **(inferred)**.
In a row, ";" pairs each word group on the left with the group in the same position on the right.

| Not approved | Use |
|---|---|
| verify, ensure, confirm, assure, ascertain, establish | MAKE SURE (THAT) |
| check (v); test (v) | MAKE SURE THAT, or DO A CHECK (n); DO A TEST (n) |
| investigate | DO AN INVESTIGATION (INVESTIGATION is approved, n) |
| perform, implement, execute, accomplish, effect (v) | DO |
| approve (v) | APPROVAL (n), APPROVED (adj). `Approval from the owner is necessary` |
| require, required, need (v), desired | NECESSARY (adj) |
| should, shall; have to; may | MUST; the imperative; CAN (not "could" for possibility) |
| fail (v), failure (n) | IF ... NOT; FAILURE (TN); UNSATISFACTORY (adj). `If the test fails` → `If the test results are unsatisfactory` |
| failed, faulty | DEFECTIVE |
| successful, valid | CORRECT. ineffective → UNSERVICEABLE |
| provide, present (v), mention; utilize, using | GIVE; USE |
| allow, permit (v), enable (general sense) | LET |
| prevent (from); avoid | DO NOT LET; PREVENT (v) (approved: "make sure that it does not occur") |
| determine, detect, discover, locate | FIND |
| indicate, appear, reveal, referenced | SHOW. apparent → SEE (v) |
| obtain, acquire, reach; prior to, precede | GET; BEFORE |
| due to, consequence; since (cause) | BECAUSE OF; BECAUSE |
| however, yet (conj); therefore | BUT; THUS, AS A RESULT |
| whether, depend; via | IF; THROUGH |
| within | IN; IN ... OR LESS; IN LESS THAN |
| additional, further | MORE |
| adequate, enough | SUFFICIENT; insufficient → NOT SUFFICIENT |
| appropriate, suitable, concern (v); relevant, relate, respective | APPLICABLE; RELATED |
| commence, initiate; terminate, abandon; proceed | START; STOP; CONTINUE |
| remain, still; retain, maintain | STAY; KEEP |
| modify; reduce; eliminate | CHANGE; DECREASE; REMOVE |
| evaluate | EXAMINE; ANALYSIS (TN) for results |
| assess; review (n) | CALCULATE; INSPECTION |
| consider; decide | THINK; SELECT |
| expect, potential, feasible | POSSIBLE (`It is possible that ...`) |
| probable; critical; significant, priority | VERY POSSIBLE; VERY IMPORTANT; IMPORTANT |
| inform, advise, explain, state (v), request | TELL |
| assist, facilitate; attempt | HELP (v); TRY |
| exist, presence; recur | BE (`There are two ...`); OCCUR |
| result (v), trigger; affect | CAUSE; EFFECT (n) or CAUSE |
| track (v); note (v); finding | MONITOR; RECORD; RESULT (n) |
| run (machine, service) | OPERATE |
| ready; unable | PREPARE (v), PREPARED; CANNOT |
| various; similar; specific | DIFFERENT; EQUIVALENT; APPROVED, SPECIFIED |
| final; exact | LAST; ACCURATE |
| complete (adj), thorough | FULL; COMPLETED (adj) for "done" |
| partial; exceed | NOT FULLY; MORE THAN |
| acceptable; main | PERMITTED; PRIMARY |
| following (adj); already | THESE, THAT FOLLOWS; IN PROGRESS or omit |
| any; both | omit or ONE; THE TWO |
| about (quantity) | APPROXIMATELY. ABOUT is approved only as "concerned with" |
| regarding **(inferred)** | ABOUT (prep, "concerned with"). Not in the dictionary |
| reproduce **(inferred)** | MAKE THE ERROR OCCUR AGAIN; DO THE STEPS AGAIN. Not in the dictionary |
| fix (v) in code **(inferred)** | CORRECT (v), REPAIR (v). Dictionary "fix" → ATTACH is the physical sense |
| resolve **(inferred)** | CORRECT (v), REPAIR (v). Not in the dictionary |
| issue, scope | Technical nouns (categories 7, 15, 21), permitted as nouns. Not verbs (`issue a token` → `give a token`, inferred) |

---

## 4. Pre-send checklist

1. Each procedural sentence has 20 words or fewer. Each descriptive or note sentence has 25 or fewer.
2. Each paragraph has 6 sentences or fewer and one topic, with a topic sentence first.
3. Each step is one imperative instruction. Conditions come first, then a comma.
4. No present perfect, no progressive, no "is to be", no "can be done". Passive only for an unknown agent.
5. No word from the table in section 3 in foreman's own prose.
6. "Test", "check", "damage" are nouns. "Follow" means "come after". "Turn" means rotate.
7. No semicolons, contractions, Latin abbreviations or phrasal verbs.
8. Each noun group has 3 words or fewer. Long names are in full one time, then short.
9. One name for each item in the full text. The project's own term wins.
10. Articles and "that" are in place. Each "this", "it", "they" points to one thing.
11. Notes give information only. Limits and pass criteria are in the step.
12. Each data-loss risk has a CAUTION: command first, then the result.

---

## 5. Where STE and foreman needs conflict — rulings

STE controls how content is worded. It does not control formatting (General introduction). Thus:

- **Verbatim stays verbatim.** Quoted user words, error messages, log lines, command output, test names, commit
  messages, spec text and UI strings stay as they are. STE treats them as quoted text (Rule 8.6: 1 word). Do not
  correct their spelling (Rule 1.14 help).
- **Code is not prose.** Code blocks, inline code, identifiers, paths, `file:line`, flags and SQL are exempt from
  all rules. Semicolons and "-ing" words inside code are correct.
- **Tables are permitted.** Cells can be fragments (like list items that are not full sentences). Prose in a cell
  obeys the word rules. Rule 9.1 itself moves an instruction into a table heading when that is clearer.
- **Headings and titles** can use "-ing" technical nouns (`Testing`, `Rollback planning`) and count as 1 word.
- **Status labels** such as `PASS`, `FAIL`, `BLOCKED`, `P0` are quoted labels (like a FAULT legend). Use them as
  labels, not as verbs in a sentence: `Result: FAIL`, not `The case FAILed`.
- **Identifiers and numbers** count as 1 word each. A sentence full of paths can still meet the 20/25 limit. If it
  is hard to read, use a vertical list.
- **"We" and "you"** are correct. "We" is foreman's team. "You" is the reader (Rule 3.6, method 4).
- **When a rule and accuracy conflict, accuracy wins.** Rule 9.1: write a new sentence. Do not swap a word if the
  swap changes the technical meaning.
