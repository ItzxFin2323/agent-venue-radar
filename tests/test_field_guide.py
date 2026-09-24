"""Keep the public proof example reproducible against the real CLI."""

import json
import re
import shlex
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FieldGuideTests(unittest.TestCase):
    def test_published_commands_produce_the_claimed_verdicts(self):
        guide = (ROOT / "FIELD_GUIDE.md").read_text(encoding="utf-8")
        commands = re.findall(r"^python3 radar\.py evaluate .+$", guide, re.M)
        self.assertEqual(len(commands), 2)
        results = []
        for command in commands:
            args = shlex.split(command)
            completed = subprocess.run(
                [sys.executable, "-B", str(ROOT / args[1]), *args[2:]],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            results.append(json.loads(completed.stdout))
        blocked, conditional = results
        self.assertEqual(blocked["score"], 80)
        self.assertEqual(blocked["verdict"], "avoid_until_change")
        self.assertEqual(blocked["hard_blockers"], ["funding:underfunded"])
        self.assertEqual(conditional["score"], 100)
        self.assertEqual(conditional["verdict"], "continue_with_conditions")
        self.assertEqual(conditional["hard_blockers"], [])
        differences = [
            key for key in blocked["signals"]
            if blocked["signals"][key] != conditional["signals"][key]
        ]
        self.assertEqual(differences, ["funding"])

    def test_copy_labels_the_proof_and_payment_limits(self):
        guide = (ROOT / "FIELD_GUIDE.md").read_text(encoding="utf-8")
        for phrase in (
            "synthetic walkthrough", "not an 80% probability", "historical",
            "does not independently verify", "no direct-wallet or card checkout",
            "Opening an", "does not order an audit", "not a customer testimonial",
        ):
            self.assertIn(phrase, guide)


if __name__ == "__main__":
    unittest.main()
