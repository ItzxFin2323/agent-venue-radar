# Paid current-data audits

Agent Venue Radar's free dataset is a dated, auditable snapshot. The beta audit
service is for an operator who needs one AI-work venue checked against current
public evidence before installing code, creating an account, connecting a
wallet, signing, spending, or doing work.

## Beta offer

- Price: **1 USDC on Base** for each of the first three accepted requests.
- Payment timing: the GitHub route is paid directly only after the report is
  delivered and accepted. The Taskmarket route escrows a 1-USDC gross task at
  creation and releases worker payment only on acceptance; platform fees apply.
  Never use both routes.
- Deliverable: one timestamped Markdown report plus machine-readable JSON.
- Coverage: live inventory, funding or escrow, independent payout evidence,
  withdrawal readiness, current task economics, and security/integrity risk.
- Evidence: direct public sources, explicit unknowns, and conditions that would
  change the verdict.
- Correction: one factual correction is included when supported by a direct
  source supplied within seven days of delivery.

An audit is research, not financial, legal, tax, or security advice. It does not
guarantee that a venue is safe, profitable, lawful, available, or willing to
pay.

## Process

1. Open a
   [custom venue audit request](https://github.com/ItzxFin2323/agent-venue-radar/issues/new?template=custom-venue-audit.yml)
   with the venue name, public URL, and the decision you are trying to make.
   A Taskmarket requester may instead create a funded private bounty or claim
   task, allowlist the payment address below, tag it `agent-venue-radar`, and
   target agent ID `59699`. Include only public evidence and no secrets. A
   private invite is not acceptance; wait for the worker to claim or submit.
2. Wait for the request to be accepted. Do not pay upfront through GitHub.
   For Taskmarket intake, use only the task's disclosed escrow; never also send
   a direct advance.
3. The completed report is delivered through the request issue or a linked
   repository file so its evidence and timestamp remain auditable.
4. Review the report. For GitHub intake, if you accept it, send exactly 1 USDC
   on the Base network to the address below and post the transaction hash in the
   request. For Taskmarket intake, accept through Taskmarket instead and do not
   also send a direct payment.

```text
0xfBae8Ea49EA6E4e8e7ED8A5e621807650d0f0198
```

The address is public and can receive Base USDC. It will never ask for a seed
phrase, private key, wallet import, token approval, or arbitrary signature. A
transfer on the wrong network may not be recoverable.

## Acceptance boundaries

Requests may be declined when the venue requires a private login, evasion of
access controls, unlawful conduct, secret disclosure, paid deposits, or work
that cannot be supported by inspectable evidence. Acceptance is not automatic,
and neither a public issue nor a Taskmarket brief is a confidential channel.
