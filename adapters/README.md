# Adapters

One launcher per harness. Claude Code is the only coordinator. Another harness runs one phase from a brief and
`handoff.md`, and never opens a gate.

Rule: an adapter may run only after its guard tests pass, and each test tries a call that must be refused:
1. MCP: no MCP server the workspace did not declare (so no prod server can be called);
2. prod: the brief holds no prod server name and no forbidden term;
3. gate: a phase with an open gate is refused;
4. one agent: only one harness holds the pen at a time.

## command-code (M4)

`command-code/nufra-cmd` is a hand-off adapter: nufra never starts Command Code. Its terms forbid scripts that
"perform automated searches or requests" (commandcode.ai/terms, Acceptable Use). The user runs `cmd` by hand.

    nufra-cmd prepare runs/<name> --repo <worktree> --phase "4 investigate" --brief brief.md
    # user: cd <worktree> && cmd, then "Read .nufra/cmd-brief.md and follow it."
    nufra-cmd collect runs/<name> --repo <worktree>

Guard 5 (resume): the brief holds the `nufra-continue` prompt, built only when `nufra-handoff check` says OK.
`collect` refuses a new commit or any change outside `.nufra/`. Guard tests: `tests/test_nufra_cmd.py`.
The guard "network only to the model API" does not apply: nufra does not start the process.

## claude-gateway (Claude Code on an Anthropic-format gateway)

`claude-gateway/nufra-gateway` runs Claude Code itself against a gateway that speaks the Anthropic Messages format
(for example a prepaid router). The workflow, skills and hooks stay the same; only the model and the bill change.
It is a coordinator like any Claude session, so guard 3 (gate) does not apply: the same gate rules hold.

    nufra-gateway check --profile ~/.config/nufra/gateways/<name>.json
    nufra-gateway start --profile <profile> --run runs/<name> --repo <repo> [--window]
    nufra-gateway release --run runs/<name>

Guards: no MCP server (`--strict-mcp-config`, empty file); key file mode 600, https only; one model for every slot
(main, aliases, subagents, auto mode); one pen; `nufra-handoff check` OK before start. Fresh session from
`handoff.md` + `nufra-continue`, never a resume of the old chat. Guard tests: `tests/test_nufra_gateway.py`.
