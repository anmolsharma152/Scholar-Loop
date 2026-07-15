---
difficulty: easy
last_sent: null
review_count: 0
tags:
- cdn
- performance
- edge-computing
topic: system-design
---

# Content Delivery Network (CDN)

A CDN is a geographically distributed network of servers that caches content close to users. Think of it as having multiple warehouse branches worldwide instead of one central warehouse — users get served from the nearest branch.

## How it works

1. **Edge servers** — CDN servers located globally that cache your content near users. A user in Mumbai gets served from Mumbai edge, not US origin.
2. **Origin server** — Your main server with original content. CDN fetches from here only on cache miss (first request or after TTL expires).
3. **DNS routing** — When a user requests your site, DNS resolves to the nearest edge server based on their geographic location.
4. **Cache invalidation** — Updates cached content using TTL expiration (e.g., 1 hour), versioning (e.g., `app.v2.js`), or manual purge APIs.

## Request path

```
User (closest)
  → Edge server
    → Regional server
      → Origin server (furthest, last resort)
```

## Why use it

- **Lower latency** — 500ms drops to 50ms by serving content locally. Users perceive your site as faster.
- **Traffic absorption** — Handles traffic spikes (product launches, viral content) without overwhelming origin servers
- **Bandwidth savings** — 60-80% cost reduction since most requests never reach origin. CDN providers charge less per GB than cloud compute.
- **DDoS protection** — CDN absorbs attack traffic across its global capacity before it reaches your servers

## What to cache

- Static assets (JS, CSS, images, fonts) — safest, longest TTLs
- Video segments (HLS .ts files) — Netflix/YouTube model
- API responses with cacheable headers — product listings, public data
- Fully-rendered HTML pages with short TTLs — for marketing sites

## Real impact

Netflix streams globally using CDN. Without it, every user hitting US origin servers would cause massive buffering and the service wouldn't be viable internationally. Facebook uses CDN to serve profile pictures — a user in Japan gets served from a Tokyo edge server, not Virginia.

## Cache invalidation strategies

- **TTL (Time-to-Live)**: Cache expires after N seconds. Simple but stale until expiry.
- **Versioned URLs**: `app.v2.js` — new version = new URL = cache miss. Clean but requires build changes.
- **Purge API**: Manual invalidation via CDN dashboard. Use for emergency updates.
- **Surrogate keys**: Tag cached objects and purge by tag. Good for bulk invalidation.

## Popular tools

Cloudflare (free tier available), AWS CloudFront, Akamai, Fastly, Bunny CDN