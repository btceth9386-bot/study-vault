---
id: ucp-ap2-commerce-payment-separation
title: UCP and AP2 Commerce-Payment Separation
depth: 2
lab_status: not-started
last_reviewed: 2026-09-25
review_due: 2026-09-28
sources:
  - sources/papers/agent-tools---interoperability-day-2/
related:
  - bounded-tool-calls-vs-agent-delegation
  - agent-space-access-boundary
tags:
  - llm-engineering
  - payments
  - protocol
---

# UCP and AP2 Commerce-Payment Separation

- **One-sentence definition**: UCP handles agentic shopping and order construction, while AP2 proves constrained human authorization for the payment.
- **Why it exists / what problem it solves**: An agent needs rich merchant interactions without unrestricted access to a user's money. Signed mandates, amount limits, and auditable intent keep payment governed while shopping remains autonomous.
- **Keywords**: UCP, AP2, agentic commerce, payment authorization, mandate, order construction
- **Related concepts**: [[bounded-tool-calls-vs-agent-delegation]], [[agent-space-access-boundary]]
- **Depth**: 2/4
- **Last updated**: 2026-09-25
- **Source**: Agent Tools & Interoperability — Day 2

## Summary

UCP is the shopping side of an agentic transaction: it discovers merchant options, checks availability, and builds an order with details such as fees and estimated arrival. AP2 is the payment side: it carries a signed authorization with clear limits, such as a maximum amount. Keeping those jobs separate means an agent can choose and construct a purchase without silently gaining permission to spend any amount. The payment system can verify the mandate and block a charge that exceeds it.

## Example

A user authorizes lunch spending up to $25. An agent uses UCP to find a restaurant, compare menus, and create an $18.50 order. It then presents the AP2 mandate for payment; if the merchant tries to charge $50, the constrained authorization blocks it.

## Relationship to existing concepts

- [[bounded-tool-calls-vs-agent-delegation]]: UCP and AP2 define structured transactional operations after a decision has been made, rather than the broader choice of delegating an evolving task.
- [[agent-space-access-boundary]]: The broader access boundary limits which merchant and payment capabilities an agent may use.

## My questions

- How should an AP2 mandate express substitutions, tips, taxes, and delivery changes?
- Which parts of an order should require renewed human authorization before payment?
