import importlib.util
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RADAR_PATH = ROOT / "radar.py"
DATA_PATH = ROOT / "data" / "venues.json"

SPEC = importlib.util.spec_from_file_location("radar", RADAR_PATH)
assert SPEC and SPEC.loader
radar = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(radar)


class RadarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = radar.load_data(DATA_PATH)

    def test_dataset_has_twenty_unique_venues(self):
        venues = self.data["venues"]
        self.assertEqual(len(venues), 20)
        self.assertEqual(len({venue["id"] for venue in venues}), 20)

    def test_only_taskmarket_survives_current_hard_blockers(self):
        results = [radar.assess(venue) for venue in self.data["venues"]]
        survivors = [
            result
            for result in results
            if result["verdict"] != "avoid_until_change"
        ]
        self.assertEqual([result["id"] for result in survivors], ["taskmarket"])
        self.assertEqual(survivors[0]["verdict"], "continue_with_conditions")

    def test_dataset_contract_rejects_uncited_or_malformed_maintenance(self):
        cases = (
            ("checked_at", "July 23, 2026", "must be an ISO date"),
            ("sources", ["not-a-url"], "must be an HTTPS URL"),
            ("evidence", "", "must be a non-empty string"),
            ("conditions", [], "must contain at least one"),
        )
        for field, value, message in cases:
            with self.subTest(field=field):
                malformed = copy.deepcopy(self.data)
                malformed["venues"][0][field] = value
                with self.assertRaisesRegex(radar.RadarError, message):
                    radar.validate_data(malformed)

    def test_dataset_contract_rejects_unknown_signal_criteria(self):
        malformed = copy.deepcopy(self.data)
        malformed["venues"][0]["signals"]["reputation"] = "excellent"
        with self.assertRaisesRegex(radar.RadarError, "unknown criteria: reputation"):
            radar.validate_data(malformed)

    def test_real_escrow_does_not_override_negative_economics(self):
        venue = radar.find_venue(self.data["venues"], "agentbounties")
        result = radar.assess(venue)
        self.assertEqual(result["verdict"], "avoid_until_change")
        self.assertIn("economics:negative", result["hard_blockers"])

    def test_security_critical_is_a_hard_blocker(self):
        venue = radar.find_venue(self.data["venues"], "clawmolt")
        result = radar.assess(venue)
        self.assertIn("security:critical", result["hard_blockers"])

    def test_cli_recommend_is_machine_readable(self):
        completed = subprocess.run(
            [sys.executable, str(RADAR_PATH), "recommend", "--json"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["id"], "taskmarket")
        self.assertIn("breakdown", result)

    def test_cli_rejects_unknown_venue(self):
        completed = subprocess.run(
            [sys.executable, str(RADAR_PATH), "check", "does-not-exist"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("unknown venue", completed.stderr)


if __name__ == "__main__":
    unittest.main()
