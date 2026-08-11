import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp_server.py"


class MCPProcess:
    def __init__(self):
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        self.process = subprocess.Popen(
            [sys.executable, str(SERVER)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

    def send(self, message):
        assert self.process.stdin
        self.process.stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
        self.process.stdin.flush()

    def receive(self):
        assert self.process.stdout
        line = self.process.stdout.readline()
        if not line:
            stderr = self.process.stderr.read() if self.process.stderr else ""
            raise AssertionError(f"MCP server closed unexpectedly: {stderr}")
        self._last_line = line
        return json.loads(line)

    def initialize(self):
        self.send(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0"},
                },
            }
        )
        response = self.receive()
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return response

    def close(self):
        if self.process.stdin and not self.process.stdin.closed:
            self.process.stdin.close()
        self.process.wait(timeout=5)
        if self.process.stdout:
            remainder = self.process.stdout.read()
            self.process.stdout.close()
            if remainder:
                raise AssertionError(f"unexpected stdout: {remainder}")
        if self.process.stderr:
            stderr = self.process.stderr.read()
            self.process.stderr.close()
            if stderr:
                raise AssertionError(f"unexpected stderr: {stderr}")


class MCPServerTests(unittest.TestCase):
    def setUp(self):
        self.client = MCPProcess()

    def tearDown(self):
        self.client.close()

    def test_initialize_and_list_tools(self):
        initialized = self.client.initialize()
        self.assertEqual(initialized["result"]["protocolVersion"], "2025-06-18")
        self.assertEqual(
            initialized["result"]["capabilities"],
            {"tools": {"listChanged": False}},
        )

        self.client.send(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        )
        response = self.client.receive()
        tools = response["result"]["tools"]
        self.assertEqual(
            {tool["name"] for tool in tools},
            {
                "check_venue",
                "recommend_venue",
                "list_venues",
                "evaluate_venue",
                "get_current_audit_offer",
            },
        )
        self.assertTrue(all(tool["annotations"]["readOnlyHint"] for tool in tools))

    def test_check_venue_returns_structured_and_text_content(self):
        self.client.initialize()
        self.client.send(
            {
                "jsonrpc": "2.0",
                "id": "check",
                "method": "tools/call",
                "params": {
                    "name": "check_venue",
                    "arguments": {"venue": "agentbounties"},
                },
            }
        )
        response = self.client.receive()["result"]
        structured = response["structuredContent"]
        self.assertEqual(structured["id"], "agentbounties")
        self.assertEqual(structured["verdict"], "avoid_until_change")
        self.assertIn("economics:negative", structured["hard_blockers"])
        self.assertEqual(json.loads(response["content"][0]["text"]), structured)

    def test_recommendation_keeps_snapshot_warning(self):
        self.client.initialize()
        self.client.send(
            {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {"name": "recommend_venue", "arguments": {}},
            }
        )
        result = self.client.receive()["result"]["structuredContent"]
        self.assertEqual(result["recommendation"]["id"], "taskmarket")
        self.assertIn("dated evidence snapshot", result["warning"])

    def test_current_audit_offer_is_agent_native_and_after_acceptance(self):
        self.client.initialize()
        self.client.send(
            {
                "jsonrpc": "2.0",
                "id": "offer",
                "method": "tools/call",
                "params": {
                    "name": "get_current_audit_offer",
                    "arguments": {},
                },
            }
        )
        response = self.client.receive()["result"]
        offer = response["structuredContent"]
        self.assertEqual(offer["price"], "1 USDC")
        self.assertEqual(offer["network"], "Base")
        self.assertIn("after delivery", offer["payment_timing"])
        self.assertIn("issues/new", offer["request_url"])
        self.assertIn("Do not pay upfront", offer["safety"])
        self.assertEqual(json.loads(response["content"][0]["text"]), offer)

    def test_unknown_tool_is_protocol_error(self):
        self.client.initialize()
        self.client.send(
            {
                "jsonrpc": "2.0",
                "id": 8,
                "method": "tools/call",
                "params": {"name": "missing", "arguments": {}},
            }
        )
        error = self.client.receive()["error"]
        self.assertEqual(error["code"], -32602)
        self.assertIn("Unknown tool", error["message"])

    def test_unknown_venue_is_a_tool_execution_error(self):
        self.client.initialize()
        self.client.send(
            {
                "jsonrpc": "2.0",
                "id": 9,
                "method": "tools/call",
                "params": {
                    "name": "check_venue",
                    "arguments": {"venue": "does-not-exist"},
                },
            }
        )
        result = self.client.receive()["result"]
        self.assertTrue(result["isError"])
        self.assertNotIn("structuredContent", result)
        self.assertIn("unknown venue", result["content"][0]["text"])

    def test_tool_call_before_initialized_notification_is_rejected(self):
        self.client.send(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1"},
                },
            }
        )
        self.client.receive()
        self.client.send(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        )
        response = self.client.receive()
        self.assertEqual(response["error"]["code"], -32002)

    def test_parse_error_and_stdout_framing(self):
        assert self.client.process.stdin
        self.client.process.stdin.write("{not json}\n")
        self.client.process.stdin.flush()
        response = self.client.receive()
        self.assertEqual(response["error"]["code"], -32700)
        self.assertTrue(self.client._last_line.endswith("\n"))
        self.assertEqual(self.client._last_line.count("\n"), 1)


if __name__ == "__main__":
    unittest.main()
