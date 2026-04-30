---
id: ssl-termination
title: SSL Termination
depth: 2
last_reviewed: 2026-04-30
review_due: 2026-05-03
sources:
  - sources/videos/cs75-summer-2012-lecture-9-scalability-harvard-web-development-david-malan
related:
  - load-balancing
  - high-availability
tags:
  - system-design
  - security
---

# SSL Termination

- **One-sentence definition**: Decrypting HTTPS traffic at the load balancer so backend servers communicate over plain HTTP, centralizing certificate management and offloading crypto overhead.
- **Why it exists / what problem it solves**: HTTPS is essential for user-facing traffic, but performing TLS handshakes on every backend server wastes CPU and makes certificate deployment a pain. Terminating SSL at one point simplifies operations.
- **Keywords**: SSL termination, TLS, HTTPS, certificate management, load balancer, encryption offload
- **Related concepts**: [[load-balancing]], [[high-availability]]
- **Depth**: 2/4
- **Last updated**: 2026-04-30
- **Source**: sources/videos/cs75-summer-2012-lecture-9-scalability-harvard-web-development-david-malan

## Summary

Think of a secure building with a single guarded entrance. Visitors show ID at the front door (SSL termination point), then move freely inside without re-checking at every room. The guard (load balancer) handles all the security work so the rooms (backend servers) can focus on their actual job.

The load balancer (HAProxy, NGINX, or hardware like F5) holds the SSL certificate, performs the TLS handshake with clients, decrypts incoming HTTPS, and forwards plain HTTP to backends. This means:
- Certificates are installed in one place, not on every server.
- Backend servers use less CPU (no crypto overhead).
- Internal traffic is unencrypted — acceptable when you control the network, but a risk if the internal network is compromised.

Firewall rules typically allow TCP 443 (HTTPS) from the internet to the LB, TCP 80 (HTTP) from the LB to backends, and restrict database ports (e.g., 3306) to internal traffic only.

## Example

Before SSL termination:
- 10 backend servers each need an SSL certificate installed and renewed.
- Each server spends CPU cycles on TLS handshakes for every connection.
- Certificate renewal requires touching all 10 servers.

After SSL termination at the LB:
- 1 certificate on the load balancer.
- Backends receive plain HTTP — simpler, faster.
- Certificate renewal is a single operation.
- Trade-off: internal traffic between LB and backends is unencrypted.

## Relationship to other concepts

- [[load-balancing]]: SSL termination is a core load balancer responsibility — both software (HAProxy, NGINX) and hardware (F5, Citrix) LBs support it.
- [[high-availability]]: If the LB doing SSL termination is a SPOF, you need an HA pair. The certificate must be on both LBs.

## Open questions

- When is end-to-end encryption (re-encrypting LB → backend) worth the overhead vs trusting the internal network?
- How does mutual TLS (mTLS) in service meshes change the SSL termination model?
