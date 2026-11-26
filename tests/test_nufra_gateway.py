#!/usr/bin/env python3
"""nufra-gateway guards. Temp dirs and fake keys only; claude is never started (start uses --dry-run)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "adapters", "claude-gateway", "nufra-gateway")
HANDOFF = os.path.join(HERE, "..", "bin", "nufra-handoff")
FAKE = "fk-test-0000000000000000000000"


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout.strip()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp())
        self.key = os.path.join(self.tmp, "key")
        open(self.key, "w").write(FAKE + "\n")
        os.chmod(self.key, 0o600)
        self.profile = os.path.join(self.tmp, "p.json")
        self.write_profile()
        self.repo = os.path.join(self.tmp, "repo")
        os.makedirs(self.repo)
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "c1")
        self.run_dir = os.path.join(self.tmp, "runs", "r1")
        os.makedirs(self.run_dir)
        open(os.path.join(self.run_dir, "evidence.md"), "w").write("x\n")
        r = subprocess.run([sys.executable, HANDOFF, "write", self.run_dir, "--phase", "2 done, next 3", "--next",
                            "build", "--repo", self.repo, "--footprint", os.path.join(self.run_dir, "evidence.md")],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write_profile(self, **over):
        p = {"name": "gw", "base_url": "https://gw.example", "key_file": self.key, "model": "m-1"}
        p.update(over)
        json.dump({k: v for k, v in p.items() if v is not None}, open(self.profile, "w"))

    def tool(self, *args):
        return subprocess.run([sys.executable, TOOL, *args], capture_output=True, text=True)

    def start(self):
        return self.tool("start", "--profile", self.profile, "--run", self.run_dir, "--repo", self.repo, "--dry-run")


class Check(Base):
    def test_ok_hides_key_and_sets_one_model_everywhere(self):
        r = self.tool("check", "--profile", self.profile)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn(FAKE, r.stdout)
        for v in ("ANTHROPIC_MODEL", "ANTHROPIC_DEFAULT_HAIKU_MODEL", "CLAUDE_CODE_SUBAGENT_MODEL",
                  "CLAUDE_CODE_AUTO_MODE_MODEL"):
            self.assertIn(f"{v}=m-1", r.stdout)
        self.assertIn("--strict-mcp-config", r.stdout)

    def test_key_readable_by_others_refused(self):
        os.chmod(self.key, 0o644)
        r = self.tool("check", "--profile", self.profile)
        self.assertEqual(r.returncode, 4)
        self.assertIn("chmod 600", r.stdout)

    def test_http_refused(self):
        self.write_profile(base_url="http://gw.example")
        self.assertEqual(self.tool("check", "--profile", self.profile).returncode, 4)

    def test_key_inside_profile_refused(self):
        self.write_profile(api_key=FAKE)
        r = self.tool("check", "--profile", self.profile)
        self.assertEqual(r.returncode, 4)
        self.assertNotIn(FAKE, r.stdout)

    def test_missing_model_refused(self):
        self.write_profile(model=None)
        self.assertEqual(self.tool("check", "--profile", self.profile).returncode, 4)


class Start(Base):
    def test_dry_run_writes_nothing(self):
        r = self.start()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn('"dry_run": true', r.stdout)
        self.assertNotIn(FAKE, r.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.run_dir, ".pen.json")))

    def test_pen_held_refused(self):
        json.dump({"harness": "commandcode"}, open(os.path.join(self.run_dir, ".pen.json"), "w"))
        r = self.start()
        self.assertEqual(r.returncode, 4)
        self.assertIn("G4", r.stdout)

    def test_moved_code_refused(self):
        git(self.repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "c2")
        r = self.start()
        self.assertEqual(r.returncode, 4)
        self.assertIn("G5", r.stdout)

    def test_release_only_gateway_pen(self):
        pen = os.path.join(self.run_dir, ".pen.json")
        json.dump({"harness": "commandcode"}, open(pen, "w"))
        self.assertEqual(self.tool("release", "--run", self.run_dir).returncode, 4)
        json.dump({"harness": "claude@gw"}, open(pen, "w"))
        self.assertEqual(self.tool("release", "--run", self.run_dir).returncode, 0)
        self.assertFalse(os.path.exists(pen))


if __name__ == "__main__":
    unittest.main()
