---
difficulty: easy
last_sent: null
review_count: 0
tags:
- load-balancing
- scalability
- high-availability
topic: system-design
---

# Load Balancer

A Load Balancer distributes incoming traffic across multiple servers to prevent any single server from being overwhelmed. Think of it as a traffic cop directing cars to different lanes to keep traffic flowing smoothly.

## How it works

1. **Health checks** — Continuously monitors servers by pinging them periodically. If a server fails health checks, traffic stops routing to it automatically.
2. **Distribution algorithms**:
   - Round Robin — equal turns across all servers
   - Least Connections — pick the server with fewest active connections (best for varying request times)
   - IP Hash — same client always hits the same server (useful for session state)
3. **SSL termination** — Handles encryption/decryption at the load balancer level, reducing backend workload by ~80%
4. **Session persistence** — When needed, keeps users connected to the same server (sticky sessions)

## Types

- **Layer 4 (Transport)** — Routes by IP/port. Faster, handles more connections, but can't inspect content. Good for TCP/UDP load balancing.
- **Layer 7 (Application)** — Routes by URL/headers/cookies. Smarter — can send image requests to one pool and API requests to another. More flexible but slightly slower.

## Why use it

Provides high availability (automatic failover when servers die), better performance (distributed workload), and easy horizontal scaling — add servers without downtime. If one server crashes, traffic automatically routes to healthy servers within seconds. No client code changes needed. Essential for any production system serving more than a few hundred concurrent users.

## Real-world example

A typical setup: 3 web servers behind a load balancer. The balancer checks health every 10 seconds. Server 2 dies at 2:00 AM — load balancer stops sending traffic to it. You wake up to an alert, fix server 2, and traffic resumes. Zero downtime for users. During Black Friday, you add 10 more servers — load balancer starts distributing traffic to them immediately.

## Algorithms in detail

- **Round Robin**: Simple, fair. Good when servers are similar and requests take similar time.
- **Least Connections**: Better when request times vary. A server handling long connections gets fewer new requests.
- **IP Hash**: Ensures session affinity. Same user always hits same server — useful when server stores session state locally.
- **Weighted Round Robin**: Give powerful servers more traffic. Good when servers have different capacities (e.g., 8-core vs 4-core).

## Popular tools

AWS ELB/ALB (managed), Nginx (reverse proxy), HAProxy (high performance), Cloudflare Load Balancing (global)