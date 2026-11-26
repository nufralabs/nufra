#!/usr/bin/env python3
"""nufra-gateway guards. Temp dirs and fake keys only; claude is never started (start uses --dry-run)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import importlib.machinery
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "adapters", "claude-gateway", "nufra-gateway")
HANDOFF = os.path.join(HERE, "..", "bin", "nufra-handoff")
FAKE = "fk-test-0000000000000000000000"


def load_gateway():
    loader = importlib.machinery.SourceFileLoader("nufra_gateway_under_test", TOOL)
    mod = importlib.util.module_from_spec(importlib.util.spec_from_loader("nufra_gateway_under_test", loader))
    loader.exec_module(mod)
    return mod


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
        self.assertIn("apiKeyHelper", r.stdout)

    def test_subagent_model_moves_only_subagents(self):
        """G3 with one named exception: the subagent slot takes the profile's model, every other slot keeps m-1."""
        self.write_profile(subagent_model="free-1")
        r = self.tool("check", "--profile", self.profile)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("CLAUDE_CODE_SUBAGENT_MODEL=free-1", r.stdout)
        for v in ("ANTHROPIC_MODEL", "ANTHROPIC_DEFAULT_HAIKU_MODEL", "ANTHROPIC_DEFAULT_SONNET_MODEL",
                  "ANTHROPIC_DEFAULT_OPUS_MODEL", "ANTHROPIC_DEFAULT_FABLE_MODEL", "CLAUDE_CODE_AUTO_MODE_MODEL"):
            self.assertIn(f"{v}=m-1", r.stdout)

    def test_subagent_model_reaches_the_child_env(self):
        G = load_gateway()
        p = G.load_profile(self.profile)
        env = G.child_env(p, FAKE)
        self.assertEqual(env["CLAUDE_CODE_SUBAGENT_MODEL"], "m-1")
        self.write_profile(subagent_model="free-1")
        p = G.load_profile(self.profile)
        env = G.child_env(p, FAKE)
        self.assertEqual(env["CLAUDE_CODE_SUBAGENT_MODEL"], "free-1")
        self.assertEqual(env["ANTHROPIC_MODEL"], "m-1")
        self.assertEqual(env["CLAUDE_CODE_AUTO_MODE_MODEL"], "m-1")

    def test_subagent_model_must_be_a_string(self):
        self.write_profile(subagent_model=["a", "b"])
        r = self.tool("check", "--profile", self.profile)
        self.assertEqual(r.returncode, 4)
        self.assertIn("subagent_model", r.stdout)

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


class Permissions(Base):
    """A gateway window gets its own mode and tool list, in its own settings file. Other sessions keep theirs."""

    def settings_for(self, **over):
        """The real settings file the window will get, written by the real function."""
        self.write_profile(**over)
        G = load_gateway()
        prof = G.load_profile(self.profile)
        path = G.helper_settings(prof)
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))
        return json.load(open(path))

    def test_default_is_accept_edits_not_auto(self):
        """`auto` makes a second model judge every tool call. That is the wait and the tokens this fixes."""
        s = self.settings_for()
        self.assertEqual(s["permissions"]["defaultMode"], "acceptEdits")

    def test_allows_the_four_tools_with_no_matcher(self):
        allow = self.settings_for()["permissions"]["allow"]
        for tool in ("Bash", "Read", "Edit", "Write"):
            self.assertIn(tool, allow, f"{tool} must be allowed with no argument matcher")

    def test_auto_is_never_the_default(self):
        """Req: acceptEdits is the default. `auto` runs a second model on every tool call, which is the cost."""
        s = self.settings_for()
        self.assertEqual(s["permissions"]["defaultMode"], "acceptEdits")
        self.assertNotEqual(s["permissions"]["defaultMode"], "auto")

    def test_a_profile_may_still_choose_auto(self):
        """Banning it would take away the user's own choice, so a profile can opt in by name."""
        self.assertEqual(self.settings_for(default_mode="auto")["permissions"]["defaultMode"], "auto")

    def test_an_unknown_mode_is_refused(self):
        self.write_profile(default_mode="yolo")
        r = self.tool("check", "--profile", self.profile)
        self.assertEqual(r.returncode, 4)
        self.assertIn("default_mode", r.stdout)

    def test_profile_can_choose_a_documented_mode(self):
        self.assertEqual(self.settings_for(default_mode="plan")["permissions"]["defaultMode"], "plan")

    def test_key_is_still_only_a_helper_never_in_settings(self):
        s = self.settings_for()
        self.assertNotIn(FAKE, json.dumps(s))
        self.assertIn("apiKeyHelper", s)

    def test_global_settings_are_not_written(self):
        """The fix must never touch the user's own ~/.claude/settings.json."""
        global_path = os.path.expanduser("~/.claude/settings.json")
        before = open(global_path).read() if os.path.exists(global_path) else None
        self.settings_for()
        after = open(global_path).read() if os.path.exists(global_path) else None
        self.assertEqual(before, after, "the gateway wrote to the user's global settings")


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


class Delegation(Base):
    """A profile's delegation mode travels in the launch prompt, so every window it opens carries the rule."""

    def test_refuses_unknown_mode(self):
        self.write_profile(delegation="sometimes")
        r = self.tool("check", "--profile", self.profile)
        self.assertEqual(r.returncode, 4)
        self.assertIn("delegation must be one of", r.stdout)

    def test_check_names_the_mode(self):
        self.write_profile(delegation="always")
        r = self.tool("check", "--profile", self.profile)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("delegation=always", r.stdout)

    def test_no_mode_prints_no_line(self):
        r = self.tool("check", "--profile", self.profile)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn("delegation=", r.stdout)

    def test_note_names_the_subagent_model(self):
        self.write_profile(delegation="always", subagent_model="free-small")
        g = load_gateway()
        note = g.delegation_note(g.load_profile(self.profile))
        self.assertIn("free-small", note)
        self.assertIn("Batch", note)
        self.assertIn("Never let a subagent decide", note)

    def test_note_carries_the_orchestrator_rule(self):
        g = load_gateway()
        note = g.delegation_note({"model": "m-1", "subagent_model": "free-small", "delegation": "always"})
        self.assertIn("orchestrator, not the worker", note)
        self.assertIn("6 calls or fewer", note)
        self.assertIn("subagents here run on free-small", note)
        self.assertNotIn("cheaper inline", note)

    def test_note_falls_back_to_main_model(self):
        self.write_profile(delegation="always")
        g = load_gateway()
        note = g.delegation_note(g.load_profile(self.profile))
        self.assertIn("subagents here run on m-1", note)

    def test_no_delegation_means_empty_note(self):
        g = load_gateway()
        self.assertEqual(g.delegation_note(g.load_profile(self.profile)), "")

    def test_prompt_file_carries_the_note(self):
        """The end of the chain that matters: the note lands in the text the window reads.
        Checks launch_prompt, not `start`: start without --window execs claude, so it cannot be a test."""
        self.write_profile(delegation="always", subagent_model="free-small")
        g = load_gateway()
        body = g.launch_prompt("intro line", "resume point", g.load_profile(self.profile))
        self.assertIn("intro line", body)
        self.assertIn("free-small", body)
        self.assertIn("Batch", body)
        self.assertIn("resume point", body)
        # order matters: intro, then rules, then the resume point the rules must not be buried after
        self.assertLess(body.index("intro line"), body.index("Batch"))
        self.assertLess(body.index("Batch"), body.index("resume point"))

    def test_prompt_without_delegation_has_no_note(self):
        g = load_gateway()
        body = g.launch_prompt("intro line", "resume point", g.load_profile(self.profile))
        self.assertNotIn("Never let a subagent decide", body)
        self.assertEqual(body, "intro line\n\nresume point")

    def test_empty_intro_still_carries_the_note(self):
        self.write_profile(delegation="always")
        g = load_gateway()
        body = g.launch_prompt("", "resume point", g.load_profile(self.profile))
        self.assertFalse(body.startswith("\n"))
        self.assertTrue(body.startswith("Delegation"))


if __name__ == "__main__":
    unittest.main()
