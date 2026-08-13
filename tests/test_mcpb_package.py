import json
import stat
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MCPBundleTests(unittest.TestCase):
    def test_manifest_matches_server_and_declares_no_secrets(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["manifest_version"], "0.3")
        self.assertEqual(manifest["name"], "agent-venue-radar")
        self.assertEqual(manifest["version"], "0.3.4")
        self.assertEqual(manifest["server"]["type"], "python")
        self.assertEqual(manifest["server"]["entry_point"], "mcp_server.py")
        self.assertEqual(
            manifest["server"]["mcp_config"]["command"],
            "${__dirname}/mcp_server.py",
        )
        self.assertEqual(manifest["server"]["mcp_config"]["args"], [])
        self.assertEqual(
            manifest["compatibility"]["platforms"],
            ["darwin", "linux"],
        )
        self.assertNotIn("user_config", manifest)
        self.assertNotIn("tools", manifest)

    def test_manifest_entry_point_and_dataset_exist(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(ROOT.joinpath(manifest["server"]["entry_point"]).is_file())
        self.assertTrue((ROOT / "radar.py").is_file())
        self.assertTrue((ROOT / "data" / "venues.json").is_file())

    def test_bundle_preserves_executable_python3_entry_point(self):
        bundle = ROOT / "dist" / "agent-venue-radar-0.3.4.mcpb"
        with zipfile.ZipFile(bundle) as archive:
            mode = archive.getinfo("mcp_server.py").external_attr >> 16

        self.assertTrue(mode & stat.S_IXUSR)


if __name__ == "__main__":
    unittest.main()
