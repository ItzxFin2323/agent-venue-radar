import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MCPBundleTests(unittest.TestCase):
    def test_manifest_matches_server_and_declares_no_secrets(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["manifest_version"], "0.3")
        self.assertEqual(manifest["name"], "agent-venue-radar")
        self.assertEqual(manifest["version"], "0.3.1")
        self.assertEqual(manifest["server"]["type"], "python")
        self.assertEqual(manifest["server"]["entry_point"], "mcp_server.py")
        self.assertEqual(
            manifest["server"]["mcp_config"]["args"],
            ["${__dirname}/mcp_server.py"],
        )
        self.assertNotIn("user_config", manifest)
        self.assertNotIn("tools", manifest)

    def test_manifest_entry_point_and_dataset_exist(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(ROOT.joinpath(manifest["server"]["entry_point"]).is_file())
        self.assertTrue((ROOT / "radar.py").is_file())
        self.assertTrue((ROOT / "data" / "venues.json").is_file())


if __name__ == "__main__":
    unittest.main()
