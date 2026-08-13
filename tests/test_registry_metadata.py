import hashlib
import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]


class RegistryMetadataTests(unittest.TestCase):
    def test_server_json_points_to_the_public_release(self):
        metadata = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
        package = metadata["packages"][0]

        self.assertEqual(
            metadata["$schema"],
            "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
        )
        self.assertEqual(
            metadata["name"], "io.github.ItzxFin2323/agent-venue-radar"
        )
        self.assertGreaterEqual(len(metadata["description"]), 1)
        self.assertLessEqual(len(metadata["description"]), 100)
        self.assertEqual(metadata["version"], "0.3.4")
        self.assertEqual(package["registryType"], "mcpb")
        self.assertEqual(package["transport"], {"type": "stdio"})
        self.assertEqual(
            package["identifier"],
            "https://github.com/ItzxFin2323/agent-venue-radar/releases/"
            "download/v0.3.4/agent-venue-radar-0.3.4.mcpb",
        )

    def test_mcpb_metadata_satisfies_official_registry_static_rules(self):
        metadata = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
        package = metadata["packages"][0]
        identifier = package["identifier"]
        parsed = urlparse(identifier)

        self.assertEqual(parsed.scheme, "https")
        self.assertIn(parsed.hostname, {"github.com", "www.github.com"})
        self.assertIn("mcp", identifier.lower())
        self.assertNotIn("registryBaseUrl", package)
        self.assertRegex(package["fileSha256"], r"^[a-f0-9]{64}$")
        self.assertRegex(
            parsed.path,
            re.compile(
                r"^/[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?"
                r"/[A-Za-z0-9._-]+/releases/download/[^/]+/[^/]+$"
            ),
        )

    def test_registry_hash_matches_bundle(self):
        metadata = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
        bundle = ROOT / "dist" / "agent-venue-radar-0.3.4.mcpb"
        digest = hashlib.sha256(bundle.read_bytes()).hexdigest()

        self.assertEqual(metadata["packages"][0]["fileSha256"], digest)


if __name__ == "__main__":
    unittest.main()
