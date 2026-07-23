import hashlib
import re
import unittest
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "publication-files.txt"
GENERATED_PARTS = {".git", "__pycache__"}
GENERATED_SUFFIXES = {".pyc"}
SENSITIVE_NAME = re.compile(
    r"(^|[._-])(credentials?|private[_-]?key|secrets?|tokens?)([._-]|$)",
    re.IGNORECASE,
)


def publication_paths():
    return [
        line.strip()
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class PublicationPayloadTests(unittest.TestCase):
    def test_publication_manifest_is_sorted_unique_and_uses_safe_paths(self):
        paths = publication_paths()

        self.assertEqual(paths, sorted(set(paths)))
        for value in paths:
            path = PurePosixPath(value)
            self.assertFalse(path.is_absolute(), value)
            self.assertNotIn("..", path.parts, value)
            self.assertFalse(SENSITIVE_NAME.search(path.name), value)

    def test_every_publication_file_is_regular_and_no_source_file_is_omitted(self):
        declared = set(publication_paths())
        discovered = set()

        for path in ROOT.rglob("*"):
            relative = path.relative_to(ROOT)
            if any(part in GENERATED_PARTS for part in relative.parts):
                continue
            if path.suffix in GENERATED_SUFFIXES:
                continue
            if path.is_file():
                discovered.add(relative.as_posix())

        self.assertEqual(declared, discovered)
        for value in declared:
            path = ROOT / value
            self.assertTrue(path.is_file(), value)
            self.assertFalse(path.is_symlink(), value)

    def test_release_checksum_file_matches_the_only_bundle(self):
        bundles = sorted((ROOT / "dist").glob("*.mcpb"))
        self.assertEqual(
            [path.name for path in bundles],
            ["agent-venue-radar-0.2.0.mcpb"],
        )

        expected_line = (ROOT / "dist" / "SHA256SUMS").read_text(
            encoding="utf-8"
        ).strip()
        digest, filename = expected_line.split(maxsplit=1)
        filename = filename.lstrip("*")
        self.assertEqual(filename, bundles[0].name)
        self.assertEqual(
            digest,
            hashlib.sha256(bundles[0].read_bytes()).hexdigest(),
        )

    def test_publish_workflow_is_pinned_to_the_frozen_release(self):
        workflow = (ROOT / ".github" / "workflows" / "publish.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("      - v0.2.0", workflow)
        self.assertIn("  contents: write", workflow)
        self.assertIn("  id-token: write", workflow)
        self.assertIn("sha256sum --check dist/SHA256SUMS", workflow)
        self.assertIn("releases/download/v1.7.9/", workflow)
        self.assertIn(
            "ab128162b0616090b47cf245afe0a23f3ef08936fdce19074f5ba0a4469281ac",
            workflow,
        )
        self.assertIn("/tmp/mcp-publisher login github-oidc", workflow)
        self.assertIn("/tmp/mcp-publisher publish", workflow)


if __name__ == "__main__":
    unittest.main()
