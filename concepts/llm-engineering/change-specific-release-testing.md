---
id: change-specific-release-testing
title: Change-Specific Release Testing
depth: 2
lab_status: not-started
last_reviewed: 2026-07-11
review_due: 2026-07-14
sources:
  - sources/articles/aws-devops-agent-docs/
related:
  - release-readiness-blast-radius-review
  - sparse-validation-evaluation
  - agentic-coding-80-percent-problem
  - ai-compressed-sdlc
  - execution-mode-specific-agent-prompting
  - risk-focused-high-velocity-code-review
tags:
  - llm-engineering
  - aws
  - devops-agent
  - release-management
  - testing
---

# Change-Specific Release Testing

- **One-sentence definition**: Change-specific release testing generates and runs tests targeted at the risks introduced by a particular software change instead of relying only on a fixed regression suite.
- **Why it exists / what problem it solves**: Full regression suites can be slow, expensive, and still miss the behavior most affected by a change. Targeted tests spend effort where the current change is most likely to break something.
- **Keywords**: release testing, targeted tests, test profiles, regression risk, verification
- **Related concepts**: [[release-readiness-blast-radius-review]], [[sparse-validation-evaluation]], [[agentic-coding-80-percent-problem]], [[execution-mode-specific-agent-prompting]], [[risk-focused-high-velocity-code-review]]
- **Depth**: 2/4
- **Last updated**: 2026-07-11
- **Source**: sources/articles/aws-devops-agent-docs/

## Summary

Change-specific testing starts from the question: what did this change put at risk? If a pull request changes checkout behavior, the most useful tests are not random tests across the whole product. They are tests that exercise checkout paths, API contracts, and integrations affected by that change. AWS DevOps Agent connects this idea to release readiness findings and test profiles so testing follows the risk.

## Example

A web application changes discount-code handling. Instead of running only a static smoke suite, the agent creates a test plan for valid discounts, expired discounts, stacked discounts, and checkout totals. If the readiness review also found a dependency on a pricing API, the test plan includes that integration path.

## Relationship to existing concepts

- [[release-readiness-blast-radius-review]]: Readiness review identifies risk areas that focused testing should cover.
- [[sparse-validation-evaluation]]: Both concepts use selective evaluation to spend limited test budget where it is most valuable.
- [[agentic-coding-80-percent-problem]]: Change-focused testing concentrates effort on the hard edge cases and integrations agents may miss.
- [[ai-compressed-sdlc]]: Targeted verification helps manage the quality bottleneck created when implementation accelerates.
- [[execution-mode-specific-agent-prompting]]: A task's execution mode states the evidence to collect; this concept focuses release tests on the resulting change risk.
- [[risk-focused-high-velocity-code-review]]: Automated targeted tests provide the evidence that lets reviewers concentrate on higher-order risks.

## Open questions

- How much static regression coverage should remain when change-specific testing exists?
- How should generated tests be reviewed before they can block a release?
