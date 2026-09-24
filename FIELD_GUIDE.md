# Evidence before effort

## A marketplace can score 80/100 and still be a no-go

**Agent Venue Radar helps agent builders separate advertised work from evidence
that the work can actually pay.** Start with six checks, not a wallet connection.

This is a synthetic walkthrough, not a claim about a real marketplace. The
commands run locally, use no network and move no money. The score is a weighted
checklist, **not an 80% probability of payment**.

## Try the failure case

From the repository directory, with Python 3.9 or newer:

```bash
python3 radar.py evaluate --inventory active --funding underfunded --payout verified_recent --withdrawal ready --economics positive --security normal --json
```

The relevant output is:

```json
{
  "score": 80,
  "score_max": 100,
  "verdict": "avoid_until_change",
  "hard_blockers": ["funding:underfunded"]
}
```

Five favorable inputs cannot override an underfunded current obligation. A
past payout and an active job board answer different questions from whether
the particular work you are about to do is funded.

Now change just the hypothetical funding input:

```bash
python3 radar.py evaluate --inventory active --funding verified_current --payout verified_recent --withdrawal ready --economics positive --security normal --json
```

That produces `100/100`, no hard blockers, and
`continue_with_conditions`—**never a payment guarantee**. The program evaluates
the inputs you supply; it does not independently verify them. Do not change an
input merely to obtain a favorable verdict.

## Your six-question evidence card

For each answer, record a public source, when you checked it, and what remains
unknown. A promotional claim is not independent verification.

| Check | Evidence to seek | What does not establish it |
|---|---|---|
| Current work | A still-open task and objective acceptance criteria | A homepage job counter |
| Funding | Funds covering the current task's obligations | Historical revenue or an old balance |
| Payout | A settled receipt independently linked to delivered work | Credits, screenshots without provenance, or promised rewards |
| Withdrawal | A usable route to receive the proceeds | A withdraw button alone |
| Economics | Reward minus required fees, deposits, bonds and other costs | The headline reward alone |
| Integrity | Inspectable behavior, permissions and material risk disclosures | A polished landing page or popularity |

An unknown is a result, not an invitation to invent confidence. Preserve the
exact condition that would change your decision and recheck only when it changes.

## Use Radar on your next evaluation

1. Run the two synthetic commands above. They require no account or credentials.
2. Read [the method and limitations](README.md#dataset-and-method) before
   supplying your own evidence. The included real-venue dataset was checked in
   July 2026; it is **historical**, not current market advice.
3. If you need a current public-evidence report for one venue, see the
   [documented paid beta](PAID_AUDITS.md). The existing offer is $0.20 through
   Agrenting pre-funded escrow. Availability and a funded hire must be confirmed
   before work. There is no direct-wallet or card checkout in this repository.

For a public scope question, use the
[audit-scope form](https://github.com/ItzxFin2323/agent-venue-radar/issues/new?template=custom-venue-audit.yml).
Include only a public venue URL and the decision you need to make. Opening an
issue does not order an audit or authorize work. Never include secrets or
personal data.

Radar is AI-assisted software from AgentLoop, a human-owned engineering process.
This example demonstrates the checker; it is not a customer testimonial,
independent install, earned revenue or a promise of safety or profit.
