# Foreman config

Filled in by `/master-foreman-setup`, or by hand. A blank field makes foreman ask, never guess.
Secrets never go here: store the name of an environment variable, not its value.

## Project

- name:
- what it does, in one line:
- words this project uses that an outsider would misread:

## Repos

Copy this block per repo.

### repo:

- path:
- stack:
- package manager:
- base branch:
- install command:
- start command:
- stop command:
- test command:
- lint command:
- typecheck command:
- end-to-end test folder:
- app URL:

## Local database

Commands read SQL from stdin and must reach this machine only.

- engine:
- read command:
- write command, test fixtures only:
- schema lookup hint:

## Test accounts

Names of environment variables, never values.

- login URL:
- username variable:
- password variable:

## Known sources

Off by default. Each one is used only when named in a run, by its key.
Example: `app-logs: /path/to/logs`

- none

## House rules

This company's own engineering rules. They sit on top of the pipeline's rules and win when they conflict.

- none
