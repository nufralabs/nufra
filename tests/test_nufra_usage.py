#!/usr/bin/env python3
"""Tests for nufra-usage. Stdlib unittest, fixtures in a temp dir only.

Run: bin/test
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "bin", "nufra-usage")
PROMPT = "SECRET-PROMPT-TEXT-do-not-print"
REPLY = "SECRET-REPLY-TEXT-do-not-print"
KEY = "sk-FAKEKEY-do-not-print"


def ts(days_ago=0.0):
    t = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days_ago)
    return t.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


def make_claude(home):
    p = os.path.join(home, ".claude", "projects", "-tmp-proj", "s1.jsonl")
    usage = {"input_tokens": 10, "output_tokens": 20,
             "cache_creation_input_tokens": 30, "cache_read_input_tokens": 40}
    write_jsonl(p, [
        {"type": "user", "timestamp": ts(0.1), "message": {"role": "user", "content": PROMPT}},
        {"type": "assistant", "timestamp": ts(0.1), "requestId": "r1",
         "message": {"id": "m1", "content": [{"type": "text", "text": REPLY}], "usage": usage}},
        # duplicate streaming line of the same message: must not double count
        {"type": "assistant", "timestamp": ts(0.1), "requestId": "r1",
         "message": {"id": "m1", "content": [{"type": "text", "text": REPLY}], "usage": usage}},
        # record with no usage field
        {"type": "assistant", "timestamp": ts(0.1), "requestId": "r2",
         "message": {"id": "m2", "content": [{"type": "text", "text": REPLY}]}},
        # outside the 7-day window
        {"type": "assistant", "timestamp": ts(9), "requestId": "r3",
         "message": {"id": "m3", "usage": {"input_tokens": 999999}}},
    ])


def codex_rows():
    def tc(days, total, primary=True):
        return {"timestamp": ts(days), "type": "event_msg", "payload": {
            "type": "token_count",
            "info": {"total_token_usage": {"input_tokens": total - 5, "cached_input_tokens": 1,
                                           "output_tokens": 5, "reasoning_output_tokens": 0,
                                           "total_tokens": total}},
            "rate_limits": {"primary": {"used_percent": 42.0, "window_minutes": 10080,
                                        "resets_at": 1795743084}} if primary else None}}
    return [
        {"timestamp": ts(8), "type": "session_meta", "payload": {"base_instructions": {"text": PROMPT}}},
        {"timestamp": ts(8), "type": "response_item", "payload": {"type": "message", "content": PROMPT}},
        tc(8, 1000),          # before window: baseline of the cumulative counter
        tc(1, 1500),
        {"timestamp": ts(1), "type": "event_msg", "payload": {"type": "token_count", "info": None,
                                                               "rate_limits": None}},  # no usage
        tc(0.5, 1700),        # window tokens = 1700 - 1000 = 700
        {"timestamp": ts(0.5), "type": "event_msg", "payload": {"type": "agent_message", "message": REPLY}},
    ]


def make_codex(home, zst=False):
    d = os.path.join(home, ".codex", "sessions", "2026", "11", "20")
    p = os.path.join(d, "rollout-x.jsonl")
    write_jsonl(p, codex_rows())
    with open(os.path.join(home, ".codex", "auth.json"), "w") as fh:
        json.dump({"OPENAI_API_KEY": KEY}, fh)
    if zst:
        subprocess.run([shutil.which("zstd"), "-q", "--rm", p], check=True)


def make_gemini(home):
    p = os.path.join(home, ".gemini", "tmp", "proj", "chats", "session-1.json")
    os.makedirs(os.path.dirname(p))
    with open(p, "w") as fh:
        json.dump({"sessionId": "s", "messages": [
            {"id": "u1", "timestamp": ts(0.2), "type": "user", "content": PROMPT},
            {"id": "g1", "timestamp": ts(0.2), "type": "gemini", "content": REPLY,
             "tokens": {"input": 100, "output": 7, "cached": 50, "thoughts": 3, "tool": 0, "total": 110}},
            {"id": "g2", "timestamp": ts(0.2), "type": "gemini", "content": REPLY},  # no usage
        ]}, fh)
    with open(os.path.join(home, ".gemini", "oauth_creds.json"), "w") as fh:
        json.dump({"access_token": KEY}, fh)


def run(home, *args):
    out = subprocess.run([sys.executable, TOOL, "--home", home] + list(args),
                         capture_output=True, text=True, check=True)
    return out.stdout


class CorvusUsageTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="nufra-test-")

    def tearDown(self):
        shutil.rmtree(self.home)

    def by_name(self, *args):
        data = json.loads(run(self.home, "--json", *args))
        return {h["harness"]: h for h in data["harnesses"]}

    def test_all_missing_prints_not_configured(self):
        out = run(self.home)
        for h in ("claude", "codex", "gemini"):
            self.assertRegex(out, r"(?m)^%s\s+\| not configured$" % h)

    def test_claude_present_dedup_and_no_usage(self):
        make_claude(self.home)
        r = self.by_name()["claude"]
        self.assertEqual(r["tokens_window"], 100)
        self.assertEqual(r["records_with_usage"], 1)
        self.assertEqual(r["records_without_usage"], 1)
        self.assertIsNone(r["limit"])
        self.assertIn("weekly limit: not measured", run(self.home).splitlines()[0])

    def test_short_table(self):
        make_claude(self.home)
        make_codex(self.home)
        out = run(self.home, "--short")
        lines = out.strip().splitlines()
        self.assertTrue(all(len(l) <= 40 for l in lines), lines)
        self.assertRegex(lines[1], r"^claude\s+100\s+— not on disk$")
        self.assertRegex(lines[2], r"^codex\s+700\s+42% used to 11-27$")
        self.assertRegex(lines[3], r"^gemini\s+—\s+not configured$")
        self.assertNotIn("0%", lines[1])

    def test_codex_plain_jsonl(self):
        make_codex(self.home)
        r = self.by_name()["codex"]
        self.assertEqual(r["tokens_window"], 700)
        self.assertEqual(r["records_without_usage"], 1)
        self.assertEqual(r["limit"]["used_percent"], 42.0)
        self.assertEqual(r["limit"]["window_minutes"], 10080)
        self.assertEqual(r["limit"]["resets_at"], "2026-11-27T01:31:24Z")

    @unittest.skipUnless(shutil.which("zstd"), "zstd binary not installed")
    def test_codex_zst(self):
        make_codex(self.home, zst=True)
        r = self.by_name()["codex"]
        self.assertEqual(r["tokens_window"], 700)
        self.assertIn("zstd", r["method"])

    def test_codex_sqlite_fallback(self):
        import sqlite3
        make_codex(self.home)
        db = os.path.join(self.home, ".codex", "state_5.sqlite")
        con = sqlite3.connect(db)
        con.execute("CREATE TABLE threads (id TEXT, tokens_used INTEGER, updated_at INTEGER, title TEXT)")
        now = int(dt.datetime.now(dt.timezone.utc).timestamp())
        con.executemany("INSERT INTO threads VALUES (?,?,?,?)",
                        [("a", 300, now - 3600, PROMPT), ("b", 5000, now - 10 * 86400, PROMPT)])
        con.commit()
        con.close()
        r = self.by_name("--codex-sqlite")["codex"]
        self.assertEqual(r["tokens_window"], 300)
        self.assertIn("state_5.sqlite", r["method"])

    def test_gemini_present(self):
        make_gemini(self.home)
        r = self.by_name()["gemini"]
        self.assertEqual(r["tokens_window"], 110)
        self.assertEqual(r["records_without_usage"], 1)

    def test_no_prompt_reply_or_key_in_any_output(self):
        make_claude(self.home)
        make_codex(self.home)
        make_gemini(self.home)
        for out in (run(self.home), run(self.home, "--json")):
            for secret in (PROMPT, REPLY, KEY, "SECRET", "sk-"):
                self.assertNotIn(secret, out)
        self.assertEqual(len(run(self.home).splitlines()), 3)

    def test_writes_nothing(self):
        make_claude(self.home)
        make_codex(self.home)
        make_gemini(self.home)

        def snap():
            s = {}
            for d, _, ns in os.walk(self.home):
                for n in ns:
                    p = os.path.join(d, n)
                    s[p] = (os.path.getsize(p), os.path.getmtime(p))
            return s
        before = snap()
        run(self.home)
        run(self.home, "--json")
        self.assertEqual(before, snap())


if __name__ == "__main__":
    unittest.main(verbosity=2)
