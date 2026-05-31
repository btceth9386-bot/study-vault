result = await session.elicit_input(
    message="Please confirm your booking details:",
    schema={
        "type": "object",
        "properties": {
            "confirmBooking": {
                "type": "boolean",
                "description": "Confirm the booking ($3,000)"
            },
            "seatPreference": {
                "type": "string",
                "enum": ["window", "aisle", "no preference"]
            }
        },
        "required": ["confirmBooking"]
    }
)
```

**TypeScript Implementation:**

```typescript
const result = await session.elicitInput({
  message: "Confirm booking details:",
  schema: {
    type: "object",
    properties: {
      confirmBooking: { type: "boolean" },
      seatPreference: { 
        type: "string",
        enum: ["window", "aisle", "no preference"]
      }
    },
    required: ["confirmBooking"]
  }
});
```

Sources: [docs/docs/learn/client-concepts.mdx:20-104]()

### Roots: Filesystem Boundaries

Roots communicate filesystem access boundaries to servers. While not enforced by the protocol, well-behaved servers should respect these boundaries.

**Roots Usage Pattern:**

```python