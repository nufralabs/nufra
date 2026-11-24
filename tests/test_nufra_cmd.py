#!/usr/bin/env python3
"""M4: Command Code hand-off adapter. Each guard test tries a call that must be refused.

Temp dirs only. Command Code itself is never started.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "adapters", "command-code", "nufra-cmd")
HANDOFF = os.path.join(HERE, "..", "bin", "nufra-handoff")


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout.strip()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.cmd_home = os.path.join(self.tmp, "cmdhome")
        os.makedirs(self.cmd_home)
        self.terms = os.path.join(self.tmp, "terms.txt")
        open(self.terms, "w").write("acmecorp\n")
        self.repo = os.path.join(self.tmp, "repo")
        os.makedirs(self.repo)
        git(self.repo, "init", "-q", "-b", "feat/demo")
        open(os.path.join(self.repo, "app.py"), "w").write("print(1)\n")
        git(self.repo, "add", ".")
        git(self.repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "c1")
        self.run_dir = os.path.join(self.tmp, "runs", "demo")
        os.makedirs(self.run_dir)
        open(os.path.join(self.run_dir, "evidence.md"), "w").write("x\n")
        self.brief = os.path.join(self.tmp, "brief.md")
        open(self.brief, "w").write("Find where app.py prints and why.\n")
        self.handoff("3 done, next 4")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def env(self):
        return dict(os.environ, NUFRA_CMD_HOME=self.cmd_home, NUFRA_FORBIDDEN_TERMS=self.terms)

    def handoff(self, phase, *extra):
        r = subprocess.run([sys.executable, HANDOFF, "write", self.run_dir, "--phase", phase, "--next", "go",
                            "--repo", self.repo, "--footprint", os.path.join(self.run_dir, "evidence.md"),
                            "--cli-version", "1.0.0", *extra], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def cmd(self, *args):
        return subprocess.run([sys.executable, TOOL, *args], capture_output=True, text=True, env=self.env())

    def prepare(self, *extra):
        return self.cmd("prepare", self.run_dir, "--repo", self.repo, "--phase", "4 investigate",
                        "--brief", self.brief, *extra)

    def collect(self):
        return self.cmd("collect", self.run_dir, "--repo", self.repo)

    def assertRefused(self, r, word):
        self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
        self.assertIn("REFUSED", r.stdout)
        self.assertIn(word, r.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.run_dir, ".pen.json")))


class Guard1Mcp(Base):
    def test_user_scope_server_refused(self):
        json.dump({"mcpServers": {"postgres": {"command": "x"}}}, open(os.path.join(self.cmd_home, "mcp.json"), "w"))
        self.assertRefused(self.prepare(), "G1 MCP")

    def test_project_mcp_json_refused(self):
        json.dump({"mcpServers": {"grafana": {"url": "x"}}}, open(os.path.join(self.repo, ".mcp.json"), "w"))
        self.assertRefused(self.prepare(), "G1 MCP")

    def test_local_scope_refused(self):
        d = os.path.join(self.cmd_home, "projects", "slug")
        os.makedirs(d)
        json.dump({"mcpServers": {"db": {}}}, open(os.path.join(d, "mcp.json"), "w"))
        self.assertRefused(self.prepare(), "G1 MCP")

    def test_unreadable_config_fails_closed(self):
        open(os.path.join(self.cmd_home, "mcp.json"), "w").write("{oops")
        self.assertRefused(self.prepare(), "G1 MCP")

    def test_allowlisted_server_passes(self):
        json.dump({"mcpServers": {"docs": {}}}, open(os.path.join(self.cmd_home, "mcp.json"), "w"))
        self.assertEqual(self.prepare("--allow-mcp", "docs").returncode, 0)


class Guard2Prod(Base):
    def test_prod_server_name_refused(self):
        open(self.brief, "w").write("Query postgres-prod-v2 for the row.\n")
        self.assertRefused(self.prepare(), "G2 prod")

    def test_forbidden_term_refused(self):
        open(self.brief, "w").write("Check the AcmeCorp tenant.\n")
        self.assertRefused(self.prepare(), "G2 prod")

    def test_word_product_is_fine(self):
        open(self.brief, "w").write("Read the product docs and production notes.\n")
        self.assertEqual(self.prepare().returncode, 0)


class Guard3Gate(Base):
    def test_open_gate_refused(self):
        self.handoff("2 done", "--gate", "2.5", "--gate-ts", "123.456")
        self.assertRefused(self.prepare(), "G3 gate")


class Guard4OneAgent(Base):
    def test_second_prepare_refused(self):
        self.assertEqual(self.prepare().returncode, 0)
        r = self.prepare()
        self.assertEqual(r.returncode, 4)
        self.assertIn("G4 one agent", r.stdout)

    def test_other_harness_in_handoff_refused(self):
        self.handoff("3 done, next 4", "--harness", "codex")
        self.assertRefused(self.prepare(), "G4 one agent")


class Flow(Base):
    def test_prepare_writes_brief_lock_handoff(self):
        r = self.prepare()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("cmd", r.stdout)
        brief = open(os.path.join(self.repo, ".nufra", "cmd-brief.md")).read()
        self.assertIn("Read only", brief)
        self.assertIn("Find where app.py prints", brief)
        self.assertIn("- harness: commandcode", open(os.path.join(self.run_dir, "handoff.md")).read())
        self.assertTrue(os.path.exists(os.path.join(self.run_dir, ".pen.json")))

    def write_result(self):
        open(os.path.join(self.repo, ".nufra", "cmd-result.md"), "w").write("app.py:1 prints 1\n")

    def test_collect_ok_hands_pen_back(self):
        self.prepare()
        self.write_result()
        r = self.collect()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.run_dir, "cmd-result.md")))
        self.assertFalse(os.path.exists(os.path.join(self.run_dir, ".pen.json")))
        self.assertFalse(os.path.exists(os.path.join(self.repo, ".nufra")))
        self.assertIn("- harness: claude", open(os.path.join(self.run_dir, "handoff.md")).read())

    def test_collect_refuses_code_change(self):
        self.prepare()
        self.write_result()
        open(os.path.join(self.repo, "app.py"), "a").write("print(2)\n")
        r = self.collect()
        self.assertEqual(r.returncode, 4)
        self.assertIn("outside .nufra", r.stdout)
        self.assertTrue(os.path.exists(os.path.join(self.run_dir, ".pen.json")))  # pen stays locked

    def test_collect_refuses_new_commit(self):
        self.prepare()
        self.write_result()
        git(self.repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "c2")
        r = self.collect()
        self.assertEqual(r.returncode, 4)
        self.assertIn("HEAD moved", r.stdout)

    def test_collect_refuses_missing_result(self):
        self.prepare()
        r = self.collect()
        self.assertEqual(r.returncode, 4)
        self.assertIn("no result", r.stdout)


if __name__ == "__main__":
    unittest.main()
