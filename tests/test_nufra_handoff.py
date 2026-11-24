#!/usr/bin/env python3
"""Tests for nufra-handoff (M2: safe handoff.md write). Temp dirs only.

Run: bin/test
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "bin", "nufra-handoff")


def run(*args, env=None):
    e = dict(os.environ)
    e.update(env or {})
    return subprocess.run([sys.executable, TOOL, *args], capture_output=True, text=True, env=e)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout.strip()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.repo = os.path.join(self.tmp, "repo")
        os.makedirs(self.repo)
        git(self.repo, "init", "-q", "-b", "feat/demo")
        git(self.repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "c1")
        self.run_dir = os.path.join(self.repo, "runs", "demo")
        os.makedirs(self.run_dir)
        self.footprint = os.path.join(self.run_dir, "evidence.md")
        open(self.footprint, "w").write("phase 3 evidence\n")
        self.handoff = os.path.join(self.run_dir, "handoff.md")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, phase="3 done, next 4", nxt="start phase 4", *extra, env=None):
        return run("write", self.run_dir, "--phase", phase, "--next", nxt, "--repo", self.repo,
                   "--footprint", "runs/demo/evidence.md", "--cli-version", "9.9.9", *extra, env=env)

    def temps(self):
        return [n for n in os.listdir(self.run_dir) if n.startswith(".handoff.md.")]


class WriteTests(Base):
    def test_writes_all_fields(self):
        r = self.write()
        self.assertEqual(r.returncode, 0, r.stderr)
        text = open(self.handoff).read()
        for f in ("phase", "branch", "sha", "last footprint", "next action", "open gate",
                  "harness", "cli_version", "adapter", "written"):
            self.assertIn(f"- {f}: ", text)
        self.assertIn("- branch: feat/demo", text)
        self.assertIn("- sha: " + git(self.repo, "rev-parse", "HEAD"), text)
        self.assertEqual(self.temps(), [])

    def test_missing_field_writes_nothing(self):
        r = run("write", self.run_dir, "--phase", "3 done", "--next", "x", "--cli-version", "1.0.0")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("missing field", r.stderr)
        self.assertFalse(os.path.exists(self.handoff))

    def test_secret_refused(self):
        r = self.write("3 done", "use key sk-abcdefghijklmnop123")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("secret", r.stderr)
        self.assertFalse(os.path.exists(self.handoff))

    def test_unknown_harness_refused(self):
        r = self.write("3 done", "x", "--harness", "cursor")
        self.assertNotEqual(r.returncode, 0)

    def test_open_gate_needs_ts(self):
        self.assertNotEqual(self.write("2 done", "x", "--gate", "2.5").returncode, 0)
        r = self.write("2 done", "x", "--gate", "2.5", "--gate-ts", "123.456")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("- open gate: 2.5 (question ts 123.456)", open(self.handoff).read())

    def test_stop_appends_quota_row(self):
        self.write("3 done, next 4", "x", "--stop", "quota claude weekly", "--days-lost", "2")
        self.write("4 done, next 5", "y", "--stop", "quota claude session")
        stops = open(os.path.join(self.repo, "runs", "quota-stops.md")).read()
        self.assertEqual(stops.count("| date | run |"), 1)
        self.assertIn("| demo | 3 done, next 4 | quota claude weekly | 2 |", stops)
        self.assertIn("| demo | 4 done, next 5 | quota claude session | 0 |", stops)

    def test_stop_between_write_and_rename_keeps_old_file(self):
        self.write("3 done, next 4", "old")
        before = open(self.handoff).read()
        r = self.write("4 done, next 5", "new", env={"NUFRA_HANDOFF_TEST_CRASH": "before-rename"})
        self.assertEqual(r.returncode, 9)
        self.assertEqual(open(self.handoff).read(), before)  # old file intact, not half written
        self.assertEqual(len(self.temps()), 1)               # the stopped temp is left over
        self.assertEqual(run("check", self.run_dir, "--repo", self.repo).returncode, 0)
        self.write("4 done, next 5", "new")                  # next write cleans the old temp
        self.assertEqual(self.temps(), [])
        self.assertIn("- next action: new", open(self.handoff).read())


class CheckTests(Base):
    def test_ok(self):
        self.write()
        r = run("check", self.run_dir, "--repo", self.repo)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("resume at '3 done, next 4'", r.stdout)

    def test_no_handoff(self):
        self.assertEqual(run("check", self.run_dir).returncode, 1)

    def test_sha_mismatch(self):
        self.write()
        git(self.repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "c2")
        r = run("check", self.run_dir, "--repo", self.repo)
        self.assertEqual(r.returncode, 1)
        self.assertIn("sha mismatch", r.stdout)

    def test_branch_mismatch(self):
        self.write()
        git(self.repo, "checkout", "-q", "-b", "other")
        r = run("check", self.run_dir, "--repo", self.repo)
        self.assertIn("branch mismatch", r.stdout)

    def test_footprint_gone(self):
        self.write()
        os.remove(self.footprint)
        r = run("check", self.run_dir, "--repo", self.repo)
        self.assertIn("last footprint not found", r.stdout)

    def test_hand_edited_missing_field(self):
        self.write()
        text = open(self.handoff).read().replace("- adapter: none\n", "")
        open(self.handoff, "w").write(text)
        r = run("check", self.run_dir, "--repo", self.repo)
        self.assertIn("missing field(s): adapter", r.stdout)


class ThreeForcedPauses(Base):
    """Mechanism proof for M2: 3 pauses mid-phase, each resumes at the right phase, 0 phases redone.

    Each cycle: a phase is open, a stop hits while handoff.md is being written, the old handoff
    survives, the phase finishes at the boundary (ledger row + handoff), then a new session
    checks the handoff and resumes the next phase. The ledger must show each phase once.
    """

    def test_three_pauses(self):
        ledger = os.path.join(self.run_dir, "ledger.md")
        open(ledger, "w").write("| phase | status |\n|---|---|\n| 3 | done |\n")
        self.write("3 done, next 4", "start phase 4")
        for phase in (4, 5, 6):
            # stop arrives mid-phase, during a handoff write
            r = self.write(f"{phase} half", "x", env={"NUFRA_HANDOFF_TEST_CRASH": "before-rename"})
            self.assertEqual(r.returncode, 9)
            # resume: the handoff on disk still points at this phase, and it is safe
            c = run("check", self.run_dir, "--repo", self.repo)
            self.assertEqual(c.returncode, 0, c.stdout)
            self.assertIn(f"next {phase}'", c.stdout)
            # the resumed session finishes the phase once and moves the pointer
            with open(ledger, "a") as fh:
                fh.write(f"| {phase} | done |\n")
            self.assertEqual(self.write(f"{phase} done, next {phase + 1}", f"start phase {phase + 1}",
                                        "--stop", "forced test pause").returncode, 0)
        rows = [l for l in open(ledger).read().splitlines() if l.endswith("| done |")]
        phases = [l.split("|")[1].strip() for l in rows]
        self.assertEqual(phases, ["3", "4", "5", "6"])          # 0 phases redone, none skipped
        self.assertEqual(len(set(phases)), len(phases))
        stops = open(os.path.join(self.repo, "runs", "quota-stops.md")).read()
        self.assertEqual(stops.count("forced test pause"), 3)
        self.assertEqual(self.temps(), [])


if __name__ == "__main__":
    unittest.main()
