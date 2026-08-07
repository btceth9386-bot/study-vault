---
id: domain-owned-semantic-conventions
title: Domain-Owned Semantic Conventions
depth: 2
lab_status: not-started
last_reviewed: 2026-08-07
review_due: 2026-08-10
sources:
  - sources/repos/open-telemetry-semantic-conventions/
related:
  - semantic-conventions-as-telemetry-schema
  - semantic-attribute-registry-reuse
  - semantic-convention-validation-and-generation
  - cross-provider-genai-telemetry-refinements
tags:
  - observability
  - opentelemetry
  - semantic-conventions
---

# Domain-Owned Semantic Conventions

- **One-sentence definition**: Domain-owned semantic conventions give technology experts responsibility for their telemetry definitions while keeping global review for cross-domain consistency.
- **Why it exists / what problem it solves**: A shared vocabulary needs deep expertise in HTTP, databases, messaging, cloud platforms, and runtimes without becoming a collection of incompatible local schemas.
- **Keywords**: ownership, governance, domains, review, CODEOWNERS, interoperability
- **Related concepts**: [[semantic-conventions-as-telemetry-schema]], [[semantic-attribute-registry-reuse]], [[semantic-convention-validation-and-generation]]
- **Depth**: 2/4
- **Last updated**: 2026-08-07
- **Source**: open-telemetry/semantic-conventions

## Summary

Domain ownership puts the people who understand a technology closest to its telemetry decisions. Database specialists can review database fields, while HTTP specialists review HTTP fields. Global reviewers still protect shared names and rules so one domain does not accidentally break another.

This is a practical balance between local knowledge and one interoperable ecosystem. Automation checks the common rules before human reviewers make the final judgment.

## Example

A proposed messaging attribute is reviewed by the messaging-domain owners for technical accuracy. A global semantic-convention reviewer also confirms that it reuses an existing network attribute instead of creating a near-duplicate. CI validates both the reference and the generated documentation before merge.

## Relationship to Existing Concepts

- [[semantic-conventions-as-telemetry-schema]]: Governance maintains the shared schema across technology domains.
- [[semantic-attribute-registry-reuse]]: Reviewers prefer common registry fields over domain-specific duplicates.
- [[semantic-convention-validation-and-generation]]: Automated checks support the human approval path.
- [[cross-provider-genai-telemetry-refinements]]: Provider specialists own necessary extensions while shared review keeps the core portable.

## My Questions

- Which changes need both domain and global approval?
- How can a project keep review ownership accurate as domains and maintainers change?
