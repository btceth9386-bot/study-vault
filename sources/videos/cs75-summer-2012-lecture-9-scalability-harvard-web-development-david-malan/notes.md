# CS75 (Summer 2012) Lecture 9: Scalability - Harvard Web Development - David Malan

## Summary

David Malan's final lecture in CS75 walks through the full spectrum of web scalability, starting from a single-server setup and progressively adding layers of infrastructure to handle growth.

The lecture begins with hosting options — shared hosts, VPS providers, and cloud platforms like Amazon EC2 — and the trade-offs between cost, control, and isolation. Malan then introduces **vertical scaling** (upgrading a single machine's CPU, RAM, and disk) as the simplest but ceiling-limited approach, contrasting it with **horizontal scaling** (adding more machines), which becomes the dominant strategy.

Horizontal scaling immediately raises the question of how to distribute traffic. Malan covers **load balancing** approaches: DNS round-robin (simple but naive, broken by caching and uneven load), dedicated load balancers (software like HAProxy or expensive hardware from Citrix/F5), and the algorithms they use (round-robin, load-aware routing). He then explores the **sticky session** problem — how PHP sessions break when users bounce between servers — and evaluates solutions: shared file servers, storing sessions in MySQL, embedding server IDs in cookies, and having the load balancer manage session affinity.

Storage reliability is addressed through **RAID** (0 for striping/performance, 1 for mirroring/redundancy, 5/6 for economy, 10 for both). **Database replication** is covered in depth: master-slave for read scaling and hot spares, master-master for write redundancy. Facebook's early use of partitioning (one database per school) illustrates real-world sharding. Caching gets three treatments: static HTML generation (Craigslist), MySQL query cache, and **Memcached** as an in-memory key-value store using LRU eviction.

The lecture culminates in a chalkboard exercise building a complete multi-tier architecture: redundant load balancers (active-active/active-passive with heartbeats), web server tiers, database tiers with replication, redundant switches, multiple data centers (Amazon availability zones and regions), and firewall rules (TCP 80/443 inbound, port 3306 for MySQL internally, SSL termination at the load balancer).

## Knowledge Map

- Vertical scaling vs. horizontal scaling as the fundamental scaling decision
- Load balancing mechanisms (DNS round-robin, dedicated LB, software vs. hardware)
- Sticky sessions and shared state management
- RAID levels for storage redundancy and performance
- Database replication patterns (master-slave, master-master)
- Caching layers (static HTML, MySQL query cache, Memcached with LRU)
- Single points of failure analysis and elimination
- High availability (active-active, active-passive, heartbeats)
- Multi-tier architecture design (web tier, DB tier, LB tier)
- Network security (firewall rules, SSL termination, port filtering)
- Cloud infrastructure (Amazon EC2, availability zones, regions)

## Key Takeaways

- Vertical scaling is the easy first step but always hits a ceiling — plan for horizontal scaling from the start
- Every architectural improvement that removes one bottleneck tends to introduce a new single point of failure — always ask "what dies next?"
- Sticky sessions are a deceptively hard problem; the cleanest solution is externalizing session state or using load-balancer-managed cookies
- RAID and replication address different failure modes: RAID protects against disk failure within a machine, replication protects against machine failure
- Caching (especially Memcached) is critical for read-heavy workloads — Facebook's early architecture depended heavily on it
- Hardware load balancers can cost $100K+; software alternatives (HAProxy, LVS) achieve the same thing for free
- True high availability requires redundancy at every layer: load balancers, switches, databases, and even data centers
- SSL termination at the load balancer simplifies certificate management and reduces backend server costs
