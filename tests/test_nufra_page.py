#!/usr/bin/env python3
"""M6: read-only page. States, 127.0.0.1 only, missing files, no secrets or home path in HTML, 0 writes,
memory. Temp dirs only; usage comes from a fixture file, so no harness file is read."""
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "bin", "nufra-page")
HANDOFF = os.path.join(HERE, "..", "bin", "nufra-handoff")


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout.strip()


def make_fixture(tmp):
    """One run in each state. Returns the runs dir."""
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "c1")
    runs = os.path.join(tmp, "runs")

    def handoff(name, phase, nxt, *extra):
        d = os.path.join(runs, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "evidence.md"), "w").write("x\n")
        r = subprocess.run([sys.executable, HANDOFF, "write", d, "--phase", phase, "--next", nxt, "--repo", repo,
                            "--footprint", os.path.join(d, "evidence.md"), "--cli-version", "1.0.0", *extra],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        return d

    handoff("ask-run", "2 done", "wait for gate", "--gate", "2.5", "--gate-ts", "111.222")
    d = handoff("cmd-run", "3 done, next 4", "go")
    json.dump({"harness": "commandcode", "phase": "4 investigate", "started": "2026-11-24T10:00:00Z"},
              open(os.path.join(d, ".pen.json"), "w"))
    handoff("quota-run", "4 done, next 5", "start phase 5", "--stop", "quota claude weekly", "--days-lost", "1")
    handoff("done-run", "7 done", "none")
    handoff("idle-run", "1 done, next 2", "audit")
    d = handoff("broken-run", "1 done", "x")
    text = open(os.path.join(d, "handoff.md")).read().replace("- adapter: none\n", "")
    open(os.path.join(d, "handoff.md"), "w").write(text)
    os.makedirs(os.path.join(runs, "no-handoff-run"))  # ignored
    return runs


def tree(path):
    out = {}
    for dp, _, names in os.walk(path):
        for n in names:
            p = os.path.join(dp, n)
            st = os.stat(p)
            out[p] = (st.st_mtime_ns, st.st_size)
    return out


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp())
        self.runs = make_fixture(self.tmp)
        self.usage = os.path.join(self.tmp, "usage.json")
        json.dump({"harnesses": [
            {"harness": "claude", "status": "ok", "tokens_window": 4_700_000_000, "limit": None},
            {"harness": "codex", "status": "ok", "tokens_window": 0,
             "limit": {"used_percent": 82.0, "resets_at": "2026-11-27T01:31:24Z", "timestamp": "2026-11-06T10:49:49Z",
                       "file": os.path.expanduser("~/.codex/sessions/x.jsonl")}},
            {"harness": "commandcode", "status": "not installed", "limit": None}]}, open(self.usage, "w"))
        self.env = dict(os.environ, NUFRA_PAGE_USAGE_JSON=self.usage)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def once(self):
        r = subprocess.run([sys.executable, TOOL, "--runs", self.runs, "--once"], capture_output=True, text=True,
                           env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout


class States(Base):
    def test_each_state_has_shape_and_word(self):
        page = self.once()
        for run, state, shape in (("ask-run", "waiting", "■"), ("cmd-run", "working", "●"),
                                  ("quota-run", "paused", "⏸"), ("done-run", "done", "✓"),
                                  ("idle-run", "ready", "○"), ("broken-run", "unreadable", "!")):
            row = page.split(f"<td>{run}</td>", 1)[1].split("</tr>", 1)[0]
            self.assertIn(f'class="chip {state}"', row, run)
            self.assertIn(f">{shape}</span> {state}<", row, run)  # word and shape, not colour only
        self.assertNotIn("no-handoff-run", page)

    def test_accessibility_fixes(self):
        page = self.once()
        self.assertNotIn('http-equiv="refresh"', page)              # no auto reload by default (WCAG 2.2.1)
        self.assertIn('<span aria-hidden="true">■</span> Waiting', page)
        self.assertIn('class="scroll" tabindex="0" role="region" aria-label="Runs"', page)
        self.assertIn("font:16px", page)

    def test_waiting_on_top_and_first(self):
        page = self.once()
        self.assertIn("Waiting on you (1)", page)
        self.assertLess(page.index("<td>ask-run</td>"), page.index("<td>idle-run</td>"))
        self.assertIn("quota claude weekly", page)
        self.assertIn("Command Code", page)

    def test_usage_cards(self):
        page = self.once()
        self.assertIn("<b>82%?</b>", page)                 # old reading is marked, not shown as fresh
        self.assertIn("old: last seen", page)
        self.assertIn('aria-label="Codex: 82% used, stale, last seen', page)
        self.assertIn('aria-label="Claude: limit not on disk"', page)
        self.assertIn("resets 2026-11-27", page)
        self.assertIn("limit not on disk", page)          # Claude: dash with a reason, never 0%
        self.assertIn("not on this machine", page)

    def test_missing_runs_and_usage(self):
        os.remove(self.usage)
        r = subprocess.run([sys.executable, TOOL, "--runs", os.path.join(self.tmp, "nope"), "--once"],
                           capture_output=True, text=True, env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("No runs with a handoff.md yet", r.stdout)
        self.assertIn("did not answer", r.stdout)


class Sessions(Base):
    def write_sessions(self, windows=True):
        d = os.path.join(self.tmp, "listener")
        os.makedirs(d, exist_ok=True)
        now = time.time()
        json.dump({"C1:1.1": {"workspace": "shop", "cli": "claude", "topic": "build M2"},
                   "C1:2.2": {"workspace": "cafe", "cli": "claude", "topic": "ask council"},
                   "C1:3.3": {"workspace": "old", "cli": "claude", "topic": "closed window"}},
                  open(os.path.join(d, "sessions.json"), "w"))
        json.dump({"C1:1.1": {"text": "Phase 3: reproducing", "at": now - 30, "state": "working", "step": "3/7"},
                   "C1:2.2": {"text": "Waiting for you: pick 1 or 2", "at": now - 600, "state": "waiting"},
                   "C1:3.3": {"text": "Done", "at": now - 60, "state": "done"}},
                  open(os.path.join(d, "progress.json"), "w"))
        if windows:
            json.dump({"C1:1.1": 1, "C1:2.2": 2}, open(os.path.join(d, "windows.json"), "w"))
        open(os.path.join(d, "config.json"), "w").write('{"bot_token": "xoxb-secret-token-123456"}')
        return d

    def page(self, d):
        r = subprocess.run([sys.executable, TOOL, "--runs", self.runs, "--sessions", d, "--once"],
                           capture_output=True, text=True, env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_open_windows_only_and_waiting_on_top(self):
        page = self.page(self.write_sessions())
        self.assertIn("<h2>Slack sessions</h2>", page)
        self.assertIn("Phase 3: reproducing", page)
        self.assertIn('aria-label="step 3 of 7"', page)
        self.assertNotIn("closed window", page)               # window gone: not shown, like the Home tab
        self.assertIn("Waiting on you (2)", page)              # 1 run + 1 session
        self.assertLess(page.index("pick 1 or 2"), page.index("Phase 3: reproducing"))
        self.assertNotIn("xoxb-secret", page)                  # the token file is never read

    def test_without_windows_file_uses_age(self):
        page = self.page(self.write_sessions(windows=False))
        self.assertIn("closed window", page)                   # done 1 min ago: inside 24 h

    def test_off_by_default(self):
        self.assertNotIn("Slack sessions", self.once())


class Privacy(Base):
    def test_no_home_path_no_secret(self):
        d = os.path.join(self.runs, "idle-run")
        text = open(os.path.join(d, "handoff.md")).read().replace(
            "- next action: audit", "- next action: use sk-abcdefghijklmnop123 then <script>x</script>")
        open(os.path.join(d, "handoff.md"), "w").write(text)
        page = self.once()
        self.assertNotIn(os.path.expanduser("~") + "/", page)
        self.assertNotIn("sk-abcdefghijklmnop123", page)
        self.assertIn("[hidden]", page)
        self.assertNotIn("<script>", page)                # escaped
        self.assertNotIn("http://", page.replace('http-equiv', ''))  # no external resource


class Server(Base):
    def setUp(self):
        super().setUp()
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            self.port = s.getsockname()[1]
        self.before = tree(self.tmp)
        self.proc = subprocess.Popen([sys.executable, TOOL, "--runs", self.runs, "--port", str(self.port)],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env, cwd=self.tmp)
        self.proc.stdout.readline()

    def tearDown(self):
        self.proc.terminate()
        self.proc.wait(5)
        self.proc.stdout.close()
        self.proc.stderr.close()
        super().tearDown()

    def get(self, path="/", host=None, method="GET"):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", method=method)
        if host:
            req.add_header("Host", host)
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, r.read().decode(), dict(r.headers)
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode(), dict(e.headers)

    def test_serves_page_and_favicon(self):
        code, body, headers = self.get()
        self.assertEqual(code, 200)
        self.assertIn("Waiting on you (1)", body)
        self.assertIn("default-src 'none'", headers["Content-Security-Policy"])
        code, body, headers = self.get("/favicon.svg")
        self.assertEqual(code, 200)
        self.assertIn("<svg", body)

    def test_loopback_only(self):
        out = subprocess.run(["lsof", "-nP", "-a", "-p", str(self.proc.pid), "-iTCP", "-sTCP:LISTEN"],
                             capture_output=True, text=True).stdout
        self.assertIn(f"127.0.0.1:{self.port}", out)
        self.assertNotIn("*:", out)

    def test_auto_reload_is_opt_in(self):
        self.assertNotIn('http-equiv="refresh"', self.get()[1])
        body = self.get("/?auto=30")[1]
        self.assertIn('http-equiv="refresh" content="30"', body)
        self.assertIn("Stop auto-reload", body)

    def test_other_host_refused(self):
        self.assertEqual(self.get(host="evil.example")[0], 421)  # DNS rebinding

    def test_read_only(self):
        self.assertEqual(self.get(method="POST")[0], 405)
        self.assertEqual(self.get("/../handoff.md")[0], 404)
        for _ in range(3):
            self.get()
        self.assertEqual(tree(self.tmp), self.before)  # 0 writes

    def test_memory_under_50_mb(self):
        for _ in range(20):
            self.get()
        rss_kb = int(subprocess.run(["ps", "-o", "rss=", "-p", str(self.proc.pid)],
                                    capture_output=True, text=True).stdout.strip())
        self.assertLess(rss_kb, 50 * 1024, f"{rss_kb} KB")


if __name__ == "__main__":
    unittest.main()
