#!/usr/bin/env python3
"""Refuse an MCP call unless its server is listed in ./foreman.mcp.json.

A plain `claude` still connects every MCP server in the user's global config, so this hook is
what keeps them out of a session that did not come through bin/master-foreman.
Exit 2 blocks the call and shows stderr to the model. A broken list blocks everything.
"""
import json
import os
import re
import sys


def normalise(name):
    # Claude Code turns anything outside [a-zA-Z0-9_-] into "_" in tool names.
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name)


def refuse(message):
    print(message, file=sys.stderr)
    sys.exit(2)


try:
    event = json.load(sys.stdin)
    tool = event["tool_name"]
except Exception as err:
    refuse(f"Could not read the tool call, so it is blocked: {err}")

if not tool.startswith("mcp__"):
    sys.exit(0)

server = tool.split("__")[1]
root = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
path = os.path.join(root, "foreman.mcp.json")

try:
    with open(path, encoding="utf-8") as handle:
        allowed = {normalise(name) for name in json.load(handle).get("mcpServers", {})}
except FileNotFoundError:
    allowed = set()
except Exception as err:
    refuse(f"{path} could not be read, so {tool} is blocked: {err}")

if server not in allowed:
    refuse(
        f"Blocked: MCP server '{server}' is not in foreman.mcp.json. This workspace uses local "
        "code and the local database only. To use it, the user adds it to foreman.mcp.json and "
        "hands it over for the run."
    )
