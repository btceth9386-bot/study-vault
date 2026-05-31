---
id: mcp-elicitation-for-structured-user-input
title: MCP Elicitation for Structured User Input
depth: 2
lab_status: not-started
last_reviewed: 2026-05-31
review_due: 2026-06-03
sources:
  - sources/repos/modelcontextprotocol-modelcontextprotocol/
related:
  - mcp-capability-negotiation-handshake
tags:
  - llm-engineering
  - mcp
  - human-in-the-loop
  - structured-output
---

# MCP Elicitation for Structured User Input

- **One-sentence definition**: MCP elicitation lets a server ask the client to collect structured user input, such as confirmation fields or option selections.
- **Why it exists / what problem it solves**: Free-form chat is a poor fit for decisions that need typed, validated answers. Elicitation gives the client a schema so it can render a suitable interaction and return predictable data.
- **Keywords**: elicitation, form, schema, confirmation, user input, human-in-the-loop
- **Related concepts**: [[mcp-capability-negotiation-handshake]]
- **Depth**: 2/4
- **Last updated**: 2026-05-31
- **Source**: sources/repos/modelcontextprotocol-modelcontextprotocol/

## Summary

Imagine a booking tool that needs a final confirmation and a seat preference. Asking in prose works until the user replies ambiguously. Elicitation turns the question into a small form contract. The host application can render the form, validate the response, and return structured data to the server.

## Example

```json
{
  "type": "object",
  "properties": {
    "confirmBooking": {"type": "boolean"},
    "seatPreference": {"type": "string", "enum": ["window", "aisle"]}
  },
  "required": ["confirmBooking"]
}
```

## Relationship to existing concepts

- [[mcp-capability-negotiation-handshake]]: The client must advertise elicitation support before a server uses it.

## Open questions

- Which requests should require explicit user confirmation even if defaults are available?
- How should clients present sensitive fields without leaking them into model context?
