---
id: raid-storage
title: RAID Storage
depth: 2
last_reviewed: 2026-04-30
review_due: 2026-05-03
sources:
  - sources/videos/cs75-summer-2012-lecture-9-scalability-harvard-web-development-david-malan
related:
  - high-availability
  - vertical-scaling
tags:
  - system-design
  - infrastructure
---

# RAID Storage

- **One-sentence definition**: Combining multiple hard drives into one logical unit to get speed (striping), redundancy (mirroring/parity), or both — so a single disk failure doesn't lose data.
- **Why it exists / what problem it solves**: Hard drives fail. RAID protects against disk-level data loss without requiring application changes. It's the hardware-level answer to "what if a disk dies?"
- **Keywords**: RAID 0, RAID 1, RAID 5, RAID 6, RAID 10, striping, mirroring, parity, hot-swap
- **Related concepts**: [[high-availability]], [[vertical-scaling]]
- **Depth**: 2/4
- **Last updated**: 2026-04-30
- **Source**: sources/videos/cs75-summer-2012-lecture-9-scalability-harvard-web-development-david-malan

## Summary

Think of RAID levels like different ways to organize backup copies of a book:

- **RAID 0** (striping): Tear the book in half, store each half on a different shelf. Twice as fast to read (parallel access), but if either shelf collapses, the book is gone. Zero redundancy.
- **RAID 1** (mirroring): Keep two identical copies on two shelves. Either can be destroyed and you still have the full book. But you need 2× the shelf space.
- **RAID 5** (striping + parity): Spread the book across N shelves with one shelf of "recovery notes" (parity). Any one shelf can fail and you reconstruct from the others. Better space efficiency than RAID 1.
- **RAID 6**: Like RAID 5 but tolerates two simultaneous failures.
- **RAID 10** (1+0): Mirror first, then stripe across the mirrors. Both fast and redundant — the gold standard for databases.

Hot-swappable drives let you replace a failed disk without shutting down the server.

## Example

A MySQL database server with 4 × 1TB drives:
- **RAID 0**: 4TB usable, fast writes, but one drive failure = total data loss. Never use for databases.
- **RAID 1**: 2TB usable (2 mirrored pairs). Safe but expensive per TB.
- **RAID 10**: 2TB usable, fast reads/writes, survives one failure per mirror pair. Standard choice for production databases.
- **RAID 5**: 3TB usable, survives one failure, but write performance suffers due to parity calculations.

## Relationship to other concepts

- [[high-availability]]: RAID provides HA at the disk level. Database replication provides HA at the server level. Both are needed for full resilience.
- [[vertical-scaling]]: RAID is a vertical scaling strategy — improving one machine's resilience and performance rather than adding machines.

## Open questions

- With cloud providers managing storage (EBS, Persistent Disks), is RAID still relevant for application developers?
- How does RAID interact with SSDs differently than with spinning disks (write amplification, wear leveling)?
