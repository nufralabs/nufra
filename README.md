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
- `bin/nufra-init` set up a workspace for your repos: reads each repo, proposes `foreman.config.md` with the file each value came from, writes after you confirm, copies `core/` into `.claude/`
- `bin/master-foreman` start Claude Code with only the workspace's MCP servers
- `bin/nufra-usage` read-only usage meter (local files only, no network; `--short` for a narrow table)
- `bin/nufra-handoff` write and check the resume point (`handoff.md`)
- `bin/nufra-continue` the continuation prompt for the next agent (only when the resume point is safe), and each agent's resume line. Adapted from Orca, see `NOTICE`
- `adapters/command-code/nufra-cmd` hand-off to Command Code: guards, the user runs `cmd`, then collect
- `adapters/claude-gateway/nufra-gateway` Claude Code on an Anthropic-format gateway (one model, no MCP)
- `bin/nufra-page` one read-only page on http://127.0.0.1:7401: what waits on you, weekly usage, every run with its state (colour + shape + word). Stdlib, no JavaScript, writes nothing
- `core/favicon.svg`, `core/mark.svg` the mark (seed in the notch)
- `bin/test` run all tests

## Start on a new repo

    mkdir ~/my-ws && cd ~/my-ws
    ~/nufra/bin/nufra-init ~/code/my-app      # shows the proposal, asks y/N
    ./master-foreman                          # then /master-foreman-setup for the database
    ~/nufra/bin/nufra-page                    # in the workspace: open http://127.0.0.1:7401

## Test

    bin/test

## Licence

MIT. See `LICENSE`.
