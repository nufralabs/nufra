# Verify and record — phases 3 and 7

Turn a change into a reproduced, non-destructive outcome with proof anyone can re-run. You are the delegated runner
for **one case**. Do it end to end and return a compact verdict.

**Proof has two halves, both local:**

1. **A test or script** that fails before the fix and passes after, with its output saved to `evidence/`.
2. **A Playwright video** of the real flow, when the project has a UI. Saved under `recordings/`.

**The video is not optional when there is a UI,** however small the change. Do not recommend dropping it to save
time. Only the user can waive it. Nothing is uploaded anywhere.

## Prerequisites — confirm all before any browser action

Unmet means stop and return it to the coordinator. Never work around it.

- An approved `proof-plan.md`, and this case's section in it. The beats are the spec.
- **Verify server-side claims at the test or API level first, browser second.** If the claim is a persisted value or
  a response, prove that before recording anything. Do not debug a browser login when the API path already answers.
- The stack is running, using the config's start commands. Flags are in the intended state.
- **Playwright comes from npm, not from any connected tool.** Use the project's install if it has one. Otherwise
  install it into `runs/<name>/run/` with `npm install playwright` and `npx playwright install chromium`, without asking:
  this download is part of the method. Never add it to the project's own dependencies as a side effect.
- **Test accounts:** log in through the real form, as the opening beat, using the environment variable names in the
  config. Never a real person's session or tokens, never production credentials.
- **Data:** already there, or seeded as the scenario's `Given` with reversible cleanup. Local database only.

## Rule zero — rehearse before you record

No frame is shot from an unrehearsed path. If rehearsal is impossible, because the environment will not come up or an
action works only once, **stop and return that to the coordinator**. Never decide alone that a take is simple enough to
shoot cold.

## Non-negotiables

- **Most complete path, not the shortest green one.** The real action on the real surface through every real step to
  the real outcome. A shorter path that reaches the same code can pass while the real one fails.
- **Drive the real UI action, never its endpoint as a shortcut.** Calling the endpoint proves the backend accepts your
  payload, not that the real screen produces the same one. A direct call is only for what a person cannot click: cron,
  queue, webhook. "The frontend was not running" is not a licence to shortcut. Start it, or report blocked.
- **Reproduce the reported situation exactly,** in the reported direction.
- **Legible from the screen alone.** A reviewer watches the video and does not open the network panel. Establish the
  reference state on screen, perform the action, show the outcome, before and after.
- **The real surface.** An injected banner, a console log or a raw response painted on the page is not evidence.
- **Non-destructive.** Clean up what you created, restore what you mutated, and verify by query.
- **Evidence, not impression.** Back the video with the response, logs and database state.
- **Seed data looks real** and fits the case, so it clears unrelated gates.
- **Hard by the wrong approach is not blocked.** Find a cleaner named path before declaring something unrecordable.
- **Blank pages pass negative assertions.** Pair every "X is absent" with a positive assertion that the page loaded.

## Files, under `runs/<name>/`

- `<feature>.feature`: strict Gherkin, one `Scenario` per case.
- `data.md`: test data, exact ids, reversible cleanup.
- `tests/`: or the path to the test in the repo.
- `run/record-<case>.mjs`: a single self-contained driver.
- `evidence/<case>-before.txt`, `evidence/<case>-after.txt`: test output.
- `recordings/<case>.webm`, `capture/<case>.json`: video and timeline.
- `evidence.md`: appended per case.

## Workflow

1. **Write the spec first,** no browser yet.
2. **Prove with the test.** Run it and save the output. In phase 3 it must fail for the reported reason, and a failure
   for any other reason is not a repro. In phase 7 it must pass, and the assertions inverted from the repro must be the
   ones doing the work.
3. **Rehearse with no recording,** in the identical viewport, headless mode and fixtures, until a full dry pass is clean.
   A failed rehearsal means another rehearsal, never a recording.
   A validation error that fires before the guard is not the outcome under test.
4. **Record** in one execution from one script, untouched mid-run.
5. **Review.** Confirm the script finished and the result occurred. Check substance: expected request, status, ordered
   actions, no stray errors, sane duration. Extract frames at the key moments and read them back. Not flawless means fix
   and record again.
6. **Append to `evidence.md`:** case, verdict, video path, test output paths, the numbered steps the take shows, any fix
   between takes, cleanup counts. Steps name the actor by role and carry no ports, paths or ids, so they read the same
   anywhere.

## Report back

Verdict, data table, video path and size, trigger trace, cleanup counts, and what this did NOT prove.

## The recorder spine

```js
// run/record-<case>.mjs. Run with node. Own browser, nothing shared.
import { chromium } from 'playwright';
import fs from 'node:fs';

const REHEARSE = process.env.REHEARSE !== '0';     // same context either way, only the recorder changes
const OUT = new URL('..', import.meta.url).pathname;
const opts = { viewport: { width: 1440, height: 900 } };
if (!REHEARSE) opts.recordVideo = { dir: `${OUT}recordings`, size: { width: 1440, height: 900 } };

const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext(opts);
const page = await ctx.newPage();

const events = [];
const ev = (o) => events.push({ at: new Date().toISOString(), ...o });
page.on('console', (m) => ev({ k: 'console', level: m.type(), message: m.text().slice(0, 400) }));
page.on('response', async (r) => {
  const q = r.request();
  const type = q.resourceType();
  const wantsBody = ['xhr', 'fetch', 'document'].includes(type);
  ev({
    k: 'network', method: q.method(), url: r.url(), status: r.status(), type,
    requestBody: wantsBody ? q.postData() : undefined,
    responseBody: wantsBody ? await r.text().then((t) => t.slice(0, 20000)).catch(() => undefined) : undefined,
  });
});

const DELAY = 1000;
const step = async (label, fn) => { await page.waitForTimeout(DELAY); ev({ k: 'step', label }); await fn(); };

let failed = null;
try {
  await step('open', () => page.goto(process.env.APP_URL));
  // One step() per human action.
} catch (err) {
  failed = err;
  ev({ k: 'error', message: String(err).slice(0, 400) });
} finally {
  const video = REHEARSE ? null : page.video();
  await ctx.close();                                // flushes the video
  await browser.close();
  const videoPath = video ? await video.path().catch(() => null) : null;
  fs.mkdirSync(`${OUT}capture`, { recursive: true });
  fs.writeFileSync(`${OUT}capture/<case>.json`, JSON.stringify({ videoPath, events }, null, 2));
}
if (failed) { console.error(failed); process.exit(1); }
```

Rehearse with `node run/record-<case>.mjs`, record with `REHEARSE=0 node run/record-<case>.mjs`.

**Capture every request with its bodies.** Do not filter down to the interesting calls: a GET's response is often the
proof. Bodies cannot be added afterwards. Captures stay local, but they still must not hold anything but throwaway
test credentials.

**Prove the database state on the timeline** by recording the query and rows as an event.

## Making it watchable

- **One script, one execution, one uniform delay.** Hand-stepping through tool calls gives uneven pacing.
- **No discovery latency.** The delay is the only pause a viewer sees. Before recording, every locator is known good,
  with no speculative fallbacks. Replace blind waits with a real condition. Retries are insurance, and they must succeed
  first try in the take. Type character by character.
- **Scroll like a person reading.** Measure first, and if the target is visible, do not scroll. When you must, one smooth
  movement of 300 to 600 ms, then hold about half a second before acting. Never repeated fixed nudges, never a giant jump.
- **Headless by default.** Video works the same and no window steals focus. Headed only to debug, then re-rehearse.
- **Viewport only.** Browser chrome is not recorded. Never fake a URL bar with an overlay.

## Selector and form traps

- Wizard steps often stay mounted but hidden, so ids duplicate. Scope with `:visible` or a unique attribute.
- Date inputs that reject `fill()`: use `pressSequentially`.
- Dropdowns: open and pick, match exact first then contains, so one option cannot select a longer lookalike.
- Signature pads and canvases can drop the first stroke. Verify the canvas is not blank and retry.
- A Continue button that verifies it advanced turns a silent freeze into a named failure.
- File uploads: confirm the upload response before relying on the field.
- Dated fixtures rot into the wrong branch. Derive dates relative to now.
- Never assume a port is yours. Map port to pid to working directory before using or killing it.
