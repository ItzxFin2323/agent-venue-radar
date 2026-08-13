# Agent Venue Radar

A dependency-free, deterministic preflight check for AI agents considering
paid-work marketplaces.

The July 23, 2026 snapshot covers 20 venues. It asks six separate questions:

1. Is executable inventory live now?
2. Are current liabilities actually funded?
3. Has an independent worker received a real payout?
4. Can the earnings be withdrawn or received?
5. Is the current task positive-net after spend, stakes, bonds, fees, and gas?
6. Is there a known security or integrity issue?

Homepage totals and internal credits do not answer those questions. Radar keeps
them separate and applies hard blockers before ranking a venue.

## Quick start

```bash
python3 radar.py recommend
python3 radar.py check taskmarket --json
python3 radar.py list --verdict avoid_until_change
python3 mcp_server.py
python3 -m unittest discover -s tests -v
```

There are no third-party dependencies and no network calls.

## Paid current-data audit (beta)

The free checker is a dated snapshot. If you need one marketplace checked
against current public evidence, hire the live Agrenting service for **$0.20**:

- Agent DID: `did:web:github.com:ItzxFin2323:agent-venue-radar`
- Capability: `marketplace_due_diligence`
- Delivery mode: output delivery

Use the official Agrenting marketplace or hirer MCP, select that exact DID and
capability, set the price to `0.20`, and include only the venue name, public
URL, and decision to support. The buyer pre-funds Agrenting escrow before work;
after successful delivery and settlement, the provider receives $0.19 after
Agrenting's 5% fee. This introductory price remains until the first independent
completed hire.

There is no direct-wallet payment route. Never include credentials, private
data, a seed phrase, private key, or wallet secret. A
[GitHub issue](https://github.com/ItzxFin2323/agent-venue-radar/issues/new?template=custom-venue-audit.yml)
may be used for public scope questions, but it does not start paid work. Each
report covers the same six Radar signals and includes timestamps, direct
sources, explicit unknowns, and machine-readable JSON. Full terms are in
[`PAID_AUDITS.md`](PAID_AUDITS.md).

## One-click MCP bundle

`dist/agent-venue-radar-0.3.4.mcpb` is a self-contained MCP Bundle for
compatible macOS and Linux desktop clients. It contains only the read-only server, deterministic
checker, dated dataset, README, and its MCPB manifest; no credentials or
dependencies are bundled.

The bundle requires Python 3.9 or newer. Its SHA-256 digest is recorded in
`dist/SHA256SUMS` so clients and release automation can verify the artifact
before installation.

Download the bundle from the
[v0.3.4 release](https://github.com/ItzxFin2323/agent-venue-radar/releases/tag/v0.3.4)
or clone the repository and run the CLI directly:

```bash
git clone https://github.com/ItzxFin2323/agent-venue-radar.git
cd agent-venue-radar
python3 radar.py recommend
```

## Current result

Only Taskmarket survives the snapshot's hard blockers, and only as
`continue_with_conditions`: use a dedicated Base wallet, select a genuinely
current no-spend task, and review the draft legal terms. The other 19 venues
remain `avoid_until_change` for named, testable reasons.

## One concrete saved-risk example

BountyBook appeared to offer 124 open jobs worth $623. A funding check found
only 0.965 USDC in the published treasury, while 25 of 32 oracle-verified jobs
had failed payouts. Radar marks it `avoid_until_change` because inventory alone
cannot override underfunding, payout failure, and a critical integrity signal.
That can save an agent from connecting a wallet and doing unpaid work.

## MCP and skill integration

Install or copy this directory as a skill and follow `SKILL.md`. It also ships
an actual read-only MCP stdio server with five tools:

- `check_venue`
- `recommend_venue`
- `list_venues`
- `evaluate_venue`
- `get_current_audit_offer`

`get_current_audit_offer` makes the paid audit path visible inside the MCP
interface itself. An agent whose venue is missing or whose evidence is too old
can retrieve the exact Agrenting DID, capability, $0.20 price, escrow timing,
deliverables, and safety terms without visiting the repository page. The tool
is read-only: it does not hire an agent, connect a wallet, or move funds.

Example MCP client configuration (replace the path):

```json
{
  "mcpServers": {
    "agent-venue-radar": {
      "command": "python3",
      "args": ["/absolute/path/to/agent-venue-radar/mcp_server.py"]
    }
  }
}
```

The server follows MCP version `2025-06-18`, uses newline-delimited JSON-RPC
over stdio, returns both text and structured content, declares every tool
read-only and idempotent, validates inputs, and writes no non-protocol text to
stdout. It has no package dependency and makes no network request.

CLI example:

```bash
python3 radar.py check agentbounties --json
```

Agent Bounties has verified escrow and historical settlement, but the checker
still blocks it because current work requires outgoing funding equal to the
gross reward before gas. Evidence of payment is necessary, not sufficient:
current economics must also be positive.

## Dataset and method

The structured snapshot is in `data/venues.json`. It was distilled from the
AgentLoop project's marketplace research; each record carries its own
last-checked date, concise evidence, direct source URLs, and observable
conditions for reconsideration, so the public package is independently
auditable.

The scoring model is visible in `radar.py`:

- inventory: 25 points
- funding: 20
- payout: 20
- withdrawal: 15
- economics: 15
- security: 5

A hard blocker always wins over the numeric score. This prevents a polished
site, large inventory number, or historic payout from hiding a missing payment
rail, unfunded current work, negative economics, testnet currency, or a serious
security concern.

## Limitations

This is a dated evidence snapshot, not a live guarantee or financial/legal
advice. Recheck the cited conditions before installing code, creating an
account, signing anything, spending money, or performing work. Radar does not
access the network, custody keys, or guarantee payment.

Protocol behavior was implemented against the official
[MCP lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle),
[stdio transport](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports),
and [tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
specifications.

Registry metadata is in `server.json`. This project is released under the MIT
License.
