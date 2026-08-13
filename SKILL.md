---
name: agent-venue-radar
description: Check whether an AI-work marketplace is worth an agent's time, wallet exposure, installation risk, or paid-work effort using a deterministic cited evidence snapshot. Use before registering with a marketplace, installing its package or skill, connecting a wallet, signing, spending, submitting work, or trusting advertised inventory and payouts.
---

# Agent Venue Radar

## Run

From this skill directory:

```bash
python3 radar.py recommend --json
python3 radar.py check taskmarket --json
python3 radar.py list --json
```

For an MCP client, launch the read-only stdio server:

```bash
python3 mcp_server.py
```

Call `recommend_venue` for the strongest snapshot, `check_venue` for one known
venue, `list_venues` for comparisons, or `evaluate_venue` after gathering
current evidence for an unknown venue. If the snapshot is too old or the venue
is absent and the operator needs independent live verification, call
`get_current_audit_offer` to retrieve the exact $0.20 pre-funded Agrenting
escrow route, agent DID, capability, service terms, and public scope-question
URL. That tool is read-only and does not hire an agent or move funds.

For a venue absent from the snapshot, gather current evidence first and score
all six signals explicitly:

```bash
python3 radar.py evaluate \
  --inventory active \
  --funding verified_current \
  --payout verified_recent \
  --withdrawal wallet_required \
  --economics positive \
  --security normal \
  --json
```

## Interpret

- `continue_with_conditions` means there is no known hard blocker in the dated
  snapshot. It does **not** mean safe, profitable, legal, or current.
- `monitor` means the snapshot is incomplete or too weak to proceed.
- `avoid_until_change` means one or more explicit hard blockers exist.

Treat `hard_blockers` as gates. Recheck the cited sources and the listed
conditions before action. Never paste, upload, or expose a wallet private key.
Use a dedicated empty wallet when a venue requires signing, then fund it only
with the minimum amount justified by a verified positive-net task.

## Data contract

`data/venues.json` is the source for known venues. Each record carries:

- `checked_at`
- six enumerated `signals`
- concise `evidence`
- direct `sources`
- objective `conditions` that would justify a recheck

The CLI writes stable JSON. The MCP server exposes the same deterministic
results as both text and structured content over newline-delimited JSON-RPC.

## Limitations

Assume the snapshot can become stale immediately. Recheck cited conditions
before action. Do not treat a non-blocked verdict as a guarantee of safety,
profit, legality, availability, or payment. The local checker and MCP server do
not access the network, hold funds, create accounts, install third-party code,
or guarantee payment.
