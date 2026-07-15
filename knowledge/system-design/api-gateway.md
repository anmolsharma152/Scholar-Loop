---
difficulty: easy
last_sent: 2026-07-14 11:52:32.072530+00:00
review_count: 1
tags:
- api-gateway
- microservices
- architecture
topic: system-design
---

# API Gateway

An API Gateway is the single entry point for all client requests in a microservices architecture. Think of it as a smart receptionist that handles everything before requests reach your backend services — authentication, routing, rate limiting, and response formatting.

## How it works

1. **Request routing** — Directs requests to the right microservice based on URL path, headers, or query parameters. A single gateway can route `/users/*` to the user service and `/orders/*` to the order service.
2. **Authentication & authorization** — Validates JWT tokens, API keys, or OAuth credentials before allowing access. Centralizes auth logic so individual services don't need to implement it.
3. **Rate limiting** — Protects services from overload by limiting requests per client. Without it, one misbehaving client could DDoS your entire system.
4. **Response aggregation** — Combines data from multiple services into one response. Instead of the client making 5 calls to get a dashboard, the gateway does it and returns one response.
5. **Protocol translation** — Converts between formats (REST to gRPC, HTTP to WebSocket). External clients use REST; internal services use gRPC for efficiency.

## Without vs with gateway

Without a gateway, clients must know every service URL, handle auth per service, and deal with inconsistent error formats. With a gateway, clients call ONE endpoint. All security, monitoring, and rate limiting happen in one place — no duplication across services.

## Cross-cutting concerns

The gateway handles logging, monitoring, and request transformation in one place. This means consistent observability across all services without each service implementing its own logging middleware. It also enables canary deployments — route 5% of traffic to new service version and monitor before full rollout.

## Trade-offs

The gateway is a single point of failure — if it goes down, everything goes down. Use redundancy (multiple gateways behind a load balancer) and health checks. It also adds latency to every request, though typically just a few milliseconds. Debugging is harder since you're adding a layer between client and services.

## Real-world example

Netflix uses API Gateway to route mobile, TV, and web clients to different backend services. The gateway handles auth, rate limiting per device type, and response formatting — mobile gets smaller payloads, TV gets higher quality. Without it, every client would need custom logic for each service. The gateway also enables API versioning — `/v1/users` and `/v2/users` can route to different service versions.

## Popular tools

AWS API Gateway, Kong, Nginx, Apigee, Zuul, Traefik