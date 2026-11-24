#!/usr/bin/env python3
"""nufra init: proposes from evidence, never overwrites, never reads a real .env. Temp dirs only."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "bin", "nufra-init")


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout.strip()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp())
        self.repo = os.path.join(self.tmp, "shop")
        os.makedirs(self.repo)
        git(self.repo, "init", "-q", "-b", "main")
        write(os.path.join(self.repo, "package.json"), json.dumps({
            "scripts": {"dev": "next dev", "test": "vitest", "lint": "eslint ."},
            "devDependencies": {"typescript": "5", "next": "15"}}))
        write(os.path.join(self.repo, "pnpm-lock.yaml"), "lockfileVersion: 9\n")
        write(os.path.join(self.repo, ".github", "workflows", "ci.yml"),
              "jobs:\n  t:\n    steps:\n      - run: pnpm test --run\n      - run: pnpm typecheck\n")
        write(os.path.join(self.repo, "docker-compose.yml"), "services:\n  db:\n    image: postgres:16\n")
        write(os.path.join(self.repo, ".env.example"),
              "APP_URL=http://localhost:3000\nDATABASE_URL=postgres://u:p@localhost/db\nAPI_KEY=\n")
        write(os.path.join(self.repo, ".env"), "API_KEY=sk-realsecretvalue123456\nSTAGING_URL=https://real.example\n")
        write(os.path.join(self.repo, "playwright.config.ts"), "export default {}\n")
        os.makedirs(os.path.join(self.repo, "e2e"))
        git(self.repo, "add", ".")
        git(self.repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "c1")
        self.ws = os.path.join(self.tmp, "ws")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def init(self, *extra, stdin=None):
        return subprocess.run([sys.executable, TOOL, self.repo, "--workspace", self.ws, *extra],
                              capture_output=True, text=True, input=stdin)

    def config(self):
        return open(os.path.join(self.ws, "foreman.config.md")).read()


class Proposal(Base):
    def test_values_come_with_sources(self):
        r = self.init("--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = r.stdout
        self.assertIn("pnpm   <- pnpm-lock.yaml", out)
        self.assertIn("typescript (next)", out)
        self.assertIn("pnpm test --run   <- .github/workflows/ci.yml", out)  # CI wins over scripts
        self.assertIn("pnpm typecheck   <- .github/workflows/ci.yml", out)
        self.assertIn("pnpm lint   <- package.json scripts.lint", out)
        self.assertIn("http://localhost:3000   <- .env.example APP_URL", out)
        self.assertIn("postgres   <- docker-compose.yml", out)
        self.assertIn("e2e", out)
        self.assertFalse(os.path.exists(self.ws))  # dry run writes nothing

    def test_real_env_never_read(self):
        out = self.init("--dry-run").stdout
        self.assertNotIn("sk-realsecret", out)
        self.assertNotIn("real.example", out)
        self.assertNotIn("u:p@", out)  # database URL value from the sample stays out too

    def test_no_evidence_stays_blank(self):
        bare = os.path.join(self.tmp, "bare")
        os.makedirs(bare)
        git(bare, "init", "-q", "-b", "main")
        r = subprocess.run([sys.executable, TOOL, bare, "--workspace", self.ws, "--yes"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        cfg = self.config()
        self.assertIn("- test command:\n", cfg)
        self.assertIn("- stack:\n", cfg)
        self.assertIn("- read command:\n", cfg)


class Write(Base):
    def test_yes_writes_config_and_core(self):
        r = self.init("--yes")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        cfg = self.config()
        self.assertIn("### repo: shop", cfg)
        self.assertIn(f"- path: {self.repo}", cfg)
        self.assertIn("- package manager: pnpm", cfg)
        self.assertIn("- read command:\n", cfg)  # database commands stay blank
        for rel in (".claude/settings.json", ".claude/hooks/block-undeclared-mcp.py",
                    ".claude/skills/master-foreman/SKILL.md",
                    ".claude/skills/master-foreman/references/proof-gate.md", "foreman.mcp.json"):
            self.assertTrue(os.path.exists(os.path.join(self.ws, rel)), rel)
        self.assertTrue(os.access(os.path.join(self.ws, ".claude/hooks/block-undeclared-mcp.py"), os.X_OK))
        self.assertTrue(os.path.islink(os.path.join(self.ws, "master-foreman")))

    def test_confirm_no_writes_nothing(self):
        # no terminal: refuses instead of prompting
        r = self.init(stdin="y\n")
        self.assertEqual(r.returncode, 4)
        self.assertIn("--yes", r.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.ws, "foreman.config.md")))

    def test_existing_config_refused(self):
        os.makedirs(self.ws)
        write(os.path.join(self.ws, "foreman.config.md"), "mine\n")
        r = self.init("--yes")
        self.assertEqual(r.returncode, 4)
        self.assertEqual(open(os.path.join(self.ws, "foreman.config.md")).read(), "mine\n")

    def test_existing_claude_files_kept(self):
        write(os.path.join(self.ws, ".claude", "settings.json"), '{"mine": true}\n')
        r = self.init("--yes")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(open(os.path.join(self.ws, ".claude", "settings.json")).read(), '{"mine": true}\n')
        self.assertIn("kept 1", r.stdout)


class Refusals(Base):
    def test_not_a_repo(self):
        plain = os.path.join(self.tmp, "plain")
        os.makedirs(plain)
        r = subprocess.run([sys.executable, TOOL, plain, "--workspace", self.ws, "--yes"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 4)
        self.assertIn("git repository", r.stdout)

    def test_workspace_inside_nufra_refused(self):
        inside = os.path.join(HERE, "..", "tmp-ws")
        r = subprocess.run([sys.executable, TOOL, self.repo, "--workspace", inside, "--yes"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 4)
        self.assertFalse(os.path.exists(inside))


if __name__ == "__main__":
    unittest.main()
