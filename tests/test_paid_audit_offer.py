import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WALLET = "0xfBae8Ea49EA6E4e8e7ED8A5e621807650d0f0198"


class PaidAuditOfferTests(unittest.TestCase):
    def test_offer_is_transparent_and_payment_is_after_delivery(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        terms = (ROOT / "PAID_AUDITS.md").read_text(encoding="utf-8")

        for document in (readme, terms):
            self.assertIn("1 USDC", document)
            self.assertIn("Base", document)
            self.assertIn(WALLET, document)
        self.assertIn("payable only after", readme)
        self.assertIn("Do not pay upfront", terms)
        self.assertRegex(terms, r"does not\s+guarantee")

    def test_request_form_forbids_secrets_and_requires_terms(self):
        template = (
            ROOT / ".github" / "ISSUE_TEMPLATE" / "custom-venue-audit.yml"
        ).read_text(encoding="utf-8")

        self.assertIn('title: "[Audit] "', template)
        self.assertIn("private keys", template)
        self.assertIn("seed phrases", template)
        self.assertEqual(template.count("required: true"), 5)

    def test_intake_workflow_has_narrow_permissions_and_no_untrusted_shell_data(self):
        workflow = (
            ROOT / ".github" / "workflows" / "audit-intake.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("  contents: read", workflow)
        self.assertIn("  issues: write", workflow)
        self.assertIn("Do not pay yet", workflow)
        self.assertIn(WALLET, workflow)
        self.assertNotIn("github.event.issue.body", workflow)
        self.assertNotIn("pull_request_target", workflow)


if __name__ == "__main__":
    unittest.main()
