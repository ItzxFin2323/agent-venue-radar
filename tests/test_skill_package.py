import os
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillPackageTests(unittest.TestCase):
    def test_skill_frontmatter_is_minimal_and_valid(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(match)
        fields = {}
        for line in match.group(1).splitlines():
            key, value = line.split(":", 1)
            fields[key] = value.strip()
        self.assertEqual(set(fields), {"name", "description"})
        self.assertEqual(fields["name"], "agent-venue-radar")
        self.assertRegex(fields["name"], r"\A[a-z0-9]+(?:-[a-z0-9]+)*\Z")
        self.assertLessEqual(len(fields["name"]), 64)
        self.assertLessEqual(len(fields["description"]), 1024)
        self.assertNotRegex(fields["description"], r"[<>]")

    def test_openai_metadata_matches_skill(self):
        text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Agent Venue Radar"', text)
        self.assertIn("Screen AI-work venues", text)
        self.assertIn("$agent-venue-radar", text)
        self.assertIn("allow_implicit_invocation: true", text)

    def test_entrypoints_are_executable(self):
        for name in ("radar.py", "mcp_server.py"):
            self.assertTrue(os.access(ROOT / name, os.X_OK), name)


if __name__ == "__main__":
    unittest.main()
