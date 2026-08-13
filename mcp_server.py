#!/usr/bin/env python3
"""Read-only MCP stdio server for Agent Venue Radar."""

from __future__ import annotations

import json
import sys
import time
from collections import deque
from pathlib import Path
from typing import Any

import radar


SERVER_NAME = "agent-venue-radar"
SERVER_VERSION = "0.3.4"
LATEST_PROTOCOL = "2025-06-18"
SUPPORTED_PROTOCOLS = {
    "2024-11-05",
    "2025-03-26",
    LATEST_PROTOCOL,
}
MAX_MESSAGE_BYTES = 1_048_576
MAX_CALLS_PER_MINUTE = 120

ASSESSMENT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "checked_at": {"type": "string"},
        "verdict": {
            "type": "string",
            "enum": [
                "continue_with_conditions",
                "monitor",
                "avoid_until_change",
            ],
        },
        "score": {"type": "integer", "minimum": 0, "maximum": 100},
        "score_max": {"type": "integer", "const": 100},
        "hard_blockers": {
            "type": "array",
            "items": {"type": "string"},
        },
        "signals": {"type": "object"},
        "conditions": {"type": "array", "items": {"type": "string"}},
        "evidence": {"type": "string"},
        "sources": {"type": "array", "items": {"type": "string"}},
        "breakdown": {"type": "object"},
    },
    "required": [
        "id",
        "name",
        "checked_at",
        "verdict",
        "score",
        "score_max",
        "hard_blockers",
        "signals",
        "conditions",
        "evidence",
        "sources",
        "breakdown",
    ],
    "additionalProperties": False,
}

READ_ONLY_ANNOTATIONS = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}

AUDIT_REQUEST_URL = (
    "https://github.com/ItzxFin2323/agent-venue-radar/issues/new"
    "?template=custom-venue-audit.yml"
)
AGRENTING_AGENT_DID = "did:web:github.com:ItzxFin2323:agent-venue-radar"
AGRENTING_CAPABILITY = "marketplace_due_diligence"
AUDIT_OFFER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "service": {"type": "string"},
        "availability": {"type": "string"},
        "price": {"type": "string"},
        "payment_rail": {"type": "string"},
        "payment_timing": {"type": "string"},
        "request_url": {"type": "string"},
        "agrenting_agent_did": {"type": "string"},
        "agrenting_capability": {"type": "string"},
        "hire_instructions": {"type": "string"},
        "deliverables": {"type": "array", "items": {"type": "string"}},
        "safety": {"type": "array", "items": {"type": "string"}},
        "disclaimer": {"type": "string"},
    },
    "required": [
        "service",
        "availability",
        "price",
        "payment_rail",
        "payment_timing",
        "request_url",
        "agrenting_agent_did",
        "agrenting_capability",
        "hire_instructions",
        "deliverables",
        "safety",
        "disclaimer",
    ],
    "additionalProperties": False,
}

TOOLS: list[dict[str, Any]] = [
    {
        "name": "check_venue",
        "title": "Check one AI-work venue",
        "description": (
            "Assess one venue in the dated evidence snapshot. Call before "
            "registering, installing venue code, connecting a wallet, signing, "
            "spending, or performing promised paid work."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "venue": {
                    "type": "string",
                    "minLength": 1,
                    "description": "Venue id or an unambiguous name fragment.",
                }
            },
            "required": ["venue"],
            "additionalProperties": False,
        },
        "outputSchema": ASSESSMENT_SCHEMA,
        "annotations": READ_ONLY_ANNOTATIONS,
    },
    {
        "name": "recommend_venue",
        "title": "Recommend the strongest non-blocked venue",
        "description": (
            "Return the highest-ranked venue without a known hard blocker in "
            "the dated snapshot, or explain that none is actionable."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "recommendation": {
                    "anyOf": [ASSESSMENT_SCHEMA, {"type": "null"}]
                },
                "snapshot_date": {"type": "string"},
                "warning": {"type": "string"},
            },
            "required": ["recommendation", "snapshot_date", "warning"],
            "additionalProperties": False,
        },
        "annotations": READ_ONLY_ANNOTATIONS,
    },
    {
        "name": "list_venues",
        "title": "List AI-work venue assessments",
        "description": (
            "List every assessed venue, optionally filtered by derived verdict."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "verdict": {
                    "type": "string",
                    "enum": [
                        "continue_with_conditions",
                        "monitor",
                        "avoid_until_change",
                    ],
                }
            },
            "additionalProperties": False,
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "count": {"type": "integer", "minimum": 0},
                "snapshot_date": {"type": "string"},
                "venues": {"type": "array", "items": ASSESSMENT_SCHEMA},
            },
            "required": ["count", "snapshot_date", "venues"],
            "additionalProperties": False,
        },
        "annotations": READ_ONLY_ANNOTATIONS,
    },
    {
        "name": "evaluate_venue",
        "title": "Evaluate explicit venue signals",
        "description": (
            "Apply Radar's deterministic rules to current evidence gathered "
            "for a venue that is absent from or newer than the snapshot."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                criterion: {
                    "type": "string",
                    "enum": list(rule["values"]),
                }
                for criterion, rule in radar.CRITERIA.items()
            },
            "required": list(radar.CRITERIA),
            "additionalProperties": False,
        },
        "outputSchema": ASSESSMENT_SCHEMA,
        "annotations": READ_ONLY_ANNOTATIONS,
    },
    {
        "name": "get_current_audit_offer",
        "title": "Get a current evidence audit",
        "description": (
            "Return the paid current-evidence audit offer and intake paths when "
            "a venue is absent from the snapshot, the dated evidence is too "
            "old for a real decision, or independent live verification is "
            "needed. The exact $0.20 service uses Agrenting pre-funded escrow. "
            "This read-only tool never hires, connects a wallet, or moves funds."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        "outputSchema": AUDIT_OFFER_SCHEMA,
        "annotations": READ_ONLY_ANNOTATIONS,
    },
]


class MCPRequestError(ValueError):
    """JSON-RPC error that should be returned to the client."""

    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class RateLimiter:
    """Small in-process limiter for tool calls."""

    def __init__(self, limit: int = MAX_CALLS_PER_MINUTE):
        self.limit = limit
        self.calls: deque[float] = deque()

    def allow(self) -> bool:
        now = time.monotonic()
        cutoff = now - 60
        while self.calls and self.calls[0] < cutoff:
            self.calls.popleft()
        if len(self.calls) >= self.limit:
            return False
        self.calls.append(now)
        return True


def jsonrpc_result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def jsonrpc_error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def tool_result(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, sort_keys=True, separators=(",", ":")),
            }
        ],
        "structuredContent": payload,
    }


def tool_error(message: str) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": message}],
        "isError": True,
    }


def require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise MCPRequestError(-32602, f"{name} must be an object")
    return value


def reject_extra(arguments: dict[str, Any], allowed: set[str]) -> None:
    extra = sorted(set(arguments) - allowed)
    if extra:
        raise MCPRequestError(-32602, f"Unexpected arguments: {', '.join(extra)}")


def load_snapshot() -> dict[str, Any]:
    try:
        return radar.load_data(radar.DEFAULT_DATA)
    except radar.RadarError as exc:
        raise MCPRequestError(-32603, f"Dataset error: {exc}") from exc


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "get_current_audit_offer":
        reject_extra(arguments, set())
        return tool_result(
            {
                "service": "One current AI-work venue evidence audit",
                "availability": "First three accepted beta requests",
                "price": "$0.20",
                "payment_rail": "Agrenting pre-funded escrow",
                "payment_timing": (
                    "The buyer funds exactly $0.20 in Agrenting escrow before "
                    "work begins. After successful delivery and settlement, "
                    "the provider is credited $0.19 after Agrenting's 5% fee."
                ),
                "request_url": AUDIT_REQUEST_URL,
                "agrenting_agent_did": AGRENTING_AGENT_DID,
                "agrenting_capability": AGRENTING_CAPABILITY,
                "hire_instructions": (
                    "Use the official Agrenting marketplace or hirer MCP to "
                    "hire the agent DID above for capability "
                    "marketplace_due_diligence at price 0.20 with output "
                    "delivery. Include only the venue, its public URL, and the "
                    "decision to support. The GitHub issue route is only for "
                    "public scope questions and does not start paid work."
                ),
                "deliverables": [
                    "Timestamped Markdown report",
                    "Machine-readable JSON findings",
                    "Direct public sources and explicit unknowns",
                ],
                "safety": [
                    "Pay only through the stated Agrenting escrow",
                    "Never send a direct wallet payment",
                    "Never provide credentials, private data, or wallet secrets",
                ],
                "disclaimer": (
                    "Research only; no guarantee of safety, profitability, "
                    "legality, availability, or payment."
                ),
            }
        )

    data = load_snapshot()
    venues = data["venues"]

    if name == "check_venue":
        reject_extra(arguments, {"venue"})
        query = arguments.get("venue")
        if not isinstance(query, str) or not query.strip():
            raise MCPRequestError(-32602, "venue must be a non-empty string")
        try:
            payload = radar.assess(radar.find_venue(venues, query))
        except radar.RadarError as exc:
            return tool_error(str(exc))
        return tool_result(payload)

    if name == "recommend_venue":
        reject_extra(arguments, set())
        ranked = sorted(
            (radar.assess(venue) for venue in venues),
            key=lambda item: (-item["score"], item["name"]),
        )
        candidates = [
            item for item in ranked if item["verdict"] != "avoid_until_change"
        ]
        payload = {
            "recommendation": candidates[0] if candidates else None,
            "snapshot_date": data["snapshot_date"],
            "warning": data["limitations"],
        }
        return tool_result(payload)

    if name == "list_venues":
        reject_extra(arguments, {"verdict"})
        verdict = arguments.get("verdict")
        allowed = {
            "continue_with_conditions",
            "monitor",
            "avoid_until_change",
        }
        if verdict is not None and verdict not in allowed:
            raise MCPRequestError(-32602, "verdict is not a supported value")
        assessments = sorted(
            (radar.assess(venue) for venue in venues),
            key=lambda item: (-item["score"], item["name"]),
        )
        if verdict:
            assessments = [
                item for item in assessments if item["verdict"] == verdict
            ]
        payload = {
            "count": len(assessments),
            "snapshot_date": data["snapshot_date"],
            "venues": assessments,
        }
        return tool_result(payload)

    if name == "evaluate_venue":
        reject_extra(arguments, set(radar.CRITERIA))
        missing = [
            criterion for criterion in radar.CRITERIA if criterion not in arguments
        ]
        if missing:
            raise MCPRequestError(
                -32602, f"Missing arguments: {', '.join(missing)}"
            )
        signals = {criterion: arguments[criterion] for criterion in radar.CRITERIA}
        try:
            evaluation = radar.evaluate(signals)
        except radar.RadarError as exc:
            raise MCPRequestError(-32602, str(exc)) from exc
        payload = {
            "id": "ad_hoc",
            "name": "Ad hoc venue",
            "checked_at": "user_supplied",
            **evaluation,
            "signals": signals,
            "conditions": [],
            "evidence": "Signals supplied by the MCP client.",
            "sources": ["user_supplied"],
        }
        return tool_result(payload)

    raise MCPRequestError(-32602, f"Unknown tool: {name}")


class Server:
    def __init__(self) -> None:
        self.initialized = False
        self.client_ready = False
        self.rate_limiter = RateLimiter()

    def handle(self, message: Any) -> dict[str, Any] | None:
        if not isinstance(message, dict):
            return jsonrpc_error(None, -32600, "Invalid Request")
        request_id = message.get("id")
        is_notification = "id" not in message

        if message.get("jsonrpc") != "2.0" or not isinstance(
            message.get("method"), str
        ):
            return None if is_notification else jsonrpc_error(
                request_id, -32600, "Invalid Request"
            )

        method = message["method"]
        params = message.get("params", {})
        try:
            if method == "initialize":
                if is_notification:
                    return None
                params = require_object(params, "params")
                requested = params.get("protocolVersion")
                if not isinstance(requested, str):
                    raise MCPRequestError(
                        -32602, "protocolVersion must be a string"
                    )
                selected = (
                    requested
                    if requested in SUPPORTED_PROTOCOLS
                    else LATEST_PROTOCOL
                )
                self.initialized = True
                return jsonrpc_result(
                    request_id,
                    {
                        "protocolVersion": selected,
                        "capabilities": {"tools": {"listChanged": False}},
                        "serverInfo": {
                            "name": SERVER_NAME,
                            "title": "Agent Venue Radar",
                            "version": SERVER_VERSION,
                        },
                        "instructions": (
                            "Treat every result as a dated preflight snapshot. "
                            "Recheck cited conditions before taking action."
                        ),
                    },
                )

            if method == "notifications/initialized":
                if self.initialized:
                    self.client_ready = True
                return None

            if method == "ping":
                return None if is_notification else jsonrpc_result(request_id, {})

            if not self.initialized or not self.client_ready:
                raise MCPRequestError(-32002, "Server is not initialized")

            if method == "tools/list":
                if is_notification:
                    return None
                require_object(params, "params")
                return jsonrpc_result(request_id, {"tools": TOOLS})

            if method == "tools/call":
                if is_notification:
                    return None
                if not self.rate_limiter.allow():
                    raise MCPRequestError(-32000, "Tool call rate limit exceeded")
                params = require_object(params, "params")
                name = params.get("name")
                if not isinstance(name, str) or not name:
                    raise MCPRequestError(-32602, "Tool name must be a string")
                arguments = require_object(params.get("arguments", {}), "arguments")
                return jsonrpc_result(request_id, call_tool(name, arguments))

            if is_notification:
                return None
            raise MCPRequestError(-32601, f"Method not found: {method}")
        except MCPRequestError as exc:
            return None if is_notification else jsonrpc_error(
                request_id, exc.code, exc.message
            )


def write_message(message: dict[str, Any]) -> None:
    encoded = json.dumps(
        message,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    sys.stdout.write(encoded + "\n")
    sys.stdout.flush()


def main() -> int:
    server = Server()
    source = sys.stdin.buffer
    while True:
        raw = source.readline(MAX_MESSAGE_BYTES + 1)
        if not raw:
            return 0
        if len(raw) > MAX_MESSAGE_BYTES:
            while raw and not raw.endswith(b"\n"):
                raw = source.readline(MAX_MESSAGE_BYTES + 1)
            write_message(jsonrpc_error(None, -32600, "Message too large"))
            continue
        try:
            message = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            write_message(jsonrpc_error(None, -32700, "Parse error"))
            continue
        response = server.handle(message)
        if response is not None:
            write_message(response)


if __name__ == "__main__":
    sys.exit(main())
