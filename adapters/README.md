# Adapters

One launcher per harness. Empty in v0.1-M0.

Rule: an adapter may run only after it passes 4 of 4 guard tests, and each test tries a call that must be refused:
1. a prod MCP call fails;
2. network goes only to the model API;
3. a gate stops when there is no quoted approval;
4. only one agent runs at a time.

Claude Code is the only coordinator. Another harness runs one phase from a brief and `handoff.md`, and never opens a gate.
