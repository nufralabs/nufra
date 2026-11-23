"""Fail if a personal or company term (whole word, any case) appears in the working tree or in any commit.

The terms live OUTSIDE the repo (so the list itself leaks nothing):
  $NUFRA_FORBIDDEN_FILE, default ~/.config/nufra/forbidden-terms.txt, one term per line, '#' for comments.
If the file is missing the test is skipped and says so.
"""
import os
import re
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TERMS_FILE = os.environ.get("NUFRA_FORBIDDEN_FILE",
                            os.path.expanduser("~/.config/nufra/forbidden-terms.txt"))


def load_terms():
    with open(TERMS_FILE, encoding="utf-8") as f:
        return [t.strip() for t in f if t.strip() and not t.startswith("#")]


@unittest.skipUnless(os.path.isfile(TERMS_FILE), f"no terms file at {TERMS_FILE}")
class NoPersonalData(unittest.TestCase):
    def test_working_tree(self):
        hits = []
        for term in load_terms():
            r = subprocess.run(["git", "-C", ROOT, "grep", "-I", "-i", "-w", "-n", "-F", "--untracked", term],
                               capture_output=True, text=True)
            hits += [f"{term!r}: {line}" for line in r.stdout.splitlines()]
        self.assertEqual(hits, [], "\n".join(hits))

    def test_all_history(self):
        if subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True).returncode:
            self.skipTest("no commits yet")
        log = subprocess.run(["git", "-C", ROOT, "log", "--all", "-p", "--format=%B"],
                             capture_output=True, text=True).stdout.lower()
        found = [t for t in load_terms() if re.search(r"(?<![a-z0-9])" + re.escape(t.lower()) + r"(?![a-z0-9])", log)]
        self.assertEqual(found, [], f"terms found in history: {len(found)}")


if __name__ == "__main__":
    unittest.main()
