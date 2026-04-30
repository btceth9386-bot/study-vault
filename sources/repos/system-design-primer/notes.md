# System Design Primer

## Summary

The System Design Primer is a comprehensive, structured collection of resources for learning how to design large-scale distributed systems and preparing for system design interviews. It covers fundamental trade-offs (performance vs scalability, latency vs throughput, CAP theorem), consistency and availability patterns, infrastructure components (DNS, CDN, load balancers, reverse proxies), application-layer architecture (microservices, service discovery), database scaling techniques (replication, federation, sharding, denormalization, SQL vs NoSQL), caching strategies (cache-aside, write-through, write-behind, refresh-ahead), asynchronous processing (message queues, task queues, back pressure), and communication protocols (HTTP, TCP/UDP, RPC vs REST). The repo includes eight complete system design interview solutions (Twitter, Pastebin, Web Crawler, Mint.com, Social Graph, Query Cache, Sales Rank, AWS Scaling), each following a 4-step methodology: requirements gathering → high-level design → core component design → scaling analysis. It also provides six object-oriented design problems and Anki spaced-repetition flashcard decks.

## Knowledge Map

- Foundational trade-offs: Performance vs Scalability, Latency vs Throughput, CAP Theorem
- Consistency & availability patterns: Weak / Eventual / Strong Consistency, Active-Passive / Active-Active Failover
- Infrastructure layer: DNS, CDN (Push vs Pull), Load Balancer (L4 vs L7), Reverse Proxy
- Application layer: Microservices, Service Discovery (Consul / Etcd / Zookeeper)
- Data layer: RDBMS scaling (Master-Slave / Master-Master / Federation / Sharding / Denormalization), four NoSQL types (Key-Value / Document / Wide Column / Graph)
- Performance optimization: Four cache update patterns, Async processing (Message Queue / Task Queue / Back Pressure)
- Communication protocols: HTTP, TCP vs UDP, RPC vs REST
- System design solutions: Twitter Timeline, Pastebin, Web Crawler, Mint.com, Social Graph, Query Cache, Sales Rank, AWS Scaling

## Key Takeaways

- Every scaling decision involves trade-offs — there is no universal best approach; the optimal choice depends on workload characteristics, consistency requirements, and operational constraints
- CAP theorem forces a choice between consistency and availability when network partitions are inevitable
- Read/write ratio drives architecture: read-heavy systems use caching + read replicas; write-heavy systems use async processing + sharding
- The 4-step interview method (requirements → high-level design → core components → scaling) is a universal framework for structured system design problem-solving
- Horizontal scaling requires stateless application servers with session state externalized to shared storage
- Cache invalidation is one of the hardest problems; choosing cache-aside vs write-through depends on read/write patterns and consistency needs
- Async processing improves throughput by decoupling expensive operations, but introduces eventual consistency and additional complexity
- Progressive scaling path from single server to millions of users: vertical scaling → horizontal scaling → DB separation → read replicas → caching → CDN → stateless architecture → sharding → async processing → multi-region deployment
