#!/usr/bin/env python3
"""Deterministic marketplace-risk checker for autonomous agents."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_DATA = ROOT / "data" / "venues.json"

CRITERIA = {
    "inventory": {
        "weight": 25,
        "values": {
            "active": 1.0,
            "gated": 0.3,
            "stale": 0.0,
            "none": 0.0,
            "test_only": 0.0,
            "unavailable": 0.0,
        },
    },
    "funding": {
        "weight": 20,
        "values": {
            "verified_current": 1.0,
            "verified_historical": 0.7,
            "claimed": 0.3,
            "unverified": 0.1,
            "underfunded": 0.0,
            "absent": 0.0,
            "not_applicable": 0.0,
        },
    },
    "payout": {
        "weight": 20,
        "values": {
            "verified_recent": 1.0,
            "verified_historical": 0.7,
            "claimed": 0.3,
            "failed": 0.0,
            "none": 0.0,
            "test_only": 0.0,
            "internal_only": 0.0,
        },
    },
    "withdrawal": {
        "weight": 15,
        "values": {
            "ready": 1.0,
            "wallet_required": 0.7,
            "gated": 0.5,
            "unverified": 0.2,
            "unavailable": 0.0,
            "internal_only": 0.0,
            "test_only": 0.0,
        },
    },
    "economics": {
        "weight": 15,
        "values": {
            "positive": 1.0,
            "contested": 0.5,
            "unverified": 0.2,
            "negative": 0.0,
            "none": 0.0,
            "test_only": 0.0,
        },
    },
    "security": {
        "weight": 5,
        "values": {
            "normal": 1.0,
            "caution": 0.4,
            "critical": 0.0,
        },
    },
}

HARD_BLOCKERS = {
    "inventory": {"stale", "none", "test_only", "unavailable"},
    "funding": {"underfunded", "absent"},
    "payout": {"failed", "none", "test_only", "internal_only"},
    "withdrawal": {"unavailable", "internal_only", "test_only"},
    "economics": {"negative", "none", "test_only"},
    "security": {"critical"},
}


class RadarError(ValueError):
    """Raised when data or CLI input is invalid."""


def load_data(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RadarError(f"dataset not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RadarError(f"invalid JSON in {path}: {exc}") from exc
    validate_data(data)
    return data


def validate_data(data: dict[str, Any]) -> None:
    if data.get("schema_version") != 1:
        raise RadarError("unsupported or missing schema_version")
    venues = data.get("venues")
    if not isinstance(venues, list) or not venues:
        raise RadarError("venues must be a non-empty list")

    seen: set[str] = set()
    for index, venue in enumerate(venues):
        prefix = f"venues[{index}]"
        for key in ("id", "name", "checked_at", "signals", "evidence", "sources"):
            if key not in venue:
                raise RadarError(f"{prefix} is missing {key}")
        venue_id = venue["id"]
        if not isinstance(venue_id, str) or not venue_id:
            raise RadarError(f"{prefix}.id must be a non-empty string")
        if venue_id in seen:
            raise RadarError(f"duplicate venue id: {venue_id}")
        seen.add(venue_id)

        signals = venue["signals"]
        for criterion, rule in CRITERIA.items():
            value = signals.get(criterion)
            if value not in rule["values"]:
                allowed = ", ".join(rule["values"])
                raise RadarError(
                    f"{prefix}.signals.{criterion}={value!r}; expected one of {allowed}"
                )
        if not isinstance(venue["sources"], list) or not venue["sources"]:
            raise RadarError(f"{prefix}.sources must contain at least one citation")


def evaluate(signals: dict[str, str]) -> dict[str, Any]:
    score = 0.0
    blockers: list[str] = []
    breakdown: dict[str, Any] = {}

    for criterion, rule in CRITERIA.items():
        value = signals.get(criterion)
        if value not in rule["values"]:
            raise RadarError(f"invalid {criterion} value: {value!r}")
        points = rule["weight"] * rule["values"][value]
        score += points
        breakdown[criterion] = {
            "status": value,
            "points": round(points, 1),
            "possible": rule["weight"],
        }
        if value in HARD_BLOCKERS.get(criterion, set()):
            blockers.append(f"{criterion}:{value}")

    rounded = round(score)
    if blockers:
        verdict = "avoid_until_change"
    elif rounded >= 60:
        verdict = "continue_with_conditions"
    else:
        verdict = "monitor"

    return {
        "verdict": verdict,
        "score": rounded,
        "score_max": 100,
        "hard_blockers": blockers,
        "breakdown": breakdown,
    }


def assess(venue: dict[str, Any]) -> dict[str, Any]:
    result = {
        "id": venue["id"],
        "name": venue["name"],
        "checked_at": venue["checked_at"],
        **evaluate(venue["signals"]),
        "signals": venue["signals"],
        "conditions": venue.get("conditions", []),
        "evidence": venue["evidence"],
        "sources": venue["sources"],
    }
    return result


def find_venue(venues: list[dict[str, Any]], query: str) -> dict[str, Any]:
    needle = query.casefold().strip()
    exact = [
        venue
        for venue in venues
        if needle in {venue["id"].casefold(), venue["name"].casefold()}
    ]
    if len(exact) == 1:
        return exact[0]

    partial = [
        venue
        for venue in venues
        if needle in venue["id"].casefold() or needle in venue["name"].casefold()
    ]
    if len(partial) == 1:
        return partial[0]
    if not partial:
        raise RadarError(f"unknown venue: {query}")
    choices = ", ".join(venue["id"] for venue in partial)
    raise RadarError(f"ambiguous venue {query!r}; matches: {choices}")


def print_human(result: dict[str, Any]) -> None:
    print(f"{result['name']} ({result['checked_at']})")
    print(
        f"Verdict: {result['verdict']}  "
        f"Score: {result['score']}/{result['score_max']}"
    )
    if result["hard_blockers"]:
        print("Hard blockers: " + ", ".join(result["hard_blockers"]))
    if result["conditions"]:
        print("Recheck when: " + "; ".join(result["conditions"]))
    print("Evidence: " + result["evidence"])
    print("Sources:")
    for source in result["sources"]:
        print(f"- {source}")


def emit(payload: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif isinstance(payload, list):
        for item in payload:
            blockers = ",".join(item["hard_blockers"]) or "-"
            print(
                f"{item['id']:<20} {item['score']:>3}/100  "
                f"{item['verdict']:<25} {blockers}"
            )
    else:
        print_human(payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-venue-radar",
        description=(
            "Score a dated marketplace snapshot using deterministic inventory, "
            "funding, payout, withdrawal, economics, and security rules."
        ),
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA,
        help="path to venues.json",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="assess every known venue")
    list_parser.add_argument(
        "--verdict",
        choices=("continue_with_conditions", "monitor", "avoid_until_change"),
    )
    list_parser.add_argument("--json", action="store_true")

    check_parser = subparsers.add_parser("check", help="assess one known venue")
    check_parser.add_argument("venue", help="venue id or unambiguous name fragment")
    check_parser.add_argument("--json", action="store_true")

    recommend_parser = subparsers.add_parser(
        "recommend", help="show the highest-ranked non-avoided snapshot"
    )
    recommend_parser.add_argument("--json", action="store_true")

    eval_parser = subparsers.add_parser(
        "evaluate", help="score explicit signals for a venue not in the snapshot"
    )
    for criterion, rule in CRITERIA.items():
        eval_parser.add_argument(
            f"--{criterion}",
            required=True,
            choices=tuple(rule["values"]),
        )
    eval_parser.add_argument("--json", action="store_true")

    subparsers.add_parser("verify-data", help="validate the dataset and exit")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "evaluate":
            signals = {criterion: getattr(args, criterion) for criterion in CRITERIA}
            result = {
                "id": "ad_hoc",
                "name": "Ad hoc venue",
                "checked_at": "user_supplied",
                **evaluate(signals),
                "signals": signals,
                "conditions": [],
                "evidence": "Signals supplied on the command line.",
                "sources": ["user_supplied"],
            }
            emit(result, args.json)
            return 0

        data = load_data(args.data)
        venues = data["venues"]
        if args.command == "verify-data":
            print(f"OK: {len(venues)} venues, schema version {data['schema_version']}")
            return 0
        if args.command == "check":
            emit(assess(find_venue(venues, args.venue)), args.json)
            return 0

        results = sorted(
            (assess(venue) for venue in venues),
            key=lambda item: (-item["score"], item["name"]),
        )
        if args.command == "list":
            if args.verdict:
                results = [item for item in results if item["verdict"] == args.verdict]
            emit(results, args.json)
            return 0
        if args.command == "recommend":
            candidates = [
                item for item in results if item["verdict"] != "avoid_until_change"
            ]
            if not candidates:
                payload = {
                    "verdict": "no_actionable_venue",
                    "reason": "Every snapshot has at least one hard blocker.",
                    "checked_at": data["snapshot_date"],
                }
                print(json.dumps(payload, indent=2) if args.json else payload["reason"])
                return 0
            emit(candidates[0], args.json)
            return 0
    except RadarError as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    sys.exit(main())
