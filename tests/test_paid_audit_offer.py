import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGRENTING_DID = "did:web:github.com:ItzxFin2323:agent-venue-radar"


class PaidAuditOfferTests(unittest.TestCase):
    def test_offer_is_transparent_and_uses_prefunded_escrow(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        terms = (ROOT / "PAID_AUDITS.md").read_text(encoding="utf-8")

        for document in (readme, terms):
            self.assertIn("$0.20", document)
            self.assertIn("Agrenting", document)
            self.assertIn(AGRENTING_DID, document)
            self.assertIn("escrow", document)
            self.assertIn("marketplace_due_diligence", document)
        self.assertIn("no direct-wallet payment route", readme)
        self.assertIn("There is no direct-wallet payment route", terms)
        self.assertRegex(terms, r"does not\s+guarantee")

    def test_request_form_forbids_secrets_and_requires_terms(self):
        template = (
            ROOT / ".github" / "ISSUE_TEMPLATE" / "custom-venue-audit.yml"
        ).read_text(encoding="utf-8")

        self.assertIn('title: "[Audit scope] "', template)
        self.assertIn("private keys", template)
        self.assertIn("seed phrases", template)
        self.assertEqual(template.count("required: true"), 5)

    def test_intake_workflow_has_narrow_permissions_and_no_untrusted_shell_data(self):
        workflow = (
            ROOT / ".github" / "workflows" / "audit-intake.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("  contents: read", workflow)
        self.assertIn("  issues: write", workflow)
        self.assertIn("does not start paid work", workflow)
        self.assertIn(AGRENTING_DID, workflow)
        self.assertIn("price `0.20`", workflow)
        self.assertIn("pre-funded escrow", workflow)
        self.assertNotIn("github.event.issue.body", workflow)
        self.assertNotIn("pull_request_target", workflow)


if __name__ == "__main__":
    unittest.main()
