# nufra

Stop anywhere. Resume where you left off.

nufra runs one gated coding workflow (the master-foreman template: phases, human gates, proof per test case) and
lets you move a phase to another coding harness only on your command, between phases. It shows the weekly usage of
each harness. One agent at a time. Local first.

Status: v0.1 in progress. Early: expect breaking changes. Solo project, best-effort support.
nufra switches a harness only on your command and never rotates accounts.

## Layout

- `core/workflow/master-foreman/` the workflow template (skill + references), incl. `pause` and `handoff.md`
- `core/hooks/`, `core/settings.json` the MCP block and settings for a Claude Code workspace
- `adapters/` one launcher per harness (none yet; see its README for the guard rule)
- `bin/master-foreman` start Claude Code with only the workspace's MCP servers
- `bin/nufra-usage` read-only usage meter (local files only, no network)
- `bin/test` run all tests

## Test

    bin/test

## Licence

MIT. See `LICENSE`.
