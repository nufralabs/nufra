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

`collect` refuses a new commit or any change outside `.nufra/`. Guard tests: `tests/test_nufra_cmd.py`.
The guard "network only to the model API" does not apply: nufra does not start the process.
